# Problem Set Question (Workflow A)

Use this workflow only after the user explicitly selects Workflow A for a worked solution, derivation, calculation, exercise, or exam problem. Also continue it without a new selection when the user explicitly asks to continue, correct, or add material to the existing Workflow A files for the same problem. Follow every step in order; do not abbreviate.

Before a Workflow A run that may require an answer-generated figure, sketch, graph, Feynman or quark-flow diagram, energy-level diagram, lineshape, transition diagram, or similar asset, read `sources/Diagram_Workflow_Guide.md` once before doing the figure work. In a multi-question run, one full read at the start is enough unless the guide changes during the session. Use a verified static SVG rendered from local LaTeX/TikZ rather than a view-time diagram renderer.

Before source-question preparation or retrieval, identify the course and read its matching rule under `course_rules/` if one exists. Do this before opening the question text artifact, locator, lecture-note text artifact, or optional user-supplied notes. A course rule may refine the generic retrieval procedure below and takes priority if the two conflict.

## Source-Question Preparation

- If the question is available only as a local PDF and no canonical text artifact exists, read `meta/pdf_conversion_methods.md` and convert it with the included MinerU precision-API procedure before retrieval. Use OCR for question material unless the user says otherwise.
- Keep the original PDF, converted Markdown, and any required extracted assets together. For exam material, use the generic path `questions_and_answers/exam_questions_raw/<course>/<paper>/<source-file>`. For problem-set source material, use `questions_and_answers/problem_sets/<problem-set-source-file>`.
- Run the cleanup procedure in `cleanup_reporting.md` only when the user requests cleanup or when a verified cleaned transcript is needed to establish exact question wording.
- Use the raw or cleaned MinerU Markdown as the exact-question wording source, depending on whether cleanup was performed. Reopen the PDF only to check margin marks, repair concrete conversion problems, or inspect figures that matter to the question.

## Retrieval (complete before writing)

Use the vault's retrieval order for every Workflow A problem. Keep retrieval narrow and follow this sequence:

1. Read `index.md` and locate the relevant source family.
2. Read relevant synthesis pages, if any.
3. Read the relevant lecture-note source map, summary page, and locator.
4. Read the targeted lines in the primary lecture-note text artifact named by the locator or summary.
5. Read optional user-supplied notes only when the user explicitly requests them, the selected workflow requires them, or an approved source artifact points to them for clarification.
6. Open only the targeted pages of the original lecture-note PDF when a figure, page-layout issue, suspicious conversion, or missing detail requires it.

Do not search beyond this scope unless a required source is genuinely missing or a locator explicitly points onward. Once the relevant locator is found, stay within these steps unless a concrete gap requires one narrowly justified lookup.

For a question with clearly labelled parts such as `(a)`, `(b)`, `(i)`, or `(ii)`, apply the retrieval sequence at the level of the current part whenever different parts need different material. If a question has no explicit labels but is partitioned by marks such as `[3]`, `[2]`, and `[4]`, treat each marked segment as a part. Read the full question first so its structure is known, but do not retrieve later parts before the current part has been written into the answer file.

## Answer

Write the answer in the appropriate Q&A Markdown file, including the exact question wording. Use `questions_and_answers/exam_questions/<course>/<paper>/<paper>_Questions_and_Answers.md` for an exam or `questions_and_answers/problem_sets/<problem-set>_Questions_and_Answers.md` for a problem set. Preserve every explicit part-mark in that wording; if a mark is visible only in the original PDF, verify it there and append it to the corresponding question text. Synthesise from the retrieved sources and state where substantial own knowledge fills a gap. The answer must be a worked derivation or solution, not a recap. Keep it mostly as continuous derivation or prose rather than heavily subdivided scaffolding. Do not add a final `Summary`, `Recap`, `Takeaway`, or similar closing section.

If the question has labelled parts, use only the corresponding labels as answer subheadings, for example `### (a)` and `### (b)`. Do not append marks to those headings; preserve marks in the exact question wording. If marks partition an otherwise unlabelled question, use one escaped mark heading per segment, for example `### \[3\]`, `### \[2\]`, and `### \[4\]`, so the headings render correctly in Obsidian. The continuous-derivation preference applies inside each required part heading.

Unless the user explicitly asks for another structure, avoid internal headings such as `Step`, `Physical interpretation`, `Connection`, or `Takeaway`. Required question-part or mark headings are the exception.

For a multi-part question, finish the current part's retrieval and write that part into the Q&A file before starting the next part. After every part of the current question is answered, create the workflow log and source extracts. Only then may work begin on another question.

## Output Files

Create one complete output set for every question, even when two questions use overlapping sources.

1. **Answer file:** update the appropriate Q&A Markdown file with the exact question wording and worked answer.
2. **Workflow log:** create the matching `*_Workflow_Log.md` beside the answer file. Use a numbered chronological list, with each retrieval step occupying no more than one line and the final numbered item reading `Wrote answer`. End with `Own knowledge used` and `Steps skipped` sections. Use Obsidian-safe MathJax delimiters. `questions_and_answers/problem_sets/B3_Atomic_Problems_Q7_Workflow_Log.md` is the canonical format example.
3. **Source extracts:** create the matching `*_Source_Extracts.md` beside the answer file. Include only passages actually used. Each passage must have a `##` heading that identifies its source file and targeted range, followed by the passage in a Markdown blockquote. Normalize mathematical delimiters to Obsidian-safe `$...$` and `$$...$$`; do not present the extracts as raw code blocks. Never omit this file merely because another question used the same range. `questions_and_answers/problem_sets/B3_Atomic_Problems_Q7_Source_Extracts.md` is the canonical format example.

## Completion and Follow-Ups

A Workflow A question is complete only when its answer file, workflow log, source extracts, and any immediate synthesis or source-artifact writebacks caused by that question are complete. In a multi-question request, finish that full set before retrieving for the next question. Do not batch retrieval across questions.

Treat a follow-up as an in-file Workflow A continuation only when the user writes it inside the existing Q&A file or explicitly asks to continue, correct, or add material to that file. In that case, repeat the relevant retrieval before editing, turn scratch wording into a clear follow-up heading plus a full derivation-style answer, and match the depth and style of the existing worked answer. Do not create a new workflow log or source-extract file for an in-file follow-up unless the user asks for one.

Answer a conversational clarification about the existing result normally in the current dialogue without editing files or automatically rerunning the complete workflow. A distinct new problem requires a new A/B/C choice under `DIFFERENCES.md`.

## Rules

- Never write the answer before completing the retrieval sequence for the current question or current part.
- If a retrieval step is unavailable or skipped, record it under `Steps skipped` in the workflow log.
- If own knowledge is used substantially, disclose it in the workflow log and in the answer where relevant.
- Follow `sources/Diagram_Workflow_Guide.md` for answer-generated figures and use verified static SVG assets by default. Use only the palette roles `gray`, `blue!50`, and `red` unless the guide explicitly authorizes another role; do not use explicit `black` for answer-generated diagram elements.
- Do not update `log.md` for a single question; log entries are for session-level harvests.
- Do not print the worked answer in the conversation. A brief confirmation that the files were written is sufficient.

Startup canary: `CANARY_WORKFLOW_A_H1`
