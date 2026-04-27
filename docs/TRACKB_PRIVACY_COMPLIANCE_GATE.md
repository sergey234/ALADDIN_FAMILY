# Track B Privacy/Compliance Gate

Scope:

- mandatory check before merging phase work into release branch.

## Command

Run:

`python3 scripts/trackb_privacy_compliance_gate.py`

Expected:

- `SMOKE RESULT: PASS`

## Required artifacts

1. `docs/PHASE8_COMPLIANCE_VALIDATION.md`
2. `scripts/phase8_compliance_smoke.py`
3. `docs/TRACKB_TESTFLIGHT_BETA_RING_RUNBOOK.md`

## Merge policy

- release merge is blocked until this gate is green and attached to PR checks.
