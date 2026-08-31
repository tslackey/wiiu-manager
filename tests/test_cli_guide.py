from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wiiu_manager.cli import main  # noqa: E402
from wiiu_manager.console import next_key  # noqa: E402
from wiiu_manager.guide import next_steps_text  # noqa: E402
from wiiu_manager.nand import collect_nand  # noqa: E402
from wiiu_manager.util import ManagerError  # noqa: E402


class GuideTests(unittest.TestCase):
    def test_first_step_is_power(self) -> None:
        data = {
            "nickname": "black-deluxe",
            "model": "WUP-101",
            "region": "NA",
            "firmware": None,
            "progress": {},
        }
        self.assertEqual(next_key(data), "console_powers_on")
        text = next_steps_text(data)
        self.assertIn("powers on", text.lower())
        self.assertIn("https://wiiu.hacks.guide", text)

    def test_nand_comes_before_payloadloader(self) -> None:
        data = {
            "nickname": "black-deluxe",
            "model": "WUP-101",
            "region": "NA",
            "firmware": "5.5.6",
            "progress": {
                "console_powers_on": True,
                "firmware_recorded": True,
                "sd_prepared": True,
                "entry_point_ran": True,
            },
        }
        self.assertEqual(next_key(data), "nand_backed_up")
        text = next_steps_text(data)
        self.assertIn("nand-backup", text)


class NandCollectTests(unittest.TestCase):
    def test_collect_copies_and_optionally_deletes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sd = Path(tmp) / "sd"
            backups = Path(tmp) / "backups"
            sd.mkdir()
            (sd / "slc.bin").write_bytes(b"slc-data")
            (sd / "otp.bin").write_bytes(b"otp-data")
            dest = collect_nand(sd, dest_parent=backups, delete_from_sd=True)
            self.assertTrue((dest / "slc.bin").exists())
            self.assertEqual((dest / "otp.bin").read_bytes(), b"otp-data")
            self.assertFalse((sd / "slc.bin").exists())
            self.assertTrue((dest / "README.txt").exists())

    def test_missing_nand_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ManagerError):
                collect_nand(Path(tmp), dest_parent=Path(tmp) / "b")


class CliSmokeTests(unittest.TestCase):
    def test_doctor_succeeds(self) -> None:
        self.assertEqual(main(["doctor"]), 0)

    def test_next_prints_without_console_json(self) -> None:
        self.assertEqual(main(["next"]), 0)

    def test_verify_missing_path_fails(self) -> None:
        self.assertEqual(main(["verify", "/tmp/definitely-missing-wiiu-sd-root"]), 1)


class FetchResolveTests(unittest.TestCase):
    def test_github_asset_matching(self) -> None:
        from wiiu_manager.catalog import Package
        from wiiu_manager.fetch import resolve_download_url

        package = Package(
            id="savemii",
            kind="github-release",
            description="",
            filename="savemii-aroma.zip",
            repo="w3irDv/savemii",
            asset_prefix="SaveMiiProcessMod-Aroma",
            asset_suffix=".zip",
        )
        fake = {
            "assets": [
                {
                    "name": "SaveMiiProcessMod-HBL.zip",
                    "browser_download_url": "https://example.invalid/hbl.zip",
                },
                {
                    "name": "SaveMiiProcessMod-Aroma.zip",
                    "browser_download_url": "https://example.invalid/aroma.zip",
                },
            ]
        }
        with mock.patch("wiiu_manager.fetch.http_json", return_value=fake):
            url, filename = resolve_download_url(package)
        self.assertEqual(url, "https://example.invalid/aroma.zip")
        self.assertEqual(filename, "savemii-aroma.zip")


if __name__ == "__main__":
    unittest.main()
