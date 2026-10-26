import { cp, mkdir, readFile, writeFile } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const desktopDirectory = dirname(fileURLToPath(import.meta.url));
const frontendDirectory = resolve(desktopDirectory, "../frontend");
const distDirectory = join(frontendDirectory, "dist");
const mathJaxSource = join(frontendDirectory, "node_modules/mathjax-full/es5");
const mathJaxTarget = join(distDirectory, "mathjax");
const htmlPath = join(distDirectory, "index.html");
const remoteScript = "https://cdn.jsdelivr.net/npm/mathjax@3.2.1/es5/tex-chtml.js";
const localScript = "/mathjax/tex-chtml.js";

await mkdir(mathJaxTarget, { recursive: true });
await cp(mathJaxSource, mathJaxTarget, {
  recursive: true,
  filter: (source) => {
    const name = basename(source);
    return !name.endsWith(".map") && !/ \d+\.[^.]+$/.test(name);
  }
});
await cp(join(frontendDirectory, "node_modules/mathjax-full/LICENSE"), join(mathJaxTarget, "LICENSE"));

const html = await readFile(htmlPath, "utf8");
if (!html.includes(remoteScript)) {
  throw new Error("The expected MathJax script URL is missing from the frontend build.");
}
await writeFile(htmlPath, html.replace(remoteScript, localScript));
