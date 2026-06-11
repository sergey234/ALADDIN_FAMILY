# ML System Handoff — Security 100% (138 функций + SFM + Antifake)

**Версия:** 1.4 · **2026-06-11** (BATCH 7 🔄 GATE-J · 111/143 · B7-04 VPS pending)  
**Аудитория:** следующая ML-система / Cursor Agent  
**Репозиторий:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/`  
**Prod:** `149.154.65.180` · SSH `~/.ssh/aladdin_server` · API `https://aladdin-ai.ru` · backend `:8002` · SFM `:8003`

---

## 0. Первое действие ML-системы (обязательно)

0. **SFM Truth (30 сек):** прочитать `docs/SFM_ML_QUICKSTART.md` и выполнить `sfm_truth_check.sh`.  
   **Не писать «SFM нет / неполный»** без этого шага. Спека: `docs/SFM_SINGLE_SOURCE_OF_TRUTH.md`.

1. Прочитать документы из **§1** в указанном порядке.
2. Открыть `.cursor/IMPLEMENTATION_BATCHES_TODO.md` — **главный todo для Cursor**.
3. Вести прогресс: при закрытии задачи ставить ✅ в:
   - `.cursor/IMPLEMENTATION_BATCHES_TODO.md`
   - зеркальный ID в `.cursor/SECURITY_138_MASTER_TODO.md` и/или `.cursor/ANTIFAKE_PRODUCTION_TODO.md`
4. После **каждого крупного блока** — gate из **§4** (тесты). **Без PASS — не начинать следующий блок.**
5. **Xcode Archive / TestFlight — только после 100% batch (§5).** Между блоками — только `xcodebuild test` / unit tests / backend smoke.

**Запрещено сообщать заказчику «готово / работает» без PASS gate текущего блока + записи в `security-l3-report.json`.**

---

## 1. Пакет документов для передачи ML-системе

### 1.1 Обязательные (читать первыми)

| # | Путь | Зачем |
|---|------|-------|
| 1 | **`ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md`** | Этот файл — инструкция |
| 2 | `.cursor/SECURITY_MASTER_INDEX.md` | Карта всех задач |
| 3 | `.cursor/IMPLEMENTATION_BATCHES_TODO.md` | **143 batch-задачи — главный tracker (107/143 ✅)** |
| 4 | `docs/OPS_ANTI_REGRESSION_GATES.md` | Анти-регрессия SFM |
| 5 | `docs/server/L3_SMOKE_CONTRACT.md` | Критерии PASS/FAIL для ML |
| 6 | `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` | SSH, prod, **MOCK ЗАПРЕЩЕН** |
| 7 | `docs/SECURITY_UNIFIED_100_PERCENT_PLAN.md` | Продуктовый план 9 категорий |
| 8 | `docs/SFM_SERVER_FORENSIC_REPORT.md` | Факты VPS (SFM на диске, wire сломан) |
| 8a | **`docs/SFM_SINGLE_SOURCE_OF_TRUTH.md`** | **Почему ML путались + как не путаться** |
| 8b | **`docs/SFM_ML_QUICKSTART.md`** | **Первая команда для любой ML** |
| 9 | **`docs/SEC06_LEGACY_ROUTER_AUDIT.md`** | **Legacy vs explicit — что отключено, что оставить** |
| 9a | **`docs/IOS_EXPLICIT_API_MATRIX.md`** | **iOS AppConfig ↔ explicit B1 paths (B-PRE)** |
| 10 | **`docs/release/gates/security-l3-report.json`** | **Evidence всех gates** |

### 1.2 Todo и детализация по доменам

| Путь | Задач |
|------|-------|
| `.cursor/ANTIFAKE_PRODUCTION_TODO.md` | 72 (`af-0`…`af-12`) — news/video/audio/calls |
| `.cursor/SECURITY_138_MASTER_TODO.md` | 226 — SEC, SFM, DW, ID, CAT… |
| `.cursor/SECURITY_100_PERCENT_ROADMAP_TODO.md` | 53 gates `R0-G`…`R8-G` |

### 1.3 Техспеки

| Путь |
|------|
| `docs/ANTIFAKE_PRODUCTION_PLAN.md` |
| `docs/SECURITY_100_PERCENT_MASTER_PLAN.md` |
| `docs/SECURITY_138_GAP_ANALYSIS.md` |
| `docs/SFM_CENTRAL_ARCHITECTURE_COMPLETE.md` |

### 1.4 Skills Cursor (если доступны)

| Путь |
|------|
| `.cursor/skills/aladdin-server-deploy/SKILL.md` |
| `.cursor/skills/aladdin-no-mock-bypass/SKILL.md` |
| `.cursor/rules/prod-no-mock-bypass.mdc` (если есть) |

