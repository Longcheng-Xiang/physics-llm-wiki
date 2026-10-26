import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { rankFilenameMatches } from "../lib/filenameSearch";
import {
  listVaultFiles,
  readVaultFile,
  type VaultChangeEvent,
  type VaultDocument,
  type VaultFileEntry
} from "../lib/vault";
import { FileTree } from "./FileTree";
import { ResizableWorkspace } from "./ResizableWorkspace";
import { DocumentOutline } from "./DocumentOutline";
import type { OutlineHeading } from "../lib/documentOutline";
import { FilenameResults } from "./FilenameResults";
import { MarkdownMessage } from "./MarkdownMessage";

// Each loaded document first renders in a hidden pending layer. Once its math is
// typeset and its images are ready, it replaces the visible layer in a single
// commit, so neither a refresh nor a navigation ever shows raw TeX. A refresh
// that arrives while another is still rendering waits in `next`.
type DocumentLayer = {
  key: string;
  document: VaultDocument;
  keepScroll: boolean;
  headings: OutlineHeading[];
};

type Layers = {
  shown: DocumentLayer | null;
  pending: DocumentLayer | null;
  next: DocumentLayer | null;
};

const EMPTY_HEADINGS: OutlineHeading[] = [];
const noLayers: Layers = { shown: null, pending: null, next: null };

// Show a pending layer anyway if its rendering never reports back.
const PENDING_LAYER_TIMEOUT_MS = 6000;

