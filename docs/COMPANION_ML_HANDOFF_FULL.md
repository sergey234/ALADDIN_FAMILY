# Companion Platform — полная передача дел следующей ML-системе

> **⚠️ Актуальный handoff (2026-05-27):** [COMPANION_ML_HANDOFF_2026-05-27.md](./COMPANION_ML_HANDOFF_2026-05-27.md)  
> Этот файл — расширенная справка (SSH, BE, история). Счётчики и TODO смотри в трекере.

**Дата handoff:** 2026-05-26  
**Рабочий корень iOS + backend-кода Companion:**  
`/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

**Прогресс спринта:** **25 / 68** задач (37%) · блок **CX** (универсальный компаньон): **0 / 6** · **P0: 19/19** · **P1: 6/11** · **P1+: 0/12** · **OPS: 0/4** · **P2–P3, Adult: 0**

**Вне scope (отменено):** **X-06** push «вернись к Единорогу» · **X-07** ежедневный backup БД

**Цель:** production + App Store + Grok parity — закрытие только при **BE + iOS + Test + Prod = ✅** (§15–17).

**Следующие задачи:** **OPS-01** (деплой P1-04…06) → **P1-07** (косметика iOS)

---

## 1. Что мы реализуем (продукт)

**Companion Platform** — детский AI-компаньон в приложении ALADDIN Family (iOS): персонажи **Единорог** / **Аладин**, текстовый чат, голос в реальном времени (MVP), trust-прогресс, родительское согласие, память, история диалогов (threads), стриминг ответов с **resume после обрыва сети**.

Цель — безопасный аналог Grok для детей (COPPA / 152-ФЗ), **отдельно** от взрослого Assistant на Main.

| Слой | Технологии |
|------|------------|
| Backend | FastAPI на VPS `:8002`, путь `/opt/aladdin-backend` |
| Данные P0 | **SQLite** `companion_platform.db` (не Postgres пока) |
| iOS | SwiftUI, `CompanionAPIService`, `CompanionStreamingService`, WebSocket голос |
| Прод-домен | `https://aladdin-ai.ru` → nginx → `127.0.0.1:8002` |
| IP сервера | `149.154.65.180` |

**Важно:** на том же IP есть **другой** продукт — Telegram Shop Bot в `/opt/aladdin-telegram-shop-bot`. **Не деплоить Companion туда.**

---

## 2. Легенда статусов (обязательно для каждой задачи)

| Символ | Значение |
|--------|----------|
| **✅** | Реализовано и пригодно к использованию |
| **🟡** | Stub / MVP / частично (есть код, но не production-complete) |
| **❌** | Нет или не подключено |

Колонки в таблицах задач:

- **BE** — backend (Python в `security/`)
- **iOS** — Swift UI / сервисы
- **Test** — автотесты
- **Prod** — выкат на `aladdin-ai.ru` (нужен SSH-ключ)

**«Спринт готово»** в `COMPANION_IMPLEMENTATION_TODOS.md` = задача закрыта по scope спринта, но отдельные слои могут оставаться **🟡** (например SQLite вместо Postgres).

---

## 3. Счётчики и два списка задач

| Список | Кол-во | Файл |
|--------|--------|------|
| **Спринтовые задачи (Cursor TODO)** | **68** активных + **7** отменённых (X) | `docs/COMPANION_IMPLEMENTATION_TODOS.md` |
| **CX — жизнь, возрасты, одиночество** | **6** (P1-25…P1-30) | § CX в TODOS + **§19–20** здесь |
| **Матрица Grok (трассировка)** | **102** строки | `docs/GROK_FULL_FEATURE_MATRIX.md` |

**102 ≠ 47:** одна спринтовая задача закрывает несколько ID матрицы (например P1-03 → B11 и др.).

---

## 4. Ключевые документы (читать в этом порядке)

| Документ | Абсолютный путь | Зачем |
|----------|-----------------|-------|
| **Подключение к серверу** | `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` | SSH, IP, `/opt/aladdin-backend`, nginx WS, health |
| **Деплой Companion** | `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/COMPANION_DEPLOY_P0.md` | Env, nginx voice, verify |
| **Список задач спринта** | `.../docs/COMPANION_IMPLEMENTATION_TODOS.md` | 47 ID, прогресс |
| **Мастер-план** | `.../docs/COMPANION_MASTER_PLAN_v1.md` | Roadmap, эндпоинты |
| **Модульная архитектура** | `.../docs/COMPANION_MODULAR_ARCHITECTURE.md` | PlatformModule, registry |
| **Архитектура Grok→ALADDIN** | `.../docs/GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md` | Сопоставление фич |
| **Матрица 102 фич** | `.../docs/GROK_FULL_FEATURE_MATRIX.md` | B16, F11, статусы 🟡 |
| **Env-пример** | `.../docs/COMPANION_FEATURE_FLAGS.env.example` | FEATURE_* |
| **Правило prod no mock** | `.../.cursor/rules/prod-no-mock-bypass.mdc` | Не mock в prod (bypass + companion) |
| **Правило server** | `.../.cursor/rules/aladdin-server-connection.mdc` | Ссылка на server guide |

---

## 5. Скрипты деплоя и проверки

