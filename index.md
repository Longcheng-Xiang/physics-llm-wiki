# Wiki Index

Primary router for the agent-maintained physics wiki. Most questions should start here, not in the longer docs.

## Start Here

| Need | Read |
|---|---|
| Routine physics question | Relevant lecture-note source maps, summaries, locators, and primary text artifacts; use `<USER_NOTES>` only when explicitly available |
| Exam question in supported topic | Relevant lecture-note source maps, summaries, locators, primary text artifacts, and any cleaned caches; open `meta/workflows.md` only if needed |
| Exam answer workspace | `questions_and_answers/exam_questions/<course>/<paper>/<paper>_Questions_and_Answers.md` |
| Exam source workspace | `questions_and_answers/exam_questions_raw/<course>/<paper>/<source-file>` |
| Problem-set answer workspace | `questions_and_answers/problem_sets/<problem-set>_Questions_and_Answers.md` |
| New lecture-note PDF | [[meta/workflows]] |
| Restructure or optimize | [[meta/workflows]] |
| Tool or MCP choice | [[meta/tools]] |
| PDF conversion method | [[meta/pdf_conversion_methods]] |
| Current vault status | [[meta/status]] |
| Project-level context | [[meta/understanding]] |
| Recent change awareness | [[log]] only if continuing recent work or about to edit |
| Startup rules | [[CLAUDE]] |

## How To Use This Index

- Use this file as the first stop for normal questions.
- For technical claims, canonical lecture-note PDFs, their primary text artifacts, and their access pages are the authority layer.
- Use the user's markdown notes mainly for clarification, alternate explanation, and locating the right lecture-note material.
- Do not read `log.md` by default for routine question answering.
- Do not read `meta/workflows.md` by default for routine question answering.
- Open longer docs only when the task type actually requires them.

## Lecture-Note Access Layer

| Page | One-line summary |
|---|---|
| [[sources/Lecture_Note_Inventory]] | Canonical lecture-note PDFs, primary text artifacts, locators, and companion notes |
| [[sources/cache/README]] | How targeted cleaned sections fit in once merged TeX exists |
| [[sources/Diagram_Workflow_Guide]] | Active workflow for answer-generated diagrams: source images, Mermaid for simple flowcharts, and static SVG assets rendered from local LaTeX/TikZ |

## B2 - Symmetry and Relativity

Primary source map: [[sources/B2_Symmetry_and_Relativity_Map]]
Primary lecture-note summary: [[sources/B2_Symmetry_and_Relativity_Summary]]
Primary TeX locator: [[sources/B2_Symmetry_and_Relativity_Locator]]
Companion user notes: `<USER_LECTURE_NOTES>`, `<USER_TUTORIAL_NOTES>` (not included)

| Page | One-line summary |
|---|---|
| [[sources/B2_Symmetry_and_Relativity_Map]] | Curated topic routing across symmetries, Lagrangian methods, Lorentz transformations, relativistic dynamics, covariant electromagnetism, stress-energy, and radiation |
| [[sources/B2_Symmetry_and_Relativity_Summary]] | B2 source role, retrieval strategy, notation notes, conversion caveats, and current gaps |
| [[sources/B2_Symmetry_and_Relativity_Locator]] | Exact TeX line routing for the merged B2 lecture-note artifact |

## B3 — Atomic Physics

Primary source map: [[sources/B3_Atomic_Physics_(Ewart)_Map]]
Primary lecture-note summary: [[sources/B3_Atomic_Physics_(Ewart)_Summary]]
Primary TeX locator: [[sources/B3_Atomic_Physics_(Ewart)_Locator]]
Other equal-priority B3 locators: [[sources/B3_Lasers_Notes_(2017)_Locator]], [[sources/B3_Quantum_Notes_Locator]], [[sources/B3_Radiation_Transport_(2024)_Locator]]
Problem-set Q&A entrypoint: [[questions_and_answers/problem_sets/B3_Atomic_Problems_Questions_and_Answers]]

## B4 — Nuclear and Particle Physics

