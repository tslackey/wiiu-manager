# Troubleshooting (Mac / SD first)

Console-side errors: start at [Common Issues & Fixes](https://wiiu.hacks.guide/common-issues-fixes.html). This page is the Mac/SD overlay.

## `FSGetMountSource failed` / no SD detected

- Reseat the card. Blow **canned** air in the slot if it is dusty (not your mouth).
- Lock slider unlocked.
- Volume label is not `wiiu`.
- Filesystem is FAT32/MBR, not ExFAT, not GPT.
- Try another reader; some USB 3 readers are flaky with SDHC.

## `FSOpenFile failed ... payload.elf`

- Confirm `wiiu/payload.elf` exists on the root-level `wiiu` folder (`./scripts/wiiu verify /Volumes/WIIUHB`).
- Delete `wiiu/._payload.elf` and `.DS_Store` (`./scripts/wiiu clean-junk`).
- You replaced instead of merged the two official zips — run `wiiu stage` and `wiiu copy-sd` again.

## `SD Mount failed`

- Reformat with `wiiu format-sd`.
- Avoid no-name cards.
- One primary partition only (MBR).

## Aroma `150-3030`

SD is write-protected or failed a write. Unlock the slider; make sure macOS did not mount the card read-only.

## Format picked the wrong disk

If `format-sd` refused: good. If you overrode safety on an internal disk, stop and recover from Time Machine / Apple, not from this repo. The CLI requires `--confirm` to match `--disk` and skips `Internal` devices; do not patch that out.

## Browser exploit freeze / white screen

That is a console-side issue. The live Browser Exploit page says to wait, reboot, reset browser save data, retry. Holding the wrong button lands you in EnvironmentLoader instead of nanddumper — read the current page for which button to hold.

## PayloadLoader already installed from a previous attempt

Skip SD prep duplication; jump to the live Finalizing Setup / autoboot pages. Do not install a second time over a healthy install unless the installer is doing an update.

## Need live help

Nintendo Homebrew Discord, `#wiiu-assistance`, English, after reading `#faq-wiiu` — linked from the top of https://wiiu.hacks.guide/
