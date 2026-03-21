# SFM Function Map Completeness - Stage 3.2 (Build 124/125)

## Inputs
- Called function list (from failed endpoint paths):  
  `docs/server/CALLED_FUNCTIONS_FROM_FAIL_ENDPOINTS_BUILD_124_125.json`
- Runtime registered functions (on-host extraction):  
  `docs/server/REGISTERED_SFM_FUNCTIONS_RUNTIME_BUILD_124_125.json`
- Gap report:  
  `docs/server/SFM_FUNCTION_GAP_REPORT_BUILD_124_125.json`

## Core Metrics
- **Called functions (from FAIL paths):** `124`
- **Registered runtime SFM functions:** `104`
- **Directly matched:** `0`
- **Missing (proxy-call name not resolvable directly):** `124`

## Interpretation
- Smart Proxy constructs names as `path.replace('/', '_')`, optionally prefixed with `api_`.
- Runtime SFM registry uses semantic names (`get_*`, `update_*`, `block_*`, etc.), not direct path-underscore names.
- There is no visible deterministic mapping layer between proxy-generated function names and runtime registry names for the failed set.
- This explains broad fallback usage (`sfm_mock/mock_fallback`) despite an existing function registry.

## Top Missing Families (by proxy function prefix)
- `reports`: 34
- `gamification`: 24
- `family`: 8
- `network-protection`: 7
- `user`: 6
- `v1`: 6
- `components`: 5
- `parental-control`: 5
- `subscription`: 5

(Full cluster file: `docs/server/SFM_FUNCTION_GAP_FAMILIES_BUILD_124_125.json`)

## Root Cause Statement (Stage 3.2)
1. Proxy naming contract and SFM runtime function naming contract are misaligned.
2. For many routes, proxy calls function names that are not directly registered.
3. Fallback path returns mock markers (or now hard-fail `503` where policy blocks mock leakage).

## Required Remediation (feeds Stage 3.3 / Stage 4.1)
- Introduce explicit route-to-function mapping table for critical domains (`reports`, `gamification`, `family`, `parental-control`).
- Add/repair missing SFM adapter methods or aliases matching proxy invocation contract.
- Keep mock->503 policy active for sensitive routes until real mappings are complete.
- Re-run full audit and expect:
  - drop in `mock_marker_count`
  - drop in `unauthorized_503_count`
  - increase in real `200` responses for business-ready paths.

