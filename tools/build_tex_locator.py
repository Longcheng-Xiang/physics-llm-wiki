#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import re
from pathlib import Path


HEADING_COMMAND_RE = re.compile(r"\\(subsubsection|subsection|section)\*?")
DISPLAY_OPEN_RE = re.compile(r"(?<!\\)\\\[")
DISPLAY_CLOSE_RE = re.compile(r"(?<!\\)\\\]")
TOC_RE = re.compile(r"^(.*?)\s+\.{3,}\s+(\d+)\s*$")
PLACEHOLDER_AGENT_NOTES = (
    "*Add honest notes here about coverage gaps, unusual TeX structure, sections "
    "you could not verify, or context limits encountered during manual review. "
    "Flag anything you are uncertain about rather than leaving it silently wrong.*"
)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a Markdown locator for a merged lecture-note .tex file."
    )
    parser.add_argument("tex", help="Path to the merged .tex file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output markdown path. Defaults to <tex stem>.locator.md beside the tex file.",
    )
    parser.add_argument("--title", help="Locator title override.")
    parser.add_argument("--pdf", help="Original lecture-note PDF filename.")
    parser.add_argument(
        "--notes",
        action="append",
        default=[],
        help="Optional user-supplied companion note path. Repeat for multiple notes.",
    )
    return parser


def normalize_title(text: str) -> str:
    cleaned = text.replace(r"\&", "and")
    cleaned = re.sub(r"\$.*?\$", "", cleaned)
    cleaned = re.sub(r"\\[a-zA-Z]+\{.*?\}", "", cleaned)
    cleaned = re.sub(r"\\[a-zA-Z]+", "", cleaned)
    cleaned = cleaned.replace("&", "and")
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", cleaned)
    return cleaned.strip().lower()


def plain_title(text: str) -> str:
    cleaned = re.sub(r"\$.*?\$", "", text)
    cleaned = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\[a-zA-Z]+", "", cleaned)
    cleaned = cleaned.replace(r"\&", "&")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def parse_toc(lines: list[str]) -> dict[str, list[int]]:
    toc_map: dict[str, list[int]] = {}
    in_toc = False
    for line in lines:
        stripped = line.strip()
        if stripped == r"\section*{Contents}":
            in_toc = True
            continue
        if not in_toc:
            continue
        if stripped.startswith(r"\section*{") and stripped != r"\section*{Contents}":
            break
        cleaned = stripped.replace(r"\[0pt]", "").rstrip("\\").strip()
        match = TOC_RE.match(cleaned)
        if not match:
            continue
        title = match.group(1).strip()
        page = int(match.group(2))
        toc_map.setdefault(normalize_title(title), []).append(page)
    return toc_map


def skip_optional_short_title(line: str, pos: int) -> int:
    if pos >= len(line) or line[pos] != "[":
        return pos
    depth = 0
    for idx in range(pos, len(line)):
        char = line[idx]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return idx + 1
    return pos


