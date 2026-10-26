# Workflow B (Explicit Selection)

Use Workflow B only when the user explicitly selects it for the current worked solution, derivation, calculation, exercise, or exam problem. Do not infer Workflow B from wording that does not explicitly name Workflow B.

If a worked problem falls within the workflow-choice rule and the user has not selected A, B, or C, apply `DIFFERENCES.md` and ask for a choice before retrieval or answering. General conceptual, explanatory, interpretive, and open-ended physics questions do not trigger Workflow B and are answered normally after the vault's default retrieval order.

## User-Specified Procedures

If the user selects Workflow B and also gives a narrower retrieval scope, source restriction, or answering procedure, follow the user's procedure wherever it does not conflict with mandatory vault rules.

If the user requests file-writing behavior, clarify or follow their explicit choice of Workflow A or Workflow C. Workflow B's answer and workflow log remain dialogue-only.

## Retrieval

Follow Workflow A's complete **Source-Question Preparation** and **Retrieval** sections in `workflow_a.md`. This is the same retrieval process used by Workflows A and C, including part-by-part retrieval where required.

Source-preparation artifacts may be created only when needed to make a user-supplied question accessible for retrieval. They are inputs, not Workflow B output files.

## Output (Current Dialogue Only)

Apply Workflow A's **Answer** requirements, but present the worked answer directly in the current dialogue instead of writing it to a Q&A file.

Then present a concise **Workflow log** in the dialogue. Use a numbered chronological list covering the retrieval steps, end the numbered list with `Wrote answer`, and include `Own knowledge used` and `Steps skipped` sections. Follow the direct-conversation math formatting rule in `output_format.md`.

Do not create a source-extract output and do not copy verbatim source passages into a substitute extract section.

## Rules

- Do not create or update an answer, workflow-log, or source-extract Markdown file.
- Do not widen retrieval beyond Workflow A's retrieval scope unless a required source is genuinely missing.
- Do not run the conversation-harvest workflow after Workflow B.
- Workflow selection applies only to the current problem. A distinct new problem requires a new A/B/C choice.

Startup canary: `CANARY_WORKFLOW_B_I1`
