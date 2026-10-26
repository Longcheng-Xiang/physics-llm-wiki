# Tooling Guide

Use this note for tool choice, not as a general startup or retrieval-policy document. For exact PDF-conversion commands, defaults, outputs, and recovery procedures, read [[meta/pdf_conversion_methods]].

## Core Local Capabilities

| Capability | Use |
|---|---|
| File reading and search | Read files, list paths, and search for exact structure or terminology |
| Shell commands | Run local scripts, file operations, and inspections |
| PDF reading and extraction | Inspect targeted pages when a primary text artifact is unavailable or insufficient |
| Web lookup | Use only when local source artifacts are insufficient |

## PDF, Text, and Diagram Tools

| Tool/Script | Use |
|---|---|
| `tools/pdf_convert_mineru_api.py` | Convert a local PDF or remote PDF URL to Markdown through the MinerU precision API; writes `*.mineru_api.md` plus an extracted asset bundle |
| `tools/render_tex_diagram.py` | Render standalone LaTeX/TikZ diagram source to SVG using local `latex` and `dvisvgm` |
| `tools/preprocess_blue_ink_pages.py` | Pre-clean photographed pages before OCR by suppressing visually distinct blue handwritten annotations and rebuilding a combined PDF; requires Pillow, and HEIC input additionally uses macOS `sips` |
| `tools/build_tex_locator.py` | Build a locator from an existing merged TeX artifact and emit heading classes, line ranges, a build report, and an equation/figure audit |
| `tools/build_markdown_locator.py` | Build a Markdown-line locator and collapse consecutive duplicate headings so slide-deck routing stays usable |
| `tools/normalize_precision_tex.py` | Normalize a LaTeX export explicitly requested from MinerU |

## Tool-Choice Rules

- For canonical lecture-note PDFs, prefer the primary durable text artifact first and reopen the PDF only when that artifact is unavailable or insufficient. A locally supplied merged TeX artifact uses the `*.defaultmethod.tex` name; a Markdown-first source uses its MinerU precision-API Markdown artifact.
- For a new PDF conversion, use the MinerU precision-API procedure in `meta/pdf_conversion_methods.md`.
- Keep OCR off by default. Pass `--ocr` for exam papers, problem sheets, exercise sheets, and other question-source PDFs unless the user says otherwise.
- If a signed local upload times out before conversion, first suspect throughput to the object-storage host. Prefer a stable remote-URL submission, another network, a larger upload timeout, or carefully merged smaller page chunks.
- Before reopening a PDF, check the source locator, the primary text artifact, and `sources/cache/`.
- For photographed exercise sheets with blue handwritten annotations, consider a pre-OCR pass through `tools/preprocess_blue_ink_pages.py` and compare the cleaned OCR against the raw OCR rather than trusting either output alone.
- For Obsidian-facing Markdown, use `$...$` and `$$...$$`, not `\(...\)` or `\[...\]`.
- After building a locator, check its build report and equation/figure audit. If headings look incomplete or figures are placeholders, inspect manually and add `## Agent Notes`.

## Reference Files

| File | Use |
|---|---|
| `meta/pdf_conversion_methods.md` | Canonical operational guide for the MinerU precision-API conversion route |
| `sources/Lecture_Note_Inventory.md` | Canonical lecture-note artifact inventory |
| `sources/Diagram_Workflow_Guide.md` | Active diagram workflow: source-provided figures, Mermaid for simple flowcharts, and verified static SVG assets from local LaTeX/TikZ |
| `sources/*_Locator.md` | Exact line routing for primary lecture-note text artifacts |
| `meta/workflows.md` | Infrequent procedures for PDF ingestion, page extraction, and restructuring |
