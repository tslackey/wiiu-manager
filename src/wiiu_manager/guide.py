from __future__ import annotations

from wiiu_manager.console import next_key

GUIDE = "https://wiiu.hacks.guide"
AROMA = "https://aroma.foryour.cafe/"

STEPS = {
    "console_powers_on": {
        "title": "Confirm the black Wii U actually powers on",
        "detail": (
            "Homebrew cannot be installed on a dead console. Wait for a known-good OEM-compatible AC adapter. "
            "Look for a red standby LED, then a boot to the Wii U Menu. The GamePad powering on by itself does not count."
        ),
        "links": (GUIDE,),
    },
    "firmware_recorded": {
        "title": "Record the firmware version",
        "detail": (
            "On the Wii U: System Settings -> System Information. North American latest is 5.5.6. "
            "Write it into config/console.json as firmware. Then start at the live Wii U Hacks Guide for that version."
        ),
        "links": (GUIDE,),
    },
    "sd_prepared": {
        "title": "Prepare the SD card on this Mac",
        "detail": (
            "From this repo: `wiiu doctor`, `wiiu fetch --profile recommended`, `wiiu list-disks`, "
            "`wiiu format-sd --disk diskN --confirm diskN`, `wiiu copy-sd`, `wiiu verify`. "
            "FAT32, MBR, label WIIUHB (never 'wiiu'). Eject before unplugging."
        ),
        "links": (f"{GUIDE}/aroma/sd-preparation.html", AROMA),
    },
    "entry_point_ran": {
        "title": "Run the current official entry point on the console",
        "detail": (
            "Follow the live Browser Exploit page on the Wii U Hacks Guide. Do not use Haxchi, Coldboot Haxchi, "
            "or random old URLs. Insert the prepared SD, then do exactly what that page says."
        ),
        "links": (f"{GUIDE}/aroma/browser-exploit.html",),
    },
    "nand_backed_up": {
        "title": "Make a NAND backup before PayloadLoader",
        "detail": (
            "Follow the live NAND backup page. After nanddumper finishes, plug the SD back into this Mac and run "
            "`wiiu collect-nand --delete-from-sd`. Keep slc.bin / slccmpt.bin / seeprom.bin / otp.bin private and redundant."
        ),
        "links": (f"{GUIDE}/aroma/nand-backup.html",),
    },
    "payloadloader_installed": {
        "title": "Install PayloadLoader from the official guide",
        "detail": (
            "Only after the NAND backup is copied off the SD. Follow Installing PayloadLoader on the live guide. "
            "A factory reset will not remove PayloadLoader — uninstall it with the official uninstall page if needed."
        ),
        "links": (f"{GUIDE}/aroma/installing-payloadloader.html",),
    },
    "aroma_autoboot": {
        "title": "Set Aroma as the default environment",
        "detail": "Follow Autobooting Aroma on the live guide if you want Health & Safety / boot to launch Aroma.",
        "links": (f"{GUIDE}/aroma/autobooting.html",),
    },
    "updates_blocked": {
        "title": "Block system updates",
        "detail": "Follow Blocking Updates on the live guide (Aroma warning screen / AutobootMenu). Stay on 5.5.x.",
        "links": (f"{GUIDE}/block-updates.html",),
    },
    "extras_installed": {
        "title": "Add the recommended extras if they are not already on the SD",
        "detail": (
            "SaveMii, Homebrew App Store, Bloopair, FTPiiU, SDCafiine, Screenshot are in `wiiu fetch --profile recommended`. "
            "Finalizing Setup on the live guide is the checklist."
        ),
        "links": (f"{GUIDE}/aroma/finalizing-setup.html",),
    },
    "vwii_modded": {
        "title": "Optional later: vWii / GameCube (do not mix this with the first Aroma pass)",
        "detail": (
            "vWii is a separate environment. After Aroma is stable, follow the current vWii page linked from Finalizing Setup. "
            "GameCube on Wii U is typically Nintendont on vWii using dumps of discs you own. Skip this until Aroma is done."
        ),
        "links": (f"{GUIDE}/aroma/finalizing-setup.html",),
    },
}


def next_steps_text(console: dict) -> str:
    key = next_key(console)
    lines = [
        f"Console: {console.get('nickname')} ({console.get('model')}, {console.get('region')})",
        f"Firmware recorded: {console.get('firmware') or '(unknown — read it from System Settings)'}",
        "",
    ]
    if key is None:
        lines.append("Checklist complete. For anything new, re-read the live Wii U Hacks Guide before changing the console.")
        lines.append(GUIDE)
        return "\n".join(lines) + "\n"

    step = STEPS[key]
    lines.append(f"Next: {step['title']}")
    lines.append(step["detail"])
    if step["links"]:
        lines.append("Official pages:")
        lines.extend(f"  {url}" for url in step["links"])
    else:
        lines.append(f"Guide home: {GUIDE}")
    lines.append("")
    lines.append("When that step is actually done:  wiiu mark " + key)
    lines.append("Do not invent click-by-click console instructions from memory. Re-check the live guide.")
    return "\n".join(lines) + "\n"
