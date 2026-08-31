"""Optional live download test. Enable with WIIU_LIVE_FETCH=1."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wiiu_manager.catalog import load_catalog  # noqa: E402
from wiiu_manager.fetch import fetch_packages  # noqa: E402
from wiiu_manager.layout import verify_layout  # noqa: E402
from wiiu_manager.stage import stage_downloads  # noqa: E402


@unittest.skipUnless(os.environ.get("WIIU_LIVE_FETCH") == "1", "set WIIU_LIVE_FETCH=1 to hit aroma.foryour.cafe")
class LiveFetchTests(unittest.TestCase):
    def test_recommended_profile_stages_a_valid_sd_tree(self) -> None:
        catalog = load_catalog(ROOT)
        packages = catalog.packages_for_profile("recommended")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            downloads = tmp_path / "downloads"
            sdroot = tmp_path / "sdroot"
            fetch_packages(packages, downloads)
            staged = stage_downloads(download_dir=downloads, sdroot=sdroot)
            report = verify_layout(staged, "recommended")
            self.assertTrue(report.ok, report.summary_lines())
            self.assertEqual(report.junk, [])


if __name__ == "__main__":
    unittest.main()
