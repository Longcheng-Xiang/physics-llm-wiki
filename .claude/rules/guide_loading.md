# Conditional Guide Loading

Detailed instructions help only if they are read at the time they matter.

## Rule

When a task clearly uses a tool, format, or artifact class that has a dedicated guide in the vault, read that guide before planning or editing in that format.

## Current Required Triggers

- **PDF conversion methods:** before converting any PDF with the MinerU precision API, read `meta/pdf_conversion_methods.md` and follow the conversion guidance there.
- **Diagram workflow:** if you are creating, editing, auditing, or restyling any answer-generated figure, graph, energy-level diagram, Zeeman pattern, lineshape, Feynman/quark-flow diagram, TikZ source, `pgfplots` source, Mermaid block, or static diagram asset, read `sources/Diagram_Workflow_Guide.md` before doing the figure work. The active default for answer-generated physics diagrams is static SVG rendered from local LaTeX/TikZ.

## Relocation Rule

Moving detail out of `CLAUDE.md` is not enough by itself.

If you move detailed instructions from `CLAUDE.md` into a narrower document, also add or preserve a trigger that makes the narrower document get read when the relevant task appears.

Acceptable triggers include:

- a short cross-cutting pointer in `CLAUDE.md`;
- an auto-loaded rule under `.claude/rules/`;
- a relevant workflow step that explicitly says to open the guide.

## Placement Preference

- Put the detail in the narrowest durable guide.
- Put the loading trigger in the narrowest startup-loaded rule that still reliably catches the task.

Startup canary: `CANARY_GUIDE_LOADING_G1`
