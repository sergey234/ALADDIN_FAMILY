# Voice Notes Backend API Design (For Future Sync Mode)

## Status

Current product mode is **local-only** for Voice Notes.  
This API design is prepared for future optional sync mode and is not enabled by default.

## Goals

- Keep local-only as default behavior.
- Support optional secure sync for users who explicitly opt in.
- Separate raw audio handling from metadata workflows.

## Endpoints

## 1) Create Voice Note Metadata

- `POST /api/voice-notes`
- Purpose: create metadata record before optional upload.
- Request:
  - `title: string`
  - `duration_sec: int`
  - `source: string` (`voice_notes`, `call_assistant`)
  - `consent_flags: object`
  - `encryption_version: string`
  - `retention_policy_days: int`
- Response:
  - `voice_note_id`
  - `upload_url` (optional pre-signed URL)
  - `created_at`

## 2) Upload Audio (Optional)

- `PUT <upload_url>` or `POST /api/voice-notes/{id}/audio`
- Purpose: upload encrypted audio blob.
- Request:
  - binary audio (`m4a`)
  - checksum header
- Response:
  - `audio_uploaded: true`
  - `audio_size_bytes`

## 3) Trigger Transcription

- `POST /api/voice-notes/{id}/transcribe`
- Purpose: start server transcription (future mode only).
- Request:
  - `language: string`
  - `model: string`
- Response:
  - `job_id`
  - `status: queued|running|done|failed`

## 4) Trigger Summary

- `POST /api/voice-notes/{id}/summary`
- Purpose: generate/refresh summary.
- Request:
  - `strategy: concise|detailed|action-items`
  - `version_from: int` (optional)
- Response:
  - `summary_text`
  - `summary_confidence`
  - `summary_version`

## 5) List Notes

- `GET /api/voice-notes?cursor=...&limit=...`
- Response:
  - paginated notes
  - summary metadata
  - sync timestamps

## 6) Update Note

- `PATCH /api/voice-notes/{id}`
- Purpose: update title/tags/summary.

## 7) Delete Note

- `DELETE /api/voice-notes/{id}`
- Purpose: soft delete with retention policy, then purge.

## Data Contract Notes

- `voice_note_id` is server UUID.
- `client_note_id` is local UUID for reconciliation.
- All responses include `updated_at`.
- Server never returns raw audio in list endpoints.

## Rollout Strategy

1. Keep local-only default.
2. Add feature flag + explicit user consent.
3. Run pilot with low retention and strict audit logging.
