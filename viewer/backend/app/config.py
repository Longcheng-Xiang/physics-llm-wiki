from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


if os.environ.get("WIKI_DESKTOP_VIEWER_ONLY") != "1":
    vault_root_hint = os.environ.get("WIKI_VAULT_ROOT", "").strip()
    if vault_root_hint:
        load_dotenv(Path(vault_root_hint).expanduser() / "web" / "backend" / ".env")
    else:
        load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _default_vault_root() -> Path:
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    vault_root: Path
    openai_api_key: str | None
    model: str
    reasoning_effort: str
    agent_backend: str
    codex_binary: str
    codex_model: str | None
    max_agent_iterations: int
    max_output_tokens: int
    workflow_b_primary_source_read_synthesis_threshold: int
    max_file_lines_without_range: int
    search_match_limit: int
    search_output_limit: int


def get_settings() -> Settings:
    vault_root_raw = os.environ.get("WIKI_VAULT_ROOT", "").strip()
    vault_root = Path(vault_root_raw).expanduser() if vault_root_raw else _default_vault_root()
    return Settings(
        vault_root=vault_root.resolve(),
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        model=os.environ.get("OPENAI_MODEL", "gpt-5.4"),
        reasoning_effort=os.environ.get("OPENAI_REASONING_EFFORT", "medium"),
        agent_backend=os.environ.get("AGENT_BACKEND", "openai").strip().lower() or "openai",
        codex_binary=os.environ.get("CODEX_BINARY", "codex"),
        codex_model=os.environ.get("CODEX_MODEL") or None,
        max_agent_iterations=int(os.environ.get("MAX_AGENT_ITERATIONS", "80")),
        max_output_tokens=int(os.environ.get("MAX_OUTPUT_TOKENS", "32000")),
        workflow_b_primary_source_read_synthesis_threshold=int(
            os.environ.get("WORKFLOW_B_PRIMARY_SOURCE_READ_SYNTHESIS_THRESHOLD", "8")
        ),
        max_file_lines_without_range=int(os.environ.get("MAX_FILE_LINES_WITHOUT_RANGE", "800")),
        search_match_limit=int(os.environ.get("SEARCH_MATCH_LIMIT", "50")),
        search_output_limit=int(os.environ.get("SEARCH_OUTPUT_LIMIT", "20000")),
    )
