/// <reference types="vite/client" />

interface Window {
  chrome?: {
    webview?: { postMessage: (message: { type: "appearance"; theme: "light" | "dark" }) => void };
  };
  webkit?: {
    messageHandlers?: {
      appearance?: { postMessage: (theme: "light" | "dark") => void };
    };
  };
  MathJax?: {
    typesetPromise?: (elements?: HTMLElement[]) => Promise<void>;
    typesetClear?: (elements?: HTMLElement[]) => void;
    startup?: {
      defaultReady?: () => void;
      promise?: Promise<void>;
    };
  };
  physicsWikiMathJax?: Window["MathJax"];
}
