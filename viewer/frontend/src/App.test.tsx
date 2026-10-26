import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ChatView } from "./components/ChatView";

const encoder = new TextEncoder();

function makeStream(chunks: string[]) {
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk));
      }
      controller.close();
    }
  });
}

describe("ChatView", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("submits a question and renders streamed trace and answer", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        makeStream([
          'data: {"type":"trace","title":"Startup preflight","detail":"Loaded AGENTS.md.","path":"AGENTS.md"}\n\n',
          'data: {"type":"answer_delta","text":"Answer with $E=mc^2$."}\n\n',
          'data: {"type":"answer_done","text":"Answer with $E=mc^2$."}\n\n'
        ]),
        { status: 200, headers: { "Content-Type": "text/event-stream" } }
      )
    );

    render(<ChatView />);
    await userEvent.type(screen.getByLabelText(/ask the physics wiki/i), "Explain energy");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByRole("button", { name: /process/i })).toBeInTheDocument();
    expect(await screen.findByText(/Answer with/)).toBeInTheDocument();
  });

  it("does not force page scroll when only process traces stream in", async () => {
    const scrollIntoView = vi.fn();
    Element.prototype.scrollIntoView = scrollIntoView;
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        makeStream([
          'data: {"type":"trace","title":"Codex command","detail":"read source 1"}\n\n',
          'data: {"type":"trace","title":"Codex command","detail":"read source 2"}\n\n'
        ]),
        { status: 200, headers: { "Content-Type": "text/event-stream" } }
      )
    );

    render(<ChatView />);
    await userEvent.type(screen.getByLabelText(/ask the physics wiki/i), "Explain energy");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByRole("button", { name: /process/i })).toBeInTheDocument();
    expect(await screen.findByText("2")).toBeInTheDocument();
    expect(scrollIntoView).not.toHaveBeenCalled();
  });

  it("shows a clear error when the server stream ends before a final answer", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        makeStream([
          'data: {"type":"trace","title":"Codex command","detail":"read source"}\n\n',
          'data: {"type":"answer_delta","text":"Partial answer"}\n\n'
        ]),
        { status: 200, headers: { "Content-Type": "text/event-stream" } }
      )
    );

    render(<ChatView />);
    await userEvent.type(screen.getByLabelText(/ask the physics wiki/i), "Explain energy");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText(/Partial answer/)).toBeInTheDocument();
    expect(await screen.findByText(/chat stream ended before the backend sent a final answer/i)).toBeInTheDocument();
  });
});
