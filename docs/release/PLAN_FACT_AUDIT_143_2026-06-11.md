# План–факт аудит 143 задач — финальный отчёт

> **⚠️ Superseded:** см. актуальный [`PLAN_FACT_AUDIT_143_2026-06-13.md`](PLAN_FACT_AUDIT_143_2026-06-13.md) и [`MASTER_STATUS_INDEX.md`](MASTER_STATUS_INDEX.md). Этот файл — архив 2026-06-11.

**Дата:** 2026-06-11 · **Счёт:** **137 / 143** ✅ · **Осталось:** **6** (R-07 Archive block)  
**SSOT счётчик:** `docs/release/gates/security-l3-report.json` · **Трекер:** `.cursor/IMPLEMENTATION_BATCHES_TODO.md`

---

## 1. Executive summary

| Область | План | Факт | Вердикт |
|---------|------|------|---------|
| Backend explicit routers (B1) | 12/12 | 12/12 + GATE-D smokes | ✅ PASS |
| iOS Hubs B2–B6 | 50 impl | 50/50 code | ✅ PASS |
| BATCH 7 Extras + VPN | 4/4 | 4/4 + emergency smoke | ✅ PASS |
| SEC-P2 legacy | 5/5 | 5/5 VPS | ✅ PASS |
| COPY audit (B-COPY) | 4/4 | 4/4 docs | ✅ PASS |
| **R-19 COPY-POST-L3** | marketing RU/EN | код + kb + landing | ✅ PASS |
| **R-08…10 Hub demos** | B2-09 B3-08 B4-06 | VPS smokes + guides | ✅ backend PASS · PNG ⏸ device |
| B-QA-03 mock-free | static + 24h | grep 0 + VPS re-run | ✅ PASS |
| xcodebuild | compile | **BUILD SUCCEEDED** 2026-06-11 | ✅ PASS |
| B-QA-02 Archive | TestFlight 138 | blocked signing cert | ⏸ **единственный блокер** |

**Рекомендация специалиста:** код и prod API готовы к Archive. Следующая сессия — **только Mac + Apple ID**: Archive → TestFlight → PNG Hub → 138 walkthrough.

---

## 2. Автотесты (выполнено сегодня)

| Проверка | Команда / артефакт | Результат |
|----------|-------------------|-----------|
| FAQ catalog | `grep UnifiedFAQEntry` → 41 | ✅ |
| Onboarding RU copy | `verify_onboarding_sync_01_03.py` | ✅ RU strings · ⏸ Figma case1 layout (pre-existing) |
| Stale marketing | grep LocalizationManager + ML mirror | **0** hits |
| Localizable.strings OB | ru.lproj page1/4 | ✅ sync с LM |
| VPS antifake | `test_antifake_prod_smoke.py` | `pass: true` |
| VPS darkweb | `test_darkweb_prod_smoke.py` | `pass: true` |
| VPS identity | `test_identity_theft_prod_smoke.py` | `pass: true` |
| Mock grep 24h | `run_hub_demo_vps_smoke.sh` | **0** all services |
| kb sync | `sync_cp3_kb_from_loc.py` | 40 faq + 2 onboarding |
| xcodebuild | iPhone 13 Pro Max sim 18.4 | **BUILD SUCCEEDED** |
| Unit tests via scheme | ALADDINTests | ⏸ scheme/test plan — ранее **62/62** (R-05) |

---

## 3. План–факт по фазам (143)

| # | Фаза | План | Факт | Gate |
|---|------|------|------|------|
| 1 | SFM-WIRE | 12 | 12/12 | GATE-A |
| 2 | OPS | 22 | 22/22 | GATE-A0 |
| 3 | BATCH 0 | 8 | 8/8 | GATE-B |
| 4 | BATCH 1 API | 12 | 12/12 | GATE-D |
| 5 | BATCH SYNC | 5 | 5/5 | — |
| 6 | B-PRE iOS | 6 | 6/6 | pre-GATE-E |
| 7 | BATCH 2 Antifake | 12 | 12/12 | GATE-E |
| 8 | BATCH 3 Privacy | 8 | 8/8 | GATE-F |
| 9 | BATCH 4 Identity | 8 | 6/6 impl + 2 loc | GATE-G |
| 10 | BATCH 5 Device | 9 | 9/9 | GATE-H |
| 11 | BATCH 6 Family | 5 | 5/5 | GATE-I |
| 12 | BATCH 7 Extras | 4 | 4/4 | GATE-J |
| 13 | BATCH LOC | 12 | 12/12 | pre-FINAL |
| 14 | BATCH COPY | 4 | 4/4 | GATE-K |
| 15 | SEC-P2 | 5 | 5/5 | post-L3 |
| 16 | **R-19 COPY-POST-L3** | 1 | 1/1 | GATE-K-post |
| 17 | **R-08…10** | 3 | 3/3 backend | GATE-FINAL-prep |
| 18 | BATCH QA | 6 | 5/6 | GATE-FINAL ⏸ |
| — | **Осталось** | 6 | R-07 block | Archive |

*Счёт 137 = 143 − 6 (B-QA-02 + PNG + walkthrough + archive sign-off sub-items).*

---

## 4. Дополнительные задачи (вне исходного BATCH, вошли в план)

| ID | Описание | Артефакты |
|----|----------|-----------|
| **R-19** | Marketing copy post-L3: OB, FAQ 41, Privacy 5+, Terms | `COPY_POST_L3_*`, `LocalizationManager`, kb JSON |
| **R-08** | B2-09 Antifake dfk matrix demo | `QA_HUB_DEMO_R08_R10.md` §R-08 |
| **R-09** | B3-08 Privacy dark web demo | same + darkweb smoke |
| **R-10** | B4-06 Identity SNILS demo | same + identity smoke |
| **CP3-scripts** | kb + ML mirror automation | `scripts/sync_cp3_kb_from_loc.py`, `sync_cp3_ml_loc_mirror.py` |
| **CP3-scripts** | Hub VPS bundle | `scripts/run_hub_demo_vps_smoke.sh` |
| **Gates JSON** | Hub demo evidence | `gates/hub-demo-smoke-report.json` |

