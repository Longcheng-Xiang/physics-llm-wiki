import { useEffect, useRef, useState, type RefObject } from "react";
import type { OutlineHeading } from "../lib/documentOutline";

type Branch = OutlineHeading & { children: Branch[] };
function hierarchy(headings: OutlineHeading[]): Branch[] {
  const roots: Branch[] = [];
  const stack: Branch[] = [];
  for (const heading of headings) {
    const branch = { ...heading, children: [] };
    while (stack.length && stack[stack.length - 1].level >= heading.level) stack.pop();
    (stack.length ? stack[stack.length - 1].children : roots).push(branch);
    stack.push(branch);
  }
  return roots;
}

export function DocumentOutline({ headings, readerRef, documentPath }: {
  headings: OutlineHeading[]; readerRef: RefObject<HTMLDivElement | null>; documentPath: string | null;
}) {
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());
  const [active, setActive] = useState("");
  const outlineRef = useRef<HTMLElement>(null);
  useEffect(() => { setCollapsed(new Set()); }, [documentPath]);
  useEffect(() => {
    const panel = outlineRef.current;
    const current = panel?.querySelector<HTMLElement>('[aria-current="location"]');
    if (!panel || !current) return;
    const box = panel.getBoundingClientRect();
    const item = current.getBoundingClientRect();
    if (item.top < box.top) panel.scrollTop += item.top - box.top;
    else if (item.bottom > box.bottom) panel.scrollTop += item.bottom - box.bottom;
  }, [active]);
  useEffect(() => {
    const reader = readerRef.current;
    if (!reader) return;
    let frame = 0;
    const update = () => {
      const top = reader.getBoundingClientRect().top + 36;
      const rendered = reader.querySelector(".document-layer:not(.pending)");
      let current = headings[0]?.id ?? "";
      rendered?.querySelectorAll<HTMLElement>("h1,h2,h3,h4,h5,h6").forEach((heading) => {
        if (heading.getBoundingClientRect().top <= top) current = heading.id;
      });
      setActive(current);
    };
    const schedule = () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(update); };
    reader.addEventListener("scroll", schedule, { passive: true });
    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(schedule);
    observer?.observe(reader);
    update();
    return () => { reader.removeEventListener("scroll", schedule); observer?.disconnect(); cancelAnimationFrame(frame); };
  }, [headings, readerRef]);

  function jump(id: string) {
    const reader = readerRef.current;
    const rendered = reader?.querySelector(".document-layer:not(.pending)");
    const heading = Array.from(rendered?.querySelectorAll<HTMLElement>("h1,h2,h3,h4,h5,h6") ?? []).find((node) => node.id === id);
    if (reader && heading) {
      reader.scrollTop += heading.getBoundingClientRect().top - reader.getBoundingClientRect().top - 24;
      setActive(id);
    }
  }
  function branches(nodes: Branch[]) {
    return <ul className="outline-list">{nodes.map((node) => <li key={node.id}>
      <div className="outline-row">
        {node.children.length ? <button type="button" className="outline-chevron"
          aria-label={`${collapsed.has(node.id) ? "Expand" : "Collapse"} ${node.title}`} aria-expanded={!collapsed.has(node.id)}
          onClick={() => setCollapsed((previous) => { const next = new Set(previous); if (next.has(node.id)) next.delete(node.id); else next.add(node.id); return next; })}>
          {collapsed.has(node.id) ? "›" : "⌄"}</button> : <span />}
        <button type="button" className="outline-heading" aria-current={active === node.id ? "location" : undefined}
          onClick={() => jump(node.id)}>{node.title}</button>
      </div>
      {node.children.length && !collapsed.has(node.id) ? <div className="outline-children">{branches(node.children)}</div> : null}
    </li>)}</ul>;
  }
  return <aside className="outline-sidebar" aria-label="Outline panel">
    <div className="outline-panel-title">Outline</div>
    <nav ref={outlineRef} className="outline-scroll" aria-label="Document outline">{branches(hierarchy(headings))}</nav>
  </aside>;
}
