# Retrieval Order

Use this default retrieval rule after resolving any workflow choice required by `DIFFERENCES.md`. General conceptual, explanatory, interpretive, and open-ended physics questions use this retrieval order directly and are answered normally in the current dialogue.

## Source Preparation

Check the source format before retrieval:

- **PDF only, with no primary text artifact:** convert it first with the included MinerU precision-API procedure, then continue. Keep OCR off by default. Use OCR when the source is question material, such as an exam paper, problem sheet, or exercise sheet, unless the user says otherwise.
- **Converted TeX, Markdown, or plain text:** use it directly.
- **Image:** transcribe or convert it to Markdown with an available extraction tool before proceeding.

If the task clearly concerns a specific course and a matching rule exists under `course_rules/`, read that rule before making course-specific retrieval decisions. Course rules may refine or override the generic defaults below.

## Retrieval Sequence

For technical physics work, use this order:

1. `index.md`
2. relevant synthesis pages
3. the relevant lecture-note source map, summary page, and locator
4. the targeted primary lecture-note text artifact named by the locator or summary page, normally a merged `.defaultmethod.tex` artifact; for a Markdown-first source family, use its MinerU precision-API Markdown artifact
5. optional user-supplied notes only when the user explicitly asks for them, a selected workflow includes them, or an approved lecture-note artifact points to them for clarification
6. the original lecture-note PDF as a fallback for figures, page layout, suspicious conversion, or details unavailable in the primary text artifact

Original PDF access is a fallback, not the default detailed-query path. If a primary text artifact already exists, use it first and open only the targeted PDF pages needed to resolve a concrete gap.

For technical claims, canonical lecture-note artifacts outrank optional user-supplied notes. Treat "lecture notes" as the canonical professor-provided sources and "my notes" as optional user material supplied separately.

Startup canary: `CANARY_RULES_D1`
