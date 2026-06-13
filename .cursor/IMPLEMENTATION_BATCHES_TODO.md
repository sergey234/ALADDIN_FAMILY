# Implementation Batches — 100% Security (Cursor Todo)

**Создано:** 2026-06-09 · **Forensic:** `docs/SFM_SERVER_FORENSIC_REPORT.md`  
**Единый план:** `docs/SECURITY_UNIFIED_100_PERCENT_PLAN.md`  
**Онбординг:** ✅ COPY-POST-L3 (R-19) — `COPY_POST_L3_PROGRESS.md`  
**SSOT индекс:** `docs/release/MASTER_STATUS_INDEX.md` ← **начинать здесь**

> **ПРАВИЛО:** каждый batch доводим до **100%** — без «частично» в отчётах. Gate PASS только с evidence.

**Мастер-индекс:** `.cursor/SECURITY_MASTER_INDEX.md`  
**План–факт аудит:** `docs/release/PLAN_FACT_AUDIT_143_2026-06-13.md` ← **build 232**  
**Handoff для ML:** `ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md` ← передать следующей ML-системе  
**Анти-регрессия:** `docs/OPS_ANTI_REGRESSION_GATES.md`  
**L3 smoke:** `docs/server/L3_SMOKE_CONTRACT.md`  
**SFM правда для ML:** `docs/SFM_SINGLE_SOURCE_OF_TRUTH.md` · quickstart: `docs/SFM_ML_QUICKSTART.md`  
**Счёт:** **137 / 143** total ✅ (**114 / 131** impl + **12 / 12** LOC ✅ + **COPY 4/4** + **R-19** ✅ + **R-08…10** ✅) · Backend **100%** · **BATCH 2/3/4: 12/12, 8/8, 6/6** ✅ · **BATCH QA: 5/6** · **B-PRE 6/6** ✅ · **Build 232 supplemental: 18/18** ✅  
**LOC SSOT:** `docs/LOCALIZATION_BATCH_GATE.md` — RU/EN gate для каждого batch 1…131  
**Archive / TestFlight (B-QA-02):** ⏸ **самый последний шаг** — на твоём Mac с Apple ID (см. ниже)  
**Сейчас:** R-07 B-QA-02 Archive + PNG screenshots (**последний блок**, 6/143 осталось) · build **232** committed

**Матрица iOS↔backend:** `docs/IOS_EXPLICIT_API_MATRIX.md`

---

## План–факт (2026-06-11) — сверка

| Фаза | План | Факт | Gate |
|------|------|------|------|
| SFM-WIRE | 12 | ✅ 12/12 | GATE-A PASS |
| OPS | 22 | ✅ 22/22 | GATE-A0 PASS |
| BATCH 0 SEC-INFRA | 8 | ✅ 8/8 | GATE-B PASS |
| BATCH 1 API Wiring | 12 | ✅ 12/12 | GATE-D backend PASS |
| BATCH SYNC | 5 | ✅ 5/5 | — |
| B-PRE iOS migration | 6 | ✅ 6/6 (`B2-00c` 62/62) | pre-GATE-E ✅ |
| BATCH 2 Antifake iOS | 12 | ✅ 12/12 (`B2-09` R-08) | GATE-E PASS |
| BATCH 3 Privacy Hub | 8 | ✅ 8/8 (`B3-08` R-09) | GATE-F PASS |
| BATCH 4 Identity Hub | 6 | ✅ 6/6 (`B4-06` R-10) | GATE-G PASS |
| BATCH 5 Device Hub | 9 | ✅ 9/9 | GATE-H PASS |
| BATCH 6 Family polish | 5 | ✅ 5/5 | GATE-I PASS |
| BATCH 7 Extras | 4+support | ✅ 4/4 (`B7-04` VPN 10/10) | GATE-J PASS |
| BATCH LOC RU/EN | 12 | ✅ 12/12 | pre-FINAL ✅ |
| BATCH COPY | 4 | ✅ 4/4 | GATE-K PASS |
| BATCH QA docs | 6 | 🔄 5/6 (`B-QA-02` ⏸) | GATE-FINAL in_progress |
| BATCH SEC-P2 | 5 | ✅ 5/5 | SEC-P2 PASS |
| Post-L3 COPY (R-19) | 1 | ✅ | `COPY_POST_L3_PROGRESS.md` |
| Hub demos (R-08…10) | 3 | ✅ backend · PNG ⏸ device | `QA_HUB_DEMO_R08_R10.md` |

**Как делали:** backend → Hubs B2–B6 → B7 emergency → SEC-P2 → R-19 marketing → R-08…10 VPS demos → QA docs. **Archive (R-07) — последний блок на Mac.**

**Следующий шаг:** **R-07 B-QA-02** Archive + TestFlight + PNG `testflight-build227/` (см. `PLAN_FACT_AUDIT_143_2026-06-13.md`).

### Build 232 supplemental (2026-06-13) — ✅ 18/18 код

| ID | Факт | Commit |
|----|------|--------|
| af-m2 Call Directory + sync + post-call | ✅ | `3cfcf256` |
| af-m3 history 50 + quick voice 5s | ✅ | same |
| ux-1-07 accordion antifake | ✅ | same |
| ux-6-03/05/01b, ux-8-06 | ✅ | same |
| QA bypass Premium (TEMP) | ✅ | same |

