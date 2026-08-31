# Console profile

Fill gaps with `./scripts/wiiu set-firmware` and `./scripts/wiiu mark` as you go. `config/console.json` is local working state (gitignored); this file is the durable description.

## Hardware

| Field | Value |
| --- | --- |
| Nickname | black-deluxe |
| Model | WUP-101 (black Deluxe, 32 GB internal) |
| Region | North America |
| Disc drive | Yes — original drive electronics stay with this console |
| GamePad | Powers independently; that does **not** mean the console is alive |
| Current blocker | Possible OEM PSU failure. Replacement brick ordered. No homebrew until a red standby LED and a Wii U Menu boot |
| SD card | ~32 GB, arriving with the operator, prepared on macOS |

## Firmware

Unknown until System Settings → System Information. NA latest at last check: **5.5.6**. All current Aroma / browser-entry methods target 5.5.x.

## Target end state

```
Power on
  └─ Wii U Menu
       └─ Aroma (EnvironmentLoader / PayloadLoader)
            ├─ Wii U homebrew (.wuhb on the menu)
            ├─ SaveMii / App Store / Bloopair / utilities
            └─ (later, separate project) vWii → Wii homebrew / Nintendont
```

Aroma runs on the black console, not on the GamePad.

## What we are not doing on day one

- Haxchi or Coldboot Haxchi
- Indexiine / Mocha-from-old-guides
- vWii Smash Stack
- Pretendo / Inkay
- de_Fuse soldering
- Installing games that were not dumped from discs/eShop titles this console owns

## Storage plan

| Media | Role |
| --- | --- |
| SD (FAT32) | Aroma, payloads, small homebrew, NAND dump (temporarily) |
| USB HDD/SSD later | Large libraries; Wii U formatted USB is console-unique |
| Mac + second copy | NAND backup (`backups/nand/`), SD snapshot (`backups/sd/`) |

## Optical drive

Keep the original drive board with this motherboard. A random Wii U drive PCB is not a drop-in swap.

## SK Hynix note

Black 32 GB units often used SK Hynix eMMC that ages badly. That is extra reason to take the NAND backup as soon as the first entry point works, before PayloadLoader.
