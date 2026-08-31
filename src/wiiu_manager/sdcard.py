from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from wiiu_manager.util import ManagerError, eprint, human_bytes, is_linux, is_macos, run, which


MIN_SD_BYTES = 1 * 1024 * 1024 * 1024  # 1 GiB
MAX_SD_BYTES = 256 * 1024 * 1024 * 1024  # 256 GiB, safety cap
DEFAULT_LABEL = "WIIUHB"
FORBIDDEN_LABELS = {"wiiu"}


@dataclass
class Disk:
    identifier: str
    device: str
    size_bytes: int
    name: str
    internal: bool
    protocol: str
    mountpoint: str | None
    volumes: tuple[str, ...] = ()

    def summary(self) -> str:
        kind = "internal" if self.internal else "removable"
        mount = self.mountpoint or "-"
        return (
            f"{self.identifier:8} {human_bytes(self.size_bytes):>10}  {kind:10}  "
            f"{self.protocol or '-':12}  {self.name or '-'}  mounted={mount}"
        )


def _plist(args: list[str]) -> dict:
    import plistlib
    import subprocess

    # diskutil -plist may emit XML or binary; never decode as text.
    result = subprocess.run(args, check=True, capture_output=True)
    return plistlib.loads(result.stdout)


def list_disks_macos() -> list[Disk]:
    if not which("diskutil"):
        raise ManagerError("diskutil not found — this command needs macOS Disk Utility CLI")
    listing = _plist(["diskutil", "list", "-plist"])
    disks: list[Disk] = []
    for ident in listing.get("WholeDisks", []):
        info = _plist(["diskutil", "info", "-plist", ident])
        size = int(info.get("TotalSize") or info.get("Size") or 0)
        protocol = str(info.get("BusProtocol") or info.get("Protocol") or "")
        name = str(info.get("MediaName") or info.get("IORegistryEntryName") or "")
        internal = bool(info.get("Internal"))
        mount = info.get("MountPoint") or None
        volumes: list[str] = []
        for child in listing.get("AllDisksAndPartitions", []):
            if child.get("DeviceIdentifier") != ident:
                continue
            for part in child.get("Partitions", []) or []:
                if part.get("MountPoint"):
                    volumes.append(str(part["MountPoint"]))
                if part.get("VolumeName"):
                    volumes.append(str(part["VolumeName"]))
        disks.append(
            Disk(
                identifier=str(ident),
                device=f"/dev/{ident}",
                size_bytes=size,
                name=name,
                internal=internal,
                protocol=protocol,
                mountpoint=str(mount) if mount else (volumes[0] if volumes else None),
                volumes=tuple(volumes),
            )
        )
    return disks


def list_disks_linux() -> list[Disk]:
    lsblk = which("lsblk")
    if not lsblk:
        raise ManagerError("lsblk not found")
    result = run(
        [lsblk, "-J", "-b", "-o", "NAME,SIZE,TYPE,RM,HOTPLUG,TRAN,MOUNTPOINT,MODEL,VENDOR,PKNAME"],
        capture=True,
    )
    data = json.loads(result.stdout)
    disks: list[Disk] = []
    for node in data.get("blockdevices", []):
        if node.get("type") != "disk":
            continue
        children = node.get("children") or []
        mounts = [c.get("mountpoint") for c in children if c.get("mountpoint")]
        size = int(node.get("size") or 0)
        removable = bool(int(node.get("rm") or 0) or int(node.get("hotplug") or 0))
        name = " ".join(p for p in (node.get("vendor"), node.get("model")) if p).strip()
        disks.append(
            Disk(
                identifier=str(node.get("name")),
                device=f"/dev/{node.get('name')}",
                size_bytes=size,
                name=name,
                internal=not removable,
                protocol=str(node.get("tran") or ""),
                mountpoint=mounts[0] if mounts else node.get("mountpoint"),
                volumes=tuple(str(m) for m in mounts),
            )
        )
    return disks


def list_disks() -> list[Disk]:
    if is_macos():
        return list_disks_macos()
    if is_linux():
        return list_disks_linux()
    raise ManagerError(f"Unsupported platform for disk listing: {__import__('sys').platform}")


def classify_candidate(disk: Disk) -> list[str]:
    """Return human warnings. Empty means it looks like a plausible SD/USB card reader."""
    warnings: list[str] = []
    if disk.internal:
        warnings.append("disk is marked internal — refusing to treat it as an SD card")
    if disk.size_bytes < MIN_SD_BYTES:
        warnings.append(f"size {human_bytes(disk.size_bytes)} is smaller than 1 GiB")
    if disk.size_bytes > MAX_SD_BYTES:
        warnings.append(f"size {human_bytes(disk.size_bytes)} is larger than 256 GiB (probably not the SD card)")
    protocol = disk.protocol.lower()
    if protocol and protocol not in {"usb", "secure digital", "sd", "sd/mmc", "sdio"}:
        # Thunderbolt card readers still often show as USB. NVMe/SATA is a hard no.
        if protocol in {"sata", "nvme", "pci-e", "pcie", "disk image", "virtual"}:
            warnings.append(f"protocol {disk.protocol!r} is not a removable card reader")
    ident = disk.identifier.lower()
    if ident.startswith("disk0") or ident in {"sda", "nvme0n1", "mmcblk0"} and disk.internal:
        warnings.append("identifier looks like the boot disk")
    return warnings


