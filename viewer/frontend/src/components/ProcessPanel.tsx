import type { TraceEvent } from "../types";

type Props = {
  traces: TraceEvent[];
  open: boolean;
  onToggle: () => void;
};

function formatPath(trace: TraceEvent): string | null {
  if (!trace.path) return null;
  if (!trace.lineRange) return trace.path;
  return `${trace.path}:${trace.lineRange[0]}-${trace.lineRange[1]}`;
}

export function ProcessPanel({ traces, open, onToggle }: Props) {
  if (traces.length === 0) return null;

  return (
    <section className="process-panel">
      <button className="process-toggle" type="button" onClick={onToggle} aria-expanded={open}>
        <span>Process</span>
        <span className="process-count">{traces.length}</span>
      </button>
      {open ? (
        <ol className="process-list">
          {traces.map((trace, index) => {
            const path = formatPath(trace);
            return (
              <li key={`${trace.title}-${index}`}>
                <div className="process-title">{trace.title}</div>
                {trace.detail ? <div className="process-detail">{trace.detail}</div> : null}
                {path ? <div className="process-path">{path}</div> : null}
              </li>
            );
          })}
        </ol>
      ) : null}
    </section>
  );
}

