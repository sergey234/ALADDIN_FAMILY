## What changed

- Briefly describe what was implemented and why.

## Validation

- [ ] Unit tests executed where applicable
- [ ] UI/integration checks executed where applicable
- [ ] `python3 scripts/localization_lint.py` passed locally

## Localization (RU/EN) - Required

- [ ] New/updated user-facing text uses localization keys only (no hardcoded literals)
- [ ] RU keys added/updated in `Resources/Localization/ru.lproj/Localizable.strings`
- [ ] EN keys added/updated in `Resources/Localization/en.lproj/Localizable.strings`
- [ ] RU/EN key parity preserved (no missing keys on either side)
- [ ] Placeholder parity preserved (`%@`, `%d`, etc.)
- [ ] Error states, empty states, and loading/fallback messages localized
- [ ] Accessibility strings localized (`accessibilityLabel`, `accessibilityHint`, `accessibilityValue`)
- [ ] Namespace map followed (no semantic key duplicates)
- [ ] Localization standards reviewed:
  - [ ] `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`
  - [ ] `docs/LOCALIZATION_PR_CHECKLIST.md`
  - [ ] `docs/LOCALIZATION_KEY_NAMESPACE_MAP.md`

## Screenshots

Add screenshots for all changed UI screens in both locales.

### RU screenshots

- [ ] Attached

### EN screenshots

- [ ] Attached

## Risk and rollback

- Risk level: Low / Medium / High
- Rollback plan:
  - [ ] Revert PR
  - [ ] Feature flag rollback (if applicable)
  - [ ] Follow-up fix PR (if needed)

