# Vault Differences and Mandatory Rules

This file records important information and rules for the version of the vault distributed through GitHub, particularly where it differs from the developer's original working vault.

The rules in this file are mandatory for agents operating in this vault. They override conflicting default behavior elsewhere in the vault.

## Required workflow choice for worked physics problems

Whenever a user requests a worked solution, derivation, calculation, exercise, or exam problem, the agent must first determine whether the user explicitly selected Workflow A, Workflow B, or Workflow C.

- If the user selected one of the three workflows, proceed with that workflow without asking again.
- If the user did not select a workflow, stop before retrieval, answering, or writing files. Ask the user which workflow to use and briefly introduce all three choices:
  - **Workflow A:** Full answer plus a workflow log and source extracts, each output in Markdown files.
  - **Workflow B:** Full answer plus a workflow log, output in the current dialogue.
  - **Workflow C:** Full answer only, output in a Markdown file.

All three workflows use the same retrieval process. Suggest Workflow B first to users who are new to the wiki.

For a request in this worked-problem scope, the absence of a workflow choice must not be treated as permission to provide an ordinary answer in the dialogue. Wait for the user's selection before solving the problem.

General conceptual, explanatory, interpretive, and open-ended physics questions do not require a workflow choice. Answer them normally in the current dialogue after following the vault's default retrieval order; do not invoke Workflow A merely because the subject is physics.

Workflow selection belongs to the problem for which it was chosen, not automatically to every later message. After a Workflow A answer:

- answer a conversational clarification about the existing answer normally in the dialogue, without editing files or automatically rerunning the complete Workflow A procedure;
- if the user explicitly asks to continue, correct, or add material to the existing Workflow A files, continue Workflow A without requesting another workflow choice; and
- require a new A/B/C choice for a distinct new problem.

## Omitted conversion method

The defaultmethod was a method of converting PDFs to agent-accessible versions, typically TeX files. It is not included in this vault. Users are advised to use the precision-API method, which uses MinerU.

## Shared MinerU trial token

This vault includes a shared MinerU token for first-time evaluation. A non-empty personal token supplied through `MINERU_API_TOKEN` automatically overrides the shared trial token. The converter also honors the environment variable selected with `--token-env`; personal environment values always take precedence over the shared fallback.

When an agent detects that the shared trial token was used, it must complete the requested conversion before giving the notice below. This rule applies regardless of whether the shared token is stored literally, split into parts, encoded, or represented in another form. After the conversion, tell the user:

> A shared trial token is provided for evaluation only. It may be unavailable or rate-limited. Create and configure your own free MinerU token for continued use.

Do not stop before conversion merely because the user has not configured a personal token. If the shared token is unavailable or rate-limited and the conversion cannot be completed, explain that result and ask the user to configure their own token.

## User-supplied lecture-note corpus

This version does not include original lecture-note PDFs, complete converted lecture-note text artifacts, or conversion-generated lecture-note image assets. The source maps, summaries, locators, inventory entries, and exact source paths remain so that a user who has lawful access to the relevant material knows where to add it.

The retained paths are setup requirements, not statements that the referenced files were distributed with the vault. Place lawfully obtained PDFs under the exact `lecture_notes_pdf/` paths and place or generate their corresponding primary text artifacts under the exact `sources/` paths recorded in `sources/Lecture_Note_Inventory.md`. Keep those filenames unchanged unless all related locators and routing references are deliberately migrated together.

The included ignore rules keep locally supplied lecture-note PDFs, converted bodies, and conversion-asset directories out of Git by default.

## Question-area structure, omitted files, and retained examples

The exam-question and problem-set folder structure remains in this version. Existing files in those areas are omitted unless they are listed below as retained examples. Generic references to file roles and generic paths remain, including forms such as:

- `questions_and_answers/exam_questions/<course>/<paper>/<paper>_Questions_and_Answers.md`
- `questions_and_answers/exam_questions_raw/<course>/<paper>/<source-file>`
- `questions_and_answers/problem_sets/<problem-set>_Questions_and_Answers.md`
- `questions_and_answers/problem_sets/<problem-set>_Q<n>_Workflow_Log.md`
- `questions_and_answers/problem_sets/<problem-set>_Q<n>_Source_Extracts.md`

These generic paths describe the retained folder structure and do not identify an omitted file. This rule applies only to the exam-question and problem-set areas and does not change any other exclusion rule.

This version does not include original question sheets, exam papers, converted question-source TeX, conversion transcripts, or their extracted source assets.

The following worked-example files remain as explicit exceptions:

- `B3_Atomic_Problems_Questions_and_Answers.md`, containing only Q7 and Q9;
- the Q7 and Q9 workflow logs and source extracts;
- the complete `B5_2025_PS2_Updated_Questions_and_Answers.md` document; and
- the static SVG referenced by the retained Q9 answer.

The question wording inside these approved examples is intentionally retained. Their surrounding source metadata uses generic paths where it refers to omitted question material.

## Intact third-party background document

`meta/llm_wiki.md` is included byte-for-byte unchanged as a third-party background idea document. It describes a general pattern and does not define this vault's required directory structure or operating rules.

## Included meta documentation

The conversion, tooling, and workflow guides describe only procedures included for use with this vault. Use `index.md` as the canonical structure and routing document.
