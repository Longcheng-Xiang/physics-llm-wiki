# Course Rules

This folder contains course-specific rules that are loaded only when a workflow or generic trigger explicitly points to them.

- Keep course-specific retrieval, notation, optional-note, and answer-style overrides here, not under `.claude/rules/`.
- These files are not part of startup preflight.
- When a matching course rule is triggered, read it before any course-specific source-question preparation, retrieval, or drafting.
- If a course rule conflicts with generic Workflow A, the course rule takes priority for that course.

Current course rules: `B3.md`, `B4.md`, and `B5.md`.

Startup canary: `CANARY_COURSE_RULES_L1`
