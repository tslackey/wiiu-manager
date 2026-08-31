# wiiu-manager

Prepare a Wii U **Aroma** SD card from this Mac, using the current official packages.

This is not a replacement for the [Wii U Hacks Guide](https://wiiu.hacks.guide/). The scripts download the same Base Aroma / payload zips the guide tells you to download, format the card the way the Wii U expects, merge the folders (including the macOS Finder “Merge” problem), and strip junk files macOS likes to drop on SD cards.

Homebrew here means unsigned apps, save tools, and similar community software for a console you own. It does not mean downloading games you do not own.

## Requirements (macOS)

- A Wii U that **actually boots to the Wii U Menu** (a GamePad that turns on by itself is not enough)
- SD or SDHC card (32 GB is the size this project assumes)
- Built-in or USB card reader
- `python3` (Xcode CLT or Homebrew) and `curl`

```bash
xcode-select --install          # if python3 is missing
# or
brew install python
```

## Fast path

```bash
git clone https://github.com/tslackey/wiiu-manager.git
cd wiiu-manager
./scripts/wiiu doctor
./scripts/wiiu next
./scripts/wiiu fetch --profile recommended
./scripts/wiiu stage
./scripts/wiiu verify
```

Plug in the SD card, then identify it carefully:

```bash
./scripts/wiiu list-disks
```

`disk0` is almost always the internal SSD. Formatting the wrong disk destroys the Mac. When you are sure you have the SD reader (example `disk4`):

```bash
./scripts/wiiu format-sd --disk disk4 --confirm disk4
./scripts/wiiu copy-sd /Volumes/WIIUHB
./scripts/wiiu verify /Volumes/WIIUHB --profile recommended
./scripts/wiiu eject
```

Put the card in the Wii U and continue from the live guide:

1. [SD Preparation](https://wiiu.hacks.guide/aroma/sd-preparation.html) (files should already be in place)
2. [Browser Exploit](https://wiiu.hacks.guide/aroma/browser-exploit.html)
3. [NAND backup](https://wiiu.hacks.guide/aroma/nand-backup.html) **before** PayloadLoader
4. [Installing PayloadLoader](https://wiiu.hacks.guide/aroma/installing-payloadloader.html)
5. [Autobooting Aroma](https://wiiu.hacks.guide/aroma/autobooting.html)
6. [Blocking Updates](https://wiiu.hacks.guide/block-updates.html)
7. [Finalizing Setup](https://wiiu.hacks.guide/aroma/finalizing-setup.html)

After nanddumper writes files to the card:

```bash
./scripts/wiiu collect-nand --delete-from-sd
```

That copies `slc.bin`, `slccmpt.bin`, `seeprom.bin`, `otp.bin` (and any `mlc.bin.part*`) into `backups/nand/`, then removes them from the SD so you get the space back. Keep `otp.bin` private.

## Commands

| Command | What it does |
| --- | --- |
| `wiiu doctor` | Check python/curl/diskutil and repo files |
| `wiiu next` | Next checklist item for **this** console |
| `wiiu fetch [--profile recommended]` | Download official zips into `downloads/` |
| `wiiu stage` | Merge zips into `staging/sdroot/` |
| `wiiu verify [path]` | Check Aroma file layout; flag macOS junk |
| `wiiu list-disks` | Show disks; mark likely SD readers |
| `wiiu format-sd --disk ID --confirm ID` | Erase card, FAT32, label `WIIUHB` |
| `wiiu copy-sd [mount]` | Copy staged files onto the card |
| `wiiu clean-junk PATH` | Remove `.DS_Store` / `._*` files |
| `wiiu backup-sd` | Snapshot the card into `backups/sd/` |
| `wiiu collect-nand` | Archive NAND dump files from the card |
| `wiiu eject` | Eject `/Volumes/WIIUHB` |
| `wiiu set-firmware 5.5.6` | Record System Information version |
| `wiiu mark KEY` | Tick a checklist box |

Profiles: `base` (payloads + Aroma only), `recommended` (adds SaveMii, App Store, Bloopair, FTPiiU, SDCafiine, Screenshot, SwipSwapMe), `pretendo` (Inkay only, skip until you want Pretendo).

## macOS specifics

- Do **not** name the volume `wiiu`. That collides with homebrew.
- Finder will often **Replace** instead of **Merge** when combining two `wiiu` folders. `wiiu stage` / `wiiu copy-sd` merge in the sense the guide describes.
- Hidden `._payload.elf` files from Finder cause `FSOpenFile failed` style errors. Always eject via the CLI or Finder eject, never yank.
- Full notes: [docs/macos.md](docs/macos.md)

## Safety

Every system modification can brick a Wii U. Follow the live guide exactly, keep the console on a known-good power supply during writes, and do not skip the NAND backup.

Haxchi / Coldboot Haxchi are legacy. Do not install them.

## Layout of this repo

```
scripts/wiiu          CLI entrypoint
src/wiiu_manager/     Python 3 stdlib package
config/packages.json  Official download catalog
docs/                 Console profile, runbook, architecture
AGENTS.md             Steering for future agent sessions
```

Downloaded blobs and NAND dumps are gitignored (`downloads/`, `staging/`, `backups/`).

## Tests

```bash
python3 -m unittest discover -s tests -v
```
