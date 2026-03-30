# rel-08 contract suite

## Implemented
- Added matrix contract runner: `tools/release_contract_matrix_runner.py`.
- Runner reads endpoint inventory (`docs/release/inventory/endpoint_matrix_enriched.json`), executes endpoints, and writes release artifact:
  - `docs/release/gates/endpoint-report.json`
- Gate conditions:
  - no forbidden markers (`sfm_mock/sfm_fallback/sfm_error/mock_fallback/reports_compat/source:mock`)
  - endpoint response status within accepted contract range

## Fixes applied during rel-08
- `security/ai_agents/dark_web_monitoring_agent.py`
  - explicit `self.config` assignment to avoid runtime `AttributeError`
- `security/ai_agents/driving_reports_agent.py`
  - explicit `self.config` and `self.logger` initialization to avoid runtime `AttributeError`

## Verification run
- Base: `http://149.154.65.180:8002`
- Command:
  - `ALADDIN_API_BASE='http://149.154.65.180:8002' ALADDIN_CONTRACT_LIMIT=138 python3 tools/release_contract_matrix_runner.py`
- Result:
  - `PASS`
  - checked `138`
  - passed `138`
  - failed `0`

## Artifact
- `docs/release/gates/endpoint-report.json`

## Status
- `rel-08`: **PASS**
