import { useEffect, useState } from "react";
import type { VaultFileEntry } from "../lib/vault";

type TreeDirectory = {
  name: string;
  path: string;
  directories: Map<string, TreeDirectory>;
  files: VaultFileEntry[];
};

type Props = {
  files: VaultFileEntry[];
  selectedPath: string | null;
  onSelect: (path: string) => void;
};

function makeDirectory(name: string, path: string): TreeDirectory {
  return { name, path, directories: new Map(), files: [] };
}

function buildTree(files: VaultFileEntry[]): TreeDirectory {
  const root = makeDirectory("Vault", "");
  for (const file of files) {
    const parts = file.path.split("/");
    let current = root;
    for (const part of parts.slice(0, -1)) {
      const path = current.path ? `${current.path}/${part}` : part;
      const existing = current.directories.get(part);
      if (existing) {
        current = existing;
      } else {
        const directory = makeDirectory(part, path);
        current.directories.set(part, directory);
        current = directory;
      }
    }
    current.files.push(file);
  }
  return root;
}

function FileButton({ file, selectedPath, onSelect }: Pick<Props, "selectedPath" | "onSelect"> & { file: VaultFileEntry }) {
  return (
    <button
      className={`tree-file${selectedPath === file.path ? " active" : ""}`}
      type="button"
      title={file.path}
      onClick={() => onSelect(file.path)}
    >
      <span className="tree-file-icon" aria-hidden="true" />
      <span>{file.name.replace(/\.md$/i, "")}</span>
    </button>
  );
}

function DirectoryNode({
  directory,
  selectedPath,
  onSelect
}: {
  directory: TreeDirectory;
  selectedPath: string | null;
  onSelect: (path: string) => void;
}) {
  const containsSelection = Boolean(selectedPath?.startsWith(`${directory.path}/`));
  const [open, setOpen] = useState(containsSelection);
  const directories = [...directory.directories.values()].sort((a, b) => a.name.localeCompare(b.name));
  const files = [...directory.files].sort((a, b) => a.name.localeCompare(b.name));

  useEffect(() => {
    if (containsSelection) setOpen(true);
  }, [containsSelection]);

  return (
    <details className="tree-directory" open={open} onToggle={(event) => setOpen(event.currentTarget.open)}>
      <summary>{directory.name}</summary>
      <div className="tree-children">
        {directories.map((child) => (
          <DirectoryNode
            key={child.path}
            directory={child}
            selectedPath={selectedPath}
            onSelect={onSelect}
          />
        ))}
        {files.map((file) => (
          <FileButton key={file.path} file={file} selectedPath={selectedPath} onSelect={onSelect} />
        ))}
      </div>
    </details>
  );
}

export function FileTree({ files, selectedPath, onSelect }: Props) {
  const tree = buildTree(files);
  return (
    <nav className="file-tree" aria-label="Markdown files">
      {[...tree.directories.values()]
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((directory) => (
          <DirectoryNode
            key={directory.path}
            directory={directory}
            selectedPath={selectedPath}
            onSelect={onSelect}
          />
        ))}
      {[...tree.files]
        .sort((a, b) => a.name.localeCompare(b.name))
        .map((file) => (
          <FileButton key={file.path} file={file} selectedPath={selectedPath} onSelect={onSelect} />
        ))}
    </nav>
  );
}
