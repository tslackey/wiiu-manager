# vWii and GameCube — later

Do not start this until Aroma coldboots cleanly and the NAND backup is off the SD.

## vWii

The Wii U’s Wii compatibility OS is a separate environment. Modding it is **not** the Aroma guide. Use the vWii page linked from [Finalizing Setup](https://wiiu.hacks.guide/aroma/finalizing-setup.html) when you are ready.

This black Deluxe can use disc-based Wii entry points because it has a drive. That still does not make Smash Stack a substitute for Aroma.

vWii NAND is `slccmpt.bin` in your dump. Keep it.

## GameCube

There is no native Wii U GameCube mode like a Wii family edition. Typical stack:

```
owned disc dump on SD or USB  →  Nintendont on vWii  →  GameCube software
```

Folder layout and filesystem rules come from Nintendont’s own docs, not from Aroma. Use dumps of discs you own.

## USB reminder

Wii U Data Management formatted USB is invisible to the Mac. Keep Aroma on SD even after a USB library exists.

## Drive repair

If the optical drive is flaky, check cables first. Do not swap the drive **board** from another Wii U; it is paired. Mechanism swaps that keep the original board are a different, hardware-only topic.
