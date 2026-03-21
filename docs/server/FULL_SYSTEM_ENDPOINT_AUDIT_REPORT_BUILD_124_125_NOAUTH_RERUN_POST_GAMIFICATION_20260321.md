# Full System Endpoint Audit Report (Build 124/125)

- Generated: `2026-03-21T11:46:27.434001+00:00`
- Base URL: `http://149.154.65.180:8002`
- Auth mode: `no_auth`

## Summary

- **total_cases**: `360`
- **runnable_cases**: `235`
- **skipped_cases**: `125`
- **critical_cases**: `88`
- **critical_runnable**: `69`
- **failed_cases**: `94`
- **mock_marker_count**: `87`
- **unauthorized_503_count**: `7`
- **jwt_in_url_count**: `0`
- **contract_drift_candidates**: `88`
- **ios_http_call_sites**: `216`
- **ios_endpoint_constants**: `244`
- **openapi_paths**: `263`

## Top Fail Cases (first 40)

| Method | Path | HTTP | Fail Reasons |
|---|---|---:|---|
| GET | `/api/reports/driving/stats` | 200 | `mock_marker_detected` |
| GET | `/api/reports/dark-web/stats` | 200 | `mock_marker_detected` |
| GET | `/api/reports/identity-theft/stats` | 200 | `mock_marker_detected` |
| GET | `/api/reports/privacy/location/stats` | 200 | `mock_marker_detected` |
| GET | `/api/reports/privacy/cleanup/stats` | 200 | `mock_marker_detected` |
| GET | `/api/reports/privacy/tracker/stats` | 200 | `mock_marker_detected` |
| GET | `/api/reports/ai-categories/stats` | 200 | `mock_marker_detected` |
| GET | `/api/system/uptime` | 200 | `mock_marker_detected` |
| GET | `/api/system/version` | 200 | `mock_marker_detected` |
| GET | `/api/test` | 200 | `mock_marker_detected` |
| GET | `/api/ai/chat` | 200 | `mock_marker_detected` |
| GET | `/api/ai/message` | 200 | `mock_marker_detected` |
| GET | `/api/components/bulk-update` | 200 | `mock_marker_detected` |
| GET | `/api/components/config` | 200 | `mock_marker_detected` |
| GET | `/api/components/disable` | 200 | `mock_marker_detected` |
| GET | `/api/components/enable` | 200 | `mock_marker_detected` |
| GET | `/api/components/status` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/alert` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/settings/update` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/setup` | 200 | `mock_marker_detected` |
| GET | `/api/devices` | 200 | `mock_marker_detected` |
| GET | `/api/family/add` | 200 | `mock_marker_detected` |
| GET | `/api/family/chat/messages` | 200 | `mock_marker_detected` |
| GET | `/api/family/chat/send` | 200 | `mock_marker_detected` |
| GET | `/api/family/join` | 200 | `mock_marker_detected` |
| GET | `/api/family/member` | 200 | `mock_marker_detected` |
| GET | `/api/family/members` | 503 | `unauthorized_503` |
| GET | `/api/family/recover` | 200 | `mock_marker_detected` |
| GET | `/api/family/remove` | 200 | `mock_marker_detected` |
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