def require_safe_target(disk: Disk, *, confirm: str) -> None:
    if confirm != disk.identifier:
        raise ManagerError(
            f"--confirm must exactly match the disk identifier {disk.identifier!r} (got {confirm!r})"
        )
    problems = classify_candidate(disk)
    fatal = [p for p in problems if "internal" in p or "boot disk" in p or "not a removable" in p]
    if disk.internal:
        raise ManagerError(
            f"Refusing to format internal disk {disk.identifier} ({disk.name}). {'; '.join(problems)}"
        )
    if fatal:
        raise ManagerError(f"Refusing to format {disk.identifier}: {'; '.join(fatal)}")
    if disk.size_bytes > MAX_SD_BYTES:
        raise ManagerError(
            f"Refusing to format {disk.identifier}: {human_bytes(disk.size_bytes)} looks too large to be the Wii U SD card"
        )


def validate_label(label: str) -> str:
    cleaned = label.strip().upper().replace(" ", "")
    if not cleaned:
        raise ManagerError("Volume label is empty")
    if cleaned.lower() in FORBIDDEN_LABELS:
        raise ManagerError("Volume label cannot be WIIU — the official guide says that breaks homebrew")
    if len(cleaned) > 11:
        raise ManagerError("FAT32 volume labels must be 11 characters or fewer")
    return cleaned


def format_sd_macos(disk: Disk, label: str) -> None:
    device = disk.device
    eprint(f"Unmounting {device}")
    run(["diskutil", "unmountDisk", "force", device], check=False)
    eprint(f"Partitioning {device} as MBR FAT32 labeled {label}")
    # MS-DOS FAT32 + MBR is what the Wii U expects. Cluster size is best-effort;
    # macOS diskutil does not always honor 32k, which is still accepted by the console.
    try:
        run(["diskutil", "partitionDisk", device, "MBR", "MS-DOS FAT32", label, "R"])
        return
    except Exception:
        eprint("partitionDisk MS-DOS FAT32 failed; trying eraseDisk FAT32")
    run(["diskutil", "eraseDisk", "FAT32", label, "MBRFormat", device])


def format_sd_linux(disk: Disk, label: str) -> None:
    mkfs = which("mkfs.vfat") or which("mkfs.fat")
    if not mkfs:
        raise ManagerError("mkfs.vfat not found. Install dosfstools.")
    parted = which("parted")
    device = disk.device
    # Unmount any partitions
    result = run(["lsblk", "-ln", "-o", "NAME,MOUNTPOINT", device], capture=True, check=False)
    for line in (result.stdout or "").splitlines():
        parts = line.split()
        if len(parts) == 2:
            run(["umount", parts[1]], check=False)
    if parted:
        # Single MBR FAT32 partition.
        run([parted, "-s", device, "mklabel", "msdos"])
        run([parted, "-s", device, "mkpart", "primary", "fat32", "1MiB", "100%"])
    part = f"{device}1" if not device[-1].isdigit() else f"{device}p1"
    # 64 sectors * 512 bytes = 32 KiB clusters, matching the official 32k guidance.
    run([mkfs, "-F", "32", "-s", "64", "-n", label, part])


def format_sd(identifier: str, *, confirm: str, label: str = DEFAULT_LABEL) -> Disk:
    label = validate_label(label)
    disks = {d.identifier: d for d in list_disks()}
    if identifier not in disks:
        known = ", ".join(sorted(disks)) or "(none)"
        raise ManagerError(f"Unknown disk {identifier!r}. Known: {known}")
    disk = disks[identifier]
    require_safe_target(disk, confirm=confirm)
    eprint(f"Formatting {disk.summary()}")
    eprint("THIS ERASES THE CARD. Keep going only if this is the Wii U SD card.")
    if is_macos():
        format_sd_macos(disk, label)
    elif is_linux():
        format_sd_linux(disk, label)
    else:
        raise ManagerError("SD formatting is implemented for macOS and Linux only")
    return disk


def detect_sd_mount(preferred_label: str = DEFAULT_LABEL) -> Path | None:
    if is_macos():
        preferred = Path("/Volumes") / preferred_label
        if preferred.exists():
            return preferred
        volumes = Path("/Volumes")
        if volumes.is_dir():
            for item in volumes.iterdir():
                if item.is_dir() and (item / "wiiu").exists():
                    return item
        return None
    # Linux: look at lsblk mountpoints
    for disk in list_disks_linux():
        for vol in disk.volumes:
            path = Path(vol)
            if path.name.upper() == preferred_label or (path / "wiiu").exists():
                return path
    return None


def copy_to_sd(sdroot: Path, dest: Path) -> None:
    if not sdroot.exists():
        raise ManagerError(f"Staged SD root {sdroot} does not exist. Run: wiiu fetch && wiiu stage")
    dest.mkdir(parents=True, exist_ok=True)
    eprint(f"Copying staged files -> {dest}")
    from wiiu_manager.util import copy_tree_merge

    copy_tree_merge(sdroot, dest)
    from wiiu_manager.stage import clean_junk

    removed = clean_junk(dest)
    if removed:
        eprint(f"Removed {len(removed)} macOS junk file(s) from the SD card")
    if is_macos() and which("sync"):
        run(["sync"], check=False)


def eject_mount(path: Path) -> None:
    if is_macos() and which("diskutil"):
        run(["diskutil", "eject", str(path)])
        return
    if is_linux():
        run(["umount", str(path)])
        return
    raise ManagerError("Do not know how to eject on this platform")


def guess_volume_label(path: Path) -> str | None:
    if is_macos() and path.parent == Path("/Volumes"):
        return path.name
    return path.name if path.name else None
