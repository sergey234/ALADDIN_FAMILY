# Full System Endpoint Audit Report (Build 124/125)

- Generated: `2026-03-21T12:30:00.615367+00:00`
- Base URL: `http://149.154.65.180:8002`
- Auth mode: `no_auth`

## Summary

- **total_cases**: `360`
- **runnable_cases**: `235`
- **skipped_cases**: `125`
- **critical_cases**: `88`
- **critical_runnable**: `69`
- **failed_cases**: `41`
- **mock_marker_count**: `36`
- **unauthorized_503_count**: `5`
- **jwt_in_url_count**: `0`
- **contract_drift_candidates**: `42`
- **ios_http_call_sites**: `216`
- **ios_endpoint_constants**: `244`
- **openapi_paths**: `309`

## Top Fail Cases (first 40)

| Method | Path | HTTP | Fail Reasons |
|---|---|---:|---|
| GET | `/api/system/uptime` | 200 | `mock_marker_detected` |
| GET | `/api/system/version` | 200 | `mock_marker_detected` |
| GET | `/api/test` | 200 | `mock_marker_detected` |
| GET | `/api/ai/chat` | 200 | `mock_marker_detected` |
| GET | `/api/ai/message` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/alert` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/settings/update` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/setup` | 200 | `mock_marker_detected` |
| GET | `/api/devices` | 200 | `mock_marker_detected` |
| GET | `/api/location/geofences` | 200 | `mock_marker_detected` |
| GET | `/api/malware/quarantine/action` | 200 | `mock_marker_detected` |
| GET | `/api/malware/threats` | 200 | `mock_marker_detected` |
| GET | `/api/network-protection/config` | 200 | `mock_marker_detected` |
| GET | `/api/network-protection/connect` | 200 | `mock_marker_detected` |
| GET | `/api/network-protection/disconnect` | 200 | `mock_marker_detected` |
| GET | `/api/network-protection/servers` | 200 | `mock_marker_detected` |
| GET | `/api/network-protection/settings` | 200 | `mock_marker_detected` |
| GET | `/api/network-protection/stats` | 200 | `mock_marker_detected` |
| GET | `/api/network-protection/status` | 200 | `mock_marker_detected` |
| GET | `/api/notifications/archive` | 200 | `mock_marker_detected` |
| GET | `/api/notifications/bulk-mark-read` | 200 | `mock_marker_detected` |
| GET | `/api/notifications/categories` | 200 | `mock_marker_detected` |
| GET | `/api/notifications/stats` | 200 | `mock_marker_detected` |
| GET | `/api/parental-control/app-blocks` | 503 | `unauthorized_503` |
| GET | `/api/parental-control/geofences` | 503 | `unauthorized_503` |
| GET | `/api/parental-control/schedules` | 503 | `unauthorized_503` |
| GET | `/api/parental-control/settings` | 503 | `unauthorized_503` |
| GET | `/api/parental-control/time-limits` | 503 | `unauthorized_503` |
| GET | `/api/parental/block` | 200 | `mock_marker_detected` |
| GET | `/api/parental/control` | 200 | `mock_marker_detected` |
| GET | `/api/parental/limits` | 200 | `mock_marker_detected` |
| GET | `/api/payments/qr/status/test` | 200 | `mock_marker_detected` |
| GET | `/api/protection/quarantine/action` | 200 | `mock_marker_detected` |
| GET | `/api/protection/threats` | 200 | `mock_marker_detected` |
| GET | `/api/protection/threats/test` | 200 | `mock_marker_detected` |
| GET | `/api/subscription/activate` | 200 | `mock_marker_detected` |
| GET | `/api/subscription/activation/activate` | 200 | `mock_marker_detected` |
| GET | `/api/subscription/activation/verify` | 200 | `mock_marker_detected` |
| GET | `/api/subscription/subscribe` | 200 | `mock_marker_detected` |
| GET | `/api/subscription/tariffs` | 200 | `mock_marker_detected` |
