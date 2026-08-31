# Safety

## Before any modification

- Console reaches the Wii U Menu on stable power.
- You have read the danger notice on https://wiiu.hacks.guide/ (unrecoverable brick is rare, not zero).
- SD card is a copy you can afford to erase.
- You will not skip the NAND backup.

## During writes

- Stay plugged into the adapter, not a dying battery-backed strip.
- Do not yank the SD card, power off, or quit an installer until it says it is done.
- If something throws a code, write the code down before trying a second guide.

## Persistent changes

PayloadLoader lives in Health & Safety. A **factory reset will not remove it**. Uninstall only via the current official uninstall page.

## Data you must treat as secret

`otp.bin` (and the rest of the NAND dump) identifies this console. Store it in `backups/nand/` and a second offline copy. Never commit it, never paste it into a chat, never mix it with someone else’s dump.

## Legal / policy (plain language)

- Nintendo’s EULA forbids unauthorized modification; they can refuse service.
- Circumventing console protections can be illegal depending on jurisdiction (US DMCA is the usual citation). This repo does not give legal advice.
- Using homebrew is not the same as downloading commercial games you do not own. This project will not help with the latter.
- Community consensus (see the Hacks Guide FAQ): ordinary homebrew is not what Nintendo bans Wii U consoles for; cheating online and eShop fraud are.

## Out of scope without a new, explicit request

- Soldering / de_Fuse
- Installing CBHC on a healthy 5.5.x unit
- “Download this list of games”
- Sharing otp dumps
