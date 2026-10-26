from __future__ import annotations

import re


FENCE_PATTERN = re.compile(r"```[\s\S]*?```")
INLINE_PATTERN = re.compile(r"\\\(([\s\S]*?)\\\)")
BRACKET_DISPLAY_PATTERN = re.compile(r"\\\[([\s\S]*?)\\\]")
DISPLAY_PATTERN = re.compile(r"\$\$([\s\S]*?)\$\$")
STANDALONE_INLINE_PATTERN = re.compile(r"(?m)^([ \t]{0,3})\$([^$\n]+)\$[ \t]*$")


def normalize_display_math(text: str) -> str:
    """Normalize final Markdown math without touching fenced code blocks."""

    def normalize_segment(segment: str) -> str:
        segment = INLINE_PATTERN.sub(lambda match: f"${match.group(1).strip()}$", segment)
        segment = BRACKET_DISPLAY_PATTERN.sub(
            lambda match: f"$${match.group(1).strip()}$$",
            segment,
        )

        def rewrite_display(match: re.Match[str]) -> str:
            inner = match.group(1).strip()
            if not inner:
                return "$$$$$$"
            inner = re.sub(r"\s*\n\s*", " ", inner)
            inner = re.sub(r"[^\S\n]+", " ", inner).strip()
            return f"$$\n{inner}\n$$"

        segment = DISPLAY_PATTERN.sub(rewrite_display, segment)

        def rewrite_standalone_inline(match: re.Match[str]) -> str:
            indent = match.group(1)
            inner = match.group(2).strip()
            return f"{indent}$$\n{inner}\n{indent}$$"

        return STANDALONE_INLINE_PATTERN.sub(rewrite_standalone_inline, segment)

    parts: list[str] = []
    last = 0
    for fence in FENCE_PATTERN.finditer(text):
        parts.append(normalize_segment(text[last : fence.start()]))
        parts.append(fence.group(0))
        last = fence.end()
    parts.append(normalize_segment(text[last:]))
    return "".join(parts)


def chunk_text(text: str, size: int = 700) -> list[str]:
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = max(text.rfind("\n", start, end), text.rfind(" ", start, end))
            if boundary > start + size // 2:
                end = boundary + 1
        chunks.append(text[start:end])
        start = end
    return chunks
