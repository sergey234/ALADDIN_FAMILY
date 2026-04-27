# Phase 9.5 Validation (Elderly Accessibility Localization)

Scope:

- `9.5` — localize accessibility labels and hints for elderly cards/modals/actions.

## Smoke command

Run:

`python3 scripts/phase9_elderly_accessibility_localization_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. Elderly screen uses localized accessibility labels/hints on critical controls:
   - SOS / emergency
   - quick family call
   - medications action
   - contact edit/delete actions
2. Required `elderly_a11y_*` keys and permission-notice key exist in localization maps.
3. Accessibility coverage has minimum threshold in screen code.
4. Build succeeds on iPhone 16 simulator.
