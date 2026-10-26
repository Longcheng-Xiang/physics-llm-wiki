from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app import cli_agent
from app.cli_agent import CODEX_STDIO_LIMIT, CodexCliAgent
from app.config import Settings


def make_settings(root: Path) -> Settings:
    return Settings(
        vault_root=root,
        openai_api_key=None,
        model="gpt-5.4",
        reasoning_effort="medium",
        agent_backend="codex_cli",
        codex_binary="codex",
        codex_model=None,
        max_agent_iterations=4,
        max_output_tokens=1000,
        workflow_b_primary_source_read_synthesis_threshold=3,
        max_file_lines_without_range=300,
        search_match_limit=20,
        search_output_limit=8000,
    )


def test_codex_cli_command_wraps_user_question_for_website(tmp_path: Path) -> None:
    agent = CodexCliAgent(make_settings(tmp_path))
    session = agent._session("session-1")

    command = agent._command("Workflow B: explain linewidth.", session)
    prompt = command[-1]

    assert command[command.index("-a") + 1] == "never"
    assert command[command.index("-s") + 1] == "read-only"
    assert "--ephemeral" not in command
    assert "local physics wiki website" in prompt
    assert "Do not begin with progress updates" in prompt
    assert "User question:\nWorkflow B: explain linewidth." in prompt


def test_codex_cli_resume_command_uses_saved_thread(tmp_path: Path) -> None:
    agent = CodexCliAgent(make_settings(tmp_path))
    session = agent._session("session-1")
    session.codex_thread_id = "019df919-9db8-7a01-9c36-550be83ec1c6"

    command = agent._command("Can you explain the last equation again?", session)
    prompt = command[-1]

    assert command[command.index("-a") + 1] == "never"
    assert command[command.index("-s") + 1] == "read-only"
    assert command[command.index("resume") + 1] == "--json"
    assert "019df919-9db8-7a01-9c36-550be83ec1c6" in command
    assert "--ephemeral" not in command
    assert "-C" not in command
    assert "Continue the same local physics wiki website conversation" in prompt
    assert "Can you explain the last equation again?" in prompt


def test_codex_cli_usage_detail_explains_cumulative_tokens(tmp_path: Path) -> None:
    agent = CodexCliAgent(make_settings(tmp_path))

    detail = agent._usage_detail({"input_tokens": 483000, "output_tokens": 1200})

    assert "input tokens 483000" in detail
    assert "sum across Codex's internal model calls" in detail
    assert "larger than one model context window" in detail


class FakeReader:
    def __init__(self, lines: list[bytes]) -> None:
        self._lines = lines

    async def readline(self) -> bytes:
        if not self._lines:
            return b""
        return self._lines.pop(0)


class RaisingReader:
    async def readline(self) -> bytes:
        raise ValueError("Separator is not found, and chunk exceed the limit")


class FakeProcess:
    def __init__(self, stdout_lines: list[dict[str, Any]]) -> None:
        self.stdout = FakeReader([json.dumps(line).encode("utf-8") + b"\n" for line in stdout_lines])
        self.stderr = FakeReader([])
        self.returncode: int | None = None
        self.pid = 12345

    async def wait(self) -> int:
        self.returncode = 0
        return 0


@pytest.mark.asyncio
async def test_codex_cli_stream_uses_only_final_agent_message(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = FakeProcess(
        [
            {"type": "thread.started", "thread_id": "thread-1"},
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "Preflight update that should not become answer."},
            },
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "Final answer with \\(x\\)."},
            },
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 5}},
        ]
    )

    captured_kwargs: dict[str, Any] = {}

    async def fake_create_subprocess_exec(*_args: Any, **_kwargs: Any) -> FakeProcess:
        captured_kwargs.update(_kwargs)
        return process

    monkeypatch.setattr(cli_agent.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)
    agent = CodexCliAgent(make_settings(tmp_path))

    events = [event async for event in agent.stream_chat("question", "session-1")]

    assert events[-1] == {"type": "answer_done", "text": "Final answer with $x$."}
    assert captured_kwargs["limit"] == CODEX_STDIO_LIMIT
    assert agent._session("session-1").codex_thread_id == "thread-1"
    assert "Preflight update" not in events[-1]["text"]
    assert any("interim assistant update" in event.get("detail", "") for event in events)


