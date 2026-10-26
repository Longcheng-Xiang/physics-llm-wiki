import { memo, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import rehypeMathjax from "rehype-mathjax/browser";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import { queueMathJaxClear, queueMathJaxTypeset } from "../lib/mathJax";
import { normalizeObsidianDisplayMath } from "../lib/markdownMath";
import { remarkReadingBreaks } from "../lib/remarkReadingBreaks";
import { observeReadingMath } from "../lib/readingMathLayout";
import { readRenderedOutline, remarkDocumentOutline, stripReadingFrontmatter, type OutlineHeading } from "../lib/documentOutline";
import { resolveVaultPath, viewerAssetUrl } from "../lib/vault";

type Props = {
  content: string;
  currentPath?: string;
  assetVersion?: number;
  onNavigate?: (path: string) => void;
  // Called once the math is typeset and its images and fonts are ready.
  onRendered?: (headings: OutlineHeading[]) => void;
};

// Memoized so that a parent re-render never re-parses the Markdown or touches
// DOM that MathJax has already replaced.
export const MarkdownMessage = memo(function MarkdownMessage({
  content,
  currentPath,
  assetVersion = 0,
  onNavigate,
  onRendered
}: Props) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const normalizedContent = normalizeObsidianDisplayMath(currentPath ? stripReadingFrontmatter(content) : content);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    let cancelled = false;
    let stopObservingMath: (() => void) | undefined;
    void queueMathJaxTypeset(root, () => cancelled)
      .catch(() => undefined)
      .then(() => waitForImagesAndFonts(root))
      .finally(() => {
        if (!cancelled) {
          if (currentPath) stopObservingMath = observeReadingMath(root);
          onRendered?.(readRenderedOutline(root));
        }
      });

    return () => {
      cancelled = true;
      stopObservingMath?.();
      queueMathJaxClear(root);
    };
  }, [content, currentPath, onRendered]);

  return (
    <div ref={rootRef}>
      <ReactMarkdown
        remarkPlugins={currentPath ? [remarkMath, remarkGfm, remarkReadingBreaks, remarkDocumentOutline] : [remarkMath, remarkGfm]}
        rehypePlugins={[rehypeMathjax]}
        components={{
          code(props) {
            const { children, className, ...rest } = props;
            const isInline = !String(className ?? "").includes("language-");
            if (isInline) {
              return (
                <code className="inline-code" {...rest}>
                  {children}
                </code>
              );
            }
            return (
              <code className={className} {...rest}>
                {children}
              </code>
            );
          },
          a(props) {
            const href = String(props.href ?? "");
            const resolved = currentPath ? resolveVaultPath(currentPath, href) : null;
            if (resolved?.toLowerCase().endsWith(".md") && onNavigate) {
              return (
                <a
                  {...props}
                  href={`#${resolved}`}
                  onClick={(event) => {
                    event.preventDefault();
                    onNavigate(resolved);
                  }}
                />
              );
            }
            return <a {...props} target="_blank" rel="noreferrer" />;
          },
          img(props) {
            const src = String(props.src ?? "");
            const resolved = currentPath ? resolveVaultPath(currentPath, src) : null;
            if (!resolved) return <span className="image-unavailable">[Image unavailable: {props.alt || src}]</span>;
            // Loaded eagerly: a refreshed document waits for its images before it
            // is shown, and lazy images in a hidden layer would never load.
            return <img {...props} src={viewerAssetUrl(resolved, assetVersion)} />;
          }
        }}
      >
        {normalizedContent}
      </ReactMarkdown>
    </div>
  );
});

function waitForImagesAndFonts(root: HTMLElement): Promise<unknown> {
  const images = Array.from(root.querySelectorAll("img"), (image) =>
    typeof image.decode === "function" ? image.decode().catch(() => undefined) : undefined
  );
  // MathJax fonts load when first used; wait so a new glyph never flashes in a fallback font.
  return Promise.all([...images, document.fonts?.ready]);
}
