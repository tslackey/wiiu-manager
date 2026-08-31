# macOS SD card notes

The Wii U is picky. macOS makes this worse in a few specific ways.

## Format

Target: **FAT32**, **MBR** (not GUID), label **`WIIUHB`**, 32 KiB allocation unit when possible.

Disk Utility GUI on modern macOS will offer ExFAT for cards over 32 GB and sometimes hides FAT32. Prefer:

```bash
./scripts/wiiu list-disks
./scripts/wiiu format-sd --disk diskN --confirm diskN
```

That wraps `diskutil` (`MS-DOS FAT32` + `MBR`). It refuses internal disks and disks that look like hard drives.

Manual equivalent if you ever need it:

```bash
diskutil list
diskutil unmountDisk /dev/diskN
diskutil partitionDisk /dev/diskN MBR "MS-DOS FAT32" WIIUHB R
```

Volume name **must not** be `wiiu` / `WIIU`. The official guide and common-issues page both call this out (browser `FSGetMountSource failed` / mount confusion).

## Merge, do not replace

Base Aroma and Payloads are two zips that both contain a top-level `wiiu/` folder. Finder’s default is **Replace**, which deletes the first zip’s files. The guide says: extract both, drag with **Merge** (hold **Option** if Merge does not appear).

`./scripts/wiiu stage` and `./scripts/wiiu copy-sd` merge in that sense. Use them instead of Finder when you can.

## Hidden files that break payload load

macOS writes:

- `.DS_Store`
- `._filename` AppleDouble siblings (these are the dangerous ones next to `payload.elf`)
- `.Spotlight-V100`, `.Trashes`, `.fseventsd`

The console can then throw `FSOpenFile failed ... payload.elf` even though Finder shows `payload.elf`.

```bash
./scripts/wiiu clean-junk /Volumes/WIIUHB
./scripts/wiiu verify /Volumes/WIIUHB
```

On macOS you can also run `dot_clean -m /Volumes/WIIUHB` after copying. The CLI already deletes junk names it knows about.

## Eject

Always:

```bash
./scripts/wiiu eject
```

or Finder Eject. Unplugging a busy card corrupts FAT32.

## Lock slider

If the physical lock is down, the Wii U may fail to mount the card. Aroma can also throw **150-3030** if the card is write-protected.

## Card type

SDHC 32 GB is the boring, compatible choice. SDXC (>32 GB) must still be FAT32, not ExFAT, unless the live guide changes. Avoid no-name cards; SanDisk / Samsung / PNY are what the FAQ suggests.

## After Aroma is installed

Keep a snapshot:

```bash
./scripts/wiiu backup-sd
```

That is much cheaper than reconstructing the card from zips after a Finder accident.
