# Original plan (operator notes)

Adapted from the operator’s pre-session outline. Kept so future agents know the *intent*, not as a substitute for the live Hacks Guide.

## Console

Black Wii U with optical drive. GamePad powers independently. Console had a suspected PSU failure; a replacement OEM-compatible brick was ordered. Homebrew waits on a real Wii U Menu boot. Record firmware from System Settings → System Information.

## Approach

1. Prepare SD (this repo).
2. Current Wii U Hacks Guide entry for the firmware.
3. Aroma.
4. EnvironmentLoader / PayloadLoader as the guide directs.
5. NAND backup, stored in more than one place.
6. Only the homebrew actually needed.
7. Wii / vWii / GameCube as later, separate layers.

Do not start from Haxchi or Coldboot Haxchi.

## SD

Full-size SD/SDHC, 32 GB, FAT32, official package layout only. Back up the card if it had anything on it before format.

## Safety the operator already agreed to

- Untouched NAND backup
- No random system titles from untrusted sources
- One current guide per task
- Stable power during writes
- Do not interrupt firmware/system writes
- Record error codes before changing course
- Homebrew ≠ piracy; own-game dumps only