### 1.5 Не передавать как «источник правды»

- `docs/audit/EXTENDED_138_CHECKLIST.md` — переписать на L3 (`B-OPS-12`)
- Старые отчёты «1074 ok» без L3 smoke — **игнорировать**

---

## 2. Контекст: что сломано и что план устраняет

| # | Проблема | Решение в плане | Batch |
|---|----------|-----------------|-------|
| P1 | SFM код есть, :8003 в fallback | SFM-WIRE | W01–W10 |
| P2 | Registry 14 вместо 1000+ | Rebuild registry | W06 |
| P3 | ML: HTTP 200 = «работает» | L3 contract + OPS | B-OPS-07…12 |
| P4 | protection не persist | PostgreSQL UPSERT | B0-02 |
| P5 | enable → 500 (logger) | sec-01 | B0-01 |
| P6 | iOS не грузит settings | loadSettingsFromServer | B0-04 |
| P7 | wildcard mock | blocklist + explicit routers | B0-05, B1 |
| P8 | antifake пустой result | `/api/antifake/check/*` | af-2, B1-01, B2 |
| P9 | 9 category schema mismatch | canonical IDs | B0-03 |
| P10 | OptimizedSFM mock | remove prod path | W07, B-OPS-04 |
| P11 | healthcheck 203 | fix systemd | B-OPS-09 |
| P12 | 138 checklist ложный | L3 only | B-QA-01 |
| P13 | Онбординг vs реальность | **не менять** до COPY | B-COPY-01 audit only |

---

## 3. Порядок реализации (строго)

```
Фаза 1: SFM-WIRE (W01–W10) + OPS (B-OPS-01…06)     → GATE-A
Фаза 2: BATCH 0 SEC-INFRA (B0-01…08)                 → GATE-B + GATE-C
Фаза 3: AF-1…3 backend + BATCH 1 (B1-01…12)        → GATE-D (antifake API)
Фаза 4: BATCH 2 + AF-5…6 iOS Hub                   → GATE-E (antifake L3 backend; iOS unit only)
Фаза 5: BATCH 3 Privacy                            → GATE-F
Фаза 6: BATCH 4 Identity                           → GATE-G
Фаза 7: BATCH 5 Device                             → GATE-H
Фаза 8: BATCH 6 Family                             → GATE-I
Фаза 9: BATCH 7 Extras                             → GATE-J
Фаза 10: OPS-07…12 + BATCH COPY                    → GATE-K
Фаза 11: BATCH QA                                  → GATE-FINAL
Фаза 12: XCODE ARCHIVE + TestFlight                → только после GATE-FINAL
```

Параллель: backend + iOS внутри фазы 4–7 допустим при 2 исполнителях.

---

## 4. Тесты после каждого крупного блока (не Xcode Archive)

### GATE-A — после SFM-WIRE + OPS-01…06

| Проверка | Команда / критерий |
|----------|-------------------|
| SFM loaded | `curl :8003/api/health` → `sfm_loaded: true` |
| Registry | `functions_count >= 1000` |
| Unknown fn | `__nonexistent__` → не success |
| Real agent | `fake_news_detection_agent` → не `status:success` |
| systemd | `aladdin-sfm-core` active, не restart loop |

Записать: `security-l3-report.json` block=`SFM-WIRE`

---

### GATE-B — после BATCH 0

| Проверка | Критерий |
|----------|----------|
| enable deepfakes | POST → **200**, не 500 |
| persist | POST true → GET **true** |
| iOS | `ProtectionSettingsManager` load не stub (code review + unit test) |
| wildcard | `POST /api/deepfake/analyze-video` → **404 или explicit**, не mock envelope |
| 9 categories | round-trip каждой |

Записать: block=`SEC-INFRA`

---

### GATE-D — после BATCH 1 (B1-01…B1-12, SEC-06) ✅

| Проверка | Критерий |
|----------|----------|
| Orchestrator | `docs/server/test_security_prod_smoke.py` → **pass:true** (11 domains) |
| OpenAPI | `test_security_openapi_prod_smoke.py` → 32 explicit routes |
| Per-domain | verdict/source≠mock, premium 403, no mock envelope |
| Legacy | `docs/SEC06_LEGACY_ROUTER_AUDIT.md` — explicit wins on 5 collisions |

**Xcode:** только `swift test` — **не Archive** до GATE-FINAL

---

### GATE-E — после BATCH 2 (iOS Antifake Hub)

