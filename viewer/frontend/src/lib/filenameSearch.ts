import type { VaultFileEntry } from "./vault";

export type FilenameMatch = { file: VaultFileEntry; score: number; positions: number[] };

function compact(text: string): string {
  return text.toLowerCase().replace(/[\s_-]+/g, "");
}

// Ordered subsequence matching, like Quick Switcher: omitted letters are fine,
// but letters may not be reordered. Paths never participate in the score.
// Dynamic programming chooses the strongest match, favouring word beginnings,
// consecutive letters, early matches and shorter names. O(query × name).
export function rankFilenameMatches(files: VaultFileEntry[], query: string): FilenameMatch[] {
  const needle = Array.from(compact(query.trim()));
  if (!needle.length) return [];
  const results: FilenameMatch[] = [];
  for (const file of files) {
    const name = file.name.replace(/\.md$/i, "");
    const characters = Array.from(name);
    const text = characters.map((character) => character.toLowerCase());
    if (needle.length > text.length) continue;
    let previous = new Float64Array(text.length).fill(-Infinity);
    const parents: Int32Array[] = [];
    for (let i = 0; i < needle.length; i++) {
      const scores = new Float64Array(text.length).fill(-Infinity);
      const parent = new Int32Array(text.length).fill(-1);
      let bestPrefix = -Infinity;
      let bestIndex = -1;
      for (let j = 0; j < text.length; j++) {
        if (j > 0 && previous[j - 1] + 0.7 * (j - 1) > bestPrefix) {
          bestPrefix = previous[j - 1] + 0.7 * (j - 1);
          bestIndex = j - 1;
        }
        if (text[j] !== needle[i]) continue;
        const boundary = j === 0 || /[^\p{L}\p{N}]/u.test(characters[j - 1]) ||
          (characters[j] !== text[j] && characters[j - 1] === text[j - 1]);
        const bonus = 10 + (boundary ? 14 : 0);
        if (i === 0) {
          scores[j] = bonus - j * 0.2;
          continue;
        }
        scores[j] = bestPrefix - 0.7 * (j - 1) - 4 + bonus;
        parent[j] = bestIndex;
        if (j > 0 && previous[j - 1] + 12 + bonus > scores[j]) {
          scores[j] = previous[j - 1] + 12 + bonus;
          parent[j] = j - 1;
        }
      }
      parents.push(parent);
      previous = scores;
    }
    let end = -1;
    let score = -Infinity;
    previous.forEach((value, index) => {
      if (value > score) { score = value; end = index; }
    });
    if (end < 0) continue;
    const positions = new Array<number>(needle.length);
    for (let i = needle.length - 1; i >= 0; i--) {
      positions[i] = end;
      end = parents[i][end];
    }
    const normalizedName = compact(name);
    const normalizedQuery = needle.join("");
    score += normalizedName === normalizedQuery ? 1000 : normalizedName.startsWith(normalizedQuery) ? 150 :
      normalizedName.includes(normalizedQuery) ? 50 : 0;
    results.push({ file, score: score - characters.length * 0.04, positions });
  }
  return results.sort((a, b) => b.score - a.score || a.file.name.localeCompare(b.file.name) || a.file.path.localeCompare(b.file.path));
}
