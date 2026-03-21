# Full System Endpoint Audit Report (Build 124/125)

- Generated: `2026-03-21T10:10:59.044379+00:00`
- Base URL: `https://aladdin-ai.ru`
- Auth mode: `auth`

## Summary

- **total_cases**: `244`
- **runnable_cases**: `244`
- **skipped_cases**: `0`
- **critical_cases**: `75`
- **critical_runnable**: `75`
- **failed_cases**: `176`
- **mock_marker_count**: `142`
- **unauthorized_503_count**: `34`
- **jwt_in_url_count**: `0`
- **contract_drift_candidates**: `244`
- **ios_http_call_sites**: `216`
- **ios_endpoint_constants**: `244`
- **openapi_paths**: `0`

## Top Fail Cases (first 40)

| Method | Path | HTTP | Fail Reasons |
|---|---|---:|---|
| GET | `/api/ai/assistant/analyze_threat` | 200 | `mock_marker_detected` |
| GET | `/api/ai/assistant/chat` | 200 | `mock_marker_detected` |
| GET | `/api/ai/assistant/feedback` | 200 | `mock_marker_detected` |
| GET | `/api/ai/assistant/report_incident` | 200 | `mock_marker_detected` |
| GET | `/api/ai/chat` | 200 | `mock_marker_detected` |
| GET | `/api/ai/message` | 200 | `mock_marker_detected` |
| GET | `/api/auth/login` | 200 | `mock_marker_detected` |
| GET | `/api/auth/login-by-recovery-code` | 200 | `mock_marker_detected` |
| GET | `/api/auth/logout` | 200 | `mock_marker_detected` |
| GET | `/api/auth/refresh` | 200 | `mock_marker_detected` |
| GET | `/api/auth/register` | 200 | `mock_marker_detected` |
| GET | `/api/auth/register-device` | 200 | `mock_marker_detected` |
| GET | `/api/auth/register-device-trial` | 200 | `mock_marker_detected` |
| GET | `/api/chat/offline-messages/resolve-conflicts` | 200 | `mock_marker_detected` |
| GET | `/api/chat/offline-messages/send` | 200 | `mock_marker_detected` |
| GET | `/api/chat/offline-messages/sync` | 200 | `mock_marker_detected` |
| GET | `/api/components/bulk-update` | 200 | `mock_marker_detected` |
| GET | `/api/components/config` | 200 | `mock_marker_detected` |
| GET | `/api/components/disable` | 200 | `mock_marker_detected` |
| GET | `/api/components/enable` | 200 | `mock_marker_detected` |
| GET | `/api/components/status` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/alert` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/data` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/notifications/send` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/report` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/settings/update` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/setup` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/start` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/stop` | 200 | `mock_marker_detected` |
| GET | `/api/crash-detection/sync` | 200 | `mock_marker_detected` |
| GET | `/api/devices` | 200 | `mock_marker_detected` |
| GET | `/api/elderly/appointments/sync` | 200 | `mock_marker_detected` |
| GET | `/api/elderly/appointments/update` | 200 | `mock_marker_detected` |
| GET | `/api/elderly/medications/sync` | 200 | `mock_marker_detected` |
| GET | `/api/elderly/medications/update` | 200 | `mock_marker_detected` |
| GET | `/api/family/add` | 200 | `mock_marker_detected` |
| GET | `/api/family/chat/messages` | 200 | `mock_marker_detected` |
| GET | `/api/family/chat/send` | 200 | `mock_marker_detected` |
| GET | `/api/family/create` | 200 | `mock_marker_detected` |
| GET | `/api/family/join` | 200 | `mock_marker_detected` |
