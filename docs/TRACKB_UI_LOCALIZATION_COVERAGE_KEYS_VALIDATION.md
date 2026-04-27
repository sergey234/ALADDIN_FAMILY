# Track B Validation: UI Localization Coverage + Keys Hygiene

Scope:

- each UI task must include localization coverage for:
  - happy-path,
  - error-state,
  - empty-state,
  - accessibility texts;
- RU/EN keys must be clean (no duplicate drift, namespace discipline for active scope).

## Command

Run:

`python3 scripts/trackb_ui_localization_coverage_keys_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. Checklist and implementation standard explicitly require:
   - happy/error/empty/a11y localization.
2. Scoped localization lint passes for active elderly scope.
3. Namespace-map smoke passes for active phase files.
