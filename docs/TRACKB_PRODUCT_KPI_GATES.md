# Track B Product KPI Gates

This document defines measurable gates and evidence contracts for product KPIs.

## KPI thresholds

- Startup time: `< 3 seconds`.
- Battery consumption: `< 15% per hour`.
- Background memory: `< 200MB`.
- Engagement: `> 20 minutes/session`.
- Retention: target values per age segment, reviewed after beta cohorts.
- Lesson completion: `> 80%`.
- Parent approval: `> 4.5 stars`.

## Evidence contract

For each KPI gate, keep:

1. measurement method;
2. source artifact/report path;
3. owner and review cadence.

## Reporting cadence

- Weekly: startup, battery, memory.
- Bi-weekly: engagement, lesson completion.
- Per beta cohort: retention by age segment.
- Monthly: parent approval rating trend.

## Validation

Run:

`python3 scripts/trackb_product_kpi_gates_smoke.py`

Expected:

- `SMOKE RESULT: PASS`
