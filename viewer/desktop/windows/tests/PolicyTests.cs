using PhysicsWiki;

var root = Path.Combine(Path.GetTempPath(), "physics-wiki-policy-" + Guid.NewGuid());
Directory.CreateDirectory(root);
try
{
    void Check(bool condition, string label) { if (!condition) throw new Exception(label); }
    var saved = Path.Combine(root, "saved é 中文");
    var configured = Path.Combine(root, "configured");
    foreach (var folder in new[] { saved, configured })
    {
        Directory.CreateDirectory(folder);
        File.WriteAllText(Path.Combine(folder, "index.md"), "# Index");
        File.WriteAllText(Path.Combine(folder, "CLAUDE.md"), "# Instructions");
    }
    Check(!ViewerPolicy.IsVault(root), "incomplete vault rejected");
    Check(ViewerPolicy.IsVault(saved), "Unicode vault recognized");
    Check(ViewerPolicy.FindVault(root, saved, configured) == configured, "configured vault first");
    Check(ViewerPolicy.FindVault(root, saved, "missing") == saved, "invalid configured vault falls back");
    var nested = Path.Combine(configured, "tools", "viewer"); Directory.CreateDirectory(nested);
    Check(ViewerPolicy.FindVault(nested, "missing", null) == configured, "parent vault discovered");
    Check(ViewerPolicy.FindVault(root, null, null) == null, "no vault returns chooser state");
    var store = new PreferencesStore(Path.Combine(root, "settings"));
    Check(store.Load() == new ViewerPreferences(), "missing preferences accepted");
    var original = new ViewerPreferences(saved, "dark"); store.Save(original);
    Check(store.Load() == original, "preferences round trip preserves Unicode paths and theme");
    File.WriteAllText(Path.Combine(root, "settings", "preferences.json"), "invalid JSON");
    Check(store.Load() == new ViewerPreferences(), "corrupt preferences recover");
    var local = new Uri("http://127.0.0.1:4173/");
    Check(ViewerPolicy.IsLocalPage("http://127.0.0.1:4173/api/health", local), "same origin accepted");
    foreach (var url in new[] { "http://127.0.0.1:9999/", "https://127.0.0.1:4173/", "http://localhost:4173/",
             "http://127.0.0.1.evil.example:4173/", "http://name@127.0.0.1:4173/", "file:///tmp/local", "javascript:alert(1)" })
        Check(!ViewerPolicy.IsLocalPage(url, local), "different origin rejected: " + url);
    Check(!ViewerPolicy.IsLocalPage(local.ToString(), null), "no active server rejects messages");
    Check(ViewerPolicy.IsExternalLink("https://example.com/note"), "HTTPS link supported");
    Check(!ViewerPolicy.IsExternalLink("file:///C:/Windows/test.exe"), "file launch rejected");
    Check(!ViewerPolicy.IsExternalLink("javascript:alert(1)"), "script launch rejected");
    Check(ViewerPolicy.ParsePort(" 4173\n") == 4173, "port whitespace accepted");
    foreach (var port in new[] { "0", "-1", "65536", "not a port", "1:80" })
    {
        try { ViewerPolicy.ParsePort(port); throw new Exception("invalid port accepted: " + port); }
        catch (InvalidDataException) { }
    }
    Console.WriteLine("PASS: vault discovery/recovery, Unicode preferences, exact-origin checks, links and port validation.");
}
finally { Directory.Delete(root, recursive: true); }
