# ALADDIN Family Companion — архитектура и ТЗ

**Дата:** 26 мая 2026  
**Статус:** Superseded by [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md) (финал)  
**TODO:** [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md)  
**Референс продукта:** xAI Grok Companions (Ani / Rudy) — см. обзор в начале чата  
**Персонажи ALADDIN:** [ALADDIN_Character_Bible.md](./ALADDIN_Character_Bible.md) — Аладдин + Единорог  

---

## 1. Простыми словами: что это и зачем

**ALADDIN Companion** — **полноценный AI-компаньон уровня Grok** (голос, текст, эмоции, 3D-герой, память, поиск, картинки, мульти-агент), но с персонажами **Аладдин** и **Единорог** из бренда ALADDIN.

**Не только безопасность:** пользователь может говорить о чём угодно — учёба, игры, хобби, новости, код, творчество, советы, юмор, семья, **плюс** глубокая экспертиза ALADDIN по VPN, угрозам и родительскому контролю (это суперсила, а не единственная тема).

| Grok | ALADDIN Companion (цель 100%) |
|------|-------------------------------|
| Ani / Rudy 3D + голос | Аладдин / Единорог 3D + голос |
| Affection + косметика | Trust / Bond + косметика героя |
| Общий чат + Imagine + Search | То же через API + интеграция в companion UI |
| Multi-agent Heavy | **Весь SFM-зоопарк агентов** (не один психолог) |
| NSFW для взрослых SuperGrok | **Нет откровенного 18+** (семейный бренд, дети в аудитории) — см. §1.1 |
| Запись разговора в приложении | **Не делаем** |
| Push «вернись ко мне» | Умные напоминания + safety, без манипуляций |

**Зачем:** конкурентный продукт «живой друг в телефоне» + уникальная связка с защитой семьи.

### 1.1 Почему «NSFW — нет» (и это не «урезание до безопасности»)

У Grok NSFW — опция для **взрослых** подписчиков SuperGrok (эротика, флирт Ani).  
У ALADDIN в App Store семейный контекст, дети, репутация бренда «защита семьи» → **откровенный 18+ контент юридически и этически нельзя** так же, как Grok.

**Что остаётся «на 100%» без NSFW:**
- любые обычные темы (школа, спорт, мемы, фильмы, рецепты, программирование);
- тёплый флирт/дружба в рамках PG-13 (как Disney+, не как Ani level 5);
- **18+ / NSFW** — backend и `policy_engine` **готовы сразу** (`app_id=aladdin_adult`), но **отдельное приложение**, не бинарник ALADDIN.

**Итог:** полнота Grok = модальности + агенты + companion UX. Эротика — только Adult app через JWT.

**Матрица всех пунктов:** [GROK_FULL_FEATURE_MATRIX.md](./GROK_FULL_FEATURE_MATRIX.md)  
**Общая платформа:** `security/services/ai_platform/`, `security/api/routers/ai_platform_router.py`

---

## 2. Чеклист Grok → ALADDIN (цель 100%, v2)

| Функция Grok | Берём? | ALADDIN (целевое) |
|--------------|--------|-------------------|
| 3D avatar + lip-sync | **Да, полный** | SceneKit/Rive → lip-sync + эмоции (фазы MVP→C) |
| Voice real-time (speech-to-speech) | **Да** | WebSocket voice agent (xAI/OpenAI-compatible или свой) |
| Text chat | **Да** | Есть + companion UI |
| Любые темы разговора | **Да** | General LLM + persona; security — усиленный режим |
| Character personality | **Да** | Аладдин / Единорог + customizable tone |
| Affection / Bond game | **Да** | Trust + Bond levels, квесты, косметика |
| Outfit unlocks | **Да** | Gamification + companion cosmetics API |
| Memory cross-session | **Да** | С export/delete; для детей — parent gate |
| NSFW 18+ | **Нет** | Семейный бренд (§1.1); PG-13 max по умолчанию |
| Web + live search | **Да** | web_search tool (не только KB) |
| X / social search | Опционально | Только если есть legal API; иначе web |
| Image generation (Imagine) | **Да** | Фаза C, family-safe filter |
| Video generation | **Да** | Фаза C, лимиты тарифа |
| Vision / camera | **Да** | Фото экрана, домашки, «что на картинке» |
| PDF / files | **Да** | Как Grok file analysis |
| Code / Canvas | **Да** | Для подростков/родителей; sandbox |
| Multi-agent | **Да, полный** | **Все** server agents via SFM orchestrator |
| Deep reasoning / Think | **Да** | Hermes reasoning mode |
| Custom instructions | **Да** | Per user / per character |
| Workspaces / projects | **Да** | «Комнаты» чатов в приложении |
| Share conversation link | Опционально | Без PII детей |
| Screen recording in app | **Нет** | По решению продукта |
| Push companion | **Да** | Напоминания, streak, safety — без guilt-tripping |
| Switch characters | **Да** | Аладдин ↔ Единорог, отдельная bond history |
| Subscription tiers | **Да** | free / trial / premium лимиты |

