# Phase 2 Stimulus Budget Policy (Ages 1-6)

Task ID: `P2-408`

## Goal

Limit overstimulation in 1-6 child flows while preserving engagement and clear progress feedback.

## Budget Limits

- `effects_per_minute_max = 6`
- `rewards_per_minute_max = 4`
- `high_intensity_burst_max = 2` (per 5-minute window)

## Scope (1-6 Categories)

- `child_interface_category_toys`
- `child_interface_category_drawing`
- `child_interface_category_songs`
- `child_interface_category_stories`

## Event Mapping

Effects events (count toward `effects_per_minute_max`):
- mascot emotion/activity transitions
- surprise visual event trigger
- fast animated transition in content cards

Rewards events (count toward `rewards_per_minute_max`):
- skill progress reward sound/points
- completion reward
- surprise reward outcome

## Runtime Guardrails

- If `effects/min` exceeds threshold, fallback to reduced animation preset for remaining session.
- If `rewards/min` exceeds threshold, coalesce consecutive reward emissions into one summary reward.
- If both exceed thresholds, enable calm mode:
  - suppress non-critical effects
  - keep only milestone rewards

## QA Matrix

Category-level:
- all 1-6 categories are explicitly listed in policy scope.
- budget numeric limits are present and non-zero.

Item-level:
- effects and rewards event mappings are declared.
- runtime fallback behavior is declared for threshold breach.

## Acceptance Rule

Policy is valid when:
- policy document exists and contains limits + scope + guardrails,
- smoke report passes with `0` failed checks,
- report artifacts are generated in `docs/`.
