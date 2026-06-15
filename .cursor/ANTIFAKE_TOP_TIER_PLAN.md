# Antifake — итоговый план v4.2 (FINAL)

**Версия:** 4.3 · **Дата:** 2026-06-15  
**Build:** 232+ · **iOS min:** 15.2  
**Единая точка входа:** [ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md)  
**SSOT статусов (134):** [ANTIFAKE_V4_TASK_REGISTRY.md](./ANTIFAKE_V4_TASK_REGISTRY.md) (**111 ✅**)  
**Индекс:** [ANTIFAKE_V4_DOC_INDEX.md](./ANTIFAKE_V4_DOC_INDEX.md)  
**Cursor TODO ID:** `af-{TASK-ID}` (пример: `af-D-04`)  
**Контекст:** [ANTIFAKE_MASTER_ROADMAP.md](./ANTIFAKE_MASTER_ROADMAP.md) (архитектура, не ID задач)  
**Prod audit:** 2026-06-14 — SSH `149.154.65.180:8002`

---

## Стратегия (одна фраза)

**Не строим второй Truecaller с миллиардной базой — строим семейный antifake: проверка ссылок / голоса / видео / записи + метки на звонках (iOS 15.2+) + честная privacy; PIR для iOS 18+ — только если решим позже, не условие релиза.**

---

## Решения команды (зафиксировано)

| Тема | Решение |
|------|---------|
| **PIR / OHTTP (Batch H)** | ⏸ **В самый конец.** Пока не решено — делать или нет. На iOS 15.2 не нужно. |
| **G-03 + B-10 + Q-01 (bypass off)** | ✅ **Сделано** — `bypassPremiumGate=false`, `verify_antifake_bypass_off.py` pass |
| **Фокус сейчас** | **Device QA** — D-01…D-04, D-09, E-06, R-02 на real iPhone |
| **Device QA (Archive/TestFlight/iPhone)** | ⬜ **Последний шаг** — xcodebuild + TestFlight + чеклисты |
| **Batch O (Safari filter)** | ❌ **Cancelled** — дублирует Hub URL check + Content Blocker |

---

## Счётчик задач v4 (sync 2026-06-15)

| Статус | Кол-во |
|--------|--------|
| ✅ Done | **111** |
| ⬜ Open | **7** (device QA only) |
| 🟡 In progress | **0** |
| ⏸ Deferred (Ф3) | **13** (H + K) |
| ❌ Cancelled | **3** (O-01…O-03) |
| **Итого** | **134** (**131 активных**) |

**Пропуски ID (намеренно):** A-12, E-04 не используются. D-05 только в Done.

**Детальные статусы каждой строки — только в [REGISTRY](./ANTIFAKE_V4_TASK_REGISTRY.md).**

---

## AI на prod — фактический статус (аудит 15.06.2026)

| Компонент | Статус |
|-----------|--------|
| SFM `:8003` | ✅ `sfm_loaded: true`, BERT/torch в venv (F-13) |
| Worker `aladdin-antifake-worker` | ✅ active, audio/video jobs poll OK |
| Mock guard | ✅ `sfm_mock` отклоняется |
| Smoke + gate af-11 | ✅ pass (`R-03`, `F-05`) |
| call-directory | ✅ ≥113 номеров, delta sync, QA phones (C-batch) |

**Что возвращает API сейчас:**

| Тип | source на prod | Примечание |
|-----|----------------|------------|
| text (golden scam) | `real_agent` | Q-06/Q-07 при healthy SFM |
| url | `local_ml` / rules | эвристики URL |
| audio/video/call | worker + probe | probe **не** → `likely_fake` без ML (F-02/F-11) |

**Итог:** гибрид **real_agent + local_ml + rules**; Batch **B** — hardening (OpenAPI, nginx 25MB, cron TTL, rollback).

---

## Фазы выполнения (единый порядок)

```
ФАЗА 1 — СЕЙЧАС (ядро продукта)
  D → C → A → F → J → B → E → N → R

ФАЗА 2 — УСИЛЕНИЕ (после ядра)
  I → L → M → P → G-marketing → Q

ФАЗА 3 — САМЫЙ КОНЕЦ (решение позже)
  G-03 / B-10 / Q-01 (bypass off) → H (PIR/OHTTP) → K (on-device)

ОТМЕНЕНО
  O (Safari URL filter)
```

---

## Итоговая таблица всех задач

