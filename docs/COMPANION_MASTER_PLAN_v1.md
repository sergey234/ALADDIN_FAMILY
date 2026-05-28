# ALADDIN Companion Platform — Master Plan v1.0 (FINAL)

**Дата:** 26 мая 2026  
**Статус:** Утверждён к реализации (обсуждение закрыто)  
**Аудитория:** iOS, backend, ML/AI, QA, product, **внешние ML-системы** (handoff)  
**Репозиторий iOS:** `/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
**Связанные файлы:**
- [COMPANION_MODULAR_ARCHITECTURE.md](./COMPANION_MODULAR_ARCHITECTURE.md) — **модульная архитектура, потоки, флаги**
- [COMPANION_RIVE_CONNECT_NODE_MCP.md](./COMPANION_RIVE_CONNECT_NODE_MCP.md) — **HERO-3-07: Rive Editor, Node, RiveMCP (2026-05-28)**
- [COMPANION_ML_HANDOFF_2026-05-28.md](./COMPANION_ML_HANDOFF_2026-05-28.md) — handoff для внешней ML-системы
- [COMPANION_PLAN_TOMORROW_2026-05-29.md](./COMPANION_PLAN_TOMORROW_2026-05-29.md) — план следующей сессии
- [GROK_FULL_FEATURE_MATRIX.md](./GROK_FULL_FEATURE_MATRIX.md) — трассировка 90+ ID
- [GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md](./GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md) — API companion
- Код: `security/services/ai_platform/`, `security/api/routers/ai_platform_router.py`, `ai_companion_router.py`

---

## 0. Как читать этот документ (для другой ML-системы)

1. **Цель продукта** — §1  
2. **Где что живёт** (Family / Kids / Adult) — §2  
3. **Возрастные полосы** — §3  
4. **Что НЕ делаем** — §4  
5. **Приоритеты P0→P3 и фазы** — §5 (главная дорожная карта)  
6. **Текущее состояние кода** — §6  
7. **Спринты по неделям** — §7  
8. **Голос realtime в MVP** — §8  
9. **Бизнес-рамка L–N** — §9  
10. **Метрики успеха** — §10  
11. **Чеклист задач** — §11 + [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md)

**Правило:** не начинать Phase C, пока не зелёные метрики §10 после MVP.

---

## 1. Что строим и зачем

**ALADDIN Companion Platform** — backend и клиенты для AI-компаньона уровня Grok:

- говорит и слушает (**двусторонний realtime voice с MVP**);
- текст, память, threads, эмоции 3D/2.5D персонажа;
- любые темы **с фильтром по возрасту**;
- суперсила ALADDIN: security, VPN, семья, угрозы.

| Поверхность | Пользователь | Персонажи | NSFW |
|-------------|--------------|-----------|------|
| **ALADDIN Family (Main)** | Родитель 18+ | AI Assistant (без 3D) | Нет |
| **Kids / Игры** | Child / Teen | Аладдин, Единорог | Нет |
| **Adult app (отдельно)** | 18+ verified | TBD (не в ALADDIN binary) | Только там |

**Два входа, один мозг:** Assistant на Main **не заменяется**; Companion — в **Kids/играх**.

---

## 2. Архитектура (как выглядит в проде)

```
┌─────────────────────────────────────────────────────────────────┐
│ ALADDIN Family iOS          │  Kids / Games module (тот же repo) │
│ • AI Assistant screen       │  • CompanionHub + Conversation    │
│ • security, VPN             │  • Hero + Trust + Voice realtime  │
└──────────────┬──────────────┴──────────────────┬──────────────────┘
               │                                  │
               ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ API Gateway :8002                                                │
