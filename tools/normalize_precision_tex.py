#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


PREAMBLE = r"""\documentclass[10pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage[version=4]{mhchem}
\usepackage{stmaryrd}
\usepackage{graphicx}
\usepackage[export]{adjustbox}
\graphicspath{{./images/}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.6em}

\begin{document}
"""


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize raw MinerU precision-API LaTeX into a smaller, compileable "
            "starter file for manual cleanup."
        )
    )
    parser.add_argument("input", help="Path to the raw precision .tex file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output path. Defaults to <input stem>.normalized.tex beside the input.",
    )
    parser.add_argument(
        "--image-width",
        type=float,
        default=0.58,
        help="Figure width fraction for extracted images. Default: 0.58",
    )
    return parser


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}.normalized.tex")


def extract_body(text: str) -> str:
    match = re.search(r"\\begin\{document\}(.*)\\end\{document\}", text, flags=re.S)
    if not match:
        raise SystemExit("Could not find \\begin{document} ... \\end{document} in input.")
    return match.group(1).strip()


def normalize_section_commands(body: str) -> str:
    def repl_factory(command: str):
        pattern = re.compile(
            rf"\\{command}\{{(.*?)\}}(?:\\label\{{.*?\}})?",
            flags=re.S,
        )

        def repl(match: re.Match[str]) -> str:
            title = " ".join(match.group(1).split())
            return rf"\{command}*{{{title}}}"

        return pattern, repl

    for command in ("section", "subsection", "subsubsection"):
        pattern, repl = repl_factory(command)
        body = pattern.sub(repl, body)
    return body


def normalize_images(body: str, image_width: float) -> str:
    def repl(match: re.Match[str]) -> str:
        image_name = Path(match.group(1)).name
        return (
            "\\begin{figure}[htbp]\n"
            "\\centering\n"
            f"\\includegraphics[width={image_width:.2f}\\textwidth]{{{image_name}}}\n"
            "\\end{figure}"
        )

    pattern = re.compile(
        r"\\pandocbounded\{\\includegraphics\[.*?\]\{images/([^}]+)\}\}",
        flags=re.S,
    )
    return pattern.sub(repl, body)


def cleanup_inline_artifacts(text: str) -> str:
    text = text.replace(r"\textquotesingle{}", "'")
    text = text.replace(r"\textquotesingle", "'")
    text = text.replace(r"\ldots{}", "...")
    text = text.replace(r"=\textgreater{}", r"$\Rightarrow$")
    text = re.sub(r"\s+([,.;:?!])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_page_number_line(stripped: str) -> bool:
    return bool(re.fullmatch(r"\d{1,3}", stripped))


def normalize_body(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    skip_alt_text = False
    just_saw_figure = False
    env_depth = 0
    in_display_math = False

    def flush_paragraph() -> None:
        nonlocal paragraph, just_saw_figure
        if not paragraph:
            return
        text = cleanup_inline_artifacts(" ".join(paragraph))
        lower = text.casefold()
        if just_saw_figure and (
            "simple line drawing" in lower
            or "labeled" in lower
            or "no text or symbols" in lower
            or "image" in lower
            or "photo" in lower
            or "diagram" in lower
        ):
            paragraph = []
            just_saw_figure = False
            return
        out.append(text)
        paragraph = []
        just_saw_figure = False

    for raw_line in lines:
        stripped = raw_line.strip()

        if skip_alt_text:
            if not stripped:
                skip_alt_text = False
            continue

        if stripped == r"natural\_image":
            flush_paragraph()
            skip_alt_text = True
            continue

        if is_page_number_line(stripped):
            continue

        if not stripped:
            continue

        if stripped == r"\[":
            flush_paragraph()
            out.append(stripped)
            in_display_math = True
            continue

        if stripped == r"\]":
            flush_paragraph()
            out.append(stripped)
            in_display_math = False
            continue

        if stripped.startswith(r"\begin{"):
            flush_paragraph()
            out.append(stripped)
            if stripped.startswith(r"\begin{figure}"):
                just_saw_figure = True
            env_depth += 1
            continue

        if stripped.startswith(r"\end{"):
            flush_paragraph()
            out.append(stripped)
            env_depth = max(0, env_depth - 1)
            continue

        if in_display_math or env_depth > 0:
            out.append(stripped)
            continue

        if stripped.startswith(
            (
                r"\section",
                r"\subsection",
                r"\subsubsection",
                r"\item",
                r"\centering",
                r"\includegraphics",
                r"\renewcommand",
            )
        ):
            flush_paragraph()
            out.append(stripped)
            continue

        paragraph.append(stripped)

    flush_paragraph()

    return "\n".join(out).strip()


def build_output(body: str) -> str:
    return PREAMBLE + "\n\n" + body + "\n\n\\end{document}\n"


def main() -> None:
    args = make_parser().parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else default_output_path(input_path)
    )

    text = input_path.read_text(encoding="utf-8")
    body = extract_body(text)
    body = normalize_section_commands(body)
    body = normalize_images(body, args.image_width)
    body = normalize_body(body)
    output_path.write_text(build_output(body), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
