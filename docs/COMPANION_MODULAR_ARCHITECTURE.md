# Архитектура компаньона — модульная (простыми словами)

**Версия:** 1.0  
**Связь:** [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md)

---

## 1. Какой тип архитектуры

**Модульная гибридная:**

| Часть | Тип | Зачем |
|-------|-----|-------|
| **Backend** | Модули (плагины) + общее ядро | Включить/выключить поиск, голос, картинки без переписывания чата |
| **iOS** | Слои UI + сервисы | Можно убрать голос, оставить текст; поменять Rive на PNG |
| **Данные** | Один «мозг» (orchestrator) | Все модули сходятся в одну точку — не разъезжается логика |

**Не монолит:** фича = отдельный файл/роутер/флаг.  
**Не микросервисы:** пока один VPS, один процесс FastAPI — проще и дешевле.

---

## 2. Картина целиком (кто с кем говорит)

```
┌─────────────────────────────────────────────────────────────┐
│  ПОЛЬЗОВАТЕЛЬ (ребёнок / родитель)                           │
└───────────────┬─────────────────────────┬───────────────────┘
                │                         │
        ┌───────▼────────┐        ┌───────▼────────┐
        │  Kids / Игры   │        │  ALADDIN Main  │
        │  Companion UI  │        │  AI Assistant  │
        └───────┬────────┘        └───────┬────────┘
                │                         │
                │    ┌────────────────────┘
                │    │
        ┌───────▼────▼───────────────────────────────────────┐
        │  iOS СЛОЙ ПРИЛОЖЕНИЯ                                  │
        │  • CompanionViewModel (чат + голос + trust UI)        │
        │  • CompanionVoiceSession (только WebSocket аудио)   │
        │  • AIAssistantViewModel (старый чат — не трогаем)     │
        └───────┬────────────────────────────────────────────┘
                │ HTTPS / WSS + JWT
        ┌───────▼────────────────────────────────────────────┐
        │  API ШЛЮЗ (FastAPI)                                 │
        │  /companion/*  /assistant/*  /platform/*  /voice/*  │
        └───────┬────────────────────────────────────────────┘
                │
        ┌───────▼────────────────────────────────────────────┐
        │  ЯДРО ПЛАТФОРМЫ (ai_platform)                        │
        │  ① policy_engine — возраст, NSFW, лимиты            │
        │  ② orchestrator — куда направить запрос             │
        │  ③ usage_meters — сколько потратили                 │
        └───────┬────────────────────────────────────────────┘
                │
     ┌──────────┼──────────┬─────────────┬──────────────┐
     ▼          ▼          ▼             ▼              ▼
 ┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
 │ Модуль │ │ Модуль │ │ Модуль  │ │ Модуль   │ │ Модуль   │
 │  Чат   │ │ Голос  │ │ Поиск   │ │ Память   │ │ Персонаж │
 │ Hermes │ │  WS    │ │  web    │ │ threads  │ │ trust    │
 │ SFM KB │ │ TTS    │ │ (P2)    │ │ (P1)     │ │ cosmetics│
 └────────┘ └────────┘ └─────────┘ └──────────┘ └──────────┘
                │
        ┌───────▼────────────────────────────────────────────┐
        │  Postgres / Redis                                   │
        └────────────────────────────────────────────────────┘
```

---

## 3. Модули backend (включаются флагами)

Конфиг: `security/services/ai_platform/feature_flags.py`  
Реестр: `security/services/ai_platform/modules/registry.py`

| Модуль | Файл | Env-флаг | Фаза |
|--------|------|----------|------|
| `chat` | `modules/chat_core.py` | `FEATURE_CHAT_CORE` | P0 |
| `voice_realtime` | `modules/voice_realtime.py` | `FEATURE_VOICE_ENABLED` | P0 |
| `companion` | `modules/companion.py` | `FEATURE_COMPANION_ENABLED` | P0 |
| `web_search` | `modules/web_search.py` | `FEATURE_WEB_SEARCH_ENABLED` | P2 |
| + новые | `modules/your_feature.py` | `FEATURE_*` | по плану |

**Как добавить фичу:**
1. Создать класс от `PlatformModule` в `modules/`.
2. `register_module(YourModule())` в registry.
3. Env `FEATURE_YOUR=true`.
4. iOS увидит через `GET /capabilities` — без релиза приложения для скрытия кнопки.

**Как убрать:** `FEATURE_VOICE_ENABLED=false` → capabilities `voice_realtime.enabled=false` → iOS скрывает mic.

---

## 3.1 Контракт модуля (`PlatformModule`)

Файл: `security/services/ai_platform/modules/base.py`

| Метод | Назначение |
|-------|------------|
| `module_id` | Ключ в JSON capabilities |
| `enabled(ctx)` | Включён ли для user/age_band |
| `capability_fragment(ctx)` | `{ enabled, ui, limits }` для iOS |
| `before_chat(ctx, message)` | Вернуть строку = заблокировать |
| `after_chat(ctx, result)` | Обогатить ответ (опционально) |

