# Phase 2 Unified Telemetry Schema

Task ID: `P2-601`

## Goal

Define a single telemetry contract that unifies `Learning + Engagement + Freshness` signals for Phase 2 operations.

## Core Envelope

- `event_id`
- `event_name`
- `ts_utc`
- `child_id`
- `category_id`
- `item_id`
- `age_band`
- `session_id`

## Learning Block

- `mastery_gain`
- `reattempt_success`
- `drop_off_step`
- `hint_dependency`
- `first_pass_success`

## Engagement Block

- `session_depth`
- `used_seconds`
- `completion_rate`
- `boredom_signal`
- `frustration_recovery_triggered`
- `d1_d7_voluntary_return`

## Freshness Block

- `content_last_refresh_at`
- `content_refresh_due_at`
- `freshness_tier`
- `freshness_sla_status`
- `staleness_seconds`

## Event Families

- `learning_outcome_updated`
- `engagement_checkpoint`
- `freshness_window_evaluated`
- `parent_dashboard_digest_generated`

## Validation Rules

Category-level:
- all three blocks (`Learning`, `Engagement`, `Freshness`) must exist in schema;
- each event family must include the core envelope.

Item-level:
- every listed metric field name must be present and non-empty in schema definition;
- freshness status must be enum-like (`ok|warning|breach`);
- numeric metrics are documented as numeric values.

## Acceptance Rule

Schema is valid when:
- schema doc exists with all blocks and event families,
- smoke report passes with `0` failed checks,
- report artifacts are generated in `docs/`.
