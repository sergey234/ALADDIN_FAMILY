# Track B Validation (Phase Exit Criteria)

Scope:

- Track B governance rule:
  - for each active phase (7, 8, 9), exit criteria include:
    - unit coverage,
    - integration smoke,
    - UI smoke,
    - accessibility smoke.

## Smoke command

Run:

`python3 scripts/trackb_phase_exit_criteria_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Phase 7**
   - unit evidence in `Tests/UnitTests/*PolicyTests.swift`
   - integration/UI/accessibility smoke artifacts are present.
2. **Phase 8**
   - unit test presence in `Tests/UnitTests`
   - integration/UI/accessibility smoke scripts are present.
3. **Phase 9**
   - unit evidence for roster reconcile policy tests
   - dedicated integration/UI/accessibility smoke scripts are present.