**Легенда:** ✅ готово · 🟡 в работе · ⬜ открыто · ⏸ отложено · ❌ cancelled  
**Cursor TODO:** каждая строка = `af-{ID}` в реестре [ANTIFAKE_V4_TASK_REGISTRY.md](./ANTIFAKE_V4_TASK_REGISTRY.md)

### ✅ BATCH DONE — сделано 14.06.2026 (8)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| A-01 | `af-A-01` | Карточка 3 строки (выбранный copy) | ✅ |
| A-02 | `af-A-02` | «Как включить» sheet (4 шага) | ✅ |
| A-03 | `af-A-03` | Кнопки Call Directory — вертикально | ✅ |
| A-04 | `af-A-04` | Локализованные ошибки sync | ✅ |
| B-01 | `af-B-01` | Deploy `/call-directory` на prod | ✅ |
| D-05 | `af-D-05` | CI profile Call Directory | ✅ |
| E-01 | `af-E-01` | CXCallObserver | ✅ |
| E-02 | `af-E-02` | Local notification после звонка | ✅ |

---

### 🔄 ФАЗА 1 — порядок: D → C → A → F → J → B → E → N → R

#### BATCH D — Call Directory device QA (9)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| D-01 | `af-D-01` | Archive build 232+ | ⬜ |
| D-02 | `af-D-02` | TestFlight → real iPhone | ⬜ |
| D-03 | `af-D-03` | Extension ON → Sync → входящий с test number | ⬜ |
| D-04 | `af-D-04` | Метка «Возможный мошенник?» на экране звонка | ⬜ |
| D-06 | `af-D-06` | QA-документ `ANTIFAKE_CALL_DIRECTORY_DEVICE_QA.md` | ⬜ |
| D-07 | `af-D-07` | Тест blocked[] vs identified[] | ⬜ |
| D-08 | `af-D-08` | Regression: extension OFF → оранжевый статус | ⬜ |
| D-09 | `af-D-09` | Reload после airplane mode | ⬜ |
| D-10 | `af-D-10` | EN locale: метка на английском | ⬜ |

#### BATCH C — Fraud DB (11) ✅

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| C-01 | `af-C-01` | DDL `antifake_scam_numbers` | ✅ |
| C-02 | `af-C-02` | Service `antifake_call_directory_store.py` | ✅ |
| C-03 | `af-C-03` | API только из БД (без seed) | ✅ |
| C-04 | `af-C-04` | Ingest из call analyze + reports | ✅ |
| C-05 | `af-C-05` | CSV import ops | ✅ |
| C-06 | `af-C-06` | iOS: «Синхронизировано N номеров · дата» | ✅ |
| C-07 | `af-C-07` | Unit tests | ✅ |
| C-08 | `af-C-08` | RU feeds ≥100 номеров | ✅ |
| C-09 | `af-C-09` | Delta sync `?since=timestamp` | ✅ |
| C-10 | `af-C-10` | DB rollback + max_entries guard | ✅ |
| C-11 | `af-C-11` | QA test numbers (`source=qa`) для D-03 | ✅ |

#### BATCH A — UX & Copy (10) ✅

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| A-05 | `af-A-05` | Accordion — те же 3 строки что карточка | ✅ |
| A-06 | `af-A-06` | Help/FAQ ← `ANTIFAKE_APPLE_LIMITS_AND_CLAIMS.md` | ✅ |
| A-07 | `af-A-07` | App Store Review Notes (+ P1 limits) | ✅ |
| A-08 | `af-A-08` | Onboarding extension: GIF + retry switches | ✅ |
| A-09 | `af-A-09` | Path iOS 18: Settings → **Apps** → Phone | ✅ |
| A-10 | `af-A-10` | VoiceOver labels | ✅ |
| A-11 | `af-A-11` | CD label EN/RU (не hardcode RU) | ✅ |
| A-13 | `af-A-13` | Call Directory entitlement doc для Review | ✅ |
| A-14 | `af-A-14` | Empty state Hub: честный paywall | ✅ |
| A-15 | `af-A-15` | Media tabs honesty copy (probe ≠ deepfake ML) | ✅ |

