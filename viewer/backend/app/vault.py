from __future__ import annotations

import fnmatch
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import Settings
from .events import ChatEvent, trace

EXCLUDED_AGENT_PATH_PREFIXES: tuple[str, ...] = ()
VIEWER_EXCLUDED_PARTS = {
    ".git",
    ".obsidian",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
}
VIEWER_EXCLUDED_PATH_PREFIXES = (
    "temporary",
)
VIEWER_IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}


@dataclass(frozen=True)
class ToolResult:
    output: str
    trace: ChatEvent


class VaultAccessError(ValueError):
    pass


class VaultToolbox:
    """Read-only filesystem tools exposed to the web agent."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.root = settings.vault_root.resolve()

    def _is_excluded_rel(self, rel: str) -> bool:
        rel = rel.strip("/")
        return bool(rel) and any(rel == prefix or rel.startswith(f"{prefix}/") for prefix in EXCLUDED_AGENT_PATH_PREFIXES)

    def _is_excluded_path(self, path: Path) -> bool:
        rel = path.relative_to(self.root).as_posix()
        return self._is_excluded_rel(rel)

    def _is_viewer_excluded_path(self, path: Path) -> bool:
        try:
            rel_path = path.resolve().relative_to(self.root)
        except ValueError:
            return True
        rel = rel_path.as_posix().strip("/")
        # Expose the vault's agent instructions, without opening other hidden paths.
        if any(part in VIEWER_EXCLUDED_PARTS or
               (part.startswith(".") and not (index == 0 and part == ".claude"))
               for index, part in enumerate(rel_path.parts)):
            return True
        return any(rel == prefix or rel.startswith(f"{prefix}/") for prefix in VIEWER_EXCLUDED_PATH_PREFIXES)

    def _unique_sources_basename(self, rel: str) -> Path | None:
        if not rel or "/" in rel or "\\" in rel:
            return None
        source_dir = self.root / "sources"
        if not source_dir.exists():
            return None
        matches = [
            candidate
            for candidate in source_dir.rglob(rel)
            if candidate.is_file() and not self._is_excluded_path(candidate)
        ]
        return matches[0] if len(matches) == 1 else None

    @property
    def schemas(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "name": "read_file",
                "description": "Read a UTF-8 text file from the vault. Use start_line/end_line for large files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Vault-relative path, for example index.md or sources/B5_GR_(Balbus)_Locator.md.",
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "First line to read, 1-indexed.",
                        },
                        "end_line": {
                            "type": "integer",
                            "description": "Last line to read, 1-indexed.",
                        },
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "list_files",
                "description": "List files and directories inside a vault directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Vault-relative directory path. Use an empty string for the vault root.",
                        }
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "search_files",
                "description": "Search vault text files for a literal pattern and return matching file paths and line numbers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Literal text to search for."},
                        "path": {
                            "type": "string",
                            "description": "Vault-relative directory to search in. Use an empty string for the whole vault.",
                        },
                        "file_glob": {
                            "type": "string",
                            "description": "Filename glob, for example *.md or *.defaultmethod.tex.",
                        },
                    },
                    "required": ["pattern", "path", "file_glob"],
                    "additionalProperties": False,
                },
            },
        ]

    def safe_path(self, rel: str) -> Path:
        rel = rel or ""
        try:
            resolved = (self.root / rel).resolve()
            resolved.relative_to(self.root)
        except Exception as exc:
            raise VaultAccessError(f"ACCESS DENIED: path escapes vault: {rel}") from exc
        if self._is_excluded_rel(rel):
            raise VaultAccessError(f"ACCESS DENIED: path is excluded from web retrieval: {rel}")
        return resolved

    def viewer_markdown_files(self) -> list[dict[str, Any]]:
        """Return the Markdown files exposed by the read-only file viewer."""
        files: list[dict[str, Any]] = []
        for candidate in self.root.rglob("*.md"):
            if not candidate.is_file() or self._is_viewer_excluded_path(candidate):
                continue
            try:
                stat = candidate.stat()
            except OSError:
                continue
            files.append(
                {
                    "path": candidate.relative_to(self.root).as_posix(),
                    "name": candidate.name,
                    "modifiedNs": stat.st_mtime_ns,
                }
            )
        return sorted(files, key=lambda item: str(item["path"]).casefold())

    def read_viewer_markdown(self, rel: str) -> dict[str, Any]:
        """Read a complete Markdown file, retrying if an in-progress save changes it."""
        target = self.safe_path(rel)
        if self._is_viewer_excluded_path(target):
            raise VaultAccessError(f"ACCESS DENIED: path is excluded from the file viewer: {rel}")
        if target.suffix.lower() != ".md":
            raise VaultAccessError(f"ACCESS DENIED: the file viewer only opens Markdown files: {rel}")
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(rel)

        content = ""
        stat_after = target.stat()
        for attempt in range(3):
            stat_before = target.stat()
            content = target.read_text(encoding="utf-8", errors="replace")
            stat_after = target.stat()
            if (stat_before.st_mtime_ns, stat_before.st_size) == (stat_after.st_mtime_ns, stat_after.st_size):
                break
            if attempt < 2:
                time.sleep(0.025)

        return {
            "path": target.relative_to(self.root).as_posix(),
            "name": target.name,
            "content": content,
            "modifiedNs": stat_after.st_mtime_ns,
        }

    def viewer_asset_path(self, rel: str) -> Path:
        target = self.safe_path(rel)
        if self._is_viewer_excluded_path(target):
            raise VaultAccessError(f"ACCESS DENIED: path is excluded from the file viewer: {rel}")
        if target.suffix.lower() not in VIEWER_IMAGE_SUFFIXES:
            raise VaultAccessError(f"ACCESS DENIED: unsupported viewer asset type: {rel}")
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(rel)
        return target

    def viewer_change(self, changed_path: str | Path, change: str) -> dict[str, Any] | None:
        """Normalize a watchfiles change for the browser event stream."""
        target = Path(changed_path).resolve()
        try:
            rel = target.relative_to(self.root).as_posix()
        except ValueError:
            return None
        if self._is_viewer_excluded_path(target):
            return None
        suffix = target.suffix.lower()
        if suffix == ".md":
            kind = "markdown"
        elif suffix in VIEWER_IMAGE_SUFFIXES:
            kind = "asset"
        else:
            return None
        return {"type": "vault_change", "path": rel, "kind": kind, "change": change}

    def coalesce_viewer_changes(self, changes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Collapse atomic-save bursts so a live file is never reported as deleted."""
        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in changes:
            grouped.setdefault(str(item["path"]), []).append(item)

        coalesced: list[dict[str, Any]] = []
        for path, items in grouped.items():
            item = dict(items[-1])
            observed = {str(candidate["change"]) for candidate in items}
            if (self.root / path).exists():
                item["change"] = "added" if observed == {"added"} else "modified"
            else:
                item["change"] = "deleted"
            coalesced.append(item)
        return sorted(coalesced, key=lambda value: str(value["path"]))

    def read_file(
        self,
        path: str,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> ToolResult:
        target = self.safe_path(path)
        if not target.exists():
            fallback = self._unique_sources_basename(path)
            if fallback is None:
                return ToolResult(f"NOT FOUND: {path}", trace("Read failed", "File not found.", path=path))
            target = fallback
            path = fallback.relative_to(self.root).as_posix()
        if target.is_dir():
            return ToolResult(f"IS DIRECTORY: {path}", trace("Read failed", "Path is a directory.", path=path))

        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        if start_line is None and len(lines) > self.settings.max_file_lines_without_range:
            shown = self.settings.max_file_lines_without_range
            message = (
                f"[FILE TRUNCATED: {len(lines)} lines total, showing first {shown} only]\n"
                "This file is too large to read without a line range. Check the locator for "
                "the relevant line range, then call read_file again with start_line and end_line.\n\n"
                + "\n".join(lines[:shown])
            )
            return ToolResult(
                message,
                trace(
                    "Reading large file preview",
                    f"{path} has {len(lines)} lines; returned the first {shown} lines and requested a targeted range.",
                    path=path,
                    line_range=(1, shown),
                ),
            )

        start = max((start_line or 1) - 1, 0)
        stop = min(end_line or len(lines), len(lines))
        selected = lines[start:stop]
        if start_line is not None:
            output = "\n".join(f"{start + idx + 1}: {line}" for idx, line in enumerate(selected))
        else:
            output = "\n".join(selected)

        return ToolResult(
            output,
            trace(
                "Reading source",
                f"Read {len(selected)} line{'s' if len(selected) != 1 else ''}.",
                path=path,
                line_range=(start + 1, stop) if selected else None,
            ),
        )

    def list_files(self, path: str = "") -> ToolResult:
        target = self.safe_path(path)
        if not target.exists():
            return ToolResult(f"NOT FOUND: {path}", trace("List failed", "Directory not found.", path=path))
        if not target.is_dir():
            return ToolResult(f"NOT DIRECTORY: {path}", trace("List failed", "Path is not a directory.", path=path))

        rows = []
        for item in sorted(target.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.lower())):
            if self._is_excluded_path(item):
                continue
            tag = "DIR" if item.is_dir() else "FILE"
            rows.append(f"[{tag}] {item.name}")
        return ToolResult(
            "\n".join(rows) or "(empty directory)",
            trace("Listing vault directory", f"Listed {len(rows)} item{'s' if len(rows) != 1 else ''}.", path=path or "."),
        )

    def search_files(self, pattern: str, path: str = "", file_glob: str = "*.md") -> ToolResult:
        base = self.safe_path(path)
        if not base.exists():
            return ToolResult(f"NOT FOUND: {path}", trace("Search failed", "Search path not found.", path=path))
        if base.is_file():
            candidates = [base]
        else:
            candidates = [
                candidate
                for candidate in base.rglob("*")
                if candidate.is_file()
                and not self._is_excluded_path(candidate)
                and fnmatch.fnmatch(candidate.name, file_glob or "*")
            ]

        matches: list[str] = []
        for candidate in candidates:
            try:
                lines = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            rel = candidate.relative_to(self.root)
            for idx, line in enumerate(lines, start=1):
                if pattern in line:
                    matches.append(f"{rel}:{idx}:{line}")
                    if len(matches) >= self.settings.search_match_limit:
                        break
            if len(matches) >= self.settings.search_match_limit:
                break

        output = "\n".join(matches) if matches else "No matches found."
        if len(output) > self.settings.search_output_limit:
            output = output[: self.settings.search_output_limit] + "\n[TRUNCATED]"
        return ToolResult(
            output,
            trace(
                "Searching vault",
                f"Pattern {json.dumps(pattern)} produced {len(matches)} match{'es' if len(matches) != 1 else ''}.",
                path=path or ".",
            ),
        )

    def call(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        if name == "read_file":
            return self.read_file(
                str(arguments.get("path", "")),
                arguments.get("start_line"),
                arguments.get("end_line"),
            )
        if name == "list_files":
            return self.list_files(str(arguments.get("path", "")))
        if name == "search_files":
            return self.search_files(
                str(arguments.get("pattern", "")),
                str(arguments.get("path", "")),
                str(arguments.get("file_glob", "*.md")),
            )
        return ToolResult(f"Unknown read-only tool: {name}", trace("Tool error", f"Unknown tool: {name}"))


def startup_preflight(toolbox: VaultToolbox) -> tuple[str, list[ChatEvent]]:
    """Load deterministic startup files for a new web chat session."""
    docs: list[tuple[str, str]] = []
    events: list[ChatEvent] = []
    required = ["AGENTS.md", "CLAUDE.md", "index.md"]
    for rel in required:
        result = toolbox.read_file(rel)
        docs.append((rel, result.output))
        events.append(trace("Startup preflight", f"Loaded {rel}.", path=rel))

    rules_root = toolbox.safe_path(".claude/rules")
    rule_paths = sorted(
        path.relative_to(toolbox.root).as_posix()
        for path in rules_root.rglob("*.md")
        if path.is_file()
    )
    for rel in rule_paths:
        result = toolbox.read_file(rel)
        docs.append((rel, result.output))
        events.append(trace("Startup preflight", f"Loaded {rel}.", path=rel))

    content = "\n\n".join(f"<vault_doc path=\"{path}\">\n{body}\n</vault_doc>" for path, body in docs)
    return content, events
