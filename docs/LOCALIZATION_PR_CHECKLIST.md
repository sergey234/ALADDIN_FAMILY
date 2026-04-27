# Localization PR Checklist (RU/EN)

Use this checklist in every PR that implements tasks from `NEXT_VERSION_IMPLEMENTATION_PLAN.md`.

## 1) Scope and keys

- [ ] All new user-facing texts are key-based, not literal strings.
- [ ] New keys follow namespace style (`family.*`, `parental.*`, `settings.*`, `profile.*`, `privacy.*`, `errors.*`, `common.*`).
- [ ] One meaning uses one key; no duplicate semantic keys added.

## 2) RU/EN parity

- [ ] Every new/changed key exists in both files:
  - `Resources/Localization/ru.lproj/Localizable.strings`
  - `Resources/Localization/en.lproj/Localizable.strings`
- [ ] RU and EN values are complete and product-correct.
- [ ] No mixed-language output in one user-visible string.

## 3) Quality of string values

- [ ] No extra quotes in final user text.
- [ ] No noisy nested brackets or redundant punctuation patterns.
- [ ] No technical jargon in user text unless explicitly approved.

## 4) Placeholder safety

- [ ] Placeholders are consistent between RU and EN (`%@`, `%d`, etc.).
- [ ] Placeholder count and intended order match in both locales.
- [ ] Runtime formatting paths are tested for at least one real example per changed key group.

## 5) Full UX coverage

- [ ] Happy-path labels localized.
- [ ] Error messages localized.
- [ ] Empty states localized.
- [ ] Loading/fallback messages localized.
- [ ] Alerts/sheets/buttons localized.

## 6) Accessibility coverage

- [ ] New/changed controls have localized accessibility labels.
- [ ] Localized accessibility hints and values are added where needed.
- [ ] VoiceOver flow was smoke-tested in RU and EN for changed screens.

## 7) Validation and testing

- [ ] Changed screens manually tested in RU.
- [ ] Changed screens manually tested in EN.
- [ ] `python3 scripts/localization_lint.py` (or scoped variant) passes and is attached to PR checks.
- [ ] Snapshot/UI tests updated where text assertions are used.
- [ ] No localization regressions in existing key screens.

## 8) Reviewer gate

- [ ] Reviewer confirmed no hardcoded user-facing strings in changed code.
- [ ] Reviewer confirmed no duplicate keys in changed localization sections.
- [ ] Reviewer confirmed parity of RU/EN for all changed keys.
- [ ] PR is blocked until all localization checks pass.

---

## Optional command hints for reviewers

Use these as quick checks during review:

- Detect possible hardcoded user strings in Swift:
  - `rg 'Text\\(".*[A-Za-zА-Яа-я].*"\\)|\\.title\\s*=\\s*".+"|UIAlertAction\\(title:\\s*".+"' --glob '*.swift'`
- Find duplicate keys in one localization file:
  - `rg '^[[:space:]]*"[^"]+"[[:space:]]*=' Resources/Localization/en.lproj/Localizable.strings`
  - `rg '^[[:space:]]*"[^"]+"[[:space:]]*=' Resources/Localization/ru.lproj/Localizable.strings`

Note: command output should be interpreted with context because some literal strings may be test-only or intentionally technical.

