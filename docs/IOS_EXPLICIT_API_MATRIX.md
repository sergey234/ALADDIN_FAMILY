# iOS ↔ Explicit Backend API Matrix (B1 canonical)

**Версия:** 1.0 · **2026-06-10**  
**Связано:** `docs/SEC06_LEGACY_ROUTER_AUDIT.md`, `Core/Config/AppConfig.swift`, GATE-D smokes  
**Правило:** iOS Hub'ы и `APIService` **только explicit paths** из `app/routers/*`. Legacy `/api/reports/*` — deprecated, не использовать в новом коде.

---

## Приоритет миграции (B-PRE → B2)

| Шаг | Batch ID | Действие |
|-----|----------|----------|
| 1 | `B-PRE-01` | Этот документ ✅ |
| 2 | `SYNC-01`…`SYNC-05` | Синхронизация todo-файлов |
| 3 | `B2-00` | `AppConfig.Endpoint` → explicit paths |
| 4 | `B2-00b` | `SecurityVerdict` model + `PremiumGateHandler` |
| 5 | `B2-00c` | `AppConfigTests` — assert no `/api/reports/*` security |
| 6 | `B2-01`…`B2-10` | Antifake Hub UI + wire |

---

## Матрица доменов

| Hub | AppConfig key(s) | Explicit path (B1) | Legacy iOS (deprecated) | Smoke script |
|-----|------------------|--------------------|-------------------------|--------------|
| **Protection** | `protectionSettings`, `protectionEnable`… | `/api/protection/*` | — | BATCH 0 |
| **Antifake** | `antifakeCheckText`… | `/api/antifake/*` | `/api/deepfake/*`, wildcard | `test_antifake_prod_smoke.py` |
| **Dark Web** | `darkWebStats`, `darkWebLeaks`… | `/api/darkweb/*` | `/api/reports/dark-web/*` | `test_darkweb_prod_smoke.py` |
| **Identity** | `identityTheftStats`, `identityTheftDetect`… | `/api/identity-theft/*` | `/api/reports/identity-theft/*` | `test_identity_theft_prod_smoke.py` |
| **Data Cleanup** | `dataCleanupStats`, `dataCleanupStart` | `/api/data-cleanup/*` | `/api/reports/privacy/cleanup/*` | `test_data_cleanup_prod_smoke.py` |
| **Location Bubble** | `locationBubble`, `locationStats`… | `/api/location-bubble/*` | `/api/reports/privacy/location/*`, `/api/location/bubble` | `test_location_bubble_prod_smoke.py` |
| **Malware/AV** | `malwareThreats`, `malwareFileScan` | `/api/malware/*`, `/api/antivirus/scan` | `/api/protection/threats` (compat) | `test_malware_prod_smoke.py` |
| **Phishing/Components** | `componentStatus`… | `/api/phishing/*`, `/api/components/*` | — | `test_components_prod_smoke.py` |
| **IoT** | `iotScan`, `iotStatus`… | `/api/iot/*` | legacy `iot_router` disabled | `test_iot_prod_smoke.py` |
| **Mobile Security** | *(add B5)* | `/api/mobile/*` | — | `test_mobile_security_prod_smoke.py` |
| **Parental Monitoring** | *(add B6)* | `/api/parental-control/monitoring/*` | mega-router except monitoring | `test_parental_monitoring_prod_smoke.py` |

---

## Antifake — explicit endpoints (B2-01)

| Method | Path | AppConfig key | Async |
|--------|------|---------------|-------|
| POST | `/api/antifake/check/text` | `antifakeCheckText` | sync |
| POST | `/api/antifake/check/url` | `antifakeCheckUrl` | sync |
| POST | `/api/antifake/check/audio` | `antifakeCheckAudio` | job |
| POST | `/api/antifake/check/video` | `antifakeCheckVideo` | job |
| POST | `/api/antifake/check/document` | `antifakeCheckDocument` | job |
| POST | `/api/antifake/call/analyze` | `antifakeCallAnalyze` | job |
| GET | `/api/antifake/jobs/{id}` | `antifakeJob(id:)` | poll |
| GET | `/api/antifake/metrics` | `antifakeMetrics` | sync |

**Verdict contract:** `verdict`, `confidence`, `reasons`, `source` (≠ mock), `agent`, `premium_required`.

---

## Dark Web — path mapping

