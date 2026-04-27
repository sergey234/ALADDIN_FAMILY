# Phase 9.5 Validation (Elderly Localization Merge Gate)

Scope:

- `9.5` — mandatory `localization-lint` merge gate for 60+ screens.

## Smoke command

Run:

`python3 scripts/phase9_elderly_localization_gate_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. CI workflow `localization-lint` job runs:
   - `python3 scripts/localization_lint.py --scope elderly60plus`
2. Scoped lint succeeds locally for the 60+ screen scope.
3. Lint output reports the selected scope explicitly.
