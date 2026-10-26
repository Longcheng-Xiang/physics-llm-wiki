type Node = { type: string; value?: string; children?: Node[] };

// Preserve an author's single newlines in reading view. Work on parsed prose
// so that newlines inside code and TeX remain part of those expressions.
export function remarkReadingBreaks() {
  return (tree: Node) => {
    function visit(node: Node) {
      if (!node.children) return;
      node.children = node.children.flatMap((child) => {
        if (child.type !== "text" || !child.value?.includes("\n")) {
          visit(child);
          return [child];
        }
        return child.value.split(/\r?\n/).flatMap((value, index): Node[] =>
          index === 0 ? [{ type: "text", value }] : [{ type: "break" }, { type: "text", value }]
        );
      });
    }
    visit(tree);
  };
}