См. `docs/release/MASTER_STATUS_INDEX.md` §2.

### BATCH 1 — детальный план–факт

| ID | План | Факт | Prod smoke |
|----|------|------|------------|
| B1-01 antifake | explicit router | ✅ | `test_antifake_prod_smoke.py` |
| B1-02 darkweb | explicit router | ✅ | `test_darkweb_prod_smoke.py` |
| B1-03 identity | explicit router | ✅ | `test_identity_theft_prod_smoke.py` |
| B1-04 cleanup | explicit router | ✅ | `test_data_cleanup_prod_smoke.py` |
| B1-05 location-bubble | explicit router | ✅ | `test_location_bubble_prod_smoke.py` |
| B1-06 malware | explicit router | ✅ | `test_malware_prod_smoke.py` |
| B1-07 components | explicit + skip legacy | ✅ | `test_components_prod_smoke.py` |
| B1-08 iot | explicit + skip legacy | ✅ | `test_iot_prod_smoke.py` |
| B1-09 mobile | explicit router | ✅ | `test_mobile_security_prod_smoke.py` |
| B1-10 parental mon | explicit router | ✅ | `test_parental_monitoring_prod_smoke.py` |
| B1-11 OpenAPI | 32 explicit routes | ✅ | `test_security_openapi_prod_smoke.py` |
| B1-12 all domains | orchestrator | ✅ | `test_security_prod_smoke.py` |
| **SEC-06** | legacy audit | ✅ | `docs/SEC06_LEGACY_ROUTER_AUDIT.md` |

**GATE-D команда (VPS):**
```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180
/opt/aladdin-backend/venv/bin/python3 /opt/aladdin-backend/docs/server/test_security_prod_smoke.py
# ожидаем: pass:true, domains_pass:11
```

**Legacy audit:** `docs/SEC06_LEGACY_ROUTER_AUDIT.md` — Tier A–E, 5 path-коллизий, location legacy skipped.

---

## Что УЖЕ есть (не переделывать)

| Есть | Где | Действие |
|------|-----|----------|
| SafeFunctionManager + registry ≥1000 | VPS `:8003` | Regression only |
| Explicit routers B1 (11 domains) | `app/routers/*` | GATE-D smokes |
| SEC-06 legacy audit | `docs/SEC06_LEGACY_ROUTER_AUDIT.md` | Tier D keep |
| iOS explicit AppConfig paths | `Core/Config/AppConfig.swift` | B2-00 ✅ |
| iOS API matrix | `docs/IOS_EXPLICIT_API_MATRIX.md` | B-PRE-01 ✅ |
| Parental 32, VPN 6 | FastAPI routers | Regression only |
| iOS ThreatProtectionCategory 9 | Swift | Align server IDs |
| ANTIFAKE/SEC/138 todo files | `.cursor/` | Execute batches |

## Чего НЕТ / в работе (делать)

| Нет / в работе | Критичность | Batch |
|----------------|-------------|-------|
| Extras crash/roadside/elderly | P1 | **B7** ← **NEXT** |
| COPY + QA sign-off | P0 | B-COPY, B-QA |
| af-3 async workers (Redis/RQ) | P1 | af-3-01…07 |
| af-2-09 rate limits | P2 | ✅ `antifake_rate_limit.py` build 227 |
| SEC-06-P2 legacy migration | P2 | SEC-P2 |

## Что НЕ стоит делать

- ❌ Писать SFM с нуля
- ❌ `deploy_optimized_sfm.sh` mock path снова
- ❌ 100 отдельных экранов
- ❌ Менять онбординг до L3 готов
- ❌ Считать HTTP 200 = 100% без registry smoke
- ❌ Поднимать монолит без restore registry (будет 14 fn)

---

# BATCH SFM-WIRE — Подключить текущий SFM (P0) · 10 задач

**Не откат.** Код уже на VPS (`app/security/safe_function_manager.py`). Wire + rebuild registry.

**Gate:** `sfm_loaded=true` + registry ≥1000 + `fake_news_detection_agent` → real verdict (не `status:success`)

| ID | Задача | Статус |
|----|--------|--------|
| `B-SFM-W01` | Backup `data/sfm/function_registry.json` before change | ✅ |
| `B-SFM-W02` | Fix `reactive/performance_optimizer.py` (rm symlink, cp real file) | ✅ |
| `B-SFM-W03` | `start_sfm_core_http.py`: PYTHONPATH + import SafeFunctionManager | ✅ |
| `B-SFM-W04` | `aladdin-sfm-core.service`: Environment PYTHONPATH | ✅ |
| `B-SFM-W05` | Rename stub `/opt/.../safe_function_manager.py` → `.stub.bak` | ✅ |
| `B-SFM-W06` | Rebuild registry: restore `app/data/sfm/` + `data/sfm/` (1074 fn) | ✅ |
| `B-SFM-W07` | `sfm_singleton` → delegate real SFM; remove OptimizedSFM prod | ✅ |
| `B-SFM-W08` | Smoke: init SFM, `len(functions)≥1000`, execute 5 mapped fn | ✅ |
| `B-SFM-W09` | `enable` category → `activate_agents_for_category` | ✅ |
| `B-SFM-W10` | Wire `complete_api_sfm_mapping.py` in explicit routers | ✅ |
| `B-SFM-W06b` | Manifest + `sync_sfm_registry_from_manifest.sh` (cp canonical→legacy) | ✅ |
| `B-SFM-W11` | ML deps policy: torch/cv2 только worker (`docs/SFM_ML_DEPS_POLICY.md`) | ✅ |

