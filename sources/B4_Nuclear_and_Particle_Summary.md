# B4 Nuclear and Particle Summary

Summary page for the current B4 source hierarchy, Markdown-first retrieval rule, and slide-specific caveats.

## Source Priority

- The only default B4 lecture-note authority is the Wilkinson 2024 slide family:
  - `lecture_notes_pdf/B4_Nuclear_Slides_(Wilkinson).pdf`
  - `lecture_notes_pdf/B4_Scattering_Slides_(Wilkinson).pdf`
  - `lecture_notes_pdf/B4_Particle_Slides_(Wilkinson).pdf`
- The main durable text artifacts for those slide decks are:
  - `sources/B4_Nuclear_Slides_(Wilkinson).mineru_api.md`
  - `sources/B4_Scattering_Slides_(Wilkinson).mineru_api.md`
  - `sources/B4_Particle_Slides_(Wilkinson).mineru_api.md`
- `lecture_notes_pdf/B4_Nuclear_and_Particle.pdf` and `lecture_notes_pdf/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).pdf` are `other resources`.
- The opt-in Wascko and Viehhauser PDFs now have Precision-API Markdown sidecars and locators:
  - `sources/B4_Nuclear_and_Particle.mineru_api.md`, locator `sources/B4_Nuclear_and_Particle.mineru_api_Locator.md`
  - `sources/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).mineru_api.md`, locator `sources/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).mineru_api_Locator.md`
- Do not use those extra resources in ordinary answers, Workflow A, or Workflow B unless the user explicitly says `other resources`, `other lecturenotes resources`, or explicitly names the source.

## Current Conversion Coverage

- Wilkinson nuclear slides: MinerU precision-API Markdown, extracted assets, and Markdown-line locator exist.
- Wilkinson scattering slides: MinerU precision-API Markdown, extracted assets, and Markdown-line locator exist.
- Wilkinson particle slides: MinerU precision-API Markdown, extracted assets, and Markdown-line locator exist.
- No B4 `.defaultmethod.tex` artifacts are kept by design.
- Wascko and Viehhauser have opt-in Precision-API Markdown sidecars and locators. They remain `other resources`, not the default B4 authority layer.

## Retrieval Advice

- Treat B4 as three operational parts: nuclear, scattering, and particle physics. Use the locator headings / slide titles to decide which part a question belongs to before reading source text.
- If the question is clearly within one B4 part, start with that part's locator and read the targeted lines in the matching `*.mineru_api.md` file.
- If the question spans more than one B4 part, read the relevant sections from each relevant part only.
- For B4 Workflow A and similar narrow retrieval, `my notes` means `<USER_TUTORIAL_ORDER_NOTES>` unless the user explicitly says otherwise. If separately supplied, use it in parallel as the main user-note layer. Use `<USER_TUTORIAL_NOTES>` only when the user explicitly asks for tutorials, says `both`, or otherwise puts tutorials in scope.
- The repeated slide titles are a property of the original PDFs, not a MinerU-specific failure. The B4 locators therefore collapse consecutive duplicate title runs and join clearly split title fragments.
- Reopen the slide PDF for figure-layout questions or whenever a formula-heavy passage in the Markdown looks suspicious.

## Precision API Quality Notes

- The precision-API Markdown is the canonical B4 text layer because it preserves slide annotations and image-backed material better than the old B4 TeX route did.
- Important equations can still suffer local corruption, placeholder symbols, or awkward line breaking, so exact derivations should still be checked against the slide PDF when needed.
- A previous precision-API nuclear-slide test showed that local-file `page_range` requests may be ignored on this slide family, so treat full-deck returns as normal.
- Whole-file signed upload timed out for the opt-in Wascko and Viehhauser PDFs on 2026-05-20, so their sidecars were converted without OCR from temporary page chunks and then merged. The chunk markers in the Markdown are conversion aids, not source section headings.
- A 2026-05-20 spot audit found all image links resolvable after renaming the Viehhauser asset directory without parentheses. Treat the opt-in sidecar locators as useful search/routing aids, but not clean semantic outlines: they include table-of-contents headings, some chunk boundaries split paragraphs or formulas, and some OCR-free extraction artifacts remain in figure-heavy/column-heavy passages. For exact formula, figure-layout, or boundary-sensitive claims from these opt-in sources, reopen the PDF.
