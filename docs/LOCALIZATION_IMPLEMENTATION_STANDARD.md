# Localization Implementation Standard (RU/EN)

## Purpose

This standard defines how the team implements user-facing text in Russian and English while delivering tasks from `NEXT_VERSION_IMPLEMENTATION_PLAN.md`.

Main goal: every shipped feature is production-ready in RU and EN with no duplicate keys, no mixed-language UI text, and no noisy typography.

## Scope

Applies to:
- SwiftUI and UIKit user-facing text.
- Error messages, empty states, onboarding, settings, parental control flows.
- Accessibility strings: labels, hints, values.
- Test assertions that validate text behavior.

Current primary localization files:
- `Resources/Localization/ru.lproj/Localizable.strings`
- `Resources/Localization/en.lproj/Localizable.strings`

## Mandatory Rules

### 1) Dual-language delivery rule

Any new UI feature must include both RU and EN strings in the same PR.

A PR cannot be merged if:
- a new key exists only in one locale, or
- UI introduces hardcoded text bypassing localization keys.

### 2) No literal UI text in code

Do not hardcode user-facing strings in views or controllers.

Use localization keys only, for example:
- `Text(L("family.parent_mode.enter"))`
- `NSLocalizedString("parental.time_limit.title", comment: "")`

### 3) Stable key namespace

Use dot-separated semantic namespaces:
- `family.*`
- `parental.*`
- `settings.*`
- `profile.*`
- `privacy.*`
- `errors.*`
- `common.*`

Examples:
- `family.parent_mode.enter`
- `parental.time_limit.daily_title`
- `profile.data_export.request_sent`

### 4) One meaning equals one key

If text meaning is the same, reuse the key.
Do not create synonyms for the same UI intention.

### 5) Clean typography and content hygiene

For RU and EN values:
- no extra quotes;
- no double brackets or nested bracket noise;
- no RU and EN in one final user-visible string;
- no technical abbreviations for user-facing text unless product-approved.

### 6) Placeholder parity

If a key uses placeholders, RU and EN must have:
- same placeholder count;
- same placeholder types (`%@`, `%d`, etc.);
- same runtime argument order unless explicitly documented and tested.

### 7) Errors and empty states are mandatory

Each feature must localize not only happy-path labels but also:
- API/network errors;
- validation errors;
- empty states;
- loading fallback messages.

### 8) Accessibility localization is required

Localize all accessibility-facing strings:
- `accessibilityLabel`
- `accessibilityHint`
- `accessibilityValue`

### 9) No duplicate keys across active locales

Prevent:
- duplicate key names in the same file;
- same key with conflicting meaning across features.

### 10) Backward-safe key lifecycle

When renaming/removing keys:
- migrate all usages in the same PR;
- avoid breaking active screens;
- avoid leaving dead keys without cleanup task.

## Recommended Development Workflow Per Task

For each plan task:
1. Define feature string map (UI, errors, empty states, accessibility).
2. Add keys in EN and RU files in one commit.
3. Replace literals in code with keys.
4. Validate on device/simulator in RU and EN.
5. Run localization quality checks before merge.

## PR Gate (Localization)

A PR is blocked if at least one condition fails:
- New or changed feature has missing RU or EN key.
- User-facing hardcoded text is introduced.
- Duplicate localization keys are introduced.
- Placeholder mismatch exists between RU and EN.
- Accessibility text for new controls is not localized.

## QA Acceptance Criteria

For each shipped feature:
- RU and EN both render correctly in all primary screens.
- Text truncation is acceptable in supported Dynamic Type ranges.
- Error and empty-state messages are translated.
- VoiceOver reads localized labels and hints.

## Suggested Automation Checks

Pre-merge checks should include:
- Search for potential hardcoded strings in Swift files.
- Diff-based detection for newly added localization keys and parity check RU/EN.
- Duplicate key detection in `Localizable.strings`.
- Placeholder parity checks between RU and EN for changed keys.

## Ownership

- Feature developer: creates/updates keys and replaces literals.
- Reviewer: validates gate criteria and key quality.
- QA: validates RU/EN behavior on target screens and edge states.