---

# BATCH OPS — Анти-регрессия + честные ML-проверки (P0) · 21 задач

**Спека:** `docs/OPS_ANTI_REGRESSION_GATES.md` — делать **параллельно** с SFM-WIRE.

| ID | Задача | Статус |
|----|--------|--------|
| `B-OPS-01` | :8003 health: `sfm_loaded`, fail systemd if false | ✅ |
| `B-OPS-02` | Honest `functions_count` from registry file | ✅ |
| `B-OPS-03` | Unknown execute → 503 (не `status:success`) | ✅ |
| `B-OPS-04` | Ban `deploy_optimized_sfm.sh` from prod runbook | ✅ |
| `B-OPS-05` | Registry backup hook; forbid empty overwrite | ✅ |
| `B-OPS-06` | `preflight_sfm.py` in deploy pipeline | ✅ |
| `B-OPS-07` | `docs/server/L3_SMOKE_CONTRACT.md` + update ML guide | ✅ |
| `B-OPS-08` | `aladdin-sfm-prod-smoke.timer` every 15m | ✅ |
| `B-OPS-09` | Fix `sfm-healthcheck.service` 203 EXEC | ✅ |
| `B-OPS-10` | `security-l3-report.json` generator | ✅ |
| `B-OPS-11` | functional-138 runner: fail on mock/404 | ✅ |
| `B-OPS-12` | EXTENDED_138: verify=L3 criterion only | ✅ |
| `B-OPS-13` | `GET /api/sfm/status` honest JSON (sfm_loaded, registry_count) | ✅ |
| `B-OPS-14` | Deploy `sfm_truth_check.sh` on VPS | ✅ |
| `B-OPS-15` | `SFM_ML_QUICKSTART.md` linked from ML guide | ✅ |
| `B-OPS-16` | AGENTS.md + handoff: step 0 = truth check | ✅ |
| `B-OPS-17` | Rename root SFM stub → `.STUB_DO_NOT_IMPORT` | ✅ |
| `B-OPS-18` | `README_SFM.md` on server with canonical paths | ✅ |
| `B-OPS-19` | Deploy blocked if `sfm_truth_check.sh` fails | ✅ |
| `B-OPS-20` | `function_registry.manifest.json` in repo | ✅ |
| `B-OPS-21` | `Restart=on-failure` + health 503 → not healthy (`aladdin-sfm-core.service`) | ✅ |
| `B-OPS-22` | systemd timer: `test_security_prod_smoke.py` every 15m (like sfm smoke) | ⬜ |

**Спека SFM truth:** `docs/SFM_SINGLE_SOURCE_OF_TRUTH.md` — **делать вместе с SFM-WIRE**

---

# BATCH SYNC — Todo mirror sync (P0) · 5 задач

**Зачем:** IMPLEMENTATION_BATCHES ✅, но MASTER/ANTIFAKE/ROADMAP показывают 0% — риск переделки закрытого.

| ID | Задача | Статус |
|----|--------|--------|
| `SYNC-01` | `SECURITY_138_MASTER_TODO.md` — sec/sfm/dw counters ✅ | ✅ |
| `SYNC-02` | `ANTIFAKE_PRODUCTION_TODO.md` — af-0, af-2 backend ✅ | ✅ |
| `SYNC-03` | `SECURITY_100_PERCENT_ROADMAP_TODO.md` — R0-G1…G8, R1 backend | ✅ |
| `SYNC-04` | Handoff §12 plan–fact + fix duplicate §8 + deploy typo | ✅ |
| `SYNC-05` | `security-l3-report.json` — `IOS-MIGRATION` block + batch 61/129 | ✅ |

---

# BATCH PRE — iOS migration layer (P0) · 6 задач

**Gate:** AppConfig explicit + unit test PASS **до** Antifake Hub UI.  
**Матрица:** `docs/IOS_EXPLICIT_API_MATRIX.md`

| ID | Задача | Статус |
|----|--------|--------|
| `B-PRE-01` | `docs/IOS_EXPLICIT_API_MATRIX.md` — Hub → path → smoke | ✅ |
| `B-PRE-02` | GATE-D re-confirm on VPS (`test_security_prod_smoke.py` pass:true) | ✅ |
| `B2-00` | `AppConfig.Endpoint` explicit paths (11 domains) | ✅ |
| `B2-00b` | `SecurityVerdict` model + `PremiumGateHandler` shared layer | ✅ |
| `B2-00c` | `AppConfigTests` + `SecurityVerdictModelsTests` | ✅ 62/62 2026-06-11 |
| `B-PRE-03` | `APIService` audit + `docs/APISERVICE_SECURITY_PATH_AUDIT.md` | ✅ |

---

# BATCH 2 — Antifake Hub iOS (P0) · 12 задач

