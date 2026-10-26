#!/usr/bin/env python3
"""Render a standalone LaTeX/TikZ diagram to SVG.

This is intended for Obsidian notes that should embed a verified static
diagram asset rather than compiling diagram code at view time.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout


def prepare_tex_for_dvisvgm(tex_path: Path, work_tex: Path) -> None:
    text = tex_path.read_text(encoding="utf-8")
    if r"\def\pgfsysdriver" not in text:
        package_re = re.compile(
            r"\\usepackage(?:\[[^\]]*\])?\{(?:tikz|pgfplots|circuitikz|chemfig|tikz-feynman)\}"
        )
        if r"\documentclass" in text or package_re.search(text):
            driver = r"\def\pgfsysdriver{pgfsys-dvisvgm.def}" + "\n"
            text = driver + text
    work_tex.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile a standalone LaTeX/TikZ source file to SVG."
    )
    parser.add_argument("tex", type=Path, help="Path to the .tex diagram source")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .svg path. Defaults to the input path with .svg suffix.",
    )
    parser.add_argument(
        "--keep-workdir",
        action="store_true",
        help="Keep the temporary compile directory for debugging.",
    )
    args = parser.parse_args()

    tex_path = args.tex.resolve()
    if not tex_path.exists():
        raise SystemExit(f"Input file not found: {tex_path}")
    if tex_path.suffix.lower() != ".tex":
        raise SystemExit("Input must be a .tex file")

    output = (args.output or tex_path.with_suffix(".svg")).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    work_parent = None if args.keep_workdir else tempfile.TemporaryDirectory()
    workdir = Path(work_parent.name if work_parent else tempfile.mkdtemp())
    try:
        work_tex = workdir / tex_path.name
        prepare_tex_for_dvisvgm(tex_path, work_tex)
        run(
            [
                "latex",
                "-halt-on-error",
                "-interaction=nonstopmode",
                work_tex.name,
            ],
            cwd=workdir,
        )
        dvi = work_tex.with_suffix(".dvi")
        if not dvi.exists():
            raise SystemExit(f"LaTeX did not create expected DVI: {dvi}")
        svg_tmp = workdir / output.name
        dvisvgm_output = run(
            [
                "dvisvgm",
                "--no-fonts",
                "--exact",
                f"--output={svg_tmp.name}",
                dvi.name,
            ],
            cwd=workdir,
        )
        ignored = re.search(r"WARNING:\s+(\d+)\s+PostScript specials ignored", dvisvgm_output)
        if ignored and int(ignored.group(1)) > 10:
            print(dvisvgm_output, file=sys.stderr)
            raise SystemExit("dvisvgm ignored PostScript specials; SVG would be incomplete")
        if not svg_tmp.exists() or svg_tmp.stat().st_size == 0:
            raise SystemExit("dvisvgm did not create a non-empty SVG")
        shutil.copy2(svg_tmp, output)
        print(output)
    finally:
        if work_parent is not None:
            work_parent.cleanup()
        elif not args.keep_workdir:
            shutil.rmtree(workdir, ignore_errors=True)
        else:
            print(f"Kept workdir: {workdir}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