export function VaultReader() {
  const [files, setFiles] = useState<VaultFileEntry[]>([]);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [layers, setLayers] = useState<Layers>(noLayers);
  const [query, setQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const searchDialogRef = useRef<HTMLDialogElement>(null);
  const searchTriggerRef = useRef<HTMLButtonElement>(null);
  const [searchIndex, setSearchIndex] = useState(0);
  const searchMatches = useMemo(() => rankFilenameMatches(files, query), [files, query]);
  const activeSearchIndex = Math.min(searchIndex, Math.max(0, searchMatches.length - 1));
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [assetVersion, setAssetVersion] = useState(0);
  const readerRef = useRef<HTMLDivElement | null>(null);
  const selectedPathRef = useRef<string | null>(null);
  const fileRequestRef = useRef<AbortController | null>(null);
  const refreshTimerRef = useRef<number | null>(null);
  const pendingChangesRef = useRef<Map<string, VaultChangeEvent>>(new Map());
  const layerCountRef = useRef(0);
  const swapScrollTopRef = useRef(0);

  const closeSearch = useCallback(() => {
    setSearchOpen(false);
    setQuery("");
    setSearchIndex(0);
  }, []);

  useEffect(() => {
    const dialog = searchDialogRef.current;
    if (!dialog) return;
    if (searchOpen) {
      if (!dialog.open) {
        if (dialog.showModal) dialog.showModal();
        else dialog.setAttribute("open", "");
      }
      dialog.querySelector("input")?.focus();
    } else if (dialog.open) {
      if (dialog.close) dialog.close();
      else dialog.removeAttribute("open");
      searchTriggerRef.current?.focus();
    }
  }, [searchOpen]);

  useEffect(() => {
    selectedPathRef.current = selectedPath;
  }, [selectedPath]);

  const loadFiles = useCallback(async (signal?: AbortSignal) => {
    const nextFiles = await listVaultFiles(signal);
    setFiles(nextFiles);
    return nextFiles;
  }, []);

  const loadFile = useCallback(async (path: string, keepScroll: boolean) => {
    fileRequestRef.current?.abort();
    const controller = new AbortController();
    fileRequestRef.current = controller;
    try {
      const nextDocument = await readVaultFile(path, controller.signal);
      layerCountRef.current += 1;
      const layer: DocumentLayer = {
        key: `${nextDocument.path}:${nextDocument.modifiedNs}:${layerCountRef.current}`,
        document: nextDocument,
        keepScroll,
        headings: []
      };
      // Navigation replaces whatever is still rendering; a refresh lets it finish.
      setLayers((current) =>
        keepScroll && current.pending
          ? { ...current, next: layer }
          : { ...current, pending: layer, next: null }
      );
      setSelectedPath(path);
      setError(null);
    } catch (requestError) {
      if (controller.signal.aborted) return;
      setError(requestError instanceof Error ? requestError.message : "Could not open the file.");
    }
  }, []);

  const openFile = useCallback((path: string) => void loadFile(path, false), [loadFile]);

  const handleLayerRendered = useCallback((key: string, headings: OutlineHeading[] = []) => {
    swapScrollTopRef.current = readerRef.current?.scrollTop ?? 0;
    setLayers((current) =>
      current.pending?.key === key
        ? { shown: { ...current.pending, headings }, pending: current.next, next: null }
        : current.shown?.key === key ? { ...current, shown: { ...current.shown, headings } } : current
    );
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void (async () => {
      try {
        await loadFiles(controller.signal);
        setError(null);
      } catch (requestError) {
        if (!controller.signal.aborted) {
          setError(requestError instanceof Error ? requestError.message : "Could not load the vault.");
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    })();
    return () => controller.abort();
  }, [loadFiles]);

  useEffect(() => {
    if (typeof EventSource === "undefined") return;
    // EventSource reconnects on its own if the local server connection drops.
    const source = new EventSource("/api/vault/events");
    source.addEventListener("vault_change", (event) => {
      const change = JSON.parse((event as MessageEvent<string>).data) as VaultChangeEvent;
      pendingChangesRef.current.set(change.path, change);
      if (refreshTimerRef.current !== null) window.clearTimeout(refreshTimerRef.current);
      refreshTimerRef.current = window.setTimeout(() => {
        const changes = [...pendingChangesRef.current.values()];
        pendingChangesRef.current.clear();

        if (changes.some((item) => item.kind === "asset")) {
          setAssetVersion(Date.now());
        }

        const markdownChanges = changes.filter((item) => item.kind === "markdown");
        const selectedChange = markdownChanges.find((item) => item.path === selectedPathRef.current);
        const treeChanged = markdownChanges.some((item) => item.change !== "modified");

        if (treeChanged) {
          void loadFiles()
            .then((nextFiles) => {
              if (
                selectedChange?.change === "deleted" &&
                nextFiles.some((file) => file.path === selectedChange.path)
              ) {
                void loadFile(selectedChange.path, true);
              }
            })
            .catch(() => undefined);
        }

        if (selectedChange) {
          if (selectedChange.change === "deleted") {
            setLayers(noLayers);
            setError("The open file was deleted.");
          } else {
            void loadFile(selectedChange.path, true);
          }
        }
      }, 110);
    });
    return () => source.close();
  }, [loadFile, loadFiles]);

  const shownLayer = layers.shown;
  useLayoutEffect(() => {
    if (!shownLayer || !readerRef.current) return;
    readerRef.current.scrollTop = shownLayer.keepScroll ? swapScrollTopRef.current : 0;
  }, [shownLayer]);

  const pendingKey = layers.pending?.key;
  useEffect(() => {
    if (!pendingKey) return;
    const timer = window.setTimeout(() => handleLayerRendered(pendingKey), PENDING_LAYER_TIMEOUT_MS);
    return () => window.clearTimeout(timer);
  }, [pendingKey, handleLayerRendered]);

  useEffect(
    () => () => {
      fileRequestRef.current?.abort();
      if (refreshTimerRef.current !== null) window.clearTimeout(refreshTimerRef.current);
      pendingChangesRef.current.clear();
    },
    []
  );

  return (
    <ResizableWorkspace left={<aside className="vault-sidebar">
        <div className="sidebar-heading">
          <div>
            <p className="eyebrow">READ ONLY</p>
            <h1>Files</h1>
          </div>
        </div>
        <div className="file-filter">
          <button ref={searchTriggerRef} type="button" className="file-search-trigger"
            onClick={() => setSearchOpen(true)}>Find filename…</button>
        </div>
        <div className="tree-scroll">
          {loading ? <p className="tree-empty">Loading Markdown files…</p> : null}
          {!loading ? <FileTree files={files} selectedPath={selectedPath} onSelect={openFile} /> : null}
        </div>
        <div className="sidebar-footer">{files.length} Markdown files</div>
      </aside>} right={<DocumentOutline headings={layers.shown?.headings ?? EMPTY_HEADINGS} readerRef={readerRef} documentPath={layers.shown?.document.path ?? null} />}>

      <section className="document-pane">
        <header className="document-bar">
          <div className="document-path" title={selectedPath ?? undefined}>{selectedPath ?? ""}</div>
        </header>
        <div className="reader-scroll" ref={readerRef}>
          {error ? <div className="reader-error">{error}</div> : null}
          {layers.shown || layers.pending ? (
            <article className="markdown-preview-view">
              <div className="document-layers">
                {[layers.shown, layers.pending].map((layer) =>
                  layer ? (
                    <DocumentLayerView
                      key={layer.key}
                      layer={layer}
                      pending={layer === layers.pending}
                      assetVersion={assetVersion}
                      onNavigate={openFile}
                      onRendered={handleLayerRendered}
                    />
                  ) : null
                )}
              </div>
            </article>
          ) : null}
        </div>
      </section>
      <dialog ref={searchDialogRef} className="file-search-dialog" aria-label="Find a file"
        onCancel={(event) => { event.preventDefault(); closeSearch(); }}
        onClick={(event) => {
          if (event.target !== event.currentTarget) return;
          const bounds = event.currentTarget.getBoundingClientRect();
          if (event.clientX < bounds.left || event.clientX > bounds.right ||
              event.clientY < bounds.top || event.clientY > bounds.bottom) closeSearch();
        }}>
        <div className="file-search-header">
          <input type="search" aria-label="Filter Markdown files" placeholder="Find a file…" value={query}
            aria-controls="filename-search-results"
            aria-activedescendant={searchMatches.length ? `file-result-${activeSearchIndex}` : undefined}
            onChange={(event) => { setQuery(event.target.value); setSearchIndex(0); }}
            onKeyDown={(event) => {
              if (event.key === "Escape") { event.preventDefault(); closeSearch(); }
              else if (searchMatches.length && (event.key === "ArrowDown" || event.key === "ArrowUp")) {
                event.preventDefault();
                const step = event.key === "ArrowDown" ? 1 : -1;
                setSearchIndex((activeSearchIndex + step + searchMatches.length) % searchMatches.length);
              } else if (searchMatches.length && event.key === "Enter") {
                event.preventDefault();
                openFile(searchMatches[activeSearchIndex].file.path);
                closeSearch();
              }
            }} />
          <button type="button" className="file-search-close" aria-label="Close file search" onClick={closeSearch}>×</button>
        </div>
        <FilenameResults matches={searchMatches} activeIndex={activeSearchIndex} query={query}
          onSelect={(path) => { openFile(path); closeSearch(); }} />
        <div className="file-search-footer"><span>↑↓ to navigate</span><span>↵ to open</span><span>esc to dismiss</span></div>
      </dialog>

    </ResizableWorkspace>
  );
}

type DocumentLayerViewProps = {
  layer: DocumentLayer;
  pending: boolean;
  assetVersion: number;
  onNavigate: (path: string) => void;
  onRendered: (key: string, headings: OutlineHeading[]) => void;
};

function DocumentLayerView({ layer, pending, assetVersion, onNavigate, onRendered }: DocumentLayerViewProps) {
  // Stable per layer, so promoting the layer does not re-run its typesetting.
  const handleRendered = useCallback((headings: OutlineHeading[]) => onRendered(layer.key, headings), [onRendered, layer.key]);
  return (
    <div className={pending ? "document-layer pending" : "document-layer"} aria-hidden={pending || undefined}>
      <MarkdownMessage
        content={layer.document.content}
        currentPath={layer.document.path}
        assetVersion={assetVersion}
        onNavigate={onNavigate}
        onRendered={handleRendered}
      />
    </div>
  );
}
