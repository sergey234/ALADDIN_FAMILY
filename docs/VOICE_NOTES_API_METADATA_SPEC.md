# Voice Notes API Metadata Spec

## Scope

Required metadata fields for future Voice Notes API requests.

## Required Fields

- `source: string`
  - Allowed values: `voice_notes`, `call_assistant`, `ai_assistant`
  - Purpose: attribution and analytics segmentation.

- `consent_flags: object`
  - Example:
    - `audio_recording_consent: bool`
    - `cloud_processing_consent: bool`
    - `policy_version: string`
  - Purpose: legal and compliance tracking.

- `encryption_version: string`
  - Example: `ios-local-v1`, `ios-cloud-v2`
  - Purpose: track cryptographic scheme compatibility.

- `retention_policy_days: int`
  - Allowed values: `30`, `90`, `180` (or policy-driven)
  - Purpose: lifecycle and purge logic.

## Optional Recommended Fields

- `client_note_id: string` (UUID)
- `device_model: string`
- `ios_version: string`
- `app_build: string`
- `locale: string`
- `created_at_client: ISO8601`

## Validation Rules

- Reject requests without required fields.
- Reject unknown `source` values.
- Reject `retention_policy_days <= 0`.
- Reject `encryption_version` not in allowlist.

## Privacy Notes

- Metadata must not contain raw transcript snippets unless explicitly required.
- Avoid sending PII in free-form metadata.
- Consent flags are immutable audit records per note version.