| AppConfig key | Explicit | Legacy (remove) |
|---------------|----------|-----------------|
| `darkWebStats` | `/api/darkweb/stats` | `/api/reports/dark-web/stats` |
| `darkWebLeaks` | `/api/darkweb/leaks` | `/api/reports/dark-web/leaks` |
| `darkWebLeaksList` | `/api/darkweb/leaks` | `/api/reports/dark-web/leaks/list` |
| `darkWebScans` | `/api/darkweb/scans` | `/api/reports/dark-web/scans` |
| `darkWebScanStart` | `/api/darkweb/scan/start` | `/api/reports/dark-web/scan/start` |
| `darkWebScanSecure` | `/api/darkweb/scan/start` | `/api/reports/dark-web/scan/secure` |
| `darkWebScanFast` | `/api/darkweb/check` | `/api/reports/dark-web/scan/fast` |
| `darkWebResolve` | `/api/darkweb/resolve` | `/api/reports/dark-web/resolve` |

Legacy-only (Tier D, keep until SEC-06-P2-01): `GET /api/darkweb/breaches`, `POST /start-monitoring`.

---

## Identity — path mapping

| AppConfig key | Explicit | Notes |
|---------------|----------|-------|
| `identityTheftStats` | `/api/identity-theft/stats` | |
| `identityTheftAttempts` | `/api/identity-theft/attempts` | |
| `identityTheftDetect` | `/api/identity-theft/detect` | **NEW** B2-00 |
| `identityTheftMonitorCredit` | `/api/identity-theft/monitor/credit` | canonical (not `/monitor-credit`) |
| `identityTheftCheckFraud` | `/api/identity-theft/check/fraud` | **NEW** |
| `identityTheftAllow` | `/api/identity-theft/allow` | |
| `identityTheftBlock` | `/api/identity-theft/block` | |
| `identityTheftWhitelist` | `/api/identity-theft/whitelist` | legacy-only until P2; may 404 |

Legacy-only: `POST /monitor-snils` (SEC-06 Tier D).

---

## Location Bubble — path mapping

| AppConfig key | Explicit |
|---------------|----------|
| `locationStats` | `/api/location-bubble/stats` |
| `locationRequests` | `/api/location-bubble/requests` |
| `locationBubble` | `/api/location-bubble/generate` |
| `locationAllow` | `/api/location-bubble/allow` |
| `locationBlock` | `/api/location-bubble/block` |
| `locationUpdateAccuracy` | `/api/location-bubble/update-accuracy` |
| `locationBubbleSettings` | `/api/location-bubble/settings` |

SEC-06: legacy `/api/location/bubble/*` skipped when explicit available.

---

## Data Cleanup — path mapping

| AppConfig key | Explicit |
|---------------|----------|
| `dataCleanupStats` | `/api/data-cleanup/stats` |
| `dataCleanupRecords` | `/api/data-cleanup/records` |
| `dataCleanupStart` | `/api/data-cleanup/start` |

Legacy dual-stack: `/scan`, `/remove`, `/preferences` on legacy router (Tier D).

---

## Parental Monitoring (B6)

| Method | Path | AppConfig key |
|--------|------|---------------|
| GET | `/api/parental-control/monitoring/detail` | `parentalMonitoringDetail` |
| POST | `/api/parental-control/monitoring/events` | `parentalMonitoringEvents` |

---

## Mobile Security (B5)

| Method | Path |
|--------|------|
| GET | `/api/mobile/app_lock` |
| GET | `/api/mobile/biometric` |
| GET/POST | `/api/mobile/security/check` |
| POST | `/api/mobile/scan` |

---

## Ещё legacy (не трогать в B2-00)

| Path prefix | Причина |
|-------------|---------|
| `/api/reports/privacy/tracker/*` | anti-tracker — нет explicit B1 |
| `/api/reports/driving/*` | вне security 100% scope |
| `/api/reports/ai-categories/*` | отдельный домен |

---

## Проверка после B2-00

```bash
# Unit
xcodebuild test -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' \
  -only-testing:ALADDINUnitTests/AppConfigTests/testExplicitSecurityEndpointsUseCanonicalPaths

# Grep — не должно быть reports/* в security keys
rg '/api/reports/(dark-web|identity-theft|privacy/(location|cleanup))' Core/Config/AppConfig.swift
```

---

## SEC-06 Phase 2 backlog (BATCH SEC-P2)

| ID | Задача |
|----|--------|
| `SEC-06-P2-01` | darkweb `/breaches` → explicit or 410 |
| `SEC-06-P2-02` | identity `/monitor-credit` unify |
| `SEC-06-P2-03` | `/api/location/bubble` → 301/410 doc |
| `SEC-06-P2-04` | Split parental_control mega-router |
| `SEC-06-P2-05` | misc_other_compat devices → dedicated router |

*Matrix v1.0 · Next: B2-00 AppConfig migration*
