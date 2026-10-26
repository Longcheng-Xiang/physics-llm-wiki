import { useEffect, useRef } from "react";
import type { FilenameMatch } from "../lib/filenameSearch";

type Props = {
  matches: FilenameMatch[];
  activeIndex: number;
  query: string;
  onSelect: (path: string) => void;
};

export function FilenameResults({ matches, activeIndex, query, onSelect }: Props) {
  const rootRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    rootRef.current?.querySelector('[aria-selected="true"]')?.scrollIntoView?.({ block: "nearest" });
  }, [activeIndex, matches]);

  return (
    <div ref={rootRef} className="filename-results" id="filename-search-results" role="listbox" aria-label="Matching filenames">
      {matches.map((match, index) => {
        const name = match.file.name.replace(/\.md$/i, "");
        const directory = match.file.path.slice(0, match.file.path.lastIndexOf("/") + 1);
        const positions = new Set(match.positions);
        return (
          <button key={match.file.path} type="button" role="option" id={`file-result-${index}`}
            className="filename-result" aria-label={name} aria-selected={index === activeIndex}
            title={match.file.path} onClick={() => onSelect(match.file.path)}>
            <span className="filename-result-directory">{directory}</span><span>{Array.from(name).map((character, position) =>
              positions.has(position) ? <mark key={position}>{character}</mark> : character
            )}</span>
          </button>
        );
      })}
      {!matches.length ? <p className="filename-results-empty">{query.trim() ? "No filenames match." : "Type a filename to search."}</p> : null}
    </div>
  );
}
