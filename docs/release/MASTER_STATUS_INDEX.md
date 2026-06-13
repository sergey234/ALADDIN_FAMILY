# ALADDIN — единый мастер-индекс статуса (SSOT)

**Обновлено:** 2026-06-13 · **Build:** **232** (supplemental commit) · **Ветка:** `master`  
**Канонический репозиторий:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

> **Начинайте отсюда.** Один документ — ссылки на все трекеры, аудиты и gate-артефакты.  
> **Build 232 (antifake M2/M3):** главный handoff — **[`BUILD_232_RELEASE_SUMMARY.md`](BUILD_232_RELEASE_SUMMARY.md)**.

---

## 1. Сводка (одна картина)

| Трек | Счёт | Статус | Блокер |
|------|------|--------|--------|
| **Security batches (направление 143)** | **137 / 143** ✅ | Код + VPS + COPY + Hub demos | **R-07 Archive** (6 пунктов) |
| **Build 232 supplemental** (UX + AF M2/M3 + CI/copy) | **28 / 28** ✅ | Код + xcodebuild PASS 2026-06-13 | P0-4 bypass revert, device QA |
| **Antifake `af-*` детальный бэклог** | **38 / 72** ✅ | Hub B2 + M2/M3 build 232 | Workers VPS, af-11 QA gate |
| **Cursor master (36 id)** | **14 / 36** ✅ | См. `.cursor/ALADDIN_MASTER_TODO.md` | perf-1, Archive, device QA |

**xcodebuild (2026-06-13 supplemental):** `BUILD SUCCEEDED` · iPhone 13 Pro Max sim 18.4 · build **232**  
**Commits:** `3cfcf256` (core) + supplemental (af-4-03/05, af-5-04, af-8, CI Call Directory)

---

## 2. Build 232 — что закрыто (supplemental)

| ID | Задача | Evidence |
|----|--------|----------|
| `bypass-premium-qa` | TEMP QA: Hub без paywall | `AntifakeAccessPolicy.swift`, `antifake_premium.py` |
| `af-m2-calls` | Call Directory + sync + post-call | `ALADDINCallDirectory/`, `AntifakeCallDirectorySyncService`, `AntifakeCallObserverService` |
| `af-m3-semi` | История 50 + quick voice 5с | `AntifakeCheckHistoryStore`, `AntifakeQuickVoiceCaptureView` |
| `ux-1-07` | Строка в аккордеоне «Защита от угроз» | `03_NetworkProtectionScreen.swift` |
| `ux-6-03` | Placeholder дневника снов | `WellnessDreamJournalScreen` + LM |
| `ux-6-05` | Coachmark первый визит | `WellnessDreamJournalScreen` |
| `ux-6-01b` | Контраст Values Form | `WellnessValuesCardSheet.swift` |
| `ux-8-06` | Prompt sheet reflective | `WellnessReflectiveModeScreen.swift` |
| `af-4-02` | Call Directory Extension target | Xcode target + embed |
| `af-4-03` | Post-call → Hub + upload banner | `AntifakeCallObserverService`, `AntifakeMediaCheckView` banner |
| `af-4-05` | Spoof heuristics server | `antifake_service.py` |
| `af-5-04` | deepfakes Premium sync | `ProtectionSettingsManager.swift` |
| `af-8` | Честные тексты onboarding/FAQ | `LocalizationManager.swift` |
| `ux-1-06` | Карточка Antifake на Защите | `AntifakeQuickAccessCard` |
| P0-1/P0-2 | CI 4 extensions | `Fastfile`, `check-secrets.yml` |
| P1-8 | Call Directory MARKETING_VERSION 1.0.0 | `ALADDINCallDirectory/Info.plist` |

**⏸ Не блокирует merge, нужно до App Store:** `bypassPremiumGate = false`, `ANTIFAKE_ALLOW_FREE=0`, device QA Call Directory.

---

## 3. Направление 143 — осталось (6)

| ID | Задача |
|----|--------|
| R-07 | B-QA-02 Archive + TestFlight 138/138 |
| — | Hub PNG → `gates/testflight-build227/` |
| — | `xcode_archive_allowed: true` |
| — | 138 matrix walkthrough on device |
| CP3-12 | FAQ phase 2 (не блокер) |
| — | Signing / Distribution cert на Mac PO |

**Детали:** `docs/release/PLAN_FACT_AUDIT_143_2026-06-13.md` · `docs/release/COPY_POST_L3_PROGRESS.md`

---

## 4. Главные трекеры (исполнение)

