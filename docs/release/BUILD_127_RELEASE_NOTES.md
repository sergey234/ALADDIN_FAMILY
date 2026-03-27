# BUILD 127 Release Notes

## Scope
- Stabilization of Analytics screen to reduce UI livelock/freeze scenarios on real devices.
- Hardened family auth/error handling around `Invalid user_id in token`.

## Included Changes
- `AnalyticsViewModel`:
  - Added structured mini-log diagnostics with `loadId` correlation.
  - Added lifecycle cancellation hook via `cancelAll(reason:)`.
  - Introduced staged loading behavior: base analytics first, components after first paint.
  - Debounced `SessionExpired` notifications to prevent global cascade loops.
- `AnalyticsScreen`:
  - Added `onDisappear` cancellation path to stop background activity when screen is closed.
- `RemoteAnalyticsService`:
  - Limited component fetch concurrency to reduce request bursts (`maxConcurrent = 3`).
- `APIService`:
  - Switched component stats decoding from `[String: AnyCodable]` to typed DTO.
- `NetworkManager`:
  - Reduced hot-path response body logging (body now logged for HTTP errors only).
  - Contract 401 detection enhanced to include `Invalid user_id` markers (no token-expired flow for contract errors).
- Backend family auth compatibility:
  - Added legacy claim fallback for `id/device_id/sub` resolution in family router.

## Risks Addressed
- Endless spinner on Analytics with delayed or unstable component requests.
- Gesture/UI “stuck” behavior after high-frequency render/reload loops.
- Notification cascade from repeated unauthorized events.
- False “server unavailable” user messaging due to contract-401 misclassification.

## Validation Checklist
- Open/close Analytics screen 10-20 times on real device.
- Confirm mini-log sequence includes:
  - `analytics_load_start`
  - `analytics_load_base_ok`
  - `analytics_components_start`
  - terminal state (`analytics_components_ok` or `analytics_components_fail` or `analytics_watchdog_timeout`)
  - `analytics_cancel_all` on screen exit.
- Ensure no repeated `SessionExpired` notification storm in logs.
- Ensure no request burst > expected component batch behavior.

