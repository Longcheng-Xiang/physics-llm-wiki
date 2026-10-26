# Vault Status

This file describes the physics coverage and working facilities available in this vault. Start with `CLAUDE.md` for agent startup rules and `index.md` for topic routing.

## Available From First Use

- The startup and retrieval rules are present under `CLAUDE.md`, `DIFFERENCES.md`, and `.claude/rules/`.
- Source maps, summaries, locators, and the exact expected local paths for the lecture-note corpus are available for the coverage listed below. The original PDFs and complete converted bodies must be supplied locally by the user.
- Workflows A, B, and C are available for worked physics problems.
- General conceptual, explanatory, interpretive, and open-ended physics questions can be answered normally in dialogue after the default retrieval process.
- Generic exam-question and problem-set workspaces are ready for material supplied by the user.
- Worked examples demonstrate answer files, workflow logs, source extracts, and a static SVG diagram.
- Local tools are included for MinerU conversion, diagram rendering, page-image preprocessing, locator construction, and precision-TeX normalization.

## Physics Coverage

| Area | Expected user-supplied authority layer | Available routing layer |
|---|---|---|
| B2 Symmetry and Relativity | Canonical PDF and merged TeX | Source map, summary, and locator |
| B3 Atomic Physics | Four canonical PDFs and four merged TeX artifacts covering the principal atomic-physics notes, lasers, quantum notes, and radiation transport | Main source map and summary; a locator for each source family |
| B4 Nuclear and Particle Physics | Five canonical PDFs and five MinerU Markdown artifacts, including their referenced figure assets | Shared source map and summary; a locator for each source family |
| B5 General Relativity | Canonical PDF and merged TeX | Locator |
| B6 Condensed Matter Physics | Canonical PDF and merged TeX | Locator |

The exact expected file-level paths and B4 source priority are recorded in `sources/Lecture_Note_Inventory.md`. Once the user has supplied the source corpus, use the source locator and targeted primary text before reopening the PDF. Use the PDF when figures, page layout, or a suspicious conversion require direct checking.

## Worked-Problem Workflows

- **Workflow A:** writes a full answer, workflow log, and source extracts to Markdown files.
- **Workflow B:** returns a full answer and workflow log in the current dialogue.
- **Workflow C:** writes a full answer to a Markdown file without separate workflow-log or source-extract files.

All three use the same source-preparation and retrieval process. When a user requests a worked solution, derivation, calculation, exercise, or exam problem without selecting a workflow, ask them to choose before beginning. `DIFFERENCES.md` and `.claude/rules/` define the complete behavior.

## Included Worked Examples

- `questions_and_answers/problem_sets/B3_Atomic_Problems_Questions_and_Answers.md` contains complete Q7 and Q9 worked answers.
- The B3 Q7 and Q9 examples each include a workflow log and source-extract file.
- The Q9 example includes a referenced static SVG diagram under `questions_and_answers/problem_sets/B3_Atomic_Problems_answer_assets/diagrams/`.
- `questions_and_answers/problem_sets/B5_2025_PS2_Updated_Questions_and_Answers.md` contains the retained B5 Q3 and Q4 worked-answer document and its follow-up explanations.

## Question Workspaces

- Exam answers: `questions_and_answers/exam_questions/<course>/<paper>/<paper>_Questions_and_Answers.md`
- Exam sources supplied by the user: `questions_and_answers/exam_questions_raw/<course>/<paper>/<source-file>`
- Problem-set answers: `questions_and_answers/problem_sets/<problem-set>_Questions_and_Answers.md`

This vault does not include a pre-existing exam-paper collection or original question-source files. The generic paths are workspaces for material a user adds later. See `questions_and_answers/exam_questions/README.md` for naming conventions.

## Tooling

The six included scripts under `tools/` provide:

1. MinerU precision-API PDF conversion;
2. local LaTeX/TikZ-to-SVG rendering;
3. photographed-page preprocessing;
4. TeX locator construction;
5. Markdown locator construction; and
6. MinerU precision-TeX normalization.

Read `meta/tools.md` before choosing a tool and `meta/pdf_conversion_methods.md` before converting a PDF. New MinerU conversions require the user's own `MINERU_API_TOKEN`. Some local operations also require the external programs or Python packages named in the tooling guide.

## Current Limits

- Original lecture-note PDFs, complete converted lecture-note bodies, and conversion-generated lecture-note assets are not bundled. Source-grounded retrieval requires the user to add lawfully obtained material at the paths recorded in `sources/Lecture_Note_Inventory.md`.
- Optional user lecture, tutorial, and background notes represented by placeholders are not bundled with the vault.
- Existing worked-answer coverage is limited to the examples listed above; the generic question workspaces otherwise begin empty.
- B2 and the main B3 and B4 families have maps and summaries. The remaining listed source families rely on their locators after the corresponding primary text artifacts are supplied.
- The cache layer currently provides routing guidance but no substantial collection of pre-extracted sections; locators and user-supplied primary text artifacts are the normal retrieval path.
- The locators retain references to expected `*.defaultmethod.tex` artifacts, but those artifacts and their original conversion method are not included. Use the included MinerU procedure for new conversions.

Update this file whenever source coverage, worked-answer coverage, workflow availability, or a major usability gap changes.