#### BATCH F — Настоящий AI (12) + ML-100% ✅

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| F-01 | `af-F-01` | SFM 422 purge + restart | ✅ |
| F-02 | `af-F-02` | Video worker; probe DoD | ✅ |
| F-03 | `af-F-03` | Call recording full pipeline | ✅ |
| F-04 | `af-F-04` | Latency SLA + progress UX | ✅ |
| F-05 | `af-F-05` | af-11 prod gate pass | ✅ |
| F-06 | `af-F-06` | Metrics dashboard | ✅ |
| F-07 | `af-F-07` | Model versioning + rollback | ✅ |
| F-08 | `af-F-08` | Golden RU/EN — obvious scam `likely_fake` | ✅ |
| F-09 | `af-F-09` | 25MB iOS/API/nginx + UI hint | ✅ |
| F-10 | `af-F-10` | Badge «AI» / «Правила» | ✅ |
| F-11 | `af-F-11` | Audio worker probe hint only | ✅ |
| F-12 | `af-F-12` | Tier-2 local_ml + heuristic | ✅ |
| F-13 | `af-F-13` | torch+transformers prod → `real_agent` | ✅ |
| F-14 | `af-F-14` | SFM systemd grace 15s | ✅ |
| B-11 | `af-B-11` | Smoke `/api/sfm/status` | ✅ |
| Q-07 | `af-Q-07` | sfm_loaded → golden `real_agent` | ✅ |
| P-06 | `af-P-06` | Runbook SFM degraded / OOM | ✅ |

#### BATCH J — Понятный результат (5)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| J-01 | `af-J-01` | Verdict card v2: confidence bar + top-3 reasons | ✅ |
| J-02 | `af-J-02` | Disclaimer inline «не юридическое заключение» | ✅ |
| J-03 | `af-J-03` | «Что делать дальше» per verdict | ✅ |
| J-04 | `af-J-04` | History export PDF (P2) | ⬜ |
| J-05 | `af-J-05` | Spoof hints UI (caller_id vs display_name) | ✅ |

#### BATCH B — Backend prod (8) ⬜ **СЕЙЧАС**

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| B-02 | `af-B-02` | call-directory в smoke script | ✅ |
| B-03 | `af-B-03` | OpenAPI media routes | ✅ |
| B-04 | `af-B-04` | Redis/RQ worker — verify jobs | ✅ |
| B-05 | `af-B-05` | Persistent `antifake_jobs` PostgreSQL | ✅ |
| B-06 | `af-B-06` | nginx **25MB** + timeout | ✅ |
| B-07 | `af-B-07` | Deploy script + rollback | ✅ |
| B-08 | `af-B-08` | Media TTL 15 min + cron | ✅ |
| B-09 | `af-B-09` | Rate limit + iOS 429 UX | ✅ |

#### BATCH E — Post-call (5)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| E-03 | `af-E-03` | Tap push → Hub «Звонок» | ✅ |
| E-05 | `af-E-05` | Toggle «напоминать после звонка» | ✅ |
| E-06 | `af-E-06` | Device QA post-call | ⬜ |
| E-07 | `af-E-07` | Prefill caller_id from last call | ✅ |
| E-08 | `af-E-08` | Cooldown 1 push / 15 min | ✅ |

#### BATCH N — Privacy (5)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| N-01 | `af-N-01` | `PrivacyInfo.xcprivacy` main + extensions | ✅ |
| N-02 | `af-N-02` | Hash phone in logs/local history | ✅ |
| N-03 | `af-N-03` | Delete antifake data on account delete | ✅ |
| N-04 | `af-N-04` | Privacy policy section antifake | ✅ |
| N-05 | `af-N-05` | Consent before first media upload | ✅ |

#### BATCH R — Release checklist (3)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| R-01 | `af-R-01` | Чеклист TestFlight + static gate `verify_antifake_release_readiness.py` | ✅ |
| R-02 | `af-R-02` | QA sign-off: скрин метки + sync N (device; infra ready) | ⬜ |
| R-03 | `af-R-03` | Prod smoke pass on VPS (+ Q-06) | ✅ |

---

### ⬜ ФАЗА 2 — I → L → M → P → G → Q

#### BATCH I — Crowd reports (8)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| I-01 | `af-I-01` | UI «Сообщить о мошеннике» | ✅ |
| I-02 | `af-I-02` | API + moderation queue | ✅ |
| I-03 | `af-I-03` | Ingest → fraud DB | ✅ |
| I-04 | `af-I-04` | Label default, block only high confidence | ✅ |
| I-05 | `af-I-05` | Whitelist contacts | ✅ |
| I-06 | `af-I-06` | Appeal «не мошенник» | ✅ |
| I-07 | `af-I-07` | Rate limit reports | ✅ |
| I-08 | `af-I-08` | Report only after completed check | ✅ |