│  /api/ai/assistant/*   /api/ai/companion/*   /api/ai/platform/* │
│  /api/ai/voice/realtime (WebSocket)                              │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ ai_platform: policy_engine (age_band, app_id) → orchestrator     │
│ → Hermes / SFM / KB RAG / specialist agents                      │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Postgres/Redis: threads, trust, memory, profile, usage meters  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Adult iOS (ОТДЕЛЬНЫЙ репозиторий / target — ПОСЛЕ PMF Family)    │
│ JWT app_id=aladdin_adult, age_verified=true                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Возрастные полосы (Age bands) — блок O

| `age_band` | Возраст | Где UI | Персонажи | Темы | Память |
|------------|---------|--------|-----------|------|--------|
| `child` | до 12 (родитель задал) | Kids | **только Единорог** | PG, коротко, без личных данных | Только с `parent_consent` |
| `teen` | 13–17 | Kids | Единорог / Аладдин | PG-13, без 18+ | Consent + export/delete |
| `parent` | 18+ | Family + Kids опционально | Аладдин | Полный + security | По настройке |
| `adult_app` | 18+ verified | **Adult app only** | Adult personas | Политика Adult | Отдельная DB partition |

**JWT (целевой):**

```json
{
  "sub": "user-uuid",
  "app_id": "aladdin_family",
  "age_band": "child",
  "age_verified": false,
  "content_policy": "family_pg13",
  "parent_consent": { "memory": true, "companion": true },
  "subscription": { "level": "premium", "limits": { "max_ai_messages": 1000, "voice_minutes_month": 120 } }
}
```

---

## 4. Исключения (Removed — не в roadmap Family/Kids)

| ID | Функция | Причина |
|----|---------|---------|
| F11 | Запись разговора | Приватность детей |
| B14 | Публичная ссылка на чат | Утечка переписки |
| D5 | Клон голоса | Deepfake / legal |
| C3 | X Search | Нет экосистемы X |
| A4,E9,E10,G4 | X embed, Build, Computer, X bundle | Не наш продукт |
| A6 | Tesla / telephony | B2B xAI |
| E8 | 4-head agents | Достаточно E7 orchestrator |
| B13 | Canvas | Низкий ROI mobile family |
| F12 | Push guilt «вернись» | Только **safety push** |
| J5 | Telegram в companion | Отдельный канал поддержки |

---

## 5. Приоритеты реализации (что в первую, вторую, третью очередь)

### P0 — Спринт 1 (недели 1–3) «Фундамент + Kids companion + realtime voice»

**Цель:** ребёнок/подросток открывает Kids → говорит с Единорогом → слышит ответ в realtime.

| # | Задача | ID | Выход |
|---|--------|-----|-------|
| P0.1 | JWT: `app_id`, `age_band`, `parent_consent`, voice limits | I1, O | auth issue token |
| P0.2 | `policy_engine` + prompts по age_band | O, I6 | block 18+ в family |
| P0.3 | Postgres/Redis: trust, threads (не RAM) | B6, F6 | persistence |
| P0.4 | WebSocket voice realtime server path | D1,D2,H3 | `WS /api/ai/voice/realtime` |
| P0.5 | iOS Kids: `CompanionHub` + `CompanionConversation` | F1–F3 | UI |
| P0.6 | iOS: WebSocket voice client + lip-sync lite | F4,F5,D2 | mic ↔ speaker |
| P0.7 | Companion chat/stream + persona | B1,B2,F8 | `/companion/chat` |
| P0.8 | Ephemeral token для WS | H6,I1 | без API key на device |
| P0.9 | PII gate + no mock prod | I2,I3 | compliance |
| P0.10 | Smoke tests + deploy VPS | K1,K2 | CI green |
| P0.11 | Unit economics meters (voice min, msgs) | L1 | usage table |
| P0.12 | **modules/** + `PlatformModule` контракт | — | `modules/base.py`, registry |
| P0.13 | **GET /capabilities** platform + companion | — | iOS без хардкода кнопок |
| P0.14 | iOS `CompanionCapabilitiesService` | — | mic/trust/characters из API |

*Нумерация в [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md): P0-16..P0-18 — модули и capabilities.*

### P1 — Спринт 2 (недели 4–6) «Качество диалога + родитель»

| # | Задача | ID |
|---|--------|-----|
| P1.1 | Threads UI + history list | B5,B6 |
| P1.2 | Parent consent screen → API | I5 |
| P1.3 | Memory GET/DELETE + UI | B11,I5 |
| P1.4 | Custom instructions/profile | B9,B10 |
| P1.5 | Feedback + suggested actions | B15,B17 |
| P1.6 | Stream resume | B16 |
| P1.7 | Trust cosmetics unlock | F7 |
| P1.8 | Rive emotion state machine | F5 |
| P1.9 | Legal strings + privacy manifest | M1–M5 |
| P1.10 | Metrics events (analytics) | N1–N5 |

### P2 — Phase B (недели 7–14) «Grok parity core»

| # | Задача | ID |
|---|--------|-----|
| P2.1 | Web search tool + citations | C1,C4,C5 |
| P2.2 | Multi-agent orchestrator (all server agents) | E7,J2 |
| P2.3 | Fast/Reasoning/Think modes | B3 |
| P2.4 | Vision + PDF upload | D8,D10 |
| P2.5 | STT/TTS REST fallback | D3,D4 |
| P2.6 | Bond decay / streak | F13 |
| P2.7 | Gamification ↔ cosmetics | J3 |
| P2.8 | Family context in prompts | J4 |
| P2.9 | Platform Responses API + tools | H2 |
| P2.10 | COGS alerts vs revenue | L2,L3 |

### P3 — Phase C (недели 15+) «Расширение»

Image/video gen (D11,D12), workspaces (B12), long context (B4), sync web (B7), Android (A3), Adult app Store (F10,F14), DeepSearch (C2), MCP (E5), video input (D9), priority tier (G3).

### Adult app — параллельно только backend до PMF

| Когда | Что |
|-------|-----|
| **Сейчас (P0)** | `policy_engine` adult path, OpenAPI, JWT schema |
| **После PMF Family** | Отдельный iOS target, Store, personas, NSFW UI |

---

## 6. Где остановились (состояние на 26.05.2026)

| Компонент | Статус | Файл |
|-----------|--------|------|
| Companion API stub | 🟡 | `security/api/routers/ai_companion_router.py` |
| Platform API stub | 🟡 | `security/api/routers/ai_platform_router.py` |
| policy_engine | 🟡 | `security/services/ai_platform/policy_engine.py` |
| orchestrator stub | 🟡 | `security/services/ai_platform/orchestrator.py` |
| AI Assistant chat/stream | 🟡 | `ai_assistant_router.py`, `AIAssistantViewModel` |
| JWT age_band | ❌ | нужен `app/auth` |
| Voice WebSocket server | ❌ | P0.4 |
| Kids Companion UI | ❌ | P0.5 |
| Postgres trust/threads | ❌ | P0.3 |
| Ephemeral voice token | 🟡 stub | `ai_platform_router` |

**Следующий шаг для ML/dev:** начать **P0.1 → P0.4 → P0.5** (параллельно backend + iOS).

---

## 7. Голос: двусторонний realtime в MVP (решение зафиксировано)

| Слой | Реализация |
|------|------------|
| Transport | `wss://…/api/ai/voice/realtime` (OpenAI Realtime-совместимый или xAI) |
| Auth | `POST /api/ai/voice/ephemeral-token` → клиент без secret |
| Turn-taking | Server VAD |
| iOS | `CompanionVoiceSession` → WS + AVAudioEngine |
| Avatar | `listening` / `thinking` / `speaking` + lip-sync lite (амплитуда) |
| Fallback | Если WS недоступен → STT REST + chat + TTS REST (не silent fail) |

**Не откладываем voice на Phase B** — polish (latency, 5 голосов, clone) в Phase B.

---

## 8. Блок L — Unit economics

| ID | Требование | Фаза |
|----|------------|------|
| L1 | Счётчики: `ai_messages`, `voice_seconds`, `image_gen` per user/month | P0 |
| L2 | Лимиты в JWT: `max_ai_messages`, `voice_minutes_month` | P0 |
| L3 | Алерт COGS: если LLM+voice cost > X% MRR (manual threshold) | P2 |
| L4 | Тарифная сетка в админке / config | P1 |
| L5 | Soft cap: предупреждение 80% лимита в UI | P1 |

---

## 9. Блок M — Legal / privacy

| ID | Требование | Фаза |
|----|------------|------|
| M1 | Child companion: явное согласие родителя (UI + API) | P1 |
| M2 | Политика: что хранится в memory (redacted summary only) | P1 |
| M3 | Export/delete memory и threads (GDPR-style) | P1 |
| M4 | Age band в оферте + App Store privacy labels | P1 |
| M5 | Legal sign-off checklist (внутренний doc) | P1 |
| M6 | Логирование без сырого child PII | P0 |

---

## 10. Блок N — Metrics MVP

| ID | Метрика | Цель MVP (пример) |
|----|---------|-------------------|
| N1 | D7 retention (открыли Kids companion) | > 25% |
| N2 | Среднее msgs/user/week в companion | > 8 |
| N3 | % users с 3+ sessions/week | > 20% |
| N4 | Voice session completion rate | > 70% |
| N5 | Trial → paid conversion (companion users) | baseline +10% vs non |
| N6 | Incident: policy block rate | monitor, не PR-скандал |

События: `companion_open`, `companion_message`, `voice_start`, `voice_end`, `trust_level_up`, `policy_blocked`.

---

## 11. API quick reference

| Method | Path | P0 |
|--------|------|-----|
| GET | `/api/ai/companion/characters` | ✅ |
| GET | `/api/ai/companion/state` | ✅ |
| POST | `/api/ai/companion/chat` | ✅ |
| POST | `/api/ai/companion/stream` | ✅ |
| POST | `/api/ai/companion/consent` | P1 |
| GET/DELETE | `/api/ai/companion/memory` | P1 |
| POST | `/api/ai/platform/chat` | ✅ |
| GET/POST | `/api/ai/platform/threads` | P1 |
| PUT | `/api/ai/platform/profile` | P1 |
| POST | `/api/ai/voice/ephemeral-token` | ✅ |
| WS | `/api/ai/voice/realtime` | ✅ |

---

## 12. iOS структура (новые файлы — целевые)

```
Screens/Companion/
  CompanionHubScreen.swift
  CompanionConversationScreen.swift
  CompanionSettingsScreen.swift
ViewModels/
  CompanionViewModel.swift
  CompanionVoiceSession.swift
Core/Models/
  CompanionModels.swift
Core/Config/AppConfig.swift  // endpoints уже добавлены
```

**Навигация:** Kids/Games module → `.companionHub` (не заменять `aiAssistant` на Main).

---

## 13. Definition of Done — MVP (P0+P1)

- [ ] Child с `parent_consent` говорит с Единорогом через **realtime WS**
- [ ] Teen/Parent age_band работает, NSFW block 100% в family JWT
- [ ] Trust персистится в DB
- [ ] Нет mock в prod; PII gate
- [ ] L1/L2 meters пишут usage
- [ ] M1–M4 в сторе/политике
- [ ] N1–N4 события в аналитике
- [ ] K2 smoke green на VPS

---

## 14. Handoff checklist для другой ML-системы

1. Прочитать §6 — что уже есть в коде.  
2. Взять задачи из [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md) со статусом `pending`.  
3. Не менять `app_id=aladdin_family` для включения NSFW.  
4. Voice: сначала ephemeral token, потом WS; ключи только на сервере.  
5. Деплой: `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`.  
6. После P0 — обновить §6 и todo-файл.

---

*Конец Master Plan v1.0*
