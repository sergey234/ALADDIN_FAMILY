# Runbook для следующей ML-системы — Этап 2 (Sprint 4) и Этап 3 (Sprint 5)

**Обновлено:** 2026-05-29  
**Канонический репозиторий:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Связанные документы:** [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md) · [COMPANION_PLAN_TO_100_PERCENT.md](./COMPANION_PLAN_TO_100_PERCENT.md) · [COMPANION_CURSOR_TODO_STAGE2_3.md](./COMPANION_CURSOR_TODO_STAGE2_3.md) · [GATE-OPS signoff](./COMPANION_GATE_OPS_SIGNOFF_2026-05-29.md) · [ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md)

---

## Статус на сегодня (что уже сделано)

| Шаг | Статус | Детали |
|-----|--------|--------|
| Код Sprint 4–5 + stream-fix | ✅ | `master` коммит **`351a9b03`**, build **215** в трёх файлах |
| Деплой VPS | ✅ | `deploy_companion_p0.sh` → `149.154.65.180`, сервис **active** |
| Verify прод | ✅ | `verify_companion_p0_prod.sh` — 17 шагов, 3 героя всем, `/domains`, `/cogs`, `/workspaces` |
| Verify-скрипт 3 героя | ⏳ | правки в `scripts/verify_companion_p0_prod.sh` — **закоммитить** если ещё локально |
| TestFlight 215 + smoke device | ✅ | В TestFlight и на тестовом iPhone (2026-05-29, PO) |
| Этап 2 Sprint 4 MVP | ✅ | VPS + verify 18; iOS в **build 216** |
| Этап 3 Sprint 5 MVP | ✅ код | **TestFlight 216** для COGS/вложений на device |

**Не начинать без PO:** HERO-3-07 (production `.riv`), GATE-DIALOG, Rive pipeline, 12 отложённых QA.

---

## С чего начать (10 минут)

1. Прочитать **§0** в [COMPANION_ML_HANDOFF_NEXT_SYSTEM.md](./COMPANION_ML_HANDOFF_NEXT_SYSTEM.md).  
2. Убедиться в git: `git log -1` → `351a9b03` или новее.  
3. Прогнать verify (должен быть **exit 0**):

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```

4. Если есть незакоммиченный `verify_companion_p0_prod.sh` — commit + push.  
5. ~~TestFlight 215~~ ✅ (2026-05-29).  
6. Выполнять таблицы **Этап 2**, затем **Этап 3** по порядку (сейчас: Redis 4.1, orchestrator 4.2, E2E 4.4–4.6, Sprint 5 UI).

---

## Этап 2 — Sprint 4 (6 пунктов) → 100% MVP

Код уже на **aladdin-ai.ru**. Задача — включить конфиг, проверить E2E, довести iOS.

| # | Пункт | Сейчас | Действие для 100% MVP | Файлы / проверка | Готово? |
|---|--------|--------|------------------------|------------------|---------|
| 4.1 | **Redis stream cache** | ✅ redis на VPS | `COMPANION_STREAM_CACHE_BACKEND=redis`, `REDIS_URL=redis://127.0.0.1:6379/0` (2026-05-29). | `companion_stream_redis.py`, `companion_store.py` | ✅ |
| 4.2 | **Оркестратор** | ✅ `=1` на VPS | Smoke: verify 18 OK. Откатить в `0` при регрессии LLM. | `_invoke_companion_llm`, `feature_flags.py` | ✅ |
| 4.3 | **Темы chips** | API ✅ · device TF215 ✅ | chips из `GET /domains` над полем ввода | `companion_life_domains.py` | ✅ |
| 4.4 | **Social bridge** | ✅ verify **18** | Fix: `social_bridge` в profile persist. E2E: 2× «одиноко» → `show_social_bridge: true`. | `companion_social_bridge.py` | ✅ |
| 4.5 | **Teen playbook** | ✅ pytest | `pytest Tests/test_companion_sprint4.py` | `companion_teen_playbook.py` | ✅ |
| 4.6 | **Trust за эмпатию** | ✅ | `trust_delta` в meta + «+N к доверию» в UI (216) | `_trust_delta` | ✅ |

**Postgres:** полная миграция **не блокер** «100% без Rive». Остаётся **SQLite** + опционально **Redis** для stream resume.

### Команды VPS (Этап 2)

```bash
# SSH (см. ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md)
ssh -o IdentitiesOnly=yes -i ~/.ssh/aladdin_server root@149.154.65.180

# Проверить Redis (если уже установлен)
redis-cli ping

# Добавить в .env (пример — подставьте реальный REDIS_URL)
cd /opt/aladdin-backend
grep -q COMPANION_STREAM_CACHE_BACKEND .env || cat >> .env <<'EOF'
COMPANION_STREAM_CACHE_BACKEND=redis
REDIS_URL=redis://127.0.0.1:6379/0
EOF
# Опционально orchestrator:
# COMPANION_USE_ORCHESTRATOR=1

systemctl restart aladdin-backend.service
systemctl is-active aladdin-backend.service
```

Повторный verify с Mac:

```bash
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```

---

## Этап 3 — Sprint 5 (14 пунктов) → 100% MVP

