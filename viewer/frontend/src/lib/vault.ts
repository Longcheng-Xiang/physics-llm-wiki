export type VaultFileEntry = {
  path: string;
  name: string;
  modifiedNs: number;
};

export type VaultDocument = VaultFileEntry & {
  content: string;
};

export type VaultChangeEvent = {
  type: "vault_change";
  path: string;
  kind: "markdown" | "asset";
  change: "added" | "modified" | "deleted";
};

async function responseMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string };
    return payload.detail || fallback;
  } catch {
    return fallback;
  }
}

export async function listVaultFiles(signal?: AbortSignal): Promise<VaultFileEntry[]> {
  const response = await fetch("/api/vault/files", { signal });
  if (!response.ok) {
    throw new Error(await responseMessage(response, "Could not load the vault file list."));
  }
  const payload = (await response.json()) as { files: VaultFileEntry[] };
  return payload.files;
}

export async function readVaultFile(path: string, signal?: AbortSignal): Promise<VaultDocument> {
  const response = await fetch(`/api/vault/file?path=${encodeURIComponent(path)}`, { signal });
  if (!response.ok) {
    throw new Error(await responseMessage(response, "Could not open the Markdown file."));
  }
  return (await response.json()) as VaultDocument;
}

export function viewerAssetUrl(path: string, version: number): string {
  return `/api/vault/asset?path=${encodeURIComponent(path)}&v=${version}`;
}

function decodedPath(value: string): string {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

export function resolveVaultPath(currentPath: string, target: string): string | null {
  const withoutFragment = target.split("#", 1)[0].split("?", 1)[0];
  if (!withoutFragment || /^(?:[a-z]+:|\/\/)/i.test(withoutFragment)) return null;

  const decoded = decodedPath(withoutFragment).replaceAll("\\", "/");
  const base = decoded.startsWith("/") ? [] : currentPath.split("/").slice(0, -1);
  const parts = [...base, ...decoded.replace(/^\/+/, "").split("/")];
  const normalized: string[] = [];
  for (const part of parts) {
    if (!part || part === ".") continue;
    if (part === "..") {
      if (normalized.length === 0) return null;
      normalized.pop();
      continue;
    }
    normalized.push(part);
  }
  return normalized.join("/");
}