| Проверка | Критерий |
|----------|----------|
| Unit | `ProtectionSettings` round-trip tests |
| UI code | AntifakeHub 4 tabs exist, navigation from deepfakes |
| Simulator | smoke navigate to Hub (optional) |

**Запрещено:** TestFlight до GATE-FINAL

---

### GATE-F / G / H — Privacy / Identity / Device

Для каждого Hub:

- Backend smoke по домену (`test_security_prod_smoke.py` section)
- iOS: wired API calls in code (grep APIService)
- Per-threat CAT IDs: mark ✅ in MASTER when L3 criterion met

---

### GATE-I / J — Family + Extras

- Parental monitoring/detail: не mock envelope
- VPN regression smoke
- Elderly: no mockData in calendar

---

### GATE-K — OPS + COPY

- `functional-138` runner fails on 404/mock
- FAQ audit only — **onboarding UI untouched**
- `L3_SMOKE_CONTRACT.md` linked from ML guide

---

### GATE-FINAL — BATCH QA (B-QA-01…05)

- 138/138 manual TestFlight checklist
- prod grep 24h: zero `mock-real-protection`
- `security-l3-report.json` all blocks pass
- merge `SECURITY_UNIFIED_IMPLEMENTATION.md`

**Только после GATE-FINAL → §5 Xcode**

---

## 5. Xcode — ТОЛЬКО в самом конце

### Когда разрешено

- ✅ Все batch W, OPS, 0–7, COPY, QA — **✅**
- ✅ GATE-FINAL — **PASS**
- ✅ `security-l3-report.json` — all blocks pass

### Когда запрещено

- ❌ После каждого блока делать Archive/TestFlight «для проверки»
- ❌ Менять onboarding в процессе

### Разрешено между блоками

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
xcodebuild test -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 16' -quiet
# или конкретные test targets: ProtectionSettings, Antifake, etc.
```

### Финальная сборка (после 100%)

```bash
# 1. Bump build number
# 2. Archive
xcodebuild archive -scheme ALADDIN -archivePath build/ALADDIN.xcarchive

# 3. Export + Upload TestFlight
# 4. TestFlight L3: все Hub'ы, 138 matrix, скриншоты в docs/release/gates/
# 5. B-QA-02 sign-off
```

---

## 6. Как ML не выдавать ложную информацию

### Обязательный шаблон отчёта после блока

```markdown
## Block: [SFM-WIRE | SEC-INFRA | …]

### Сделано
- [task IDs] ✅

### Проверено (evidence)
- [команда] → [вывод / pass]

### Не проверено / pending
- [что] — причина

### Вердикт блока
- GATE: PASS | FAIL