def parse_braced_text(line: str, pos: int) -> tuple[str, int] | None:
    if pos >= len(line) or line[pos] != "{":
        return None
    depth = 0
    start = pos + 1
    for idx in range(pos, len(line)):
        char = line[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return line[start:idx], idx + 1
    return None


def iter_heading_commands(line: str) -> list[tuple[str, str]]:
    headings: list[tuple[str, str]] = []
    search_pos = 0
    while True:
        match = HEADING_COMMAND_RE.search(line, search_pos)
        if not match:
            return headings
        level_name = match.group(1)
        pos = skip_optional_short_title(line, match.end())
        parsed = parse_braced_text(line, pos)
        if parsed is None:
            search_pos = match.end()
            continue
        raw_title, end_pos = parsed
        headings.append((level_name, raw_title))
        search_pos = end_pos


def lookup_toc_page(
    raw_title: str,
    toc_map: dict[str, list[int]],
    toc_seen: dict[str, int],
) -> int | None:
    norm_title = normalize_title(raw_title)
    pages = toc_map.get(norm_title)
    if not pages:
        return None
    seen = toc_seen.get(norm_title, 0)
    toc_seen[norm_title] = seen + 1
    if seen < len(pages):
        return pages[seen]
    return pages[-1]


def parse_headings(lines: list[str], toc_map: dict[str, list[int]]) -> list[dict[str, object]]:
    headings: list[dict[str, object]] = []
    toc_seen: dict[str, int] = {}
    for lineno, line in enumerate(lines, start=1):
        for level_name, raw_title in iter_heading_commands(line):
            level = {
                "section": "section",
                "subsection": "subsection",
                "subsubsection": "subsubsection",
            }[level_name]
            headings.append(
                {
                    "level": level,
                    "title": raw_title,
                    "line": lineno,
                    "page": lookup_toc_page(raw_title, toc_map, toc_seen),
                }
            )
    annotate_headings(headings, len(lines))
    return headings


def title_starts_numbered_section(title: str) -> bool:
    return bool(re.match(r"^\d+(?:\.\d+)+\b", plain_title(title)))


def title_is_bare_number(title: str) -> bool:
    return bool(re.match(r"^\d+$", plain_title(title)))


def title_is_chapter_marker(title: str) -> bool:
    return bool(re.match(r"^chapter\s+\d+\b", plain_title(title), flags=re.I))


def title_is_lecture_marker(title: str) -> bool:
    return bool(re.match(r"^lecture\s+\d+\b", plain_title(title), flags=re.I))


def title_is_artifact(title: str) -> bool:
    norm = normalize_title(title)
    if not norm:
        return True
    artifact_titles = {
        "contents",
        "steven balbus",
        "acknowledgements",
    }
    if norm in artifact_titles:
        return True
    return "\\includegraphics" in title or norm.startswith("image ")


def classify_heading(heading: dict[str, object], previous: dict[str, object] | None) -> str:
    title = str(heading["title"])
    level = str(heading["level"])
    norm = normalize_title(title)

    if title_is_artifact(title):
        return "artifact"
    if title_is_bare_number(title) or title_is_chapter_marker(title):
        return "chapter-marker"
    if previous is not None and previous.get("class") == "chapter-marker" and level == "section":
        return "chapter-title"
    if title_is_lecture_marker(title):
        return "lecture-marker"
    if norm == "exercises":
        return "exercises"
    if plain_title(title).lower().startswith("appendix"):
        return "appendix"
    if title_starts_numbered_section(title):
        return "numbered-heading"
    if heading["page"] is None and level == "section":
        return "local-heading"
    return "heading"


def annotate_headings(headings: list[dict[str, object]], total_lines: int) -> None:
    previous: dict[str, object] | None = None
    for heading in headings:
        heading["class"] = classify_heading(heading, previous)
        previous = heading

    for idx, heading in enumerate(headings):
        start = int(heading["line"])
        if idx + 1 < len(headings):
            next_start = int(headings[idx + 1]["line"])
            end = start if next_start <= start else next_start - 1
        else:
            end = total_lines
        heading["end_line"] = end


def md_cell(text: str) -> str:
    return text.replace("|", r"\|")


def extract_existing_agent_notes(output_path: Path) -> str | None:
    if not output_path.exists():
        return None
    text = output_path.read_text(encoding="utf-8")
    marker = "\n## Agent Notes\n"
    if marker not in text:
        return None
    notes = text.split(marker, 1)[1].strip()
    if not notes or notes == PLACEHOLDER_AGENT_NOTES:
        return None
    return notes


def audit_tex(lines: list[str], tex_path: Path) -> dict[str, object]:
    text = "\n".join(lines)
    asset_dir = tex_path.with_name(f"{tex_path.stem}_assets")
    includegraphics = text.count(r"\includegraphics")
    audit = {
        "line_count": len(lines),
        "display_open": len(DISPLAY_OPEN_RE.findall(text)),
        "display_close": len(DISPLAY_CLOSE_RE.findall(text)),
        "aligned_open": text.count(r"\begin{aligned}"),
        "aligned_close": text.count(r"\end{aligned}"),
        "array_open": text.count(r"\begin{array}"),
        "array_close": text.count(r"\end{array}"),
        "equation_open": text.count(r"\begin{equation}"),
        "equation_close": text.count(r"\end{equation}"),
        "includegraphics": includegraphics,
        "asset_dir_exists": asset_dir.exists(),
        "replacement_chars": text.count("\ufffd"),
        "empty_display": len(re.findall(r"\\\[\s*\\\]", text, flags=re.S)),
    }
    return audit


def build_quick_routing(headings: list[dict[str, object]]) -> list[str]:
    document_end = max((int(h["end_line"]) for h in headings), default=0)
    route_ids: set[int] = set()
    for idx, heading in enumerate(headings):
        if heading["class"] in {"chapter-title", "lecture-marker"}:
            route_ids.add(idx)
        elif (
            heading["class"] == "heading"
            and heading["level"] == "section"
            and heading["page"] is not None
        ):
            route_ids.add(idx)
        elif heading["class"] == "chapter-marker":
            next_heading = headings[idx + 1] if idx + 1 < len(headings) else None
            if next_heading is None or next_heading.get("class") != "chapter-title":
                route_ids.add(idx)
    route_headings = [
        h for idx, h in enumerate(headings) if idx in route_ids
    ]
    if len(headings) < 40 and len(route_headings) < 4:
        return []

    lines = [
        "## Quick Routing",
        "",
        "Major section starts. Use the full heading index below for subsections and local headings.",
        "",
    ]
    for idx, heading in enumerate(route_headings):
        if idx + 1 < len(route_headings):
            route_end = int(route_headings[idx + 1]["line"]) - 1
        else:
            route_end = document_end
        page = heading["page"] if heading["page"] is not None else "?"
        lines.append(
            f"- type `{heading['class']}` | pdf `{page}` | tex `{heading['line']}-{route_end}` | {md_cell(str(heading['title']))}"
        )
    lines.append("")
    return lines


def audit_warnings(audit: dict[str, object]) -> list[str]:
    warnings: list[str] = []
    paired_fields = [
        ("display math delimiters", "display_open", "display_close"),
        ("aligned blocks", "aligned_open", "aligned_close"),
        ("array blocks", "array_open", "array_close"),
        ("equation blocks", "equation_open", "equation_close"),
    ]
    for label, open_key, close_key in paired_fields:
        if audit[open_key] != audit[close_key]:
            warnings.append(
                f"{label} are imbalanced (`{audit[open_key]}` opens vs `{audit[close_key]}` closes)"
            )
    if audit["empty_display"]:
        warnings.append(f"empty display-math blocks found: `{audit['empty_display']}`")
    if audit["replacement_chars"]:
        warnings.append(
            f"Unicode replacement characters found: `{audit['replacement_chars']}`"
        )
    if audit["includegraphics"] and not audit["asset_dir_exists"]:
        warnings.append(
            "`\\includegraphics` references exist but no asset directory is present; figures are placeholders"
        )
    return warnings


def build_markdown(
    tex_path: Path,
    title: str,
    pdf_name: str | None,
    notes: list[str],
    headings: list[dict[str, object]],
    toc_found: bool,
    audit: dict[str, object],
    existing_agent_notes: str | None,
) -> str:
    lines: list[str] = [f"# {title}", ""]
    lines.append(f"**Merged TeX:** `{tex_path.name}`")
    if pdf_name:
        lines.append(f"**Source PDF:** `{pdf_name}`")
    if notes:
        note_list = ", ".join(f"`{note}`" for note in notes)
        lines.append(f"**Optional companion notes:** {note_list}")
    lines.extend(
        [
            "",
            "## How To Use",
            "",
            "1. Start from the relevant index entry, source map, or exam topic.",
            "2. Use the quick routing and heading index below to jump to the exact TeX line range for the matching section.",
            "3. If optional user-supplied companion notes were provided, read them only when they are needed for clarification or alternate ordering.",
            "4. Reopen the live PDF only for page-layout issues, figures, or equation verification that the TeX artifact does not capture cleanly.",
            "",
        ]
    )
    lines.extend(build_quick_routing(headings))
    lines.extend(["## Heading Index", ""])
    for heading in headings:
        page = heading["page"] if heading["page"] is not None else ""
        page_text = str(page) if page != "" else "?"
        lines.append(
            f"- type `{heading['class']}` | level `{heading['level']}` | pdf `{page_text}` | tex `{heading['line']}-{heading['end_line']}` | {md_cell(str(heading['title']))}"
        )

    # Build report
    unknown_pages = sum(1 for h in headings if h["page"] is None)
    class_counts = Counter(str(h["class"]) for h in headings)
    class_summary = ", ".join(
        f"{name}: {count}" for name, count in sorted(class_counts.items())
    )
    lines.extend(
        [
            "",
            "## Build Report",
            "",
            f"- Headings found: {len(headings)}",
            f"- Headings with unknown page (marked `?`): {unknown_pages}",
            f"- TOC parsed: {'yes' if toc_found else 'no — all page numbers may be missing'}",
            f"- Heading pattern used: `\\\\section*{{}}`, `\\\\section{{}}`, `\\\\section[short]{{long}}` (starred and unstarred, anywhere on a line)",
            f"- Heading classes: {class_summary}",
            "",
            "If heading count looks low for the document size, the TeX may use non-standard heading commands not matched by this script.",
            "",
            "## Equation and Figure Audit",
            "",
            f"- TeX line count: {audit['line_count']}",
            f"- Display math delimiters: `{audit['display_open']}` opens, `{audit['display_close']}` closes",
            f"- `aligned` blocks: `{audit['aligned_open']}` opens, `{audit['aligned_close']}` closes",
            f"- `array` blocks: `{audit['array_open']}` opens, `{audit['array_close']}` closes",
            f"- `equation` blocks: `{audit['equation_open']}` opens, `{audit['equation_close']}` closes",
            f"- Empty display-math blocks: `{audit['empty_display']}`",
            f"- Unicode replacement characters: `{audit['replacement_chars']}`",
            f"- `\\\\includegraphics` references: `{audit['includegraphics']}`",
            f"- Asset directory present beside TeX: {'yes' if audit['asset_dir_exists'] else 'no'}",
        "",
            "Warnings:",
        ]
    )
    warnings = audit_warnings(audit)
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "Equation audit checks structure only. For final worked answers, verify important equations against the PDF or another canonical source when the conversion quality is uncertain.",
        ]
    )

    # Agent notes section
    agent_notes = existing_agent_notes or PLACEHOLDER_AGENT_NOTES
    lines.extend(["", "## Agent Notes", "", agent_notes])

    lines.append("")
    return "\n".join(lines)


def default_output_path(tex_path: Path) -> Path:
    return tex_path.with_name(f"{tex_path.stem}.locator.md")


def main() -> int:
    args = make_parser().parse_args()
    tex_path = Path(args.tex).expanduser().resolve()
    if not tex_path.exists():
        raise SystemExit(f"TeX file not found: {tex_path}")
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else default_output_path(tex_path)
    )
    lines = tex_path.read_text(encoding="utf-8").splitlines()
    toc_map = parse_toc(lines)
    headings = parse_headings(lines, toc_map)
    toc_found = bool(toc_map)
    title = args.title or f"TeX Locator: {tex_path.stem}"
    audit = audit_tex(lines, tex_path)
    existing_agent_notes = extract_existing_agent_notes(output_path)
    output = build_markdown(
        tex_path,
        title,
        args.pdf,
        args.notes,
        headings,
        toc_found,
        audit,
        existing_agent_notes,
    )
    output_path.write_text(output, encoding="utf-8")
    print(f"Wrote {output_path}")
    unknown = sum(1 for h in headings if h["page"] is None)
    print(f"  {len(headings)} headings found, {unknown} with unknown page number")
    if not toc_found:
        print("  WARNING: TOC not found — page numbers will all be '?'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