---

## 5. Код ↔ заявления (spot-check)

| Заявление | Код / evidence | OK |
|-----------|----------------|-----|
| FAQ 41 в Support | `13_SupportScreen.swift` 41 entries | ✅ |
| OB «основных киберугроз» | LM + Localizable + Onboarding fallbacks | ✅ |
| OB_02 military keep RU | LM `onboarding_page2_desc` | ✅ |
| Privacy 5+ servers | LM `privacy_policy_*_servers_subtitle` | ✅ |
| Terms antifake async | `terms_section_network_protection_content_6/7` | ✅ |
| Antifake 4 tabs | `AntifakeHubScreen.swift` | ✅ |
| Privacy 3 tabs | `PrivacyHubScreen.swift` | ✅ |
| Identity 4 tabs | `IdentityHubScreen.swift` | ✅ |
| No mock in prod logs | VPS grep 24h | ✅ |
| landing privacy §13 | «Анонимная модель аккаунта» | ✅ |
| `faq_unsafe_wifi` unchanged | LM unchanged vs audit | ✅ |

---

## 6. Известные расхождения (не блокеры Archive)

| Item | Статус | Действие |
|------|--------|----------|
| Figma OB case1 anchors | drift | Отдельный UX тикет; copy gate PASS |
| Hub PNG screenshots | нет файлов в `testflight-build227/` | Capture at Archive session |
| iOS Distribution cert | blocker в QA_02 | Xcode Accounts на Mac PO |
| CP3-12 phase-2 FAQ | defer | После релиза |
| `help-faq.html` | defer | Нет stale фраз |
| ALADDINTests scheme | test plan | Использовать prior 62/62 или fix scheme |

---

## 7. Индекс документов (направление 143)

### Главные трекеры

| Документ | Роль |
|----------|------|
| `.cursor/IMPLEMENTATION_BATCHES_TODO.md` | **143 batch todo** |
| `.cursor/SECURITY_MASTER_INDEX.md` | Карта всех docs |
| `docs/release/gates/security-l3-report.json` | **Evidence gates** |
| `docs/release/PLAN_FACT_AUDIT_143_2026-06-11.md` | **Этот отчёт** |
| `docs/release/COPY_POST_L3_PROGRESS.md` | R-19 + остаток 6/143 |

### COPY / Marketing (R-19)

| Документ |
|----------|
| `docs/release/COPY_POST_L3_FULL_AUDIT.md` |
| `docs/release/COPY_POST_L3_TODO.md` |
| `docs/release/COPY_01_ONBOARDING_L3_AUDIT.md` |
| `docs/release/COPY_02_FAQ_L3_AUDIT.md` |
| `docs/release/COPY_03_TARIFFS_HUB_MAP.md` |
| `docs/release/COPY_04_APP_STORE_REVIEW_NOTES.md` |

### Hub demos (R-08…10)

| Документ |
|----------|
| `docs/release/QA_HUB_DEMO_R08_R10.md` |
| `docs/release/gates/hub-demo-smoke-report.json` |
| `docs/release/gates/testflight-build227/README.md` |

### QA / Archive (R-07)

| Документ |
|----------|
| `docs/release/QA_02_TESTFLIGHT_CHECKLIST.md` |
| `docs/release/QA_01_EXTENDED138_L3_CRITERION.md` |
| `docs/release/QA_03_MOCK_GREP_AUDIT.md` |
| `docs/release/QA_03_RUNTIME_VPS_24H.md` |
| `docs/release/QA_05_SFM_REGISTRY_SMOKE.md` |
| `docs/release/QA_06_LOC_REGRESSION.md` |

### Backend / SEC-P2

| Документ |
|----------|
| `docs/SEC06_LEGACY_ROUTER_AUDIT.md` |
| `docs/release/SEC_P2_LEGACY_MIGRATION.md` |
| `docs/server/L3_SMOKE_CONTRACT.md` |
| `docs/IOS_EXPLICIT_API_MATRIX.md` |

### Handoff ML

| Документ |
|----------|
| `ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md` |

---

## 8. Рекомендации специалиста

### P0 — перед submit в App Store

1. **Archive** на Mac с Distribution cert (`QA_02_TESTFLIGHT_CHECKLIST.md`).
2. **PNG** по `QA_HUB_DEMO_R08_R10.md` → `gates/testflight-build227/`.
3. Вставить `COPY_04_APP_STORE_REVIEW_NOTES.md` в Review Notes.
4. Пройти 138 matrix на TestFlight build → `xcode_archive_allowed: true`.

### P1 — после релиза

1. ~~CP3-12 FAQ (bypass, geofencing, wellness)~~ ✅ build 227.
2. ~~Figma anchor sync OB_02 title y=356~~ ✅ Figma `103:68` + Swift + verify PASS.
3. ~~ALADDIN_SecurityCore.xctestplan + scheme + CI~~ ✅.
4. ~~af-2-09 rate limits~~ ✅ `antifake_rate_limit.py` (text/url 60/min, media 10/h).
5. Main card «Защита Aladdin» ✅.

### P2 — ops

1. Периодический `run_hub_demo_vps_smoke.sh` (weekly).
2. `test_security_prod_smoke.py` timer (B-OPS-22) — уже deployed.

---

*Audit v1.0 · evidence run 2026-06-11 · Next: R-07 Archive*
