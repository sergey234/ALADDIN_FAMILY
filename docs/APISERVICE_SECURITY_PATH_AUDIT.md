# APIService Security Path Audit (B-PRE-03)

**Дата:** 2026-06-10 · **Batch:** B-PRE-03  
**Матрица:** `docs/IOS_EXPLICIT_API_MATRIX.md`

---

## Вердикт: ✅ PASS

`Core/Network/APIService.swift` использует **только** `AppConfig.Endpoint.*` для security domains.  
Hardcoded legacy `/api/reports/dark-web/*`, `/api/reports/identity-theft/*`, `/api/reports/privacy/*` — **не найдены**.

---

## Explicit paths в APIService (via AppConfig)

| Domain | AppConfig keys used | Explicit prefix |
|--------|---------------------|-----------------|
| Dark Web | `darkWebStats`, `darkWebLeaksList`, `darkWebScans`, `darkWebResolve`, `darkWebScanStart`, `darkWebScanSecure`, `darkWebScanFast` | `/api/darkweb/*` |
| Identity | `identityTheftAttempts`, `identityTheftStats`, `identityTheftAllow`, `identityTheftBlock`, `identityTheftWhitelist` | `/api/identity-theft/*` |
| Data Cleanup | `dataCleanupStats`, `dataCleanupRecords`, `dataCleanupStart` | `/api/data-cleanup/*` |
| Location Bubble | `locationBubble` | `/api/location-bubble/*` |
| Malware/AV | `malwareThreats`, `malwareQuarantineAction`, `malwareFileScan` | `/api/malware/*`, `/api/antivirus/scan` |
| Antifake | `antifakeCheckText`, `antifakeCheckUrl`, `antifakeUploadMedia`, `antifakePollJob`, `getAntifakeMetrics` | `/api/antifake/*` (all 8 explicit paths) |

---

## Pending (следующие batch)

| ID | Задача | Batch |
|----|--------|-------|
| — | `antifakeCallAnalyze` wire | B2-06 |
| — | `identityTheftDetect`, `identityTheftMonitorCredit` wire | B4 |
| — | `parentalMonitoringDetail/Events` wire | B6 |
| — | `mobileScan`, `mobileSecurityCheck` wire | B5 |

---

## Проверка (grep)

```bash
rg '/api/reports/(dark-web|identity-theft|privacy/(location|cleanup))' Core/Network/APIService.swift
# ожидаем: 0 matches
```

*Audit B-PRE-03 ✅ · Antifake API 8/8 wired · B2-08 Share extension ✅ · Next: B2-09 TestFlight matrix*
