# Background research summary

Condensed from a pre-session research report. **Not** install instructions. The live [Wii U Hacks Guide](https://wiiu.hacks.guide/) is the procedure.

## Fit for this hardware

Black Deluxe WUP-101, disc drive, vWii capable. Software entry points that work on 5.5.x apply. Disc-based *Wii* exploits are possible later because of the drive; they are irrelevant to installing Aroma.

NA firmware expected in the 5.5.6 generation.

## Entry / CFW landscape (names only)

- **Browser entry** — current guide default; SD payload + Wii U Internet Browser
- **DNS entry (DNSpresso)** — alternate software entry using a crafted DNS during connection test
- **Haxchi / CBHC** — old persistent CFW via a DS Virtual Console title; avoid on a fresh install
- **Aroma / (legacy Tiramisu)** — environments loaded by EnvironmentLoader; Aroma is current
- **PayloadLoader** — Health & Safety injector so you are not stuck on the browser
- **de_Fuse** — RP2040 boot-ROM hardware recovery; soldering; last resort

## Policy notes the operator should not be surprised by

- Nintendo EULA forbids unauthorized modification; brick/warranty language is explicit
- Anti-circumvention law may apply (US DMCA commonly cited); this is not legal advice
- Hacks Guide FAQ: typical homebrew is not what they describe as a Nintendo console ban trigger; online cheating and eShop fraud are
- SK Hynix eMMC on many 32 GB units: dump NAND early

## Decision the operator already made

Browser (or current official alternative) → Aroma → extras. vWii/GameCube later. Hardware mods only if the board is otherwise dead.
