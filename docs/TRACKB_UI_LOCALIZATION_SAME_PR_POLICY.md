# Track B Policy: UI Tasks Require RU/EN In Same PR

Scope:

- every UI task from phases 0-8 is considered done only when:
  - RU localization is included,
  - EN localization is included,
  - both are delivered in the same PR.

## Mandatory evidence

1. UI change references affected screen(s).
2. Localization keys for RU and EN exist for those changes.
3. PR checklist includes confirmation of dual-locale delivery.
4. Localization lint check is attached in the same PR.

## Validation

Run:

`python3 scripts/trackb_ui_localization_same_pr_smoke.py`

Expected:

- `SMOKE RESULT: PASS`
