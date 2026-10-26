# Lecture Note Inventory

This page records the expected local paths for canonical lecture-note PDFs and their primary text artifacts. The maps, summaries, and locators are included, but the PDFs, complete converted bodies, and conversion-generated image assets are not distributed with this vault. A user who has lawful access to the source material may add it at the exact paths below.

## Current Policy

- Treat the paths in the inventory as the source-installation contract; they may be absent until the user supplies the files locally.
- After the source files have been supplied, start with the map or locator when one exists, then read only the targeted section of the primary text artifact.
- Use the locally supplied original PDF for figures, page layout, or formula verification when the text artifact is insufficient.
- Expected converted TeX artifacts use the `*.defaultmethod.tex` filename.
- The B4 slide family expects MinerU precision-API Markdown as its primary text layer.
- Optional user notes are not included. If the user supplies them separately, treat them as explanatory companions rather than as authority over the lecture notes.
- Add cleaned cache sections only when a targeted live-PDF read produces something worth preserving beyond the primary text artifact.

## Inventory

| Course / topic | Canonical PDF | Primary text artifact | Map / summary | Locator | Optional user notes | Cache |
|---|---|---|---|---|---|---|
| B2 Symmetry and Relativity | `lecture_notes_pdf/B2_Symmetry_and_Relativity.pdf` | `sources/B2_Symmetry_and_Relativity.defaultmethod.tex` | `sources/B2_Symmetry_and_Relativity_Map.md`; `sources/B2_Symmetry_and_Relativity_Summary.md` | `sources/B2_Symmetry_and_Relativity_Locator.md` | `<USER_LECTURE_NOTES>`, `<USER_TUTORIAL_NOTES>` | none |
| B3 Atomic Physics (Ewart) | `lecture_notes_pdf/B3_Atomic_Physics_(Ewart).pdf` | `sources/B3_Atomic_Physics_(Ewart).defaultmethod.tex` | `sources/B3_Atomic_Physics_(Ewart)_Map.md`; `sources/B3_Atomic_Physics_(Ewart)_Summary.md` | `sources/B3_Atomic_Physics_(Ewart)_Locator.md` | `<USER_LECTURE_NOTES>`, `<USER_TUTORIAL_ORDER_NOTES>`, `<USER_TUTORIAL_NOTES>` | `sources/cache/B3_Atomic_Physics_(Ewart)/` |
| B3 Lasers Notes (2017) | `lecture_notes_pdf/B3_Lasers_Notes_(2017).pdf` | `sources/B3_Lasers_Notes_(2017).defaultmethod.tex` | none | `sources/B3_Lasers_Notes_(2017)_Locator.md` | `<USER_LECTURE_NOTES>` | none |
| B3 Quantum Notes | `lecture_notes_pdf/B3_Quantum_Notes.pdf` | `sources/B3_Quantum_Notes.defaultmethod.tex` | none | `sources/B3_Quantum_Notes_Locator.md` | `<USER_LECTURE_NOTES>` | none |
| B3 Radiation Transport (2024) | `lecture_notes_pdf/B3_Radiation_Transport_(2024).pdf` | `sources/B3_Radiation_Transport_(2024).defaultmethod.tex` | none | `sources/B3_Radiation_Transport_(2024)_Locator.md` | `<USER_LECTURE_NOTES>` | none |
| B4 Nuclear Slides (Wilkinson) | `lecture_notes_pdf/B4_Nuclear_Slides_(Wilkinson).pdf` | `sources/B4_Nuclear_Slides_(Wilkinson).mineru_api.md` | `sources/B4_Nuclear_and_Particle_Map.md`; `sources/B4_Nuclear_and_Particle_Summary.md` | `sources/B4_Nuclear_Slides_(Wilkinson)_Locator.md` | `<USER_TUTORIAL_ORDER_NOTES>`, `<USER_TUTORIAL_NOTES>` | none |
| B4 Scattering Slides (Wilkinson) | `lecture_notes_pdf/B4_Scattering_Slides_(Wilkinson).pdf` | `sources/B4_Scattering_Slides_(Wilkinson).mineru_api.md` | `sources/B4_Nuclear_and_Particle_Map.md`; `sources/B4_Nuclear_and_Particle_Summary.md` | `sources/B4_Scattering_Slides_(Wilkinson)_Locator.md` | `<USER_TUTORIAL_ORDER_NOTES>`, `<USER_TUTORIAL_NOTES>` | none |
| B4 Particle Slides (Wilkinson) | `lecture_notes_pdf/B4_Particle_Slides_(Wilkinson).pdf` | `sources/B4_Particle_Slides_(Wilkinson).mineru_api.md` | `sources/B4_Nuclear_and_Particle_Map.md`; `sources/B4_Nuclear_and_Particle_Summary.md` | `sources/B4_Particle_Slides_(Wilkinson)_Locator.md` | `<USER_TUTORIAL_ORDER_NOTES>`, `<USER_TUTORIAL_NOTES>` | none |
| B4 Nuclear and Particle (Wascko) | `lecture_notes_pdf/B4_Nuclear_and_Particle.pdf` | `sources/B4_Nuclear_and_Particle.mineru_api.md` | `sources/B4_Nuclear_and_Particle_Map.md`; `sources/B4_Nuclear_and_Particle_Summary.md` | `sources/B4_Nuclear_and_Particle.mineru_api_Locator.md` | `<USER_TUTORIAL_ORDER_NOTES>`, `<USER_TUTORIAL_NOTES>` | none |
| B4 First Steps in Subatomic Physics (Viehhauser) | `lecture_notes_pdf/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).pdf` | `sources/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).mineru_api.md` | `sources/B4_Nuclear_and_Particle_Map.md`; `sources/B4_Nuclear_and_Particle_Summary.md` | `sources/B4_First_Steps_in_Subatomic_Physics_(Viehhauser).mineru_api_Locator.md` | `<USER_TUTORIAL_ORDER_NOTES>`, `<USER_TUTORIAL_NOTES>` | none |
| B5 General Relativity | `lecture_notes_pdf/B5_GR_(Balbus).pdf` | `sources/B5_GR_(Balbus).defaultmethod.tex` | none | `sources/B5_GR_(Balbus)_Locator.md` | `<USER_LECTURE_NOTES>`, `<USER_TUTORIAL_NOTES>` | none |
| B6 Condensed Matter | `lecture_notes_pdf/B6_Condensed_Matter.pdf` | `sources/B6_Condensed_Matter.defaultmethod.tex` | none | `sources/B6_Condensed_Matter_Locator.md` | `<USER_LECTURE_NOTES>`, `<USER_TUTORIAL_ORDER_NOTES>`, `<USER_TUTORIAL_NOTES>` | none |

## B4 Source Priority

The three Wilkinson slide decks are the default B4 authority family. Use the matching nuclear, scattering, or particle locator according to the topic. The Wascko and Viehhauser sources are optional alternatives and should be consulted only when the user explicitly requests other lecture notes or names that source.
