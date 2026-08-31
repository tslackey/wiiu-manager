from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from wiiu_manager.layout import NAND_ROOT_FILES
from wiiu_manager.paths import backups_dir
from wiiu_manager.util import ManagerError, ensure_dir, eprint, human_bytes


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup_sd(source: Path, dest_parent: Path | None = None) -> Path:
    if not source.exists():
        raise ManagerError(f"SD path {source} does not exist")
    dest_parent = dest_parent or backups_dir() / "sd"
    dest = dest_parent / f"sd-{_stamp()}"
    eprint(f"Backing up SD {source} -> {dest}")
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns("._*", ".DS_Store", "__MACOSX"))
    return dest


def collect_nand(source: Path, dest_parent: Path | None = None, *, delete_from_sd: bool = False) -> Path:
    found: list[Path] = []
    for name in NAND_ROOT_FILES:
        path = source / name
        if path.exists():
            found.append(path)
    found.extend(sorted(source.glob("mlc.bin.part*")))
    if not found:
        raise ManagerError(
            "No NAND dump files found on that volume. Expected slc.bin, slccmpt.bin, seeprom.bin, otp.bin "
            "(and optional mlc.bin.part*) on the SD root after nanddumper finishes."
        )
    dest = (dest_parent or backups_dir() / "nand") / f"nand-{_stamp()}"
    ensure_dir(dest)
    for path in found:
        target = dest / path.name
        eprint(f"Copying {path.name} ({human_bytes(path.stat().st_size)})")
        shutil.copy2(path, target)
        # Verify copy size before optional delete.
        if target.stat().st_size != path.stat().st_size:
            raise ManagerError(f"Copy size mismatch for {path.name}; leaving the SD file in place")
    readme = dest / "README.txt"
    readme.write_text(
        "This NAND backup is unique to one Wii U. Keep it private.\n"
        "Files: slc.bin, slccmpt.bin, seeprom.bin, otp.bin, optional mlc.bin.part*.\n"
        "Restoring a NAND backup needs ISFShax or hardware tools. Do not share otp.bin.\n",
        encoding="utf-8",
    )
    if delete_from_sd:
        for path in found:
            path.unlink()
            eprint(f"Deleted {path.name} from SD after verified copy")
    eprint(f"NAND backup stored at {dest}")
    return dest
