# Workflow C (Answer File Only)

Use Workflow C only when the user explicitly selects it for the current worked solution, derivation, calculation, exercise, or exam problem.

## Governing Rule

Workflow A (`workflow_a.md`) governs Workflow C except for the output-artifact overrides below. Apply its requirements for:

- conditional guide and course-rule loading;
- source-question preparation;
- the complete retrieval sequence;
- part-by-part retrieval and answer writing;
- answer depth, exact question wording, marks, mathematical formatting, and diagram handling;
- strict serial processing of multi-part and multi-question requests;
- immediate synthesis or source-artifact writebacks caused by the question; and
- the chat/file boundary and brief final confirmation.

The only output differences from Workflow A are:

1. Write the worked answer into the same Q&A Markdown file that Workflow A would use.
2. Do not create or update a `*_Workflow_Log.md` file.
3. Do not create or update a `*_Source_Extracts.md` file.
4. Do not insert substitute workflow-log or source-extract sections into the answer file.

## Completion Boundary

A Workflow C question is complete when its answer has been written to the Q&A Markdown file and any immediate synthesis or source-artifact writebacks caused by that question are complete. Only then may retrieval begin for the next question.

Leave workflow-log or source-extract files from earlier work unchanged unless the user explicitly asks to modify or delete them.

## Reporting

Do not print the worked answer in the conversation. Return only a brief confirmation that the answer was written using Workflow C.

Workflow selection applies only to the current problem. A distinct new problem requires a new A/B/C choice under `DIFFERENCES.md`.

Startup canary: `CANARY_WORKFLOW_C_A1`