---

## 3. Слои системы

```
┌─────────────────────────────────────────────────────────┐
│ iOS: CompanionScreen (hero + chat + voice + trust bar)   │
├─────────────────────────────────────────────────────────┤
│ API: /api/ai/companion/*  (persona, emotion, trust)      │
├─────────────────────────────────────────────────────────┤
│ Shared brain: ai_assistant_router (Hermes, KB RAG, SFM)  │
├─────────────────────────────────────────────────────────┤
│ Safety: PII gate, parental consent, max_ai_messages JWT   │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Персонажи (character_id)

| `character_id` | Имя | Роль в диалоге | Аудитория |
|----------------|-----|----------------|-----------|
| `aladdin` | Аладдин | Наставник, спокойный, объясняет угрозы и настройки | Родитель, подросток |
| `unicorn` | Единорог | Игривый, короткие ответы, поддержка ребёнка | Ребёнок (с parental gate) |

Один активный персонаж на сессию; переключение сохраняет **отдельную** историю trust (не смешивать с romance-механикой Grok).

### Эмоции аватара (`emotion`)

| Код | Когда |
|-----|--------|
| `idle` | Ожидание |
| `listening` | Запись голоса / стрим |
| `thinking` | Запрос на сервере |
| `happy` | Успех, похвала |
| `alert` | Угроза, предупреждение |
| `celebrate` | Достижение / level up trust |
| `comfort` | Поддержка (мягкий тон) |

Сервер возвращает `emotion` + опционально `animation_hint` для клиента.

---

## 5. Trust (вместо Affection)

| Уровень | Баллы | Название | Разблокировка |
|---------|-------|----------|---------------|
| 1 | 0–20 | Знакомство | Базовые эмоции |
| 2 | 21–40 | Друг | +1 cosmetic |
| 3 | 41–60 | Надёжный помощник | Расширенные подсказки |
| 4 | 61–80 | Семейный герой | Косметика «золотое свечение рога» |
| 5 | 81–100 | Хранитель семьи | Все idle-анимации (без NSFW) |

**Начисление:** полезные вопросы о безопасности, выполнение `suggested_actions`, streak без спама.  
**Снятие:** оскорбления, спам, попытки обойти parental controls (логируется, без публичного shame).

---

## 6. Экраны iOS (ТЗ)

### 6.1 `CompanionHubScreen` (точка входа)

- Карточки Аладдин / Единорог (preview из Character Bible)
- Trust bar + уровень
- CTA «Начать разговор»
- Ссылка на настройки: память, согласие родителя, голос

**Навигация:** `NavigationManager` → `.companionHub` (новый case) или таб с Main.

### 6.2 `CompanionConversationScreen`

| Зона | ~% высоты | Содержимое |
|------|-----------|------------|
| Hero | 56% | **Прямоугольная full-body сцена** (`conversationFullBody`), Rive 360×480 |
| Status | overlay | Эмоция + доверие (`heroStatusOverlay`) |
| Dialogue | 28% | **Субтитр** последнего ответа (`CompanionDialogueStrip`), не лента пузырей |
| Input | ~6% | Текст + mic |

**Реализация iOS:** `CompanionHeroLayout` · `CompanionHeroAvatarView` · `CompanionDialogueStrip`.

**Состояния:** loading, streaming, offline (FAQ local только если разрешено политикой).

### 6.2b Adaptive Immersive Layout (AIL) — утверждено 2026-06-04

> **План реализации:** [COMPANION_HERO_IMMERSIVE_IMPLEMENTATION_PLAN.md](./COMPANION_HERO_IMMERSIVE_IMPLEMENTATION_PLAN.md)

§6.2 описывает режим **standard** (56% зоны от GeometryReader «Главное», не от полного экрана; видимый герой при `scaledToFit` ≈ **36%** экрана — см. MASTER §5).

| Режим | hero / chat (GR) | Масштаб | Когда |
|-------|------------------|---------|-------|
| **standard** | 0.56 / 0.28 | fit | Старт, пустой тред |
| **focused** | 0.72 / 0.20 | fit | Есть сообщения (текст) |
| **immersive** | 0.88 / 0.12 | fill, anchor bottom | Голос: listen / think / speak |

**Цель immersive:** видимый герой **~72–75%** высоты экрана; tab bar скрыт на «Главное»; выход — тап верхней зоны / смена вкладки.

**Не менять:** Figma/Rive artboard **360×480**; Hub **96 pt**; Wellness **48 pt**.

### 6.3 `CompanionSettingsScreen`

- Выбор персонажа по умолчанию
- Память: вкл/выкл (только parent role)
- Экспорт / удалить память
- Голос: вкл TTS ответа
- Child mode: только Единорог + укороченные ответы

### 6.4 Фазы UI

| Фаза | Экраны | Avatar |
|------|--------|--------|
| **MVP** | Hub + Conversation | Статичный hero + 6 emotions (assets) |
| **B** | + Voice waveform | Rive state machine + TTS lip-sync lite |
| **C** | + Cosmetics picker | Unlock из API cosmetics |

---

## 7. API контракт `/api/ai/companion/*`

Полная реализация: `security/api/routers/ai_companion_router.py`  
Префикс роутера: `/api/ai/companion`  
Auth: `Authorization: Bearer <JWT>` (как AI Assistant).

### 7.1 `GET /characters`

Список доступных персонажей и фич по тарифу.

**Response 200:**

```json
{
  "characters": [
    {
      "id": "aladdin",
      "display_name": "Аладдин",
      "tagline": "Старший друг и защитник семьи",
      "available": true,
      "min_subscription": "trial"
    },
    {
      "id": "unicorn",
      "display_name": "Единорог",
      "tagline": "Тёплый магический компаньон",
      "available": true,
      "min_subscription": "free"
    }
  ]
}
```

### 7.2 `GET /state?character_id=unicorn`

Текущий trust, cosmetics, consent flags.

**Response 200:**

```json
{
  "character_id": "unicorn",
  "trust_score": 35,
  "trust_level": 2,
  "trust_level_name": "Друг",
  "emotion_default": "idle",
  "cosmetics_unlocked": ["horn_glow_soft"],
  "memory_enabled": false,
  "parent_consent_memory": false,
  "voice_enabled": true,
  "nsfw_blocked": true
}
```

### 7.3 `POST /chat`

**Request:**

```json
{
  "message": "Как включить VPN для ребёнка?",
  "character_id": "aladdin",
  "context": "companion",
  "response_language": "ru",
  "session_id": "uuid-client-session",
  "input_mode": "text"
}
```

`input_mode`: `text` | `voice` (метаданные для аналитики).

**Response 200:**

```json
{
  "response": "…",
  "character_id": "aladdin",
  "emotion": "happy",
  "animation_hint": "nod",
  "trust_delta": 2,
  "trust_score": 37,
  "trust_level": 2,
  "confidence": 0.9,
  "intent": "app_help",
  "grounded": true,
  "sources": ["faq_vpn_child"],
  "tools_used": ["hermes:app_help"],
  "suggested_actions": [
    { "id": "open_parental_controls", "title": "Родительский контроль" }
  ],
  "cosmetic_unlocked": null,
  "nsfw_blocked": true
}
```

Ошибки: `401`, `422` (PII block), `429` (rate limit / `max_ai_messages`), `503` (AI unavailable, **no mock** in prod).

### 7.4 `POST /stream`

Тело как `/chat` + SSE события (совместимо с `ai_assistant/stream`):

| event | payload |
|-------|---------|
| `token` | `{ "text": "…" }` |
| `emotion` | `{ "emotion": "thinking" }` |
| `done` | `ChatMessageResponse`-поля + trust |

### 7.5 `POST /consent`

Только роль parent в JWT / family admin.

**Request:**

```json
{
  "memory_enabled": true,
  "child_can_use_companion": true,
  "allowed_characters": ["unicorn", "aladdin"]
}
```

### 7.6 `GET /memory`

Возвращает redacted summary (не сырой чат).

### 7.7 `DELETE /memory`

Удаляет companion memory для user/family.

### 7.8 `GET /cosmetics?character_id=unicorn`

Список косметики: locked / unlocked.

---

## 8. Связь с существующим AI Assistant

| Companion | Assistant |
|-----------|-----------|
| `POST /api/ai/companion/chat` | Делегирует в `ai_assistant_chat` с `context=companion` + persona prompt |
| `POST /api/ai/assistant/stream` | Companion stream вызывает тот же pipeline |
| Лимиты JWT | Общий счётчик `max_ai_messages` |
| PII | `prepare_for_llm_prompt` / iOS `AIOutboundTextGate` |

**Persona injection (server):** префикс system prompt по `character_id` (см. router `_companion_system_prefix`).

---

## 9. iOS — endpoints в `AppConfig`

```swift
static let aiCompanionCharacters = "/api/ai/companion/characters"
static let aiCompanionState = "/api/ai/companion/state"
static let aiCompanionChat = "/api/ai/companion/chat"
static let aiCompanionStream = "/api/ai/companion/stream"
static let aiCompanionConsent = "/api/ai/companion/consent"
static let aiCompanionMemory = "/api/ai/companion/memory"
static let aiCompanionCosmetics = "/api/ai/companion/cosmetics"
```

Модели Swift: `CompanionChatRequest`, `CompanionChatResponse`, `CompanionStateResponse` (зеркало JSON выше).

---

## 10. Фазы реализации

См. полную привязку пунктов B–H в [GROK_FULL_FEATURE_MATRIX.md](./GROK_FULL_FEATURE_MATRIX.md).

### NOW (инфраструктура — уже начато)

- [x] `ai_platform` (`AppId`, `ContentPolicy`, `policy_engine`, `orchestrator` stub)
- [x] `ai_platform_router` (`/platform/chat`, threads, profile, ephemeral voice token)
- [x] `ai_companion_router` (family-only policy)
- [ ] JWT claims: `app_id`, `age_verified`, `content_policy` в auth
- [ ] Adult app repo (отдельный) — только клиент, тот же API

### MVP (4–6 недель) — ALADDIN app

- [ ] `CompanionConversationScreen` + hero states
- [ ] B1,B2,B5,B6,B8 + F1–F3,F6,F8
- [ ] Threads UI ↔ `GET/POST /platform/threads`

### Phase B

- [ ] B3,B9–B11,C1,C4,C5,D1–D4,D8,D10,E4,E7,F4,F5,F7,H2–H4

### Phase C

- [ ] Остальное из матрицы (Imagine, video, workspaces, canvas, multi-agent 4-head, push)

---

## 11. Безопасность и compliance

- **18+ / NSFW:** hard block в prod; PG-13 default; adult profile 18+ — отдельное ТЗ
- **Дети:** child profile → Единорог, лимиты, parental dashboard
- **Память:** export/delete; child memory — parent consent
- **Mock:** prod reject `sfm_mock` ([AI_ASSISTANT_RESPONSE_SOURCES.md](./AI_ASSISTANT_RESPONSE_SOURCES.md))
- **Запись разговора в приложении:** не реализуем

---

## 12. Деплой

1. `scp` → `/opt/aladdin-backend/security/api/routers/ai_companion_router.py`
2. `main.py`: `include_router(ai_companion_router)`
3. `py_compile` + restart gunicorn (см. `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`)
4. Smoke: `curl -H "Authorization: Bearer …" …/api/ai/companion/characters`

---

## 13. Полный каталог функций Grok

**Источник правды:** [GROK_FULL_FEATURE_MATRIX.md](./GROK_FULL_FEATURE_MATRIX.md) — каждый пункт Grok с ID, фазой, API и статусом.

## 14. Ссылки

- [ALADDIN_Character_Bible.md](./ALADDIN_Character_Bible.md)
- [AI_ASSISTANT_RESPONSE_SOURCES.md](./AI_ASSISTANT_RESPONSE_SOURCES.md)
- xAI Voice Agent: https://docs.x.ai/developers/model-capabilities/audio/voice-agent
- Grok product: https://x.ai/grok