@pytest.mark.asyncio
async def test_codex_cli_second_message_resumes_saved_thread(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    processes = [
        FakeProcess(
            [
                {"type": "thread.started", "thread_id": "thread-1"},
                {"type": "item.completed", "item": {"type": "agent_message", "text": "First answer."}},
            ]
        ),
        FakeProcess(
            [
                {"type": "thread.started", "thread_id": "thread-1"},
                {"type": "item.completed", "item": {"type": "agent_message", "text": "Follow-up answer."}},
            ]
        ),
    ]
    captured_args: list[tuple[Any, ...]] = []

    async def fake_create_subprocess_exec(*args: Any, **_kwargs: Any) -> FakeProcess:
        captured_args.append(args)
        return processes.pop(0)

    monkeypatch.setattr(cli_agent.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)
    agent = CodexCliAgent(make_settings(tmp_path))

    first_events = [event async for event in agent.stream_chat("first question", "session-1")]
    second_events = [event async for event in agent.stream_chat("what about that?", "session-1")]

    assert first_events[-1] == {"type": "answer_done", "text": "First answer."}
    assert second_events[-1] == {"type": "answer_done", "text": "Follow-up answer."}
    assert "resume" not in captured_args[0]
    assert "resume" in captured_args[1]
    assert "thread-1" in captured_args[1]
    assert "Continue the same local physics wiki website conversation" in captured_args[1][-1]


@pytest.mark.asyncio
async def test_codex_cli_stream_reports_oversized_stdout_event(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = FakeProcess([])
    process.stdout = RaisingReader()
    killed: list[tuple[int, int]] = []

    async def fake_create_subprocess_exec(*_args: Any, **_kwargs: Any) -> FakeProcess:
        return process

    def fake_killpg(pid: int, sig: int) -> None:
        killed.append((pid, sig))
        process.returncode = -sig

    monkeypatch.setattr(cli_agent.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)
    monkeypatch.setattr(cli_agent.os, "killpg", fake_killpg)
    agent = CodexCliAgent(make_settings(tmp_path))

    events = [event async for event in agent.stream_chat("question", "session-1")]

    assert killed
    assert events[-1]["type"] == "error"
    assert "unusually large progress/output event" in events[-1]["message"]


@pytest.mark.asyncio
async def test_codex_cli_stream_reports_failed_turn(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    process = FakeProcess(
        [
            {"type": "thread.started", "thread_id": "thread-1"},
            {
                "type": "turn.failed",
                "error": {"message": "context window exhausted before final answer"},
            },
        ]
    )

    async def fake_create_subprocess_exec(*_args: Any, **_kwargs: Any) -> FakeProcess:
        return process

    monkeypatch.setattr(cli_agent.asyncio, "create_subprocess_exec", fake_create_subprocess_exec)
    agent = CodexCliAgent(make_settings(tmp_path))

    events = [event async for event in agent.stream_chat("question", "session-1")]

    assert events[-1] == {
        "type": "error",
        "message": "Codex CLI stopped before completing the answer.\ncontext window exhausted before final answer",
    }
    assert any("process exited with status 0" in event.get("detail", "") for event in events)


@pytest.mark.asyncio
async def test_codex_cli_refuses_write_requests_before_starting_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fail_create_subprocess_exec(*_args: Any, **_kwargs: Any) -> FakeProcess:
        raise AssertionError("Codex CLI should not start for website write requests")

    monkeypatch.setattr(cli_agent.asyncio, "create_subprocess_exec", fail_create_subprocess_exec)
    agent = CodexCliAgent(make_settings(tmp_path))

    events = [
        event
        async for event in agent.stream_chat(
            "Workflow A: write this answer to a markdown file",
            "session-1",
        )
    ]

    assert events == [
        {
            "type": "answer_delta",
            "text": (
                "This local website prototype is read-only. It can answer questions in chat, including "
                "Workflow B-style full answers, but it cannot run Workflow A or write/edit vault files."
            ),
        },
        {
            "type": "answer_done",
            "text": (
                "This local website prototype is read-only. It can answer questions in chat, including "
                "Workflow B-style full answers, but it cannot run Workflow A or write/edit vault files."
            ),
        },
    ]
