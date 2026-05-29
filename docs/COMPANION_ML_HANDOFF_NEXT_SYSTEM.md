# Handoff для следующей ML-системы — Companion «доделать до 100%»

**Дата:** 2026-05-29  
**Проект:** ALADDIN Family iOS + backend `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Цель:** довести **90 из 102** задач до рабочего продакшена **без Rive** и **без 12 отложённых QA/gates**.

---

## 0. С чего начать (5 минут)

1. Открой **[COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)** — единый источник цифр **90/102**.  
2. Открой **[COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md)** — пошаговый план этапов 1–5.  
3. Открой **[COMPANION_CODE_TODO_TRACKER.md](./COMPANION_CODE_TODO_TRACKER.md)** — 49 CODE задач (все `[x]` в коде).  
4. Проверь git: `git status` — много файлов Sprint 4–5 **ещё не в push**.  
5. Запусти тесты:

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 -m pytest Tests/test_companion*.py Tests/test_adult_companion_policy.py -q
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

**Твоя задача:** убедиться, что это в commit, на VPS и в TestFlight ≥215.

---

## 2. Что на сервере и в TestFlight

| Место | Что есть |
|-------|----------|
| **GitHub `master` (remote)** | Коммит `771340a3` — **только спринты 1–3**, build 214 |
| **Локальный диск** | Спринты **4–5**, stream-fix, ~15 новых `companion_*.py`, тесты sprint4/5 |
| **aladdin-ai.ru** | Базовый компаньон (как на момент последнего deploy ~27.05). **Нет** `/domains`, `/workspaces`, `/cogs` |
| **TestFlight 214** | Спринты 1–3. **Нет** спринтов 4–5, возможно старая карточка Rewards |

**Вывод:** старый MVP на сервере — **да**. Новые ~20 задач — **нет**, пока не сделаете **commit → deploy → build 215**.

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

### Блок J — Спринт 4 (6) ✅ код / ❌ VPS

| Что | Файл | На VPS |
|-----|------|--------|
| Redis stream cache | `companion_stream_redis.py` | ❌ |
| Orchestrator (флаг) | `_invoke_companion_llm` | ❌ |
| Темы chips | `companion_life_domains.py`, `GET /domains` | ❌ |
| Social bridge | `companion_social_bridge.py` | ❌ |
| Teen playbook | `companion_teen_playbook.py` | ❌ |
| Trust эмпатия | `_trust_delta` | ❌ |

### Блок K — Спринт 5 (14) ✅ код / ❌ VPS / stream исправлен локально

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

## 5. План работ (копия краткая)

См. полный **[COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md)**.

### Этап 1 — Критично

- [x] Stream iOS + BE (в рабочей копии)  
- [ ] `git commit` + `git push`  
- [ ] `deploy_companion_p0.sh` + verify  
- [ ] iOS build **215** → TestFlight  
- [ ] Короткий smoke на iPhone  

### Этап 2 — Блок G

- [ ] Rewards card на TF215  
- [ ] Все входы → `companionHome`  

### Этап 3 — Спринт 4 на VPS

- [ ] Redis env  
- [ ] Проверка `/domains`, social bridge, teen playbook  

### Этап 4 — Спринт 5 MVP

- [ ] PhotosPicker для вложений  
- [ ] UI workspaces в «Моё»  
- [ ] COGS строка для родителя  
- [ ] Дока по поиску-заглушке  

### Этап 5 — Тесты + обновить трекеры

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

1. `master` содержит Sprint 4–5 + stream-fix.  
2. VPS verify PASS; `/domains` отвечает 200 с JWT.  
3. TestFlight ≥215: chips, 60+, режимы, карточка Rewards.  
4. pytest ≥80 passed.  
5. Трекеры обновлены с датой деплоя.  

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
- **Build:** 214 в TF; следующий **215** после Sprint 4–5.  
- **Remote:** `git@github.com:sergey234/ALADDIN_FAMILY.git`, branch `master`.

Удачи. Начни с **Этапа 1** в [COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md).
