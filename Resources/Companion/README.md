# Companion hero assets (P1-08)

- `unicorn.riv` / `aladdin.riv` / `genie.riv` — runtime bundle (iOS).
- **Editor source:** `unicorn_source.rev` (правки только в `.rev`, не в runtime `.riv`).
- **Backups:** `backups/2026-06-17/` — снимок перед merge 2026-06-17.
- PNG fallbacks: `{unicorn,aladdin,genie}_master.png` (360×480).

## Unicorn golden (2026-06-17)

- **Runtime:** `unicorn.riv` — built via RiveMCP (`Hero360`, `Face`, `HeroSM`, `mouth_open`, 13 triggers).
- **Editor:** `unicorn_golden.rev` / `unicorn_source.rev` — open in Rive.app for polish.
- **Backups:** `backups/2026-06-17/` before rebuild.

Verify:

```bash
python3 scripts/companion_07_verify_unicorn_riv.py unicorn
```

**uni-14 (2026-06-17):** all 13 `*_anim` have keyframes; `sad`/`comfort`/`alert` sparkle=0; `playful`/`celebrate` sparkle on.

Remaining for 100%: **device QA** (Hub 96pt, Conversation, TTS `mouth_open`) + clone → aladdin/genie.

- Inputs match `CompanionHeroRiveMapping.riveStateName` (`idle`, `happy`, `listening`, …).
- `CompanionHeroRiveHost.swift` — `HeroSM` + `mouth_open`.
- **UI:** Conversation = rect full-body 360×480; Hub = 96pt circle.
