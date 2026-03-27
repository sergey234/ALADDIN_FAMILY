# BUILD 127 Rollback Checklist

## Release Blockers
- Any reproducible UI freeze/hang on Analytics screen during 5-10 minute soak test.
- Gesture stuck state propagating to other screens after Analytics usage.
- Repeated unauthorized/session cascade causing forced navigation loops.

## Rollback Scope (Minimal)
- iOS app changes:
  - `ViewModels/AnalyticsViewModel.swift`
  - `Screens/04_AnalyticsScreen.swift`
  - `Core/Analytics/RemoteAnalyticsService.swift`
  - `Core/Network/APIService.swift`
  - `Core/Network/NetworkManager.swift`
- Backend family claim fallback:
  - `app/routers/family.py`

## Rollback Procedure
1. Identify target stable commit/tag before build 127 analytics stabilization.
2. Revert listed files to stable revision.
3. Rebuild app and deploy TestFlight candidate.
4. If backend rollback needed, restore previous `family.py` backup and restart gateway service.
5. Execute smoke tests:
   - family stats auth
   - analytics load/open-close cycle
   - registration flows in all 3 entry points.

## Acceptance After Rollback
- No UI freeze during Analytics navigation/stress.
- No persistent loading spinner loops.
- Family card status remains consistent (no false network fallback).
- Registration flow returns deterministic errors/success (no generic false server unavailable state).

