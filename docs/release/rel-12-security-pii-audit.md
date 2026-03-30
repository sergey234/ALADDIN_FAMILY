# rel-12 security / PII audit

## Findings and remediation
- Found runtime leakage markers in backend logs before fix:
  - `Token preview`
  - `SECRET_KEY preview`
  - source: `app/services/jwt_service.py`
- Applied fix:
  - removed token/secret preview logging in `backend/app/services/jwt_service.py`
- Deployed fix to server and restarted `:8002`.

## Verification after fix
- Service health: `GET /api/health` -> `200`.
- Runtime log scanner (`tools/rel12_runtime_pii_scan.py`) -> PASS:
  - no email/bearer/jwt/secret/token_preview/phone patterns in recent logs.
- Metrics scan (`/metrics`) -> PASS:
  - no sensitive marker matches in metric names/labels/values by scanner pattern.

## Artifacts
- `docs/release/gates/security-pii-audit-report.json`

## Status
- `rel-12`: **PASS**
