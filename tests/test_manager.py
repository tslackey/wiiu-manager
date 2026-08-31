from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wiiu_manager.catalog import load_catalog  # noqa: E402
from wiiu_manager.layout import verify_layout  # noqa: E402
from wiiu_manager.sdcard import Disk, classify_candidate, require_safe_target, validate_label  # noqa: E402
from wiiu_manager.stage import clean_junk, extract_zip, is_junk_name, stage_downloads  # noqa: E402
from wiiu_manager.util import ManagerError, copy_tree_merge  # noqa: E402


def touch(path: Path, data: bytes = b"ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


class CatalogTests(unittest.TestCase):
    def test_profiles_resolve_known_packages(self) -> None:
        catalog = load_catalog(ROOT)
        self.assertIn("base", catalog.profiles)
        self.assertIn("recommended", catalog.profiles)
        for name in ("base", "recommended", "pretendo"):
            packages = catalog.packages_for_profile(name)
            self.assertTrue(packages)
            for package in packages:
                self.assertTrue(package.filename.endswith(".zip"))

    def test_unknown_profile(self) -> None:
        catalog = load_catalog(ROOT)
        with self.assertRaises(ManagerError):
            catalog.profile("haxchi")


class LayoutTests(unittest.TestCase):
    def test_missing_files_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = verify_layout(root, "base")
            self.assertFalse(report.ok)
            self.assertIn("wiiu/payload.elf", report.missing)

    def test_complete_base_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (
                "wiiu/payload.elf",
                "wiiu/payload.rpx",
                "wiiu/payloads/default/payload.elf",
                "wiiu/payloads/nanddumper/payload.elf",
                "wiiu/environments/aroma/root.rpx",
                "wiiu/environments/aroma/modules/setup/00_mocha.rpx",
                "wiiu/environments/aroma/modules/setup/10_wums_loader.rpx",
                "wiiu/environments/aroma/modules/setup/99_autoboot.rpx",
                "wiiu/environments/aroma/plugins/AromaBasePlugin.wps",
                "wiiu/environments/aroma/plugins/homebrew_on_menu.wps",
                "wiiu/environments/aroma/plugins/regionfree.wps",
                "wiiu/environments/aroma/plugins/drc_region_free.wps",
                "wiiu/apps/AromaUpdater/AromaUpdater.wuhb",
                "wiiu/apps/PayloadLoaderInstaller.wuhb",
            ):
                touch(root / rel)
            report = verify_layout(root, "base")
            self.assertTrue(report.ok)
            self.assertEqual(report.missing, [])

    def test_wiiu_volume_label_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = verify_layout(root, "base", volume_label="wiiu")
            self.assertFalse(report.ok)
            self.assertIsNotNone(report.volume_label_warning)

    def test_nand_files_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            touch(root / "slc.bin")
            touch(root / "otp.bin")
            touch(root / "mlc.bin.part00")
            report = verify_layout(root, "base")
            self.assertEqual(set(report.nand_files), {"slc.bin", "otp.bin", "mlc.bin.part00"})


class JunkTests(unittest.TestCase):
    def test_junk_names(self) -> None:
        self.assertTrue(is_junk_name(".DS_Store"))
        self.assertTrue(is_junk_name("._payload.elf"))
        self.assertTrue(is_junk_name("__MACOSX"))
        self.assertFalse(is_junk_name("payload.elf"))

    def test_clean_junk_removes_finder_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            keep = root / "wiiu" / "payload.elf"
            touch(keep, b"payload")
            touch(root / ".DS_Store")
            touch(root / "wiiu" / "._payload.elf")
            (root / "__MACOSX").mkdir()
            touch(root / "__MACOSX" / "junk")
            removed = clean_junk(root)
            self.assertTrue(keep.exists())
            self.assertFalse((root / ".DS_Store").exists())
            self.assertFalse((root / "wiiu" / "._payload.elf").exists())
            self.assertFalse((root / "__MACOSX").exists())
            self.assertGreaterEqual(len(removed), 3)


class StageTests(unittest.TestCase):
    def test_merge_two_zips_like_the_guide(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            zips = tmp_path / "zips"
            zips.mkdir()
            a = zips / "a.zip"
            b = zips / "b.zip"
            with zipfile.ZipFile(a, "w") as archive:
                archive.writestr("wiiu/payload.elf", b"elf")
                archive.writestr("__MACOSX/._payload.elf", b"junk")
            with zipfile.ZipFile(b, "w") as archive:
                archive.writestr("wiiu/environments/aroma/root.rpx", b"rpx")
                archive.writestr("wiiu/.DS_Store", b"finder")
            sdroot = stage_downloads(download_dir=zips, sdroot=tmp_path / "sdroot", zip_paths=[a, b])
            self.assertEqual((sdroot / "wiiu" / "payload.elf").read_bytes(), b"elf")
            self.assertEqual(
                (sdroot / "wiiu" / "environments" / "aroma" / "root.rpx").read_bytes(),
                b"rpx",
            )
            self.assertFalse((sdroot / "wiiu" / ".DS_Store").exists())
            self.assertFalse((sdroot / "__MACOSX").exists())

    def test_copy_tree_merge_does_not_clobber_sibling_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dest = Path(tmp) / "dest"
            touch(src / "wiiu" / "payload.elf", b"new")
            touch(dest / "wiiu" / "payload.rpx", b"keep")
            copy_tree_merge(src, dest)
            self.assertEqual((dest / "wiiu" / "payload.elf").read_bytes(), b"new")
            self.assertEqual((dest / "wiiu" / "payload.rpx").read_bytes(), b"keep")


class DiskSafetyTests(unittest.TestCase):
    def test_internal_disk_is_rejected(self) -> None:
        disk = Disk(
            identifier="disk0",
            device="/dev/disk0",
            size_bytes=500 * 1024**3,
            name="APPLE SSD",
            internal=True,
            protocol="PCI-E",
            mountpoint="/",
        )
        warnings = classify_candidate(disk)
        self.assertTrue(any("internal" in w for w in warnings))
        with self.assertRaises(ManagerError):
            require_safe_target(disk, confirm="disk0")

    def test_confirm_must_match(self) -> None:
        disk = Disk(
            identifier="disk4",
            device="/dev/disk4",
            size_bytes=32 * 1024**3,
            name="SD Card Reader",
            internal=False,
            protocol="USB",
            mountpoint=None,
        )
        with self.assertRaises(ManagerError):
            require_safe_target(disk, confirm="disk5")
        require_safe_target(disk, confirm="disk4")

    def test_huge_disk_rejected(self) -> None:
        disk = Disk(
            identifier="disk5",
            device="/dev/disk5",
            size_bytes=1024 * 1024**3,
            name="USB HDD",
            internal=False,
            protocol="USB",
            mountpoint=None,
        )
        with self.assertRaises(ManagerError):
            require_safe_target(disk, confirm="disk5")

    def test_label_cannot_be_wiiu(self) -> None:
        with self.assertRaises(ManagerError):
            validate_label("wiiu")
        self.assertEqual(validate_label("WIIUHB"), "WIIUHB")


class ExtractZipTests(unittest.TestCase):
    def test_skips_macos_junk_inside_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "p.zip"
            dest = Path(tmp) / "out"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr("wiiu/payload.elf", b"ok")
                archive.writestr("__MACOSX/wiiu/._payload.elf", b"nope")
            extract_zip(zip_path, dest)
            self.assertTrue((dest / "wiiu" / "payload.elf").exists())
            self.assertFalse((dest / "__MACOSX").exists())


if __name__ == "__main__":
    unittest.main()
