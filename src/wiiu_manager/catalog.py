from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wiiu_manager.paths import packages_path, repo_root
from wiiu_manager.util import ManagerError, load_json


@dataclass(frozen=True)
class Package:
    id: str
    kind: str
    description: str
    filename: str
    profile: str = "optional"
    url: str | None = None
    repo: str | None = None
    asset_name: str | None = None
    asset_prefix: str | None = None
    asset_suffix: str | None = None

    @classmethod
    def from_dict(cls, package_id: str, raw: dict[str, Any]) -> Package:
        return cls(
            id=package_id,
            kind=raw["kind"],
            description=raw.get("description", ""),
            filename=raw["filename"],
            profile=raw.get("profile", "optional"),
            url=raw.get("url"),
            repo=raw.get("repo"),
            asset_name=raw.get("asset_name"),
            asset_prefix=raw.get("asset_prefix"),
            asset_suffix=raw.get("asset_suffix"),
        )


@dataclass(frozen=True)
class Profile:
    id: str
    description: str
    packages: tuple[str, ...]


@dataclass(frozen=True)
class Catalog:
    updated: str
    notes: str
    authoritative_guide: str
    aroma_site: str
    profiles: dict[str, Profile]
    packages: dict[str, Package]

    def profile(self, name: str) -> Profile:
        if name not in self.profiles:
            known = ", ".join(sorted(self.profiles))
            raise ManagerError(f"Unknown profile {name!r}. Known profiles: {known}")
        return self.profiles[name]

    def packages_for_profile(self, name: str) -> list[Package]:
        profile = self.profile(name)
        missing = [pid for pid in profile.packages if pid not in self.packages]
        if missing:
            raise ManagerError(f"Profile {name!r} references unknown packages: {missing}")
        return [self.packages[pid] for pid in profile.packages]

    def get(self, package_id: str) -> Package:
        if package_id not in self.packages:
            known = ", ".join(sorted(self.packages))
            raise ManagerError(f"Unknown package {package_id!r}. Known packages: {known}")
        return self.packages[package_id]


def load_catalog(root: Path | None = None) -> Catalog:
    path = packages_path(root or repo_root())
    raw = load_json(path)
    if not isinstance(raw, dict):
        raise ManagerError(f"Invalid catalog at {path}")
    packages = {
        key: Package.from_dict(key, value)
        for key, value in raw.get("packages", {}).items()
    }
    profiles = {
        key: Profile(
            id=key,
            description=value.get("description", ""),
            packages=tuple(value.get("packages", [])),
        )
        for key, value in raw.get("profiles", {}).items()
    }
    return Catalog(
        updated=str(raw.get("updated", "")),
        notes=str(raw.get("notes", "")),
        authoritative_guide=str(raw.get("authoritative_guide", "https://wiiu.hacks.guide/")),
        aroma_site=str(raw.get("aroma_site", "https://aroma.foryour.cafe/")),
        profiles=profiles,
        packages=packages,
    )
