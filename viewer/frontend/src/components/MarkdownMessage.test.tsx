import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarkdownMessage } from "./MarkdownMessage";

describe("MarkdownMessage", () => {
  it("renders Markdown text and preserves fenced code content", () => {
    render(<MarkdownMessage content={"A line with `code`.\n\n```tex\n$not rendered$\n```"} />);

    expect(screen.getByText(/A line with/)).toBeInTheDocument();
    expect(screen.getByText("$not rendered$")).toBeInTheDocument();
  });

  it("passes math through MathJax rendering", () => {
    const { container } = render(<MarkdownMessage content={"Inline $E=mc^2$.\n\n$$\nx=y\n$$"} />);

    expect(container.textContent).toContain("\\(E=mc^2\\)");
    expect(container.textContent).toContain("x=y");
  });

  it("anchors real headings uniquely, ignores fenced examples and hides YAML metadata", () => {
    const { container } = render(<MarkdownMessage currentPath="outline.md" content={
      "---\ncourse: B3\n---\n# Example\n\n## Question $E$\n\n## Question $E$\n\nSetext\n---\n\n```md\n# Fake heading\n```"
    } />);
    const headings = Array.from(container.querySelectorAll("h1,h2"));
    expect(headings.map((heading) => heading.id)).toEqual([
      "heading-example", "heading-question-e", "heading-question-e-2", "heading-setext"
    ]);
    expect(headings[1]).toHaveAttribute("data-outline-label", "Question E");
    expect(container.textContent).not.toContain("course: B3");
    expect(container.querySelector("pre")?.textContent).toContain("# Fake heading");
  });

  it("preserves reading-view newlines without inserting breaks inside TeX or code", () => {
    const { container } = render(<MarkdownMessage
      currentPath="notes/example.md"
      content={"First line with $T$.\nSecond line.\n\n> Quoted first line\n> Quoted second line\n\n$$\n\\begin{aligned}a&=b\\\\\nc&=d\\end{aligned}\n$$\n\n```text\nfirst code line\nsecond code line\n```"}
    />);

    expect(container.querySelectorAll("p br")).toHaveLength(2);
    expect(container.querySelector("pre br")).toBeNull();
    expect(container.querySelector("pre")?.textContent).toBe("first code line\nsecond code line\n");
    expect(container.textContent).toContain("c&=d\\end{aligned}");
    expect(container.querySelectorAll("br")).toHaveLength(2);
  });

  it("treats Obsidian one-line double-dollar math as display math", () => {
    const { container } = render(<MarkdownMessage content={"$$E=mc^2$$"} />);

    expect(container.textContent).toContain("\\[E=mc^2\\]");
    expect(container.textContent).not.toContain("\\(E=mc^2\\)");
  });

  it("renders GitHub-flavored Markdown tables", () => {
    render(<MarkdownMessage content={"| State | Energy |\n|---|---:|\n| ground | $E_0$ |"} />);

    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Energy" })).toBeInTheDocument();
  });

  it("routes standard Markdown images through the read-only vault asset endpoint", () => {
    render(
      <MarkdownMessage
        content={"![Band diagram](assets/bands.svg)"}
        currentPath="answers/example.md"
        assetVersion={42}
      />
    );

    const image = screen.getByRole("img", { name: "Band diagram" });
    expect(image).toHaveAttribute(
      "src",
      "/api/vault/asset?path=answers%2Fassets%2Fbands.svg&v=42"
    );
  });

  it("leaves Obsidian wiki-link syntax unimplemented", () => {
    render(<MarkdownMessage content={"Read [[Other Note]] and ![[diagram.svg]]."} currentPath="answer.md" />);

    expect(screen.getByText(/\[\[Other Note\]\]/)).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });
});