### Ложные сигналы отклонены
- [если был HTTP 200 mock — указать FAIL]
```

### Чеклист «нельзя писать»

- [ ] «SFM работает» без `sfm_loaded: true`
- [ ] «Antifake готов» без verdict API
- [ ] «138 ok» без TestFlight L3
- [ ] «Toggle sync» без GET после POST
- [ ] «Registry 1074» без `len(functions)` на живом процессе

### Чеклист «можно писать PASS»

- [ ] Все task IDs блока ✅ в IMPLEMENTATION_BATCHES
- [ ] Gate таблица §4 выполнена
- [ ] `security-l3-report.json` обновлён
- [ ] Нет `mock-real-protection` в curl ответах блока

---

## 7. Полный todo для Cursor (все batch и задачи)

ML-система **должна** использовать `.cursor/IMPLEMENTATION_BATCHES_TODO.md` как primary tracker. Ниже — сводная таблица (дубликат для handoff).

### 7.1 SFM-WIRE — 10

`B-SFM-W01` backup registry · `W02` reactive symlink · `W03` start_sfm PYTHONPATH · `W04` systemd env · `W05` rename stub · `W06` rebuild registry · `W07` remove OptimizedSFM · `W08` smoke ≥1000 fn · `W09` enable→agents · `W10` api mapping routers

### 7.2 OPS — 20

`B-OPS-01`…`12` — анти-регрессия · `B-OPS-13`…`20` — **SFM truth для ML** — см. `docs/OPS_ANTI_REGRESSION_GATES.md` и `docs/SFM_SINGLE_SOURCE_OF_TRUTH.md`

### 7.3 SEC-INFRA — 8

`B0-01`…`B0-08`

### 7.4 Antifake — 72

| Batch | IDs |
|-------|-----|
| AF-0 | `af-0-01`…`af-0-08` |
| AF-1 | `af-1-01`…`af-1-09` |
| AF-2 | `af-2-01`…`af-2-10` |
| AF-3 | `af-3-01`…`af-3-07` |
| AF-4 | `af-4-01`…`af-4-08` |
| AF-5 | `af-5-01`…`af-5-06` |
| AF-6 | `af-6-01`…`af-6-10` |
| AF-7 | `af-7-01`…`af-7-05` |
| AF-8 | `af-8-01`…`af-8-06` |
| AF-9 | `af-9-01`…`af-9-08` |
| AF-10 | `af-10-01`…`af-10-05` |
| AF-11 | `af-11-01`…`af-11-06` |
| AF-12 | `af-12-01`…`af-12-04` |

### 7.5 Implementation B1–B-QA — 58

`B1-01`…`B1-12` · `B2-01`…`B2-10` · `B3-01`…`B3-08` · `B4-01`…`B4-06` · `B5-01`…`B5-09` · `B6-01`…`B6-05` · `B7-01`…`B7-04` · `B-COPY-01`…`04` · `B-QA-01`…`05`

### 7.6 MASTER domains — ~154 (без дублей af)

`sec-01`…`sec-10` · `sfm-01`…`sfm-12` · `dw-01`…`dw-08` · `id-01`…`id-08` · `dc-01`…`dc-06` · `loc-01`…`loc-06` · `av-01`…`av-08` · `comp-01`…`comp-10` · `iot-01`…`iot-07` · `mob-01`…`mob-06` · `pc-01`…`pc-06` · `em-01`…`em-06` · `eld-01`…`eld-04` · `sync-01`…`sync-05` · `copy-*`

### 7.7 Per-threat L3 — 58

`cyb-01`…`10` · `frd-01`…`12` · `chd-01`…`17` · `dlk-01`…`12` · `dfk-01`…`08` · `net-01`…`06` · `mob-07`…`10` · `fam-01`…`15` · `iot-08`…`10`

### 7.8 Roadmap gates — 53

`R0-G1`…`R0-G12` · `R1-G1`…`R1-G10` · `R2-G1`…`R2-G8` · `R3-G1`…`R3-G6` · `R4-G1`…`R4-G9` · `R5-G1`…`R5-G5` · `R6-G1`…`R6-G5` · `R7-G1`…`R7-G5` · `R8-G1`…`R8-G4`

### 7.9 Итого

| Блок | Кол-во |
|------|--------|
| SFM-WIRE | 10 |
| OPS | 12 |
| SEC-INFRA | 8 |
| Antifake af-* | 72 |
| Privacy/Identity/Device… | ~61 |
| Per-threat CAT | 58 |
| Roadmap gates | 53 |
| Implementation B1…QA | ~58 |
| **С перекрытием** | **~280** |

---

## 8. Сервер: быстрые команды

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180
cd /opt/aladdin-backend

# API
curl -s http://127.0.0.1:8002/api/health

# SFM
curl -s http://127.0.0.1:8003/api/health

# JWT smoke
curl -s -X POST https://aladdin-ai.ru/api/auth/register-device \
  -H 'Content-Type: application/json' \
  -d '{"deviceId":"ml-smoke-test"}'
```

**Не использовать** прямой `:8002` с Mac (firewall) — `aladdin-ai.ru` или SSH localhost.

---

## 9. Синхронизация статусов (правило для ML)

1. Закрыл `B-SFM-W03` → ✅ в `IMPLEMENTATION_BATCHES_TODO.md` + `sfm-03` в MASTER  
2. Закрыл `af-2-02` → ✅ в `ANTIFAKE_PRODUCTION_TODO.md` + MASTER § AF  
3. После gate → запись в `docs/release/gates/security-l3-report.json`  
4. Пересчитать счётчик в шапке IMPLEMENTATION_BATCHES

---

## 10. Итог для заказчика (когда 100%)

| Компонент | Результат |
|-----------|-----------|
| SFM | loaded, registry ≥1000, honest health, no silent fallback |
| Antifake | text/url/audio/video/doc/call + Hub iOS |
| 9 categories | L2 persist + L3 Hub |
| 138 functions | L1+L2+L3 TestFlight |
| ML checks | только L3 contract |
| Deploy | preflight + smoke 15m |
| Онбординг | без изменений (или COPY после L3) |
| Xcode | **один финальный Archive** после GATE-FINAL |

---

## 11. Prompt для старта следующей ML-системы