#### BATCH L — Family moat (5)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| L-01 | `af-L-01` | Parent push: child `likely_fake` | ✅ |
| L-02 | `af-L-02` | Elderly one-tap «проверить звонок» | ✅ |
| L-03 | `af-L-03` | Family shared scam reports | ✅ |
| L-04 | `af-L-04` | Onboarding + FAQ alignment | ✅ |
| L-05 | `af-L-05` | Parent dashboard CD status (P2) | ✅ |

#### BATCH M — Security (5) ✅

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| M-01 | `af-M-01` | TLS pinning antifake API | ✅ |
| M-02 | `af-M-02` | Funnel metrics enable→sync→check | ✅ |
| M-03 | `af-M-03` | Pen-test upload/SSRF | ✅ |
| M-04 | `af-M-04` | PII-safe logging | ✅ |
| M-05 | `af-M-05` | Secret scan App Group | ✅ |

#### BATCH P — Ops & SRE (5)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| P-06 | `af-P-06` | Runbook SFM degraded / OOM | ✅ |
| P-01 | `af-P-01` | Alert job failure >5% (`antifake_ops_alerts.py`) | ✅ |
| P-02 | `af-P-02` | Alert queue depth >50 | ✅ |
| P-03 | `af-P-03` | Runbook worker OOM + SFM 422 | ✅ |
| P-04 | `af-P-04` | Mass false positive DB rollback | ✅ |
| P-05 | `af-P-05` | Post-deploy checklist | ✅ |

#### BATCH G — Marketing (6) · G-03 только в Ф3

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| G-01 | `af-G-01` | No «real-time all calls» marketing gate | ✅ |
| G-02 | `af-G-02` | Landing + kb sync | ✅ |
| G-04 | `af-G-04` | Premium paywall honest limits | ✅ |
| G-05 | `af-G-05` | App Privacy labels | ✅ |
| G-06 | `af-G-06` | Comparison vs Truecaller (P2 doc) | ✅ |
| G-07 | `af-G-07` | Policy: no contact harvest | ✅ |

#### BATCH Q — Release gates (5) · Q-01 только в Ф3

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| Q-02 | `af-Q-02` | XCUITest Hub 4 tabs | ✅ |
| Q-03 | `af-Q-03` | Contract test call-directory JSON | ✅ |
| Q-04 | `af-Q-04` | TestFlight beta criteria | ✅ |
| Q-05 | `af-Q-05` | Pre-submit grep: no mock strings | ✅ |
| Q-06 | `af-Q-06` | Smoke: golden scam → `real_agent`\|`local_ml` | ✅ |

---

### ⏸ ФАЗА 3 — САМЫЙ КОНЕЦ

#### Bypass off (3)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| G-03 | `af-G-03` | iOS: `bypassPremiumGate = false` | ⏸ |
| B-10 | `af-B-10` | Server: `ANTIFAKE_ALLOW_FREE=0` + smoke secret | ✅ |
| Q-01 | `af-Q-01` | CI assert bypass off on release branch | ⏸ |

**Сейчас:** server bypass OFF · iOS bypass ON (`bypassPremiumGate=true`) — для QA Hub.

#### BATCH H — PIR / OHTTP (10)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| H-01 | `af-H-01` | Spike Apple PIR + Privacy Pass | ⏸ |
| H-02 | `af-H-02` | Backend PIR server | ⏸ |
| H-03 | `af-H-03` | iOS LiveCallerIDLookup extension | ⏸ |
| H-04 | `af-H-04` | Fallback PIR → Call Directory | ⏸ |
| H-05 | `af-H-05` | Min iOS 18 gate UI | ⏸ |
| H-06 | `af-H-06` | 2nd extension evaluate | ⏸ |
| H-07 | `af-H-07` | BGAppRefresh auto-sync | ⏸ |
| H-08 | `af-H-08` | CD entry limits perf | ⏸ |
| H-09 | `af-H-09` | Apple OHTTP relay request | ⏸ |
| H-10 | `af-H-10` | PIR ops → P-03 runbook | ⏸ |

#### BATCH K — On-device (3)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| K-01 | `af-K-01` | CoreML voice classifier research | ⏸ |
| K-02 | `af-K-02` | UI toggle «Проверить на устройстве» | ⏸ |
| K-03 | `af-K-03` | On-device uncertain → cloud check | ⏸ |

#### BATCH O — ❌ cancelled (3)

| ID | Cursor | Задача | Статус |
|----|--------|--------|--------|
| O-01 | `af-O-01` | Safari URL filter research | ❌ |
| O-02 | `af-O-02` | NEURLFilter implementation | ❌ |
| O-03 | `af-O-03` | Hub integration | ❌ |

