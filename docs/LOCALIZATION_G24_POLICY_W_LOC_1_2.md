# G24 Policy (W-LOC-1 / W-LOC-2)

## W-LOC-1 — PR norm is mandatory

For any PR with new/changed user-facing strings:

1. Follow `docs/LOCALIZATION_IMPLEMENTATION_STANDARD.md` (section 2.5 rules are mandatory).
2. Complete `docs/LOCALIZATION_PR_CHECKLIST.md`.
3. PR is merge-blocked until localization checklist items are green.

This policy is not optional for UI, error, empty, loading, and accessibility texts.

## W-LOC-2 — lint scope and CI gate

Agreed CI minimum gate:
- `python3 scripts/localization_lint.py --scope elderly60plus`

Release-quality gate before freeze:
- `python3 scripts/localization_lint.py` (full scope) should be monitored and progressively driven to green.

Why this split:
- keeps current CI strictness (no regression from existing required scope),
- while preserving a full-scope target as release readiness requirement.

## Evidence links

- CI workflow: `.github/workflows/ci.yml`
- Lint script: `scripts/localization_lint.py`
- Primary checklist: `docs/LOCALIZATION_PR_CHECKLIST.md`