```
Ты — ML-исполнитель ALADDIN Security 100%.

1. Прочитай ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md полностью (§12 — текущий статус).
2. Веди прогресс в .cursor/IMPLEMENTATION_BATCHES_TODO.md (ставь ✅).
3. Шаг 0: docs/SFM_ML_QUICKSTART.md → sfm_truth_check.sh
4. Подтверди GATE-D: docs/server/test_security_prod_smoke.py на VPS → pass:true
5. Заверши B-PRE: B2-00b SecurityVerdict layer → B-PRE-03 APIService audit
6. BATCH 2: B2-02 AntifakeHubScreen (AppConfig explicit ✅ B2-00)
7. После каждого блока — gate §4 + security-l3-report.json.
8. Не сообщай «работает» без L3 evidence.
9. Xcode Archive/TestFlight — только после B-QA-02 PASS.
10. Онбординг не менять до B-COPY-01 (audit only).

Prod: ssh -i ~/.ssh/aladdin_server root@149.154.65.180
Mock запрещён: ALADDIN_SERVER_CONNECTION_GUIDE § PRODUCTION HARD RULE
Legacy: docs/SEC06_LEGACY_ROUTER_AUDIT.md
iOS paths: docs/IOS_EXPLICIT_API_MATRIX.md
```

---

## 12. Состояние на 2026-06-11 (план–факт для следующей ML)

> **SSOT:** `docs/release/PLAN_FACT_AUDIT_143_2026-06-11.md` · `security-l3-report.json` → **137/143**

### 12.1 Закрыто (не переделывать без регрессии)

| Блок | Задач | Gate | Evidence |
|------|-------|------|----------|
| SFM-WIRE | 12/12 | GATE-A | `:8003` sfm_loaded, registry ≥1000 |
| OPS | 22/22 | GATE-A0 | sfm_truth_check, L3 contract |
| BATCH 0 | 8/8 | GATE-B | 9 toggles persist, wildcard block |
| BATCH 1 | 12/12 + SEC-06 | GATE-D backend | 11 domain smokes + OpenAPI |
| BATCH SYNC | 5/5 | — | trackers aligned |
| B-PRE iOS | 6/6 | pre-GATE-E | AppConfig + SecurityVerdict + B2-00c tests |
| BATCH 2 Antifake iOS | 12/12 | GATE-E | Hub 4 tabs; B2-09 R-08 VPS smoke ✅ |
| BATCH 3 Privacy Hub | 8/8 | GATE-F | dlk-01…12; B3-08 R-09 VPS smoke ✅ |
| BATCH 4 Identity Hub | 6/6 | GATE-G | frd-01…12; B4-06 R-10 VPS smoke ✅ |
| BATCH 5 Device Hub | 9/9 | GATE-H | cyb/mob/iot catalogs + EICAR |
| BATCH 6 Family polish | 5/5 | GATE-I | см. §12.2 |
| BATCH 7 Extras | 4/4 | GATE-J | emergency smoke + VPN 10/10 |
| BATCH LOC | 12/12 | pre-FINAL | B-LOC-00…11 |
| BATCH COPY | 4/4 | GATE-K | COPY_01…04 |
| SEC-P2 | 5/5 | post-L3 | SEC_P2_LEGACY_MIGRATION |
| **R-19 COPY-POST-L3** | 1/1 | GATE-K-post | FAQ 41, OB sync, Privacy 5+ |
| **R-08…10 Hub demos** | 3/3 | GATE-FINAL-prep | hub-demo-smoke-report.json |

**Счёт:** **137 / 143** total — осталось **6** (R-07 Archive block)

### 12.2 BATCH 6 — что сделано (GATE-I PASS)

| ID | Что | Файлы / паттерн |
|----|-----|-----------------|
| B6-01 | Убран mock envelope parental monitoring | `NetworkManager.swift` — удалён `emptyParentalMonitoringDetailPayload()`; `Shared/Models/ParentalMonitoringValidation.swift` — `validateForProduction()`; wire в `APIService.getParentalMonitoringDetail` |
| B6-02 | Family modals на live API | **`Screens/02_FamilyScreen.swift`** — все модалки; **`Screens/FamilyModals.swift` — orphan, НЕ в pbxproj, не трогать** |
| B6-03 | PDF/CSV отчёты | `Core/Managers/ParentalControlReportsManager.swift` (@MainActor), `Core/Content/Parent/ParentalMonitoringReportExporter.swift`, кнопка export в `FamilyReportsModal` |
| B6-04 | Geofence geocoding | `Core/Services/GeofenceGeocodingService.swift` (CLGeocoder); `FamilyLocationModal`, `GeofencesSettingsModal` |
| B6-05 | Child threats coverage | `Shared/Models/FamilyChildThreatCatalog.swift` (chd-01…17), `Shared/Components/FamilyChildThreatCoverageView.swift` в `FamilyMonitoringModal` |
| LOC | B-LOC-06 ✅ | keys `family_hub_chd_*`, `family_monitoring_export_*` в `LocalizationManager.swift` RU+EN |
| Tests | unit (run at GATE-FINAL) | `ParentalMonitoringValidationTests.swift`, `FamilyChildThreatCatalogTests.swift` |

