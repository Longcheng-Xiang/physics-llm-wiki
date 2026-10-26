// Ordinary inline CHTML stays in the text's line box. Only an expression wider
// than its paragraph gets a local scrolling box; recheck when the reader resizes.
export function observeReadingMath(root: HTMLElement): () => void {
  let frame = 0;
  let width = root.getBoundingClientRect().width;

  function fit() {
    const expressions = Array.from(root.querySelectorAll<HTMLElement>('mjx-container:not([display="true"])'));
    expressions.forEach((expression) => expression.classList.remove("wide-inline-math"));
    const wide = expressions.filter((expression) => {
      const paragraph = expression.closest("p, li, td, th") ?? root;
      const math = expression.querySelector("mjx-math");
      return math && paragraph.clientWidth > 0 && math.getBoundingClientRect().width > paragraph.clientWidth;
    });
    wide.forEach((expression) => expression.classList.add("wide-inline-math"));
  }

  fit();
  const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(() => {
    const nextWidth = root.getBoundingClientRect().width;
    if (nextWidth === width) return;
    width = nextWidth;
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(fit);
  });
  observer?.observe(root);
  return () => {
    observer?.disconnect();
    cancelAnimationFrame(frame);
  };
}
