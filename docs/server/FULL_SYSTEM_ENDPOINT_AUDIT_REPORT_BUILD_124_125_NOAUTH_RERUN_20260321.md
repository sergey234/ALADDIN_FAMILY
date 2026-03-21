# Full System Endpoint Audit Report (Build 124/125)

- Generated: `2026-03-21T10:10:15.283732+00:00`
- Base URL: `http://149.154.65.180:8002`
- Auth mode: `no_auth`

## Summary

- **total_cases**: `360`
- **runnable_cases**: `235`
- **skipped_cases**: `125`
- **critical_cases**: `88`
- **critical_runnable**: `69`
- **failed_cases**: `118`
- **mock_marker_count**: `87`
- **unauthorized_503_count**: `31`
- **jwt_in_url_count**: `0`
- **contract_drift_candidates**: `112`
- **ios_http_call_sites**: `216`
- **ios_endpoint_constants**: `244`
- **openapi_paths**: `239`

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
| GET | `/api/gamification/achievements` | 503 | `unauthorized_503` |
| GET | `/api/gamification/achievements/claim` | 503 | `unauthorized_503` |
| GET | `/api/gamification/achievements/progress` | 503 | `unauthorized_503` |
| GET | `/api/gamification/achievements/unlock` | 503 | `unauthorized_503` |
| GET | `/api/gamification/progress` | 503 | `unauthorized_503` |
| GET | `/api/gamification/progress/level` | 503 | `unauthorized_503` |
| GET | `/api/gamification/progress/reset` | 503 | `unauthorized_503` |
| GET | `/api/gamification/progress/stats` | 503 | `unauthorized_503` |
| GET | `/api/gamification/progress/update` | 503 | `unauthorized_503` |
| GET | `/api/gamification/rewards` | 503 | `unauthorized_503` |
| GET | `/api/gamification/rewards/claim` | 503 | `unauthorized_503` |
