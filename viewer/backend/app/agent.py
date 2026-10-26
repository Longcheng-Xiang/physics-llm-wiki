from __future__ import annotations

import asyncio
import json
import re
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from .config import Settings
from .events import ChatEvent, answer_delta, answer_done, error, trace
from .markdown import chunk_text, normalize_display_math
from .vault import VaultToolbox, startup_preflight


WORKFLOW_A_PATTERN = re.compile(r"\bworkflow\s*a\b", re.IGNORECASE)
WRITE_ACTION_PATTERN = re.compile(r"\b(write|save|export|append|edit|update|delete|create)\b", re.IGNORECASE)
WRITE_TARGET_PATTERN = re.compile(
    r"\b(file|files|folder|folders|directory|directories|path|paths|vault|page|pages|note|notes|"
    r"markdown|document|documents|workflow\s+log|source\s+extracts?|answer\s+files?|q&a)\b|"
    r"(?<!\w)\.(?:md|tex|txt|py|json|ya?ml|toml)\b|"
    r"\bquestions_and_answers\b",
    re.IGNORECASE,
)
COURSE_CODE_PATTERN = re.compile(r"\b(B[0-9]+)\b", re.IGNORECASE)
WORKFLOW_B_PATTERN = re.compile(
    r"(?:"
    r"^\s*workflow\s*b(?:\s+please)?(?:\s*$|\s*[:.-])|"
    r"\b(?:use|using|apply|run|request(?:ing)?|want|choose|select|do)\s+(?:the\s+)?workflow\s*b\b|"
    r"\b(?:via|with|in)\s+(?:the\s+)?workflow\s*b\b|"
    r"\bswitch(?:ing)?\s+to\s+workflow\s*b\b"
    r")",
    re.IGNORECASE,
)
TOOL_TRANSCRIPT_PATTERN = re.compile(
    r'("tool_uses"|recipient_name|to=functions\.|to=multi_tool_use|functions\.(?:read_file|list_files|search_files)|'
    r"\bfunction_call\b|<tool[_-]?use|</tool[_-]?use)",
    re.IGNORECASE,
)
CONTEXT_LIMIT_PATTERN = re.compile(
    r"(context_length_exceeded|context window|context length|maximum context|too many input tokens|"
    r"input.*too large|request.*too large|token limit)",
    re.IGNORECASE | re.DOTALL,
)
OUTPUT_LIMIT_PATTERN = re.compile(r"(max_output_tokens|maximum output|output.*token)", re.IGNORECASE | re.DOTALL)
RATE_LIMIT_PATTERN = re.compile(r"(rate limit|too many requests|quota)", re.IGNORECASE | re.DOTALL)


class ResponsesProtocol(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


class OpenAIProtocol(Protocol):
    responses: ResponsesProtocol


@dataclass
class ChatSession:
    session_id: str
    preflight_text: str
    input_items: list[dict[str, Any]] = field(default_factory=list)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, ChatSession] = {}

    def get(self, session_id: str) -> ChatSession | None:
        return self._sessions.get(session_id)

    def put(self, session: ChatSession) -> None:
        self._sessions[session.session_id] = session

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