---

## Definition of Done v4.2 (без G-03 и H)

### Must — TestFlight + точность

- [ ] D-04 · [x] C-03 + C-08 · [x] F-01 + F-12 + F-10 · [x] F-08 · [x] Q-06 · [x] F-05/R-03 · [x] J-03 + J-05 · [ ] E-03 + E-06 · [x] A-05 + A-09 + A-11 · [x] B-02 · [x] N-01 · 9 routes green · [x] R-01

### Must — Apple Review

- [x] A-06 + A-07 + A-13 + A-15 + [x] G-01 + [x] G-04 + [x] G-05 + [x] N-01 + N-05 + [x] J-02 + [x] A-14 + [x] Q-05

### Later — App Store Premium

- [ ] G-03 + Q-01 (B-10 server ✅)

### Optional — PIR

- [ ] Batch H (iOS 18+ only)

### Не для v1 (Apple reject)

- Фоновый PSTN · auto-hangup · FaceTime intercept · «100% все мошенники»

---

## Приоритет — порядок работы

| # | Batch | Cursor batch | Простым языком |
|---|-------|--------------|----------------|
| 1 | **D** | `af-D-*` | iPhone → extension → sync → **метка** |
| 2 | **C** | `af-C-*` | ✅ Fraud DB |
| 3 | **A** | `af-A-*` | ✅ Тексты, iOS 18, EN/RU |
| 4 | **F** | `af-F-*` | ✅ SFM + ML-100% + probe DoD |
| 5 | **J** | `af-J-*` | ✅ кроме J-04 P2 |
| 6 | **B** | `af-B-*` | ⬜ **СЕЙЧАС** — smoke, worker, 25MB, TTL |
| 7 | **E** | `af-E-*` | Push → Hub |
| 8 | **N** | `af-N-*` | Privacy manifest |
| 9 | **R** | `af-R-*` | Чеклист TestFlight |
| 10 | **I,L,M,P,G,Q** | `af-I-*` … | Усиление после ядра |
| **∞** | **G-03, H, K** | `af-G-03` … | **Конец очереди** |

---

## Cursor TODO — 134 задачи (131 активных)

**Полный список:** [ANTIFAKE_V4_TASK_REGISTRY.md](./ANTIFAKE_V4_TASK_REGISTRY.md) · **Индекс docs:** [ANTIFAKE_V4_DOC_INDEX.md](./ANTIFAKE_V4_DOC_INDEX.md)

| Формат ID | Пример | Статус в Cursor |
|-----------|--------|-----------------|
| `af-{TASK-ID}` | `af-D-04` | pending / completed / cancelled |

**Новые v4.2:** `af-F-12`, `af-Q-06`, `af-A-15`

**Старые batch-todo (deprecated):** `af-batch-d`, `af-batch-c` … заменены на **129 granular todos** `af-A-01` … `af-O-03`.

*Обновлять реестр + план + Cursor todo при закрытии каждого ID.*

---

## Prod audit snapshot (15.06.2026)

| Endpoint | Premium smoke | source / факт |
|----------|---------------|----------------|
| `/call-directory` | 200, ≥113 | PostgreSQL + CSV |
| `/check/text` (golden) | 200 | **real_agent** (Q-07) |
| `/check/url` | 200 | local_ml / rules |
| `/check/audio` + poll | 202→completed | worker; probe DoD |
| SFM `/api/sfm/status` | 200 | `sfm_loaded: true` |
| Gate af-11 | pass | F-05 |
| Server bypass | OFF | B-10 ✅ |
| iOS bypass | ON (`bypassPremiumGate=true`) | G-03 ⏸ |

---

## Связь с другими документами

| Документ | Роль |
|----------|------|
| **ANTIFAKE_V4_TASK_REGISTRY.md** | SSOT — 134 задач + Cursor ID |
| **ANTIFAKE_V4_DOC_INDEX.md** | Карта всех документов antifake v4 |
| **ANTIFAKE_TOP_TIER_PLAN.md** | План v4.2 (этот файл) |
| ANTIFAKE_MASTER_ROADMAP.md | Архитектура, компоненты (старые af-* ID) |
| IMPLEMENTATION_BATCHES_TODO.md | BATCH 2 iOS (R-07, B2-09 — другая нумерация) |
| ANTIFAKE_PRODUCTION_TODO.md | Legacy af-1…af-11 бэклог |
