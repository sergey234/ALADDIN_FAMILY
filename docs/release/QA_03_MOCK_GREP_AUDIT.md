# B-QA-03 — Mock / Fallback grep audit (iOS security paths)

**Дата:** 2026-06-11

## APIService.shared production path

- `MockAPIService` used **only** when `#if DEBUG && AppConfig.useMockAPI`
- Release builds → real `NetworkManager` ✅

## Security-sensitive grep (Screens + Core)

| Pattern | Prod path hit | Verdict |
|---------|---------------|---------|
| `mock-real-protection` | 0 in Swift prod screens | PASS |
| `sfm_mock` | 0 in Swift | PASS |
| `MockAPIService` in Hub screens | 0 direct usage | PASS |
| `emptyParentalMonitoringDetailPayload` | removed B6 | PASS |
| `mockData` in `09_ElderlyInterfaceScreen` | 0 | PASS |

## Runtime (2026-06-11)

- VPS 24h journalctl `aladdin-api`, `aladdin-backend`, `nginx` → **0 hits** mock markers
- Evidence: `docs/release/QA_03_RUNTIME_VPS_24H.md`

**Verdict:** B-QA-03 **PASS** (static + runtime).
