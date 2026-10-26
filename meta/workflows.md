# Operational Workflows

Reference document for infrequent operations. Do not read this for routine question answering, problem sets, exam questions, harvest, or retrieval; those workflows are auto-loaded through `.claude/rules/`.

Open this only for:

- new lecture-note PDFs;
- targeted page extraction; or
- restructuring or optimization.

---

## Lecture-Note PDF

Use this when the user provides a canonical lecture-note PDF. Before converting it, read `meta/pdf_conversion_methods.md` for the current commands, defaults, outputs, and recovery procedures.

1. Confirm that it is a canonical lecture-note PDF rather than a supporting attachment.
2. Move or rename the PDF into its canonical home under `lecture_notes_pdf/`. Do not leave a duplicate at the repository root or in a transient location.
3. If the same PDF already exists in its canonical home, use that copy and remove the transient duplicate.
4. Register it in `sources/Lecture_Note_Inventory.md`.
5. Create or update its primary durable text artifact with the included MinerU precision-API procedure. If a reviewed merged `*.defaultmethod.tex` artifact already exists, preserve and use it rather than reconverting the source without a concrete reason.
6. Create or update its source map in `sources/`.
7. Create or update its source locator when the primary text artifact exists.
8. Create or update its lecture-note summary page.
9. Do not extract the full PDF again when a sufficient primary text artifact already exists.
10. Use optional user-supplied notes to improve routing or explanation only when the user provides or requests them; preserve the canonical lecture note as the technical authority.
11. Update `index.md` and `log.md` when source coverage changes.

### Targeted Page Extraction for Obsidian

Use this when the user asks for a particular PDF page to be converted to Markdown.

1. Work locally from the canonical PDF.
2. Extract the target page with the available local PDF tools first.
3. If the page is prose-dominant and extraction is clean, return the Markdown directly.
4. If equations or symbols are degraded, render the page to an image and inspect it visually.
5. Reconstruct the mathematics manually from the rendered page when needed.
6. Return Obsidian-compatible Markdown: inline math with `$...$` and display math with `$$...$$`.
7. Do not return broken extraction tokens when the user asked for final Markdown.
8. Treat dense mathematical pages as likely manual-cleanup cases even when prose extraction is usable.

### MinerU Precision-API Markdown Route

The conversion script is `tools/pdf_convert_mineru_api.py`. Supply its credential through the `MINERU_API_TOKEN` environment variable and follow `meta/pdf_conversion_methods.md` for commands and token safety.

#### OCR policy

- Keep OCR off by default.
- Pass `--ocr` for exam papers, problem sheets, exercise sheets, and other question-source PDFs unless the user explicitly asks not to.
- OCR controls recognition of scanned or rasterized text; it is not required for returned figures or extracted assets.

#### Cleanup policy

- Cleanup is not automatic. Trigger it only when the user asks for cleanup after conversion or when a narrow question-answering workflow needs a cleaned question transcript.
- Do not clean whole lecture-note conversions by default; their raw precision-API Markdown is normally the intended durable artifact.
- For question material, keep cleanup structural and conservative: repair hierarchy, formatting, tables, obvious OCR errors, image paths, and misplaced margin marks.
- Do not manually audit every equation. Check against the source only when an equation is visibly malformed, suspicious, contradicted by nearby wording, central to exact wording, or embedded as an image.
- After a cleaned transcript is verified, keep the original PDF, the cleaned Markdown, and referenced assets. Remove superseded raw conversion files, generated sidecars, and unreferenced extracted images.

#### Signed-upload failure handling

If a local upload times out, the failure occurs before conversion. Do not infer that OCR settings or the document itself caused it. Prefer, in order:

1. a stable remote PDF URL;
2. another network;
3. a substantially larger upload timeout; or
4. smaller page chunks converted serially and then merged carefully, with the chunked conversion recorded in the source summary or locator.

---

## Conceptual Physics Question

1. Apply the default retrieval order in `.claude/rules/retrieval_order.md`.
2. Use relevant synthesis pages, source maps, summaries, locators, and targeted primary text before opening the original PDF.
3. Open only the PDF pages needed to resolve a concrete gap, inspect a figure, or check suspicious conversion.
4. If live PDF extraction supplies reusable material, add or widen an appropriate cleaned cache or source-access note.
5. File reusable clarifications back into the narrowest wiki document through the conversation-harvest rule.

---

## Optimize or Restructure

1. Read `CLAUDE.md`, `DIFFERENCES.md`, `index.md`, the top 20 lines of `log.md`, and this file. Read more of `log.md` only later and only by a targeted line range when needed.
2. Keep source material in place unless moving it produces a clear retrieval benefit.
3. Update routing documents in the same pass as any structural change.
4. Prefer small, coherent changes over broad rewrites.
