import { FormEvent, useMemo, useRef, useState } from "react";
import { streamChat } from "../lib/chatStream";
import type { ChatMessage, ChatStreamEvent, TraceEvent } from "../types";
import { MarkdownMessage } from "./MarkdownMessage";
import { ProcessPanel } from "./ProcessPanel";

const welcome =
  "Ask a physics question against the wiki. Explicitly request “Workflow B” when you want the full source-grounded version.";

function newId(prefix: string) {
  return `${prefix}-${crypto.randomUUID()}`;
}

export function ChatView() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [processOpen, setProcessOpen] = useState(false);
  const [sessionId, setSessionId] = useState(() => newId("session"));
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const latestAssistant = useMemo(
    () => [...messages].reverse().find((message) => message.role === "assistant"),
    [messages]
  );

  function updateAssistant(
    id: string,
    updater: (message: ChatMessage) => ChatMessage,
    options: { scrollToBottom?: boolean } = {}
  ) {
    setMessages((current) => current.map((message) => (message.id === id ? updater(message) : message)));
    if (options.scrollToBottom === false) return;
    window.requestAnimationFrame(() => {
      if (typeof bottomRef.current?.scrollIntoView === "function") {
        bottomRef.current.scrollIntoView({ block: "end" });
      }
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = input.trim();
    if (!text || busy) return;

    const userMessage: ChatMessage = {
      id: newId("user"),
      role: "user",
      content: text,
      traces: []
    };
    const assistantId = newId("assistant");
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      traces: [],
      isStreaming: true
    };

    setMessages((current) => [...current, userMessage, assistantMessage]);
    setInput("");
    setBusy(true);

    try {
      await streamChat(text, sessionId, (streamEvent: ChatStreamEvent) => {
        if (streamEvent.type === "trace") {
          updateAssistant(
            assistantId,
            (message) => ({ ...message, traces: [...message.traces, streamEvent as TraceEvent] }),
            { scrollToBottom: false }
          );
        }
        if (streamEvent.type === "answer_delta") {
          updateAssistant(assistantId, (message) => ({
            ...message,
            content: message.content + streamEvent.text
          }));
        }
        if (streamEvent.type === "answer_done") {
          updateAssistant(assistantId, (message) => ({
            ...message,
            content: streamEvent.text,
            isStreaming: false
          }));
        }
        if (streamEvent.type === "error") {
          updateAssistant(
            assistantId,
            (message) => ({ ...message, error: streamEvent.message, isStreaming: false }),
            { scrollToBottom: false }
          );
        }
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown chat error";
      updateAssistant(assistantId, (current) => ({ ...current, error: message, isStreaming: false }), {
        scrollToBottom: false
      });
    } finally {
      setBusy(false);
    }
  }

  function handleNewChat() {
    setSessionId(newId("session"));
    setMessages([]);
    setInput("");
    setBusy(false);
    setProcessOpen(false);
  }

  return (
    <main className="chat-shell">
      <header className="chat-header">
        <div>
          <p className="eyebrow">Conversation workflow</p>
          <h1>Chat</h1>
        </div>
        <button className="quiet-button" type="button" onClick={handleNewChat}>
          New chat
        </button>
      </header>

      <section className="conversation" aria-live="polite">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-card">
              <p>{welcome}</p>
              <div className="sample-row">
                <button type="button" onClick={() => setInput("Workflow B: Explain gravitational redshift")}>
                  Workflow B: gravitational redshift
                </button>
                <button type="button" onClick={() => setInput("What are Hund's rules?")}>
                  Hund&apos;s rules
                </button>
              </div>
            </div>
          </div>
        ) : null}

        {messages.map((message) => (
          <article key={message.id} className={`message ${message.role}`}>
            <div className="message-card">
              {message.role === "assistant" ? (
                <ProcessPanel
                  traces={message.traces}
                  open={latestAssistant?.id === message.id ? processOpen : false}
                  onToggle={() => setProcessOpen((open) => !open)}
                />
              ) : null}
              {message.error ? <div className="error-box">{message.error}</div> : null}
              {message.content ? (
                message.isStreaming ? (
                  <div className="typing">{message.content}</div>
                ) : (
                  <MarkdownMessage content={message.content} />
                )
              ) : null}
              {message.isStreaming && !message.content ? <div className="typing">Reading the wiki...</div> : null}
            </div>
          </article>
        ))}
        <div ref={bottomRef} />
      </section>

      <form className="composer" onSubmit={handleSubmit}>
        <label htmlFor="chat-input" className="sr-only">
          Ask the physics wiki
        </label>
        <textarea
          id="chat-input"
          value={input}
          placeholder="Ask the wiki..."
          rows={1}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
        />
        <button type="submit" disabled={busy || !input.trim()}>
          {busy ? "Thinking" : "Send"}
        </button>
      </form>
    </main>
  );
}
