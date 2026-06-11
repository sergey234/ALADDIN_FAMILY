# Security 138 — Master Cursor Todo (синхронизированный)

**Создано:** 2026-06-09 · **Scope:** 138 функций + системная инфраструктура · **Prod:** без mock  
**Анализ:** `docs/SECURITY_138_GAP_ANALYSIS.md`  
**План 100% L1/L2/L3:** `docs/SECURITY_100_PERCENT_MASTER_PLAN.md`  
**Единый план (проблемы + SFM + 9 категорий):** `docs/SECURITY_UNIFIED_100_PERCENT_PLAN.md`  
**Roadmap по фазам:** `.cursor/SECURITY_100_PERCENT_ROADMAP_TODO.md`  
**Правило:** **онбординг не меняем** до Фазы 7 (только `copy-01-audit`).  
**Anti-fake (дубликат AF-*):** `.cursor/ANTIFAKE_PRODUCTION_TODO.md` — **не удалять**; при закрытии задачи обновлять **оба** файла.

**Счёт batch (SSOT):** **111 / 143** — см. `.cursor/IMPLEMENTATION_BATCHES_TODO.md`  
**Счёт master (этот файл):** пересчитывать при закрытии §-задач; PC-MON **6/6 ✅**, CAT partial (см. § CAT)

**Handoff для следующей ML:** `ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md` §12–§13 · **Next: BATCH 7 Extras**

---

## Синхронизация файлов

| Файл | Роль |
|------|------|
| **Этот файл** | Единый реестр всех доменов (SEC, AF, DW, ID, …) |
| `ANTIFAKE_PRODUCTION_TODO.md` | Детальный трекер anti-fake (Batch AF-0…12) — зеркало § AF |
| `ANTIFAKE_PRODUCTION_PLAN.md` | Техспек anti-fake |
| `SECURITY_138_GAP_ANALYSIS.md` | Почему 138 «ok» ≠ 100% в приложении |

**Правило:** ID задачи `af-*` = `AF` в master; `sec-*`, `dw-*`, `id-*`, … — только в master.

---

# § SEC — Общая инфраструктура (P0) · 10 задач

*Влияет на все 100 threat toggles + wildcard.*

| ID | Задача | Статус | Зеркало |
|----|--------|--------|---------|
| `sec-01` | `protection.py`: logger + enable/disable 200 | ✅ | `af-0-01` B0-01 |
| `sec-02` | DB `user_protection_settings` + UPSERT | ✅ | `af-0-02/03` B0-02 |
| `sec-03` | Канонический enum category IDs iOS↔server | ✅ | `af-0-04` B0-03 |
| `sec-04` | Block wildcard: deepfake, fake-news, antifake | ✅ | `af-0-05` B0-05 |
| `sec-05` | Gateway guard: reject mock-real-protection empty result | ✅ | `af-0-06` B0-06 |
| `sec-06` | Audit wildcard list → explicit routers backlog | ✅ | `docs/SEC06_LEGACY_ROUTER_AUDIT.md` |
| `sec-07` | Disable OptimizedSFM mock for security mutations | ✅ | B-SFM-W07 |
| `sec-08` | Пересмотр `ios-functional-138-report`: fail on 404/mock | ✅ | B-OPS-11 |
| `sec-09` | `docs/server/test_security_prod_smoke.py` all domains | ✅ | B1-12 GATE-D |
| `sec-10` | OpenAPI publish policy: security paths only explicit | ✅ | B1-11 |

---

# § SFM — Agent Registry (не монолит) · 12 задач · P0

*Прод 09.06: исправлено SFM-WIRE — `:8003` sfm_loaded, registry ≥1000.*

| ID | Задача | Статус |
|----|--------|--------|
| `sfm-01` | Переименовать `security/types/` → `security/security_types/` (circular import) | ⬜ |
| `sfm-02` | `AgentRegistry` class + honest `health.functions_count` | ✅ |
| `sfm-03` | Удалить `OptimizedSFM` mock из prod `get_sfm()` path | ✅ |
| `sfm-04` | `start_sfm_core_http.py`: unknown function → 503 `AGENT_NOT_REGISTERED` | ✅ |
| `sfm-05` | `SFMAdapter`: пробрасывать 503, не подменять success | ✅ |
| `sfm-06` | `categoryId` → `activate_agents_for_category()` mapping (9 категорий) | ✅ |
| `sfm-07` | Register parental/VPN agents (regression, уже работают via routers) | ⬜ |
| `sfm-08` | Register antifake agents (phase 1) | ✅ |
| `sfm-09` | Register privacy agents (DW, cleanup, location) | ✅ |
| `sfm-10` | Register identity + device agents | ✅ |
| `sfm-11` | Lazy load heavy deps (cv2, transformers) per agent | ⬜ |
| `sfm-12` | Опционально: port handlers из `safe_function_manager.py` chunk-by-chunk | ⬜ |

