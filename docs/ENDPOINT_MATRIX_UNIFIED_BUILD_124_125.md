# Unified Endpoint Matrix (Build 124/125)

## Purpose
- Single source of truth for iOS -> backend endpoint mapping.
- Focused on critical routes that affect parental control, family context, profile, and gamification.
- Includes current runtime behavior and release-gate status.

## Legend
- `Critical`: business-critical route for release gate.
- `Auth`: expected authorization behavior for normal runtime.
- `Runtime`: observed current behavior on production host (`149.154.65.180:8002`).
- `Gate`: pass/fail against release criteria.

| Domain | iOS Caller | Method | iOS Path Pattern | Backend Router/Path | Auth | Critical | Runtime | Gate | Notes |
|---|---|---|---|---|---|---|---|---|---|
| Parental stats (v1) | `ParentalControlViewModel` / parental screens | GET | `/api/v1/parental-control/stats?childId={id}` | `security/api/routers/parental_control_router.py` -> `/api/v1/parental-control/stats` | Yes | Yes | `503` on mock fallback | Pass (policy) | Before P0 fix it returned `200 + sfm_mock`; now blocked. |
| Bypass stats | Family/Parental bypass modals | GET | `/api/parental/bypass/stats?childId={id}` | `security/api/routers/parental_control_router.py` -> `/api/parental/bypass/stats` | Yes | Yes | `403` without auth in direct curl | N/A (needs auth scenario) | Covered by auth path; verify in full-run with token. |
| Parental sync settings | `APIService.getParentalControlSettings` | GET | `/api/parental-control/settings/{familyId}?childId={id}` | `security/api/routers/parental_control_sync_router.py` -> `/api/parental-control/settings/{familyId}` | Yes | Yes | Not yet matrix-tested | Pending | Full-run Stage 2 required. |
| Time limits | `APIService.getTimeLimits` | GET | `/api/parental-control/time-limits/{childId}` | `parental_control_sync_router.py` -> `/api/parental-control/time-limits/{childId}` | Yes | Yes | `200` valid payload | Pass | Returned concrete limits in runtime matrix. |
| Geofences | `APIService.getGeofences` | GET | `/api/parental-control/geofences/{childId}` | `parental_control_sync_router.py` -> `/api/parental-control/geofences/{childId}` | Yes | Yes | `200` valid payload (`[]`) | Pass | Endpoint reachable, no mock marker. |
| Family members | `APIService.getFamilyMembers` | GET | `/api/family/members` | family path via gateway/adapter chain | Yes | Yes | `503` when backend source is mock | Pass (policy) | Correct hard-fail for mock source. |
| User profile | `APIService.getProfile` | GET | `/api/user/profile` | `security/api/routers/user_profile_sync_router.py` prefix `/api/user/profile` | Yes | Yes | `503` when backend source is mock | Pass (policy) | Correct hard-fail for mock source. |
| Gamification shop | `APIService.getGamificationRewardsShop` | GET | `/api/gamification/rewards/shop?userId={uid}` | `security/api/routers/gamification_router.py` + proxy path | Yes | Yes | `503` on mock fallback | Pass (policy) | P0 fix expanded mock blocking for gamification. |
| Gamification balance | `APIService.getGamificationBalance` | GET | `/api/gamification/balance/{uid}` | `gamification_router.py` -> `/api/gamification/balance/{userId}` | Yes | Yes | `200` valid payload | Pass | No mock markers observed in test request. |
| Metrics upload | `APIService` metrics flow | POST | `/api/metrics/upload` | `security/api/routers/metrics_router.py` -> `/api/metrics/upload` | No/Service | No | `200` success | Pass | Stable in runtime logs. |

## Known Contract Risks
- `userId` semantics in gamification must be stable non-JWT identifier.
- Mixed namespace usage for parental data (`/api/v1/parental-control/*` and `/api/parental-control/*`) requires strict policy coverage.
- Bypass endpoints under `/api/parental/*` require auth-bound full-run validation.

## Release-Gate Critical Set
- `/api/v1/parental-control/stats`
- `/api/parental-control/time-limits/{childId}`
- `/api/parental-control/geofences/{childId}`
- `/api/family/members`
- `/api/user/profile`
- `/api/gamification/rewards/shop`
- `/api/gamification/balance/{userId}`

## Validation Rules
- Fail if body contains `source=sfm_mock` or `result=mock_fallback`.
- Fail if unauthorized `503` appears on business-ready route.
- Fail if JWT appears in URL/path/query logs.

