# Handoff для следующей ML-системы — Companion «доделать до 100%»

**Дата:** 2026-05-29 (после деплоя Sprint 4–5)  
**Проект:** ALADDIN Family iOS + backend `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Цель:** довести **90 из 102** задач до рабочего продакшена **без Rive** и **без 12 отложённых QA/gates**.  
**Runbook Этап 2–3:** [COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md) ← **главный список «что делать дальше»**

---

## 0. С чего начать (следующая ML-система)

**Рабочая папка (единственная):**  
`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Git:** `git@github.com:sergey234/ALADDIN_FAMILY.git`, ветка **`master`**

| Шаг | Действие |
|-----|----------|
| 1 | [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) — цифры **90/102** |
| 2 | **[COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md)** — Sprint 4 и 5 по пунктам |
| 3 | [COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md) — этапы 1–5 и чеклисты |
| 4 | [ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md) — SSH, VPS |
| 5 | Verify прод (должен быть exit 0): `./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru` |
| 6 | **Не начинать** Rive 07, GATE-DIALOG без запроса PO |

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 -m pytest Tests/test_companion*.py Tests/test_adult_companion_policy.py -q
./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```

---

## 1. Главная проблема (прочитать обязательно)

**Пользователь пишет в чат через поток (stream), а не через обычный POST /chat.**

До 2026-05-29 в stream **не передавались** поля:

- режим ответа (`chat_mode`: быстрый / вдумчивый / глубокий)
- вложения (`attachments`)
- папка чата (`workspace_id`)

Поэтому спринты 4–5 на сервере **есть в коде**, но в **обычном чате в приложении** частично не работали.

**Исправление (уже в рабочей копии):**

- iOS: `Core/Network/CompanionStreamingService.swift` — поля в JSON body  
- iOS: `Screens/CompanionConversationScreen.swift` — передаёт `chatMode`, `attachments`  
- Backend: `CompanionStreamRequest` + `companion_stream()` → полный `CompanionChatRequest`

**Статус:** исправление в **`351a9b03`** (master), на VPS после deploy 2026-05-29, в iOS после **TestFlight 215**.

---

## 2. Что на сервере и в TestFlight (актуально)

| Место | Что есть |
|-------|----------|
| **GitHub `master`** | **`351a9b03`** — Sprint 4–5, stream-fix, build **215** |
| **aladdin-ai.ru (VPS)** | ✅ Deploy Sprint 4–5: `/domains`, `/workspaces`, `/cogs`, обновлённый router |
| **Verify прод** | ✅ `verify_companion_p0_prod.sh` — 17 шагов, политика **3 героя всем** |
| **TestFlight** | ✅ **215** smoke · ⏳ **216** (COGS, папки, вложения, trust UI) |
| **Этап 2–3** | ✅ код+VPS — [runbook](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md) · **102 осталось:** [WHAT_REMAINS](./COMPANION_WHAT_REMAINS.md) |

**Вывод:** backend Sprint 4–5 на проде — **да**. «100% без Rive» — после **TF215 + этапы 2–3** из runbook.

### Команды деплоя

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/deploy_companion_p0.sh root <HOST> ~/.ssh/aladdin_server
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```

---

## 3. Список ~90 сделанных задач (простым языком)

### Блок A — Базовый MVP (19) ✅ на сервере

Чтобы чат, голос, лимиты и безопасность вообще работали.

| № | Простыми словами | Ключевые файлы |
|---|------------------|----------------|
| 1–2 | Вход с возрастом; правила для детей | `jwt_claims.py`, `policy_engine.py`, `age_policy.py` |
| 3 | База доверия, история, лимиты | `companion_store.py` |
| 4–5 | Голос по сети + временный токен | `ai_voice_ws_router.py` |
| 6–9 | API + iOS экраны + голосовая сессия | `ai_companion_router.py`, `Companion*Screen` |
| 10–13 | Эмоции, детский вход, PII, лимиты | эмоции, navigation, gates |
| 14–19 | Тесты, деплой, модули, capabilities | `test_companion_p0_smoke.py`, `feature_flags.py` |

### Блок B — Функции чата (11) ✅

| № | Простыми словами | Файлы |
|---|------------------|-------|
| 20 | История диалогов | threads API |
| 21–22 | Согласие родителя, память | consent, memory |
| 23–26 | Характер, лайки, stream resume, косметика | profile, feedback |
| 27 | Подготовка Rive (placeholder) | Rive SPM |
| 28–30 | Правила, аналитика, баннер лимита | legal, analytics, usage banner |

### Блок C — «Живой» компаньон (6) ✅

| № | Простыми словами | Файлы |
|---|------------------|-------|
| 31–36 | Этика, жизнь не только VPN, темы/настроение, возраст, эксперт-режим, эмоции | `companion_ethics.py`, `companion_persona.py`, `companion_intent_router.py` |

### Блок D — Операции (4) ✅

Деплой, verify, алерт стоимости LLM, чеклист OPS.

### Блок E — Три героя (24/26) ✅ код / ⏳ Rive prod

