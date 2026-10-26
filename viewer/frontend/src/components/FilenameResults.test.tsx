import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { rankFilenameMatches } from "../lib/filenameSearch";
import { FilenameResults } from "./FilenameResults";

describe("complete search results", () => {
  it("shows the entire directory and filename and opens the exact path on click", async () => {
    const name = "B3_Final_2025_Paper_Questions_and_Answers.md";
    const path = `questions_and_answers/exam_questions/B3/B3_2025/${name}`;
    const matches = rankFilenameMatches([{ name, path, modifiedNs: 1 }], "b3 questions and");
    const onSelect = vi.fn();
    render(<FilenameResults matches={matches} activeIndex={0} query="b3 questions and" onSelect={onSelect} />);
    const option = screen.getByRole("option", { name: name.slice(0, -3) });
    expect(option.textContent).toBe(path.slice(0, -3));
    expect(option).toHaveAttribute("aria-selected", "true");
    expect(option.querySelector("mark")).not.toBeNull();
    await userEvent.click(option);
    expect(onSelect).toHaveBeenCalledWith(path);
  });
});
