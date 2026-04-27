# Track B Localization Gate Policy

Scope:

- `localization-lint` is a blocking CI gate for phase delivery.

## Gate requirements

1. CI has dedicated `localization-lint` job.
2. Lint command is explicit and reproducible.
3. Build job depends on localization gate (no bypass).
4. Gate result must be attached in PR checks before merge.

## Validation

Run:

`python3 scripts/trackb_localization_gate_smoke.py`

Expected:

- `SMOKE RESULT: PASS`