🦄🧑🧞 всем, Figma, placeholder `.riv`, iOS Hub — **готово**.  
**Не в 90% «готово на 100%»:** production `.riv` aladdin+genie, device QA 11b/11c.

### Блок F — Продакшен (11/12) ✅

Голос, XCUITest, модерация после LLM, 429, l10n, offline, ADR.  
**Открыто:** полный Postgres (сейчас SQLite + Redis опционально).

### Блок G — UX «Мир героев» (17) ✅ в коде / ⏳ TF

| № | Что | Файл |
|---|-----|------|
| 74–76 | Три героя BE/iOS/голос | см. блок E |
| 77–78 | Карточка Rewards, текст 🦄🧑🧞 | `ChildRewardsScreen.swift` |
| 79–82 | Друзья, питомец, legacy→Home | `08_ChildInterfaceScreen`, `UnicornPetView`, nav |
| 83–85 | Mic coach, hold, busy assistant | `CompanionConversationScreen` |
| 86 | Чистый overlay ребёнка | `heroStatusOverlay` |
| 87–88 | RU/EN, VoiceOver | `LocalizationManager` |

**Доделать до 100%:** карточка в **TestFlight 215** (сейчас фикс может быть только локально).

### Блок H — Спринт 2 (4) ✅ iOS

Голос polish, полная l10n, a11y, offline.

### Блок I — Спринт 3 (5) ✅

XCUITest, 429, post-LLM moderation, ADR, App Store doc.

### Блок J — Спринт 4 (6) ✅ код + VPS / ⏳ MVP 100%

| Что | Файл | VPS код | MVP 100% |
|-----|------|---------|----------|
| Redis stream cache | `companion_stream_redis.py` | ✅ | ⏳ env `redis` |
| Orchestrator (флаг) | `_invoke_companion_llm` | ✅ | ⏳ smoke `ORCHESTRATOR=1` |
| Темы chips | `GET /domains` | ✅ | ⏳ iOS TF215 |
| Social bridge | `companion_social_bridge.py` | ✅ | ⏳ E2E meta |
| Teen playbook | `companion_teen_playbook.py` | ✅ | ⏳ pytest + manual |
| Trust эмпатия | `_trust_delta` | ✅ | ⏳ UI trust_delta |

### Блок K — Спринт 5 (14) ✅ код + VPS / ⏳ MVP 100%

| Что | Файл |
|-----|------|
| Поиск-заглушка | `companion_web_search.py` |
| Режимы ответа | `chat_mode` + iOS Menu |
| Вложения | `companion_attachments.py` |
| Trust decay | `companion_trust_decay.py` |
| Семья в промпте | `companion_family_context.py` |
| Tools | `companion_responses_tools.py` |
| COGS | `companion_cogs.py`, `GET /cogs` |
| 60+ Main | `01_MainScreen.swift` |
| Media stub | `companion_media_gen.py` |
| Workspaces API | `companion_workspaces.py` |
| Long context recap | `companion_long_context.py` |
| Android / Adult docs | `docs/android/`, `docs/adult/` |
| Adult policy tests | `Tests/test_adult_companion_policy.py` |

### Блок L — iOS стабильность POL-01…12 ✅ builds 213–214

Кэш API, микрофон tap+hold, STT fixes, карточка «Мир героев».

---

## 4. Что НЕ делать (12 отложённых)

PO просил **не трогать** в этом цикле:

1. Production Rive `.riv` ×3 (HERO-3-07)  
2. Device QA STT/TTS (11b)  
3. MIMIC после production riv (11c)  
4. UX-14b (эмоции только анимацией)  
5. Figma↔Rive pipeline (P2-09)  
6. A/B humor genie+teen (P2-17)  
7–12. GATE-P0, GATE-EMO, GATE-DIALOG, GATE-DIALOG-REGRESS, и др.

---

## 5. План работ — что делать дальше

| Этап | Документ | Статус |
|------|----------|--------|
| **1** Критично (git, deploy, 215) | [PLAN §3](./COMPANION_PLAN_TO_100_PERCENT.md) | ✅ git+deploy+verify+TF215+smoke |
| **2** Sprint 4 (6 пунктов) | **[STAGE2/3 RUNBOOK](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md)** § Sprint 4 | ⏳ |
| **3** Sprint 5 (14 пунктов) | **[STAGE2/3 RUNBOOK](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md)** § Sprint 5 | ⏳ |
| **2b** Блок G «Мир героев» | RUNBOOK § G | ⏳ device TF215 |
| **5** Тесты + трекеры | PLAN §7 | ⏳ |

### Этап 1 — закрыто / осталось

- [x] Stream iOS + BE  
- [x] `git push` → `351a9b03`, build **215**  
- [x] `deploy_companion_p0.sh` + verify (17 шагов)  
- [x] **TestFlight 215** + smoke: Друзья → чат → chips → режим (2026-05-29)  

### Этап 2 — Sprint 4 (кратко; детали в runbook)

