# Root Cause Map - Stage 3 (Build 124/125)

## Input
- Source report: `docs/server/FULL_SYSTEM_ENDPOINT_AUDIT_REPORT_BUILD_124_125.json`
- Failed cases analyzed: `124`

## Failure Clusters

### Cluster A - `200 + sfm_mock/mock_fallback` (87 cases, P0)
- Signature:
  - HTTP `200`
  - `source=sfm_mock` and/or `result=mock_fallback`
- Top domains:
  - `/api/reports/*` -> `34`
  - `/api/network-protection/*` -> `7`
  - `/api/user/*` -> `6`
  - `/api/v1/*` -> `6`
  - `/api/components/*` -> `5`
- Root-cause hypothesis:
  - endpoint path lands in proxy execution path that still allows successful mock fallback for this namespace.
  - SFM function resolution returns fallback for unresolved/missing functions.
- Production risk:
  - false-positive business success
  - incorrect analytics and UI state

### Cluster B - `503 Protection backend temporarily unavailable` (37 cases, P0/P1)
- Signature:
  - HTTP `503`
  - no mock marker in body (already transformed by blocking policy)
- Top domains:
  - `/api/gamification/*` -> `24`
  - `/api/family/*` -> `8`
  - `/api/parental-control/*` -> `5`
- Root-cause hypothesis:
  - mock-blocking policy is now correctly active, but upstream SFM/proxy still returns fallback for these paths.
  - business routes remain degraded until missing function/adapter chain is fixed.
- Production risk:
  - visible service degradation on core user flows.

## Quantitative Summary
- Failed: `124`
- `mock_marker_detected`: `87`
- `unauthorized_503`: `37`
- HTTP status split in failures:
  - `200`: `87` (unsafe success with mock)
  - `503`: `37` (safe fail, but degraded product behavior)

## Route-Level Priority Backlog

### P0.1 Remove hidden mock-success from reports/system/components/user/v1 domains
- Objective: convert all `200 + mock` to either:
  - real backend response (`200 real`)
  - or explicit controlled fail (`503`) until real implementation is ready.
- Owners: backend + SFM.

### P0.2 Restore business-critical degraded endpoints
- Target first:
  - `/api/gamification/*` (especially rewards/progress/settings)
  - `/api/family/members`
  - `/api/parental-control/*`
- Objective: move from `503` back to real `200` (no mock markers).

### P0.3 Confirm function-map visibility
- `/api/functions` currently returns `sfm_mock/mock_fallback`.
- Need direct on-host extraction of registered function names from runtime module.

## Stage 3.2 Inputs (Called vs Registered)
- Called function names are derived in proxy as:
  - `func_name = path.replace('/', '_')`
- Required next extraction:
  1. full set of called function names from failed paths
  2. full set of registered SFM callable names from runtime
  3. diff set = missing/incorrect signatures

## Immediate Next Actions
1. Generate called-function list from fail endpoints (automated).
2. Extract runtime registered functions via on-host Python inspection (bypass `/api/functions` mock path).
3. Produce gap diff report and convert to fix tasks per route family.