---

# § AF — Anti-Fake / Deepfakes (8 угроз) · 72 задачи

> Полная таблица: **`.cursor/ANTIFAKE_PRODUCTION_TODO.md`**  
> Закрывая `af-X-YY` здесь — ставь ✅ и в ANTIFAKE файле.

| Batch | Название | Задач | P | Статус |
|-------|----------|-------|---|--------|
| AF-0 | Prod safety & infra | 8 | P0 | 7/8 ✅ |
| AF-1 | Agents & deps | 9 | P0 | 0/9 ⬜ |
| AF-2 | API routers | 10 | P0 | 10/10 ✅ |
| AF-3 | Async workers & metrics | 7 | P0 | 0/7 ⬜ |
| AF-4 | Calls & spoofing | 8 | P1 | 0/8 ⬜ |
| AF-5 | iOS sync & settings | 6 | P0 | 5/6 🔄 |
| AF-6 | iOS Antifake Hub UI | 10 | P1 | 9/10 🔄 |
| AF-7 | Share + AI tool | 5 | P1 | 0/5 ⬜ |
| AF-8 | Copy & App Store | 6 | P1 | 0/6 ⬜ |
| AF-9 | 8 threats matrix | 8 | P1 | 0/8 ⬜ |
| AF-10 | Deploy & nginx | 5 | P0 | 0/5 ⬜ |
| AF-11 | QA acceptance | 6 | P0 | 0/6 ⬜ |
| AF-12 | Ops monitoring | 4 | P2 | 0/4 ⬜ |

**AF IDs:** `af-0-01` … `af-12-04` — см. ANTIFAKE_PRODUCTION_TODO.md

---

# § DW — Dark Web / dataLeaks (UG-LEAK #34) · 8 задач

| ID | Задача | Статус |
|----|--------|--------|
| `dw-01` | Router `app/routers/darkweb.py` — check email/phone (real agent, no mock) | ✅ |
| `dw-02` | `POST /api/darkweb/scan/start` → user_id ingest (не legacy leaks table) | ✅ |
| `dw-03` | `GET /api/darkweb/leaks` — только user-scoped breaches | ✅ |
| `dw-04` | Worker: `dark_web_monitoring_agent` lazy load | ✅ lazy via dark_web_scan_service |
| `dw-05` | iOS `DarkWebMonitoringModal` — scan CTA → real job + poll | ⬜ BATCH 3 |
| `dw-06` | iOS empty state 0/0/0 vs real breaches UX | ⬜ BATCH 3 |
| `dw-07` | Premium gate server-side | ✅ |
| `dw-08` | Smoke: prod scan → leak row OR honest empty + source≠mock | ✅ test_darkweb_prod_smoke.py |

---

# § ID — Identity Theft / fraud (UG-FRAUD) · 8 задач

| ID | Задача | Статус |
|----|--------|--------|
| `id-01` | Router `/api/identity-theft/*` — SNILS monitor (RU agent) | ✅ |
| `id-02` | `monitor/credit`, `check/fraud`, `detect` endpoints | ✅ |
| `id-03` | Unified verdict contract (как antifake) | ✅ |
| `id-04` | iOS `IdentityTheftModal` — формы SNILS/паспорт hash only | ⬜ |
| `id-05` | iOS attempts list + block/allow actions | ⬜ |
| `id-06` | Связать `fraud` category toggle → agent activation | ⬜ |
| `id-07` | Reports stats ≠ substitute for detect — separate UI | ✅ backend split `/api/identity-theft/detect` |
| `id-08` | Smoke prod identity-theft flow | ✅ test_identity_theft_prod_smoke.py |

---

# § DC — Personal Data Cleanup (dataLeaks) · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `dc-01` | Verify/fix `POST /api/data/cleanup/start` — real agent | ✅ |
| `dc-02` | `GET stats/records` user-scoped persist | ✅ |
| `dc-03` | iOS `PersonalDataCleanupModal` — scan progress + results | ⬜ |
| `dc-04` | `ProtectionSettingsViewModel.setPersonalDataCleanup` → API | ⬜ |
| `dc-05` | Remove wildcard path for cleanup | ✅ blocklist + explicit router |
| `dc-06` | Smoke: start cleanup → record in DB | ✅ test_data_cleanup_prod_smoke.py |

---

