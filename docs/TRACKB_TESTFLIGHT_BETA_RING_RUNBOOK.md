# Track B Runbook (TestFlight Beta Ring + Rollback)

Goal:

- every phase release goes through:
  - **internal ring** first,
  - then **limited external ring**,
  - with explicit rollback checklist.

## Rollout rings

1. **Internal ring**
   - testers: team-only
   - duration: at least 24h
   - gates:
     - critical crashes = 0
     - localization gate = pass
     - phase smoke suite = pass

2. **Limited external ring**
   - testers: selected cohort
   - duration: at least 48h
   - gates:
     - no P0/P1 blockers
     - KPI deltas within expected range
     - support volume stable

## Rollback checklist

- disable rollout for current build in TestFlight distribution groups;
- move users back to previous stable build cohort;
- publish rollback note in release log and team channel;
- create incident card with root-cause owner and ETA;
- require hotfix smoke before re-enabling ring progression.

## Exit criteria

- both rings completed and signed off;
- rollback checklist attached to release artifact;
- phase status updated in dashboard documents.
