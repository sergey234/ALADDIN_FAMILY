# Track B Namespace Enforcement

Scope:

- localization keys used by active phase screens must follow namespace-map rules;
- unstable suffixes and ad-hoc key naming are forbidden.

## Validation command

Run:

`python3 scripts/trackb_namespace_map_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What is enforced

1. Phase files use keys from approved namespace prefixes:
   - `common_*`, `family_*`, `parental_*`, `child_*`, `elderly_*`, `parent_dashboard_*`, `a11y_*`
2. Forbidden suffixes are not used:
   - `_new`, `_v2`, `_temp`, `_final`
3. Mirror-overview keys (`parent_dashboard_*`) exist in localization maps.
