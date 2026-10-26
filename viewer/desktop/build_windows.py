"""Build a portable Windows x64 ZIP on Windows, macOS or Linux.

Requires Python with pip, uv, Node/npm and .NET 10 SDK. Downloads official Python
embedded runtime and binary Windows wheels; never installs into the host Python.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

DESKTOP = Path(__file__).resolve().parent
WEB = DESKTOP.parent
PYTHON_VERSION = "3.13.16"
VIEWER_VERSION = "1.0.0-preview.1"


def run(args: list[str], **kwargs) -> None:
    subprocess.run(args, check=True, **kwargs)


def unpack(archive: Path, target: Path, wheel: bool = False) -> None:
    with zipfile.ZipFile(archive) as source:
        for entry in source.infolist():
            parts = PurePosixPath(entry.filename).parts
            if (not parts or ".." in parts or "\\" in entry.filename or ":" in entry.filename
                    or PurePosixPath(entry.filename).is_absolute()):
                raise ValueError(f"Unsafe archive member: {entry.filename}")
            if wheel and parts[0].endswith(".data"):
                if len(parts) < 3 or parts[1] not in {"purelib", "platlib"}:
                    continue  # Console scripts/headers are not used by the viewer.
                parts = parts[2:]
            destination = target.joinpath(*parts)
            if entry.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with source.open(entry) as src, destination.open("wb") as dst:
                    shutil.copyfileobj(src, dst)


def build(output: Path, work: Path, dotnet: str, launcher: Path | None, skip_frontend: bool) -> Path:
    package = output / "Physics Wiki Windows x64"
    archive = output / f"Physics-Wiki-Viewer-Windows-x64-v{VIEWER_VERSION}.zip"
    if package.exists() or archive.exists():
        raise FileExistsError("Output already exists. Choose a fresh output directory to preserve the previous build.")
    work.mkdir(parents=True, exist_ok=True)
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not skip_frontend:
        if not npm:
            raise RuntimeError("Node.js/npm is needed to build the viewer.")
        run([npm, "run", "build"], cwd=WEB / "frontend", env={**os.environ, "VITE_VIEWER_ONLY": "1"})
        run(["node", str(DESKTOP / "prepare_frontend.mjs")])
    dist = WEB / "frontend/dist"
    if not dist.joinpath("mathjax/tex-chtml.js").is_file():
        raise RuntimeError("Build the offline viewer frontend first (including prepare_frontend.mjs).")
    if launcher is None:
        launcher = work / "launcher"
        run([dotnet, "publish", str(DESKTOP / "windows/PhysicsWiki.csproj"), "-c", "Release", "-r", "win-x64",
             "--self-contained", "true", "-o", str(launcher),
             "-p:BaseIntermediateOutputPath=" + str(work / "obj") + os.sep,
             "-p:BaseOutputPath=" + str(work / "bin") + os.sep])
    if not launcher.joinpath("Physics Wiki.exe").is_file():
        raise RuntimeError("The Windows launcher was not produced.")
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(launcher, package, ignore=shutil.ignore_patterns("*.pdb", "*.xml", "Microsoft.Web.WebView2.Wpf.*"))
    # NuGet licenses are not all copied by `dotnet publish` automatically.
    package_root = Path(subprocess.check_output(
        [dotnet, "nuget", "locals", "global-packages", "--list"], text=True).strip().split(": ", 1)[1])
    relevant = [package_root / "microsoft.web.webview2/1.0.4258.31"]
    relevant += list(package_root.glob("microsoft.*.runtime.win-x64/*"))
    for source_package in relevant:
        for legal in source_package.iterdir():
            if legal.is_file() and legal.name.lower().startswith(("license", "notice", "thirdpartynotices")):
                target = package / "ThirdPartyNotices" / source_package.parent.name / source_package.name
                target.mkdir(parents=True, exist_ok=True)
                shutil.copy2(legal, target / legal.name)
    resources = package / "resources"
    runtime = resources / "runtime"
    runtime.mkdir(parents=True)
    python_archive = work / f"python-{PYTHON_VERSION}-embed-amd64.zip"
    if not python_archive.exists():
        url = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/{python_archive.name}"
        print("Downloading official Python embedded runtime", flush=True)
        urllib.request.urlretrieve(url, python_archive)
    unpack(python_archive, runtime)
    # Isolated embedded Python loads only the bundled backend and libraries.
    (runtime / "python313._pth").write_text(
        "python313.zip\n.\nsite-packages\n../backend\nimport site\n", encoding="utf-8")
    # Fresh download directory prevents an old wheel version from overwriting
    # the current lock's package when reusing a build cache.
    wheels = Path(tempfile.mkdtemp(prefix="wheels-", dir=work))
    # pip's cross-platform download options do not retarget environment markers.
    # Resolve for Windows with uv first, then fetch the exact wheel set without
    # re-resolving dependencies against this build machine's OS.
    lock = DESKTOP / "windows/requirements.lock"
    if not lock.exists():
        raise RuntimeError("Generate windows/requirements.lock using the command in windows/BUILDING.md.")
    run([sys.executable, "-m", "pip", "download", "--disable-pip-version-check", "--only-binary=:all:",
         "--platform", "win_amd64", "--python-version", "313", "--implementation", "cp", "--abi", "cp313",
         "--no-deps", "--require-hashes", "--dest", str(wheels), "--cache-dir", str(work / "pip-cache"), "-r", str(lock)])
    for wheel in sorted(wheels.glob("*.whl")):
        unpack(wheel, runtime / "site-packages", wheel=True)
    source = WEB / "backend/app"
    for path in source.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        target = resources / "backend/app" / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    shutil.copytree(dist, resources / "frontend/dist")
    (resources / "desktop").mkdir()
    for name in ["server_entry.py", "windows/smoke_test.py"]:
        shutil.copy2(DESKTOP / name, resources / "desktop" / Path(name).name)
    shutil.copy2(DESKTOP / "windows/README.txt", package / "README.txt")
    shutil.copy2(lock, package / "DEPENDENCIES.txt")
    shutil.copy2(DESKTOP / "windows/Test Windows.cmd", package / "Test Windows.cmd")
    metadata = {
        "platform": "Windows x64", "viewer_version": VIEWER_VERSION, "python": PYTHON_VERSION,
        "python_archive_sha256": hashlib.sha256(python_archive.read_bytes()).hexdigest(),
        "wheels": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(wheels.glob("*.whl"))},
        "dotnet_sdk": subprocess.check_output([dotnet, "--version"], text=True).strip(),
        "windows_native_tested": False,
    }
    (package / "BUILD.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    # Hash every shipped file so an extracted archive can be verified exactly.
    hashes = {p.relative_to(package).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(package.rglob("*")) if p.is_file()}
    (package / "SHA256SUMS.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    shutil.make_archive(str(archive.with_suffix("")), "zip", root_dir=output, base_dir=package.name)
    print("Built " + str(archive), flush=True)
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--dotnet", default="dotnet")
    parser.add_argument("--launcher", type=Path, help="Use an already-published Windows x64 launcher")
    parser.add_argument("--skip-frontend", action="store_true")
    args = parser.parse_args()
    if args.work:
        build(args.output.resolve(), args.work.resolve(), args.dotnet, args.launcher, args.skip_frontend)
    else:
        with tempfile.TemporaryDirectory(prefix="physics-wiki-windows-") as temporary:
            build(args.output.resolve(), Path(temporary), args.dotnet, args.launcher, args.skip_frontend)
