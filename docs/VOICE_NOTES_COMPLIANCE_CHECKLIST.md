# Voice Notes Compliance Checklist

## Objective

Define compliance baseline for audio features (Voice Notes and Call Assistant notes) with local-first privacy model.

## Consent Onboarding

- Show clear consent screen before first recording.
- Explain:
  - recording purpose,
  - local-only storage default,
  - optional cloud mode (future, opt-in only).
- Require explicit user action to proceed.

## Retention Policy

- Support retention presets:
  - `30 days`
  - `90 days`
  - `Never auto-delete` (if policy allows)
- Display active retention setting in feature settings.
- Provide manual delete and bulk delete.

## Policy & Disclaimer Text

- In-feature disclaimer:
  - "Records are stored only on this device" (local-only mode).
- Legal policy link from Voice Notes screen.
- Versioned policy acceptance record.

## Security/Compliance Controls

- TLS-only for any network transport.
- Encryption at rest for local metadata/audio where feasible.
- No raw audio in application logs.
- Access control for exported files.

## Data Subject Actions

- User can delete any note permanently.
- User can export note manually.
- User can disable feature at any time.

## Audit Requirements (Future Sync Mode)

- Keep immutable consent flags per note/version.
- Track retention and purge events.
- Log policy version used at recording time.

## Release Gate

Feature is not production-ready unless:

- onboarding consent exists,
- retention policy controls are visible,
- disclaimer is localized RU/EN,
- deletion flow verified via QA smoke.
