import type { ChatStreamEvent } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

function emitPackets(chunk: string, onEvent: (event: ChatStreamEvent) => void): boolean {
  let reachedTerminalEvent = false;
  const packets = chunk.split("\n\n");
  for (const packet of packets) {
    const dataLines = packet
      .split("\n")
      .filter((line) => line.startsWith("data: "));
    if (dataLines.length === 0) continue;
    const raw = dataLines.map((line) => line.slice("data: ".length)).join("\n");
    const event = JSON.parse(raw) as ChatStreamEvent;
    onEvent(event);
    if (event.type === "answer_done" || event.type === "error") {
      reachedTerminalEvent = true;
    }
  }
  return reachedTerminalEvent;
}

const endedEarlyMessage =
  "The chat stream ended before the backend sent a final answer or error. The Codex CLI process may have exited early; check the Process panel for the last completed step and try the question again.";

export async function streamChat(
  message: string,
  sessionId: string,
  onEvent: (event: ChatStreamEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, sessionId })
  });

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let shouldStop = false;

  while (!shouldStop) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
    const packets = buffer.split("\n\n");
    buffer = packets.pop() ?? "";
    shouldStop = emitPackets(packets.join("\n\n"), onEvent);
  }

  const trailing = buffer.trim();
  if (!shouldStop && trailing.startsWith("data: ")) {
    shouldStop = emitPackets(trailing, onEvent);
  }

  if (shouldStop) {
    await reader.cancel().catch(() => undefined);
    return;
  }

  throw new Error(endedEarlyMessage);
}
