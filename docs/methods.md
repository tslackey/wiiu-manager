# Method overview (why this repo picks Aroma)

High-level only. Installation clicks live on https://wiiu.hacks.guide/.

For a stock NA Deluxe on 5.5.x, the maintained path is:

**browser (or current DNS) entry → EnvironmentLoader → NAND dump → Aroma → PayloadLoader**

That is what `wiiu fetch --profile recommended` prepares.

## Comparison (operator-relevant)

| Approach | Use on this console? | Notes |
| --- | --- | --- |
| Browser entry + Aroma | **Yes — default** | Matches the current Hacks Guide. SD + internet. |
| DNS entry (DNSpresso) | Fallback if the guide still lists it and the browser path fails | Same SD payload; different trigger |
| Haxchi / CBHC | **No** for a fresh install | Legacy DS-VC patch; high brick cost; uninstall first if already present |
| Tiramisu | Only to run old `.elf` apps | Archived; Aroma succeeded it |
| vWii game exploits (Smash Stack, etc.) | Later, optional, vWii-only | Possible because this unit has a disc drive |
| de_Fuse RP2040 | Recovery if already bricked | Soldering; not a convenience jailbreak |

## Layers people conflate

1. **Wii U OS / Aroma** — this project
2. **vWii** — Wii mode, separate NAND (`slccmpt`), separate guides
3. **GameCube** — not a Wii U mode; typically Nintendont under vWii
4. **GamePad** — display/controller; you do not “homebrew the GamePad” to install Aroma

## Research notes

A longer method catalog (legal/warranty framing, flowchart-level comparison) is in [context/research-summary.md](context/research-summary.md). Treat it as background. If it conflicts with the live Hacks Guide, ignore it.
