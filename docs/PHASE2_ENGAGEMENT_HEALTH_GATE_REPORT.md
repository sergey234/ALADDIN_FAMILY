# Phase 2 Engagement Health Gate Report

- generated_at: `2026-04-27T18:07:04.996213+00:00`
- enforce_signals: `False`
- checks: `7`
- failed: `0`
- required_metrics: `session_depth, d1_d7_voluntary_return, boredom_signal`
- available_metrics: `(none declared)`

| ID | Status | Description | Details |
|---|---|---|---|
| P2E-FILE-1 | PASS | Progress systems file exists | Core/Content/Progress/ProgressSystems.swift |
| P2E-FILE-2 | PASS | Child content screen exists | Screens/ChildContentScreen.swift |
| P2E-FILE-3 | PASS | Acceptance smoke report exists | docs/PHASE2_CATEGORY_ACCEPTANCE_SMOKE_REPORT.json |
| P2E-SIGNAL-BASE-1 | PASS | Session-depth baseline hooks exist | usedSeconds + opens/completions tracking |
| P2E-SIGNAL-BASE-2 | PASS | Child flow has loading/empty/error states for dropout observation | loading/empty/error branches |
| P2E-SIGNAL-BASE-3 | PASS | Daily trend points available for retention proxies | ParentActivityDailyAggregator.trendPoints |
| P2E-METRICS-DECL | PASS | Engagement metrics declaration present in acceptance smoke report | declared=[] |
