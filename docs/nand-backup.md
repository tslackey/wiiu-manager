# NAND backup

Official steps: [Making a NAND Backup](https://wiiu.hacks.guide/aroma/nand-backup.html)

Do this as soon as EnvironmentLoader can launch `nanddumper`, and **before** PayloadLoader.

## What you should end up with

On the SD root, then copied off:

| File | Why it matters |
| --- | --- |
| `slc.bin` | System NAND |
| `slccmpt.bin` | vWii NAND |
| `seeprom.bin` | Console EEPROM |
| `otp.bin` | Per-console keys — keep private |
| `mlc.bin.part*` | Optional user/MLC dump (needs SD larger than 32 GB internal) |

MLC holds saves and installed titles. Skipping MLC still leaves a useful brick-recovery set; restoring anything still needs ISFShax or hardware, per the guide.

## Mac-side

```bash
./scripts/wiiu collect-nand --delete-from-sd
```

- Copies into `backups/nand/nand-<utc-timestamp>/`
- Verifies sizes
- Deletes the dump files from the SD only after that check (the official guide frees the space this way)
- Writes a short README next to the files

Then duplicate that folder to another disk. These files are gitignored on purpose.

## Rules

- One dump belongs to one motherboard. Do not restore this onto a different Wii U.
- Do not rename casually.
- Do not keep the only copy on the SD card.
