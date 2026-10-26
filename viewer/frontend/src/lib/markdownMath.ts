type Fence = {
  character: "`" | "~";
  length: number;
};

type LineParts = {
  prefix: string;
  content: string;
  indentedCode: boolean;
};

function splitContainerPrefix(line: string): LineParts {
  const match = /^(\s*(?:>\s*)*)(.*)$/.exec(line);
  const prefix = match?.[1] ?? "";
  const content = match?.[2] ?? line;
  const leadingWhitespace = /^\s*/.exec(line)?.[0] ?? "";
  return {
    prefix,
    content,
    indentedCode: !prefix.includes(">") && leadingWhitespace.replaceAll("\t", "    ").length >= 4
  };
}

function openingFence(content: string): Fence | null {
  const match = /^(?: {0,3})(`{3,}|~{3,})/.exec(content);
  if (!match) return null;
  return {
    character: match[1][0] as Fence["character"],
    length: match[1].length
  };
}

function closesFence(content: string, fence: Fence): boolean {
  const marker = fence.character.repeat(fence.length);
  return new RegExp(`^(?: {0,3})${marker}${fence.character}*\\s*$`).test(content);
}

/**
 * Make the Obsidian display-math forms used in this vault unambiguous to
 * remark-math. Source files remain unchanged; normalization is presentation
 * only. Fenced and indented code is deliberately left byte-for-byte intact.
 */
export function normalizeObsidianDisplayMath(markdown: string): string {
  const newline = markdown.includes("\r\n") ? "\r\n" : "\n";
  const lines = markdown.split(/\r?\n/);
  const output: string[] = [];
  let fence: Fence | null = null;
  let inDisplayMath = false;

  for (const line of lines) {
    const { prefix, content, indentedCode } = splitContainerPrefix(line);

    if (fence) {
      output.push(line);
      if (closesFence(content, fence)) fence = null;
      continue;
    }

    const nextFence = openingFence(content);
    if (nextFence) {
      output.push(line);
      fence = nextFence;
      continue;
    }

    if (indentedCode) {
      output.push(line);
      continue;
    }

    const body = content.trim();

    if (inDisplayMath) {
      if (body === "$$") {
        output.push(line);
        inDisplayMath = false;
        continue;
      }

      if (body.endsWith("$$")) {
        const beforeClosingDelimiter = body.slice(0, -2).trimEnd();
        if (beforeClosingDelimiter) output.push(`${prefix}${beforeClosingDelimiter}`);
        output.push(`${prefix}$$`);
        inDisplayMath = false;
        continue;
      }

      output.push(line);
      continue;
    }

    if (body === "$$") {
      output.push(line);
      inDisplayMath = true;
      continue;
    }

    if (body.startsWith("$$")) {
      const remainder = body.slice(2);
      const closingIndex = remainder.lastIndexOf("$$");

      if (closingIndex === remainder.length - 2 && closingIndex >= 0) {
        const formula = remainder.slice(0, -2).trim();
        if (formula) {
          output.push(`${prefix}$$`, `${prefix}${formula}`, `${prefix}$$`);
          continue;
        }
      }

      if (!remainder.includes("$$")) {
        const formulaStart = remainder.trimStart();
        output.push(`${prefix}$$`);
        if (formulaStart) output.push(`${prefix}${formulaStart}`);
        inDisplayMath = true;
        continue;
      }
    }

    output.push(line);
  }

  return output.join(newline);
}
