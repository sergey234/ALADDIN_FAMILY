# ALADDIN Security — мастер-индекс всех документов и задач

**Обновлено:** 2026-06-13 (v1.8 — **137/143** · **build 232** · **6 осталось** = R-07 Archive)  
**SSOT:** `docs/release/MASTER_STATUS_INDEX.md` ← **единая точка входа**  
**Старт реализации:** SFM-WIRE → B1 → Hubs B2–B6 → B7 → SEC-P2 → **R-19** → **R-08…10** → build **232** → QA  
**Онбординг:** R-19 COPY-POST-L3 ✅ (marketing sync)  
**Финальный аудит:** `docs/release/PLAN_FACT_AUDIT_143_2026-06-13.md`

---

## Быстрый старт (что читать)

| Порядок | Документ | Зачем |
|---------|----------|-------|
| 0 | **`docs/release/MASTER_STATUS_INDEX.md`** | **Единый SSOT — начинать здесь** |
| 0b | **`ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md`** | **Передать следующей ML-системе** |
| 1 | **Этот файл** | Карта всего |
| 2 | `.cursor/IMPLEMENTATION_BATCHES_TODO.md` | **Главный todo по батчам (137/143)** |
| 2b | `docs/release/PLAN_FACT_AUDIT_143_2026-06-13.md` | **План–факт + build 232** |
| 3 | `docs/OPS_ANTI_REGRESSION_GATES.md` | Чтобы не слетало + честные ML-проверки |
| 4 | `docs/SECURITY_UNIFIED_100_PERCENT_PLAN.md` | Продуктовый план 100% |
| 5 | `docs/SFM_SERVER_FORENSIC_REPORT.md` | Что на VPS с SFM |

---

## Все документы

### A. Cursor Todo (исполнение)

| Файл | Задач | Содержание |
|------|-------|------------|
| **`.cursor/IMPLEMENTATION_BATCHES_TODO.md`** | **143** | **Главный батч-план:** SFM-WIRE, 0–7, COPY, QA, OPS, R-19, R-08…10 (**137/143 ✅**) |
| `.cursor/SECURITY_138_MASTER_TODO.md` | 226 | Реестр по доменам: SEC, SFM, AF, DW, ID, CAT… |
| `.cursor/ANTIFAKE_PRODUCTION_TODO.md` | 72 | Детально anti-fake: af-0-01…af-12-04 |
| `.cursor/SECURITY_100_PERCENT_ROADMAP_TODO.md` | 53 gates | Фазы 0–8, R0-G1…R8-G4 |
| `.cursor/STORM_MESH_TODO.md` | 64 | UI Storm Mesh (отдельно от security) |
| `.cursor/BATCH_UX_FIX_TODO.md` | — | UX фиксы |

### B. Техспеки и анализ

| Файл | Роль |
|------|------|
| `docs/SECURITY_UNIFIED_100_PERCENT_PLAN.md` | Единый план: 9 категорий, проблемы→решения |
| `docs/SECURITY_100_PERCENT_MASTER_PLAN.md` | L1/L2/L3 framework, 5 Hub'ов |
| `docs/SECURITY_138_GAP_ANALYSIS.md` | Почему 138 ok ≠ приложение |
| `docs/ANTIFAKE_PRODUCTION_PLAN.md` | Техспек antifake API + workers |
| `docs/SFM_SERVER_FORENSIC_REPORT.md` | Форензика VPS SFM |
| **`docs/SFM_SINGLE_SOURCE_OF_TRUTH.md`** | **Единая правда SFM для всех ML** |
| **`docs/SFM_ML_QUICKSTART.md`** | Первая команда (30 сек) |
| `docs/server/sfm_truth_check.sh` | Скрипт проверки на VPS |
| **`docs/SEC06_LEGACY_ROUTER_AUDIT.md`** | Legacy vs explicit (SEC-06) |
| **`docs/IOS_EXPLICIT_API_MATRIX.md`** | iOS AppConfig ↔ B1 explicit paths |
| **`docs/server/test_security_prod_smoke.py`** | GATE-D orchestrator B1-12 |
| `docs/OPS_ANTI_REGRESSION_GATES.md` | **Анти-регрессия + ML contract** |
| `docs/SFM_CENTRAL_ARCHITECTURE.md` | Архитектура SFM |
| `docs/SFM_CENTRAL_ARCHITECTURE_COMPLETE.md` | Расширенная архитектура |
| `docs/SFM_MIGRATION_PLAN.md` | Миграция SFM |
| `docs/SECURITY_COMPONENTS_MIGRATION_ANALYSIS.md` | Components migration |

