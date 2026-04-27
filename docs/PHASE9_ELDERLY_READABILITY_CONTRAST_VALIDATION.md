# Phase 9.1 Validation (Large Read Mode + Contrast Presets)

Scope:

- `9.1` — complete large read mode for elderly interface.
- `9.1` — add contrast presets with system-wide application on the elderly screen.

## Smoke command

Run:

`python3 scripts/phase9_elderly_readability_contrast_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Contracts**
   - `elderly_large_read_mode` and `elderly_contrast_preset` settings exist.
   - elderly screen applies dynamic type + contrast modifiers.
   - settings modal exposes toggle/picker for read mode and contrast preset.
2. **Localization**
   - new keys for read mode and contrast presets exist in RU/EN maps.
3. **Build**
   - app build succeeds on iPhone 16 simulator.
