# Notifications Security Release Gate

## Purpose

Block release if the security notifications chain is not proven end-to-end:

`detect -> ingest -> notifications store -> /api/notifications -> iOS UI`

## Blocking Criteria (ALL required)

- [ ] Preflight checklist passes on real device (permissions + filters).
- [ ] QA smoke scenario executed with valid `correlation_id`.
- [ ] Notifications screen shows event with `ID: <correlation_id>`.
- [ ] `/api/notifications` evidence includes same correlation id.
- [ ] `/api/notifications/read` evidence: `success=true`, non-negative `unreadCount`.
- [ ] No `notifications_contract_violation` alerts during validation window.
- [ ] Lifecycle matrix minimum set passed:
  - [ ] foreground
  - [ ] background
  - [ ] terminated
- [ ] Proof report completed using template:
  - `docs/observability/NOTIFICATIONS_SECURITY_PROOF_REPORT_TEMPLATE.md`

## Fail Conditions (auto-release block)

- Any contract violation in production candidate run.
- Missing proof artifacts.
- Correlation mismatch between UI and API.
- Fallback-only behavior without successful backend reconciliation.

## Ownership

- QA Lead: execution + artifact completeness.
- iOS Lead: client behavior and UI consistency.
- Backend Lead: ingest/store/API contract integrity.
- Release Manager: final gate decision.
