# SyncBetweenDevices Tests Policy (META-3)

## Purpose

Stabilize `SyncBetweenDevicesTests` execution by making environment intent explicit (mock/stub vs staging) and standardizing merge-blocking behavior.

## Execution Modes

- Default mode (`mock`): tests are skipped unless staging execution is explicitly requested.
- Staging mode (`staging`): tests run only when both are set:
  - `SYNC_INTEGRATION_MODE=staging`
  - `RUN_SYNC_INTEGRATION_TESTS=1`

## Merge Blocking Rules

- Required for merge:
  - Unit tests
  - Deterministic smoke scripts
- Non-blocking by default:
  - Staging-dependent sync integration tests, unless release manager promotes them to blocking for RC.

## XCTSkip Convention

- `setUpWithError()` in `SyncBetweenDevicesTests` must guard execution and issue `XCTSkip` when mode/flags are missing.
- Skip message should explain required env vars.

## CI Policy

- CI keeps sync tests in skip-safe mode by default.
- Separate release-ring execution may export required env vars to run full staging sync validation.