| Скрипт | Путь |
|--------|------|
| Деплой | `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/scripts/deploy_companion_p0.sh` |
| Verify prod | `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/scripts/verify_companion_p0_prod.sh` |

### Команды деплоя (после настройки SSH-ключа)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
chmod +x scripts/deploy_companion_p0.sh scripts/verify_companion_p0_prod.sh

# Пример (ключ — у владельца репо, НЕ в git):
./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server

./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```

### Известная проблема (2026-05-26)

Деплой **без ключа** падает:

```text
root@149.154.65.180: Permission denied (publickey,password).
```

**Действия для новой ML-системы:**

1. Получить SSH-ключ `~/.ssh/aladdin_server` (или настроить `ssh-add`) — см. `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`.
2. Повторить `deploy_companion_p0.sh` — выложит в том числе **P1-06 stream** (`ai_companion_router.py`, `companion_store.py`).
3. После деплоя в OpenAPI на сервере должны быть пути companion (скрипт проверяет subset; **добавьте вручную** проверку `/api/ai/companion/stream`, `/threads`, `/memory`, `/profile`, `/feedback`).

### Локальные smoke-тесты (без сервера)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
PYTHONPATH=. python3 Tests/test_companion_p0_smoke.py
# Ожидание: Ran 10 tests ... OK
```

---

## 6. Карта рабочих файлов

### 6.1 Backend (источник правды — копируется на VPS)

| Назначение | Файл |
|------------|------|
| **Главный роутер Companion** | `security/api/routers/ai_companion_router.py` |
| SQLite store, threads, memory, profile, feedback, **stream cache** | `security/services/ai_platform/companion_store.py` |
| Согласие семьи / memory keys | `security/services/ai_platform/consent_resolver.py` |
| JWT claims при login | `security/services/ai_platform/jwt_claims.py` + `app/routers/auth_router.py` |
| Policy child/teen/parent | `security/services/ai_platform/policy_engine.py`, `age_policy.py` |
| Лимиты сообщений/голоса | `security/services/ai_platform/usage_meters.py` |
| Capabilities | `security/services/ai_platform/capabilities.py` |
| Feature flags | `security/services/ai_platform/feature_flags.py` |
| Orchestrator (stub) | `security/services/ai_platform/orchestrator.py` |
| Модули registry | `security/services/ai_platform/modules/registry.py`, `companion.py`, `voice_realtime.py`, `web_search.py` |
| WebSocket голос MVP | `security/api/routers/ai_voice_ws_router.py` |
| Platform router | `security/api/routers/ai_platform_router.py` |
| Assistant (LLM делегат для companion chat) | `security/api/routers/ai_assistant_router.py` |
| Точка входа FastAPI | `main.py` |

### 6.2 iOS Companion

| Назначение | Файл |
|------------|------|
| Эндпоинты | `Core/Config/AppConfig.swift` (`Endpoint.aiCompanion*`, `aiVoice*`) |
| REST API | `Core/Services/CompanionAPIService.swift` |
| **SSE stream + resume** | `Core/Network/CompanionStreamingService.swift` |
| Модели | `Core/Models/CompanionModels.swift` |
| Capabilities | `Core/Services/CompanionCapabilitiesService.swift` |
| Голос WS | `Core/Voice/CompanionVoiceSession.swift` |
| Hub (история threads) | `Screens/CompanionHubScreen.swift` |
| Чат + стрим + лайк/дизлайк | `Screens/CompanionConversationScreen.swift` |
| Согласие родителя (**в таргете Xcode**) | `Screens/02_FamilyScreen.swift` + `Screens/CompanionParentConsentSection.swift` |
| Память родителя | `Screens/CompanionMemoryManagementSection.swift` (в Family) |
| Личность / инструкции | `Screens/CompanionPersonalitySection.swift` (в Family) |
| Навигация | `Core/Navigation/NavigationManager.swift`, `ALADDINApp.swift` |
| Вход из Kids | `Screens/ChildRewardsScreen.swift` → `.companionHub` |
| Xcode project | `ALADDIN.xcodeproj/project.pbxproj` |

### 6.3 Критические ловушки

1. **`FamilyModals.swift` НЕ в `project.pbxproj`** — UI родителя для companion только через **`02_FamilyScreen.swift`**.
2. **Companion chat** идёт через `ai_assistant_router` / assistant pipeline, **не** через `run_orchestrator()` (orchestrator = 🟡 stub).
3. **Голос** на WS — echo/stub MVP, не полноценный xAI realtime.
4. **База** — SQLite файл на сервере `COMPANION_DB_PATH=/opt/aladdin-backend/data/companion_platform.db`.
5. Заголовок **`X-Aladdin-Family-Id`** — из `FamilyLocalStore.loadPersistedFamilyId()` для consent/memory/profile.

---

## 7. API Companion (реализованные пути)

Базовый префикс: `/api/ai/companion`

