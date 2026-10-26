from __future__ import annotations

import asyncio
import json
import os
import signal
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from .agent import _is_workflow_a_or_write_request
from .config import Settings
from .events import ChatEvent, answer_delta, answer_done, error, trace
from .markdown import chunk_text, normalize_display_math


CODEX_STDIO_LIMIT = 20 * 1024 * 1024
CODEX_IDLE_TRACE_SECONDS = 30


@dataclass
class CodexCliSession:
    session_id: str
    active_process: asyncio.subprocess.Process | None = None
    codex_thread_id: str | None = None


class CodexCliAgent:
    """Minimal website adapter for `codex exec --json`.

    Each browser chat keeps one local read-only Codex thread so follow-up
    questions behave like a continued CLI conversation.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._sessions: dict[str, CodexCliSession] = {}

    def _session(self, session_id: str | None) -> CodexCliSession:
        resolved = session_id or "default"
        session = self._sessions.get(resolved)
        if session is None:
            session = CodexCliSession(session_id=resolved)
            self._sessions[resolved] = session
        return session

    def _command(self, message: str, session: CodexCliSession) -> list[str]:
        command = [
            self.settings.codex_binary,
            "-a",
            "never",
            "-s",
            "read-only",
            "exec",
        ]
        if self.settings.codex_model:
            command.extend(["-m", self.settings.codex_model])

        if session.codex_thread_id:
            command.extend(
                [
                    "resume",
                    "--json",
                    "--skip-git-repo-check",
                    session.codex_thread_id,
                    self._resume_prompt(message),
                ]
            )
            return command

        command.extend(
            [
                "--json",
                "--skip-git-repo-check",
                "-C",
                str(self.settings.vault_root),
                self._initial_prompt(message),
            ]
        )
        return command

    def _visible_answer_rules(self) -> str:
        return """Visible-answer rules:
- Do not begin with progress updates such as "Preflight completed", ordering notes, command details, or "I read..." status paragraphs.
- For explicit Workflow B requests, output the required Workflow B answer in the chat only: the answer body plus Workflow Log, Own Knowledge Used, and Steps Skipped sections.
- Do not write files, create source extracts, or mention source-extract/writeback behavior unless refusing or explaining that the website is read-only.
- Use Markdown and MathJax-friendly math."""

    def _initial_prompt(self, message: str) -> str:
        return f"""You are answering through the local physics wiki website, not a terminal chat.

Complete all repository startup and retrieval requirements before answering. Keep that operational work out of the visible final answer unless a required step failed or the user explicitly asks for operational details.

{self._visible_answer_rules()}

User question:
{message}"""

    def _resume_prompt(self, message: str) -> str:
        return f"""Continue the same local physics wiki website conversation.

Use the prior conversation context and any source/context already loaded in this Codex thread. Do not repeat repository startup work unless it is genuinely needed because the follow-up asks for it or the needed context is missing.

{self._visible_answer_rules()}