| # | Пункт | MVP 100% (делать) | Не сейчас | Файлы iOS / BE | Готово? |
|---|--------|-------------------|-----------|----------------|---------|
| 5.1 | **Поиск + ссылки** | Включить `FEATURE_WEB_SEARCH_ENABLED=1` на VPS **или** оставить `0` и дописать в `docs/` «MVP = citations-заглушка». Verify: ответ с `citations` при флаге. | Реальный Search API | `companion_web_search.py` | ⏳ |
| 5.2 | **Режимы fast/think** | TF215: меню режима (teen+). Stream шлёт `chat_mode` (verify шаг **12b** ✅). Device: «быстрый» vs «вдумчивый» — разная длина/таймаут. | — | `CompanionStreamingService.swift`, Conversation menu | ⏳ device |
| 5.3 | **Фото/PDF** | `ImagePickerView` (iOS 15.2+) + PDF importer → stream. BE: `companion_attachments.py`. | Vision model | `CompanionConversationScreen` | ✅ код · TF216 |
| 5.4 | **Trust streak** | Показать `trust_streak_days` из stream `done` meta (ключ l10n `companion_trust_streak` уже есть). | — | `CompanionConversationScreen` overlay | ⏳ UI |
| 5.5 | **Семья в промпте** | Убедиться, что **stream path** вызывает тот же `_companion_chat_core`, что и `/chat` (family hint не только на `/chat`). | — | `companion_family_context.py`, router stream | ⏳ audit |
| 5.6 | **Tools list** | Показать `tools_used` в debug/родительском «Моё» (опционально). BE отдаёт поле. | Полный OpenAI Responses | `companion_responses_tools.py` | ⏳ |
| 5.7 | **COGS** | Карточка в **«Моё»** родителя (`CompanionMineTabView`). | Биллинг-dashboard | `fetchCogs` | ✅ код · ⏳ TF после bump |
| 5.8 | **60+ с Main** | TF215: карточка на `01_MainScreen.swift` → companion senior. | — | `01_MainScreen.swift` | ⏳ TF |
| 5.9 | **Картинки/видео** | Дока: stub, `FEATURE_IMAGE_GEN_ENABLED=0`. Не обещать в UI. | Генерация | `companion_media_gen.py`, `COMPANION_IMPLEMENTATION_TODOS.md` | ⏳ doc |
| 5.10 | **Workspaces** | Список + создать в «Моё»; `workspace_id` в stream (`AppStorage`). API ✅. | Полный folders UX | `CompanionMineTabView` | ✅ код · ⏳ TF |
| 5.11 | **Длинный контекст** | Recap в промпте при >24 сообщениях в thread (логи/ручной тест длинного диалога). | LLM summarization | `companion_long_context.py` | ⏳ |
| 5.12 | **Android** | Док актуален | Отдельное репо | `docs/android/COMPANION_ANDROID_STUB.md` | ✅ doc |
| 5.13 | **Adult** | Док + тесты | Отдельное приложение | `docs/adult/`, `test_adult_companion_policy.py` | ✅ doc/tests |
| 5.14 | **Policy adult NSFW** | pytest green | — | `Tests/test_adult_companion_policy.py` | ✅ |

```bash
python3 -m pytest Tests/test_companion_sprint5.py Tests/test_adult_companion_policy.py -q
```

---

## Этап 2b — Блок G «Мир героев» (параллельно с Sprint 4)

| # | Задача | Критерий 100% |
|---|--------|----------------|
| G.1 | Карточка Rewards | TF215: «Мир героев» видна **родителю и ребёнку** (`ChildRewardsScreen.swift`) |
| G.2 | Входы | Kids → Друзья / питомец / legacy → `companionHome` |
| G.3 | Mic | Coach первого запуска, hold-only для child |

---

## Карта кода (главное)

| Область | Путь |
|---------|------|
| Router (все API) | `security/api/routers/ai_companion_router.py` |
| Sprint 4–5 модули | `security/services/ai_platform/companion_*.py` |
| Stream iOS (главный чат) | `Core/Network/CompanionStreamingService.swift` |
| Conversation UI | `Screens/CompanionConversationScreen.swift` |
| Блок G | `Screens/ChildRewardsScreen.swift`, `08_ChildInterfaceScreen.swift` |
| 60+ вход | `Screens/01_MainScreen.swift` |
| Деплой | `scripts/deploy_companion_p0.sh` |
| Verify | `scripts/verify_companion_p0_prod.sh` |

---

## Env на VPS (шпаргалка)

| Переменная | Значение для MVP | Заметка |
|------------|------------------|---------|
| `COMPANION_STREAM_CACHE_BACKEND` | `redis` | Этап 2.1 |
| `REDIS_URL` | `redis://…` | Обязателен с redis backend |
| `COMPANION_USE_ORCHESTRATOR` | `0` → `1` для smoke | Этап 2.2 |
| `FEATURE_WEB_SEARCH_ENABLED` | `0` или `1` + дока | Этап 5.1 |
| `FEATURE_IMAGE_GEN_ENABLED` | `0` | Stub |
| `FEATURE_WORKSPACES_ENABLED` | `1` при UI папок | Этап 5.10 |
| `COMPANION_STORE_BACKEND` | `sqlite` | Postgres — отдельный проект |

---

## Критерий «Этап 2 + 3 закрыты»

- [x] Redis stream cache на проде  
- [x] Orchestrator smoke (`COMPANION_USE_ORCHESTRATOR=1`)  
- [x] TF215: chips, режимы, Rewards — smoke OK  
- [x] Social bridge E2E (verify шаг 18)  
- [x] Вложения в коде (галерея iOS 15.2 + PDF)  
- [x] COGS + workspaces UI в «Моё» (код build **216**)  
- [x] `verify_companion_p0_prod.sh` exit 0 (**18** шагов)  
- [x] Трекеры обновлены · [ ] **TestFlight 216** на device  

---

## Порядок приоритетов (рекомендация PO)

1. **TestFlight 215** (без этого пользователи не видят Sprint 4–5 в iOS).  
2. **Этап 2.3** chips на device.  
3. **Этап 2.1** Redis на VPS.  
4. **Этап 3.2–3.3** режимы + вложения на device.  
5. **Этап 3.7 + 5.10** COGS + workspaces UI.  
6. Остальное по таблице.

Удачи. Вопросы по SSH — [ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md).
