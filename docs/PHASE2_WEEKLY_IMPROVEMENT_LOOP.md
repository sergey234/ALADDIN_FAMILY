# Phase 2 Weekly Improvement Loop

Task ID: `P2-602`

Loop: `build -> measure -> tune`

## Cadence

- Frequency: weekly (every Monday).
- Inputs:
  - build status
  - learning/engagement/freshness gates
  - parent outcome metrics
- Outputs:
  - weekly report in `docs/`
  - prioritized tuning actions for next week

## Weekly Workflow

1. **Build**
   - run `localization_lint`
   - run phase2 smokes (count/acceptance/qa/ab/freshness/stimulus/telemetry)
   - run simulator build
2. **Measure**
   - aggregate failed/passed counts
   - compare with previous weekly baseline
   - mark regression risk if any gate fails
3. **Tune**
   - define top 3 corrective actions
   - assign owner per action
   - set due date before next cycle

## Weekly Report Contract

Each report must include:
- `generated_at`
- `gates_summary`
- `regression_flags`
- `top_3_actions`
- `owner_assignment`

## Acceptance Rule

Loop is valid when:
- policy document exists,
- weekly report generator smoke passes with `0` fails,
- report artifacts are generated in `docs/`.
