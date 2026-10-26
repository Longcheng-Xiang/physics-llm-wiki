import { useEffect, useRef, useState, type ReactNode } from "react";
import { fitPanelWidths, PANEL_MAX, PANEL_MIN, READER_MIN, SPLITTER_WIDTH, type PanelWidths } from "../lib/panelWidths";

export function ResizableWorkspace({ left, right, children }: { left: ReactNode; right: ReactNode; children: ReactNode }) {
  const rootRef = useRef<HTMLElement>(null);
  const dragRef = useRef<{ side: keyof PanelWidths; x: number; width: number } | null>(null);
  const [preferred, setPreferred] = useState<PanelWidths>({ left: 240, right: 220 });
  const [totalWidth, setTotalWidth] = useState(window.innerWidth);
  const [dragging, setDragging] = useState(false);
  const widths = fitPanelWidths(preferred, totalWidth);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    const measure = () => { if (root.clientWidth) setTotalWidth(root.clientWidth); };
    measure();
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(measure);
    observer?.observe(root);
    return () => observer?.disconnect();
  }, []);

  function maximum(side: keyof PanelWidths) {
    return Math.max(PANEL_MIN, Math.min(PANEL_MAX[side], totalWidth - READER_MIN - SPLITTER_WIDTH * 2 - widths[side === "left" ? "right" : "left"]));
  }
  function change(side: keyof PanelWidths, value: number) {
    const clamped = Math.max(PANEL_MIN, Math.min(maximum(side), value));
    setPreferred({ ...widths, [side]: clamped });
  }
  function splitter(side: keyof PanelWidths) {
    return <div role="separator" tabIndex={0} aria-orientation="vertical"
      aria-label={side === "left" ? "Resize file panel" : "Resize outline panel"}
      aria-valuemin={PANEL_MIN} aria-valuemax={Math.round(maximum(side))} aria-valuenow={Math.round(widths[side])}
      className="panel-splitter" title="Drag to resize. Arrow keys also resize."
      onPointerDown={(event) => {
        if (event.button !== 0) return;
        event.preventDefault();
        event.currentTarget.setPointerCapture?.(event.pointerId);
        dragRef.current = { side, x: event.clientX, width: widths[side] };
        setDragging(true);
      }}
      onPointerMove={(event) => {
        const drag = dragRef.current;
        if (drag?.side === side) change(side, drag.width + (event.clientX - drag.x) * (side === "left" ? 1 : -1));
      }}
      onPointerUp={() => { dragRef.current = null; setDragging(false); }}
      onPointerCancel={() => { dragRef.current = null; setDragging(false); }}
      onLostPointerCapture={() => { dragRef.current = null; setDragging(false); }}
      onKeyDown={(event) => {
        if (event.key === "Home" || event.key === "End") {
          event.preventDefault(); change(side, event.key === "Home" ? PANEL_MIN : maximum(side));
        } else if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
          event.preventDefault();
          change(side, widths[side] + (event.key === "ArrowRight" ? 16 : -16) * (side === "left" ? 1 : -1));
        }
      }} />;
  }

  return <main ref={rootRef} className={`reader-shell${dragging ? " panels-resizing" : ""}`}
    style={{ gridTemplateColumns: `${widths.left}px ${SPLITTER_WIDTH}px minmax(${READER_MIN}px, 1fr) ${SPLITTER_WIDTH}px ${widths.right}px` }}>
    {left}{splitter("left")}{children}{splitter("right")}{right}
  </main>;
}
