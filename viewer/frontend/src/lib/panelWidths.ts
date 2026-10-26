export type PanelWidths = { left: number; right: number };
export const PANEL_MIN = 160;
export const PANEL_MAX = { left: 420, right: 380 };
export const READER_MIN = 280;
// Resize handles overlay the boundary; they consume no layout space.
export const SPLITTER_WIDTH = 0;

export function fitPanelWidths(preferred: PanelWidths, totalWidth: number): PanelWidths {
  const left = Math.max(PANEL_MIN, Math.min(PANEL_MAX.left, preferred.left));
  const right = Math.max(PANEL_MIN, Math.min(PANEL_MAX.right, preferred.right));
  const budget = Math.max(PANEL_MIN * 2, totalWidth - READER_MIN - SPLITTER_WIDTH * 2);
  if (left + right <= budget) return { left, right };
  const extra = left + right - PANEL_MIN * 2;
  const available = budget - PANEL_MIN * 2;
  return { left: PANEL_MIN + (left - PANEL_MIN) * available / extra,
    right: PANEL_MIN + (right - PANEL_MIN) * available / extra };
}