| Метод | Путь | Назначение | BE | Prod* |
|-------|------|------------|----|-------|
| GET | `/capabilities` | Фичи для iOS | ✅ | ✅** |
| GET | `/characters` | Список героев | ✅ | ✅** |
| GET | `/state` | Trust, emotion | ✅ | ✅** |
| POST | `/chat` | Синхронный чат | ✅ | ✅** |
| POST | `/stream` | SSE + resume (P1-06) | ✅ | ⚠️ после деплоя |
| GET | `/threads` | История диалогов | ✅ | ⚠️ |
| GET | `/threads/{id}/messages` | Сообщения thread | ✅ | ⚠️ |
| GET/POST | `/consent` | Родительское согласие | ✅ | ⚠️ |
| GET/PUT | `/profile` | Инструкции + preset | ✅ | ⚠️ |
| POST | `/feedback` | Лайк/дизлайк | ✅ | ⚠️ |
| GET/DELETE | `/memory` | Память | ✅ | ⚠️ |
| GET | `/memory/export` | Экспорт JSON | ✅ | ⚠️ |
| GET | `/cosmetics` | Каталог косметики (P1-07 BE) | ✅ | ⚠️ |
| POST | `/api/ai/voice/ephemeral-token` | Токен для WS | ✅ | ✅** |
| WS | `/api/ai/voice/realtime` | Голос MVP | 🟡 | 🟡 |

\* **Prod** = предполагается после успешного `deploy_companion_p0.sh` на 2026-05-26 (P0 выкатили); P1-04…06 могут быть только в репо до повторного деплоя.  
\** Проверяется скриптом verify (characters, capabilities).

---

## 8. Детальный статус по каждой из 47 задач

### P0 — Спринт 1 (MVP Kids + voice) — спринт **закрыт 19/19**

| ID | Задача | BE | iOS | Test | Prod | Примечание |
|----|--------|----|-----|------|------|------------|
| **P0-01** | JWT: `app_id`, `age_band`, `parent_consent`, лимиты | ✅ | ✅ | ✅ | ✅ | `jwt_claims.py`, `auth_router.py` |
| **P0-02** | policy_engine child/teen/parent | ✅ | 🟡 | ✅ | ✅ | iOS не вызывает policy напрямую |
| **P0-03** | База trust, threads, usage | 🟡 | — | ✅ | ✅ | **SQLite MVP**, не Postgres/Redis |
| **P0-04** | WebSocket `/api/ai/voice/realtime` | 🟡 | 🟡 | ❌ | 🟡 | MVP stub, не full realtime |
| **P0-05** | Ephemeral token | ✅ | ✅ | ❌ | ✅ | Без API key на устройстве |
| **P0-06** | Companion API → store + orchestrator | 🟡 | — | ✅ | ✅ | Store ✅; orchestrator **не** в hot path chat |
| **P0-07** | iOS модели + API | ✅ | ✅ | ❌ | ✅ | `CompanionAPIService`, `CompanionModels` |
| **P0-08** | Hub + Разговор | ✅ | ✅ | ❌ | ✅ | `CompanionHubScreen`, `CompanionConversationScreen` |
| **P0-09** | CompanionVoiceSession | 🟡 | 🟡 | ❌ | 🟡 | WS подключение есть, аудио pipeline MVP |
| **P0-10** | Эмоции + lip-sync lite | — | 🟡 | ❌ | ✅ | Emoji + scaleEffect, не Rive |
| **P0-11** | Вход только Kids/Игры | — | ✅ | ❌ | ✅ | `ChildRewardsScreen` → companionHub |
| **P0-12** | PII gate + no mock prod | ✅ | ✅ | ❌ | 🟡 | `AIOutboundTextGate`; проверять prod вручную |
| **P0-13** | Счётчики сообщений/голоса | ✅ | — | ✅ | ✅ | `usage_meters.py` |
| **P0-14** | Smoke-тесты | — | — | ✅ | — | `Tests/test_companion_p0_smoke.py` (10 tests) |
| **P0-15** | Деплой VPS + health | — | — | — | 🟡 | Скрипт есть; **SSH key required** |
| **P0-16** | PlatformModule + registry | ✅ | — | ❌ | 🟡 | `modules/registry.py` |
| **P0-17** | GET /capabilities | ✅ | — | ❌ | ✅ | platform + companion |
| **P0-18** | CompanionCapabilitiesService | — | ✅ | ❌ | ✅ | Скрытие mic по API |
| **P0-19** | Env FEATURE_* + док | ✅ | — | — | 🟡 | `.env` на сервере вручную |

---

### P1 — Спринт 2 — **6 / 11** в спринте «готово»

