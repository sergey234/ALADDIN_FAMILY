# rel-10 openapi drift + iOS sync

## Implemented
- Added gate runner: `tools/release_openapi_drift_and_ios_sync.py` (HTTP via **stdlib** `urllib`; no `requests` dependency)
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

## Public gateway
- `https://aladdin-ai.ru/openapi.json` currently returns **404**. For drift and snapshots, set **`ALADDIN_API_BASE`** to the runtime API host (for example `http://149.154.65.180:8002`) after **`GET /api/health`** succeeds, per the server connection guide.

## Verification
Command:
- `ALADDIN_API_BASE='http://149.154.65.180:8002' python3 tools/release_openapi_drift_and_ios_sync.py`

Artifacts (always overwritten on run):
- `docs/release/gates/openapi-drift-report.json`
- `docs/release/gates/ios-endpoint-sync-report.json`
- `docs/release/current/openapi.json`

### 2026-04-19 audit (`srv-audit-openapi`)
Result:
- `openapi-drift: FAIL` — baseline vs `:8002`: 26 paths removed from the export (full `/api/gamification/*` cluster), 3 paths added, 5 paths with method changes. Details in `openapi-drift-report.json`.
- `ios-openapi-sync: FAIL` — 30 `gamification*` endpoints in `AppConfig.swift` plus `malwareFileScan` (`/api/antivirus/scan`) are absent from the fetched OpenAPI. Details in `ios-endpoint-sync-report.json`.

Follow-ups (other plan items): rebaseline `docs/release/baseline/openapi.json` when the server contract is frozen; register the antivirus file-scan route in OpenAPI; retire or feature-gate iOS gamification URLs if those routes stay off the gateway.

### Earlier run (recorded when baseline matched server)
Result:
- `openapi-drift: PASS`
- `ios-openapi-sync: PASS`

## Status
- **2026-04-19:** gate **FAIL** (drift + iOS sync) against current `:8002` export; see reports above.
- **Earlier:** `rel-10` **PASS** when baseline and iOS matched that server generation.
