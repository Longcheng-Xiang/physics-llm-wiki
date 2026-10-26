import { describe, expect, it } from "vitest";
import { fitPanelWidths } from "./panelWidths";

describe("persistent side panel geometry", () => {
  it("keeps both panels present at their minimum even after extreme dragging", () => {
    expect(fitPanelWidths({ left: -1000, right: -1000 }, 1280)).toEqual({ left: 160, right: 160 });
  });
  it("respects maximum widths and leaves room for the reader when the window shrinks", () => {
    expect(fitPanelWidths({ left: 1000, right: 1000 }, 1280)).toEqual({ left: 420, right: 380 });
    const widths = fitPanelWidths({ left: 420, right: 380 }, 800);
    expect(widths.left).toBeGreaterThanOrEqual(160);
    expect(widths.right).toBeGreaterThanOrEqual(160);
    expect(widths.left + widths.right).toBeLessThanOrEqual(520);
  });
});
