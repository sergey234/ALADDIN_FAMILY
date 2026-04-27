# Track B Cross-Audience Regression

Scope:

- mandatory regression coverage for phases 2, 7, and 9 across:
  - child interface,
  - 60+ interface,
  - family synchronization layer.

## Validation

Run:

`python3 scripts/trackb_cross_audience_regression_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## Evidence requirements

1. Unified content lifecycle APIs exist for shared audience flow.
2. Family access policy and parental controls exist in phase 7 surface.
3. Child/elderly UI surfaces and phase 9 family integration smoke exist.
4. Integration smoke references shared permission and unified roster projection.
