import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

vi.mock("./components/VaultReader", () => ({ VaultReader: () => null }));
vi.mock("./components/ChatView", () => ({ ChatView: () => null }));

describe("native window theme bridges", () => {
  beforeEach(() => {
    window.localStorage.setItem("physics-wiki:theme", "light");
    vi.stubGlobal("chrome", undefined);
    vi.stubGlobal("webkit", undefined);
  });
  afterEach(() => { vi.unstubAllGlobals(); window.localStorage.clear(); });

  it("notifies Windows and Mac native hosts when the theme changes", async () => {
    const windows = vi.fn();
    const mac = vi.fn();
    vi.stubGlobal("chrome", { webview: { postMessage: windows } });
    vi.stubGlobal("webkit", { messageHandlers: { appearance: { postMessage: mac } } });
    render(<App />);
    expect(windows).toHaveBeenLastCalledWith({ type: "appearance", theme: "light" });
    expect(mac).toHaveBeenLastCalledWith("light");
    await userEvent.click(screen.getByRole("button", { name: "Use dark mode" }));
    expect(windows).toHaveBeenLastCalledWith({ type: "appearance", theme: "dark" });
    expect(mac).toHaveBeenLastCalledWith("dark");
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("still switches theme in an ordinary browser without native hosts", async () => {
    render(<App />);
    await userEvent.click(screen.getByRole("button", { name: "Use dark mode" }));
    expect(window.localStorage.getItem("physics-wiki:theme")).toBe("dark");
  });
});
