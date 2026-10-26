import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("build_windows", Path(__file__).resolve().parents[2] / "build_windows.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ArchiveExtractionTests(unittest.TestCase):
    def test_wheel_library_data_is_relocated_and_console_scripts_are_skipped(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            with zipfile.ZipFile(root / "wheel.zip", "w") as archive:
                archive.writestr("example/module.py", "value = 1")
                archive.writestr("example.data/platlib/native.pyd", b"binary")
                archive.writestr("example.data/purelib/extra.py", "value = 2")
                archive.writestr("example.data/scripts/console.exe", b"unused")
            builder.unpack(root / "wheel.zip", root / "libraries", wheel=True)
            self.assertEqual((root / "libraries/native.pyd").read_bytes(), b"binary")
            self.assertTrue((root / "libraries/extra.py").is_file())
            self.assertTrue((root / "libraries/example/module.py").is_file())
            self.assertFalse((root / "libraries/example.data").exists())

    def test_archive_paths_cannot_escape_on_either_windows_or_posix(self):
        for path in ["../escape", "/absolute", "C:/drive", r"..\escape", r"folder\..\escape"]:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as name:
                root = Path(name)
                with zipfile.ZipFile(root / "archive.zip", "w") as archive:
                    archive.writestr(path, b"outside")
                with self.assertRaises(ValueError):
                    builder.unpack(root / "archive.zip", root / "output")


if __name__ == "__main__":
    unittest.main()
