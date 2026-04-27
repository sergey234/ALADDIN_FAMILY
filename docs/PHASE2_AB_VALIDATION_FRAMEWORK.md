# Phase 2 A/B Validation Framework (Task Format)

Task ID: `P2-406`  
Scope: validate task-format effectiveness for `short/long` and `text/visual`.

## Goal

Measure which learning task format provides better completion quality and retention proxy without increasing frustration.

## Variants

| Axis | Variant A | Variant B |
|---|---|---|
| Length | short | long |
| Presentation | text | visual |

Combined experiment groups:
- `A1`: `short + text`
- `A2`: `short + visual`
- `B1`: `long + text`
- `B2`: `long + visual`

## Assignment Policy

- Unit: `child_id + category_id + day_key`.
- Deterministic bucketing: stable hash modulo `4`.
- Group mapping:
  - `0 -> A1`
  - `1 -> A2`
  - `2 -> B1`
  - `3 -> B2`
- Freeze assignment for one day to avoid cross-format contamination.

## Evaluation Metrics

Primary:
- `completion_rate`
- `first_pass_success`
- `hint_dependency`

Secondary:
- `time_to_complete_sec`
- `drop_off_step`
- `reattempt_success`

Guardrails:
- `boredom_signal`
- `frustration_recovery_triggered`

## Telemetry Contract

Required event fields:
- `experiment_id = phase2_task_format_ab_v1`
- `variant_id` (`A1|A2|B1|B2`)
- `category_id`
- `item_id`
- `age_band`
- `completion_rate`
- `first_pass_success`
- `hint_dependency`
- `time_to_complete_sec`
- `drop_off_step`
- `reattempt_success`
- `boredom_signal`

## QA Validation Matrix

Category-level:
- each Phase 2 category has at least one item mapped to A/B format test pool.
- each category has deterministic assignment enabled.

Item-level:
- item has declared format (`short|long` and `text|visual`).
- item reports telemetry fields from the contract.
- item outcome is comparable against same category baseline.

## Acceptance Rule

Framework is considered valid when:
- all 4 variants are declared and reachable,
- telemetry contract fields are documented,
- category-level and item-level QA checks pass in smoke report.
