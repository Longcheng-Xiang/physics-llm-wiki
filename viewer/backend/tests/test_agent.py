from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.agent import (
    WikiChatAgent,
    _course_locator_paths,
    _course_rule_paths,
    _friendly_limit_error,
    _is_workflow_a_or_write_request,
    _is_workflow_b_request,
    _looks_like_tool_transcript,
)
from app.config import Settings
from app.markdown import normalize_display_math
from app.vault import VaultToolbox


def make_settings(root: Path) -> Settings:
    return Settings(
        vault_root=root,
        openai_api_key="test-key",
        model="gpt-5.4",
        reasoning_effort="medium",
        agent_backend="openai",
        codex_binary="codex",
        codex_model=None,
        max_agent_iterations=4,
        max_output_tokens=1000,
        workflow_b_primary_source_read_synthesis_threshold=3,
        max_file_lines_without_range=300,
        search_match_limit=20,
        search_output_limit=8000,
    )


def seed_startup(root: Path) -> None:
    (root / ".claude" / "rules").mkdir(parents=True)
    (root / "AGENTS.md").write_text("agents", encoding="utf-8")
    (root / "CLAUDE.md").write_text("claude", encoding="utf-8")
    (root / "index.md").write_text("index route", encoding="utf-8")
    (root / ".claude" / "rules" / "workflow_b.md").write_text("workflow b", encoding="utf-8")


class FakeResponses:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if not self.responses:
            raise AssertionError("No fake response queued")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class FakeClient:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = FakeResponses(responses)


async def collect(agent: WikiChatAgent, message: str, session_id: str = "s1") -> list[dict[str, Any]]:
    return [event async for event in agent.stream_chat(message, session_id)]