| Пункт | Действие MVP |
|-------|----------------|
| Redis | `COMPANION_STREAM_CACHE_BACKEND=redis` + `REDIS_URL` на VPS |
| Orchestrator | staging: `COMPANION_USE_ORCHESTRATOR=1` + smoke |
| Chips | domains на проде ✅ · iOS `fetchLifeDomains` + TF215 |
| Social bridge | E2E: 2× «одиноко» → `show_social_bridge` в meta |
| Teen playbook | `pytest test_companion_sprint4` + teen JWT manual |
| Trust эмпатия | `trust_delta` в stream `done` meta + UI |

**Postgres** — не блокер; SQLite + Redis.

### Этап 3 — Sprint 5 (кратко; детали в runbook)

| Пункт | MVP 100% | Не сейчас |
|-------|----------|-----------|
| Поиск | флаг + дока «MVP citations» | реальный Search API |
| Режимы | stream + меню + разница на device | — |
| Фото/PDF | PhotosPicker + BE validate | vision |
| Trust streak | UI из `done` meta | — |
| Семья в промпте | stream path = chat path | — |
| COGS | строка в «Моё» родителя | биллинг |
| Workspaces | UI список/создать | полный UX |
| Картинки/видео | stub, flag off в доке | генерация |
| Long context | recap >24 msg | LLM summary |
| Android/Adult | доки ✅ | отдельные репо |

---

## 6. Ключевые файлы (карта репозитория)

```
security/api/routers/ai_companion_router.py   # все HTTP endpoints
security/services/ai_platform/
  companion_*.py                              # Sprint 4–5 модули
  companion_store.py                          # SQLite MVP
  feature_flags.py                            # FEATURE_* env
Core/Network/CompanionStreamingService.swift  # ГЛАВНЫЙ путь чата
Screens/CompanionConversationScreen.swift
Screens/CompanionHomeScreen.swift
Screens/ChildRewardsScreen.swift              # карточка «Мир героев»
Screens/01_MainScreen.swift                   # 60+
Screens/08_ChildInterfaceScreen.swift         # «Друзья»
Tests/test_companion_sprint4.py
Tests/test_companion_sprint5.py
scripts/deploy_companion_p0.sh
scripts/verify_companion_p0_prod.sh
```

---

## 7. Переменные окружения (prod)

| Переменная | Назначение | По умолчанию |
|------------|------------|--------------|
| `COMPANION_USE_ORCHESTRATOR` | Несколько агентов | `0` |
| `FEATURE_WEB_SEARCH_ENABLED` | Псевдо-поиск + ссылки | `0` |
| `COMPANION_STREAM_CACHE_BACKEND` | `redis` или `sqlite` | `sqlite` |
| `REDIS_URL` | Redis для stream cache | — |
| `COMPANION_STORE_BACKEND` | `postgres` → warning, SQLite | `sqlite` |
| `FEATURE_IMAGE_GEN_ENABLED` | Stub картинок | `0` |
| `FEATURE_WORKSPACES_ENABLED` | Workspaces module | `0` |

---

## 8. Критерии приёмки «100% без Rive»

1. [x] `master` содержит Sprint 4–5 + stream-fix (`351a9b03`).  
2. [x] VPS verify PASS; `/domains`, `/cogs`, `/workspaces` 200 с JWT.  
3. [ ] TestFlight **215**: chips, 60+, режимы, карточка Rewards на device.  
4. [ ] Sprint 4: 6/6 MVP (runbook).  
5. [ ] Sprint 5: 14/14 MVP (stubs задокументированы).  
6. [ ] pytest companion зелёный; трекеры с датой деплоя.  

---

## 9. Другие документы (читать по необходимости)

| Документ | Зачем |
|----------|-------|
| [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md) | Общий продуктовый план |
| [COMPANION_CODE_PLAN_NO_RIVE.md](./COMPANION_CODE_PLAN_NO_RIVE.md) | Спринты 0–5 без Rive |
| [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md) | Детали по ID |
| [COMPANION_TASKS_WITHOUT_RIVE.md](./COMPANION_TASKS_WITHOUT_RIVE.md) | Что без Rive |
| [COMPANION_UNIFIED_HOME_UX.md](./COMPANION_UNIFIED_HOME_UX.md) | UX входы |
| [docs/adr/ADR-P1-16-companion-hot-path.md](./adr/ADR-P1-16-companion-hot-path.md) | chat vs stream |
| [docs/adult/ADULT_COMPANION_OPENAPI.md](./adult/ADULT_COMPANION_OPENAPI.md) | Adult API |
| [docs/android/COMPANION_ANDROID_STUB.md](./android/COMPANION_ANDROID_STUB.md) | Android checklist |

---

## 10. Контакты контекста

- **PO:** 3 героя (🦄🧑🧞) для всех; карточка «Мир героев» только сверху Rewards (не в сетке игр).  
- **Build:** **215** в git; загрузить в TestFlight.  
- **VPS deploy:** 2026-05-29, `149.154.65.180`, `/opt/aladdin-backend`.  
- **Remote:** `git@github.com:sergey234/ALADDIN_FAMILY.git`, branch `master`.

**Начни здесь:** [COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md](./COMPANION_ML_STAGE2_STAGE3_RUNBOOK.md) → TestFlight 215 → таблицы Sprint 4 и 5.