| ID | Задача | BE | iOS | Test | Prod | Примечание |
|----|--------|----|-----|------|------|------------|
| **P1-01** | Threads (история) | ✅ | ✅ | ✅ | ⚠️ | `GET /threads`, Hub, `companion_active_thread_id` |
| **P1-02** | UI согласия родителя | ✅ | ✅ | ❌ | ⚠️ | `02_FamilyScreen` + `CompanionParentConsentSection` |
| **P1-03** | Память вкл/выкл, delete, export | ✅ | ✅ | ✅ | ⚠️ | `CompanionMemoryManagementSection` |
| **P1-04** | Инструкции + тон | ✅ | ✅ | ✅ | ⚠️ | `CompanionPersonalitySection`, preset friendly/calm/… |
| **P1-05** | Лайк/дизлайк | ✅ | ✅ | ✅ | ⚠️ | `POST /feedback`, UI в Conversation |
| **P1-06** | Stream resume после обрыва | ✅ | ✅ | ✅ | ⚠️ | `POST /stream`, `CompanionStreamingService`, кнопка «Продолжить загрузку» |
| **P1-07** | Косметика за trust | 🟡 | ❌ | ❌ | ⚠️ | `GET /cosmetics` + каталог; **нет iOS UI** выбора наряда |
| **P1-08** | Rive анимации | ❌ | ❌ | ❌ | ❌ | Сейчас emoji + lip-sync lite |
| **P1-09** | Legal COPPA/152-ФЗ | ❌ | 🟡 | ❌ | ❌ | Только текст в consent section, нет Store/legal экранов |
| **P1-10** | Аналитика N1–N6 | 🟡 | ❌ | ❌ | ❌ | Частично `ai_history_store` при feedback; нет полного N1–N6 |
| **P1-11** | Предупреждение 20% лимита | 🟡 | ❌ | ❌ | ❌ | `usage_meters` есть; UI предупреждения нет |

---

### P2 — Фаза B — **0 / 8**

| ID | Задача | BE | iOS | Test | Prod | Примечание |
|----|--------|----|-----|------|------|------------|
| **P2-01** | Web search + источники | 🟡 | ❌ | ❌ | ❌ | `WebSearchModule` stub в registry |
| **P2-02** | Все агенты через orchestrator | 🟡 | — | ❌ | ❌ | `run_orchestrator` stub |
| **P2-03** | Fast / Reasoning / Think | ❌ | ❌ | ❌ | ❌ | |
| **P2-04** | Фото и PDF в чате | ❌ | ❌ | ❌ | ❌ | |
| **P2-05** | Decay/streak trust | ❌ | ❌ | ❌ | ❌ | Trust только +/- события |
| **P2-06** | Контекст семьи в промпте | 🟡 | ❌ | ❌ | ❌ | family_id в headers; полный family context нет |
| **P2-07** | API Responses + tools | ❌ | ❌ | ❌ | ❌ | |
| **P2-08** | Алерт себестоимости AI | ❌ | ❌ | ❌ | ❌ | |

---

### P3 — Фаза C — **0 / 6**

| ID | Задача | BE | iOS | Test | Prod |
|----|--------|----|-----|------|------|
| **P3-01** | Генерация картинок family-safe | ❌ | ❌ | ❌ | ❌ |
| **P3-02** | Генерация видео | ❌ | ❌ | ❌ | ❌ |
| **P3-03** | Workspaces (папки чатов) | ❌ | ❌ | ❌ | ❌ |
| **P3-04** | Очень длинный контекст | ❌ | ❌ | ❌ | ❌ |
| **P3-05** | Android | ❌ | ❌ | ❌ | ❌ |
| **P3-06** | Adult iOS в Store | ❌ | ❌ | ❌ | ❌ |

---

### Adult (только backend) — **0 / 3**

| ID | Задача | BE | iOS | Test | Prod |
|----|--------|----|-----|------|------|
| **A-01** | OpenAPI `app_id=aladdin_adult` | ❌ | — | ❌ | ❌ |
| **A-02** | Тесты policy NSFW adult JWT | ❌ | — | ❌ | ❌ |
| **A-03** | Репозиторий Adult app | ❌ | ❌ | ❌ | ❌ |

---

### Отменено (X) — не в roadmap (5 задач)

| ID | Что | Статус |
|----|-----|--------|
| **X-01** | Запись разговора | отменено |
| **X-02** | Публичная ссылка на чат | отменено |
| **X-03** | Клон голоса | отменено |
| **X-04** | Поиск X/Twitter | отменено |
| **X-05** | X embed, Build, Canvas, … | отменено |

---

## 9. P1-06 (последняя завершённая) — как устроено

### Backend

1. Новое сообщение: `companion_chat()` → токены из `response.split()` → `put_stream_cache(message_id, user_id, tokens, meta)`.
2. Resume: `POST /stream` с `resumeFromIndex` + `messageId`, пустой `message`, `context: "resume"` → `get_stream_cache` → SSE с токена `start_index`.
3. Формат SSE как у assistant: `data: {"token":"...","done":false,"messageId":"..."}` → финал `done: true` + `[DONE]`.

Файлы: `ai_companion_router.py` (`CompanionStreamRequest`, `companion_stream`), `companion_store.py` (таблица `companion_stream_cache`).

### iOS

- `CompanionStreamingService` — URLSession bytes, UserDefaults `companion_stream_state`.
- `CompanionConversationScreen` — по умолчанию **стрим**, не `sendChat`; при ошибке — **«Продолжить загрузку»**.

### Тест

- `test_companion_stream_cache` в `Tests/test_companion_p0_smoke.py`.

---

## 10. Что делать дальше (приоритет)

### Фаза A — срочно (блокеры «как на проде»)

1. **OPS-01** — SSH + `deploy_companion_p0.sh` (P1-04…06 на `aladdin-ai.ru`).
2. **OPS-02 / P1-15** — полный `verify_companion_p0_prod.sh` (stream, threads, memory, profile, feedback, cosmetics).
3. **OPS-05** — после деплоя: ручной чек §12 + устройство (стрим + resume).

