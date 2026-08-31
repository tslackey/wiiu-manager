from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    env = os.environ.get("WIIU_MANAGER_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # src/wiiu_manager/paths.py -> repo root is parents[2]
    return Path(__file__).resolve().parents[2]


def config_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "config"


def downloads_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "downloads"


def staging_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "staging"


def sdroot_dir(root: Path | None = None) -> Path:
    return staging_dir(root) / "sdroot"


def backups_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "backups"


def packages_path(root: Path | None = None) -> Path:
    return config_dir(root) / "packages.json"


def console_path(root: Path | None = None) -> Path:
    return config_dir(root) / "console.json"


def console_example_path(root: Path | None = None) -> Path:
    return config_dir(root) / "console.example.json"
