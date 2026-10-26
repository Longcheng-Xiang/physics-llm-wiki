Physics Wiki 1.0.0-preview.1 — Windows x64 preview

1. Extract the entire ZIP to a folder on your PC. Do not run it inside the ZIP.
2. Open Physics Wiki.exe. Keep the resources folder and the DLL files beside it.
3. Choose your wiki folder (the folder containing index.md and CLAUDE.md).

Target: Windows 11 x64. Windows 10 22H2 compatibility needs testing.
This build has been cross-compiled on a Mac; real Windows testing is still
required before calling it a release. ARM64 and 32-bit Windows are not targets.

Python and .NET are included. You do not need to install them.
Microsoft Edge WebView2 Runtime must be installed. Windows 11 normally has it.
If the app reports it is missing, use Microsoft's official installer:
https://developer.microsoft.com/microsoft-edge/webview2/
After that first-time prerequisite, note viewing works without internet access.

Use File > Switch Vault (Ctrl+O) to select a different wiki.
Select note text and use Ctrl+C to copy; Ctrl+V pastes into filename search.
Ctrl+A/X/Z and Ctrl+Shift+Z work in editable text fields. Notes are read-only.
Drag the thin divider lines to resize the file and outline panels.
Close the window or use Alt+F4 / File > Exit to quit the local server too.

Settings, browser cache and the server log are stored in:
%LOCALAPPDATA%\Physics Wiki\
Nothing is installed system-wide. No notes or account credentials are included.
This build is unsigned, so Windows may show an unfamiliar-app warning.

Before sharing as a release:
- Run Test Windows.cmd. It checks the bundled server/runtime without a vault.
- Open the app, choose a real vault, open a note, and search by filename.
- Copy several prose paragraphs to Notepad; test Unicode and line breaks.
- Paste into search; test select all, cut, undo, redo and mouse selection.
- Verify light/dark title bar, math, SVGs, quote indentation, resizing/outline.
- Change an open note in an external editor and confirm it refreshes.
- Switch vaults, quit, reopen, move the vault and select its new folder.
- Check Task Manager: no bundled Python server should remain after quitting.
- Repeat offline and from an extracted folder with spaces/non-ASCII characters.
