# PDF Conversion Methods

Canonical operational guide for the PDF-conversion route included in this vault. Read this file before converting a PDF.

## Route Choice

| Route | Durable output | Use when |
|---|---|---|
| MinerU precision API | `*.mineru_api.md` plus `*_assets/` | A PDF or remote PDF URL needs to become agent-accessible Markdown |

Before conversion, move the PDF to its canonical vault location. Lecture notes belong under `lecture_notes_pdf/`; question sources belong in the matching generic question-source folder. Do not create a second durable copy.

## MinerU Precision API: PDF or URL to Markdown

### Requirements

- Python 3.10 or newer. The converter uses only the Python standard library.
- `curl` is optional. When available, it is tried first for local-file uploads and downloads; otherwise the converter uses Python's HTTP support.
- A personal MinerU API token is recommended for continued use. The converter includes a shared trial token for first-time evaluation.

### Token handling

Provide a personal MinerU credential through the `MINERU_API_TOKEN` environment variable, configured through the user's shell, operating-system credential tooling, or preferred secret manager. Any non-empty personal environment value overrides the shared trial token automatically. If no personal token is set, the converter uses the included shared token and prints the required trial notice after a successful conversion.

Never commit a personal token or place it in commands, logs, notes, or conversation output. The deliberately included shared trial credential is the only repository-token exception. Agents must follow the post-use reporting rule in `DIFFERENCES.md` whenever that shared token is used.

### Standard commands

Local PDF, normal source:

```bash
python3 tools/pdf_convert_mineru_api.py path/to/input.pdf --mode precision
```

Local question source requiring OCR:

```bash
python3 tools/pdf_convert_mineru_api.py path/to/input.pdf --mode precision --ocr
```

Remote PDF URL:

```bash
python3 tools/pdf_convert_mineru_api.py "https://example.com/input.pdf" --mode precision -o path/to/input.mineru_api.md
```

### Behavior and defaults

- Only `--mode precision` is supported.
- Default model: `vlm`; alternatives are `pipeline` and `MinerU-HTML`.
- Default language hint: `en`.
- Formula and table recognition are enabled unless explicitly disabled.
- OCR is disabled unless `--ocr` is passed.
- HTTP/upload timeout: 900 seconds; total polling timeout: 1800 seconds; polling interval: 3 seconds.
- Local files use MinerU's batch flow: request a signed object-storage upload URL, upload the PDF, poll the batch, download the returned archive, select the main Markdown, extract every other member, and rewrite relative asset links.
- Remote URLs use MinerU's URL-task flow and avoid the signed local upload.
- Default output is `<source>.mineru_api.md`; the default assets directory is `<output-without-.md>_assets/`.
- The downloaded result archive is discarded unless `--keep-zip` is passed.
- `--page-range` is forwarded as `page_ranges`: inside the local `files[]` record for uploads and at task level for a remote URL.
- `--extra-format docx`, `--extra-format html`, and `--extra-format latex` may be repeated to request additional exports.
- Local upload backend `auto` tries IPv4 `curl` first, then Python; use `--upload-backend curl` or `--upload-backend python` only for diagnosis.

### OCR policy

- Keep OCR off for ordinary lecture notes and born-digital sources.
- Pass `--ocr` for exam papers, problem sheets, exercise sheets, and other question-source PDFs unless the user explicitly says not to.
- OCR is not required for returned figures or extracted assets.

### After conversion

When future agents will revisit the Markdown, build a line locator:

```bash
python3 tools/build_markdown_locator.py path/to/input.mineru_api.md --source-pdf path/to/input.pdf
```

Use `tools/normalize_precision_tex.py` only for manual normalization of a LaTeX export requested with `--extra-format latex`.

Do not clean whole lecture-note conversions automatically. For a question source, run the precision cleanup workflow only when the user asks or when the question-answering workflow requires a cleaned transcript. Follow `.claude/rules/cleanup_reporting.md`; delete raw conversion artifacts only after the cleaned transcript has been verified.

### Signed-upload failure handling

If a local-file upload times out, the failure occurs before MinerU conversion. First suspect poor throughput to the signed object-storage host, not OCR, formula recognition, or a rejected PDF. In order of preference:

1. submit a stable remote PDF URL;
2. try a different network;
3. increase both timeouts, for example:

   ```bash
   python3 tools/pdf_convert_mineru_api.py path/to/input.pdf --mode precision --timeout 7200 --poll-timeout 7200
   ```

4. split a large PDF into smaller page chunks, convert them serially, merge the Markdown and assets carefully, and record the chunked conversion in the source summary or locator.
