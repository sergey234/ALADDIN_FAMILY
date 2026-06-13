# План–факт аудит 143 задач — финальный отчёт (build 232)

**Дата:** 2026-06-13 · **Build:** **232** (`3cfcf256`)  
**Счёт направление 143:** **137 / 143** ✅ · **Осталось:** **6** (R-07 Archive block)  
**Supplemental build 232:** **18 / 18** ✅ (UX + AF M2/M3, вне исходных 143)  
**SSOT индекс:** [`MASTER_STATUS_INDEX.md`](MASTER_STATUS_INDEX.md)  
**Evidence gates:** `docs/release/gates/security-l3-report.json`  
**Трекер:** `.cursor/IMPLEMENTATION_BATCHES_TODO.md`

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
| **R-08…10 Hub demos** | B2-09 B3-08 B4-06 | VPS smokes + guides | ✅ backend · PNG ⏸ device |
| B-QA-03 mock-free | static + 24h | grep 0 + VPS re-run | ✅ PASS |
| **Build 232 supplemental** | AF M2/M3 + UX | код committed + xcodebuild | ✅ PASS · device QA ⏸ |
| xcodebuild | compile | **BUILD SUCCEEDED** 2026-06-13 build **232** | ✅ PASS |
| B-QA-02 Archive | TestFlight 138 | blocked signing cert | ⏸ **единственный блокер 143** |

**Рекомендация:** код 143 + build 232 готовы. Следующая сессия — **Mac + Apple ID**: Archive → TestFlight → device QA Call Directory.

---

## 2. Build 232 supplemental (2026-06-13)

| ID | Описание | Commit / файлы |
|----|----------|----------------|
| `af-m2` | Call Directory extension + App Group sync | `ALADDINCallDirectory/`, `AntifakeCallDirectoryStore` |
| `af-m2` | Post-call local notification → Hub call tab | `AntifakeCallObserverService`, `aladdin://antifake/call-check` |
| `af-m2` | `GET /api/antifake/call-directory` | `app/routers/antifake.py`, `APIService` |
| `af-m3` | История 50 проверок | `AntifakeCheckHistoryStore`, `AntifakeCheckHistorySection` |
| `af-m3` | Quick voice 5 сек | `AntifakeQuickVoiceCaptureView` (вкладка Audio) |
| `qa-bypass` | TEMP Premium bypass для QA Hub | `AntifakeAccessPolicy`, `ANTIFAKE_ALLOW_FREE=1` |
| `ux-1-07` | Аккордеон «Защита от угроз» → Hub | `03_NetworkProtectionScreen.swift` |
| `ux-6-03/05/01b` | Dreams placeholder, coachmark, Values contrast | Wellness screens + LM |
| `ux-8-06` | Reflective prompt sheet | `WellnessReflectiveModeScreen.swift` |
| build | CFBundleVersion **232** | `Info.plist`, `pbxproj`×12, `AppConfig`×2 |

**Git:** `3cfcf256` on `master` · pushed `origin/master`

---

## 3. Автотесты

| Проверка | Результат |
|----------|-----------|
| xcodebuild build 232 | ✅ BUILD SUCCEEDED (2026-06-13) |
| VPS antifake smoke (prior) | ✅ `test_antifake_prod_smoke.py` |
| Mock grep 24h (prior) | ✅ 0 hits |
| Unit tests via scheme | ⏸ prior 62/62 (R-05) |
| Call Directory on device | ⏸ simulator limited |
| simctl install | ⏸ SpringBoard instability Intel sim — use Xcode ⌘R |

---

## 4. План–факт по фазам (143)

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
| 16 | R-19 COPY-POST-L3 | 1 | 1/1 | GATE-K-post |
| 17 | R-08…10 | 3 | 3/3 backend | GATE-FINAL-prep |
| 18 | BATCH QA | 6 | 5/6 | GATE-FINAL ⏸ |
| — | **Осталось** | 6 | R-07 block | Archive |

*Счёт 137 = 143 − 6 (Archive + PNG + walkthrough + sign-off).*

---

## 5. Индекс документов

**→ Главная точка входа:** [`MASTER_STATUS_INDEX.md`](MASTER_STATUS_INDEX.md)

| Категория | Документы |
|-----------|-----------|
| Трекеры | `.cursor/IMPLEMENTATION_BATCHES_TODO.md`, `.cursor/ALADDIN_MASTER_TODO.md`, `.cursor/ANTIFAKE_*` |
| Gates | `gates/security-l3-report.json`, `gates/hub-demo-smoke-report.json` |
| COPY R-19 | `COPY_POST_L3_*.md`, `COPY_01…04_*.md` |
| Archive R-07 | `QA_02_TESTFLIGHT_CHECKLIST.md`, `gates/testflight-build227/` |
| ML | `ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md` §12 |

---

## 6. Перед App Store (build 232)

1. `AntifakeAccessPolicy.bypassPremiumGate = false`
2. VPS: `ANTIFAKE_ALLOW_FREE=0`
3. Call Directory: device QA + Settings → Phone → Call Blocking
4. Выровнять `MARKETING_VERSION` extension `1.0` vs app `1.0.0`
5. R-07 Archive + TestFlight

---

*Audit v1.1 · supersedes `PLAN_FACT_AUDIT_143_2026-06-11.md` · build 232*