# § LOC — Location Bubble (UG-LEAK #39, PC-GEO) · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `loc-01` | Router `/api/location-bubble/generate` explicit | ✅ |
| `loc-02` | Settings get/set/all + history | ✅ |
| `loc-03` | iOS Location Bubble sheet → API wire | ⬜ |
| `loc-04` | Parental geofence: geocode TODO Family/FamilyModals | ⬜ |
| `loc-05` | Map display real coords vs bubble | ⬜ |
| `loc-06` | Smoke prod location-bubble | ✅ test_location_bubble_prod_smoke.py |

---

# § AV — Antivirus / cyberThreats (UG-CYBER, UG-MOB) · 8 задач

| ID | Задача | Статус |
|----|--------|--------|
| `av-01` | `POST /api/antivirus/scan` — real scan job, verdict threats[] | ✅ |
| `av-02` | `GET /api/malware/threats` + quarantine actions persist | ✅ |
| `av-03` | iOS `MalwareDetectionSettingsScreen` — wire quick scan button | ⬜ |
| `av-04` | iOS `AntivirusManager` — sync with server threats list | ⬜ |
| `av-05` | `27_ProtectionStatsScreen` — real blocked count from API | ⬜ |
| `av-06` | File importer scan flow end-to-end | ⬜ |
| `av-07` | Premium/personal tier limits on scan frequency | ✅ |
| `av-08` | Smoke: upload eicar test file → quarantine | ✅ |

---

# § COMP — Advanced Protection components · 10 задач

*Phishing, Network, Mobile, Incident, Password — кнопки TODO.*

| ID | Задача | Статус |
|----|--------|--------|
| `comp-01` | `PhishingProtectionSettingsScreen` → sensitivity API | ✅ |
| `comp-02` | `NetworkSecuritySettingsScreen` → scan network API | ⬜ |
| `comp-03` | `MobileSecuritySettingsScreen` → device check API | ⬜ |
| `comp-04` | `IncidentResponseSettingsScreen` → test incident API | ⬜ |
| `comp-05` | `ComponentStatusService` — no local-only toggles for prod | ⬜ |
| `comp-06` | `GET/POST /api/components/*` explicit only (no wildcard) | ✅ |
| `comp-07` | AI Categories `/api/ai/categories/*` — fix 404 → real routers | ⬜ |
| `comp-08` | Anti-tracker / privacy tracker stats → UI | ⬜ |
| `comp-09` | Password generator → `password_security_agent` optional check | ⬜ |
| `comp-10` | Advanced protection aggregator card — real status from API | ⬜ |

---

# § IOT — IoT Security (10 угроз) · 7 задач

| ID | Задача | Статус |
|----|--------|--------|
| `iot-01` | `IoTSecurityModule` — real home/device API (не home_default) | ⬜ |
| `iot-02` | Server IoT scan/discover router | ✅ |
| `iot-03` | `IoTSecurityScreen` fix threat — API call | ⬜ |
| `iot-04` | Threat list + severity from server | ⬜ |
| `iot-05` | Link `iotThreats` category enable → agent | ⬜ |
| `iot-06` | iOS device pairing homeId from family settings | ⬜ |
| `iot-07` | Smoke prod IoT scan | ✅ |

---

# § MOB — Mobile Threats · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `mob-01` | `mobile_security_agent` explicit endpoints | ✅ |
| `mob-02` | App inventory / sideload risk check API | ✅ |
| `mob-03` | iOS `22_DeviceDetailScreen` — mobile threats section | ⬜ |
| `mob-04` | SMS smishing check (text pipeline reuse AF) | ⬜ |
| `mob-05` | Link `mobileThreats` toggle → agents | ⬜ |
| `mob-06` | Smoke mobile security | ✅ |

---

# § PC-MON — Parental monitoring gaps · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `pc-01` | `GET /api/parental-control/monitoring/detail` — FastAPI only | ✅ |
| `pc-02` | Remove mock envelope for parental-control paths | ✅ |
| `pc-03` | `FamilyModals` messages/calls/lastContact from API | ✅ |
| `pc-04` | `ParentalControlReportsManager` — implement API (сейчас TODO) | ✅ |
| `pc-05` | PDF/CSV export reports | ✅ |
| `pc-06` | Smoke monitoring detail with JWT | ✅ |

---

# § EM — Emergency (crash + roadside) · 6 задач

| ID | Задача | Статус |
|----|--------|--------|
| `em-01` | `crash_detection_agent` routers start/history/cancel | ✅ backend |
| `em-02` | iOS uncomment `CrashDetectionSettingsModal` + API | ✅ |
| `em-03` | CoreMotion / crash pipeline prod test | 🔄 VPS smoke |
| `em-04` | `roadside_assistance_agent` call/status/cancel API | ✅ backend |
| `em-05` | iOS Support `RoadsideAssistance` sheet → real API | ✅ |
| `em-06` | Smoke emergency flows | 🔄 `test_emergency_prod_smoke.py` VPS |

