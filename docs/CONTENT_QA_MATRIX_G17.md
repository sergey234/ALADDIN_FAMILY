# G17 Content QA Matrix

## Goal

Make content validation measurable across category, age audience, and baseline scenarios:
- open content
- offline behavior
- progress persistence

## Matrix

| Category | Audience | Open flow | Offline flow | Progress flow | Evidence |
|---|---|---|---|---|---|
| Games | child (7-10) | `ChildContentScreen` category open | `OfflineManager` fallback + empty/error localized states | progress bar and `%` shown, persisted | `phase7_content_qa_matrix_smoke.py` report + UI screenshots |
| Learning | child (7-10) | content item open and details render | cached payload path works | completed/total metrics visible | smoke JSON/MD + targeted manual pass |
| Family tasks | teenager (11-13) | item list and card actions render | stale/offline fallback doesn't crash | progress values remain deterministic | smoke JSON/MD |
| Safety lessons | teenager (11-13) | route resolver opens expected experience | network loss returns localized fallback | route + progress coherence | smoke JSON/MD |

## Required checks per run

1. `python3 scripts/phase7_content_qa_matrix_smoke.py`
2. Verify generated:
   - `docs/PHASE7_CONTENT_QA_MATRIX_REPORT.json`
   - `docs/PHASE7_CONTENT_QA_MATRIX_REPORT.md`
3. Attach report artifacts to PR touching content experience or localization for child/teen flows.

## Minimal pass criteria

- All structural checks in smoke script are PASS.
- No hardcoded user-facing regression in modified files (validated by `localization_lint` policy).
- Child content empty/error/loading/progress states are still localized and reachable.