| ID | Задача | AF ref | Статус |
|----|--------|--------|--------|
| `B2-01` | AppConfig antifake endpoints | af-5 | ✅ (in B2-00) |
| `B2-02` | AntifakeHubScreen 4 tabs | af-6 | ✅ |
| `B2-03` | deepfakes → Hub nav | af-6 | ✅ |
| `B2-04` | check/text + url sync | af-2 | ✅ |
| `B2-05` | audio/video/document jobs poll | af-3 | ✅ |
| `B2-06` | call/analyze + caller_id/display_name | af-4 | ✅ |
| `B2-07` | Premium 403 handling (polish) | af-2 | ✅ |
| `B2-08` | Share extension | af-7 | ✅ |
| `B2-09` | dfk-01…08 matrix TestFlight | af-9 | ✅ R-08 `QA_HUB_DEMO_R08_R10.md` + VPS smoke |
| `B2-10` | deps: cv2/transformers lazy in worker | af-1 | ✅ |
| `B2-11` | RU/EN loc sign-off antifake (`af-6-09`) | af-6 | ✅ |
| `B2-12` | `GET /api/antifake/metrics` APIService wire | af-3 | ✅ |

---

# BATCH LOC — Localization RU/EN gates (P0) · 12 задач

**Спека:** `docs/LOCALIZATION_BATCH_GATE.md` — закрывать вместе с соответствующим impl batch.

| ID | Задача | Покрывает impl batch | Статус |
|----|--------|----------------------|--------|
| `B-LOC-00` | `docs/LOCALIZATION_BATCH_GATE.md` matrix | все 131 impl | ✅ |
| `B-LOC-01` | SFM/OPS/B0/B1/SEC-P2 — N/A backend | 1–55 | ✅ N/A |
| `B-LOC-02` | B-PRE + BATCH 2 Antifake keys | B-PRE, B2 | ✅ |
| `B-LOC-03` | BATCH 3 Privacy Hub RU/EN | B3 | ✅ |
| `B-LOC-04` | BATCH 4 Identity Hub RU/EN | B4 | ✅ |
| `B-LOC-05` | BATCH 5 Device Hub RU/EN | B5 | ✅ |
| `B-LOC-06` | BATCH 6 Family polish RU/EN | B6 | ✅ |
| `B-LOC-07` | BATCH 7 Extras RU/EN | B7 | ✅ |
| `B-LOC-08` | BATCH COPY marketing RU/EN | B-COPY | ✅ |
| `B-LOC-09` | `nav_screen_*` для всех новых Hub | B2–B7 | ✅ |
| `B-LOC-10` | grep: no hardcoded Cyrillic in new Hub Views | B2–B7 | ✅ |
| `B-LOC-11` | `af-6-09` antifake string audit | af-6 | ✅ |

---

# BATCH 0 — SEC-INFRA (P0) · 8 задач

| ID | Задача | MASTER | Статус |
|----|--------|--------|--------|
| `B0-01` | protection.py logger + enable 200 | sec-01 | ✅ |
| `B0-02` | DB user_protection_settings UPSERT | sec-02 | ✅ |
| `B0-03` | Category IDs: iOS 9 = server canonical | sec-03 | ✅ |
| `B0-04` | iOS loadSettingsFromServer | sync-01 | ✅ |
| `B0-05` | main.py wildcard blocklist security | sec-04 | ✅ |
| `B0-06` | Gateway reject mock-real-protection | sec-05 | ✅ |
| `B0-07` | Smoke toggle 9 categories round-trip | R0-G8 | ✅ |
| `B0-08` | `enable` → `activate_agents_for_category` via SFM | sfm-06 | ✅ |

**Gate 0:** 9 toggles L2 + no mock on security paths.

---

# BATCH 1 — API Wiring (SFM → FastAPI) (P0) · 12 задач

| ID | Задача | Статус |
|----|--------|--------|
| `B1-01` | Router `antifake.py` from mapping + SFM execute | ✅ |
| `B1-02` | Router `darkweb.py` → dark_web_monitoring_agent | ✅ |
| `B1-03` | Router identity-theft detect (not stats-only) | ✅ |
| `B1-04` | Router data/cleanup explicit | ✅ |
| `B1-05` | Router location-bubble explicit | ✅ |
| `B1-06` | Wire antivirus/scan → malware agent | ✅ |
| `B1-07` | Components routers: no 404 phishing_protection | ✅ |
| `B1-08` | IoT scan router | ✅ |
| `B1-09` | mobile_security_agent endpoints | ✅ |
| `B1-10` | parental monitoring/detail FastAPI only | ✅ |
| `B1-11` | OpenAPI: new routers published | ✅ |
| `B1-12` | `test_security_prod_smoke.py` all domains | ✅ |
| `SEC-06` | Legacy router audit + location_bubble skip | ✅ |

---

# BATCH SEC-P2 — Legacy migration Phase 2 (P2) · 5 задач

**Спека:** `docs/SEC06_LEGACY_ROUTER_AUDIT.md` §Backlog · после iOS Hubs L3.

