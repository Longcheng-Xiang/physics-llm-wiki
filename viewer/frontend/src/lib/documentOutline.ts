export type OutlineHeading = { id: string; title: string; level: number };
type Node = { type: string; depth?: number; value?: string; alt?: string; children?: Node[];
  data?: { hProperties?: Record<string, string> } };

function label(node: Node): string {
  if (node.type === "break") return " ";
  return node.value ?? node.alt ?? node.children?.map(label).join("") ?? "";
}

// Assign anchors in the same Markdown parse that renders the document. This
// handles Setext headings and excludes heading-like text inside code/math.
export function remarkDocumentOutline() {
  return (tree: Node) => {
    const counts = new Map<string, number>();
    function visit(node: Node) {
      if (node.type === "heading") {
        const title = label(node).trim();
        const slug = title.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "") || "section";
        const count = (counts.get(slug) ?? 0) + 1;
        counts.set(slug, count);
        node.data = { ...node.data, hProperties: { ...node.data?.hProperties,
          id: `heading-${slug}${count > 1 ? `-${count}` : ""}`, "data-outline-label": title } };
      }
      node.children?.forEach(visit);
    }
    visit(tree);
  };
}

export function stripReadingFrontmatter(content: string): string {
  const match = /^---\r?\n([\s\S]*?)\r?\n(?:---|\.\.\.)[ \t]*(?:\r?\n|$)/.exec(content);
  return match && /^[\w-]+\s*:/m.test(match[1]) ? content.slice(match[0].length) : content;
}

export function readRenderedOutline(root: HTMLElement): OutlineHeading[] {
  return Array.from(root.querySelectorAll<HTMLElement>("h1,h2,h3,h4,h5,h6"))
    .filter((heading) => heading.hasAttribute("data-outline-label"))
    .map((heading) => ({ id: heading.id, title: heading.getAttribute("data-outline-label") ?? "", level: Number(heading.tagName[1]) }));
}
