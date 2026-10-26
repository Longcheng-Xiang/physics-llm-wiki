using System.Diagnostics;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Text.Json;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace PhysicsWiki;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        ApplicationConfiguration.Initialize();
        using var instance = new Mutex(false, @"Local\PhysicsWiki.Viewer", out var first);
        if (!first)
        {
            MessageBox.Show("Physics Wiki is already open. Switch to its existing window.", "Physics Wiki");
            return;
        }
        Application.Run(new ViewerWindow());
    }
}

internal sealed class ViewerWindow : Form
{
    private readonly string dataDirectory = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Physics Wiki");
    private readonly CancellationTokenSource lifetime = new();
    private readonly Label status = new() { Dock = DockStyle.Fill, TextAlign = ContentAlignment.MiddleCenter,
        Text = "Opening physics wiki…", AutoEllipsis = true };
    private readonly Button choose = new() { Text = "Choose vault folder…", AutoSize = true, Dock = DockStyle.Bottom };
    private readonly MenuStrip menu = new();
    private readonly Panel content = new() { Dock = DockStyle.Fill };
    private readonly ToolStripMenuItem switchItem = new("Switch Vault…");
    private readonly PreferencesStore preferencesStore;
    private ViewerPreferences preferences;
    private WebView2? browser;
    private CoreWebView2Environment? browserEnvironment;
    private Process? server;
    private ServerJob? serverJob;
    private string? portFile;
    private StreamWriter? serverLog;
    private readonly object logLock = new();
    private Uri? serverUri;
    private bool busy, closing, cleanupComplete;
    private int vaultChoiceGeneration;

