# Cleanup Reporting

Be proactive in moving files to appropriate places at all times, especially files that are in the root.

Furthermore, when the durable final artifact or canonical copy already exists, proactively delete transient or superseded files instead of leaving clutter behind. Delete them before reporting what was removed.

When deleting files by agent judgment:

1. Tell the user what was deleted.
2. Group similar deletions together.
3. Give one short reason for each deleted group. For example, "the temporary image previews were one-off diagnostics for tuning the cleanup method."
4. If usefulness is genuinely uncertain, ask the user instead of guessing.

This rule applies to agent-judgment cleanup. User-requested deletions do not need to be reported.

## Precision API Cleanup

This workflow is **not** part of every MinerU precision-API conversion.

Do not run this cleanup workflow for whole lecture-note PDFs unless the user explicitly asks for cleanup. Lecture-note conversions are usually too large to clean cost-effectively, and their raw converted Markdown may be the intended durable text artifact.

Run this workflow when the user explicitly asks for cleanup after Precision API conversion, for example, "convert this using precision API and do a cleanup afterwards," or when a narrow question-answering workflow explicitly requires a cleaned question transcript.

### Precision API Cleanup Workflow

This is mainly for exam papers, problem sheets, exercise sheets, and other question-source PDFs converted with MinerU precision API.

1. Put the source PDF and conversion output in the appropriate raw-question folder.
2. Create a cleaned Markdown transcript from the MinerU Markdown.
3. Keep cleanup structural and conservative:
   - fix headings, question/part ordering, paragraphs, lists, tables, and front matter;
   - move margin marks such as `[8]` or `[3]` onto the correct question or subpart;
   - preserve exact wording where possible;
   - keep source figures/images needed by the question and update their paths if assets are moved;
   - fix obvious OCR or formatting corruption.
4. Do not run a full manual equation audit. MinerU precision API is normally accurate for mathematical equations that are not embedded in pictures.
5. Check an equation against the PDF or screenshot only when there is a concrete reason: it is visibly malformed, contradicts nearby text, has impossible syntax, is central to the exact question wording and suspicious, or is only present as an image.
6. Verify the cleaned transcript by scanning the structure, marks, required figures, and Markdown/math delimiter balance.
7. After the cleaned transcript is verified, discard superseded raw conversion artifacts.

When this cleanup workflow has been run and a cleaned transcript is verified, the canonical recovery path is the original PDF, not the raw conversion. Keep only:

1. the original PDF,
2. the cleaned Markdown transcript,
3. assets that are still referenced by the cleaned transcript or answer files.

Delete superseded `*.mineru_api.md`, `*.mineru_api_Locator.md`, JSON/model/layout sidecars, and unreferenced extracted images after the cleaned transcript is verified.

Startup canary: `CANARY_CLEANUP_A1`
