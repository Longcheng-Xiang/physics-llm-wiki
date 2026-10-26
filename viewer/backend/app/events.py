from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any


ChatEvent = dict[str, Any]


def trace(
    title: str,
    detail: str | None = None,
    *,
    path: str | None = None,
    line_range: tuple[int, int] | None = None,
) -> ChatEvent:
    event: ChatEvent = {"type": "trace", "title": title}
    if detail:
        event["detail"] = detail
    if path:
        event["path"] = path
    if line_range:
        event["lineRange"] = [line_range[0], line_range[1]]
    return event


def answer_delta(text: str) -> ChatEvent:
    return {"type": "answer_delta", "text": text}


def answer_done(text: str) -> ChatEvent:
    return {"type": "answer_done", "text": text}


def error(message: str) -> ChatEvent:
    return {"type": "error", "message": message}


def encode_sse(event: ChatEvent) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def as_sse(events: AsyncIterator[ChatEvent]) -> AsyncIterator[str]:
    async for event in events:
        yield encode_sse(event)