BASE_INSTRUCTIONS = """You are the Physics Wiki web chat agent.

You answer from the local physics wiki using only the read-only tools provided.
Before answering a technical physics question, follow the loaded vault instructions:
read the index first, prefer source maps and source locators, use targeted line ranges
for large lecture-note artifacts, and avoid answering from memory when a relevant page exists.

The startup preflight documents embedded below have already been read for this session.
Do not call vault tools merely to reload AGENTS.md, CLAUDE.md, index.md, or .claude/rules files.
Only reread a startup document when you need a narrow, targeted passage.

Course-specific rules live at course_rules/B3.md, course_rules/B4.md, and course_rules/B5.md.
If a question clearly names one of those courses, read course_rules/<course>.md before
course-specific retrieval. Do not look for course rules under .claude/rules/course_rules.

This website is read-only. You must not claim to write, update, append, delete, create, or edit
vault files. If a user asks for Workflow A or file-writing behavior, briefly explain that this
prototype only supports read-only chat and Workflow B-style conversation answers.

Workflow B is supported only in conversation when the user explicitly requests Workflow B.
Do not create Workflow B files, source extract files, or writebacks.
For Workflow B, give the full source-grounded answer in chat, then include a compact Workflow log,
Own knowledge used, and Steps skipped section. If you are close to the tool-pass limit, stop
retrieving and answer from the sources already gathered.

When the prompt already makes the topic obvious, do not begin with broad keyword searches. Instead:
- read the named or clearly implied source map or locator directly if it is obvious from the prompt
- read the relevant course rule directly if a course is named
- read the relevant locator files directly to route source-family choice
- use search_files only when the path or topic is genuinely unclear after those direct reads

When a course rule says that a course has source-family locators, read those locator files directly at
routing time instead of doing repeated broad keyword searches across all source files and optional user-supplied notes.
Once one source family is clearly dominant for the derivation, stop widening retrieval unless the
question genuinely crosses into another family.

If course source locator blocks have already been loaded into the instructions, use those preloaded
locator line ranges directly. Do not list or search for the same course locators, source inventories,
or broad course filenames unless the preloaded locators do not contain the needed topic.

For Workflow B, once targeted primary source ranges cover every requested part of the question, stop
calling tools and answer. Do not keep searching companion notes, inventories, or locator headings just
to double-check already-covered material.

Do not repeatedly probe for missing files. If directory listing or a failed direct check shows that a
relevant tutorial-order file does not exist, note that under Steps skipped instead of searching for it
again under multiple patterns.

Keep Workflow B answers derivation-first but compact. Do not restate the user's question. Avoid long
scene-setting, repeated paraphrases, or decorative structure. Put every symbolic expression inside
$...$ or $$...$$; do not emit raw TeX macros like \\boldsymbol outside math delimiters.

Use Markdown with Obsidian-safe math delimiters: $...$ for inline math and $$...$$ for display math.
Put fraction-heavy, multi-symbol, or otherwise long equations in display math instead of inline math.
Do not use \\( \\) or \\[ \\] in final answers. Do not reveal hidden chain-of-thought; provide concise,
user-facing reasoning summaries and source-grounded explanations.
"""


def _course_codes(message: str) -> list[str]:
    seen: set[str] = set()
    codes: list[str] = []
    for match in COURSE_CODE_PATTERN.finditer(message):
        code = match.group(1).upper()
        if code in seen:
            continue
        seen.add(code)
        codes.append(code)
    return codes


def _course_rule_paths(message: str) -> list[str]:
    return [f"course_rules/{code}.md" for code in _course_codes(message)]


def _course_locator_paths(root: Path, message: str) -> list[str]:
    source_dir = root / "sources"
    if not source_dir.exists():
        return []
    paths = []
    for code in _course_codes(message):
        paths.extend(sorted(source_dir.glob(f"{code}*_Locator.md")))
    return [path.relative_to(root).as_posix() for path in paths]


def _is_workflow_a_or_write_request(message: str) -> bool:
    if WORKFLOW_A_PATTERN.search(message):
        return True
    return bool(WRITE_ACTION_PATTERN.search(message) and WRITE_TARGET_PATTERN.search(message))


def _is_workflow_b_request(message: str) -> bool:
    return bool(WORKFLOW_B_PATTERN.search(message))


def _is_primary_source_read(path: str) -> bool:
    path = path.strip()
    if not path.startswith("sources/"):
        return False
    return not path.endswith(("_Locator.md", "_Map.md", "_Summary.md", "Lecture_Note_Inventory.md"))


