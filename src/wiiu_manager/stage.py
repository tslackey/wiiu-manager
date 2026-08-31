from __future__ import annotations

import zipfile
from pathlib import Path

from wiiu_manager.paths import downloads_dir, sdroot_dir
from wiiu_manager.util import ManagerError, copy_tree_merge, ensure_dir, eprint


MACOS_JUNK_NAMES = {
    ".DS_Store",
    ".AppleDouble",
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
    ".VolumeIcon.icns",
    "._.VolumeIcon.icns",
}


def is_junk_name(name: str) -> bool:
    if name in MACOS_JUNK_NAMES:
        return True
    if name.startswith("._"):
        return True
    if name == "__MACOSX":
        return True
    return False


def clean_junk(root: Path) -> list[Path]:
    """Remove Finder/AppleDouble metadata that can break Wii U SD loads."""
    removed: list[Path] = []
    if not root.exists():
        return removed
    # Walk deepest-first so directories can be removed after children.
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if is_junk_name(path.name):
            if path.is_dir():
                # rmtree-like: only delete if leftover junk dir
                import shutil

                shutil.rmtree(path, ignore_errors=True)
            else:
                try:
                    path.unlink()
                except FileNotFoundError:
                    continue
            removed.append(path)
    return removed


def extract_zip(zip_path: Path, dest: Path) -> None:
    if not zipfile.is_zipfile(zip_path):
        raise ManagerError(f"{zip_path} is not a zip file")
    ensure_dir(dest)
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            name = info.filename.replace("\\", "/")
            parts = [part for part in name.split("/") if part]
            if any(is_junk_name(part) for part in parts):
                continue
            target = dest.joinpath(*parts)
            if name.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, target.open("wb") as out:
                out.write(src.read())


def stage_downloads(
    download_dir: Path | None = None,
    sdroot: Path | None = None,
    zip_paths: list[Path] | None = None,
) -> Path:
    download_dir = download_dir or downloads_dir()
    sdroot = sdroot or sdroot_dir()
    extract_root = sdroot.parent / "extract"
    if extract_root.exists():
        import shutil

        shutil.rmtree(extract_root)
    ensure_dir(extract_root)
    if sdroot.exists():
        import shutil

        shutil.rmtree(sdroot)
    ensure_dir(sdroot)

    zips = zip_paths if zip_paths is not None else sorted(download_dir.glob("*.zip"))
    if not zips:
        raise ManagerError(f"No zip files found in {download_dir}. Run: wiiu fetch")

    for zip_path in zips:
        slot = extract_root / zip_path.stem
        eprint(f"Extracting {zip_path.name}")
        extract_zip(zip_path, slot)
        # Official guide: copy the zip contents (the wiiu folder) onto the SD root, merging.
        copy_tree_merge(slot, sdroot)

    clean_junk(sdroot)
    return sdroot