### C. ML / prod / audit

| Файл | Роль |
|------|------|
| **`docs/release/MASTER_STATUS_INDEX.md`** | **Единый SSOT build 232** |
| **`docs/release/PLAN_FACT_AUDIT_143_2026-06-13.md`** | **Финальный план–факт + build 232** |
| `docs/release/PLAN_FACT_AUDIT_143_2026-06-11.md` | Архив (2026-06-11) |
| `docs/release/COPY_POST_L3_PROGRESS.md` | R-19 + счёт 137/143 |
| `docs/release/QA_HUB_DEMO_R08_R10.md` | Hub demo R-08…10 |
| `docs/release/gates/hub-demo-smoke-report.json` | VPS hub smokes evidence |
| `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` | Подключение ML к prod + HARD RULE mock |
| `docs/audit/EXTENDED_138_CHECKLIST.md` | 138 checklist (переписать на L3) |
| **`docs/release/gates/security-l3-report.json`** | **Evidence gates (обновлять каждый batch)** |
| `docs/release/gates/ios-functional-138-report.json` | Runner (нужен fail on mock) |

---

## Все задачи по ID (сводка)

### SFM-WIRE (подключить текущий SFM, не откат)

| ID | Задача |
|----|--------|
| `B-SFM-W01` | Backup registry before any change |
| `B-SFM-W02` | Fix reactive symlink |
| `B-SFM-W03` | `start_sfm_core_http.py` PYTHONPATH + import |
| `B-SFM-W04` | systemd Environment PYTHONPATH |
| `B-SFM-W05` | Rename root stub safe_function_manager.py |
| `B-SFM-W06` | Rebuild registry from `register_*_in_sfm.py` |
| `B-SFM-W07` | Remove OptimizedSFM from prod hot path |
| `B-SFM-W08` | Smoke: sfm_loaded + execute real agent |
| `B-SFM-W09` | Wire `enable` → activate_agents_for_category |
| `B-SFM-W10` | Merge mapping from `complete_api_sfm_mapping.py` |

*(в IMPLEMENTATION_BATCHES пока как B-SFM-R01…R10 — переименовать при старте)*

### OPS — анти-регрессия (12)

`B-OPS-01` … `B-OPS-12` — см. `docs/OPS_ANTI_REGRESSION_GATES.md`

### BATCH 0 — SEC-INFRA (8)

`B0-01`…`B0-08` = `sec-01`…`sec-10`, `sync-01`, `R0-G*`

### ANTIFAKE — 72 задачи (af-*)

| Batch | Задач | IDs |
|-------|-------|-----|
| AF-0 Prod safety | 8 | `af-0-01`…`af-0-08` |
| AF-1 Agents/deps | 9 | `af-1-01`…`af-1-09` |
| AF-2 API routers | 10 | `af-2-01`…`af-2-10` |
| AF-3 Workers | 7 | `af-3-01`…`af-3-07` |
| AF-4 Calls | 8 | `af-4-01`…`af-4-08` |
| AF-5 iOS sync | 6 | `af-5-01`…`af-5-06` |
| AF-6 Hub UI | 10 | `af-6-01`…`af-6-10` |
| AF-7 Share/AI | 5 | `af-7-01`…`af-7-05` |
| AF-8 Copy | 6 | `af-8-01`…`af-8-06` |
| AF-9 8 threats | 8 | `af-9-01`…`af-9-08` |
| AF-10 Deploy | 5 | `af-10-01`…`af-10-05` |
| AF-11 QA | 6 | `af-11-01`…`af-11-06` |
| AF-12 Ops | 4 | `af-12-01`…`af-12-04` |

**Antifake L3 покрытие:** текст/URL · аудио · видео · документ · звонок · 8 угроз matrix

### SECURITY_138_MASTER — домены

