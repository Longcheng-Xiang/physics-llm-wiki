import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { VaultReader } from "./VaultReader";

class MockEventSource {
  static latest: MockEventSource | null = null;
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  listeners = new Map<string, Array<(event: MessageEvent<string>) => void>>();

  constructor(_url: string) {
    MockEventSource.latest = this;
  }

  addEventListener(type: string, listener: EventListener) {
    const listeners = this.listeners.get(type) ?? [];
    listeners.push(listener as (event: MessageEvent<string>) => void);
    this.listeners.set(type, listeners);
  }

  emit(type: string, data = "{}") {
    for (const listener of this.listeners.get(type) ?? []) {
      listener(new MessageEvent(type, { data }));
    }
  }

  close() {}
}

describe("VaultReader", () => {
  let content: string;
  let entries: Array<{ path: string; name: string; modifiedNs: number }>;

  beforeEach(() => {
    content = "# First version\n\nBody";
    entries = [{ path: "index.md", name: "index.md", modifiedNs: 1 }];
    MockEventSource.latest = null;
    vi.stubGlobal("EventSource", MockEventSource);
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/vault/files") {
        return new Response(
          JSON.stringify({ files: entries }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      if (url.startsWith("/api/vault/file?")) {
        return new Response(
          JSON.stringify({ path: "index.md", name: "index.md", content, modifiedNs: Date.now() }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      throw new Error(`Unexpected request: ${url}`);
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("navigates filename-only fuzzy suggestions with arrows and Enter, then clears with Escape", async () => {
    entries = [
      { path: "notes/Daily notes.md", name: "Daily notes.md", modifiedNs: 1 },
      { path: "notes/Distant notebook.md", name: "Distant notebook.md", modifiedNs: 1 },
      { path: "dn/Unrelated.md", name: "Unrelated.md", modifiedNs: 1 }
    ];
    render(<VaultReader />);
    await screen.findByRole("button", { name: "Daily notes" });
    await userEvent.click(screen.getByRole("button", { name: "Find filename…" }));
    const input = screen.getByRole("searchbox", { name: "Filter Markdown files" });
    await userEvent.type(input, "dn");
    expect(screen.getAllByRole("option")).toHaveLength(2);
    expect(screen.getByRole("option", { name: "Daily notes" })).toHaveAttribute("aria-selected", "true");
    await userEvent.keyboard("{ArrowDown}");
    expect(screen.getByRole("option", { name: "Distant notebook" })).toHaveAttribute("aria-selected", "true");
    await userEvent.keyboard("{Enter}");
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(
      "/api/vault/file?path=notes%2FDistant%20notebook.md", expect.anything()
    ));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Find filename…" }));
    await userEvent.type(input, "dn");
    await userEvent.keyboard("{Escape}");
    expect(input).toHaveValue("");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("keeps the rendered version on screen until a refreshed version finishes typesetting", async () => {
    const typesets: Array<() => void> = [];
    vi.stubGlobal("MathJax", {
      typesetPromise: vi.fn(() => new Promise<void>((resolve) => typesets.push(resolve))),
      typesetClear: vi.fn()
    });
    render(<VaultReader />);
    await userEvent.click(await screen.findByRole("button", { name: "index" }));

    await waitFor(() => expect(typesets).toHaveLength(1));
    expect(screen.queryByRole("heading", { name: "First version" })).not.toBeInTheDocument();
    await act(async () => typesets[0]());
    expect(await screen.findByRole("heading", { name: "First version" })).toBeInTheDocument();
    expect(typesets).toHaveLength(1);

    content = "# Second version\n\nUpdated body";
    act(() => {
      MockEventSource.latest?.emit(
        "vault_change",
        JSON.stringify({ type: "vault_change", path: "index.md", kind: "markdown", change: "modified" })
      );
    });

    await waitFor(() => expect(typesets).toHaveLength(2));
    expect(screen.getByRole("heading", { name: "First version" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Second version" })).not.toBeInTheDocument();
    await act(async () => typesets[1]());
    expect(await screen.findByRole("heading", { name: "Second version" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "First version" })).not.toBeInTheDocument();
  });

  it("starts without an open document, then refreshes a selected file without losing scroll", async () => {
    const { container } = render(<VaultReader />);
    const fileButton = await screen.findByRole("button", { name: "index" });
    expect(screen.queryByRole("heading", { name: "First version" })).not.toBeInTheDocument();
    expect(screen.getByRole("complementary", { name: "Outline panel" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Document outline" }).textContent).toBe("");
    expect(screen.getAllByRole("separator")).toHaveLength(2);
    act(() => MockEventSource.latest?.emit("ready"));
    expect(screen.queryByText("Live")).not.toBeInTheDocument();

    await userEvent.click(fileButton);
    expect(await screen.findByRole("heading", { name: "First version" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "First version" })).toBeInTheDocument();
    const reader = container.querySelector(".reader-scroll") as HTMLDivElement;
    reader.scrollTop = 240;
    content = "# Second version\n\nUpdated body";

    act(() => {
      MockEventSource.latest?.emit(
        "vault_change",
        JSON.stringify({
          type: "vault_change",
          path: "index.md",
          kind: "markdown",
          change: "modified"
        })
      );
    });

    expect(await screen.findByRole("heading", { name: "Second version" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Second version" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "First version" })).not.toBeInTheDocument();
    await waitFor(() => expect(reader.scrollTop).toBe(240));
    expect(screen.queryByText("Updated")).not.toBeInTheDocument();
  });

  it("coalesces simultaneous Markdown and asset changes without dropping either refresh", async () => {
    content = "# First version\n\n![Diagram](assets/plot.svg)";
    render(<VaultReader />);
    await userEvent.click(await screen.findByRole("button", { name: "index" }));
    expect(await screen.findByRole("heading", { name: "First version" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Diagram" })).toHaveAttribute(
      "src",
      "/api/vault/asset?path=assets%2Fplot.svg&v=0"
    );

    content = "# Batched refresh\n\n![Diagram](assets/plot.svg)";
    act(() => {
      MockEventSource.latest?.emit(
        "vault_change",
        JSON.stringify({
          type: "vault_change",
          path: "assets/plot.svg",
          kind: "asset",
          change: "modified"
        })
      );
      MockEventSource.latest?.emit(
        "vault_change",
        JSON.stringify({
          type: "vault_change",
          path: "index.md",
          kind: "markdown",
          change: "modified"
        })
      );
    });

    expect(await screen.findByRole("heading", { name: "Batched refresh" })).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByRole("img", { name: "Diagram" }).getAttribute("src")).not.toMatch(/&v=0$/)
    );
  });
});
