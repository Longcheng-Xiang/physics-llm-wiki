import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProcessPanel } from "./ProcessPanel";

describe("ProcessPanel", () => {
  it("shows trace details and source ranges when open", () => {
    render(
      <ProcessPanel
        open
        onToggle={() => undefined}
        traces={[
          {
            type: "trace",
            title: "Reading source",
            detail: "Read 2 lines.",
            path: "index.md",
            lineRange: [1, 2]
          }
        ]}
      />
    );

    expect(screen.getByText("Reading source")).toBeInTheDocument();
    expect(screen.getByText("index.md:1-2")).toBeInTheDocument();
  });

  it("calls onToggle from the header button", async () => {
    const onToggle = vi.fn();
    render(
      <ProcessPanel
        open={false}
        onToggle={onToggle}
        traces={[{ type: "trace", title: "Thinking", detail: "Model pass 1" }]}
      />
    );

    await userEvent.click(screen.getByRole("button", { name: /process/i }));

    expect(onToggle).toHaveBeenCalledTimes(1);
  });
});

