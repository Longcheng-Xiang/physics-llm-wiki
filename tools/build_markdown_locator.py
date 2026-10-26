#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
PAGE_MARKER_RE = re.compile(r"^##\s+Page\s+\d+\s*$", re.IGNORECASE)
MERGE_CONTINUATION_STARTS = tuple(")]}:;,.!?")
MERGE_CONTINUATION_ENDS = ("(", "[", "{", "-", "/", ":")


@dataclass
class RawHeading:
    level: int
    line_no: int
    text: str


@dataclass
class Heading:
    level: int
    start_line: int
    text: str
    merged_heading_count: int = 1
    repeat_run_count: int = 1
    end_line: int = 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build a Markdown locator with line ranges. Consecutive duplicate "
            "headings are collapsed into single runs so slide-deck locators stay usable."
        )
    )
    parser.add_argument("markdown", help="Markdown file to index.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output locator path. Defaults to <markdown stem>_Locator.md beside the source file.",
    )
    parser.add_argument(
        "--title",
        help="Locator title override. Defaults to 'Source Locator: <markdown stem>'.",
    )
    parser.add_argument(
        "--source-pdf",
        help="Optional source PDF path to record in the locator header.",
    )
    parser.add_argument(
        "--notes",
        action="append",
        default=[],
        help="Companion note path to record in the locator header. Repeat for multiple notes.",
    )
    return parser


def build_output_path(markdown_path: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    return markdown_path.with_name(f"{markdown_path.stem}_Locator.md")


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path.resolve())


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def dedupe_key(text: str) -> str:
    return normalize_space(text).casefold()


def should_merge_heading_lines(first: str, second: str) -> bool:
    first = normalize_space(first)
    second = normalize_space(second)
    if not first or not second:
        return False
    if first.endswith(MERGE_CONTINUATION_ENDS):
        return True
    first_char = second[0]
    return first_char.islower() or first_char in MERGE_CONTINUATION_STARTS


def only_blank_between(lines: list[str], first_line: int, second_line: int) -> bool:
    for idx in range(first_line, second_line - 1):
        if lines[idx].strip():
            return False
    return True


def parse_raw_headings(lines: list[str]) -> list[RawHeading]:
    raw: list[RawHeading] = []
    for line_no, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if not match:
            continue
        raw.append(
            RawHeading(
                level=len(match.group(1)),
                line_no=line_no,
                text=normalize_space(match.group(2)),
            )
        )
    return raw


def merge_split_headings(raw: list[RawHeading], lines: list[str]) -> tuple[list[Heading], int]:
    merged: list[Heading] = []
    merge_count = 0
    i = 0
    while i < len(raw):
        current = raw[i]
        text = current.text
        heading_count = 1
        j = i
        while j + 1 < len(raw):
            nxt = raw[j + 1]
            if not only_blank_between(lines, raw[j].line_no, nxt.line_no):
                break
            if not should_merge_heading_lines(text, nxt.text):
                break
            text = normalize_space(f"{text} {nxt.text}")
            heading_count += 1
            merge_count += 1
            j += 1
        merged.append(
            Heading(
                level=current.level,
                start_line=current.line_no,
                text=text,
                merged_heading_count=heading_count,
            )
        )
        i = j + 1
    return merged, merge_count


def collapse_duplicate_runs(headings: list[Heading]) -> tuple[list[Heading], int]:
    if not headings:
        return [], 0

    collapsed: list[Heading] = [headings[0]]
    collapse_count = 0
    for heading in headings[1:]:
        previous = collapsed[-1]
        if heading.level == previous.level and dedupe_key(heading.text) == dedupe_key(previous.text):
            previous.repeat_run_count += 1
            collapse_count += 1
            continue
        collapsed.append(heading)
    return collapsed, collapse_count


def assign_line_ranges(headings: list[Heading], line_count: int) -> None:
    for idx, heading in enumerate(headings):
        if idx + 1 < len(headings):
            heading.end_line = headings[idx + 1].start_line - 1
        else:
            heading.end_line = line_count


def render_notes(notes: list[str]) -> str:
    if not notes:
        return "`none`"
    return ", ".join(f"`{note}`" for note in notes)


