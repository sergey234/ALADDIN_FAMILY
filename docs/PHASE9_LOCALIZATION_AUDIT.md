# Phase 9 Localization Audit (RU/EN)

Date: 2026-04-25

Scope reviewed:

- `Screens/09_ElderlyInterfaceScreen.swift`
- `Screens/08_ChildInterfaceScreen.swift`
- `Core/Localization/LocalizationManager.swift`
- `Resources/Localization/ru.lproj/Localizable.strings`
- `Resources/Localization/en.lproj/Localizable.strings`
- `scripts/localization_lint.py` output

## What is already localized (confirmed)

1. **Child + Elderly runtime keys are present**
   - Verified all keys used via `localizationManager.localized("...")` in child+elderly screens.
   - Result: `used_keys=284`, `missing_in_LocalizationManager=0`.

2. **Phase 9.1/9.3 core coverage exists in RU/EN**
   - `elderly_*`, `child_interface_*`, `child_contact_*`, `elderly_contact_*`, `family_role_elderly_label` are present in localization sources used by current code paths.

3. **No structural formatting corruption in Localizable.strings**
   - `ru.lproj/Localizable.strings`: no duplicate keys, no malformed quote/semicolon lines.
   - `en.lproj/Localizable.strings`: no duplicate keys, no malformed quote/semicolon lines.

4. **No Phase 9 key-miss regression found**
   - Current lint failure is not caused by Phase 9 keys; it is dominated by other modules (`network_protection_*`, and hardcoded strings across unrelated screens).

## What must be added next (to close 9.5 + Track B cleanly)

1. **Accessibility localization for 60+ modals/cards (priority for 9.5)**
   - `09_ElderlyInterfaceScreen.swift` currently has very limited a11y localization hooks (notably only a few `.accessibilityLabel(...)` entries).
   - Need to add localized `accessibilityLabel` / `accessibilityHint` for:
     - critical action cards/buttons (SOS, quick call, medications, protection),
     - health cards (medications, appointments, blood pressure, journal),
     - family/contact cards and edit actions in modal flows.

2. **60+ hardcoded UI fragments to convert into keys (targeted)**
   - Keep emoji-only strings as-is where they are purely decorative.
   - Convert remaining user-facing mixed/interpolated text that is still built inline and visible to user into namespaced keys where practical.

3. **Plural/grammar normalization for formatted keys**
   - Keys with `%d` in RU need grammar-safe variants or controlled wording.
   - Example risk areas: "через %d часа" style phrases.

4. **Global lint baseline debt (Track B blocker)**
   - Resolve EN missing keys in `network_protection_*`.
   - Remove hardcoded strings in unrelated screens reported by `scripts/localization_lint.py`.
   - Without this baseline cleanup, 9.5 merge gate (`localization-lint`) cannot be made strict for the whole repo.

## Anti-duplication / anti-noise rules (to avoid extra work)

1. Add new keys only in one namespace family per feature (`elderly_*` for 60+ flows).
2. Reuse existing keys before creating new ones.
3. Do not create parallel synonyms for the same semantic text.
4. Keep placeholders parity RU/EN (`%@`, `%d`, argument order).
5. Avoid embedding extra quotes/brackets in values unless required by UX copy.

## Current conclusion

- Phase 9 runtime localization foundation is healthy.
- Main remaining work is **9.5 accessibility coverage for 60+ flows** + **global baseline lint debt cleanup** required by Track B quality gates.
