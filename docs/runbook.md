# Runbook

Do the Mac-side work with `./scripts/wiiu`. Do the console-side work from the **live** [Wii U Hacks Guide](https://wiiu.hacks.guide/). Re-open those pages the day you install; labels change.

## 0. Console health

1. Confirm the replacement AC adapter is OEM-compatible.
2. Red standby LED on the black console.
3. Power on to the **Wii U Menu** (not just the GamePad).
4. System Settings → System Information → record firmware: `./scripts/wiiu set-firmware 5.5.x`
5. `./scripts/wiiu mark console_powers_on`

If there is no front LED after the new brick, stop. Homebrew will not fix a power-path failure.

## 1. SD card on this Mac

```bash
./scripts/wiiu doctor
./scripts/wiiu fetch --profile recommended
./scripts/wiiu stage
./scripts/wiiu list-disks
./scripts/wiiu format-sd --disk diskN --confirm diskN
./scripts/wiiu copy-sd
./scripts/wiiu verify /Volumes/WIIUHB --profile recommended
./scripts/wiiu eject
```

Details and failure modes: [macos.md](macos.md). Official file list: [SD Preparation](https://wiiu.hacks.guide/aroma/sd-preparation.html).

## 2. Entry point

Follow [Browser Exploit](https://wiiu.hacks.guide/aroma/browser-exploit.html) exactly.

If the browser path is unavailable, the live guide and community docs also describe a DNS-based entry (DNSpresso). Prefer whatever the **current** guide lists for 5.5.x. Do not paste old exploit URLs from blogs.

`./scripts/wiiu mark entry_point_ran` when EnvironmentLoader is reachable.

## 3. NAND backup (mandatory before PayloadLoader)

Follow [Making a NAND Backup](https://wiiu.hacks.guide/aroma/nand-backup.html).

MLC dump is optional and needs an SD larger than the 32 GB internal flash. SLC + slccmpt + seeprom + otp are the minimum useful set.

Then on the Mac:

```bash
./scripts/wiiu collect-nand --delete-from-sd
```

Copy `backups/nand/` somewhere else as well (external drive / encrypted archive). Do not commit it. Do not share `otp.bin`.

Restoring a NAND backup later needs ISFShax or hardware tools. The dump is still worth taking.

## 4. PayloadLoader and autoboot

- [Installing PayloadLoader](https://wiiu.hacks.guide/aroma/installing-payloadloader.html)
- [Autobooting Aroma](https://wiiu.hacks.guide/aroma/autobooting.html)
- [Blocking Updates](https://wiiu.hacks.guide/block-updates.html)

Factory reset does **not** uninstall PayloadLoader. Official uninstall page only.

Hold **X** while loading Health & Safety / boot to get EnvironmentLoader. Hold **START (+)** for the Aroma boot selector (per current autoboot page).

## 5. Extras

`recommended` already stages SaveMii, Homebrew App Store, Bloopair, FTPiiU, SDCafiine, Screenshot, SwipSwapMe. Confirm against [Finalizing Setup](https://wiiu.hacks.guide/aroma/finalizing-setup.html).

## 6. Stop and live with Aroma

Do not chain vWii, Nintendont, Pretendo, and disc dumping into the same evening. When Aroma boots cleanly from PayloadLoader and the NAND copy is off the card, the first session is done.

## Errors worth recording verbatim

Browser/SD: `FSOpenFile failed`, `FSGetMountSource failed`, `SD Mount failed`, Aroma `150-3030` (often write-protect). See [troubleshooting.md](troubleshooting.md) and [Common Issues](https://wiiu.hacks.guide/common-issues-fixes.html).
