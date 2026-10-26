import { describe, expect, it } from "vitest";
import { rankFilenameMatches } from "./filenameSearch";

const files = (...names: string[]) => names.map((name) => ({ name: `${name}.md`, path: `folder/${name}.md`, modifiedNs: 1 }));

describe("filename fuzzy search", () => {
  it("matches ordered abbreviations and highlights the matched filename characters", () => {
    const [match] = rankFilenameMatches(files("Daily notes"), "dn");
    expect(match.file.name).toBe("Daily notes.md");
    expect(match.positions).toEqual([0, 6]);
    expect(rankFilenameMatches(files("Daily notes"), "nd")).toEqual([]);
  });

  it("searches only the basename, not parent folders or the Markdown extension", () => {
    const entry = { name: "Index.md", path: "thermodynamics/Index.md", modifiedNs: 1 };
    expect(rankFilenameMatches([entry], "thermodynamics")).toEqual([]);
    expect(rankFilenameMatches([entry], "md")).toEqual([]);
    expect(rankFilenameMatches([entry], "inx")).toHaveLength(1);
  });

  it("handles capitalization and spaces across underscore-separated names", () => {
    expect(rankFilenameMatches(files("B5_Final_2025_Paper_Questions_and_Answers"), "b5 2025 qa")).toHaveLength(1);
    expect(rankFilenameMatches(files("Daily_notes"), "DAILY NOTES")).toHaveLength(1);
  });

  it("ranks exact, prefix and contiguous matches above scattered matches", () => {
    const matches = rankFilenameMatches(files("Distant notebook", "My daily notes", "Daily notes archive", "Daily notes"), "daily notes");
    expect(matches.map((match) => match.file.name)).toEqual([
      "Daily notes.md", "Daily notes archive.md", "My daily notes.md"
    ]);
  });

  it("favours word initials over scattered letters and finds the best repeated-letter match", () => {
    expect(rankFilenameMatches(files("Underlying things", "Daily notes"), "dn")[0].file.name).toBe("Daily notes.md");
    expect(rankFilenameMatches(files("ax bx abc"), "abc")[0].positions).toEqual([6, 7, 8]);
  });
});
