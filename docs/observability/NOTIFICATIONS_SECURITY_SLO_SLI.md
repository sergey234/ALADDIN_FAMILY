# Notifications Security SLO/SLI

## Scope

This document defines service levels for the security notifications pipeline:

`detect -> ingest -> notifications store -> /api/notifications -> iOS UI`

## SLI Definitions

- **SLI-1: End-to-end visibility latency (critical)**
  - Time from event detection timestamp to visibility on Notifications screen.
  - Measured by shared `correlation_id`.
- **SLI-2: Persisted event success rate**
  - Ratio of security events that appear in backend notifications store.
- **SLI-3: UI reconciliation success**
  - Ratio of push/local events that are reconciled by backend fetch in app session.
- **SLI-4: Contract validity rate**
  - Ratio of `/api/notifications` responses that pass client contract validation.

## SLO Targets

- **SLO-1 (Latency):** p95 critical event visible in UI in **< 5 seconds**.
- **SLO-2 (Persistence):** daily persisted security event success **>= 99.0%**.
- **SLO-3 (Reconciliation):** push/local-to-backend reconciliation **>= 99.5%**.
- **SLO-4 (Contract):** contract-valid responses from notifications endpoints **>= 99.9%**.

## Alerting Thresholds

- Trigger warning if:
  - `security_events == 0` for 24h while active devices > 0.
  - contract violations > 0.1% over 1h.
  - p95 latency exceeds 5s for 3 consecutive windows.
- Trigger critical if:
  - notifications endpoint unavailable > 5 min.
  - persisted event success drops below 98% for 1h.

## Ownership

- **Mobile iOS:** client validation, UI visibility, reconciliation behavior.
- **Backend:** event ingest, persistence, notifications API contract.
- **QA/Release:** smoke cadence, proof-report completeness, release gate checks.
