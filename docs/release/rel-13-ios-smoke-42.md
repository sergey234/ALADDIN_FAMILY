# rel-13 iOS smoke (42 components)

## Implemented
- Added runner: `tools/release_ios_smoke_runner.py`
- Runner logic:
  - reads component matrix `docs/release/inventory/endpoint_matrix_enriched.json`
  - picks representative endpoint per component (prefers `GET`)
  - executes smoke calls with auth token from `register-device`
  - validates acceptable status and absence of mock markers

## Run
- `ALADDIN_API_BASE='http://149.154.65.180:8002' ALADDIN_IOS_SMOKE_COMPONENTS=42 python3 tools/release_ios_smoke_runner.py`

## Result
- `ios-smoke-42: PASS`
- checked: `42`
- passed: `42`
- failed: `0`

## Artifact
- `docs/release/gates/ios-smoke-42-report.json`

## Status
- `rel-13`: **PASS**
