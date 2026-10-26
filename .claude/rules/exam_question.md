# Exam Question

## Mandatory Workflow Selection

Before solving an exam problem, determine whether the user explicitly selected Workflow A, Workflow B, or Workflow C.

- If the user selected one, proceed with that workflow without asking again.
- If the user did not select one, stop before retrieval, answering, or writing files. Ask which workflow to use and briefly explain:
  - **Workflow A:** full answer plus a workflow log and source extracts, each output in Markdown files;
  - **Workflow B:** full answer plus a workflow log, output in the current dialogue;
  - **Workflow C:** full answer only, output in a Markdown file.

All three workflows use the same retrieval process. Suggest Workflow B first to users who are new to the wiki. Do not provide an ordinary dialogue answer while the workflow choice is unresolved.

## Workflow A

If the user explicitly selects Workflow A:

1. Follow **Workflow A** (`workflow_a.md`, auto-loaded).
2. If the exam source is only a local PDF and no canonical text artifact exists yet, read `meta/pdf_conversion_methods.md`, then convert it with `tools/pdf_convert_mineru_api.py` using precision mode and `--ocr`. Keep the raw PDF, converted Markdown, and required extracted assets together under the generic source path `questions_and_answers/exam_questions_raw/<course>/<paper>/`.
3. Run Precision API cleanup only if the user asks for cleanup or if the current Workflow A run requires a cleaned question transcript before answering. The cleaned Markdown transcript then becomes the exact-question wording source. Delete raw MinerU Markdown and sidecars only after the cleaned transcript has been verified.
4. Use the raw or cleaned Precision API Markdown as the default exact-question wording source, depending on whether cleanup was triggered. Reopen the PDF only for margin marks, symbol or format corruption, suspicious equations, or figure checks that require an extracted asset or page image. Write the answer under `questions_and_answers/exam_questions/<course>/<paper>/` using the generic form `<paper>_Questions_and_Answers.md`.
5. If the request covers multiple exam questions, apply Workflow A to each question **serially**.
6. For question $n$, before reading sources for question $n+1$, complete:
   - the answer-file update;
   - the workflow log;
   - the source extracts;
   - any exam-follow-up writebacks directly caused by question $n$.
7. Exam-follow-up writebacks may include:
   - creating or updating a synthesis page if the answer is genuinely cross-cutting;
   - updating source-summary or structure files if that question itself requires it.
8. When the exam source provides explicit part-marks, preserve them in the paper Q&A file as part of the exact question wording. If the marks are visible only in the PDF margin and not in the text artifact, check the PDF directly and annotate the corresponding subparts with `[n]`.
9. Always structure the answer by explicit part labels when present, using only those labels as headings, for example `### (a)`, not `### (a) [4]`. Preserve marks in the exact question wording. If an exam question has no labels such as `(a)`, `(b)`, or `(i)` but its paragraphs or subquestions have explicit marks, use those marks as answer subheadings, for example `### \[3\]`, `### \[2\]`, `### \[4\]`, and `### \[12\]`, in the same order as the question. Escape the square brackets in Markdown headings so Obsidian's outline displays them correctly.
10. After the full Workflow A run is complete, do any remaining session-level harvest work, such as `log.md` updates or batch-level summary-document updates.

## Workflow B

If the user explicitly selects Workflow B:

1. Follow **Workflow B** (`workflow_b.md`, auto-loaded).
2. Apply the same source preparation, exact-question wording, mark preservation, answer structure, and part-by-part processing requirements stated above for Workflow A wherever they apply.
3. Return the full answer and workflow log in the current dialogue. Do not write an answer file or create source-extract files.

## Workflow C

If the user explicitly selects Workflow C:

1. Follow **Workflow C** (`workflow_c.md`, auto-loaded).
2. Apply the same source preparation, exact-question wording, mark preservation, answer structure, part-by-part processing, immediate writebacks, and strict question-by-question serial order stated above for Workflow A.
3. For question $n$, complete the answer-file update and any immediate writebacks directly caused by question $n$ before reading sources for question $n+1$.
4. Do not create or update a workflow-log file or source-extract file.
5. After the full Workflow C run is complete, do any remaining session-level harvest work, such as `log.md` updates or batch-level summary-document updates.

Startup canary: `CANARY_EXAM_F1`
