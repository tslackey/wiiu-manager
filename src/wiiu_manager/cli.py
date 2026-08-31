from __future__ import annotations

import argparse
import sys
from pathlib import Path

from wiiu_manager import __version__
from wiiu_manager.catalog import load_catalog
from wiiu_manager.console import (
    PROGRESS_ORDER,
    doctor_checks,
    init_console,
    load_console,
    mark_progress,
    save_console,
)
from wiiu_manager.fetch import fetch_packages
from wiiu_manager.guide import next_steps_text
from wiiu_manager.layout import verify_layout
from wiiu_manager.nand import backup_sd, collect_nand
from wiiu_manager.paths import downloads_dir, repo_root, sdroot_dir
from wiiu_manager.sdcard import (
    DEFAULT_LABEL,
    classify_candidate,
    copy_to_sd,
    detect_sd_mount,
    eject_mount,
    format_sd,
    guess_volume_label,
    list_disks,
)
from wiiu_manager.stage import clean_junk, stage_downloads
from wiiu_manager.util import ManagerError, eprint, human_bytes


def _add_profile(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile",
        default="recommended",
        help="Package profile: base, recommended, or pretendo (default: recommended)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wiiu",
        description="Prepare a Wii U Aroma SD card from official downloads. macOS-first.",
    )
    parser.add_argument("--version", action="version", version=f"wiiu-manager {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="Check tools, platform, and repo files")
    sub.add_parser("next", help="Print the next safe step for this console")
    sub.add_parser("status", help="Show console profile and staged SD layout")

    init_p = sub.add_parser("init", help="Create config/console.json from the example profile")
    init_p.add_argument("--force", action="store_true", help="Overwrite an existing console.json")

    mark_p = sub.add_parser("mark", help="Mark a checklist item done in config/console.json")
    mark_p.add_argument("key", choices=PROGRESS_ORDER)
    mark_p.add_argument("--undo", action="store_true", help="Set the key back to false")

    firmware_p = sub.add_parser("set-firmware", help="Record the Wii U firmware string")
    firmware_p.add_argument("version", help="Example: 5.5.6")

    fetch_p = sub.add_parser("fetch", help="Download official Aroma / extra packages")
    _add_profile(fetch_p)

    stage_p = sub.add_parser("stage", help="Extract downloaded zips into staging/sdroot")
    stage_p.add_argument("--from-dir", type=Path, help="Directory of zip files (default: downloads/)")
    _add_profile(stage_p)

    verify_p = sub.add_parser("verify", help="Verify Aroma file layout on staging or an SD mount")
    verify_p.add_argument("path", nargs="?", help="Folder to check (default: staging/sdroot)")
    _add_profile(verify_p)

    sub.add_parser("list-disks", help="List disks; highlights plausible SD/USB readers")

    format_p = sub.add_parser("format-sd", help="Erase and FAT32-format a removable disk (destructive)")
    format_p.add_argument("--disk", required=True, help="Disk identifier, e.g. disk4 (macOS) or sdb (Linux)")
    format_p.add_argument("--confirm", required=True, help="Must exactly match --disk")
    format_p.add_argument("--label", default=DEFAULT_LABEL, help=f"Volume label (default {DEFAULT_LABEL}; never wiiu)")
    format_p.add_argument("--yes", action="store_true", help="Skip the interactive typed confirmation")

    copy_p = sub.add_parser("copy-sd", help="Copy staging/sdroot onto the SD card and strip macOS junk")
    copy_p.add_argument("dest", nargs="?", help="SD mount, e.g. /Volumes/WIIUHB (auto-detected when omitted)")
    _add_profile(copy_p)

    clean_p = sub.add_parser("clean-junk", help="Remove .DS_Store / AppleDouble files from a folder")
    clean_p.add_argument("path", help="Folder or SD mount")

    backup_p = sub.add_parser("backup-sd", help="Copy an SD mount into backups/sd/")
    backup_p.add_argument("source", nargs="?", help="SD mount (auto-detected when omitted)")

    nand_p = sub.add_parser("collect-nand", help="Copy NAND dump files off the SD into backups/nand/")
    nand_p.add_argument("source", nargs="?", help="SD mount (auto-detected when omitted)")
    nand_p.add_argument(
        "--delete-from-sd",
        action="store_true",
        help="Delete dump files from the SD after a size-verified copy (official guide does this to free space)",
    )

    eject_p = sub.add_parser("eject", help="Eject / unmount the SD card")
    eject_p.add_argument("path", nargs="?", help="SD mount (auto-detected when omitted)")

    return parser


def _resolve_mount(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser()
        if not path.exists():
            raise ManagerError(f"Path not found: {path}")
        return path
    detected = detect_sd_mount()
    if detected is None:
        raise ManagerError(
            "Could not auto-detect the SD card. Pass the mount path, e.g. /Volumes/WIIUHB. "
            "On macOS, format with label WIIUHB so detection works."
        )
    return detected


def cmd_doctor(_: argparse.Namespace) -> int:
    print(f"wiiu-manager {__version__}")
    print(f"repo: {repo_root()}")
    print(f"platform: {sys.platform}")
    failed = False
    for name, ok, detail in doctor_checks():
        mark = "OK " if ok else "NO "
        print(f"  [{mark}] {name:18} {detail}")
        if not ok and name in {"python3", "curl", "diskutil", "packages.json"}:
            failed = True
    print()
    print("Official guide: https://wiiu.hacks.guide/")
    print("Aroma packages: https://aroma.foryour.cafe/")
    return 1 if failed else 0


def cmd_init(args: argparse.Namespace) -> int:
    path = init_console(force=args.force)
    print(f"Console profile: {path}")
    return 0


def cmd_next(_: argparse.Namespace) -> int:
    init_console()
    print(next_steps_text(load_console()), end="")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    init_console()
    data = load_console()
    print(f"nickname:  {data.get('nickname')}")
    print(f"model:     {data.get('model')}  region={data.get('region')}  disc_drive={data.get('has_disc_drive')}")
    print(f"firmware:  {data.get('firmware') or '(not recorded)'}")
    print("progress:")
    for key in PROGRESS_ORDER:
        done = bool((data.get("progress") or {}).get(key))
        print(f"  [{'x' if done else ' '}] {key}")
    sdroot = sdroot_dir()
    if sdroot.exists():
        report = verify_layout(sdroot, "recommended")
        print()
        print("\n".join(report.summary_lines()))
    else:
        print()
        print("No staging/sdroot yet. Run: wiiu fetch && wiiu stage")
    print()
    print(next_steps_text(data), end="")
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    init_console()
    mark_progress(args.key, value=not args.undo)
    print(f"Set progress.{args.key} = {not args.undo}")
    return 0


def cmd_set_firmware(args: argparse.Namespace) -> int:
    init_console()
    data = load_console()
    data["firmware"] = args.version
    data.setdefault("progress", {})["firmware_recorded"] = True
    save_console(data)
    print(f"Recorded firmware {args.version}")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    packages = catalog.packages_for_profile(args.profile)
    print(f"Fetching profile {args.profile!r} ({len(packages)} packages)")
    print(f"Guide: {catalog.authoritative_guide}")
    results = fetch_packages(packages)
    print(f"Saved {len(results)} files in {downloads_dir()}")
    return 0


def cmd_stage(args: argparse.Namespace) -> int:
    sdroot = stage_downloads(download_dir=args.from_dir)
    print(f"Staged SD root: {sdroot}")
    report = verify_layout(sdroot, args.profile)
    print("\n".join(report.summary_lines()))
    return 0 if report.ok else 1


def cmd_verify(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser() if args.path else sdroot_dir()
    if not root.exists():
        raise ManagerError(f"Nothing to verify at {root}")
    label = guess_volume_label(root)
    report = verify_layout(root, args.profile, volume_label=label)
    print("\n".join(report.summary_lines()))
    if report.junk:
        print("Strip junk with:  wiiu clean-junk", root)
    return 0 if report.ok and not report.junk else 1


def cmd_list_disks(_: argparse.Namespace) -> int:
    disks = list_disks()
    if not disks:
        print("No disks found.")
        return 1
    print("identifier     size        kind        protocol      name")
    for disk in disks:
        flags = classify_candidate(disk)
        tag = "CANDIDATE" if not flags else "SKIP"
        print(f"{disk.summary()}  [{tag}]")
        for warning in flags:
            print(f"           ! {warning}")
    print()
    print("Destructive format example:")
    print("  wiiu format-sd --disk disk4 --confirm disk4 --yes")
    print("Never format an internal disk. Volume label must not be wiiu.")
    return 0


def cmd_format_sd(args: argparse.Namespace) -> int:
    if not args.yes:
        prompt = (
            f"Type ERASE {args.disk} to format that disk as FAT32 {args.label} "
            "(all data will be lost): "
        )
        typed = input(prompt).strip()
        if typed != f"ERASE {args.disk}":
            raise ManagerError("Aborted. Confirmation text did not match.")
    disk = format_sd(args.disk, confirm=args.confirm, label=args.label)
    print(f"Formatted {disk.identifier} as FAT32 {args.label}")
    print("If macOS created .DS_Store immediately, it will be stripped on copy-sd / clean-junk.")
    return 0


def cmd_copy_sd(args: argparse.Namespace) -> int:
    dest = _resolve_mount(args.dest)
    copy_to_sd(sdroot_dir(), dest)
    label = guess_volume_label(dest)
    report = verify_layout(dest, args.profile, volume_label=label)
    print("\n".join(report.summary_lines()))
    print()
    print("Eject before unplugging:  wiiu eject")
    print("Then follow the live SD Preparation / Browser Exploit pages on https://wiiu.hacks.guide/")
    if report.ok:
        mark_progress("sd_prepared", True)
    return 0 if report.ok else 1


def cmd_clean_junk(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser()
    removed = clean_junk(path)
    print(f"Removed {len(removed)} junk path(s) from {path}")
    return 0


def cmd_backup_sd(args: argparse.Namespace) -> int:
    source = _resolve_mount(args.source)
    dest = backup_sd(source)
    print(dest)
    return 0


def cmd_collect_nand(args: argparse.Namespace) -> int:
    source = _resolve_mount(args.source)
    dest = collect_nand(source, delete_from_sd=args.delete_from_sd)
    print(dest)
    mark_progress("nand_backed_up", True)
    return 0


def cmd_eject(args: argparse.Namespace) -> int:
    path = _resolve_mount(args.path)
    eject_mount(path)
    print(f"Ejected {path}")
    return 0


COMMANDS = {
    "doctor": cmd_doctor,
    "init": cmd_init,
    "next": cmd_next,
    "status": cmd_status,
    "mark": cmd_mark,
    "set-firmware": cmd_set_firmware,
    "fetch": cmd_fetch,
    "stage": cmd_stage,
    "verify": cmd_verify,
    "list-disks": cmd_list_disks,
    "format-sd": cmd_format_sd,
    "copy-sd": cmd_copy_sd,
    "clean-junk": cmd_clean_junk,
    "backup-sd": cmd_backup_sd,
    "collect-nand": cmd_collect_nand,
    "eject": cmd_eject,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return COMMANDS[args.cmd](args)
    except ManagerError as exc:
        eprint(f"error: {exc}")
        return 1
    except KeyboardInterrupt:
        eprint("aborted")
        return 130
