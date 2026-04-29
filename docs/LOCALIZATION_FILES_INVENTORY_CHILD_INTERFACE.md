# Child Interface Localization Files Inventory

Updated: 2026-04-29
Scope: files that directly affect translation/localization behavior in child interface runtime.

## 1) Core Localization Runtime

- `Core/Localization/LocalizationManager.swift`
- `Resources/Localization/ru.lproj/Localizable.strings`
- `Resources/Localization/en.lproj/Localizable.strings`

## 2) Child UI Screens Using Localization

- `Screens/08_ChildInterfaceScreen.swift`
- `Screens/ChildContentScreen.swift`
- `Screens/ChildContentExperienceScreen.swift`
- `Screens/ChildSafetyInstructionsModal.swift`

## 3) Child Content Data That Can Bypass i18n Keys

- `Core/Content/Seed/ContentSeedProvider.swift` (metadata titles/subtitles/descriptions)
- `Core/Content/Models/ContentModels.swift` (`ContentMetadata` fields rendered in UI)
- `Core/Content/ContentManager.swift` (content loading path to child feed)

## 4) Validation Gates and Quality Scripts

- `scripts/child_localization_gate.py`
- `scripts/localization_lint.py`
- `scripts/phase2_content_qa_matrix_smoke.py`

## 5) Canonical Documents for Policy and Handoff

- `docs/CHILD_CONTENT_FINAL_SYSTEM_HANDOFF.md`
- `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`
- `docs/LOCALIZATION_PR_CHECKLIST.md`
- `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`
- `docs/PLAN_ITEM_275_AUDIT_REPORT.md`

## 6) Notes

- Child core gate validates `child_*` keys used in the three main child screens.
- Not all runtime texts in child experience are guaranteed to come from `child_*` keys; some are content metadata literals.
