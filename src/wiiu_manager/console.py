from __future__ import annotations

import shutil
from pathlib import Path

from wiiu_manager.paths import console_example_path, console_path, repo_root
from wiiu_manager.util import ManagerError, dump_json, is_linux, is_macos, load_json, which


PROGRESS_ORDER = (
    "console_powers_on",
    "firmware_recorded",
    "sd_prepared",
    "entry_point_ran",
    "nand_backed_up",
    "payloadloader_installed",
    "aroma_autoboot",
    "updates_blocked",
    "extras_installed",
    "vwii_modded",
)


def load_console(root: Path | None = None) -> dict:
    path = console_path(root)
    if not path.exists():
        example = console_example_path(root)
        if not example.exists():
            raise ManagerError("Missing config/console.example.json")
        data = load_json(example)
        if not isinstance(data, dict):
            raise ManagerError("console.example.json is invalid")
        return data
    data = load_json(path)
    if not isinstance(data, dict):
        raise ManagerError(f"Invalid console profile at {path}")
    return data


def save_console(data: dict, root: Path | None = None) -> Path:
    path = console_path(root)
    dump_json(path, data)
    return path


def init_console(root: Path | None = None, *, force: bool = False) -> Path:
    dest = console_path(root)
    if dest.exists() and not force:
        return dest
    shutil.copy2(console_example_path(root), dest)
    return dest


def mark_progress(key: str, value: bool = True, root: Path | None = None) -> dict:
    if key not in PROGRESS_ORDER:
        known = ", ".join(PROGRESS_ORDER)
        raise ManagerError(f"Unknown progress key {key!r}. Known: {known}")
    data = load_console(root)
    progress = data.setdefault("progress", {})
    progress[key] = bool(value)
    save_console(data, root)
    return data


def next_key(data: dict) -> str | None:
    progress = data.get("progress") or {}
    for key in PROGRESS_ORDER:
        if not progress.get(key):
            return key
    return None


def doctor_checks() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    py_ok = True
    checks.append(("python3", py_ok, "Python 3 is available"))
    curl = which("curl")
    checks.append(("curl", curl is not None, "curl is used to download official Aroma packages"))
    unzip = which("unzip")
    checks.append(("unzip", unzip is not None, "unzip is optional; Python zipfile is used either way"))
    if is_macos():
        checks.append(("diskutil", which("diskutil") is not None, "macOS diskutil is required to format the SD card"))
        volumes = Path("/Volumes")
        checks.append(("/Volumes", volumes.is_dir(), "Expected macOS /Volumes mount point"))
    elif is_linux():
        checks.append(("lsblk", which("lsblk") is not None, "lsblk lists removable disks"))
        checks.append(
            ("mkfs.vfat", which("mkfs.vfat") is not None or which("mkfs.fat") is not None,
             "dosfstools optional unless you format the SD from Linux"),
        )
    root = repo_root()
    checks.append(("packages.json", (root / "config" / "packages.json").exists(), "Package catalog present"))
    checks.append(
        ("console.example.json", (root / "config" / "console.example.json").exists(), "Console profile template present")
    )
    return checks