@pytest.mark.asyncio
async def test_workflow_a_request_is_refused_without_model_call(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    fake = FakeClient([])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Please do this using Workflow A")

    assert events[-1]["type"] == "answer_done"
    assert "read-only" in events[-1]["text"]
    assert fake.responses.calls == []


def test_read_only_guard_allows_physics_write_wording() -> None:
    prompt = (
        "Workflow B: In B5 GR, derive the conserved quantities, write the radial equation "
        "as an effective potential, and explain the ISCO."
    )

    assert not _is_workflow_a_or_write_request(prompt)
    assert _is_workflow_a_or_write_request("Please write this answer to a Markdown file.")
    assert _is_workflow_a_or_write_request("Update questions_and_answers/problem_sets/B5.md")


def test_workflow_b_requires_explicit_name() -> None:
    assert _is_workflow_b_request("Use Workflow B for this derivation.")
    assert _is_workflow_b_request("Workflow B: derive the result.")
    assert not _is_workflow_b_request("Please give a detailed source-grounded derivation.")
    assert not _is_workflow_b_request("What does Workflow B do?")


@pytest.mark.asyncio
async def test_physics_write_wording_reaches_model(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    fake = FakeClient([SimpleNamespace(output=[], output_text="Answer from normal model path.")])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Workflow B: write the radial equation as an effective potential.")

    assert events[-1] == {"type": "answer_done", "text": "Answer from normal model path."}
    assert len(fake.responses.calls) == 1


@pytest.mark.asyncio
async def test_tool_call_loop_reads_vault_and_returns_answer(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    (tmp_path / "source.md").write_text("Physics fact: $E=mc^2$.", encoding="utf-8")
    first = SimpleNamespace(
        output=[
            SimpleNamespace(
                type="function_call",
                call_id="call_1",
                name="read_file",
                arguments=json.dumps({"path": "source.md", "start_line": 1, "end_line": 1}),
            )
        ],
        output_text="",
    )
    second = SimpleNamespace(output=[], output_text="The source says \\(E=mc^2\\).")
    fake = FakeClient([first, second])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Explain the equation carefully")
    done = [event for event in events if event["type"] == "answer_done"][-1]

    assert done["text"] == "The source says $E=mc^2$."
    assert any(event.get("title") == "Using vault tool" for event in events)
    assert any(event.get("path") == "source.md" for event in events)
    assert len(fake.responses.calls) == 2
    assert {schema["name"] for schema in fake.responses.calls[0]["tools"]} == {
        "read_file",
        "list_files",
        "search_files",
    }


@pytest.mark.asyncio
async def test_tool_budget_falls_back_to_final_synthesis(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    (tmp_path / "source.md").write_text("A gathered source.", encoding="utf-8")
    settings = make_settings(tmp_path)
    settings = Settings(
        vault_root=settings.vault_root,
        openai_api_key=settings.openai_api_key,
        model=settings.model,
        reasoning_effort=settings.reasoning_effort,
        agent_backend=settings.agent_backend,
        codex_binary=settings.codex_binary,
        codex_model=settings.codex_model,
        max_agent_iterations=1,
        max_output_tokens=settings.max_output_tokens,
        workflow_b_primary_source_read_synthesis_threshold=(
            settings.workflow_b_primary_source_read_synthesis_threshold
        ),
        max_file_lines_without_range=settings.max_file_lines_without_range,
        search_match_limit=settings.search_match_limit,
        search_output_limit=settings.search_output_limit,
    )
    first = SimpleNamespace(
        output=[
            SimpleNamespace(
                type="function_call",
                call_id="call_1",
                name="read_file",
                arguments=json.dumps({"path": "source.md"}),
            )
        ],
        output_text="",
    )
    second = SimpleNamespace(output=[], output_text="Final answer from gathered source.")
    fake = FakeClient([first, second])
    agent = WikiChatAgent(settings, VaultToolbox(settings), fake)

    events = await collect(agent, "Explain the gathered result")

    assert events[-1]["type"] == "answer_done"
    assert events[-1]["text"].startswith("Final answer from gathered source.")
    assert "Limit warning: The website reached its configured model/tool-pass limit" in events[-1]["text"]
    assert any(event.get("title") == "Limit warning" for event in events)
    assert any(event.get("title") == "Final synthesis" for event in events)
    assert len(fake.responses.calls) == 2
    assert "tools" not in fake.responses.calls[1]


@pytest.mark.asyncio
async def test_workflow_b_uses_configured_tool_budget(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    (tmp_path / "source.md").write_text("A gathered source.", encoding="utf-8")
    base = make_settings(tmp_path)
    settings = Settings(
        vault_root=base.vault_root,
        openai_api_key=base.openai_api_key,
        model=base.model,
        reasoning_effort=base.reasoning_effort,
        agent_backend=base.agent_backend,
        codex_binary=base.codex_binary,
        codex_model=base.codex_model,
        max_agent_iterations=7,
        max_output_tokens=base.max_output_tokens,
        workflow_b_primary_source_read_synthesis_threshold=(
            base.workflow_b_primary_source_read_synthesis_threshold
        ),
        max_file_lines_without_range=base.max_file_lines_without_range,
        search_match_limit=base.search_match_limit,
        search_output_limit=base.search_output_limit,
    )

    def tool_call(number: int) -> SimpleNamespace:
        return SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="function_call",
                    call_id=f"call_{number}",
                    name="read_file",
                    arguments=json.dumps({"path": "source.md"}),
                )
            ],
            output_text="",
        )

    fake = FakeClient(
        [tool_call(number) for number in range(1, 7)]
        + [SimpleNamespace(output=[], output_text="Answer after enough retrieval.")]
    )
    agent = WikiChatAgent(settings, VaultToolbox(settings), fake)

    events = await collect(agent, "Workflow B: derive this source-grounded result.")

    assert events[-1] == {"type": "answer_done", "text": "Answer after enough retrieval."}
    assert not any(event.get("title") == "Final synthesis" for event in events)
    assert len(fake.responses.calls) == 7


@pytest.mark.asyncio
async def test_workflow_b_primary_source_coverage_forces_final_synthesis(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    (tmp_path / "sources").mkdir()
    for number in range(1, 5):
        (tmp_path / "sources" / f"range_{number}.defaultmethod.tex").write_text(f"source {number}", encoding="utf-8")

    first = SimpleNamespace(
        output=[
            SimpleNamespace(
                type="function_call",
                call_id=f"call_{number}",
                name="read_file",
                arguments=json.dumps({"path": f"sources/range_{number}.defaultmethod.tex"}),
            )
            for number in range(1, 5)
        ],
        output_text="",
    )
    second = SimpleNamespace(output=[], output_text="Final answer from covered sources.")
    fake = FakeClient([first, second])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Workflow B: derive this source-grounded result.")

    assert events[-1] == {"type": "answer_done", "text": "Final answer from covered sources."}
    assert any(event.get("title") == "Source coverage" for event in events)
    assert any(
        event.get("title") == "Final synthesis" and "primary source ranges" in event.get("detail", "")
        for event in events
    )
    assert len(fake.responses.calls) == 2
    assert "tools" not in fake.responses.calls[1]


@pytest.mark.asyncio
async def test_output_token_limit_warning_is_streamed_and_appended(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    first = SimpleNamespace(
        output=[],
        output_text="Partial answer.",
        status="incomplete",
        incomplete_details=SimpleNamespace(reason="max_output_tokens"),
    )
    fake = FakeClient([first])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Explain the partial result")

    assert any(event.get("title") == "Limit warning" for event in events)
    assert events[-1]["type"] == "answer_done"
    assert events[-1]["text"].startswith("Partial answer.")
    assert "Limit warning: The model reached the configured output-token limit" in events[-1]["text"]


@pytest.mark.asyncio
async def test_context_window_limit_error_is_reported_cleanly(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    fake = FakeClient([RuntimeError("maximum context length exceeded for this model")])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Explain the result")

    assert any(event.get("title") == "Limit warning" for event in events)
    assert events[-1]["type"] == "error"
    assert events[-1]["message"].startswith("Context window exceeded:")
    assert "no wiki files were changed" in events[-1]["message"]


def test_friendly_limit_error_classifies_rate_and_output_limits() -> None:
    rate_error = SimpleNamespace(status_code=429, body={"error": "rate limit"})
    output_error = RuntimeError("max_output_tokens exceeded")

    assert _friendly_limit_error(rate_error) is not None  # type: ignore[arg-type]
    assert _friendly_limit_error(output_error) is not None


def test_normalize_display_math_preserves_code_fences() -> None:
    text = "Inline \\(a+b\\).\n```tex\n\\(not mathjax\\)\n```\n\\[x = y\\]"
    normalized = normalize_display_math(text)

    assert "Inline $a+b$." in normalized
    assert "```tex\n\\(not mathjax\\)\n```" in normalized
    assert "$$\nx = y\n$$" in normalized


def test_normalize_display_math_promotes_standalone_inline_math() -> None:
    text = "Use\n\n$L=-mc^2\\sqrt{1-v^2/c^2}$\n\nbut keep inline $v$ in prose."
    normalized = normalize_display_math(text)

    assert "$$\nL=-mc^2\\sqrt{1-v^2/c^2}\n$$" in normalized
    assert "inline $v$ in prose" in normalized


def test_course_rule_paths_are_generic_and_deduplicated() -> None:
    prompt = "Compare B3 and b4 ideas, then return to B3."

    assert _course_rule_paths(prompt) == ["course_rules/B3.md", "course_rules/B4.md"]


def test_course_locator_paths_are_generic_and_deduplicated(tmp_path: Path) -> None:
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "B5_GR_(Balbus)_Locator.md").write_text("balbus", encoding="utf-8")
    (tmp_path / "sources" / "B5_GR_(Supplementary)_Locator.md").write_text(
        "supplementary",
        encoding="utf-8",
    )
    (tmp_path / "sources" / "B4_Nuclear_Slides_(Wilkinson)_Locator.md").write_text("b4", encoding="utf-8")

    prompt = "In B5, compare with b4, then return to B5."

    assert _course_locator_paths(tmp_path, prompt) == [
        "sources/B5_GR_(Balbus)_Locator.md",
        "sources/B5_GR_(Supplementary)_Locator.md",
        "sources/B4_Nuclear_Slides_(Wilkinson)_Locator.md",
    ]


@pytest.mark.asyncio
async def test_named_course_rule_is_loaded_without_topic_prefetch(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    (tmp_path / "course_rules").mkdir()
    (tmp_path / "course_rules" / "B3.md").write_text("B3 says read the source locators.", encoding="utf-8")
    fake = FakeClient([SimpleNamespace(output=[], output_text="Answer from normal tool loop.")])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Workflow B: In B3, explain a derivation.")

    assert events[-1] == {"type": "answer_done", "text": "Answer from normal tool loop."}
    assert any(event.get("title") == "Course rule preflight" for event in events)
    assert not any(event.get("title") == "Prefetch route" for event in events)
    assert "tools" in fake.responses.calls[0]


@pytest.mark.asyncio
async def test_named_course_locators_are_loaded_without_topic_prefetch(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "B5_Demo_Locator.md").write_text("B5 line routing.", encoding="utf-8")
    fake = FakeClient([SimpleNamespace(output=[], output_text="Answer from normal tool loop.")])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Workflow B: In B5, explain a derivation.")

    assert events[-1] == {"type": "answer_done", "text": "Answer from normal tool loop."}
    assert any(event.get("title") == "Course locator preflight" for event in events)
    assert not any(event.get("title") == "Prefetch route" for event in events)
    assert "B5 line routing." in fake.responses.calls[0]["instructions"]


def test_tool_transcript_detector_catches_leaked_tool_syntax() -> None:
    leaked = '{"tool_uses":[{"recipient_name":"functions.search_files"}]}to=functions.search_files'

    assert _looks_like_tool_transcript(leaked)
    assert not _looks_like_tool_transcript("Workflow log: Used the B3 quantum notes and then answered.")


@pytest.mark.asyncio
async def test_leaked_tool_transcript_is_repaired_before_streaming(tmp_path: Path) -> None:
    seed_startup(tmp_path)
    first = SimpleNamespace(
        output=[],
        output_text='{"tool_uses":[{"recipient_name":"functions.search_files"}]}to=functions.search_files',
    )
    second = SimpleNamespace(output=[], output_text="Clean final answer with \\(x\\).")
    fake = FakeClient([first, second])
    agent = WikiChatAgent(make_settings(tmp_path), VaultToolbox(make_settings(tmp_path)), fake)

    events = await collect(agent, "Explain a physics derivation.")

    assert events[-1] == {"type": "answer_done", "text": "Clean final answer with $x$."}
    assert any(event.get("title") == "Answer repair" for event in events)
    assert len(fake.responses.calls) == 2
    assert "tools" not in fake.responses.calls[1]
