# Output Format

For direct user-facing replies in the current agent conversation interface, write inline math with TeX backslash-parentheses delimiters, `\(...\)`, because this is the inline format that renders clearly in the conversation.

Do not use single-dollar inline math, `$...$`, in direct conversation replies.

Display math in direct conversation replies is fine when useful.

This direct-conversation rule applies only to conversation output.

For any Markdown file written for the Obsidian vault, including temporary Markdown Q&A notes, use Obsidian-safe math delimiters: `$...$` for inline math and `$$...$$` for display math. Do not write `\(...\)` or `\[...\]` in vault Markdown prose. The only exceptions are literal code snippets or verbatim source quotations where preserving the original syntax is the point.

Apply the vault Markdown delimiter rule at write time as a wiki-wide default.

## Vault MathJax Compatibility

For angstrom units in vault Markdown math, do **not** use `\AA`, `\mathrm{\AA}`, or `\text{\AA}`. Obsidian's MathJax rendering may display `\AA` literally or as an error even when the source TeX defines it.

Use `\mathring{\mathrm{A}}` instead, for example `$2.90\,\mathring{\mathrm{A}}$` and `$1.99\,\mathring{\mathrm{A}}^{-1}$`. When converting source TeX, question text, answers, workflow logs, or source extracts into vault Markdown, normalize angstrom units to this form. Raw `.defaultmethod.tex` artifacts may keep their original `\AA` definitions and source syntax.

## Delimiter Audit Toggle

Current setting: `OFF`

When `OFF`: do not run a separate delimiter audit merely to confirm the Markdown math-delimiter rule. Write the correct delimiters at edit time. Run an explicit delimiter check only if the user requests it or there is a concrete reason to suspect mixed delimiters in files being edited.

When `ON`: after any workflow that writes Markdown files, audit the Markdown files changed by that workflow for `\(...\)` or `\[...\]` math delimiters in prose and fix them to `$...$` or `$$...$$`. Do not scan the whole vault unless the user explicitly requests a vault-wide audit.

This file-specific rule covers vault Markdown files, Workflow A/B/C Markdown outputs, and source extracts unless a narrower rule explicitly says otherwise. `.defaultmethod.tex` artifacts and other non-Markdown targets keep their own format.

Startup canary: `CANARY_OUTPUT_FORMAT_A1`
