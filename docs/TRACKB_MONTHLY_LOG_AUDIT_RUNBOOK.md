# Track B Monthly Log Audit Runbook

Goal:

- enforce recurring monthly audit of operational/security logs.

## Monthly process

1. Export latest diagnostics via in-app Visual Logger (`Export` and `Share Trace` artifacts).
2. Review startup trace, lifecycle trace, and visual logs.
3. Record findings: anomalies, PII exposure risk, repeated failures, unresolved warnings.
4. Create audit record with timestamp, reviewer, and actions.

## Required artifacts

- `Documents/aladdin_latest_export_manifest.json` (from app container)
- latest `visual-logs-*.txt`
- `startup_trace.txt`
- `app_lifecycle_trace.txt`

## Recurrence policy

- frequency: monthly;
- owner: release/on-call engineer;
- SLA: audit report prepared within 3 business days after month close.

## Validation

Run:

`python3 scripts/trackb_monthly_log_audit_smoke.py`

Expected:

- `SMOKE RESULT: PASS`
