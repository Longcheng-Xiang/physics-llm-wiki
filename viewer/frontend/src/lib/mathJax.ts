type MathJaxRuntime = NonNullable<Window["MathJax"]>;

let mathJaxQueue: Promise<void> = Promise.resolve();

function enqueue(task: () => Promise<void> | void): Promise<void> {
  const next = mathJaxQueue.catch(() => undefined).then(task);
  mathJaxQueue = next.catch(() => undefined);
  return next;
}

function pause(milliseconds: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

async function waitForMathJax(cancelled: () => boolean): Promise<MathJaxRuntime | null> {
  for (let attempt = 0; attempt < 300; attempt += 1) {
    if (cancelled()) return null;
    const mathJax = window.physicsWikiMathJax ?? window.MathJax;
    // index.html defines the MathJax configuration before anything renders, so
    // its absence means this page has no MathJax at all (as in unit tests).
    if (!mathJax) return null;
    if (mathJax.startup?.promise) {
      try {
        await mathJax.startup.promise;
      } catch {
        return null;
      }
    }
    if (mathJax?.typesetPromise) return mathJax;
    await pause(50);
  }
  return null;
}

export function queueMathJaxTypeset(root: HTMLElement, cancelled: () => boolean): Promise<void> {
  return enqueue(async () => {
    const mathJax = await waitForMathJax(cancelled);
    if (!mathJax?.typesetPromise || cancelled() || !root.isConnected) return;
    await mathJax.typesetPromise([root]);
  });
}

export function queueMathJaxClear(root: HTMLElement): void {
  void enqueue(() => {
    (window.physicsWikiMathJax ?? window.MathJax)?.typesetClear?.([root]);
  });
}
