# Endpoint Matrix Baseline Report (Build 124/125)

## Run Metadata
- **Date (UTC):** 2026-03-21T08:22:55Z
- **Base URL:** `http://149.154.65.180:8002`
- **Scenario:** `no_auth`
- **Raw artifact:** `docs/server/ENDPOINT_MATRIX_BASELINE_REPORT_BUILD_124_125.json`

## Summary
- **Total requests:** 7
- **Failed requests:** 4
- **Mock markers detected:** 0
- **Unauthorized 503 count:** 4
- **JWT in URL count:** 0

## Endpoint Results (Critical Set)

| Endpoint | HTTP | Result | Fail | Notes |
|---|---:|---|---|---|
| `/api/v1/parental-control/stats` | 503 | `detail=Protection backend temporarily unavailable` | Yes | Hard-fail policy triggered (mock hidden behind 503). |
| `/api/parental-control/time-limits/{childId}` | 200 | Valid JSON payload | No | Business-ready path currently healthy. |
| `/api/parental-control/geofences/{childId}` | 200 | `[]` | No | Business-ready path currently healthy. |
| `/api/family/members` | 503 | `detail=Protection backend temporarily unavailable` | Yes | Sensitive endpoint still degraded due to backend source state. |
| `/api/user/profile` | 503 | `detail=Protection backend temporarily unavailable` | Yes | Sensitive endpoint still degraded due to backend source state. |
| `/api/gamification/rewards/shop` | 503 | `detail=Protection backend temporarily unavailable` | Yes | Mock no longer leaks as 200; now visible degradation. |
| `/api/gamification/balance/{userId}` | 200 | Valid JSON payload | No | Business-ready path currently healthy. |

## Interpretation
- Policy-layer objective achieved: no `200 + sfm_mock/mock_fallback` in tested critical endpoints.
- System objective not achieved yet: some business-critical routes remain degraded (`503`) and require root-cause remediation in SFM function coverage/routing chain.
- Token hygiene objective for tested paths is currently good (`0` JWT pattern in URL in this baseline run).

## Next Actions
1. Stage 3.1: build root-cause map for all `503` failures.
2. Stage 3.2: compare called proxy functions vs registered SFM functions.
3. Stage 4.1: implement missing SFM functions for critical routes.
4. Re-run full matrix and verify release-gate criteria.

