# Phase 2 Learning Effectiveness Gate Report

- generated_at: `2026-04-27T18:07:04.573966+00:00`
- enforce_signals: `False`
- checks: `8`
- failed: `0`
- required_metrics: `mastery_gain, reattempt_success, drop_off_step, hint_dependency`
- available_metrics: `(none declared)`

| ID | Status | Description | Details |
|---|---|---|---|
| P2L-FILE-1 | PASS | Content models file exists | Core/Content/Models/ContentModels.swift |
| P2L-FILE-2 | PASS | Content validator file exists | Core/Content/Validation/ContentValidator.swift |
| P2L-FILE-3 | PASS | Progress systems file exists | Core/Content/Progress/ProgressSystems.swift |
| P2L-FILE-4 | PASS | Acceptance smoke report exists | docs/PHASE2_CATEGORY_ACCEPTANCE_SMOKE_REPORT.json |
| P2L-CONTRACT-1 | PASS | Learning outcome contract fields exist in model layer | ContentLearningOutcomeContract + key fields |
| P2L-CONTRACT-2 | PASS | Validator checks learning contract presence/quality | validateLearningOutcomeContract(...) |
| P2L-ANALYTICS-BASE | PASS | Progress system has baseline tracking hooks | recordOpen/recordCompletion/daily aggregator |
| P2L-METRICS-DECL | PASS | Learning metrics declaration present in acceptance smoke report | declared=[] |
