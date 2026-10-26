# Physics Wiki Viewer

This directory contains the source code for the read-only Physics Wiki desktop viewer. Released desktop builds display Markdown and local image assets, render MathJax locally, provide filename search and an outline, and remember the selected vault without modifying its files.

## Source layout

- `frontend/` contains the React reading interface and its tests.
- `backend/` contains the local read-only vault server and its tests.
- `desktop/` contains the macOS and Windows launchers, icons, packaging scripts, and platform tests.

Generated dependencies and build products are intentionally excluded. Install them locally from the checked-in dependency manifests.

## macOS build

The macOS build requires Apple command-line development tools, Node.js with npm, and `uv`. From this directory:

```sh
./desktop/build_macos.sh
```

The script builds the frontend and bundled local server, checks that every bundled binary supports the declared macOS target, signs the application ad hoc, and places `Physics Wiki.app` under `~/Downloads/Physics Wiki Viewer Builds/`.

## Windows x64 build

The Windows build requires Node.js with npm, Python 3.13 with pip, `uv`, and the .NET 10 SDK. Install frontend dependencies first, then follow `desktop/windows/BUILDING.md`.

Released desktop packages are built in viewer-only mode. The optional chat integrations retained in the development source are not enabled in those packages.