**Контекст `ModuleContext`:** `user_id`, `app_id`, `age_band`, `content_policy`, `subscription_level`, `character_id`.

---

## 3.2 Capabilities API (для iOS)

| Метод | URL |
|-------|-----|
| GET | `/api/ai/platform/capabilities` |
| GET | `/api/ai/companion/capabilities` (то же для Kids) |

**Пример ответа:**

```json
{
  "app_id": "aladdin_family",
  "age_band": "child",
  "content_policy": "family_pg13",
  "subscription_level": "premium",
  "limits": { "max_ai_messages": 1000, "voice_minutes_month": 120 },
  "characters": ["unicorn"],
  "features": {
    "chat": { "enabled": true, "ui": { "text_input": true, "streaming": true } },
    "voice_realtime": { "enabled": true, "ui": { "mic_button": true, "realtime_websocket": true } },
    "companion": { "enabled": true, "ui": { "hub_visible": true, "trust_bar": true } },
    "web_search": { "enabled": false, "ui": { "attach_search_badge": false } }
  }
}
```

**iOS:** при старте экрана Companion → `GET capabilities` → показать/скрыть mic, trust bar, персонажей.

---

## 4. Поток одного сообщения (текст)

1. Ребёнок печатает в Kids → iOS шлёт `POST /companion/chat` + JWT (`age_band=child`).  
2. **policy_engine** — можно ли вообще отвечать? не NSFW? не превышен лимит?  
3. **usage_meters** — +1 сообщение.  
4. **orchestrator** — добавляет persona Единорога, выбирает: KB → Hermes → SFM.  
5. Ответ + `emotion` + `trust_delta` → iOS меняет лицо персонажа.

---

## 5. Поток голоса (realtime, P0)

1. iOS запрашивает `POST /voice/ephemeral-token`.  
2. Открывает `WSS /voice/realtime` с токеном (без API key на телефоне).  
3. Сервер: микрофон → STT → тот же **orchestrator** → TTS → аудио обратно.  
4. Параллельно iOS получает события `emotion: listening | thinking | speaking`.  
5. **usage_meters** — + секунды голоса.

Текст и голос — **один мозг**, два транспорта.

---

## 6. Модули iOS

```
Core/
  Companion/
    CompanionAPIClient.swift      ← только HTTP к /companion
    CompanionVoiceClient.swift    ← только WSS (можно выключить сборкой)
    CompanionPolicyCache.swift   ← age_band, лимиты с JWT
ViewModels/
  CompanionViewModel.swift        ← связует чат + голос + trust
Screens/Companion/
  CompanionHubScreen.swift
  CompanionConversationScreen.swift
```

**Модульность:** нет голоса → не линкуем `CompanionVoiceClient`, UI без кнопки mic.

---

## 7. Возраст — один переключатель на всё

`age_band` в JWT → **policy_engine** режет:

| band | Голос | Темы | Персонаж | Память |
|------|-------|------|----------|--------|
| child | да | мягко | только Единорог | только с согласия |
| teen | да | PG-13 | оба | с согласия |
| parent | да | полно | Аладдин | настройка |
| adult_app | да | adult policy | Adult app | своя БД |

Один раз настроили policy — все модули читают одно решение.

---

## 8. Два приложения — один backend

| JWT `app_id` | UI | NSFW |
|--------------|-----|------|
| `aladdin_family` | ALADDIN + Kids | выкл |
| `aladdin_adult` | Adult app (позже) | по политике 18+ |

Код NSFW уже в **policy_engine**; в ALADDIN binary этого экрана нет.

---

## 9. Где что лежит в репозитории

| Что | Путь |
|-----|------|
| Ядро | `security/services/ai_platform/` |
| Флаги | `ai_platform/feature_flags.py` |
| Контракт модуля | `ai_platform/modules/base.py` |
| Реестр модулей | `ai_platform/modules/registry.py` |
| Capabilities | `ai_platform/capabilities.py` |
| Роутеры | `ai_companion_router.py`, `ai_platform_router.py` |
| iOS capabilities | `CompanionCapabilitiesService` (создать P0-17) |
| iOS UI | `Screens/Companion/` (создать) |
| План | `docs/COMPANION_MASTER_PLAN_v1.md` |
| TODO | `docs/COMPANION_IMPLEMENTATION_TODOS.md` |

---

## 10. Почему потом легко расширять

- Новая фича = **новый модуль** + флаг + 1 строка в orchestrator.  
- Не нравится Rive → меняем только `CompanionHeroView`.  
- Выключаем web search на проде → env без деплоя iOS.  
- Adult app → новый `app_id`, те же роуты.

*Это и есть «модульная гибридная» архитектура для компаньона.*
