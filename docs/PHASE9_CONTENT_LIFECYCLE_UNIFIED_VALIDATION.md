# Phase 9.4 Validation (Unified Content Lifecycle)

Scope:

- `9.4` — lock one content lifecycle for child and elderly interfaces.

## Smoke command

Run:

`python3 scripts/phase9_content_lifecycle_unified_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. `ContentManager` has unified lifecycle APIs:
   - `runUnifiedLifecycle(...)`
   - `loadUnifiedAudienceFeed(...)`
2. Child screen uses unified lifecycle entrypoint.
3. Elderly screen uses unified audience feed lifecycle.
4. Build succeeds on iPhone 16 simulator.
