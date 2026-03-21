# Proof Packet - Point #1
## Endpoint
- `GET /api/v1/parental-control/stats?childId={child_uuid}`

## Truth-State Path
- `NotStarted` -> `MockBlocked` -> `RoutedCorrectly` -> `AuthGuarded` -> `BusinessOK`

## Root Cause Chain
1. Legacy route `/api/v1/parental-control/*` existed but was not included in active `main.py`, request fell into wildcard.
2. Wildcard path returned mock markers, then blocked by mock->503 policy.
3. After router inclusion, auth path surfaced DB contract mismatch (`user_id` integer vs token subject `"anonymous"`).
4. Added strict numeric user-id coercion in active parental stats handler.
5. Corrected implementation typo in active file (`current_user.get(id)` -> `current_user.get("id")`).

## Evidence (Before / After)

### Before
- Response (historical): `503 Protection backend temporarily unavailable`
- Cause: wildcard + mock hard-fail.

### After - no auth
- Response: `403 Not authenticated`
- Interpretation: protected route reached, no wildcard success leakage.

### After - auth with device token
- Response: `401 User token does not contain numeric user id`
- Interpretation: explicit contract validation, no SQL crash.

### After - auth with real user JWT (numeric id)
- Response: `200 OK`
- Body shape: valid `ParentalControlStatsResponse` with all expected blocks:
  - `content_blocked`
  - `screen_time`
  - `location`
  - `monitoring`

## Runtime Access-Log Confirmation
- `/opt/aladdin-backend/logs/access.log` contains final successful entries for this endpoint with status `200`.

## Final Verdict
- Point #1 is **BusinessOK** for this endpoint.
- SQL error `invalid input syntax for integer: "anonymous"` is no longer reproducible in this flow.
- Endpoint now has deterministic behavior across auth modes.