**Build:** `xcodebuild -scheme ALADDIN -destination 'platform=iOS Simulator,id=82789999-A1C3-4B10-A2B9-CFE6BBB24ECF' build` → **BUILD SUCCEEDED** (2026-06-10).

**pbxproj:** при добавлении файлов — полные пути (`Shared/Models/…`, `ViewModels/…`), иначе «Build input files cannot be found».

### 12.3 Следующий шаг ML (строго по порядку)

```
1. R-07 B-QA-02: Xcode Archive + TestFlight (Mac + Apple ID)
2. PNG Hub screenshots → gates/testflight-build227/
3. 138 matrix walkthrough on device
4. security-l3-report.json → xcode_archive_allowed: true, QA-138 pass
```

**Готово до Archive:** build ✅ · VPS smokes ✅ · R-19 marketing ✅ · mock grep 0 ✅

### 12.4 iOS migration (B-PRE) — актуальный статус

| ID | Статус | Evidence |
|----|--------|----------|
| B-PRE-01 matrix doc | ✅ | `docs/IOS_EXPLICIT_API_MATRIX.md` |
| B2-00 AppConfig explicit | ✅ | `Core/Config/AppConfig.swift` |
| B2-00b SecurityVerdict + PremiumGate | ✅ | `SecurityVerdictModels.swift`, `PremiumGateHandler.swift` |
| B2-00c unit test | ✅ | `AppConfigTests.testExplicitSecurityEndpointsUseCanonicalPaths` |
| B-PRE-03 APIService audit | ✅ | `docs/APISERVICE_SECURITY_PATH_AUDIT.md` |
| B-PRE-02 GATE-D re-confirm | 🔄 | периодически на VPS |

### 12.5 Что осталось (high level)

| Фаза | Задач | Gate |
|------|-------|------|
| R-07 Archive + TestFlight | 1 | GATE-FINAL |
| Hub PNG on device | 3 files | B-QA-02 |
| 138 walkthrough | 1 | B-QA-02 |
| CP3-12 phase-2 FAQ | defer | post-release |

**Backend + iOS Hubs + marketing copy — готовы.** Дальше — **Archive на Mac PO** (`QA_02_TESTFLIGHT_CHECKLIST.md`).

---

## 13. BATCH 7 Extras — подробная инструкция для ML

**Цель batch:** закрыть emergency (crash + roadside), elderly interface без mock, VPN regression.  
**Gate:** GATE-J → обновить `security-l3-report.json` block `EXTRAS` → `pass`.  
**LOC gate:** B-LOC-07 после всех UI-строк B7.

### 13.1 B7-01 — Crash detection (em-01…em-03)

**Зачем:** L3 для `crash_detection_agent` — настройки, мониторинг CoreMotion, алерт и история через prod API, без лок-only сохранения.

**Что уже есть (не переписывать с нуля):**

| Компонент | Путь |
|-----------|------|
| APIService crash methods | `Core/Network/APIService.swift` ~2369+, ~4516+ (`setupCrashDetection`, `start/stop`, `sendCrashDetectionData`, `getCrashDetectionHistory`, …) |
| AppConfig endpoints | `Core/Config/AppConfig.swift` — `/api/crash-detection/*` |
| Settings modal | `Shared/Components/Modals/CrashDetectionSettingsModal.swift` |
| Alert modal | `Shared/Components/Modals/CrashDetectionAlertModal.swift` |
| Manager | `Core/Managers/CrashDetectionManager.swift` |

**Проблема сейчас:**

1. ~~**`CrashDetectionSettingsModal` закомментирован**~~ — **исправлено v1.4:** файл уже в pbxproj; sheet + `hasSettings` включены.
2. **`saveSettings()`** сохраняет только в `ComponentConfigurationService` локально — **не вызывает** `APIService.updateCrashDetectionSettings` / `startCrashDetectionMonitoring`.
3. Hardcoded RU strings в toast: `"Настройки сохранены"` — нарушение LOC gate.

**Как делать (пошагово):**

1. **Разкомментировать sheet** в `03_NetworkProtectionScreen.swift` для `CrashDetectionSettingsModal`. Если compile error — добавить файл в `ALADDIN.xcodeproj/project.pbxproj` с полным путём `Shared/Components/Modals/CrashDetectionSettingsModal.swift`.
2. В `CrashDetectionSettingsModal.saveSettings()`:
   - Вызвать `APIService.updateCrashDetectionSettings(userId:sensitivity:geofenceRadius:)` (async overload есть).
   - При успехе — `startCrashDetectionMonitoring()` или делегировать `CrashDetectionManager`.
   - Ошибки API → `ToastManager` + **не** fallback mock success.