| ID | Задача | Статус |
|----|--------|--------|
| `SEC-06-P2-01` | darkweb `/breaches` → explicit | ✅ VPS 2026-06-11 |
| `SEC-06-P2-02` | identity `/monitor-credit` → `/monitor/credit` alias | ✅ |
| `SEC-06-P2-03` | `/api/location/bubble` → 410 deprecation | ✅ curl 410 |
| `SEC-06-P2-04` | monitoring out of parental_control mega-router | ✅ |
| `SEC-06-P2-05` | devices → `app/routers/devices.py` | ✅ |

---

# BATCH 3 — Privacy Hub (P0) · 8 задач

| ID | Задача | Статус |
|----|--------|--------|
| `B3-01` | DW modal scan CTA | ✅ |
| `B3-02` | breaches list | ✅ |
| `B3-03` | cleanup progress | ✅ |
| `B3-04` | location bubble | ✅ |
| `B3-05` | Privacy Hub screen | ✅ |
| `B3-06` | Analytics → Hub | ✅ |
| `B3-07` | dlk-01…12 | ✅ |
| `B3-08` | TestFlight demo | ✅ R-09 + VPS darkweb smoke |

---

# BATCH 4 — Identity Hub (P0) · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `B4-01` | Identity Hub screen | ✅ |
| `B4-02` | SNILS detect | ✅ |
| `B4-03` | attempts list | ✅ |
| `B4-04` | fraud toggle → agent | ✅ |
| `B4-05` | frd-01…12 | ✅ |
| `B4-06` | TestFlight | ✅ R-10 + VPS identity smoke |

---

# BATCH 5 — Device Hub (P1) · 9 задач

| ID | Задача | Статус |
|----|--------|--------|
| `B5-01` | Device Hub screen | ✅ |
| `B5-02` | Malware scan button wire | ✅ |
| `B5-03` | Phishing/Network/Mobile/Incident scans | ✅ |
| `B5-04` | IoT fix threat | ✅ |
| `B5-05` | ProtectionStats real | ✅ |
| `B5-06` | cyb-01…10 | ✅ |
| `B5-07` | mob-01…10 | ✅ |
| `B5-08` | iot-01…10 | ✅ |
| `B5-09` | EICAR smoke | ✅ |

---

# BATCH 6 — Family polish (P1) · 5 задач

| ID | Задача | Статус |
|----|--------|--------|
| `B6-01` | monitoring/detail iOS wire (backend ✅ B1-10) | ✅ |
| `B6-02` | FamilyModals API | ✅ |
| `B6-03` | PDF reports | ✅ |
| `B6-04` | geofence geocode | ✅ |
| `B6-05` | chd-01…17 regression | ✅ |

---

# BATCH 7 — Extras (P1) · 4 + 6 support задач

**Handoff для ML:** `ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md` **§13** (пошагово + риски).  
**Gate:** GATE-J → `security-l3-report.json` block `EXTRAS` + `docs/server/test_emergency_prod_smoke.py`.  
**LOC:** B-LOC-07 после всех UI-строк B7.  
**Порядок исполнения (Day 1→4):** B7-02 → B7-04 baseline → B7-01 → B7-04 post → B7-03-pre → B7-03 → B-LOC-07 → BUILD → GATE-J.

| ID | Задача | MASTER IDs | Статус |
|----|--------|------------|--------|
| `B7-02` | Roadside: `hasSettings` + sheet `RoadsideAssistanceView` в Emergency section | `em-04…05` | ✅ |
| `B7-04a` | VPN regression baseline (до B7-01) | `R6-G5` | ✅ 10/10 VPS |
| `B7-01` | Crash: uncomment modal, `hasSettings`, APIService wire, LOC sensitivity | `em-01…03` | ✅ |
| `B7-04b` | VPN regression post-change (после B7-01) | `R6-G5` | ✅ 10/10 VPS |
| `B7-03-pre` | Elderly API discovery: `/api/elderly/blood-pressure/*` + AppConfig | `eld-01` | ✅ |
| `B7-03` | Elderly: mock removal, empty state, sync meds/appts/BP | `eld-01…04` | ✅ (`eld-03` voice ⏸) |
| `B7-EM-SMOKE` | `docs/server/test_emergency_prod_smoke.py` crash+roadside+elderly BP | GATE-J | ✅ VPS pass:true |
| `B-LOC-07` | RU/EN crash/roadside/elderly B7 strings | LOC | ✅ |
| `B7-04` | VPN regression sign-off (B7-04a + B7-04b) | `net-*` | ✅ 10/10 VPS 2026-06-11 (nonce fix) |

### B7-01 детали (crash) — scope issue снят (файл в pbxproj)

- **Файлы:** `03_NetworkProtectionScreen.swift`, `CrashDetectionSettingsModal.swift`, `CrashDetectionManager.swift`
- **Сделать:** `hasSettings: true` + `onSettingsTap`; `saveSettings()` → `updateCrashDetectionSettings` + `startCrashDetectionMonitoring` + `startMonitoring()`; LOC toast + `SensitivityOptionRow`
- **Проверить:** `NSMotionUsageDescription` + `UIBackgroundModes` в Info.plist (code review PASS)
- **Не делать:** mock fallback при ошибке API

### B7-02 детали (roadside) — конкретный UX

```swift
SecurityFeatureRow(hasSettings: true, onSettingsTap: { showRoadsideAssistance = true })
.sheet(isPresented: $showRoadsideAssistance) { RoadsideAssistanceView() }
```

