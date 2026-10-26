# B4 Nuclear and Particle Map

Routing page for the B4 source family.

## Default B4 Sources

- Nuclear topics: `lecture_notes_pdf/B4_Nuclear_Slides_(Wilkinson).pdf`
  - Converted authority artifacts: `sources/B4_Nuclear_Slides_(Wilkinson).mineru_api.md`, `sources/B4_Nuclear_Slides_(Wilkinson)_Locator.md`
- Scattering topics: `lecture_notes_pdf/B4_Scattering_Slides_(Wilkinson).pdf`
  - Converted authority artifacts: `sources/B4_Scattering_Slides_(Wilkinson).mineru_api.md`, `sources/B4_Scattering_Slides_(Wilkinson)_Locator.md`
- Particle topics: `lecture_notes_pdf/B4_Particle_Slides_(Wilkinson).pdf`
  - Converted authority artifacts: `sources/B4_Particle_Slides_(Wilkinson).mineru_api.md`, `sources/B4_Particle_Slides_(Wilkinson)_Locator.md`

These three Wilkinson slide decks are the only default B4 lecture-note authority layer. Use the MinerU precision-API Markdown files as the main text artifacts, not `.defaultmethod.tex`.

## Part Split

- Treat B4 as three operational parts: nuclear, scattering, and particle physics.
- Before retrieving, inspect the question against the relevant locator headings / source titles and decide which part or parts it belongs to.
- If the question is clearly about one part, start with that part's locator and source.
- If it spans more than one part, read the relevant sections from each relevant part only.
- Typical scattering-layer topics include differential cross section, Born approximation, Yukawa scattering, form factors, resonances, and the Breit-Wigner function.

## Other Resources

- `lecture_notes_pdf/B4_Nuclear_and_Particle.pdf`
- `lecture_notes_pdf/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).pdf`

Treat these as `other resources`.

- Do not use them in normal answers, Workflow A, or Workflow B by default.
- Consult them only when the user explicitly says `other resources`, `other lecturenotes resources`, or explicitly names the source.
- Wascko opt-in sidecar: `sources/B4_Nuclear_and_Particle.mineru_api.md`, locator `sources/B4_Nuclear_and_Particle.mineru_api_Locator.md`.
- Viehhauser opt-in sidecar: `sources/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).mineru_api.md`, locator `sources/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).mineru_api_Locator.md`.

## Optional User Notes

- `<USER_TUTORIAL_ORDER_NOTES>` (main user-note layer; not included)
- `<USER_TUTORIAL_NOTES>` (opt-in only; not included)

If separately supplied, use the user-note layer in parallel with the relevant Wilkinson slide source. For B4 retrieval, `my notes` means `<USER_TUTORIAL_ORDER_NOTES>` unless the user explicitly says otherwise. Use `<USER_TUTORIAL_NOTES>` only when the user explicitly asks for tutorials, says `both`, or otherwise puts tutorials in scope.
