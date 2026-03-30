# rel-10 openapi drift + iOS sync

## Implemented
- Added gate runner: `tools/release_openapi_drift_and_ios_sync.py`
- Gate actions:
  1. fetch current runtime OpenAPI from `:8002` and snapshot to `docs/release/current/openapi.json`
  2. compare against baseline `docs/release/baseline/openapi.json`
  3. compare iOS `Core/Config/AppConfig.swift` endpoints against runtime OpenAPI paths

## iOS endpoint sync fixes
Updated `Core/Config/AppConfig.swift` to align with actual OpenAPI routes:
- `componentStatusBatch` -> `/api/components/batch/status`
- `gamificationBalanceAdd` -> `/api/gamification/balance`
- `gamificationBalanceSubtract` -> `/api/gamification/balance`
- `gamificationBalanceHistory` -> `/api/gamification/balance`
- `protectionThreatsByStatus` -> `/api/protection/threats`
- `paymentsQRStatus` -> `/api/payments/qr/status/test`

## Verification
Command:
- `ALADDIN_API_BASE='http://149.154.65.180:8002' python3 tools/release_openapi_drift_and_ios_sync.py`

Result:
- `openapi-drift: PASS`
- `ios-openapi-sync: PASS`

Artifacts:
- `docs/release/gates/openapi-drift-report.json`
- `docs/release/gates/ios-endpoint-sync-report.json`
- `docs/release/current/openapi.json`

## Status
- `rel-10`: **PASS**
