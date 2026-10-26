"""Exercise the actual bundled Windows Python and server, using a disposable vault."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request


def main():
    resources = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="Physics Wiki test é ") as name:
        root = Path(name)
        vault = root / "wiki 中文"
        (vault / ".claude/rules").mkdir(parents=True)
        (vault / ".obsidian").mkdir()
        for rel, text in {"index.md": "# Index", "CLAUDE.md": "# Instructions",
                          "Unicode é.md": "# Café — 中文\n\nFirst paragraph.\n\nSecond paragraph.\n\n$E=mc^2$",
                          ".claude/rules/demo.md": "# A visible rule",
                          ".obsidian/private.md": "hidden", "script.py": "not viewer content"}.items():
            (vault / rel).write_text(text, encoding="utf-8")
        port_file = root / "server.port"
        environment = {**os.environ, "WIKI_VAULT_ROOT": str(vault), "WIKI_DESKTOP_VIEWER_ONLY": "1",
                       "WIKI_DESKTOP_PORT_FILE": str(port_file),
                       "WIKI_FRONTEND_DIST": str(resources / "frontend/dist")}
        with (root / "server.log").open("wb") as log:
            process = subprocess.Popen([sys.executable, str(resources / "desktop/server_entry.py")], env=environment,
                                       stdout=log, stderr=log)
            try:
                for _ in range(200):
                    if process.poll() is not None:
                        raise RuntimeError((root / "server.log").read_text(errors="replace"))
                    if port_file.exists():
                        base = "http://127.0.0.1:" + port_file.read_text()
                        try:
                            with urllib.request.urlopen(base + "/api/health", timeout=1) as response:
                                health = json.load(response)
                            assert health["viewer_only"] is True
                            break
                        except OSError:
                            pass
                    time.sleep(.1)
                else:
                    raise RuntimeError("Bundled server startup timed out")
                def read(path):
                    with urllib.request.urlopen(base + path, timeout=3) as response:
                        return response.read()
                paths = {x["path"] for x in json.loads(read("/api/vault/files"))["files"]}
                assert ".claude/rules/demo.md" in paths
                assert ".obsidian/private.md" not in paths and "script.py" not in paths
                result = json.loads(read("/api/vault/file?" + urllib.parse.urlencode({"path": "Unicode é.md"})))
                assert result["content"] == (vault / "Unicode é.md").read_text(encoding="utf-8")
                assert b"mathjax/tex-chtml.js" in read("/")
                assert len(read("/mathjax/tex-chtml.js")) > 10000
                try:
                    read("/api/vault/file?" + urllib.parse.urlencode({"path": "../outside.md"}))
                    raise AssertionError("Path traversal was accepted")
                except urllib.error.HTTPError as error:
                    assert error.code == 403
                print("PASS: Python/server startup, Unicode paths/content, .claude visibility,")
                print("      hidden exclusions, local MathJax, read-only path boundary.")
            finally:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait(timeout=3)


if __name__ == "__main__":
    main()
