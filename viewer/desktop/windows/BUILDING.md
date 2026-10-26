# Windows build

Target: Windows 11 x64. Other Windows versions/architectures are not validated.
This uses WinForms/WebView2, a self-contained .NET 10 publish and Python's
Windows x64 embedded distribution. No Mac binaries are included.

Build prerequisites: .NET 10 SDK, Python 3.13 with pip, Node.js/npm. The existing
frontend dependencies must be installed (`npm ci` in `viewer/frontend`). Generating
a new Windows dependency lock also requires uv. Builds download official .NET
runtime/NuGet, Python and PyPI artifacts. Do not run the build without consenting
to those downloads. Nothing is installed into the host Python environment.

From the vault root, use an output directory that does not contain a previous
Windows package:

```sh
python viewer/desktop/build_windows.py --output /path/to/new/output
```

On Windows, a developer can use the equivalent `py -3.13` command in PowerShell.
Run it from the repository root, where `viewer/` is present. `--work`
can put temporary downloads on an external drive. `--dotnet` selects a temporary
SDK without a system-wide installation. The script uses only Windows wheels
and verifies them against `requirements.lock` hashes. It deliberately refuses
to overwrite an existing package or ZIP.

To update the lock after changing backend dependencies:

```sh
uv pip compile viewer/backend/requirements.txt --python-platform x86_64-pc-windows-msvc --python-version 3.13 --only-binary :all: --generate-hashes --no-header --no-annotate --output-file viewer/desktop/windows/requirements.lock
```

Do not replace this with pip's platform flags alone: they select Windows wheel
tags but can still evaluate optional-dependency OS markers on the build host.
The Windows lock includes colorama and excludes macOS/Linux-only uvloop.

Checks that can run on a Mac or Linux machine:

```sh
dotnet run --project viewer/desktop/windows/tests/PolicyTests.csproj
# Windows code compilation (cannot run its GUI on macOS/Linux):
dotnet publish viewer/desktop/windows/PhysicsWiki.csproj -c Release -r win-x64 --self-contained true -o /path/to/publish
```

On a Windows PC, extract the completed ZIP and run `Test Windows.cmd`, then the
GUI checklist in `README.txt`. That backend smoke test uses disposable notes,
including paths with Unicode/spaces, not a real user vault. The test is designed
for Windows but can also check an identically laid-out source/server staging
area on the development host; that does not validate the Windows binaries.

The launcher:

- remembers the vault and theme under `%LOCALAPPDATA%\Physics Wiki`;
- runs the local server without a console and uses a random loopback port;
- uses a Windows kill-on-close Job Object and bounded asynchronous cleanup;
- keeps normal Chromium clipboard/editing shortcuts and a native Edit menu;
- uses the same React viewer and offline MathJax as the Mac build;
- does not package API keys, environment files, notes or developer build tools;
- requires Microsoft's separately serviced WebView2 Runtime (already present
  on most Windows 11 systems); missing-runtime errors give the official link.

No Windows executable is code-signed yet. Keep `BUILD.json` marked untested until
real Windows runtime/GUI checks are complete. Hashes and successful cross-builds
are not evidence of a successful Windows launch.

References: [WebView2 distribution](https://learn.microsoft.com/microsoft-edge/webview2/concepts/distribution),
[WebView2 SDK package](https://www.nuget.org/packages/Microsoft.Web.WebView2),
[Python embedded distribution](https://docs.python.org/3/using/windows.html#the-embeddable-package).
