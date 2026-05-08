# Notifications Security Event Policy

## Scope

This policy defines how ALADDIN iOS handles security notifications for:

- `threat_detected`
- `security_alert`
- `phishing_blocked`
- `bypass_attempt` / `attempt_bypass`

## Source Of Truth

- The authoritative source for Notifications screen history is backend `GET /api/notifications`.
- Push/local notifications are UX accelerators only and must be reconciled with backend immediately.
- Client logic must not treat local delivery as confirmation that security action is persisted.

## Contract Requirements (`/api/notifications`)

Each security notification must provide:

- non-empty `id`
- non-empty `title`
- non-empty `message`
- non-empty `type`
- valid correlation id (`correlation_id` or `event_id` or dedicated response field)

Rejected at client-contract level:

- explicit mock/fallback event sources (`mock`, `fallback`, `sfm_*`)
- negative counters or invalid unread semantics

## Contract Requirements (`/api/notifications/read`)

Expected:

- `success == true`
- `unreadCount >= 0`

If contract is violated, client must fail-fast with explicit contract error.

## Operational Notes

- The Notifications screen must expose load errors and health status in debug workflows.
- QA smoke scenario should always include correlation id and verify server reconciliation.
