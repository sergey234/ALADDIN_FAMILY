# Localization Key Namespace Map

## Purpose

This map defines a stable naming convention for localization keys across core application screens.
It is the reference for all new tasks from `NEXT_VERSION_IMPLEMENTATION_PLAN.md`.

Use together with:
- `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md`
- `docs/LOCALIZATION_PR_CHECKLIST.md`

## Global Naming Rules

- Format: `domain.section.element.state`
- Use lowercase and dot-separated words.
- Do not include locale in key name.
- Do not include implementation details (view model names, API names, etc.).
- One meaning equals one key.

Examples:
- `family.parent_mode.enter`
- `parental.time_limit.daily.title`
- `settings.language.selector.title`
- `profile.data_export.request.success`
- `privacy.consent.required.message`

## Shared Namespaces

These keys are reused across multiple screens.

- `common.*`
  - buttons: `common.button.save`, `common.button.cancel`, `common.button.retry`
  - status: `common.status.loading`, `common.status.success`, `common.status.error`
  - empty states: `common.empty.title`, `common.empty.description`
- `errors.*`
  - network: `errors.network.title`, `errors.network.timeout`, `errors.network.offline`
  - validation: `errors.validation.required`, `errors.validation.invalid_format`
  - backend: `errors.api.generic`, `errors.api.unauthorized`
- `a11y.*`
  - labels: `a11y.family.member_card.label`
  - hints: `a11y.parental.time_limit.hint`
  - values: `a11y.profile.subscription.value`

## Screen-Level Namespaces

## 1) Family Screen

Target screen:
- `Screens/02_FamilyScreen.swift`

Namespace:
- `family.*`

Sections:
- `family.screen.*`
  - `family.screen.title`
  - `family.screen.subtitle`
- `family.member.*`
  - `family.member.add.button`
  - `family.member.remove.confirm_title`
  - `family.member.role.parent`
  - `family.member.role.child`
- `family.parent_mode.*`
  - `family.parent_mode.enter`
  - `family.parent_mode.exit`
  - `family.parent_mode.locked_message`
- `family.invite.*`
  - `family.invite.code.title`
  - `family.invite.code.copy_success`
  - `family.invite.join.success`

Do not duplicate with:
- parental control statuses (`parental.*`)
- global settings labels (`settings.*`)

## 2) Parental Control Screen

Target screen:
- `Screens/07_ParentalControlScreen.swift`

Namespace:
- `parental.*`

Sections:
- `parental.screen.*`
  - `parental.screen.title`
  - `parental.screen.subtitle`
- `parental.card.*`
  - `parental.card.time_limits.title`
  - `parental.card.content_filters.title`
  - `parental.card.activity.title`
  - `parental.card.safety.title`
- `parental.time_limit.*`
  - `parental.time_limit.daily.title`
  - `parental.time_limit.weekly.title`
  - `parental.time_limit.limit_reached.message`
- `parental.content_filter.*`
  - `parental.content_filter.level.safe`
  - `parental.content_filter.level.moderate`
  - `parental.content_filter.level.strict`
- `parental.pin.*`
  - `parental.pin.setup.title`
  - `parental.pin.verify.title`
  - `parental.pin.invalid.message`
- `parental.authorization.*`
  - `parental.authorization.family_controls.required`
  - `parental.authorization.approved`
  - `parental.authorization.denied`

Do not duplicate with:
- family roster actions (`family.member.*`)
- account profile actions (`profile.*`)

## 3) Settings Screen

Target screen:
- `Screens/05_SettingsScreen.swift`

Namespace:
- `settings.*`

Sections:
- `settings.screen.*`
  - `settings.screen.title`
- `settings.language.*`
  - `settings.language.title`
  - `settings.language.selector.title`
  - `settings.language.apply.success`
- `settings.security.*`
  - `settings.security.title`
  - `settings.security.biometric.enable`
  - `settings.security.biometric.disable`
- `settings.audio.*`
  - `settings.audio.title`
  - `settings.audio.master_volume`
  - `settings.audio.effects_volume`
- `settings.accessibility.*`
  - `settings.accessibility.title`
  - `settings.accessibility.reduce_motion`
  - `settings.accessibility.dynamic_type`

Do not duplicate with:
- legal text keys (`privacy.*`, `terms.*`)
- profile account actions (`profile.account.*`)

## 4) Profile Screen

Target screen:
- `Screens/11_ProfileScreen.swift`

Namespace:
- `profile.*`

Sections:
- `profile.screen.*`
  - `profile.screen.title`
- `profile.account.*`
  - `profile.account.email.label`
  - `profile.account.subscription.status`
- `profile.data_export.*`
  - `profile.data_export.title`
  - `profile.data_export.request.button`
  - `profile.data_export.request.success`
- `profile.data_delete.*`
  - `profile.data_delete.title`
  - `profile.data_delete.confirm_input_hint`
  - `profile.data_delete.success`
- `profile.family_link.*`
  - `profile.family_link.title`
  - `profile.family_link.manage.button`

Do not duplicate with:
- privacy legal body text (`privacy.policy.*`)
- family operational UI (`family.*`)

## 5) Privacy and Legal Screens

Target screens:
- `Screens/18_PrivacyPolicyScreen.swift`
- `Screens/19_TermsOfServiceScreen.swift`

Namespace:
- `privacy.*`
- `terms.*`
- `consent.*`

Sections:
- `privacy.screen.*`
  - `privacy.screen.title`
  - `privacy.screen.last_updated`
- `privacy.policy.*`
  - `privacy.policy.intro`
  - `privacy.policy.data_usage`
  - `privacy.policy.contact`
- `terms.screen.*`
  - `terms.screen.title`
- `terms.section.*`
  - `terms.section.acceptance`
  - `terms.section.liability`
- `consent.*`
  - `consent.required.title`
  - `consent.required.message`
  - `consent.accept.button`
  - `consent.decline.button`

## Feature Extensions (for plan tasks)

Use dedicated top-level domains for major new modules:
- `content.*` for content architecture and catalog UX
- `progress.*` for achievements, streaks, learning path
- `rewards.*` for reward animations and feedback copy
- `testflight.*` only for internal debug builds if UI is exposed

## Anti-Duplicate Policy

Before adding a key:
1. Search existing locale files for same meaning.
2. Reuse an existing `common.*` or domain key when possible.
3. If text differs by context, encode context in namespace, not in random suffixes.

Avoid unstable suffixes:
- `_new`
- `_v2`
- `_temp`
- `_final`

Use semantic suffixes:
- `.title`
- `.subtitle`
- `.description`
- `.button`
- `.hint`
- `.error`
- `.success`

## Placeholder and Pluralization Rules

- For placeholders, keep parity between RU and EN.
- Prefer explicit semantic keys for singular/plural forms where needed.
- If advanced pluralization is introduced, document pattern in the implementation PR.

## Example Mapping Table

| Product task | Screen | Key domain |
|---|---|---|
| Add parent mode entry | Family | `family.parent_mode.*` |
| Add daily limit setup | Parental Control | `parental.time_limit.*` |
| Add biometric toggle copy | Settings | `settings.security.*` |
| Add data export request flow | Profile | `profile.data_export.*` |
| Add consent confirmation flow | Privacy/Onboarding | `consent.*` |

