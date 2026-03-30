# rel-14 iOS functional (138 functions)

## Implemented
- Added runner: `tools/release_ios_functional_138_runner.py`
- Runner covers:
  - matrix-driven functional calls from `docs/release/inventory/endpoint_matrix_enriched.json`
  - positive/negative branch acceptance by HTTP status policy
  - repeated call check for write methods (`POST/PUT/PATCH/DELETE`) for idempotency/robustness
  - anti-mock markers gate (`sfm_mock/sfm_fallback/sfm_error/mock_fallback/reports_compat`)
  - explicit timeout handling probe

## Run
- `ALADDIN_API_BASE='http://149.154.65.180:8002' ALADDIN_FUNCTIONAL_LIMIT=138 python3 tools/release_ios_functional_138_runner.py`

## Result
- `ios-functional-138: PASS`
- checked: `137` (one matrix row without valid `/api/...` endpoint skipped by runner)
- passed: `137`
- failed: `0`
- timeout probe: PASS

## Artifact
- `docs/release/gates/ios-functional-138-report.json`

## Status
- `rel-14`: **PASS**