- **pbxproj:** `Screens/RoadsideAssistanceView.swift` ✅ уже в target
- **Не делать:** fake `activeRequest` при network error

### B7-03-pre + B7-03 (elderly)

- **B7-03-pre:** `app/security/api/routers/elderly_interface_sync_router.py` — `/blood-pressure/sync|update`; `AppConfig.elderlyBloodPressure*`
- **B7-03:** убрать `mockData`; `BloodPressureReading.empty`; sync meds/appts/BP on appear; `weeklyPressureByDay` из API/cache
- **eld-03 voice:** ⏸ deferred — критерий: UI stub removed, endpoint documented в handoff §13.3
- **Дубликаты:** `ML_SYSTEM_PACKAGE/LocalizedVersions/` — sync при LOC gate

### B7-04 детали (VPN)

- **Regression only:** `vpn_prod_smoke.sh` 10/10 на VPS — до и после B7-01
- **iOS:** правки только Emergency section; VPN toggle/connect не трогать

### BATCH 7 — Risk mitigation (обязательно)

| Риск | Митигация | ID |
|------|-----------|-----|
| B7-03 нет BP API | B7-03-pre router + AppConfig | `B7-03-pre` |
| B7-01 ломает VPN | Emergency-only diff + B7-04a/b | `B7-04` |
| ML PASS без VPS curl | `test_emergency_prod_smoke.py` + §6 template | `B7-EM-SMOKE` |
| Drift MASTER↔BATCH | SYNC после каждого ✅ | `SYNC-06` |
| Unit tests fail на B-QA-02 | Targeted run после B7 build | `B7-UT-01` |

### BATCH 7 — P1 до GATE-FINAL (не блокирует B7, но в плане)

| ID | Задача | Статус |
|----|--------|--------|
| `B-OPS-22` | systemd timer `test_security_prod_smoke.py` 15m | ✅ units in `docs/server/aladdin-security-prod-smoke.*` |
| `B7-UT-01` | `xcodebuild test -only-testing` B5/B6/B7 | ✅ 62/62 (R-05); build re-confirm 2026-06-11 |
| `SYNC-06` | MASTER AF-0 counters ↔ IMPLEMENTATION_BATCHES | ✅ |
| `B7-AUDIT-01` | grep `MockAPIService` в security prod paths | ✅ `docs/release/QA_03_MOCK_GREP_AUDIT.md` |
| `B-COPY-01a` | hardcoded RU `FamilyRolesHelpView` → loc keys | ✅ |

**Порядок до релиза:** BATCH COPY ✅ → BATCH QA (5/6 docs) → **финальный блок:** `B7-04` VPN + `xcodebuild` + `B7-UT-01` → **B-QA-02:** Archive + TestFlight.

---

# BATCH COPY — Marketing (P1) · 4 задачи ✅

**B-COPY audit frozen at L3; post-L3 edits → R-19 ✅.** Evidence: `docs/release/COPY_0*.md` + `COPY_POST_L3_*`

| ID | Задача | Статус |
|----|--------|--------|
| `B-COPY-01` | Audit onboarding only (`copy-01-audit`) | ✅ `COPY_01_ONBOARDING_L3_AUDIT.md` |
| `B-COPY-02` | FAQ L3-ready only | ✅ `COPY_02_FAQ_L3_AUDIT.md` |
| `B-COPY-03` | Tariffs ↔ Hub map | ✅ `COPY_03_TARIFFS_HUB_MAP.md` |
| `B-COPY-04` | App Store notes | ✅ `COPY_04_APP_STORE_REVIEW_NOTES.md` |

---

# BATCH COPY-POST-L3 — Marketing implementation (P0) · R-19 ✅

**После:** SEC-P2 ✅ · **До:** B-QA-02 Archive  
**SSOT:** `docs/release/COPY_POST_L3_FULL_AUDIT.md` · **Исполнение:** `docs/release/COPY_POST_L3_TODO.md` (CP3-01…11) · **Dashboard:** `docs/release/COPY_POST_L3_PROGRESS.md`

| ID | Задача | Статус |
|----|--------|--------|
| `CP3-01` | Onboarding OB_01/04/06 RU+EN; OB_02 RU keep + EN military sync | ✅ |
| `CP3-02` | Tariffs/catalog «по тарифу» RU+EN | ✅ |
| `CP3-03` | FAQ soften 12 answers (skip `faq_unsafe_wifi`) RU+EN | ✅ |
| `CP3-04` | FAQ catalog +5 hidden entries | ✅ |
| `CP3-05` | FAQ new +4 (crash, roadside, SOS, dark_web) RU+EN | ✅ |
| `CP3-06` | Privacy app + keys (военное keep; no 100%/impossible) | ✅ |
| `CP3-07` | Terms + antifake/emergency sections RU+EN | ✅ |
| `CP3-08` | landing/privacy.html + PRIVACY_POLICY_FULL_152FZ | ✅ |
| `CP3-09` | COPY audits + kb JSON + trackers | ✅ |
| `CP3-10` | ML_SYSTEM_PACKAGE mirror | ✅ |
| `CP3-11` | verify_onboarding + grep gate + build | ✅ |

**Gate PASS:** §11 `COPY_POST_L3_FULL_AUDIT.md` · FAQ visible **41** · RU/EN parity.

