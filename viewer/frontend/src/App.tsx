import { useEffect, useState } from "react";
import { ChatView } from "./components/ChatView";
import { VaultReader } from "./components/VaultReader";
import "./styles.css";

type View = "files" | "chat";
type Theme = "light" | "dark";
const viewerOnly = import.meta.env.VITE_VIEWER_ONLY === "1";

function initialTheme(): Theme {
  const saved = window.localStorage.getItem("physics-wiki:theme");
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function App() {
  const [view, setView] = useState<View>("files");
  const [theme, setTheme] = useState<Theme>(initialTheme);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("physics-wiki:theme", theme);
    window.webkit?.messageHandlers?.appearance?.postMessage(theme);
    window.chrome?.webview?.postMessage({ type: "appearance", theme });
  }, [theme]);

  return (
    <div className="application">
      <header className={`application-bar${viewerOnly ? " viewer-only" : ""}`}>
        <div className="application-brand">
          <img className="brand-mark" src="/brand-mark.png" alt="" aria-hidden="true" />
          <span>Physics Wiki</span>
        </div>
        {!viewerOnly && <nav className="view-switcher" aria-label="Application view">
          <button type="button" className={view === "files" ? "active" : ""} onClick={() => setView("files")}>
            Files
          </button>
          <button type="button" className={view === "chat" ? "active" : ""} onClick={() => setView("chat")}>
            Chat
          </button>
        </nav>}
        <button
          className="theme-toggle"
          type="button"
          aria-label={`Use ${theme === "light" ? "dark" : "light"} mode`}
          onClick={() => setTheme((current) => (current === "light" ? "dark" : "light"))}
        >
          <span aria-hidden="true">{theme === "light" ? "◐" : "☀"}</span>
          <span>{theme === "light" ? "Dark" : "Light"}</span>
        </button>
      </header>
      {viewerOnly || view === "files" ? <VaultReader /> : <ChatView />}
    </div>
  );
}
