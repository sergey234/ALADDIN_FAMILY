# Child Localization Bundle Recovery Runbook

Updated: 2026-04-29

## Why this exists

Incident pattern: child screens render mixed UI where some labels are translated and some show raw keys like `child_daily_journey_*` or `child_creative_output_*`.

Root cause that was confirmed:

- `Resources/Localization/*/Localizable.strings` was not included in `Copy Bundle Resources` for the main app target.
- Runtime fallback in `LocalizationManager` was too narrow for nested localization paths.

## 100% Recovery Steps

1. Confirm resources are in app bundle config:
   - File: `ALADDIN.xcodeproj/project.pbxproj`
   - `Resources/Localization` must be present in:
     - app group children
     - `PBXResourcesBuildPhase` (`Localization in Resources`)
2. Confirm runtime resolver supports nested localization dirs:
   - File: `Core/Localization/LocalizationManager.swift`
   - `localizedFromBundle(...)` should search:
     - `<lang>.lproj`
     - `Localization/<lang>.lproj`
     - `Resources/Localization/<lang>.lproj`
   - plus fallback scan of bundle `.strings` URLs.
3. Clean and reset simulator state:
   - `Product -> Clean Build Folder` (`Shift+Cmd+K`)
   - delete app from simulator
   - run again

## Fast Verification (must-pass)

### Visual smoke in child UI

Check `1-6 -> Toys`:

- `child_daily_journey_title` -> "Путь на сегодня" / "Today's Journey"
- `child_daily_journey_step_discover` -> "Изучить" / "Discover"
- `child_daily_journey_step_practice` -> "Тренировка" / "Practice"
- `child_daily_journey_step_reflect` -> "Итог" / "Reflect"
- `child_creative_output_title` -> "Твоя творческая работа" / "Your Creative Output"

If any `child_*` is visible on screen, localization is still broken.

### Script gates

Run:

- `python3 scripts/child_localization_gate.py`
- `python3 scripts/child_runtime_localization_integrity.py`
- `python3 scripts/localization_lint.py`

## Operational Rule For Future Changes

Any child UI change that adds/uses `child_*` keys must include in the same change set:

1. RU + EN entries in `Resources/Localization/*/Localizable.strings`
2. Gate rerun evidence
3. Bundle-resource presence check in project file if localization files/folders were moved

## Quick Triage Matrix

- Raw keys only in child UI -> check bundle resources first.
- Raw keys in both RU/EN -> key missing in both files or resolver miss.
- Works after reinstall only -> stale simulator app data/build cache.
- Empty content then appears later -> content lifecycle timing/sync, not translation source itself.