| § | Prefix | Задач |
|---|--------|-------|
| SEC | `sec-01`…`sec-10` | 10 |
| SFM | `sfm-01`…`sfm-12` | 12 |
| AF | → ANTIFAKE file | 72 |
| DW | `dw-01`…`dw-08` | 8 |
| ID | `id-01`…`id-08` | 8 |
| DC | `dc-01`…`dc-06` | 6 |
| LOC | `loc-01`…`loc-06` | 6 |
| AV | `av-01`…`av-08` | 8 |
| COMP | `comp-01`…`comp-10` | 10 |
| IOT | `iot-01`…`iot-07` | 7 |
| MOB | `mob-01`…`mob-06` | 6 |
| PC-MON | `pc-01`…`pc-06` | 6 |
| EM | `em-01`…`em-06` | 6 |
| ELD | `eld-01`…`eld-04` | 4 |
| SYNC | `sync-01`…`sync-05` | 5 |
| COPY | `copy-01-audit`, `copy-02`…`copy-05` | 6 |
| CAT | `cyb/frd/chd/dlk/dfk/net/mob/fam/iot-*` | 58 |

### ROADMAP gates — фазы 0–8

| Фаза | Gates | Фокус |
|------|-------|-------|
| 0 | `R0-G1`…`R0-G12` | SEC-INFRA + SFM |
| 1 | `R1-G1`…`R1-G10` | Antifake Hub |
| 2 | `R2-G1`…`R2-G8` | Privacy Hub |
| 3 | `R3-G1`…`R3-G6` | Identity Hub |
| 4 | `R4-G1`…`R4-G9` | Device Hub |
| 5 | `R5-G1`…`R5-G5` | Family polish |
| 6 | `R6-G1`…`R6-G5` | Extras |
| 7 | `R7-G1`…`R7-G5` | COPY (не онбординг) |
| 8 | `R8-G1`…`R8-G4` | 138 L3 QA |

### IMPLEMENTATION BATCHES 1–7 (кратко)

| Batch | Задач | Покрытие |
|-------|-------|----------|
| B1 API wiring | 12 | SFM→FastAPI все домены |
| B2 Antifake iOS | 10 | Hub UI |
| B3 Privacy | 8 | DW+cleanup+location |
| B4 Identity | 6 | fraud |
| B5 Device | 9 | cyber+mobile+iot |
| B6 Family | 5 | parental gaps | ✅ 5/5 GATE-I |
| B7 Extras | 4 | crash/roadside/elderly | ⬜ **NEXT** |
| B-COPY | 4 | FAQ/tariffs |
| B-QA | 5 | 138 sign-off |

---

## Итоговый счёт задач (уникальные ID)

| Категория | Кол-во |
|-----------|--------|
| SFM-WIRE | 10 |
| OPS anti-regression | 12 |
| SEC-INFRA B0 | 8 |
| Antifake af-* | 72 |
| Master (без дублей af) | ~154 |
| CAT per-threat | 58 |
| Roadmap gates | 53 |
| Implementation batches (деталь) | ~58 |
| **Ориентир всего** | **~280** (с перекрытием gate↔master) |

**Правило дублей:** закрыл `af-X` → ✅ в ANTIFAKE + SECURITY_138 § AF. Закрыл `B0-01` → ✅ sec-01 + af-0-01.

---

## Порядок реализации до 100%

```
1. SFM-WIRE + B-OPS-01…06     ← ✅
2. BATCH 0 SEC-INFRA          ← ✅
3. BATCH 1 + AF-1…3           ← ✅ backend
4. BATCH 2 + AF-5…6           ← 🔄 11/12 (TestFlight → B-QA-02)
5. BATCH 3…6                  ← ✅ Privacy/Identity/Device/Family
6. BATCH 7                    ← **СЕЙЧАС** Extras (см. ML handoff §13)
7. B-OPS-07…12                ← ML contract + monitoring
8. BATCH COPY + QA            ← 138 L3 sign-off → Xcode Archive
```

---

## Что в итоге получается

| Компонент | 100% = |
|-----------|--------|
| SFM | loaded, registry ≥1000, execute real, health honest |
| Antifake | text/url sync + audio/video/doc jobs + Hub UI + 8 threats |
| 9 categories | L2 persist + L3 Hub action |
| 138 functions | L1+L2+L3 TestFlight each |
| ML checks | только L3 contract, не HTTP 200 |
| Deploy | preflight + post-smoke + no mock scripts |
| Онбординг | без изменений до COPY |

---

## Синхронизация статусов

При закрытии задачи обновлять:

1. `.cursor/IMPLEMENTATION_BATCHES_TODO.md`
2. Доменный файл (ANTIFAKE / MASTER)
3. `docs/release/gates/security-l3-report.json` (после B-OPS-10)