    public ViewerWindow()
    {
        preferencesStore = new(dataDirectory);
        preferences = preferencesStore.Load();
        Text = "Physics Wiki";
        Icon = System.Drawing.Icon.ExtractAssociatedIcon(Application.ExecutablePath);
        ClientSize = new(1280, 760);
        MinimumSize = new(800, 400);
        StartPosition = FormStartPosition.CenterScreen;
        var layout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 1, RowCount = 2,
            Margin = Padding.Empty, Padding = Padding.Empty };
        layout.RowStyles.Add(new RowStyle(SizeType.AutoSize));
        layout.RowStyles.Add(new RowStyle(SizeType.Percent, 100));
        menu.Dock = DockStyle.Fill;
        layout.Controls.Add(menu, 0, 0); layout.Controls.Add(content, 0, 1);
        Controls.Add(layout); content.Controls.Add(status); content.Controls.Add(choose);
        MainMenuStrip = menu;
        var file = new ToolStripMenuItem("&File");
        switchItem.ShortcutKeys = Keys.Control | Keys.O;
        switchItem.Click += async (_, _) => await ChooseVaultAsync();
        file.DropDownItems.Add(switchItem);
        var quit = new ToolStripMenuItem("Exit", null, (_, _) => Close()) { ShortcutKeys = Keys.Alt | Keys.F4 };
        file.DropDownItems.Add(quit); menu.Items.Add(file);
        var edit = new ToolStripMenuItem("&Edit");
        AddEdit(edit, "Undo", "Ctrl+Z", "z", false);
        AddEdit(edit, "Redo", "Ctrl+Shift+Z", "z", true);
        edit.DropDownItems.Add(new ToolStripSeparator());
        AddEdit(edit, "Cut", "Ctrl+X", "x", false);
        AddEdit(edit, "Copy", "Ctrl+C", "c", false);
        AddEdit(edit, "Paste", "Ctrl+V", "v", false);
        AddEdit(edit, "Select All", "Ctrl+A", "a", false);
        menu.Items.Add(edit);
        choose.Click += async (_, _) => await ChooseVaultAsync();
        Shown += async (_, _) => await InitializeAsync();
        FormClosing += OnClosing;
        ApplyTheme(preferences.Theme ?? "light");
    }

    private void AddEdit(ToolStripMenuItem menuItem, string title, string shortcut, string key, bool shift)
    {
        // Native WebView2 handles Ctrl shortcuts itself; menu clicks dispatch the
        // same input instead of replacing WebKit/Chromium clipboard semantics.
        var item = new ToolStripMenuItem(title) { ShortcutKeyDisplayString = shortcut };
        item.Click += async (_, _) => {
            if (browser?.CoreWebView2 is not { } core || closing) return;
            browser.Focus();
            try
            {
                var parameters = new { type = "keyDown", key, code = "Key" + key.ToUpperInvariant(),
                    windowsVirtualKeyCode = (int)char.ToUpperInvariant(key[0]), modifiers = shift ? 10 : 2 };
                await core.CallDevToolsProtocolMethodAsync("Input.dispatchKeyEvent", JsonSerializer.Serialize(parameters));
                await core.CallDevToolsProtocolMethodAsync("Input.dispatchKeyEvent", JsonSerializer.Serialize(new {
                    type = "keyUp", key, code = parameters.code, windowsVirtualKeyCode = parameters.windowsVirtualKeyCode,
                    modifiers = parameters.modifiers }));
            }
            catch (Exception error) { if (!closing) ShowFailure(error); }
        };
        menuItem.DropDownItems.Add(item);
    }

    private async Task InitializeAsync()
    {
        var generation = vaultChoiceGeneration;
        try
        {
            var vault = await Task.Run(() => ViewerPolicy.FindVault(AppContext.BaseDirectory,
                preferences.Vault, Environment.GetEnvironmentVariable("WIKI_VAULT_ROOT")));
            if (closing || generation != vaultChoiceGeneration) return;
            if (vault == null) { status.Text = "Choose the wiki folder containing index.md and CLAUDE.md."; return; }
            await OpenVaultAsync(vault);
        }
        catch (Exception error) { if (!closing && generation == vaultChoiceGeneration) ShowFailure(error); }
    }

    private async Task ChooseVaultAsync()
    {
        if (busy || closing) return;
        // A late automatic folder lookup must not replace a manual choice.
        vaultChoiceGeneration++;
        using var dialog = new FolderBrowserDialog { Description = "Choose your physics wiki folder",
            UseDescriptionForTitle = true, ShowNewFolderButton = false,
            SelectedPath = preferences.Vault ?? "" };
        if (dialog.ShowDialog(this) != DialogResult.OK)
        {
            if (server == null) status.Text = "Choose the wiki folder containing index.md and CLAUDE.md.";
            return;
        }
        if (!await Task.Run(() => ViewerPolicy.IsVault(dialog.SelectedPath)))
        {
            if (!closing) MessageBox.Show(this, "Choose the folder containing index.md and CLAUDE.md.", "Physics Wiki");
            return;
        }
        if (!closing) await OpenVaultAsync(dialog.SelectedPath);
    }

    private async Task OpenVaultAsync(string vault)
    {
        if (busy || closing) return;
        busy = true; choose.Enabled = switchItem.Enabled = false;
        try
        {
            var updated = preferences with { Vault = Path.GetFullPath(vault) };
            preferencesStore.Save(updated); preferences = updated;
            browser?.Dispose(); browser = null; serverUri = null;
            await StopServerAsync();
            lifetime.Token.ThrowIfCancellationRequested();
            status.Text = "Opening physics wiki…"; status.Visible = true; choose.Visible = false;
            await StartServerAsync(vault, lifetime.Token);
            lifetime.Token.ThrowIfCancellationRequested();
            browserEnvironment ??= await CoreWebView2Environment.CreateAsync(null, Path.Combine(dataDirectory, "WebView2"));
            lifetime.Token.ThrowIfCancellationRequested();
            var view = new WebView2 { Dock = DockStyle.Fill, DefaultBackgroundColor = BackColor };
            browser = view; content.Controls.Add(view); view.BringToFront();
            await view.EnsureCoreWebView2Async(browserEnvironment);
            lifetime.Token.ThrowIfCancellationRequested();
            var core = view.CoreWebView2;
            core.Settings.AreDefaultScriptDialogsEnabled = false;
            core.Settings.IsStatusBarEnabled = false;
            core.Settings.AreDevToolsEnabled = false;
            core.Settings.AreBrowserAcceleratorKeysEnabled = false;
            // Editing shortcuts (Ctrl+C/V/A/X/Z) are independent of browser-only
            // accelerator keys such as reload and devtools.
            core.PermissionRequested += (_, args) => args.State = CoreWebView2PermissionState.Deny;
            core.DownloadStarting += (_, args) => args.Cancel = true;
            core.NavigationStarting += (_, args) => {
                if (ViewerPolicy.IsLocalPage(args.Uri, serverUri)) return;
                args.Cancel = true;
                OpenExternal(args.Uri);
            };
            core.NewWindowRequested += (_, args) => { args.Handled = true; OpenExternal(args.Uri); };
            core.WebMessageReceived += (_, args) => {
                if (!ViewerPolicy.IsLocalPage(args.Source, serverUri)) return;
                try
                {
                    using var message = JsonDocument.Parse(args.WebMessageAsJson);
                    if (message.RootElement.GetProperty("type").GetString() != "appearance") return;
                    var theme = message.RootElement.GetProperty("theme").GetString();
                    if (theme is not ("light" or "dark")) return;
                    ApplyTheme(theme);
                    preferences = preferences with { Theme = theme };
                    preferencesStore.Save(preferences);
                }
                catch (Exception error) when (error is JsonException or KeyNotFoundException or InvalidOperationException
                    or IOException or UnauthorizedAccessException) { Log(error.Message); }
            };
            core.ProcessFailed += (_, _) => { if (!closing && !busy) ShowFailure(new IOException("The viewer browser stopped. Use File → Switch Vault to reopen it.")); };
            if (preferences.Theme is "light" or "dark")
                await core.AddScriptToExecuteOnDocumentCreatedAsync(
                    "localStorage.setItem('physics-wiki:theme'," + JsonSerializer.Serialize(preferences.Theme) + ");");
            Text = "Physics Wiki — " + new DirectoryInfo(vault).Name;
            core.Navigate(serverUri!.ToString());
            status.Visible = false;
        }
        catch (OperationCanceledException) when (closing) { }
        catch (Exception error)
        {
            browser?.Dispose(); browser = null; serverUri = null;
            await StopServerAsync();
            if (!closing) ShowFailure(error);
        }
        finally { busy = false; if (!closing) choose.Enabled = switchItem.Enabled = true; }
    }

    private async Task StartServerAsync(string vault, CancellationToken cancellation)
    {
        var resources = Path.Combine(AppContext.BaseDirectory, "resources");
        var executable = Path.Combine(resources, "runtime", "python.exe");
        if (!File.Exists(executable)) throw new FileNotFoundException("The Python runtime is missing. Extract the entire downloaded ZIP before opening Physics Wiki.");
        portFile = Path.Combine(Path.GetTempPath(), "physics-wiki-" + Guid.NewGuid() + ".port");
        Directory.CreateDirectory(dataDirectory);
        serverLog = new StreamWriter(Path.Combine(dataDirectory, "viewer.log"), append: true) { AutoFlush = true };
        var info = new ProcessStartInfo(executable) { UseShellExecute = false, CreateNoWindow = true,
            RedirectStandardError = true, RedirectStandardOutput = true, WorkingDirectory = Path.GetTempPath() };
        info.ArgumentList.Add(Path.Combine(resources, "desktop", "server_entry.py"));
        info.Environment["WIKI_VAULT_ROOT"] = Path.GetFullPath(vault);
        info.Environment["WIKI_DESKTOP_PORT_FILE"] = portFile;
        info.Environment["WIKI_DESKTOP_VIEWER_ONLY"] = "1";
        info.Environment["WIKI_FRONTEND_DIST"] = Path.Combine(resources, "frontend", "dist");
        info.Environment["PYTHONUNBUFFERED"] = "1";
        serverJob = new ServerJob();
        server = new Process { StartInfo = info };
        server.OutputDataReceived += (_, args) => { if (args.Data != null) Log(args.Data); };
        server.ErrorDataReceived += (_, args) => { if (args.Data != null) Log(args.Data); };
        if (!server.Start()) throw new IOException("The local server could not start.");
        serverJob.Add(server);
        server.BeginOutputReadLine(); server.BeginErrorReadLine();
        var startedServer = server;
        startedServer.EnableRaisingEvents = true;
        startedServer.Exited += (_, _) => {
            if (closing || !IsHandleCreated || IsDisposed) return;
            try { BeginInvoke(() => {
                if (!closing && !busy && ReferenceEquals(server, startedServer))
                    ShowFailure(new IOException("The local server stopped. Use File → Switch Vault to reopen it. See " + Path.Combine(dataDirectory, "viewer.log")));
            }); } catch (InvalidOperationException) { }
        };
        using var http = new HttpClient { Timeout = TimeSpan.FromMilliseconds(750) };
        var deadline = Stopwatch.StartNew();
        while (deadline.Elapsed < TimeSpan.FromSeconds(30))
        {
            cancellation.ThrowIfCancellationRequested();
            if (server.HasExited) throw new IOException("The local server stopped during startup. See " + Path.Combine(dataDirectory, "viewer.log"));
            try
            {
                if (File.Exists(portFile))
                {
                    var port = ViewerPolicy.ParsePort(await File.ReadAllTextAsync(portFile, cancellation));
                    var uri = new Uri($"http://127.0.0.1:{port}/");
                    using var response = await http.GetAsync(new Uri(uri, "api/health"), cancellation);
                    response.EnsureSuccessStatusCode();
                    using var health = JsonDocument.Parse(await response.Content.ReadAsStringAsync(cancellation));
                    if (health.RootElement.GetProperty("viewer_only").GetBoolean()) { serverUri = uri; return; }
                }
            }
            catch (Exception error) when (error is IOException or HttpRequestException or JsonException
                or TaskCanceledException && !cancellation.IsCancellationRequested) { }
            await Task.Delay(100, cancellation);
        }
        throw new TimeoutException("The local server did not become ready. See " + Path.Combine(dataDirectory, "viewer.log"));
    }

    private async Task StopServerAsync()
    {
        var process = server; server = null;
        var job = serverJob; serverJob = null;
        var port = portFile; portFile = null;
        await Task.Run(() => {
            try
            {
                if (process is { HasExited: false }) { process.Kill(entireProcessTree: true); process.WaitForExit(2000); }
            }
            catch (Exception error) when (error is InvalidOperationException or System.ComponentModel.Win32Exception) { }
            finally { job?.Dispose(); process?.Dispose(); }
        });
        lock (logLock) { serverLog?.Dispose(); serverLog = null; }
        if (port != null) { try { File.Delete(port); } catch (Exception error) when (error is IOException or UnauthorizedAccessException) { } }
    }

    private async void OnClosing(object? sender, FormClosingEventArgs args)
    {
        if (cleanupComplete) return;
        args.Cancel = true;
        if (closing) return;
        closing = true; lifetime.Cancel(); Hide();
        browser?.Dispose(); browser = null;
        await StopServerAsync();
        cleanupComplete = true; Close();
    }

    private void Log(string message)
    {
        lock (logLock) { try { serverLog?.WriteLine(message); } catch (IOException) { } }
    }
    private void ShowFailure(Exception error)
    {
        status.Text = error is WebView2RuntimeNotFoundException
            ? "Microsoft Edge WebView2 Runtime is required. Get it from developer.microsoft.com/microsoft-edge/webview2/."
            : error.Message;
        status.Visible = true; status.BringToFront(); menu.BringToFront(); choose.Visible = true; choose.BringToFront();
        MessageBox.Show(this, status.Text, "Physics Wiki", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
    private void OpenExternal(string url)
    {
        if (!ViewerPolicy.IsExternalLink(url)) return;
        try { Process.Start(new ProcessStartInfo(url) { UseShellExecute = true }); }
        catch (System.ComponentModel.Win32Exception error) { if (!closing) ShowFailure(error); }
    }
    private void ApplyTheme(string theme)
    {
        var dark = theme == "dark";
        BackColor = status.BackColor = menu.BackColor = dark ? Color.FromArgb(38, 38, 38) : Color.FromArgb(246, 246, 246);
        ForeColor = status.ForeColor = menu.ForeColor = dark ? Color.Gainsboro : Color.FromArgb(34, 34, 34);
        foreach (ToolStripItem item in menu.Items) item.ForeColor = ForeColor;
        var enabled = dark ? 1 : 0;
        if (IsHandleCreated) DwmSetWindowAttribute(Handle, 20, ref enabled, sizeof(int));
        if (browser?.CoreWebView2 is { } core)
            core.Profile.PreferredColorScheme = dark ? CoreWebView2PreferredColorScheme.Dark : CoreWebView2PreferredColorScheme.Light;
    }
    protected override void OnHandleCreated(EventArgs e) { base.OnHandleCreated(e); ApplyTheme(preferences.Theme ?? "light"); }
    [DllImport("dwmapi.dll")]
    private static extern int DwmSetWindowAttribute(IntPtr window, int attribute, ref int value, int size);
}
