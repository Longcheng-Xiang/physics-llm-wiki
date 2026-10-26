#!/bin/zsh
set -euo pipefail

desktop_dir="$(cd "$(dirname "$0")" && pwd)"
viewer_root="$(cd "$desktop_dir/.." && pwd)"
build_root="$(mktemp -d /tmp/physics-wiki-build.XXXXXX)"
app_bundle="$build_root/Physics Wiki.app"
release_dir="$HOME/Downloads/Physics Wiki Viewer Builds"
release_app="$release_dir/Physics Wiki.app"

# Oldest macOS the app supports. Every bundled binary must be built for it too.
target_macos="11.0"
build_python="3.13"
pyinstaller_version="6.22.3"

if ! command -v uv > /dev/null; then
  print -u2 "Install uv (for example with Homebrew) before building."
  exit 1
fi

# Replacing a running app moves it to the Trash and leaves the old version open.
if pgrep -f "Physics Wiki.app/Contents/MacOS/Physics Wiki" > /dev/null; then
  print -u2 "Quit Physics Wiki before rebuilding it."
  exit 1
fi

cd "$viewer_root/frontend"
VITE_VIEWER_ONLY=1 npm run build
node "$desktop_dir/prepare_frontend.mjs"

# Homebrew's Python runs only on the macOS version it was built for, so bundle a
# portable uv-managed Python instead. Those builds support macOS 11. The build
# environment lives in the temporary build folder, outside the iCloud vault.
uv python install --no-bin "$build_python"
uv venv --managed-python --python "$build_python" "$build_root/venv"
uv pip install --python "$build_root/venv/bin/python" \
  -r "$viewer_root/backend/requirements.txt" \
  "pyinstaller==$pyinstaller_version"

cd "$viewer_root/backend"
"$build_root/venv/bin/pyinstaller" \
  --noconfirm \
  --onedir \
  --console \
  --name physics-wiki-server \
  --distpath "$build_root/server-dist" \
  --workpath "$build_root/server-work" \
  --specpath "$build_root/spec" \
  --paths "$viewer_root/backend" \
  --add-data "$viewer_root/frontend/dist:frontend/dist" \
  --collect-submodules uvicorn \
  --collect-submodules watchfiles \
  "$desktop_dir/server_entry.py"

mkdir -p "$app_bundle/Contents/MacOS" "$app_bundle/Contents/Resources/server"
swiftc -swift-version 5 -parse-as-library -target "arm64-apple-macosx$target_macos" -O \
  -framework AppKit \
  -framework WebKit \
  "$desktop_dir/Launcher.swift" \
  -o "$app_bundle/Contents/MacOS/Physics Wiki"
cp "$desktop_dir/Info.plist" "$app_bundle/Contents/Info.plist"
cp "$desktop_dir/icons/PhysicsWiki.icns" "$app_bundle/Contents/Resources/PhysicsWiki.icns"
ditto "$build_root/server-dist/physics-wiki-server" \
  "$app_bundle/Contents/Resources/server/physics-wiki-server"

# Declare the newest macOS any bundled binary needs, and refuse to finish if that
# is newer than the target, so a non-portable Python cannot slip back in.
min_macos="$(
  find "$app_bundle" -type f -exec vtool -show-build {} \; 2>/dev/null |
    awk '$1 == "minos" { print $2 }' |
    sort -t. -k1,1n -k2,2n |
    tail -n 1
)"
if [[ -z "$min_macos" ]]; then
  print -u2 "Could not read the minimum macOS version from the bundled binaries."
  exit 1
fi
autoload -Uz is-at-least
if ! is-at-least "$min_macos" "$target_macos"; then
  print -u2 "The app would need macOS $min_macos, newer than the macOS $target_macos target."
  print -u2 "A bundled binary was built for a newer macOS; check which Python PyInstaller used."
  exit 1
fi
plutil -replace LSMinimumSystemVersion -string "$min_macos" "$app_bundle/Contents/Info.plist"
codesign --force --deep --sign - "$app_bundle"

mkdir -p "$release_dir"
if [[ -e "$release_app" ]]; then
  trash_dir="$(mktemp -d "$HOME/.Trash/physics-wiki-app.XXXXXX")"
  mv "$release_app" "$trash_dir/Physics Wiki.app"
  print "Previous build moved to $trash_dir"
fi
mv "$app_bundle" "$release_app"
rm -rf "$build_root"
print "Built $release_app"