def render_heading_entry(heading: Heading) -> str:
    extras: list[str] = [f"level `h{heading.level}`", f"md `{heading.start_line}-{heading.end_line}`"]
    if heading.repeat_run_count > 1:
        extras.append(f"repeat-run `{heading.repeat_run_count}`")
    if heading.merged_heading_count > 1:
        extras.append(f"joined-heading-lines `{heading.merged_heading_count}`")
    return f"- {' | '.join(extras)} | {heading.text}"


def build_locator_text(
    markdown_path: Path,
    source_pdf: str | None,
    notes: list[str],
    headings: list[Heading],
    line_count: int,
    raw_count: int,
    merged_count: int,
    split_merge_count: int,
    duplicate_collapse_count: int,
    page_marker_count: int,
    root: Path,
    title: str,
) -> str:
    markdown_rel = relpath(markdown_path, root)
    source_pdf_line = (
        f"**Source PDF:** `{source_pdf}`"
        if source_pdf
        else "**Source PDF:** `unknown`"
    )
    quick_routing = "\n".join(
        f"- `md {heading.start_line}-{heading.end_line}` | {heading.text}"
        for heading in headings
        if heading.level == 1
    )
    if not quick_routing:
        quick_routing = "_No level-1 headings found._"

    heading_index = "\n".join(render_heading_entry(heading) for heading in headings)
    if not heading_index:
        heading_index = "_No headings found._"

    return "\n".join(
        [
            f"# {title}",
            "",
            f"**Primary Markdown:** `{markdown_rel}`",
            source_pdf_line,
            f"**Optional companion notes:** {render_notes(notes)}",
            "",
            "## How To Use",
            "",
            "1. Start from the relevant index entry, source map, or exam topic.",
            "2. Use the quick routing and heading index below to jump to the exact Markdown line range for the matching slide-title run.",
            "3. If optional user-supplied companion notes were provided, read them only when they are needed for clarification, ordering, or shorthand decoding.",
            "4. Reopen the live PDF only for layout-dependent figures or if the Markdown extraction is locally unclear.",
            "",
            "## Quick Routing",
            "",
            "Major heading runs. Consecutive duplicate slide titles are collapsed into a single line-range entry.",
            "",
            quick_routing,
            "",
            "## Heading Index",
            "",
            heading_index,
            "",
            "## Build Report",
            "",
            f"- Markdown line count: {line_count}",
            f"- Raw heading lines found: {raw_count}",
            f"- Effective headings after split-heading joins: {merged_count}",
            f"- Split heading joins applied: {split_merge_count}",
            f"- Consecutive duplicate headings collapsed: {duplicate_collapse_count}",
            f"- Heading runs in final locator: {len(headings)}",
            f"- Page markers found: {page_marker_count}",
            "",
            "## Agent Notes",
            "",
            "- This locator is Markdown-line-based rather than TeX-line-based.",
            "- Consecutive repeated slide titles are collapsed into single locator runs so slide decks do not drown retrieval in duplicate headings.",
            "- Adjacent heading fragments are joined when the second line is clearly a continuation of the first, which helps with slide titles split across multiple heading lines.",
            f"- Regenerate this file with `python3 tools/build_markdown_locator.py '{markdown_rel}'` after future source updates.",
            "",
        ]
    )


def main() -> int:
    args = make_parser().parse_args()
    root = Path.cwd().resolve()
    markdown_path = Path(args.markdown).expanduser().resolve()
    if not markdown_path.exists():
        raise SystemExit(f"Markdown file not found: {markdown_path}")

    output_path = build_output_path(markdown_path, args.output)
    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    page_marker_count = sum(1 for line in lines if PAGE_MARKER_RE.match(line))

    raw_headings = parse_raw_headings(lines)
    merged_headings, split_merge_count = merge_split_headings(raw_headings, lines)
    collapsed_headings, duplicate_collapse_count = collapse_duplicate_runs(merged_headings)
    assign_line_ranges(collapsed_headings, len(lines))

    title = args.title or f"Source Locator: {markdown_path.stem}"
    locator_text = build_locator_text(
        markdown_path=markdown_path,
        source_pdf=args.source_pdf,
        notes=args.notes,
        headings=collapsed_headings,
        line_count=len(lines),
        raw_count=len(raw_headings),
        merged_count=len(merged_headings),
        split_merge_count=split_merge_count,
        duplicate_collapse_count=duplicate_collapse_count,
        page_marker_count=page_marker_count,
        root=root,
        title=title,
    )
    output_path.write_text(locator_text, encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
