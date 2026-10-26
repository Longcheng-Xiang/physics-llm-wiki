# Diagram Workflow Guide

Use this guide when an answer or workflow output needs an answer-generated diagram, graph, sketch, Feynman diagram, energy-level diagram, lineshape, transition diagram, or similar visual.

## Core Rule

For answer-generated physics diagrams, the active default is a verified static SVG asset rendered from local LaTeX/TikZ. Obsidian should display the finished image; it should not be asked to compile diagram code at view time.

Do not use a view-time diagram renderer as a fallback for current workflow outputs.

The agent does not need to copy and paste images manually. The normal robust workflow is:

1. write a diagram source file,
2. render it locally to an image asset such as SVG,
3. embed that asset in the Markdown answer,
4. keep the source file beside the rendered asset when regeneration is useful.

## Decision Tree

1. **Source-provided figure**: keep the extracted/source image unless the user explicitly asks for a redraw.
2. **No real visual value**: use prose or equations only. Do not add a diagram merely because the question says "sketch" if a short sentence fully resolves it.
3. **Simple conceptual flowchart with little or no math**: use a Mermaid code block if it will be clearer and the output is not math-heavy. Mermaid is good for flowcharts and dependency graphs, not precise physics geometry.
4. **Physics diagram, graph, spectrum, potential, Feynman-style sketch, or anything with mathematical labels**: use a static SVG asset generated from local LaTeX/TikZ.
5. **Illustrative bitmap art**: use image generation only for non-technical illustrations. Do not use generated art for precise exam diagrams, quantitative plots, Feynman diagrams, or labelled physics schematics.

## Static TikZ Asset Workflow

Use this when a Workflow A answer needs a reliable diagram.

1. Create an asset folder beside the answer file, for example:
   - `questions_and_answers/exam_questions/<course>/<paper>/<paper>_answer_assets/diagrams/`
   - `questions_and_answers/problem_sets/<set>_answer_assets/diagrams/`
2. Write a standalone `.tex` source file in that folder.
3. Render it with:

```bash
python3 tools/render_tex_diagram.py path/to/diagram.tex
```

4. Embed the resulting SVG in the Markdown answer:

```markdown
![Concise description](relative/path/to/diagram.svg)
```

Use standard Markdown image syntax for new answer-generated assets. It renders in
Obsidian reading view and in compatible read-only viewers, while Obsidian-only
`![[...]]` embeds may not render in those viewers. Make the path
relative to the Markdown file, use forward slashes, and percent-encode spaces as
`%20` when a path contains them.

5. Keep both `diagram.tex` and `diagram.svg` unless the user only wants a final static image. The `.tex` is the editable source; the `.svg` is what Obsidian displays.

## Comfortable Default Size

Answer-generated SVGs should render at a comfortable reading size by default, not as tiny thumbnail-like sketches. When using TikZ, set an explicit `scale` with `transform shape` or otherwise choose coordinates/font sizes so a simple one-panel diagram previews at roughly 350-550 px wide, and a denser physics diagram previews at roughly 450-700 px wide when converted to PNG for inspection.

For multi-panel Feynman, quark-flow, spectrum, or nonet diagrams, prefer splitting the content into one SVG per physical subdiagram unless the panels must be compared side by side. Three compact decay diagrams in one SVG are usually harder to read than three separate source-faithful SVGs. Use an explicit bounding box when needed so labels at the left/right/top are not cropped by the renderer.

Use local static rendering especially when:

- the diagram is part of a Workflow A answer or other durable wiki output;
- the diagram uses local LaTeX/TikZ, PGFPlots, circuitikz, chemfig, tikz-feynman, or similar packages;
- the note may be exported to PDF;
- the diagram is important to the correctness of the answer;
- a visual check is needed before finalizing.

## Static Asset Verification

A static asset is not done until:

- the renderer exits successfully;
- the SVG/PNG file exists and is non-empty;
- the rendered image has been visually inspected; a non-empty SVG is not enough, because a broken driver path can produce a non-empty but visually collapsed image;
- answer-generated physics diagrams obey the palette audit in `Palette And Style`; do not rely on visual inspection alone for this, because TeX/SVG defaults can silently leave black wrapper, stroke, fill, or text colors in the output;
- labels do not obviously overlap;
- the Markdown embed path points to the rendered asset;
- if the diagram is important, the rendered asset is opened or inspected with an available image/browser tool.

On this macOS machine no `rsvg-convert` or ImageMagick is installed. To inspect an SVG, rasterise it either with `qlmanage -t -s 1200 -o <dir> file.svg` or with a small Swift script that loads it through `NSImage(contentsOfFile:)` and writes a PNG. The AppKit route ignores SVG opacity, so avoid opacity-based shading and grids in answer figures, or check them in a browser.

For local TeX rendering, prefer SVG first. Use PNG only when SVG rendering/export causes problems or the source is inherently raster.

## Mermaid Workflow

Mermaid is suitable for plain flowcharts, trees, and dependency diagrams. It is not a good default for math-heavy physics diagrams because labels and equations are limited compared with LaTeX.

Use Mermaid only when:

- node labels can be plain text or light inline math-like text;
- precise geometry is not important;
- the diagram is a conceptual relation, not a quantitative sketch.

## Palette And Style

For Workflow A and exam/problem answers, keep diagrams restrained. Use the existing answer-figure palette by default:

- neutral structure: `gray`
- main contrast: `red`
- secondary contrast: `blue!50`

For static SVGs this palette can be translated into ordinary SVG colors, but keep the same visual roles.

Hard rule for answer-generated physics diagrams: do not use explicit black for visible diagram elements, text, axes, arrows, labels, or default SVG wrappers. TikZ and `dvisvgm` may introduce black even when the source file does not mention it, so check both the `.tex` source and rendered `.svg` before finalizing.

In TikZ sources, make the neutral default explicit, for example:

```tex
\begin{tikzpicture}[color=gray, every node/.style={text=gray}]
```

Then opt individual emphasis elements into `red` or `blue!50` as needed. If the rendered SVG still contains a black default wrapper such as `fill='#000' stroke='#000'`, recolor it to the neutral gray role before embedding the asset.

When rendering LaTeX text with `dvisvgm`, glyphs are often emitted as reusable `<path>` definitions plus `<use>` references. Some consumers may render `<use>` glyphs as implicit black if the color is only inherited from a parent `<g>`. For durable Obsidian SVGs, make rendered glyph colors explicit on the `<use>` elements before finalizing.

Before finalizing any answer-generated SVG, run a targeted palette audit on the affected diagram files:

```bash
rg -n "#000|black|rgb\(0%,0%,0%\)|stroke=\"black\"|fill=\"black\"|fill='#000'|stroke='#000'" path/to/diagrams
rg -n -P "<use(?![^>]*\sfill=)" path/to/diagrams/*.svg
```

Both audits should return no matches unless the match is inside a quoted source excerpt whose purpose is explicitly to discuss the forbidden color.

## Workflow A Policy

Workflow A diagrams should prioritize reliability and readability. If a question asks for a sketch or diagram, choose the simplest adequate route from this guide. For answer-generated physics diagrams, use static SVG assets rendered from local LaTeX/TikZ.
