# Agent Instructions

# Physics Wiki Agent

Short startup rules only. This vault is agent memory, not a human-facing study guide.

## Default Startup

**IMPORTANT: Complete steps 1-5 before any user-facing response.**

1. Read `DIFFERENCES.md`. Every rule in that file is mandatory for this vault and overrides any conflicting default behavior elsewhere in the vault.
2. Read `index.md`.
3. Read every Markdown rule file under `.claude/rules/` recursively before doing any work. These files govern retrieval, workflows, formatting, and harvest behavior.
4. Read `log.md` only if continuing recent work, checking what changed, or before edits that may depend on recent vault updates. On startup, read only the top 20 lines (newest-first section). Read further only later, and only by targeted line range if genuinely needed.
5. Read `meta/workflows.md` only for new lecture-note PDFs or restructuring.

If startup preflight was not completed, say so explicitly before answering.

## When Task Was Interrupted

If the visible context indicates that conversation history was summarized, compacted, resumed from a summary, or manually compressed by the user, treat that as a new startup boundary and complete the Default Startup steps again before answering.

Only when compaction occurred in the middle of an unfinished task execution, after the startup preflight and before continuing that task, reread the exact task-local materials already read for that task: files, locator entries, source line ranges, notes, workflow logs, source extracts, and target answer files as applicable. Use the visible summary and durable task artifacts to reconstruct that read set. DO NOT do this extra task-local reread merely because compaction happened between independent user requests or after the prior task was already complete. If the exact read set cannot be reconstructed well enough to continue safely, STOP and ask the user for help.


## Hard Rules

1. Optimize the vault for agent retrieval and durable memory. Human readability matters mainly for the top control docs; deeper source artifacts should prefer line-oriented, grep-friendly layouts over decorative formatting.
2. Canonical lecture-note PDFs and any merged `.defaultmethod.tex` artifacts are the technical authority. The user's notes are a parallel source and may be used when the user asks for them or when a workflow explicitly includes them. If the two conflict, defer to the lecture notes. Notes may contain errors. Terminology: when the user says "lecturenotes" or "lecture notes", they mean the professor/canonical lecture-note PDFs and merged TeX artifacts; when they say "my notes", they mean the user's notes represented by the `<USER_NOTES>` placeholder and not included in this vault.
3. **IMPORTANT: Apply the retrieval order (auto-loaded) before answering any physics question. If you skipped any step, say so before giving the answer.**
4. **IMPORTANT: If a task is clearly about a specific course and a matching rule exists under `course_rules/`, read that rule before course-specific retrieval or drafting. Course rules are conditional overrides, not startup-loaded defaults.**
5. **Avoid these failure modes:** reading long source files from the top instead of using the locator; re-extracting PDF pages when a merged `.defaultmethod.tex` already exists; answering from memory when relevant source material exists; using web search for stable content covered by the lecture notes.
6. There are no time limits on any request about this wiki whatsoever. Do not abbreviate retrieval steps, skip sources, or cut work short to save tokens or time. Completeness and correctness take priority over speed.
7. If the user gives their own retrieval, source, or answer procedure for the current message, follow that procedure instead of your default workflows (whichever they may be).
8. **Diagrams in answer files:** when an answer genuinely needs a sketch, graph, energy-level diagram, Zeeman pattern, lineshape, or transition diagram, use the diagram workflow guide rather than ASCII placeholders. For answer-generated physics diagrams, use a verified static SVG rendered from local LaTeX/TikZ rather than view-time diagram compilation. If a figure is supplied by the source question itself (for example a scanned exam plot or provided asset), keep that source figure unless the user explicitly asks for a redraw.
9. **Keep `CLAUDE.md` minimal.** Only put short, startup-critical, cross-cutting rules here. Put detailed tool-, formatting-, workflow-, or topic-specific instructions in the narrowest dedicated doc instead, and add at most a short pointer here if needed.
10. **Read dedicated guides when the task triggers them.** If a task uses a tool or format with a dedicated guide in the vault, read that guide before acting. Keep the detail in the guide, but make sure the guide is actually loaded when relevant.
## Reference Docs

- `DIFFERENCES.md` = mandatory vault-specific overrides and disclosures
- `index.md` = real router
- `meta/workflows.md` = rare procedures only (PDF ingestion, page extraction, restructuring)
- `meta/tools.md` = tools and MCP decisions
- `meta/status.md` = current physics coverage, worked-example coverage, usable workflows, and major gaps
- `meta/understanding.md` = durable project-level context
- `questions_and_answers/exam_questions/README.md` = exam-folder layout and naming
- `.claude/rules/` = auto-loaded workflows (retrieval order, Workflows A/B/C, exam questions, harvest)
Startup canary: `CANARY_CLAUDE_B1`
