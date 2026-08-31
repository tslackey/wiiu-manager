from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from wiiu_manager.stage import is_junk_name


REQUIRED_BASE = (
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
)

REQUIRED_RECOMMENDED = REQUIRED_BASE + (
    "wiiu/environments/aroma/modules/setup/30_bloopair.rpx",
    "wiiu/environments/aroma/plugins/ftpiiu.wps",
    "wiiu/environments/aroma/plugins/sdcafiine.wps",
    "wiiu/environments/aroma/plugins/screenshot.wps",
    "wiiu/environments/aroma/plugins/swipswapme.wps",
    "wiiu/apps/SaveMiiProcessMod/savemii.wuhb",
    "wiiu/apps/appstore/appstore.wuhb",
)

NAND_ROOT_FILES = ("slc.bin", "slccmpt.bin", "seeprom.bin", "otp.bin")

FORBIDDEN_VOLUME_LABELS = {"wiiu", "WIIU", "WiiU", "Wii U"}


@dataclass
class LayoutReport:
    root: Path
    profile: str
    missing: list[str] = field(default_factory=list)
    junk: list[str] = field(default_factory=list)
    nand_files: list[str] = field(default_factory=list)
    volume_label_warning: str | None = None
    ok: bool = True

    def summary_lines(self) -> list[str]:
        lines = [f"Layout check ({self.profile}) for {self.root}"]
        if self.ok and not self.junk and not self.volume_label_warning:
            lines.append("OK — required Aroma files are present.")
        if self.missing:
            lines.append("Missing required files:")
            lines.extend(f"  - {name}" for name in self.missing)
        if self.junk:
            lines.append("macOS junk files that should be removed:")
            lines.extend(f"  - {name}" for name in self.junk)
        if self.nand_files:
            lines.append("NAND dump files on this volume (copy these off the SD, then delete):")
            lines.extend(f"  - {name}" for name in self.nand_files)
        if self.volume_label_warning:
            lines.append(self.volume_label_warning)
        return lines


def required_files(profile: str) -> tuple[str, ...]:
    if profile == "base":
        return REQUIRED_BASE
    if profile in {"recommended", "all"}:
        return REQUIRED_RECOMMENDED
    return REQUIRED_BASE


def collect_junk(root: Path) -> list[str]:
    found: list[str] = []
    for path in root.rglob("*"):
        if is_junk_name(path.name):
            found.append(str(path.relative_to(root)))
    return sorted(found)


def collect_nand_files(root: Path) -> list[str]:
    found: list[str] = []
    for name in NAND_ROOT_FILES:
        if (root / name).exists():
            found.append(name)
    found.extend(sorted(p.name for p in root.glob("mlc.bin.part*")))
    return found


def verify_layout(
    root: Path,
    profile: str = "base",
    *,
    volume_label: str | None = None,
) -> LayoutReport:
    required = required_files(profile)
    missing = [rel for rel in required if not (root / rel).is_file()]
    junk = collect_junk(root)
    nand_files = collect_nand_files(root)
    label_warning = None
    if volume_label and volume_label.strip().lower() == "wiiu":
        label_warning = (
            "Volume label is 'wiiu', which the official guide warns will break homebrew. "
            "Reformat with label WIIUHB."
        )
    ok = not missing and label_warning is None
    return LayoutReport(
        root=root,
        profile=profile,
        missing=missing,
        junk=junk,
        nand_files=nand_files,
        volume_label_warning=label_warning,
        ok=ok,
    )
