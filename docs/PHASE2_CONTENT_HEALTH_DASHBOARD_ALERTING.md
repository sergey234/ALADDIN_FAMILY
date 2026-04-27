# Phase 2 Content Health Dashboard And Alerting

Task ID: `P2-603`

## Goal

Detect regressions early with a dashboard + alerts covering content quality and delivery health.

## Dashboard Panels

- Gate status timeline (pass/fail by day)
- Category readiness distribution (`READY`, `READY WITH CONDITIONS`, `NOT READY`)
- Learning/Engagement/Freshness KPI trend
- Parent outcome coverage (learned panel, digest, mastery, ROI)

## Alert Rules

- `alert_gate_failure`: any mandatory Phase 2 gate fails
- `alert_readiness_regression`: `READY` count decreases week-over-week
- `alert_parent_outcome_missing`: any parent outcome panel empty for top categories
- `alert_freshness_sla_breach`: freshness SLA report has failed checks

## Routing

- Severity `warning`: notify product + qa channel
- Severity `critical`: notify product + eng + qa on-call immediately
- Alert records are persisted in weekly report

## Acceptance Rule

Dashboard/alerting layer is valid when:
- policy document exists with panel + rule definitions,
- smoke report passes with `0` failed checks,
- report artifacts are generated in `docs/`.