3. В `CrashDetectionManager` — убедиться, что pipeline CoreMotion → `sendCrashDetectionData` → при детекте `sendCrashAlert` / `reportCrash`.
4. **em-01 backend:** проверить на VPS, что `/api/crash-detection/start|stop|history` отвечают с JWT (не mock envelope). При 404 — router уже в backend, smoke через curl.
5. **em-03:** code review + optional unit test на mapping sensitivity → API payload (run deferred).
6. Локализация: toast keys `crash_settings_save_success` / `crash_settings_save_error` + `crash_sensitivity_*_label/desc` для `SensitivityOptionRow` в RU+EN.
7. **Permissions:** `Info.plist` — `NSMotionUsageDescription` + `UIBackgroundModes` (code review до PASS).
8. **Backend smoke:** `docs/server/test_emergency_prod_smoke.py` на VPS.

**Критерий PASS B7-01:** settings modal открывается из Network Protection; save идёт на prod API; grep `emptyParentalMonitoringDetailPayload`-style mock для crash → 0; MASTER `em-01…03` ✅.

### 13.2 B7-02 — Roadside assistance (em-04…em-05)

**Зачем:** UI вызова эвакуатора/помощи на дороге с real API (`roadside_assistance_agent`).

**Что уже есть:**

| Компонент | Путь |
|-----------|------|
| View (готов, API wired) | `Screens/RoadsideAssistanceView.swift` — `callRoadsideAssistance`, `cancelRoadsideAssistance`, `getRoadsideAssistanceHistory` |
| APIService | `APIService.swift` ~5395+ |
| AppConfig | `roadsideCall`, `roadsideStatus`, `roadsideCancel`, `roadsideHistory` |
| Localization | keys `roadside_*` уже в `LocalizationManager.swift` |

**Проблема сейчас:** **`RoadsideAssistanceView` нигде не подключён** (grep `.sheet` / navigation → 0). Пользователь не может открыть экран.

**Как делать:**

1. **Точка входа (зафиксировано):** `03_NetworkProtectionScreen.swift` Emergency section — `SecurityFeatureRow(hasSettings: true, onSettingsTap: { showRoadsideAssistance = true })` + `.sheet { RoadsideAssistanceView() }`.
2. Убедиться, что `RoadsideAssistanceView.swift` в **pbxproj** (полный путь `Screens/RoadsideAssistanceView.swift`).
3. **Polling статуса:** после `callHelp` success — optional timer `getRoadsideAssistanceStatus(requestId:)` до terminal status (enhancement, не блокер если call/cancel/history work).
4. **em-04 backend smoke:** POST `/api/roadside/call` (path из AppConfig) с JWT → не mock envelope.
5. Ошибки сети — показать user-facing localized error, **не** fake activeRequest.

**Критерий PASS B7-02:** пользователь открывает Roadside из app; call + cancel + history работают против prod; MASTER `em-04…05` ✅.

### 13.3 B7-03 — Elderly interface без mock (eld-01…eld-04)

**Зачем:** экран `09_ElderlyInterfaceScreen` — Family+ wellness для пожилых; mock календаря/давления недопустим в prod.

**Проблема сейчас:** `getPressureForDay()` (~2888–2899) возвращает **hardcoded mockData** по дням недели.

**Как делать:**

0. **B7-03-pre (обязательно до wire):** grep `app/routers/` + AppConfig — добавить `/api/elderly/blood-pressure/sync|update` если нет (v1.4: `elderly_interface_sync_router.py` + `AppConfig.elderlyBloodPressure*`).
1. **eld-01:** удалить `mockData` dict; `BloodPressureReading.empty`; sync via `syncBloodPressure` + `weeklyPressureByDay` cache.
2. **eld-02:** wire medications + appointments — найти TODO в `09_ElderlyInterfaceScreen.swift` и подключить реальные endpoints (если API нет — backend уже имеет family/elderly routes, проверить `app/routers/`).
3. **eld-03:** voice session — **⏸ deferred post-L3**; критерий: «UI stub removed, wellness endpoint documented» (не блокер GATE-J).
4. Empty state при отсутствии данных — localized placeholder, **не** fake 120/80.
5. Локализация elderly keys — проверить RU/EN parity (часть keys уже есть `elderly_*`).

**Критерий PASS B7-03:** `rg mockData Screens/09_ElderlyInterfaceScreen.swift` → 0; calendar/pressure from API or empty; MASTER `eld-01…04` ✅.

### 13.4 B7-04 — VPN regression (R6-G5)