Primary source map: [[sources/B4_Nuclear_and_Particle_Map]]
Primary lecture-note summary: [[sources/B4_Nuclear_and_Particle_Summary]]
Primary slide locators: [[sources/B4_Nuclear_Slides_(Wilkinson)_Locator]], [[sources/B4_Scattering_Slides_(Wilkinson)_Locator]], [[sources/B4_Particle_Slides_(Wilkinson)_Locator]]
Primary slide PDFs: `lecture_notes_pdf/B4_Nuclear_Slides_(Wilkinson).pdf`, `lecture_notes_pdf/B4_Scattering_Slides_(Wilkinson).pdf`, `lecture_notes_pdf/B4_Particle_Slides_(Wilkinson).pdf`
Other Oxford-origin lecture-note resources (use only when the user explicitly asks for other lecture notes or names the source): `lecture_notes_pdf/B4_Nuclear_and_Particle.pdf`, `lecture_notes_pdf/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).pdf`

| Page | One-line summary |
|---|---|
| [[sources/B4_Nuclear_and_Particle_Map]] | Topic routing across the Wilkinson nuclear/scattering/particle slide family, plus the opt-in extra B4 resources |
| [[sources/B4_Nuclear_and_Particle_Summary]] | Current B4 source priority, Markdown-first retrieval rule, and slide-specific caveats |
| [[sources/B4_Nuclear_Slides_(Wilkinson)_Locator]] | Markdown-line routing for the Wilkinson nuclear slide deck, with repeated title runs collapsed |
| [[sources/B4_Scattering_Slides_(Wilkinson)_Locator]] | Markdown-line routing for the Wilkinson scattering slide deck, with repeated title runs collapsed |
| [[sources/B4_Particle_Slides_(Wilkinson)_Locator]] | Markdown-line routing for the Wilkinson particle slide deck, with repeated title runs collapsed |

## B5 — General Relativity

Primary TeX locator: [[sources/B5_GR_(Balbus)_Locator]]
Primary lecture-note artifact: `sources/B5_GR_(Balbus).defaultmethod.tex`
Companion user notes: `<USER_LECTURE_NOTES>`, `<USER_TUTORIAL_NOTES>` (not included)

| Page | One-line summary |
|---|---|
| [[sources/B5_GR_(Balbus)_Locator]] | Exact TeX routing for the canonical Balbus general-relativity lecture notes |

## B6 — Condensed Matter Physics

Primary TeX locator: [[sources/B6_Condensed_Matter_Locator]]
Primary lecture-note artifact: `sources/B6_Condensed_Matter.defaultmethod.tex`
Companion user notes: `<USER_LECTURE_NOTES>`, `<USER_TUTORIAL_ORDER_NOTES>`, `<USER_TUTORIAL_NOTES>` (not included)

| Page | One-line summary |
|---|---|
| [[sources/B6_Condensed_Matter_Locator]] | Exact TeX line routing for the B6 condensed-matter lecture-note artifact |

## Meta / Tooling

| Page | One-line summary |
|---|---|
| [[CLAUDE]] | Session-start rules (auto-loaded) |
| [[meta/llm_wiki]] | Third-party background idea document for persistent LLM-maintained wiki systems |
| [[meta/workflows]] | Step-by-step playbooks for question handling, PDFs, and optimization |
| [[meta/tools]] | Available tools, MCP usage, and lecture-note access rules |
| [[meta/pdf_conversion_methods]] | MinerU precision-API commands, defaults, outputs, credential handling, and recovery procedures |
| [[meta/status]] | Current physics coverage, worked-example coverage, usable workflows, and major gaps |
| [[meta/understanding]] | Durable project-level context for how the vault should accumulate knowledge |
| [[log]] | Recent structural changes and harvests; not mandatory for routine questions |

## Background Material

User background notes: `<USER_BACKGROUND_NOTES>` (not included).
- A1: Thermodynamics, Kinetic Theory, Statistical Physics
- A2: Electromagnetism, Optics
- A3: Quantum Mechanics
- Mathematical Methods

Startup canary: `CANARY_INDEX_C1`
