# Track B Wave 2 Feature Mode Policy

Goal:

- after Wave 1 baseline is fully closed, enforce zero-exception localization gate for every new PR.

## Contract

1. Every PR must pass `python3 scripts/localization_lint.py` (global scope).
2. PR template must keep localization checklist mandatory.
3. No bypass merges for failed localization checks.
4. Feature mode activation is allowed only when baseline debt is zero.

## Activation

- Baseline closure signal: `python3 scripts/localization_lint.py` returns `0` on current mainline.
- After activation, global lint is required for all new PRs.

## Validation

Run:

`python3 scripts/trackb_wave2_feature_mode_smoke.py`

Expected:

- `SMOKE RESULT: PASS`
