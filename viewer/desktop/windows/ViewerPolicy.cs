using System.Text.Json;

namespace PhysicsWiki;

internal static class ViewerPolicy
{
    public static bool IsVault(string? path) => !string.IsNullOrWhiteSpace(path)
        && File.Exists(Path.Combine(path, "index.md")) && File.Exists(Path.Combine(path, "CLAUDE.md"));

    public static string? FindVault(string executableDirectory, string? saved, string? configured)
    {
        foreach (var path in new[] { configured, saved })
            if (IsVault(path)) return Path.GetFullPath(path!);
        for (var dir = new DirectoryInfo(executableDirectory); dir != null; dir = dir.Parent)
            if (IsVault(dir.FullName)) return dir.FullName;
        return null;
    }

    public static bool IsLocalPage(string? url, Uri? server) => server != null
        && Uri.TryCreate(url, UriKind.Absolute, out var target)
        && target.Scheme == Uri.UriSchemeHttp && target.Host == "127.0.0.1"
        && target.Port == server.Port && string.IsNullOrEmpty(target.UserInfo);

    public static bool IsExternalLink(string? url) => Uri.TryCreate(url, UriKind.Absolute, out var uri)
        && (uri.Scheme == Uri.UriSchemeHttp || uri.Scheme == Uri.UriSchemeHttps);

    public static int ParsePort(string text) => int.TryParse(text.Trim(), out var port) && port is > 0 and <= 65535
        ? port : throw new InvalidDataException("The local server returned an invalid port.");
}

internal sealed record ViewerPreferences(string? Vault = null, string? Theme = null);

internal sealed class PreferencesStore(string directory)
{
    private string FileName => Path.Combine(directory, "preferences.json");
    public ViewerPreferences Load()
    {
        try { return JsonSerializer.Deserialize<ViewerPreferences>(File.ReadAllText(FileName)) ?? new(); }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or JsonException) { return new(); }
    }
    public void Save(ViewerPreferences preferences)
    {
        Directory.CreateDirectory(directory);
        var temporary = FileName + ".tmp";
        File.WriteAllText(temporary, JsonSerializer.Serialize(preferences));
        File.Move(temporary, FileName, overwrite: true);
    }
}