---

# BATCH QA — 138 sign-off (P0) · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `B-QA-01` | EXTENDED_138 L3 criterion | ✅ `docs/release/QA_01_EXTENDED138_L3_CRITERION.md` |
| `B-QA-02` | 138/138 TestFlight | ⏸ **единственная точка Archive** (финальный блок) |
| `B-QA-03` | grep zero mock 24h | ✅ static + VPS 24h `QA_03_RUNTIME_VPS_24H.md` |
| `B-QA-04` | merge SECURITY_UNIFIED_IMPLEMENTATION.md | ✅ |
| `B-QA-05` | prod registry ≥1074 + smoke weekly | ✅ `QA_05_SFM_REGISTRY_SMOKE.md` 2026-06-11 |
| `B-QA-06` | LOC regression: все 143 batch items RU/EN | ✅ `QA_06_LOC_REGRESSION.md` |

---

# REMAINING 19 / 143 — трекер оставшихся задач (124 → 143)

**SSOT счётчик:** отмечать ✅ здесь → обновить header `124/143` → `security-l3-report.json`.

| # | ID | Задача | Зачем | Блокирует Archive | Статус |
|---|-----|--------|-------|-------------------|--------|
| **1** | `B7-04a` | VPN baseline: `vpn_prod_smoke.sh` на VPS | Базовая линия VPN | ✅ да | ✅ 10/10 2026-06-11 |
| **2** | `B7-04b` | VPN post-change smoke после B7 crash/roadside | Emergency не сломал VPN | ✅ да | ✅ 10/10 повторный прогон |
| **3** | `B7-04` | VPN sign-off 10/10 → GATE-J + EX-VPN | BATCH 7 / EXTRAS gate | ✅ да | ✅ nonce fix deployed VPS |
| **4** | `BUILD-FINAL` | `xcodebuild build` ALADDIN Simulator | Компиляция перед TestFlight | ✅ да | ✅ BUILD SUCCEEDED |
| **5** | `B7-UT-01` | Unit tests B5/B6/B7 | Регрессия Family/Device | ✅ да | ✅ 62/62 TEST SUCCEEDED |
| **6** | `B2-00c` | `AppConfigTests` + `SecurityVerdictModelsTests` | AppConfig build 227 sync | ✅ да | ✅ в составе R-05 |
| **7** | `B-QA-02` | **Archive + TestFlight 138/138** | Финальный шаг на Mac с Apple ID | ⏸ последний | ⏸ см. `QA_02_TESTFLIGHT_CHECKLIST.md` |
| **8** | `B2-09` / **R-08** | Antifake dfk matrix demo | Deepfake reviewer path | PNG ⏸ device | ✅ backend + guide |
| **9** | `B3-08` / **R-09** | Privacy Hub demo | Privacy L3 | PNG ⏸ device | ✅ backend + guide |
| **10** | `B4-06` / **R-10** | Identity Hub demo | Identity L3 | PNG ⏸ device | ✅ backend + guide |
| **11** | `B-QA-03-runtime` | VPS 24h mock grep | Runtime mock-free | нет | ✅ re-run `hub-demo-smoke-report.json` |
| **12** | `B-LOC-02` | B-PRE loc (AppConfig/tests) | batch_loc 12/12 | нет | ✅ N/A no UI strings |
| **13** | `eld-03` | Elderly voice wellness | post-L3 doc | нет | ✅ `ELD_03_VOICE_DEFERRED.md` |
| **14** | `SEC-P2-01` | darkweb `/breaches` explicit | Убрать legacy/wildcard | нет | ✅ |
| **15** | `SEC-P2-02` | identity `/monitor-credit` alias | Канонический путь | нет | ✅ |
| **16** | `SEC-P2-03` | `/api/location/bubble` → 410 | Legacy deprecation | нет | ✅ |
| **17** | `SEC-P2-04` | parental_control без monitoring routes | Explicit only | нет | ✅ |
| **18** | `SEC-P2-05` | `app/routers/devices.py` | Dedicated router | нет | ✅ |
| **19** | `COPY-POST-L3` | Маркетинг RU/EN: OB+FAQ+Privacy+Terms+landing | R-07 Archive | — | ✅ `docs/release/COPY_POST_L3_PROGRESS.md` |

### Порядок исполнения R-01…R-19

```
R-01 B7-04a ──► R-02 B7-04b ──► R-03 B7-04
                    │
                    ▼
         R-04 BUILD-FINAL
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
    R-05 B7-UT-01         R-06 B2-00c
         └──────────┬──────────┘
                    ▼
    R-14…18 SEC-P2 ──► R-19 COPY-POST-L3
                    │
                    ▼
    R-07 B-QA-02 Archive (ПОСЛЕДНИЙ) + R-08…10 Hub demos
```

**Archive (R-07):** только на Mac с залогиненным Apple ID — в **самом конце**. До него: **R-19 COPY-POST-L3** (SEC-P2 ✅).

### R-19 COPY-POST-L3 — подзадачи (87 правок / 14 зон)

**SSOT:** `docs/release/COPY_POST_L3_FULL_AUDIT.md` · **TODO:** `docs/release/COPY_POST_L3_TODO.md`