### Фаза B — CX: универсальный компаньон (приоритет продукта)

4. **P1-26** — промпты life-first (не security-first).
5. **P1-27** — companion intent router (domains + mood).
6. **P1-28** — возрасты: child / teen / parent / senior 60+.
7. **P1-29** — режим «эксперт безопасности» (опционально).
8. **P1-30** + **P2-11** — эмоции от настроения, `sad`/`playful`/`nostalgic`.
9. **P1-25** + **P2-13** — этика одиночества L1–L3 + social bridge.

### Фаза C — спринт P1 (фичи)

11. **P1-07** — косметика iOS.
12. **P1-09 + P1-19** — legal + App Store.
13. **P1-10 + P1-11** — аналитика + лимит 20%.
14. **P1-08 + P1-23** — Rive + эмоции.

### Фаза D — production 10/10 (P1+)

15. **P1-12…P1-22**, **OPS-04**, **P2-02**.

### Фаза E — аудитории + Grok (P2+)

16. **P2-14** Senior 60+, **P2-15** teen loneliness, **P2-12…P2-16**.
17. **P2-01…P2-09** — после §17 gate.

---

## 11. Cursor TODO — импорт (68 + 4 OPS + 7 X)

Скопируй в **Cursor → TODO** (или попроси агента создать через TodoWrite). Статусы: `completed` / `pending` / `cancelled`.

### Выполнено (25) — `completed`

```
P0-01 JWT: app_id, age_band, parent_consent, лимиты
P0-02 policy_engine child/teen/parent
P0-03 База trust, threads, usage (SQLite MVP)
P0-04 WebSocket /api/ai/voice/realtime
P0-05 Ephemeral token для голоса
P0-06 Companion API → store + orchestrator
P0-07 iOS модели + Companion API
P0-08 iOS Hub + Разговор с героем
P0-09 iOS CompanionVoiceSession WebSocket
P0-10 iOS эмоции героя + lip-sync lite
P0-11 Вход только из Kids/Игры
P0-12 PII gate + no mock в prod
P0-13 Счётчики сообщений и голоса
P0-14 Smoke-тесты companion + voice
P0-15 Деплой VPS + health
P0-16 modules/ PlatformModule + registry
P0-17 GET /capabilities
P0-18 iOS CompanionCapabilitiesService
P0-19 Env FEATURE_* + док деплоя
P1-01 Список threads (история диалогов)
P1-02 UI согласия родителя
P1-03 Память: вкл/выкл, удалить, экспорт
P1-04 Свои инструкции и тон личности
P1-05 Оценка ответов лайк/дизлайк
P1-06 Продолжить stream после обрыва
```

### Ожидает (43) — `pending`

```
OPS-01 Деплой с SSH-ключом P1-04…06 на прод
OPS-02 Расширить verify (или P1-15)
OPS-04 Мониторинг стоимости LLM (ранний алерт)
OPS-05 DoD Prod после каждого деплоя
P1-25 Этика companion L1–L3 (одиночество + кризис)
P1-26 Persona life-first (промпты не security)
P1-27 Companion intent router (domains + mood)
P1-28 Возрастные персоны child/teen/parent/senior
P1-29 Режим эксперт безопасности (toggle)
P1-30 Эмоции от настроения + sad/playful/nostalgic
P1-07 Косметика за trust
P1-08 Rive анимации
P1-09 Legal тексты COPPA/152-ФЗ
P1-10 Аналитика N1–N6
P1-11 Предупреждение 20% лимита
P1-12 Postgres + Redis (миграция с SQLite)
P1-13 Голос production (не stub)
P1-14 iOS XCUITest companion smoke
P1-15 Полный prod verify script
P1-16 Hot path: assistant vs orchestrator (док)
P1-17 Accessibility VoiceOver + Dynamic Type
P1-18 Rate limiting + abuse edge cases
P1-19 App Store submission pack
P1-20 Локализация RU/EN companion
P1-21 Offline кэш последнего thread (без push)
P1-22 Модерация ответа после LLM
P1-23 Эмоции + стиль речи Grok-level (Rive+stream+voice+sad/playful)
P2-01 Web search + источники
P2-02 Companion через orchestrator (полная реализация + feature flag)
P2-03 Fast / Reasoning / Think
P2-04 Фото и PDF в чате
P2-05 Decay/streak trust
P2-06 Контекст семьи в промпте
P2-07 API Responses + tools
P2-08 Алерт себестоимости AI (дашборд)
P2-09 Figma hero assets ↔ Companion/Rive
P2-11 Mood-aware (детализация P1-30)
P2-12 Life domains API + UI подсказки тем
P2-13 Social bridge — мост к живым людям
P2-14 Вход Senior 60+ (скука, одиночество)
P2-15 Teen loneliness playbook
P2-16 Trust за эмпатию (не только security)
P3-01 Генерация картинок family-safe
P3-02 Генерация видео
P3-03 Workspaces (папки чатов)
P3-04 Очень длинный контекст
P3-05 Android
P3-06 Adult iOS в Store
A-01 OpenAPI app_id=aladdin_adult
A-02 Тесты policy NSFW adult JWT
A-03 Заготовка репозитория Adult app
```

