# Agent notes — wiiu-manager

Read this before changing the repo or telling the operator what to do on the console.

## What this project is

A **macOS-first SD-card manager** for installing **Aroma** on one specific Wii U:

- Black Deluxe **WUP-101**, North America, optical disc drive
- Possible PSU failure: the GamePad can power on while the console is dead. Homebrew waits until the **black console** reaches the Wii U Menu
- Incoming ~32 GB SD card, prepared on this Mac
- Target stack: Aroma + EnvironmentLoader + PayloadLoader, then NAND backup, then extras
- Not in the first pass: vWii homebrew, Nintendont, Pretendo/Inkay, ISFShax, de_Fuse

Operator-facing CLI: `./scripts/wiiu` (Python 3 stdlib only).

## Source of truth

| Topic | Source |
| --- | --- |
| Console-side clicks | Live [Wii U Hacks Guide](https://wiiu.hacks.guide/) — re-fetch, do not recite from memory |
| Aroma zip contents | [aroma.foryour.cafe](https://aroma.foryour.cafe/) API used by `config/packages.json` |
| This console | `docs/console-profile.md` and `config/console.json` (created by `wiiu init`) |
| macOS SD pitfalls | `docs/macos.md` |
| Why Aroma, not Haxchi | `docs/methods.md` |

`docs/` is orientation. If it disagrees with the live guide, the live guide wins.

## Day-of command sequence (Mac)

```bash
./scripts/wiiu doctor
./scripts/wiiu next
./scripts/wiiu fetch --profile recommended
./scripts/wiiu stage
./scripts/wiiu verify
./scripts/wiiu list-disks
# only after identifying the SD reader, never disk0:
./scripts/wiiu format-sd --disk diskN --confirm diskN --yes
./scripts/wiiu copy-sd /Volumes/WIIUHB
./scripts/wiiu verify /Volumes/WIIUHB
./scripts/wiiu eject
```

Then the operator follows the live guide on the console. After nanddumper:

```bash
./scripts/wiiu collect-nand --delete-from-sd
```

## Invariants

1. **Power first.** No SD work unblocks a console that will not boot.
2. **FAT32 + MBR + label `WIIUHB`.** Label `wiiu` is a known failure mode.
3. **Merge `wiiu/` folders**, do not replace one zip with the other.
4. **Strip macOS junk** (`.DS_Store`, `._*`) or the browser payload load fails.
5. **NAND backup before PayloadLoader.** `otp.bin` stays private; copy off SD, then delete from the card to free space.
6. **No Haxchi / CBHC / Indexiine** unless the live guide for this firmware explicitly requires a legacy uninstall first.
7. **No piracy tooling.** Homebrew and backups of games the owner has are the boundary.
8. **Do not write exploits.** This repo downloads official EnvironmentLoader/Aroma builds and copies files. Console entry-point steps stay on wiiu.hacks.guide.

## Layout the verifier expects

Official SD Preparation tree (plus recommended extras):

- `wiiu/payload.elf`, `wiiu/payload.rpx`
- `wiiu/payloads/default/payload.elf`
- `wiiu/payloads/nanddumper/payload.elf`
- `wiiu/environments/aroma/` (`root.rpx`, modules, plugins)
- `wiiu/apps/AromaUpdater/AromaUpdater.wuhb`
- `wiiu/apps/PayloadLoaderInstaller.wuhb`
- Recommended: Bloopair, FTPiiU, SDCafiine, Screenshot, SwipSwapMe, SaveMii ProcessMod, Homebrew App Store

If Aroma's zip layout changes, update `src/wiiu_manager/layout.py` and `config/packages.json` together, after checking aroma.foryour.cafe and the live guide.

## Firmware

NA latest at last check: **5.5.6**. Record the real value from System Settings → System Information with `wiiu set-firmware`.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Need Python 3.9+ and `curl` for live downloads. Format/eject tests that would erase disks are safety-logic only; they do not call `diskutil eraseDisk` in CI.

## Future work that should stay out of the default profile

- vWii / Homebrew Channel / Nintendont — `docs/vwii-later.md`
- Pretendo (`wiiu fetch --profile pretendo`) — only if the operator wants replacement online services
- ISFShax / de_Fuse — recovery, not a first install
