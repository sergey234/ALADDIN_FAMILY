# Rollout / Rollback Checklist

## Pre-Rollout
- Verify gateway runtime on `:8002`:
  - `curl -s http://149.154.65.180:8002/api/health`
- Confirm release gate artifacts exist and are fresh:
  - `docs/release/gates/endpoint-report.json`
  - `docs/release/gates/write-before-after-report.json`
  - `docs/release/gates/openapi-drift-report.json`
  - `docs/release/gates/ios-endpoint-sync-report.json`
- Confirm no mock markers in anti-mock outputs.
- Confirm DB grants for domain write tables are present for runtime user.

## Rollout
- Deploy backend router updates first.
- Restart gunicorn on `:8002` (runbook-safe background mode).
- Recheck:
  - openapi availability (`/openapi.json`)
  - health (`/api/health`)
  - critical POSTs return business responses (not fallback).
- Run `tools/release_write_before_after_runner.py` against `:8002`.

## Post-Rollout Validation
- Confirm `write-before-after` = PASS.
- Confirm Prometheus freshness metrics update after real endpoint replay.
- Confirm Alertmanager has no unexpected critical firing alerts.
- Confirm iOS smoke/functional reports still PASS.

## Rollback Triggers
- Any critical security endpoint returns fallback/mock marker.
- SQL before/after checks fail for must-write endpoints.
- Sustained critical alerts after deployment window.

## Rollback Steps
- Restore previous backend router version.
- Restart `gunicorn` on `:8002`.
- Re-run minimal health + anti-mock checks.
- Re-run critical write-before-after subset (identity/location/tracker/cleanup/darkweb).

## Ports / Access
- SSH: `22`
- Gateway: `8002`
- Prometheus: `9090` (if enabled in current env)
- PostgreSQL: local server access via `sudo -u postgres psql`