### Отменено (7) — `cancelled`

```
X-01 ОТМЕНА: запись разговора
X-02 ОТМЕНА: публичная ссылка на чат
X-03 ОТМЕНА: клон голоса
X-04 ОТМЕНА: поиск X/Twitter
X-05 ОТМЕНА: X embed, Build, Canvas…
X-06 ОТМЕНА: push «вернись к Единорогу» (guilt comeback)
X-07 ОТМЕНА: ежедневный cron-backup БД (Postgres+Redis — P1-12)
```

*(OPS-01…05 включены в список «Ожидает» выше.)*

---

## 12. Чеклист приёмки для новой ML-системы

- [ ] Прочитать `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`
- [ ] Настроить SSH: `ssh -i ~/.ssh/aladdin_server root@149.154.65.180`
- [ ] `PYTHONPATH=. python3 Tests/test_companion_p0_smoke.py` → 10 OK
- [ ] `./scripts/deploy_companion_p0.sh root 149.154.65.180 <key>`
- [ ] `./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru`
- [ ] На устройстве: Kids → Герои → чат → стрим → обрыв сети → «Продолжить загрузку»
- [ ] Родитель: Family → согласие / память / личность
- [ ] Обновлять `docs/COMPANION_IMPLEMENTATION_TODOS.md` после каждой закрытой задачи
- [ ] Синхронизировать Cursor TODO (68 + 4 OPS + 7 X)
- [ ] Пройти §17 «Grok parity gate» перед объявлением production-ready

---

## 15. Чёрная шляпа → что делать (простым языком)

| Риск | Что будет, если не сделать | Что сделать | Задача |
|------|----------------------------|-------------|--------|
| **SQLite на проде** | При нагрузке — гонки и потеря данных | **Postgres** + **Redis** для stream-cache; **без** ежедневного backup (**X-07**) | **P1-12** |
| **Голос stub** | Микрофон без реального диалога | **13a:** `SpeechManager` как в `06_AIAssistantScreen` → stream/chat; **13d:** убрать stub в `ai_voice_ws_router` | **P1-13** |
| **Нет iOS автотестов** | Любой PR ломает Hub/stream/consent незаметно | **XCUITest** 5–7 сценариев в CI | **P1-14** |
| **Verify урезан** | Скрипт пишет OK, а `/stream` на проде 404 | Дописать verify: все эндпоинты + один stream roundtrip | **P1-15**, **OPS-02** |
| **Orchestrator stub** | Путаница: «почему не через мозг?» | **P1-16:** ADR + комментарии в коде; **P2-02:** полный перевод companion на orchestrator (feature flag) | **P1-16**, **P2-02** ✅ делаем |
| **P1-10/11 отложены** | Не знаем, сколько стоит AI и когда резать лимит | События N1–N6 + баннер 20% **до** массового теста | **P1-10**, **P1-11** |
| **Нет миграции DB** | Postgres в плане «на словах» | Отдельная задача с критериями и rollback | **P1-12** |
| **Accessibility / offline** | App Store / без сети | VoiceOver, крупный шрифт; **offline-кэш** thread (**без push** — **X-06**) | **P1-17**, **P1-21** |
| **Rate limiting** | Один бот сжигает весь LLM-бюджет | 429 по device/family; flood protection | **P1-18** |
| **Legal / Store** | Отклонение в Review | Privacy, parental gate, AI disclosure | **P1-09**, **P1-19** |
| **Локализация** | Только RU в коде | EN каталог для Companion | **P1-20** |
| **Модерация** | Только до LLM — опасный ответ проскочит | Post-filter + blocklist | **P1-22** |
| **Backup ежедневный** | — | **Не делаем** (решение продукта) | **X-07** |
| **Стоимость LLM** | Сюрприз в счёте | Порог алерта в рублях/день | **OPS-04**, **P2-08** |
| **Figma hero** | Разные картинки в онбординге и Companion | Один pipeline ассетов | **P2-09** |

---

## 16. Эмоции и стили речи — статус и план

### Стили речи (как Custom Instructions у Grok)

| Preset | Backend (`PERSONALITY_PRESET_HINTS`) | iOS UI | В промпте LLM | Голос TTS |
|--------|--------------------------------------|--------|---------------|-----------|
| `friendly` | ✅ | ✅ Family | ✅ | ❌ **P1-23** |
| `calm` | ✅ | ✅ | ✅ | ❌ **P1-23** |
| `playful` | ✅ | ✅ | ✅ | ❌ **P1-23** |
| `mentor` | ✅ | ✅ | ✅ | ❌ **P1-23** |

Код: `ai_companion_router.py` → `_build_companion_system_prefix`; iOS → `CompanionPersonalitySection`, `CompanionProfileResponse.presetLabels`.

### Эмоции персонажа (визуал + контекст ответа)

| Emotion | BE (`_emotion_for_intent`) | iOS `CompanionHeroEmotion` | UI сейчас | Rive / production |
|---------|----------------------------|----------------------------|-----------|-------------------|
| idle, happy, listening, speaking | частично | ✅ enum | 🟡 emoji + scale | **P1-08**, **P1-23** |
| alert, comfort, celebrate, thinking | ✅ по intent | ✅ | 🟡 | **P1-23** |
| из stream SSE `emotion` | ✅ | ✅ parser | 🟡 не всегда обновляет hero | **P1-23** |
| из голоса WS | 🟡 | 🟡 `CompanionVoiceSession` | 🟡 | **P1-13**, **P1-23** |