def _looks_like_tool_transcript(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    if '"tool_uses"' in lower or "recipient_name" in lower or "to=functions." in lower:
        return True
    return len(TOOL_TRANSCRIPT_PATTERN.findall(text)) >= 3


def _response_incomplete_reason(response: Any) -> str | None:
    status = _attr(response, "status")
    incomplete_details = _attr(response, "incomplete_details")
    reason = _attr(incomplete_details, "reason")
    if reason:
        return str(reason)
    if status == "incomplete":
        return "incomplete"
    return None


def _limit_warning_for_incomplete(reason: str) -> str:
    normalized = reason.replace("_", " ").strip() or "unknown reason"
    if reason == "max_output_tokens":
        return (
            "The model reached the configured output-token limit while composing a response. "
            "The answer may be incomplete; raise MAX_OUTPUT_TOKENS or ask a narrower question."
        )
    return f"The model reported an incomplete response ({normalized}). The answer may be incomplete."


def _append_limit_warnings(text: str, warnings: list[str]) -> str:
    unique_warnings = list(dict.fromkeys(warnings))
    if not text or not unique_warnings:
        return text
    warning_block = "\n".join(f"> Limit warning: {warning}" for warning in unique_warnings)
    return f"{text.rstrip()}\n\n{warning_block}"


def _exception_text(exc: Exception) -> str:
    body = getattr(exc, "body", None)
    if body is None:
        return str(exc)
    try:
        body_text = json.dumps(body, ensure_ascii=False)
    except TypeError:
        body_text = str(body)
    return f"{exc} {body_text}"


def _friendly_limit_error(exc: Exception) -> str | None:
    status_code = getattr(exc, "status_code", None)
    text = _exception_text(exc)
    if CONTEXT_LIMIT_PATTERN.search(text):
        return (
            "Context window exceeded: this chat plus the gathered source text became too large for the "
            "model's context window. Start a fresh chat or narrow the question; no wiki files were changed."
        )
    if status_code == 429 or RATE_LIMIT_PATTERN.search(text):
        return (
            "OpenAI rate or quota limit exceeded: the model/API refused this request due to current usage "
            "limits. Please retry later or reduce the request size."
        )
    if OUTPUT_LIMIT_PATTERN.search(text):
        return (
            "Output-token limit exceeded: the model could not fit the answer into the configured output "
            "budget. Raise MAX_OUTPUT_TOKENS or ask for a smaller answer."
        )
    return None


def make_openai_client(api_key: str | None) -> OpenAIProtocol:
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to viewer/backend/.env before chatting.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The openai package is not installed. Run pip install -r viewer/backend/requirements.txt.") from exc
    return OpenAI(api_key=api_key)


def _as_dict(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return item
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_none=True)
    if hasattr(item, "dict"):
        return item.dict(exclude_none=True)
    result: dict[str, Any] = {}
    for key in ("type", "id", "call_id", "name", "arguments", "status", "role", "content"):
        if hasattr(item, key):
            value = getattr(item, key)
            if value is not None:
                result[key] = value
    return result


def _attr(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _extract_output_text(response: Any) -> str:
    output_text = _attr(response, "output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    parts: list[str] = []
    for item in _attr(response, "output", []) or []:
        item_type = _attr(item, "type")
        if item_type != "message":
            continue
        for content in _attr(item, "content", []) or []:
            content_type = _attr(content, "type")
            if content_type in {"output_text", "text"}:
                text = _attr(content, "text", "")
                if isinstance(text, str):
                    parts.append(text)
    return "".join(parts)


def _extract_function_calls(response: Any) -> list[Any]:
    return [
        item
        for item in (_attr(response, "output", []) or [])
        if _attr(item, "type") == "function_call"
    ]


def _parse_arguments(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        parsed = json.loads(str(raw))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


class WikiChatAgent:
    def __init__(
        self,
        settings: Settings,
        toolbox: VaultToolbox | None = None,
        client: OpenAIProtocol | None = None,
        sessions: SessionStore | None = None,
    ) -> None:
        self.settings = settings
        self.toolbox = toolbox or VaultToolbox(settings)
        self.client = client
        self.sessions = sessions or SessionStore()

    def _client(self) -> OpenAIProtocol:
        if self.client is None:
            self.client = make_openai_client(self.settings.openai_api_key)
        return self.client

    def _instructions(self, session: ChatSession, *, include_preflight: bool = True) -> str:
        instructions = BASE_INSTRUCTIONS
        if include_preflight:
            instructions += (
                "\n\nThe startup preflight below has already been loaded for this web chat session:\n\n"
                + session.preflight_text
            )
        else:
            instructions += (
                "\n\nThe deterministic startup preflight has already been applied server-side for this session. "
                "Obey those retrieval and workflow rules without reloading the startup documents."
            )
        return instructions

    def _new_session(self, session_id: str) -> tuple[ChatSession, list[ChatEvent]]:
        preflight_text, events = startup_preflight(self.toolbox)
        session = ChatSession(session_id=session_id, preflight_text=preflight_text)
        self.sessions.put(session)
        return session, events

    def _get_or_create_session(self, session_id: str | None) -> tuple[ChatSession, list[ChatEvent]]:
        resolved = session_id or str(uuid.uuid4())
        session = self.sessions.get(resolved)
        if session:
            return session, []
        return self._new_session(resolved)

    async def stream_chat(self, message: str, session_id: str | None = None) -> AsyncIterator[ChatEvent]:
        session, preflight_events = self._get_or_create_session(session_id)
        for event in preflight_events:
            yield event

        clean_message = message.strip()
        if not clean_message:
            yield error("Please enter a question.")
            return

        if _is_workflow_a_or_write_request(clean_message):
            reply = (
                "This local website prototype is read-only. It can answer questions in chat, including "
                "Workflow B-style full answers, but it cannot run Workflow A or write/edit vault files."
            )
            yield trace("Read-only guard", "Blocked a Workflow A or file-writing request.")
            yield answer_done(reply)
            return

        turn_instructions = self._instructions(session)
        course_rule_parts: list[str] = []
        for path in _course_rule_paths(clean_message):
            if not self.toolbox.safe_path(path).exists():
                continue
            result = self.toolbox.read_file(path)
            yield trace("Course rule preflight", f"Loaded {path}.", path=path)
            course_rule_parts.append(
                f"<course_rule_source path=\"{path}\">\n"
                f"{result.output}\n"
                "</course_rule_source>"
            )
        if course_rule_parts:
            turn_instructions += (
                "\n\nThe following course rule documents were loaded because the user named these courses. "
                "Treat them as routing instructions, not as answer content by themselves.\n\n"
                + "\n\n".join(course_rule_parts)
            )

        course_locator_parts: list[str] = []
        for path in _course_locator_paths(self.toolbox.root, clean_message):
            result = self.toolbox.read_file(path)
            yield trace("Course locator preflight", f"Loaded {path}.", path=path)
            course_locator_parts.append(
                f"<course_locator_source path=\"{path}\">\n"
                f"{result.output}\n"
                "</course_locator_source>"
            )
        if course_locator_parts:
            turn_instructions += (
                "\n\nThe following course source locators were loaded because the user named these courses. "
                "Use them only to choose targeted source line ranges before answering; they are routing metadata, "
                "not a substitute for primary source reads.\n\n"
                + "\n\n".join(course_locator_parts)
            )

        session.input_items.append({"role": "user", "content": clean_message})
        final_text = ""
        final_synthesis_reason: str | None = None
        primary_source_reads = 0
        limit_warnings: list[str] = []
        workflow_b_requested = _is_workflow_b_request(clean_message)
        iteration_limit = self.settings.max_agent_iterations
        output_token_limit = self.settings.max_output_tokens
        primary_source_synthesis_threshold = self.settings.workflow_b_primary_source_read_synthesis_threshold
        loop_reasoning_effort = self.settings.reasoning_effort
        synthesis_reasoning_effort = self.settings.reasoning_effort

        try:
            for iteration in range(1, iteration_limit + 1):
                if final_text:
                    break
                yield trace("Thinking", f"Model pass {iteration}: deciding whether source reads are needed.")
                response = await asyncio.to_thread(
                    self._client().responses.create,
                    model=self.settings.model,
                    instructions=turn_instructions,
                    input=session.input_items,
                    tools=self.toolbox.schemas,
                    reasoning={"effort": loop_reasoning_effort},
                    max_output_tokens=output_token_limit,
                )
                incomplete_reason = _response_incomplete_reason(response)
                if incomplete_reason:
                    warning = _limit_warning_for_incomplete(incomplete_reason)
                    limit_warnings.append(warning)
                    yield trace("Limit warning", warning)

                output_items = [_as_dict(item) for item in (_attr(response, "output", []) or [])]
                if output_items:
                    session.input_items.extend(output_items)

                calls = _extract_function_calls(response)
                if calls:
                    for call in calls:
                        name = str(_attr(call, "name", ""))
                        args = _parse_arguments(_attr(call, "arguments", "{}"))
                        call_id = str(_attr(call, "call_id", _attr(call, "id", "")))
                        yield trace("Using vault tool", f"{name}({json.dumps(args, ensure_ascii=False)})")
                        result = self.toolbox.call(name, args)
                        yield result.trace
                        if (
                            workflow_b_requested
                            and name == "read_file"
                            and not result.output.startswith(("NOT FOUND:", "IS DIRECTORY:", "ACCESS DENIED:"))
                        ):
                            resolved_path = str(result.trace.get("path", args.get("path", "")))
                            if _is_primary_source_read(resolved_path):
                                primary_source_reads += 1
                        session.input_items.append(
                            {
                                "type": "function_call_output",
                                "call_id": call_id,
                                "output": result.output,
                            }
                        )
                    if (
                        workflow_b_requested
                        and primary_source_reads >= primary_source_synthesis_threshold
                    ):
                        final_synthesis_reason = (
                            f"Read {primary_source_reads} primary source ranges; "
                            "asking for a final answer from the gathered sources."
                        )
                        yield trace("Source coverage", final_synthesis_reason)
                        break
                    continue

                final_text = normalize_display_math(_extract_output_text(response).strip())
                if final_text:
                    session.input_items.append(
                        {
                            "role": "assistant",
                            "content": final_text,
                        }
                    )
                    break

            if not final_text:
                if final_synthesis_reason is None:
                    warning = (
                        f"The website reached its configured model/tool-pass limit "
                        f"({iteration_limit} passes). It will now answer from the sources already gathered. "
                        "Raise MAX_AGENT_ITERATIONS if this happens during normal use."
                    )
                    limit_warnings.append(warning)
                    yield trace("Limit warning", warning)
                yield trace(
                    "Final synthesis",
                    final_synthesis_reason
                    or "Tool pass budget reached; asking for an answer from the sources already gathered.",
                )
                synthesis_instruction = (
                    "The source coverage target for this turn has been reached. "
                    if final_synthesis_reason
                    else "You have reached the read-only tool budget for this turn. "
                )
                response = await asyncio.to_thread(
                    self._client().responses.create,
                    model=self.settings.model,
                    instructions=(
                        turn_instructions
                        + "\n\n"
                        + synthesis_instruction
                        + "Do not call more tools. Answer now using only the gathered source outputs. "
                        "If a required source is missing, say that explicitly under Steps skipped."
                    ),
                    input=session.input_items,
                    reasoning={"effort": synthesis_reasoning_effort},
                    max_output_tokens=output_token_limit,
                )
                incomplete_reason = _response_incomplete_reason(response)
                if incomplete_reason:
                    warning = _limit_warning_for_incomplete(incomplete_reason)
                    limit_warnings.append(warning)
                    yield trace("Limit warning", warning)
                output_items = [_as_dict(item) for item in (_attr(response, "output", []) or [])]
                if output_items:
                    session.input_items.extend(output_items)
                final_text = normalize_display_math(_extract_output_text(response).strip())

            if not final_text:
                final_text = (
                    "I gathered sources but could not compose a final answer. "
                    "Try narrowing the question or asking for a smaller subpart."
                )

            if _looks_like_tool_transcript(final_text):
                yield trace(
                    "Answer repair",
                    "Detected leaked tool-call transcript; asking for a clean user-visible answer.",
                )
                response = await asyncio.to_thread(
                    self._client().responses.create,
                    model=self.settings.model,
                    instructions=(
                        turn_instructions
                        + "\n\nThe previous candidate answer exposed internal tool-call syntax or process text. "
                        "Produce only the clean user-visible Markdown answer now. Do not include JSON, tool names, "
                        "function-call syntax, channel labels, XML tool tags, or process logs. If source coverage is "
                        "incomplete, say so under Steps skipped instead of trying to call tools."
                    ),
                    input=session.input_items
                    + [
                        {
                            "role": "user",
                            "content": (
                                "Rewrite the previous candidate as the final answer for the user. Remove all "
                                "internal tool-call transcript text."
                            ),
                        }
                    ],
                    reasoning={"effort": "low"},
                    max_output_tokens=output_token_limit,
                )
                incomplete_reason = _response_incomplete_reason(response)
                if incomplete_reason:
                    warning = _limit_warning_for_incomplete(incomplete_reason)
                    limit_warnings.append(warning)
                    yield trace("Limit warning", warning)
                output_items = [_as_dict(item) for item in (_attr(response, "output", []) or [])]
                if output_items:
                    session.input_items.extend(output_items)
                repaired_text = normalize_display_math(_extract_output_text(response).strip())
                if repaired_text and not _looks_like_tool_transcript(repaired_text):
                    final_text = repaired_text
                else:
                    final_text = (
                        "I gathered sources, but the model output contained internal tool-call text and could not "
                        "be safely displayed. Please retry the question in a fresh chat."
                    )

            final_text = _append_limit_warnings(final_text, limit_warnings)
            yield trace("Composing answer", "Streaming the final Markdown response to the interface.")
            for chunk in chunk_text(final_text):
                yield answer_delta(chunk)
                await asyncio.sleep(0)
            yield answer_done(final_text)
        except Exception as exc:
            friendly = _friendly_limit_error(exc)
            if friendly:
                yield trace("Limit warning", friendly)
                yield error(friendly)
            else:
                yield error(str(exc))
