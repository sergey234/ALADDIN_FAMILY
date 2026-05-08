# Notifications Security Alerts

## Implemented Client-Side Alert Hooks

The iOS client emits security alert signals for notification-pipeline anomalies via `ProductionMonitoringService`.

### Alert Codes

- `notifications_contract_violation` (critical)
  - Triggered when `/api/notifications` or `/api/notifications/read` violates contract checks.
- `notifications_local_fallback_activated` (warning)
  - Triggered when API fetch fails and local persisted security events are used.
- `notifications_empty_payload` (warning)
  - Triggered when notifications endpoint responds successfully but returns empty payload.

## Operational Threshold Guidance

- Warning escalation:
  - `notifications_empty_payload` appears repeatedly across active sessions.
- Critical escalation:
  - any `notifications_contract_violation` in production.
- Investigation priority:
  1. Contract violations
  2. Local fallback activations
  3. Sustained empty payload patterns

## Notes

- Client-side alerts complement backend monitoring and do not replace server-side ingestion checks.
- Correlation IDs should be used in proofs to connect client anomalies with backend traces.
