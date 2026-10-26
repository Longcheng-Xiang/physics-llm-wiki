from __future__ import annotations

from pathlib import Path

import pytest

from app.config import Settings
from app.vault import VaultAccessError, VaultToolbox, startup_preflight


def make_settings(root: Path) -> Settings:
    return Settings(
        vault_root=root,
        openai_api_key=None,
        model="gpt-5.4",
        reasoning_effort="medium",
        agent_backend="openai",
        codex_binary="codex",
        codex_model=None,
        max_agent_iterations=4,
        max_output_tokens=1000,
        workflow_b_primary_source_read_synthesis_threshold=3,
        max_file_lines_without_range=3,
        search_match_limit=20,
        search_output_limit=8000,
    )


def test_safe_path_blocks_escape(tmp_path: Path) -> None:
    toolbox = VaultToolbox(make_settings(tmp_path))
    with pytest.raises(VaultAccessError):
        toolbox.safe_path("../outside.md")


def test_large_file_requires_line_range(tmp_path: Path) -> None:
    file_path = tmp_path / "large.md"
    file_path.write_text("\n".join(f"line {idx}" for idx in range(1, 7)), encoding="utf-8")
    toolbox = VaultToolbox(make_settings(tmp_path))

    preview = toolbox.read_file("large.md")
    assert "[FILE TRUNCATED: 6 lines total" in preview.output
    assert "line 3" in preview.output
    assert "line 4" not in preview.output

    ranged = toolbox.read_file("large.md", start_line=4, end_line=5)
    assert ranged.output == "4: line 4\n5: line 5"


def test_read_file_resolves_unique_sources_basename(tmp_path: Path) -> None:
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "B5_Demo.defaultmethod.tex").write_text("source artifact", encoding="utf-8")
    toolbox = VaultToolbox(make_settings(tmp_path))

    result = toolbox.read_file("B5_Demo.defaultmethod.tex")

    assert result.output == "source artifact"
    assert result.trace["path"] == "sources/B5_Demo.defaultmethod.tex"


def test_tool_registry_is_read_only(tmp_path: Path) -> None:
    toolbox = VaultToolbox(make_settings(tmp_path))
    names = {schema["name"] for schema in toolbox.schemas}
    assert names == {"read_file", "list_files", "search_files"}
    assert "write_file" not in names
    assert "delete_path" not in names


def test_viewer_lists_markdown_but_skips_private_and_generated_directories(tmp_path: Path) -> None:
    (tmp_path / "answers").mkdir()
    (tmp_path / "answers" / "solution.md").write_text("# Solution", encoding="utf-8")
    (tmp_path / "answers" / "figure.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / ".obsidian" / "private.md").write_text("private", encoding="utf-8")
    (tmp_path / "viewer" / "frontend" / "node_modules").mkdir(parents=True)
    (tmp_path / "viewer" / "frontend" / "node_modules" / "readme.md").write_text("generated", encoding="utf-8")
    toolbox = VaultToolbox(make_settings(tmp_path))

    listed = toolbox.viewer_markdown_files()

    assert [item["path"] for item in listed] == ["answers/solution.md"]


def test_viewer_exposes_claude_markdown_but_keeps_other_hidden_paths_blocked(tmp_path: Path) -> None:
    allowed = ".claude/rules/example.md"
    blocked = [".claude/.hidden/secret.md", ".claude/settings.json", ".other/private.md",
               ".obsidian/private.md", "nested/.claude/private.md"]
    for rel in [allowed, *blocked]:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# Rule", encoding="utf-8")
    toolbox = VaultToolbox(make_settings(tmp_path))
    assert [item["path"] for item in toolbox.viewer_markdown_files()] == [allowed]
    assert toolbox.read_viewer_markdown(allowed)["content"] == "# Rule"
    assert toolbox.viewer_change(tmp_path / allowed, "modified")["path"] == allowed
    for rel in blocked:
        with pytest.raises(VaultAccessError):
            toolbox.read_viewer_markdown(rel)


def test_viewer_reads_complete_markdown_and_rejects_other_file_types(tmp_path: Path) -> None:
    (tmp_path / "answer.md").write_text("# Answer\n\n$E=mc^2$", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not viewer content", encoding="utf-8")
    toolbox = VaultToolbox(make_settings(tmp_path))

    result = toolbox.read_viewer_markdown("answer.md")

    assert result["content"] == "# Answer\n\n$E=mc^2$"
    assert result["path"] == "answer.md"
    with pytest.raises(VaultAccessError):
        toolbox.read_viewer_markdown("notes.txt")


def test_viewer_asset_path_allows_images_and_blocks_other_files(tmp_path: Path) -> None:
    (tmp_path / "diagram.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / "script.py").write_text("print('no')", encoding="utf-8")
    toolbox = VaultToolbox(make_settings(tmp_path))

    assert toolbox.viewer_asset_path("diagram.svg") == tmp_path / "diagram.svg"
    with pytest.raises(VaultAccessError):
        toolbox.viewer_asset_path("script.py")


def test_viewer_change_reports_only_markdown_and_image_assets(tmp_path: Path) -> None:
    toolbox = VaultToolbox(make_settings(tmp_path))

    markdown = toolbox.viewer_change(tmp_path / "answer.md", "modified")
    asset = toolbox.viewer_change(tmp_path / "images" / "diagram.svg", "added")

    assert markdown == {
        "type": "vault_change",
        "path": "answer.md",
        "kind": "markdown",
        "change": "modified",
    }
    assert asset == {
        "type": "vault_change",
        "path": "images/diagram.svg",
        "kind": "asset",
        "change": "added",
    }
    assert toolbox.viewer_change(tmp_path / "notes.txt", "modified") is None


def test_viewer_change_coalescing_handles_atomic_saves(tmp_path: Path) -> None:
    target = tmp_path / "answer.md"
    target.write_text("# Current file", encoding="utf-8")
    toolbox = VaultToolbox(make_settings(tmp_path))

    live_burst = [
        toolbox.viewer_change(target, "deleted"),
        toolbox.viewer_change(target, "added"),
    ]
    assert toolbox.coalesce_viewer_changes([item for item in live_burst if item is not None]) == [
        {
            "type": "vault_change",
            "path": "answer.md",
            "kind": "markdown",
            "change": "modified",
        }
    ]

    target.unlink()
    deleted_burst = [
        toolbox.viewer_change(target, "modified"),
        toolbox.viewer_change(target, "deleted"),
    ]
    assert toolbox.coalesce_viewer_changes([item for item in deleted_burst if item is not None]) == [
        {
            "type": "vault_change",
            "path": "answer.md",
            "kind": "markdown",
            "change": "deleted",
        }
    ]


def test_startup_preflight_loads_required_docs(tmp_path: Path) -> None:
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text("agents", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("claude", encoding="utf-8")
    (tmp_path / "index.md").write_text("index", encoding="utf-8")
    (tmp_path / ".claude" / "rules" / "workflow_b.md").write_text("workflow b", encoding="utf-8")

    content, events = startup_preflight(VaultToolbox(make_settings(tmp_path)))

    assert '<vault_doc path="AGENTS.md">' in content
    assert '<vault_doc path="CLAUDE.md">' in content
    assert '<vault_doc path="index.md">' in content
    assert '<vault_doc path=".claude/rules/workflow_b.md">' in content
    assert [event["path"] for event in events] == [
        "AGENTS.md",
        "CLAUDE.md",
        "index.md",
        ".claude/rules/workflow_b.md",
    ]