| Документ | Роль |
|----------|------|
| **[`.cursor/IMPLEMENTATION_BATCHES_TODO.md`](../.cursor/IMPLEMENTATION_BATCHES_TODO.md)** | **143 batch-задачи** — SFM, B1–B7, COPY, QA |
| **[`.cursor/ALADDIN_MASTER_TODO.md`](../.cursor/ALADDIN_MASTER_TODO.md)** | Сводный реестр UX + perf + antifake (36 Cursor id) |
| **[`.cursor/ANTIFAKE_MASTER_ROADMAP.md`](../.cursor/ANTIFAKE_MASTER_ROADMAP.md)** | Antifake M1–M4, Apple limits, риски |
| **[`.cursor/ANTIFAKE_PRODUCTION_TODO.md`](../.cursor/ANTIFAKE_PRODUCTION_TODO.md)** | 72 задачи `af-*` (сервер/ML/iOS детально) |
| **[`.cursor/UX_AUDIT_COMPANION_BATCHES_TODO.md`](../.cursor/UX_AUDIT_COMPANION_BATCHES_TODO.md)** | UX audit батчи 0–10, wellness, perf |
| **[`.cursor/SECURITY_MASTER_INDEX.md`](../.cursor/SECURITY_MASTER_INDEX.md)** | Карта всех security-документов |

---

## 5. План–факт и gates (evidence)

| Документ | Роль |
|----------|------|
| **[`BUILD_232_RELEASE_SUMMARY.md`](BUILD_232_RELEASE_SUMMARY.md)** | **Build 232 handoff — главный документ antifake M2/M3** |
| **[`PLAN_FACT_AUDIT_143_2026-06-13.md`](PLAN_FACT_AUDIT_143_2026-06-13.md)** | **Финальный план–факт 143 + build 232** |
| [`PLAN_FACT_AUDIT_143_2026-06-11.md`](PLAN_FACT_AUDIT_143_2026-06-11.md) | Предыдущая версия (архив) |
| [`gates/security-l3-report.json`](gates/security-l3-report.json) | SSOT evidence gates |
| [`gates/hub-demo-smoke-report.json`](gates/hub-demo-smoke-report.json) | VPS Hub smokes R-08…10 |
| [`COPY_POST_L3_PROGRESS.md`](COPY_POST_L3_PROGRESS.md) | R-19 marketing + счёт 137/143 |

---

## 6. COPY / Marketing (R-19)

| Документ |
|----------|
| [`COPY_POST_L3_FULL_AUDIT.md`](COPY_POST_L3_FULL_AUDIT.md) |
| [`COPY_POST_L3_TODO.md`](COPY_POST_L3_TODO.md) |
| [`COPY_01_ONBOARDING_L3_AUDIT.md`](COPY_01_ONBOARDING_L3_AUDIT.md) |
| [`COPY_02_FAQ_L3_AUDIT.md`](COPY_02_FAQ_L3_AUDIT.md) |
| [`COPY_03_TARIFFS_HUB_MAP.md`](COPY_03_TARIFFS_HUB_MAP.md) |
| [`COPY_04_APP_STORE_REVIEW_NOTES.md`](COPY_04_APP_STORE_REVIEW_NOTES.md) |

---

## 7. Hub demos & QA (R-08…10, Archive)

| Документ |
|----------|
| [`QA_HUB_DEMO_R08_R10.md`](QA_HUB_DEMO_R08_R10.md) |
| [`QA_02_TESTFLIGHT_CHECKLIST.md`](QA_02_TESTFLIGHT_CHECKLIST.md) |
| [`gates/testflight-build227/README.md`](gates/testflight-build227/README.md) |
| [`QA_03_MOCK_GREP_AUDIT.md`](QA_03_MOCK_GREP_AUDIT.md) |

---

## 8. ML handoff & техспеки

| Документ |
|----------|
| [`../ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md`](../ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md) |
| [`../docs/ANTIFAKE_PRODUCTION_PLAN.md`](../ANTIFAKE_PRODUCTION_PLAN.md) |
| [`../docs/ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md`](../ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md) |
| [`../docs/SECURITY_UNIFIED_100_PERCENT_PLAN.md`](../SECURITY_UNIFIED_100_PERCENT_PLAN.md) |
| [`../docs/IOS_EXPLICIT_API_MATRIX.md`](../IOS_EXPLICIT_API_MATRIX.md) |

---

## 9. Как обновлять (правило команды)

1. Закрыли задачу → обновить **детальный** todo (`af-*`, `ux-*`, batch id).
2. Обновить **счёт** в этом файле (`MASTER_STATUS_INDEX.md`).
3. Обновить `security-l3-report.json` если меняется gate.
4. Добавить строку в `PLAN_FACT_AUDIT_143_YYYY-MM-DD.md` при релизной сессии.
5. Bump build: `Info.plist` + `project.pbxproj` (12×) + `AppConfig.swift` (2×).

---

*SSOT v1.0 · build 232 · 137/143 + supplemental 18/18*