**Вывод:** стили речи **в тексте** — P1-04 ✅. **В голосе и «живом» лице»** — закрывают **P1-13** (13a–13d) + **P1-08** + **P1-23** (чеклист 7 пунктов в `COMPANION_IMPLEMENTATION_TODOS.md`).

### P1-13 — перенос микрофона из AI Assistant (эталон)

| Компонент | AI Assistant (готово) | Companion (сейчас) | Действие |
|-----------|----------------------|-------------------|----------|
| STT | `SpeechManager` — Apple Speech on-device | WS stub, пустой `transcript` | **13a:** тот же `SpeechManager` в `CompanionConversationScreen` |
| UX микрофона | hold/tap, алерты, `warmUpPermissionsIfNeeded` | только WS ping | Скопировать паттерн из `06_AIAssistantScreen.swift` |
| Отправка текста | `sendMessage()` → assistant API | `CompanionStreamingService` | **13b:** STT → stream с `personality_preset` |
| Audio session | `VoiceAudioSessionCoordinator` | уже в `CompanionVoiceSession` | Переиспользовать `.companion` profile |
| Сервер WS | — | `ai_voice_ws_router` stub строки 107–122 | **13d:** STT→`companion_chat`→TTS + `emotion` |

---


## 17. Критерии 10/10 (оценка плана после P1+)

| Критерий | Было | Цель после P1+ / OPS |
|----------|------|----------------------|
| Полнота roadmap | 9/10 | **10/10** — 60 задач, пробелы закрыты |
| Честность статусов | 9/10 | **10/10** — закрытие только при 4 слоях ✅ |
| iOS-специфика | 8/10 | **10/10** — P1-14, P1-17, P1-20 |
| QA / Test | 6/10 | **10/10** — P1-14, P1-15, smoke+prod |
| Ops / deploy | 8/10 | **10/10** — OPS-01…05 |
| Compliance / legal | 6/10 | **10/10** — P1-09, P1-19 |
| Масштабирование / data | 7/10 | **10/10** — P1-12 (Postgres+Redis; backup **не** в scope) |
| Handoff для ML | 10/10 | **10/10** |

**Grok parity gate (перед P2):** голос не stub ✅ · stream+resume на проде ✅ · Rive+эмоции ✅ · Postgres ✅ · XCUITest green ✅ · verify full ✅ · legal/App Store ✅ · N1–N6 + лимит 20% ✅.

**Финал большой задачи Companion:**

1. **GATE-DIALOG-REGRESS** — R1–R19 (все 25 выполненных задач) — см. [COMPANION_FINAL_PLAN_AND_VERIFICATION.md](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md)
2. **GATE-DIALOG** — D01–D10 (ребёнок шутит, teen одинок, бабушка 60+, голос, 5 эмоций подряд, …)

---

## 18. Видение «компаньон против одиночества» — проверка плана (2026-05-26)

### Короткий ответ

| Вопрос | Ответ |
|--------|--------|
| Это **заложено в продуктовом видении**? | **Да** — в `GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md`: «любые темы», юмор, советы, «живой друг». |
| Это **уже работает в коде** на 100%? | **Нет** — промпт компаньона в основном про **безопасность семьи**; эмоции **узкие** (7 штук, без отдельной «грусти» героя). |
| Это **есть в спринтовом плане** до сегодняшней правки? | **Частично** — стили P1-04, эмоции P1-08/P1-23; **не было** доменов жизни, mood-NLP, этики одиночества. |
| **Добавлено в план сейчас** | **P2-10, P2-11, P2-12, P1-25** |

### Три слоя правды

```
ВИДЕНИЕ (docs)     →  «любой разговор, друг, юмор, поддержка»
        ↓
КОД (промпт/LLM)   →  «VPN, угрозы, parental control» + general fallback
        ↓
ПЛАН (задачи)      →  P1-04/08/23 эмоции; P2-10…12 темы; P1-25 границы
```

### Спектр эмоций: что есть / чего не хватает

| Нужно пользователю | В плане до P1-23 | В коде |
|--------------------|------------------|--------|
| Юморный герой | preset `playful` | ✅ в промпте |
| Грустный / сочувствующий тон | `comfort` + `calm` | 🟡 нет эмоции `sad` на аватаре |
| Радость, праздник | `celebrate`, `happy` | ✅ |
| Тревога / опасность | `alert` | ✅ (часто security) |
| Подстроиться под **настроение пользователя** | ❌ не было | ❌ только intent security | → **P2-11** |
| Rive «живое лицо» | P1-08, P1-23 | ❌ emoji |

### «Все сферы жизни» и советы

- **LLM технически** может отвечать на `general` intent — **любой текст**.
- **Персона** сейчас **не настроена** как универсальный собеседник по работе, отношениям, здоровью и т.д. — см. `_companion_system_prefix` в `ai_companion_router.py`.
- **Дети/подростки:** policy **PG / PG-13**, родительское согласие — не взрослый «психолог на все темы».
- **Взрослый без лимитов** — отдельный **Adult app** (A-01…A-03), **не** Family Kids.