---

# § ELD — Elderly interface · 4 задачи

| ID | Задача | Статус |
|----|--------|--------|
| `eld-01` | Remove `mockData` calendar in `09_ElderlyInterfaceScreen` | ✅ |
| `eld-02` | Wire medications/appointments API fully | ✅ sync on appear |
| `eld-03` | Voice session wellness integration | ⏸ deferred post-L3 |
| `eld-04` | Smoke elderly flows Family+ | 🔄 VPS + B-QA-02 |

---

# § SYNC — iOS global settings sync · 5 задач

| ID | Задача | Статус |
|----|--------|--------|
| `sync-01` | `ProtectionSettingsManager.loadSettingsFromServer` enable | ⬜ |
| `sync-02` | `AdditionalFeaturesManager` real API (TODO) | ⬜ |
| `sync-03` | `UserProfileManager` profile load implement | ⬜ |
| `sync-04` | `ParentalControlManager` TODO API blocks | ⬜ |
| `sync-05` | Conflict resolution + offline queue for settings | ⬜ |

*Детали AF-5 дублируют sync-01.*

---

# § COPY — Marketing honesty (все домены) · 5 задач

| ID | Задача | Статус |
|----|--------|--------|
| `copy-01-audit` | Audit onboarding vs L3 map — **без правок UI/текстов** | ✅ `docs/release/COPY_01_ONBOARDING_L3_AUDIT.md` |
| `copy-01` | *(заморожено до Фазы 7)* Onboarding edits only after L3 | ⏸ post B-QA-02 |
| `copy-02` | FAQ — only features with verdict UI | ✅ `docs/release/COPY_02_FAQ_L3_AUDIT.md` |
| `copy-03` | Tariffs premium bullets ↔ Hub screens map | ✅ `docs/release/COPY_03_TARIFFS_HUB_MAP.md` |
| `copy-04` | `SECURITY_138_USER_CLAIMS.md` approved list | 🔄 merged in COPY_04 |
| `copy-05` | App Store review notes per domain | ✅ `docs/release/COPY_04_APP_STORE_REVIEW_NOTES.md` |

*AF-8 дублирует anti-fake copy.*

---

# § CAT — Per-threat L3 (9 категорий × 100 угроз) · 58 задач

> Детали в `docs/SECURITY_UNIFIED_100_PERCENT_PLAN.md` §4. Gate: каждый ID = TestFlight L3.

| Префикс | Категория | IDs | Статус |
|---------|-----------|-----|--------|
| `cyb-01…10` | cyberThreats | 10 | 10/10 ✅ (B5-06 Device Hub) |
| `frd-01…12` | fraud | 12 | 12/12 ✅ (B4-05 Identity Hub) |
| `chd-01…17` | childThreats | 17 | 17/17 ✅ (B6-05 coverage + routes) |
| `dlk-01…12` | dataLeaks | 12 | 12/12 ✅ (B3-07 Privacy Hub) |
| `dfk-01…08` | deepfakes | 8 | 8/8 ✅ (= Antifake B2 + `af-9-*`) |
| `net-01…06` | internetThreats | 6 | 0/6 ⬜ (VPN regression B7-04 / R6-G5) |
| `mob-07…10` | mobileThreats | 4 | 4/4 ✅ (B5-07 mob-01…10) |
| `fam-01…15` | familyThreats | 15 | 0/15 ⬜ (fam-* regression post-B6) |
| `iot-08…10` | iotThreats | 3 | 3/3 ✅ (B5-08 iot-01…10) |

---

## Критический путь (все 138)

```
SEC-01…10 + SFM-01…06  ─┬─► AF batches (deepfakes 8)
                          ├─► DW + ID + DC (dataLeaks 12 + fraud 12)
                          ├─► AV + COMP (cyber 10 + mobile 10)
                          ├─► IOT (10)
                          ├─► PC-MON (parental monitoring)
                          ├─► SYNC (iOS)
                          ├─► CAT per-threat sign-off
                          └─► COPY (без онбординга) + QA gates
```

**Оценка полного scope:** ~14–18 недель (2 backend + 2 iOS) при параллели.

---

## Как обновлять

1. Закрыл задачу → ✅ в **этом файле** и в **доменном** файле (AF → ANTIFAKE too).  
2. Пересчитай счёт: AF 72 + SEC 10 + SFM 12 + CAT 58 + DW 8 + … = **226**.  
3. После SEC+AF gate — перегенерировать `EXTENDED_138_CHECKLIST` verify с L3 критерием.