User follow-up:
{message}"""

    def _environment(self) -> dict[str, str]:
        env = dict(os.environ)
        env.setdefault("NO_COLOR", "1")
        return env

    def _usage_detail(self, usage: dict[str, Any]) -> str:
        input_tokens = usage.get("input_tokens", "unknown")
        output_tokens = usage.get("output_tokens", "unknown")
        return (
            "CLI-reported run total: "
            f"input tokens {input_tokens}; output tokens {output_tokens}. "
            "This is the sum across Codex's internal model calls, source reads, "
            "and any compaction/resume steps; it can be larger than one model "
            "context window."
        )

    def _short_stderr_line(self, line: str) -> str:
        max_length = 600
        if len(line) <= max_length:
            return line
        return f"{line[:max_length]}... [truncated]"

    def _event_error_message(self, event: dict[str, Any]) -> str:
        for key in ("message", "detail", "reason"):
            value = event.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        event_error = event.get("error")
        if isinstance(event_error, str) and event_error.strip():
            return event_error.strip()
        if isinstance(event_error, dict):
            parts = []
            for key in ("message", "detail", "reason", "code"):
                value = event_error.get(key)
                if isinstance(value, str) and value.strip():
                    parts.append(value.strip())
            if parts:
                return " ".join(parts)
            return json.dumps(event_error, ensure_ascii=False)

        return json.dumps(event, ensure_ascii=False)

    async def _stop_process(self, process: asyncio.subprocess.Process) -> None:
        if process.returncode is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            await asyncio.wait_for(process.wait(), timeout=2)
        except TimeoutError:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
            await process.wait()

    async def stream_chat(self, message: str, session_id: str | None = None) -> AsyncIterator[ChatEvent]:
        clean_message = message.strip()
        if not clean_message:
            yield error("Please enter a question.")
            return
        if _is_workflow_a_or_write_request(clean_message):
            text = (
                "This local website prototype is read-only. It can answer questions in chat, including "
                "Workflow B-style full answers, but it cannot run Workflow A or write/edit vault files."
            )
            yield answer_delta(text)
            yield answer_done(text)
            return

        session = self._session(session_id)
        if session.active_process and session.active_process.returncode is None:
            yield error("This session already has a Codex CLI run in progress. Please wait for it to finish.")
            return

        command = self._command(clean_message, session)
        if session.codex_thread_id:
            yield trace("Codex CLI", f"Resuming local Codex thread {session.codex_thread_id} in read-only mode.")
        else:
            yield trace("Codex CLI", "Starting local Codex CLI in read-only mode.")

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(self.settings.vault_root),
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=True,
                env=self._environment(),
                limit=CODEX_STDIO_LIMIT,
            )
        except FileNotFoundError:
            yield error(f"Codex CLI was not found at {self.settings.codex_binary!r}.")
            return

        session.active_process = process
        agent_messages: list[str] = []
        cli_failures: list[str] = []
        stderr_tail: list[str] = []
        stream_failure: str | None = None
        stdout_read_task: asyncio.Task[bytes] | None = None

        async def read_stderr() -> None:
            if process.stderr is None:
                return
            while True:
                raw = await process.stderr.readline()
                if not raw:
                    break
                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                stderr_tail.append(self._short_stderr_line(line))
                del stderr_tail[:-8]

        stderr_task = asyncio.create_task(read_stderr())

        try:
            if process.stdout is None:
                yield error("Codex CLI did not provide stdout.")
                return
            stdout_read_task = asyncio.create_task(process.stdout.readline())
            while True:
                done, _pending = await asyncio.wait({stdout_read_task}, timeout=CODEX_IDLE_TRACE_SECONDS)
                if stdout_read_task not in done:
                    yield trace(
                        "Codex CLI",
                        "Still waiting for Codex CLI; no new progress event yet.",
                    )
                    continue
                try:
                    raw = stdout_read_task.result()
                except ValueError:
                    stream_failure = (
                        "Codex CLI produced an unusually large progress/output event, so the website bridge "
                        "stopped this run before it could safely finish. Please try again; if it repeats, "
                        "ask a narrower question or avoid broad Workflow B searches."
                    )
                    await self._stop_process(process)
                    break
                stdout_read_task = None
                if not raw:
                    break
                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    stdout_read_task = asyncio.create_task(process.stdout.readline())
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    stdout_read_task = asyncio.create_task(process.stdout.readline())
                    continue
                async for chat_event in self._handle_codex_event(event, session, agent_messages, cli_failures):
                    yield chat_event
                stdout_read_task = asyncio.create_task(process.stdout.readline())

            return_code = await process.wait()
            await stderr_task
        finally:
            if stdout_read_task is not None and not stdout_read_task.done():
                stdout_read_task.cancel()
            await self._stop_process(process)
            session.active_process = None
            if not stderr_task.done():
                stderr_task.cancel()

        yield trace("Codex CLI", f"Codex CLI process exited with status {return_code}.")

        if stream_failure:
            yield error(stream_failure)
            return

        if cli_failures:
            detail = "\n".join(cli_failures[-3:])
            yield error(f"Codex CLI stopped before completing the answer.\n{detail}")
            return

        if return_code != 0:
            detail = "\n".join(stderr_tail) if stderr_tail else "No stderr output captured."
            yield error(f"Codex CLI exited with status {return_code}.\n{detail}")
            return

        if len(agent_messages) > 1:
            yield trace(
                "Codex CLI",
                f"Received {len(agent_messages) - 1} interim assistant update(s); showing the final answer only.",
            )

        final_text = normalize_display_math(agent_messages[-1].strip() if agent_messages else "")
        if not final_text:
            yield error("Codex CLI finished but did not return a final answer.")
            return

        yield trace("Composing answer", "Streaming the final Markdown response to the interface.")
        for chunk in chunk_text(final_text):
            yield answer_delta(chunk)
            await asyncio.sleep(0)
        yield answer_done(final_text)

    async def _handle_codex_event(
        self,
        event: dict[str, Any],
        session: CodexCliSession,
        agent_messages: list[str],
        cli_failures: list[str],
    ) -> AsyncIterator[ChatEvent]:
        event_type = str(event.get("type", ""))
        if event_type == "thread.started":
            thread_id = str(event.get("thread_id", ""))
            if thread_id:
                session.codex_thread_id = thread_id
            yield trace("Codex CLI", f"Started local Codex thread {thread_id}.")
            return
        if event_type == "turn.started":
            yield trace("Codex CLI", "Codex is working.")
            return
        if event_type in {"turn.failed", "thread.failed", "error"}:
            message = self._event_error_message(event)
            cli_failures.append(message)
            yield trace("Codex CLI", f"Codex reported a failure: {message}")
            return
        if event_type == "turn.completed":
            usage = event.get("usage")
            if isinstance(usage, dict):
                yield trace("Codex usage", self._usage_detail(usage))
            return
        if event_type != "item.completed":
            return

        item = event.get("item")
        if not isinstance(item, dict):
            return
        item_type = str(item.get("type", ""))
        if item_type == "agent_message":
            text = item.get("text")
            if isinstance(text, str):
                agent_messages.append(text)
            return
        if item_type == "function_call":
            name = item.get("name") or "tool"
            yield trace("Codex tool", f"Codex used {name}.")
            return
        if item_type == "command_execution":
            command = item.get("command") or "shell command"
            yield trace("Codex command", str(command))
            return

    async def cancel(self, session_id: str | None = None) -> None:
        session = self._session(session_id)
        process = session.active_process
        if process is None or process.returncode is not None:
            return
        await self._stop_process(process)
