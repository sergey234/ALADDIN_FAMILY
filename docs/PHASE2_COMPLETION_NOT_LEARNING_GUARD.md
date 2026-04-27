# Phase 2 Guard: Completion != Learning

Task ID: `P2-604`

## Rule

Content completion percentage **must not** be interpreted as learning success without learning-evidence metrics.

## Mandatory Learning Evidence

- `mastery_gain`
- `reattempt_success`
- `drop_off_step`
- `hint_dependency`

## Guard In Acceptance

- Acceptance reports must explicitly mention guard: `completion != learning`.
- If completion is high but learning evidence is missing, result status must be `WARNING` or `FAIL`.
- Parent-facing summaries must include skill-based deltas and not only completion/time.

## Report Contract

Each guard report includes:
- `guard_declared`
- `learning_metrics_present`
- `completion_only_paths_detected`
- `status`

## Acceptance Rule

Guard is valid when:
- guard policy doc exists,
- smoke report passes with `0` failed checks,
- report artifacts are generated in `docs/`.
