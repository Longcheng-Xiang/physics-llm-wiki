import { describe, expect, it } from "vitest";
import { resolveVaultPath, viewerAssetUrl } from "./vault";

describe("vault path helpers", () => {
  it("resolves paths relative to the open Markdown file", () => {
    expect(resolveVaultPath("answers/2026/answer.md", "../assets/plot.svg")).toBe(
      "answers/assets/plot.svg"
    );
  });

  it("rejects remote and escaping paths", () => {
    expect(resolveVaultPath("answer.md", "https://example.com/plot.svg")).toBeNull();
    expect(resolveVaultPath("answer.md", "../outside.svg")).toBeNull();
  });

  it("creates a cache-busted asset URL", () => {
    expect(viewerAssetUrl("answer assets/plot.svg", 7)).toBe(
      "/api/vault/asset?path=answer%20assets%2Fplot.svg&v=7"
    );
  });
});
