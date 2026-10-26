# Agent Instructions

At the start of every new conversation in this repository, before producing any response at all, including greetings, acknowledgements, or clarification questions, complete this startup preflight:

1. Read `CLAUDE.md`.
2. Immediately complete every startup requirement defined in `CLAUDE.md`.
3. Do not answer the user until this preflight is complete.
4. If any step was skipped or could not be completed, say that explicitly before answering.

Treat context compaction as a fresh startup boundary. If the visible context indicates that conversation history was summarized, compacted, resumed from a summary, or manually compressed by the user, rerun the full startup preflight above before producing the next user-facing response. This applies even if the current task appears to be a continuation of work already in progress.

Startup canary: `CANARY_AGENTS_A1`