### Аудитории 60+, подростки, дети

| Аудитория | Задачи |
|-----------|--------|
| Ребёнок | P1-28 `child`, P1-25 L1–L3 |
| Подросток без друзей | P1-28 `teen`, **P2-15**, P2-13 |
| Взрослый / родитель | P1-28 `parent`, P1-26 |
| **60+ скучно / одиноко** | P1-28 `senior`, **P2-14**, persona `nostalgic`/`calm` |
| Полный взрослый без PG | **Adult app** A-01…A-03 |

---

## 19. Два спорных пункта — решение продукта (2026-05-26)

### A) «❌ Замена живого общения» — наше предложение

**Не отказываемся от миссии одиночества.** Меняем формулировку:

| Было в анализе | Стало в плане |
|----------------|---------------|
| «Намеренно не заменяем людей» | **«Рядом, когда не с кем поговорить»** (L1–L2) |
| Звучит как отказ от цели | **P1-25** + **P2-13**: эмпатия + мост к людям |
| — | **L3 кризис:** не притворяться человеком-терапевтом |

**Маркетинг (можно):** «Когда скучно или одиноко — Единорог/Аладдин всегда выслушает».  
**Маркетинг (нельзя):** «Замени друзей и семью», «Единственный, кто тебя понимает».

**Механики:** память, юмор, 4 стиля речи, mood-aware, **Social bridge** (P2-13), trust за возврат (P2-16).

### B) «❌ Промпт только про безопасность» — наше предложение

**Убираем security-first из кода.** Делаем **life-first**:

| Шаг | Задача | Суть |
|-----|--------|------|
| 1 | **P1-26** | Новый system prompt: **70% жизнь** (друзья, скука, хобби, учёба, чувства) / **30% security** при запросе или угрозе |
| 2 | **P1-27** | Отдельный `companion_intent_router` — **не** security `ai_intent_router` |
| 3 | **P1-29** | Режим «🛡️ Помощь с защитой» — включает старый security-фокус |
| 4 | **P1-30** | Эмоции от **настроения**, не от `threat_analysis` |
| 5 | **P2-01** | Web search — актуальные темы (фильмы, новости, хобби) |

**Пример структуры промпта (P1-26):**

```
Ты тёплый друг [Единорог/Аладдин]. Говоришь о: школе, друзьях, хобби, игре, скуке, грусти, радости, семье.
Поддерживаешь, шутишь уместно (PG), даёшь простые советы. Слушаешь внимательно.
Суперсила ALADDIN (VPN, угрозы, parental control) — когда пользователь спрашивает или есть опасность.
Не собирай личные данные. При тяжёлой грусти — предложи поговорить с близким (Social bridge).
```

---

## 20. Как сделать наилучшим образом (архитектура)

```
                    ┌─────────────────────────────────────┐
                    │  Пользователь (child → senior 60+)   │
                    └──────────────────┬──────────────────┘
                                       ▼
              ┌────────────────────────────────────────────┐
              │  P1-28 age persona + P1-04 personality preset │
              └──────────────────┬─────────────────────────────┘
                                 ▼
              ┌────────────────────────────────────────────┐
              │  P1-27 companion_intent: domain + mood        │
              └──────────────────┬─────────────────────────────┘
                                 ▼
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌─────────────────┐                           ┌──────────────────┐
│ Default: friend │                           │ P1-29: security  │
│ P1-26 life LLM  │                           │ mode (optional)  │
└────────┬────────┘                           └────────┬─────────┘
         ▼                                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  P1-30 emotion + P1-23 Rive + P1-13 voice (SpeechManager first) │
└─────────────────────────────────────────────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  P1-25 ethics: L1 empathy | L2 social bridge | L3 crisis         │
└─────────────────────────────────────────────────────────────────┘
```

**Лучший порядок внедрения:** P1-26 → P1-27 → P1-30 → P1-28 → P1-29 → (UI) P2-12, P2-14, P2-15 → P1-08/23 → P1-13.

---

## 13. Git / workspace

| Параметр | Значение |
|----------|----------|
| Repo root | `/Users/sergejhlystov/ALADDIN_NEW` |
| iOS + backend Companion | `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/` |
| Дубликат (не основной) | `ALADDIN_NEW/mobile_apps/ALADDIN_iOS_tmp_push146/` — не использовать без явной причины |

**Коммиты:** только по запросу пользователя. **Force push main:** запрещён.

---

## 14. Контакты контекста (transcript)

Полная история чата с реализацией P0–P1-06:  
`/Users/sergejhlystov/.cursor/projects/Users-sergejhlystov-ALADDIN-NEW/agent-transcripts/6df66f5c-d006-4f34-b221-ccf6139f010e/6df66f5c-d006-4f34-b221-ccf6139f010e.jsonl`

---

*Обновлено 2026-05-26 (rev3): **68** задач; блок **CX** P1-25…P1-30; P2-13…16; §19–20 life-first + одиночество. Синхронизировать с `COMPANION_IMPLEMENTATION_TODOS.md`.*
