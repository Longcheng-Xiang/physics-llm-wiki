# Cached PDF Sections

This directory stores targeted cleaned sections from canonical lecture-note PDFs.

## Purpose

The goal is to avoid rereading the same PDF pages repeatedly while still keeping the vault compact. When a merged `.defaultmethod.tex` exists, that TeX plus its locator is the normal detailed authority layer. Cached sections are a secondary cleanup layer for the parts that still need something better than the merged TeX.

## Scope

- Use this directory only for canonical lecture-note PDFs.
- Do not cache handwritten/supporting attachment PDFs unless the user explicitly asks for that.
- If a reliable merged `.defaultmethod.tex` already exists, use this directory only for cleaned or figure-sensitive sections that still require live PDF work.

## Structure

```text
sources/cache/
  [Lecture Note Label]/
    [start]-[end] - [Section Name].md
```

Example:

```text
sources/cache/B3_Atomic_Physics_(Ewart)/
  017-029 - Spin-Orbit Interaction.md
```

## Rules

1. Each cache file should contain the full extracted text for a contiguous page range that was read.
2. Prefer logical section boundaries from the source map over arbitrary fragments.
3. Cached sections take precedence over rereading the same pages from the live PDF and over relying on raw notes for the same technical content.
4. If a broader or cleaner extraction is later obtained, update or replace the narrower cache file rather than letting conflicting caches accumulate.
5. Add page markers inside the cache file so future citation remains easy.
6. If a live lecture-note read happens during question answering, create or widen the relevant cache in the same turn unless extraction quality made that impossible.

## Suggested Frontmatter

```yaml
---
source_pdf: [original PDF filename]
source_map: "<SOURCE_MAP>"
pages: pp. X-Y
section_hint: [logical section name]
status: extracted
---
```