**Зачем:** VPN/Network Protection уже сильный домен — **не ломать** при B7 changes; только regression smoke.

**Правило из плана:** `docs/SECURITY_100_PERCENT_MASTER_PLAN.md` — «VPN не трогать — regression only».

**Как делать:**

1. **iOS code review:** после B7-01 изменений в `03_NetworkProtectionScreen.swift` — VPN toggle, connect/disconnect, server list **не затронуты**.
2. **Backend smoke (VPS):**
   ```bash
   ssh -i ~/.ssh/aladdin_server root@149.154.65.180
   bash /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_prod_smoke.sh
   # ожидаем: 10/10 PASS
   ```
3. **iOS grep:** `rg 'mock|fallback|stub' Screens/03_NetworkProtectionScreen.swift Core/VPN` — новых mock bypass нет.
4. Записать evidence в `security-l3-report.json` EXTRAS block.

**Критерий PASS B7-04:** vpn_prod_smoke 10/10; iOS VPN flows unchanged; R6-G5 ✅.

### 13.5 После BATCH 7 — обязательные действия ML

1. ✅ в `.cursor/IMPLEMENTATION_BATCHES_TODO.md` B7-01…04
2. ✅ в `.cursor/SECURITY_138_MASTER_TODO.md` § EM, § ELD
3. **B-LOC-07** — все новые B7 strings RU+EN в `LocalizationManager.swift`; обновить `docs/LOCALIZATION_BATCH_GATE.md`
4. `security-l3-report.json`: `EXTRAS` → `status: pass`, `batch_progress.total_batches_done` → **111/143**
5. **Build check:**
   ```bash
   cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
   xcodebuild -scheme ALADDIN \
     -destination 'platform=iOS Simulator,id=82789999-A1C3-4B10-A2B9-CFE6BBB24ECF' \
     build
   ```
6. **Не** Archive / TestFlight — только BUILD SUCCEEDED.

### 13.6 BATCH COPY → QA (после B7)

| Batch | ID | Что делать |
|-------|-----|------------|
| COPY | B-COPY-01 | Audit onboarding vs L3 map — **без правок UI** |
| COPY | B-COPY-02 | FAQ только L3-ready features |
| COPY | B-COPY-03 | Tariffs ↔ Hub map |
| COPY | B-COPY-04 | App Store review notes |
| QA | B-QA-01 | EXTENDED_138 L3 criterion |
| QA | B-QA-02 | **138/138 TestFlight — ЕДИНСТВЕННАЯ точка Archive** |
| QA | B-QA-03 | grep zero mock 24h |
| QA | B-QA-04 | merge SECURITY_UNIFIED_IMPLEMENTATION.md |
| QA | B-QA-05 | prod registry ≥1074 weekly smoke |
| QA | B-QA-06 | LOC regression all 143 items |

### 13.7 Паттерны — переиспользовать из B4/B5/B6

| Паттерн | Пример |
|---------|--------|
| Mock rejection | `validateForProduction()` + `SecurityVerdictValidationError` |
| Threat catalog + coverage | `FamilyChildThreatCatalog` → для fam-* если нужно |
| Reports export | `ParentalMonitoringReportExporter` |
| Hub + tabs | DeviceHub / IdentityHub структура |
| pbxproj paths | всегда folder-qualified paths |
| LOC | `localizationManager.localized("key")`, grep `Text("[А-Яа-я]` → 0 |

### 13.8 Deploy checklist (если backend правки для em-*)

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180
BACKEND=/opt/aladdin-backend
systemctl restart aladdin-backend.service
$BACKEND/venv/bin/python3 $BACKEND/docs/server/test_security_prod_smoke.py
bash $BACKEND/docs/server/sfm_truth_check.sh
```

---

### 13.9 Risk matrix + P1 tasks (v1.4)

| Риск | Митигация | Task ID |
|------|-----------|---------|
| B7-03 нет BP API | B7-03-pre router | `B7-03-pre` |
| B7-01 ломает VPN | Emergency-only diff + B7-04a/b | `B7-04` |
| ML PASS без VPS | `test_emergency_prod_smoke.py` | `B7-EM-SMOKE` |
| MASTER drift | SYNC после ✅ | `SYNC-06` |
| Unit fail B-QA-02 | targeted test run | `B7-UT-01` |
| MockAPIService in prod | grep audit | `B7-AUDIT-01` |

**P1 до GATE-FINAL:** `B-OPS-22` timer · `B-COPY-01a` FamilyScreen ~8958 hardcoded RU audit.

---

*Handoff v1.4 · 2026-06-11 · BATCH 7 🔄 GATE-J · 111/143 · Pending: B7-04 VPS smoke*
