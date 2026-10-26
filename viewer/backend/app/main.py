from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from watchfiles import Change, awatch

from .agent import WikiChatAgent
from .cli_agent import CodexCliAgent
from .config import get_settings
from .events import as_sse, error
from .vault import VaultToolbox


settings = get_settings()
toolbox = VaultToolbox(settings)
viewer_only = os.environ.get("WIKI_DESKTOP_VIEWER_ONLY") == "1"
if viewer_only:
    agent = None
elif settings.agent_backend == "codex_cli":
    agent = CodexCliAgent(settings=settings)
else:
    agent = WikiChatAgent(settings=settings, toolbox=toolbox)

app = FastAPI(title="Physics Wiki Viewer", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "viewer_only": viewer_only,
        "agent_backend": settings.agent_backend,
        "model": settings.model,
        "codex_binary": settings.codex_binary if settings.agent_backend == "codex_cli" else None,
        "vault_root": str(settings.vault_root),
        "tools": [schema["name"] for schema in toolbox.schemas],
    }


@app.get("/api/vault/files")
def vault_files() -> dict[str, Any]:
    return {"files": toolbox.viewer_markdown_files()}


@app.get("/api/vault/file")
def vault_file(path: str) -> dict[str, Any]:
    try:
        return toolbox.read_viewer_markdown(path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Markdown file not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@app.get("/api/vault/asset")
def vault_asset(path: str) -> FileResponse:
    try:
        target = toolbox.viewer_asset_path(path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Viewer asset not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return FileResponse(target, headers={"Cache-Control": "no-cache, max-age=0, must-revalidate"})


@app.get("/api/vault/events")
async def vault_events(request: Request) -> StreamingResponse:
    async def events():
        yield "event: ready\ndata: {}\n\n"
        last_heartbeat = asyncio.get_running_loop().time()
        try:
            async for changes in awatch(
                settings.vault_root,
                debounce=140,
                step=40,
                rust_timeout=1000,
                yield_on_timeout=True,
            ):
                if await request.is_disconnected():
                    return
                normalized = []
                for raw_change, raw_path in changes:
                    change_name = {
                        Change.added: "added",
                        Change.modified: "modified",
                        Change.deleted: "deleted",
                    }.get(raw_change, "modified")
                    item = toolbox.viewer_change(raw_path, change_name)
                    if item is not None:
                        normalized.append(item)
                for item in toolbox.coalesce_viewer_changes(normalized):
                    yield f"event: vault_change\ndata: {json.dumps(item)}\n\n"
                now = asyncio.get_running_loop().time()
                if not normalized and now - last_heartbeat >= 15:
                    yield ": keep-alive\n\n"
                    last_heartbeat = now
        except asyncio.CancelledError:
            return

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/chat")
async def chat(request: Request) -> StreamingResponse:
    if agent is None:
        raise HTTPException(status_code=404, detail="Chat is not available in the desktop viewer.")
    payload = await request.json()
    message = str(payload.get("message", ""))
    session_id = payload.get("sessionId")
    if session_id is not None:
        session_id = str(session_id)

    async def events():
        if not message.strip():
            yield error("Please enter a question.")
            return
        async for event in agent.stream_chat(message, session_id):
            yield event

    return StreamingResponse(as_sse(events()), media_type="text/event-stream")


def frontend_dist_path() -> Path:
    configured = os.environ.get("WIKI_FRONTEND_DIST")
    if configured:
        return Path(configured).expanduser().resolve()
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "frontend" / "dist"
    return Path(__file__).resolve().parents[2] / "frontend" / "dist"


frontend_dist = frontend_dist_path()
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
