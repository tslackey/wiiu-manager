# Architecture

```
Black Wii U (WUP-101)
├── Wii U OS  ──► EnvironmentLoader ──► Aroma
│                    │                    ├── modules (.wms / setup .rpx)
│                    │                    ├── plugins (.wps)
│                    │                    └── apps (.wuhb on the Wii U Menu)
│                    └── nanddumper payload (one-shot, from EnvironmentLoader)
├── vWii (Wii compatibility)     ← separate later project
├── Optical disc drive           ← hardware, paired PCB
├── SD slot                      ← required for first install
└── USB                          ← later storage, not a substitute for SD
```

## Pieces this repo stages onto the SD card

| Path | Role |
| --- | --- |
| `wiiu/payload.elf` | First stage every current entry point loads |
| `wiiu/payload.rpx` | EnvironmentLoader |
| `wiiu/payloads/default/payload.elf` | Default EnvironmentLoader payload |
| `wiiu/payloads/nanddumper/payload.elf` | NAND dump tool |
| `wiiu/environments/aroma/` | Aroma environment |
| `wiiu/apps/PayloadLoaderInstaller.wuhb` | Installs PayloadLoader into Health & Safety |
| `wiiu/apps/AromaUpdater.wuhb` | Updates Aroma from the console later |

Aroma is an **environment** loaded by EnvironmentLoader. PayloadLoader is a **persistent launcher** installed into the Health & Safety title so you do not need the browser every boot. Autobooting that title is a separate, optional guide page.

## Why not Tiramisu / Haxchi

- **Tiramisu** is archived. Aroma replaced it. Only keep Tiramisu on the SD if a specific legacy `.elf` app still needs it.
- **Haxchi / CBHC** patch a DS Virtual Console title and were the old persistent CFW. High brick risk, obsolete for a fresh 5.5.x install. If this console already had CBHC, uninstall it using the live guide *before* Aroma.

## Homebrew formats

- **`.wuhb`** — Aroma-native, appears on the Wii U Menu via `homebrew_on_menu`
- **`.rpx` / `.wps` / `.wms`** — environment pieces
- **`.elf` Homebrew Launcher apps** — generally **do not** run on Aroma

## USB vs SD

The first install must use SD. USB can hold extra data later. A “Wii U formatted” USB drive is unreadable on the Mac until reformatted.
