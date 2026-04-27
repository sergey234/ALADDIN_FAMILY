# Phase 9.5 Validation (Elderly UX RU/EN)

Scope:

- `9.5` — localize all elderly (60+) scenarios in RU/EN without hardcoded UI text.
- `9.5` — add UX smoke validation for RU/EN with large text and high contrast contracts.

## Smoke command

Run:

`python3 scripts/phase9_elderly_ux_ru_en_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. All `localized("key")` usages in `Screens/09_ElderlyInterfaceScreen.swift` are backed by keys in `Core/Localization/LocalizationManager.swift`.
2. Scoped `localization-lint` gate passes for 60+ scope:
   - `python3 scripts/localization_lint.py --scope elderly60plus`
3. Large text and contrast contracts exist and are applied:
   - `elderly_large_read_mode`
   - `elderly_contrast_preset`
   - `.dynamicTypeSize(elderlyDynamicType)`
   - `.contrast(elderlyContrastValue)`
4. Build succeeds on iPhone 16 simulator.
