# Device Matrix Process (G18 / W7-2)

## Purpose

Establish a fixed, repeatable device validation matrix for ALADDIN release readiness.

## Ownership And Cadence

- Owner: `Mobile QA Lead (Release Ring)`
- Backup owner: `iOS Tech Lead`
- Cadence:
  - On every PR to `main`/`develop`: simulator CI matrix checks
  - Before TestFlight release candidate: one full physical device run
  - Before production release: signed validation report in `docs/`

## Required Device Matrix

| Type | Device | iOS | Execution mode | Required |
|---|---|---|---|---|
| Simulator | iPhone 13 | latest stable - 1 | CI | Yes |
| Simulator | iPhone 15 Pro | latest stable | CI | Yes |
| Physical | iPhone 14/15 class | latest stable | Manual pre-release | Yes |

## Mandatory Flows

1. App launch and onboarding transition
2. Parent dashboard open, export actions, and trends rendering
3. Child content loading/error/empty handling
4. Family screen and parental controls entry
5. Network protection screen open/status rendering

## Evidence And Sign-Off

- CI artifacts:
  - `xcodebuild` logs for simulator destinations
  - smoke reports from `scripts/phase8_content_device_smoke.py`
- Manual pre-release artifact:
  - signed markdown report with date, tested build, tester, and pass/fail per flow
- Sign-off fields (must be filled before release):
  - `Release candidate build: ____`
  - `Tester: ____`
  - `Date: ____`
  - `Result: PASS/FAIL`

