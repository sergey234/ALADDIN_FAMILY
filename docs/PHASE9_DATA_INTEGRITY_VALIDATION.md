# Phase 9.2 Validation (Elderly Data Integrity + Parent Desync Report)

Scope:

- `9.2` — усиление целостности/восстановления health-сущностей 60+.
- `9.2` — минимальный интеграционный контур отчёта рассинхронизации для родителя.

## Smoke command

Run:

`python3 scripts/phase9_data_integrity_smoke.py`

Expected:

- `SMOKE RESULT: PASS`

## What it validates

1. **Elderly integrity contracts**
   - no-loss cross-device merge (`synchronizeAcrossDevices` + versioned envelope).
   - `ElderlyHealthSyncAudit` exists.
   - `ElderlyHealthSyncReport` exists.
   - `perform/persistSnapshot/persistLatestReport/latestReport` are available.
   - audit is invoked on elderly screen appear.
2. **Parent desync integration**
   - parental screen has state + banner for elderly desync report.
   - parental screen reads latest persisted elderly sync report.
3. **Build verification**
   - app build succeeds on iPhone 16 simulator.

## Notes

- This is the minimum viable integration slice for phase 9.2.
- Further steps can expand report details and server-backed reconciliation.
