import AppKit
import Foundation
import WebKit

private final class WindowThemeHandler: NSObject, WKScriptMessageHandler {
    private weak var window: NSWindow?
    init(window: NSWindow) { self.window = window }

    func userContentController(_ userContentController: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard message.frameInfo.isMainFrame,
              message.frameInfo.securityOrigin.host == "127.0.0.1",
              let theme = message.body as? String else { return }
        if theme == "dark" { window?.appearance = NSAppearance(named: .darkAqua) }
        else if theme == "light" { window?.appearance = NSAppearance(named: .aqua) }
    }
}

final class ViewerApplication: NSObject, NSApplicationDelegate, NSWindowDelegate, WKNavigationDelegate {
    private var window: NSWindow?
    private var server: Process?
    private var serverLog: FileHandle?
    private var portFile: URL?
    private var scopedVaultRoot: URL?
    private var vaultRoot: URL?
    // Incremented for each server start, so a slower, superseded start cannot
    // take over the window after the user switches vaults.
    private var serverGeneration = 0
    private var terminationRequested = false
    private var shutdownInProgress = false
    private var shutdownCompletions: [() -> Void] = []
    private struct VaultChoice {
        let url: URL
        let scoped: Bool
        let renewBookmark: Bool
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        installMenu()

        showStartingWindow()
        let generation = serverGeneration
        // Bookmark resolution and iCloud file checks must not block the UI.
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            let root = self.findVaultRoot()
            DispatchQueue.main.async {
                // A vault switch or quit may finish before the bookmark lookup.
                // Never let that delayed startup replace an already chosen vault.
                guard !self.terminationRequested, generation == self.serverGeneration,
                      self.server == nil, self.vaultRoot == nil else {
                    if let root = root, root.scoped { root.url.stopAccessingSecurityScopedResource() }
                    return
                }
                if let root = root {
                    self.scopedVaultRoot = root.scoped ? root.url : nil
                    if root.renewBookmark { self.saveVaultBookmark(root.url) }
                    self.startServer(vaultRoot: root.url)
                }
                else { self.showVaultChooser() }
            }
        }
    }

    private func startServer(vaultRoot: URL) {
        guard let resources = Bundle.main.resourceURL else {
            showError("The app bundle is incomplete.")
            NSApp.terminate(nil)
            return
        }

        let serverExecutable = resources
            .appendingPathComponent("server/physics-wiki-server/physics-wiki-server")
        guard FileManager.default.isExecutableFile(atPath: serverExecutable.path) else {
            showError("The viewer server is missing from this app bundle.")
            NSApp.terminate(nil)
            return
        }

        self.vaultRoot = vaultRoot
        serverGeneration += 1
        let generation = serverGeneration

        let portFile = FileManager.default.temporaryDirectory
            .appendingPathComponent("physics-wiki-" + UUID().uuidString + ".port")
        self.portFile = portFile

        let process = Process()
        process.executableURL = serverExecutable
        process.currentDirectoryURL = FileManager.default.temporaryDirectory
        var environment = ProcessInfo.processInfo.environment
        environment["WIKI_VAULT_ROOT"] = vaultRoot.path
        environment["WIKI_DESKTOP_PORT_FILE"] = portFile.path
        environment["WIKI_DESKTOP_VIEWER_ONLY"] = "1"
        process.environment = environment
        process.standardInput = FileHandle.nullDevice

        let logDirectory = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Library/Logs", isDirectory: true)
        let logURL = logDirectory.appendingPathComponent("Physics Wiki Viewer.log")
        FileManager.default.createFile(atPath: logURL.path, contents: nil)
        if let handle = try? FileHandle(forWritingTo: logURL) {
            handle.seekToEndOfFile()
            serverLog = handle
            process.standardOutput = handle
            process.standardError = handle
        } else {
            process.standardOutput = FileHandle.nullDevice
            process.standardError = FileHandle.nullDevice
        }

        do {
            try process.run()
            server = process
            waitForServer(process: process, portFile: portFile, generation: generation)
        } catch {
            showError("The viewer could not start. See Library/Logs/Physics Wiki Viewer.log for details.")
            NSApp.terminate(nil)
        }
    }

    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        if terminationRequested { return .terminateLater }
        terminationRequested = true
        window?.orderOut(nil)
        stopServer {
            sender.reply(toApplicationShouldTerminate: true)
        }
        return .terminateLater
    }

    func applicationWillTerminate(_ notification: Notification) {
        // Normal quit has already reaped the server asynchronously. This is a
        // non-blocking last resort for an unusual system-initiated termination.
        if let process = server, process.isRunning { kill(process.processIdentifier, SIGKILL) }
        scopedVaultRoot?.stopAccessingSecurityScopedResource()
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        // The close delegate below explicitly uses the same deferred quit path
        // as Cmd+Q, keeping the run loop alive until server cleanup finishes.
        false
    }

    func windowWillClose(_ notification: Notification) {
        (window?.contentView as? WKWebView)?.stopLoading()
        if !terminationRequested { NSApp.terminate(nil) }
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        disableElasticity(in: webView)
    }

    func webView(
        _ webView: WKWebView,
        decidePolicyFor navigationAction: WKNavigationAction,
        decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
    ) {
        if navigationAction.navigationType == .linkActivated,
           let url = navigationAction.request.url,
           url.host != "127.0.0.1" {
            NSWorkspace.shared.open(url)
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    private func installMenu() {
        let mainMenu = NSMenu()
        let appItem = NSMenuItem()
        let appMenu = NSMenu()
        appMenu.addItem(
            withTitle: "Quit Physics Wiki",
            action: #selector(NSApplication.terminate(_:)),
            keyEquivalent: "q"
        )
        appItem.submenu = appMenu
        mainMenu.addItem(appItem)

        let fileItem = NSMenuItem()
        let fileMenu = NSMenu(title: "File")
        let switchItem = NSMenuItem(
            title: "Switch Vault…",
            action: #selector(switchVaultClicked(_:)),
            keyEquivalent: "o"
        )
        switchItem.target = self
        fileMenu.addItem(switchItem)
        fileItem.submenu = fileMenu
        mainMenu.addItem(fileItem)

        // Route standard editing actions through the responder chain to the
        // focused WKWebView selection or input, including native validation.
        let editItem = NSMenuItem()
        let editMenu = NSMenu(title: "Edit")
        editMenu.addItem(withTitle: "Undo", action: Selector(("undo:")), keyEquivalent: "z")
        let redoItem = editMenu.addItem(withTitle: "Redo", action: Selector(("redo:")), keyEquivalent: "z")
        redoItem.keyEquivalentModifierMask = [.command, .shift]
        editMenu.addItem(.separator())
        editMenu.addItem(withTitle: "Cut", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        editMenu.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        editMenu.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        editMenu.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        editItem.submenu = editMenu
        mainMenu.addItem(editItem)
        NSApp.mainMenu = mainMenu
    }

    private func findVaultRoot() -> VaultChoice? {
        if let configured = ProcessInfo.processInfo.environment["WIKI_VAULT_ROOT"] {
            let candidate = URL(fileURLWithPath: configured, isDirectory: true)
            if isVault(candidate) {
                return VaultChoice(url: candidate, scoped: false, renewBookmark: false)
            }
        }
        if let bookmark = UserDefaults.standard.data(forKey: "PhysicsWikiVaultBookmark") {
            var isStale = false
            if let candidate = try? URL(
                resolvingBookmarkData: bookmark,
                options: [.withSecurityScope],
                relativeTo: nil,
                bookmarkDataIsStale: &isStale
            ), candidate.startAccessingSecurityScopedResource() {
                if isVault(candidate) {
                    return VaultChoice(url: candidate, scoped: true, renewBookmark: isStale)
                }
                candidate.stopAccessingSecurityScopedResource()
            }
        }

        var candidatePath = Bundle.main.bundleURL.deletingLastPathComponent().standardizedFileURL.path
        for _ in 0..<32 {
            let candidate = URL(fileURLWithPath: candidatePath, isDirectory: true)
            if isVault(candidate) {
                return VaultChoice(url: candidate, scoped: false, renewBookmark: false)
            }
            let parentPath = (candidatePath as NSString).deletingLastPathComponent
            if parentPath.isEmpty || parentPath.count >= candidatePath.count {
                break
            }
            candidatePath = parentPath
        }
        return nil
    }

    private func showVaultChooser() {
        let content = NSView(frame: NSRect(x: 0, y: 0, width: 580, height: 300))
        let title = NSTextField(labelWithString: "Open your physics wiki")
        title.font = NSFont.systemFont(ofSize: 22, weight: .semibold)
        title.alignment = .center
        let explanation = NSTextField(
            wrappingLabelWithString: "Choose the downloaded vault folder once. Physics Wiki will remember it next time."
        )
        explanation.alignment = .center
        explanation.textColor = .secondaryLabelColor
        let button = NSButton(title: "Choose vault folder…", target: self, action: #selector(chooseVaultClicked(_:)))
        button.bezelStyle = .rounded

        let stack = NSStackView(views: [title, explanation, button])
        stack.orientation = .vertical
        stack.alignment = .centerX
        stack.spacing = 18
        stack.translatesAutoresizingMaskIntoConstraints = false
        content.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.centerXAnchor.constraint(equalTo: content.centerXAnchor),
            stack.centerYAnchor.constraint(equalTo: content.centerYAnchor),
            stack.leadingAnchor.constraint(greaterThanOrEqualTo: content.leadingAnchor, constant: 30),
            stack.trailingAnchor.constraint(lessThanOrEqualTo: content.trailingAnchor, constant: -30),
            explanation.widthAnchor.constraint(lessThanOrEqualToConstant: 440)
        ])

        let window = self.window ?? NSWindow(
            contentRect: content.bounds,
            styleMask: [.titled, .closable, .miniaturizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Physics Wiki"
        window.contentView = content
        window.delegate = self
        window.center()
        window.makeKeyAndOrderFront(nil)
        self.window = window
        NSApp.activate(ignoringOtherApps: true)
    }

    @objc private func chooseVaultClicked(_ sender: Any?) {
        chooseVault()
    }

    @objc private func switchVaultClicked(_ sender: Any?) {
        chooseVault()
    }

    private func chooseVault() {
        let panel = NSOpenPanel()
        panel.message = "Choose the downloaded physics wiki folder."
        panel.prompt = "Use this folder"
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        if let vaultRoot = vaultRoot {
            panel.directoryURL = vaultRoot.deletingLastPathComponent()
        }
        let handler: (NSApplication.ModalResponse) -> Void = { [weak self] response in
            guard response == .OK, let selected = panel.url else {
                return
            }
            self?.openChosenVault(selected)
        }
        if let window = window {
            panel.beginSheetModal(for: window, completionHandler: handler)
        } else {
            panel.begin(completionHandler: handler)
        }
    }

    // The current vault stays open unless the new folder is valid and remembered.
    private func openChosenVault(_ selected: URL) {
        guard isVault(selected) else {
            showError("That folder does not contain the physics wiki. Choose the folder containing index.md and CLAUDE.md.")
            return
        }
        guard saveVaultBookmark(selected) else {
            showError("The vault folder could not be remembered. Please choose it again.")
            return
        }
        let previousScope = scopedVaultRoot
        scopedVaultRoot = selected.startAccessingSecurityScopedResource() ? selected : nil
        stopServer { [weak self] in
            previousScope?.stopAccessingSecurityScopedResource()
            guard let self = self, !self.terminationRequested else { return }
            self.startServer(vaultRoot: selected)
        }
    }

    @discardableResult
    private func saveVaultBookmark(_ vaultRoot: URL) -> Bool {
        guard let bookmark = try? vaultRoot.bookmarkData(
            options: [.withSecurityScope],
            includingResourceValuesForKeys: nil,
            relativeTo: nil
        ) else {
            return false
        }
        UserDefaults.standard.set(bookmark, forKey: "PhysicsWikiVaultBookmark")
        return true
    }

    private func isVault(_ candidate: URL) -> Bool {
        let files = FileManager.default
        return files.fileExists(atPath: candidate.appendingPathComponent("index.md").path)
            && files.fileExists(atPath: candidate.appendingPathComponent("CLAUDE.md").path)
    }

    private func waitForServer(process: Process, portFile: URL, generation: Int) {
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            for _ in 0..<100 {
                if !process.isRunning {
                    break
                }
                if let text = try? String(contentsOf: portFile, encoding: .ascii),
                   let port = Int(text.trimmingCharacters(in: .whitespacesAndNewlines)),
                   self?.serverIsReady(port: port) == true {
                    DispatchQueue.main.async {
                        guard let self = self, !self.terminationRequested, process.isRunning, generation == self.serverGeneration else {
                            return
                        }
                        self.showWindow(port: port)
                    }
                    return
                }
                Thread.sleep(forTimeInterval: 0.1)
            }
            DispatchQueue.main.async {
                guard let self = self, !self.terminationRequested, generation == self.serverGeneration else {
                    return
                }
                self.showError("The viewer did not start. See Library/Logs/Physics Wiki Viewer.log for details.")
                NSApp.terminate(nil)
            }
        }
    }

    private func serverIsReady(port: Int) -> Bool {
        guard let url = URL(string: "http://127.0.0.1:\(port)/api/health") else {
            return false
        }
        var request = URLRequest(url: url)
        request.timeoutInterval = 0.3
        let semaphore = DispatchSemaphore(value: 0)
        var ready = false
        URLSession.shared.dataTask(with: request) { _, response, _ in
            ready = (response as? HTTPURLResponse)?.statusCode == 200
            semaphore.signal()
        }.resume()
        semaphore.wait()
        return ready
    }

    private func showWindow(port: Int) {
        guard let url = URL(string: "http://127.0.0.1:\(port)/") else {
            return
        }
        let window: NSWindow
        if let existing = self.window, existing.contentView is WKWebView {
            // Switching vaults keeps the window's current size and position.
            window = existing
        } else {
            window = self.window ?? NSWindow(
                contentRect: NSRect(x: 0, y: 0, width: 1100, height: 760),
                styleMask: [.titled, .closable, .miniaturizable, .resizable],
                backing: .buffered,
                defer: false
            )
            window.styleMask.insert(.resizable)
            window.setContentSize(NSSize(width: 1280, height: 760))
            window.minSize = NSSize(width: 800, height: 400)
            window.center()
        }
        window.title = "Physics Wiki"
        window.subtitle = vaultRoot?.lastPathComponent ?? ""
        let configuration = WKWebViewConfiguration()
        configuration.userContentController.add(WindowThemeHandler(window: window), name: "appearance")
        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = self
        webView.allowsBackForwardNavigationGestures = false
        window.contentView = webView
        window.delegate = self
        window.makeKeyAndOrderFront(nil)
        self.window = window
        NSApp.activate(ignoringOtherApps: true)
        webView.load(URLRequest(url: url))
    }

    private func showStartingWindow() {
        let content = NSView(frame: NSRect(x: 0, y: 0, width: 1280, height: 760))
        let spinner = NSProgressIndicator()
        spinner.style = .spinning
        spinner.startAnimation(nil)
        let text = NSTextField(labelWithString: "Opening physics wiki…")
        text.textColor = .secondaryLabelColor
        let stack = NSStackView(views: [spinner, text])
        stack.orientation = .vertical
        stack.spacing = 16
        stack.translatesAutoresizingMaskIntoConstraints = false
        content.addSubview(stack)
        NSLayoutConstraint.activate([stack.centerXAnchor.constraint(equalTo: content.centerXAnchor),
                                     stack.centerYAnchor.constraint(equalTo: content.centerYAnchor)])
        let window = NSWindow(contentRect: content.bounds,
                              styleMask: [.titled, .closable, .miniaturizable, .resizable],
                              backing: .buffered, defer: false)
        window.title = "Physics Wiki"
        window.minSize = NSSize(width: 800, height: 400)
        window.contentView = content
        window.delegate = self
        window.center()
        window.makeKeyAndOrderFront(nil)
        self.window = window
        NSApp.activate(ignoringOtherApps: true)
    }

    private func disableElasticity(in view: NSView) {
        if let scrollView = view as? NSScrollView {
            scrollView.verticalScrollElasticity = .none
            scrollView.horizontalScrollElasticity = .none
        }
        for child in view.subviews {
            disableElasticity(in: child)
        }
    }

    // Safe to call repeatedly: when switching vaults, and again when the window
    // closes or the app quits.
    private func stopServer(completion: @escaping () -> Void = {}) {
        shutdownCompletions.append(completion)
        if shutdownInProgress { return }
        shutdownInProgress = true
        serverGeneration += 1
        let process = server
        let oldPortFile = portFile
        let log = serverLog
        server = nil
        portFile = nil
        serverLog = nil
        // Unload the page to close its persistent file-event connection before
        // asking Uvicorn to finish. Polling/reaping happens off the UI thread.
        if let webView = window?.contentView as? WKWebView {
            webView.stopLoading()
            webView.loadHTMLString("", baseURL: nil)
        }
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            if let process = process {
                if process.isRunning {
                    process.terminate()
                    for _ in 0..<24 {
                        if !process.isRunning { break }
                        Thread.sleep(forTimeInterval: 0.025)
                    }
                    if process.isRunning {
                        kill(process.processIdentifier, SIGKILL)
                    }
                    process.waitUntilExit()
                }
            }
            if let oldPortFile = oldPortFile { try? FileManager.default.removeItem(at: oldPortFile) }
            log?.closeFile()
            DispatchQueue.main.async {
                guard let self = self else { return }
                self.shutdownInProgress = false
                let callbacks = self.shutdownCompletions
                self.shutdownCompletions.removeAll()
                callbacks.forEach { $0() }
            }
        }
    }

    private func showError(_ message: String) {
        let alert = NSAlert()
        alert.messageText = "Physics Wiki could not open"
        alert.informativeText = message
        alert.alertStyle = .warning
        alert.runModal()
    }
}

@main
struct PhysicsWiki {
    static func main() {
        let application = NSApplication.shared
        let delegate = ViewerApplication()
        application.delegate = delegate
        application.run()
    }
}