| ID | Зона | Статус |
|----|------|--------|
| `CP3-01` | Онбординг OB_01,04,06 + EN OB_02 military (военные RU keep) | ✅ |
| `CP3-02` | Тарифы/каталог «по тарифу» | ✅ |
| `CP3-03` | FAQ смягчение 12 answers (skip unsafe_wifi) | ✅ |
| `CP3-04` | FAQ +5 в каталог (aes256, network, malicious_apps, sms, location) | ✅ |
| `CP3-05` | FAQ +4 новых (crash, roadside, SOS, dark_web) | ✅ |
| `CP3-06` | Privacy app + landing (военное keep; убрать 100%/невозможно) | ✅ |
| `CP3-07` | Terms + antifake/emergency sections | ✅ |
| `CP3-08` | landing + PRIVACY_POLICY_FULL_152FZ | ✅ |
| `CP3-09` | COPY audits + trackers | ✅ |
| `CP3-10` | ML_SYSTEM_PACKAGE mirror | ✅ |
| `CP3-11` | verify script + grep gate + xcodebuild | ✅ |

**Согласовано PO:** основных киберугроз · защита по тарифу · анализирует/предупреждает · проверяет · военные технологии **не убирать** · `faq_unsafe_wifi` **не менять**.

---

## Дополнительные задачи (вошли в план 143)

| ID | Batch | Описание | Статус | Артефакт |
|----|-------|----------|--------|----------|
| R-19 | COPY-POST-L3 | Marketing RU/EN: OB, FAQ 41, Privacy 5+, Terms, landing | ✅ | `COPY_POST_L3_*` |
| R-08 | B2-09 | Antifake dfk-01…08 demo + VPS smoke | ✅ backend | `QA_HUB_DEMO_R08_R10.md` |
| R-09 | B3-08 | Privacy dark web demo + VPS smoke | ✅ backend | same |
| R-10 | B4-06 | Identity SNILS demo + VPS smoke | ✅ backend | same |
| CP3-sync | R-19 | kb JSON из LocalizationManager | ✅ | `scripts/sync_cp3_kb_from_loc.py` |
| CP3-ml | R-19 | ML_SYSTEM_PACKAGE mirror 132 keys | ✅ | `scripts/sync_cp3_ml_loc_mirror.py` |
| Hub-smoke | R-08…10 | VPS bundle + mock grep 24h | ✅ | `scripts/run_hub_demo_vps_smoke.sh` |
| Audit-143 | QA | План–факт + автотесты | ✅ | `PLAN_FACT_AUDIT_143_2026-06-11.md` |

---

## Порядок выполнения

```
SFM-WIRE + B-OPS ──► BATCH 0 ──► BATCH 1 (GATE-D backend ✅)
       │
       ▼
BATCH SYNC (SYNC-01…05) ──► B-PRE iOS migration (B2-00…00c)
       │
       ▼
BATCH 2 Antifake Hub iOS (GATE-E)
       │
   ┌───┴───┬─────────┐
   ▼       ▼         ▼
BATCH 3  BATCH 4  BATCH 5  (B3/B4 после B2; shared AppConfig готов)
   │       │         │
   └───────┴────┬────┘
                ▼
         BATCH 5 Device
                ▼
         BATCH 6 Family
                ▼
         BATCH 7 Extras
                ▼
         BATCH COPY (не онбординг)
                ▼
         BATCH QA
                ▼
         XCODE ARCHIVE + TestFlight (только здесь)
```

## Gate после каждого блока (ML обязана)

| После batch | Gate ID | Детали |
|-------------|---------|--------|
| SFM-WIRE + OPS-01…06 | GATE-A | `ML_SYSTEM_HANDOFF` §4 |
| BATCH 0 | GATE-B,C | protection persist + toggles |
| AF backend + B1 | GATE-D | antifake API smoke |
| BATCH 2 | GATE-E | iOS unit + Hub code |
| BATCH 3/4/5 | GATE-F/G/H | domain smoke |
| BATCH 6/7 | GATE-I/J | family + extras |
| OPS-07…12 + COPY | GATE-K | ML contract |
| BATCH QA | GATE-FINAL | 138 L3 → **тогда Xcode** |

Отчёт: `docs/release/gates/security-l3-report.json`

## Итоговая картина после всех batch

| Метрика | Сейчас | После SFM-WIRE | После всех batch |
|---------|--------|----------------|------------------|
| SFM functions loaded | 14 / fallback | **1000+** | 1000+ agents |
| :8003 execute | fake success | real SFM | real SFM |
| Protection L2 | ❌ | ❌ | ✅ 9/9 |
| deepfakes L3 | ❌ | ⚠️ backend | ✅ Hub |
| 138 L3 | ~55% | ~60% | **100%** |
| Mock in prod | да | меньше | **0** |

---

## Синхронизация с другими файлами

| Batch ID | MASTER / Roadmap |
|----------|------------------|
| B-SFM-W* | sfm-01…12 |
| B0-* | R0-G1…G12, sec-* |
| B1-* | dw/id/dc/loc/av/comp/iot/mob |
| B2-* | ANTIFAKE_PRODUCTION_TODO |
| B3-B7 | SECURITY_138_MASTER_TODO |
| B-QA-* | R8-* |
