import { describe, expect, it } from "vitest";
import { normalizeObsidianDisplayMath } from "./markdownMath";

describe("normalizeObsidianDisplayMath", () => {
  it("promotes Obsidian one-line display math without changing inline math", () => {
    expect(normalizeObsidianDisplayMath("Inline $E=mc^2$.\n\n$$x=y$$")).toBe(
      "Inline $E=mc^2$.\n\n$$\nx=y\n$$"
    );
  });

  it("normalizes content beside opening and closing display delimiters", () => {
    const markdown = "$$r(E)\\,dE = A\n+ B$$\n\n$$=C$$";
    expect(normalizeObsidianDisplayMath(markdown)).toBe(
      "$$\nr(E)\\,dE = A\n+ B\n$$\n\n$$\n=C\n$$"
    );
  });

  it("preserves canonical multiline display math", () => {
    const markdown = "$$\n\\boxed{x=y}\n$$";
    expect(normalizeObsidianDisplayMath(markdown)).toBe(markdown);
  });

  it("preserves fenced and indented code", () => {
    const markdown = "```md\n$$x=y$$\n```\n\n    $$z=w$$";
    expect(normalizeObsidianDisplayMath(markdown)).toBe(markdown);
  });

  it("normalizes display math inside a blockquote", () => {
    expect(normalizeObsidianDisplayMath("> $$x=y$$")).toBe("> $$\n> x=y\n> $$");
  });

  it("preserves CRLF line endings", () => {
    expect(normalizeObsidianDisplayMath("before\r\n$$x=y$$\r\nafter")).toBe(
      "before\r\n$$\r\nx=y\r\n$$\r\nafter"
    );
  });
});
