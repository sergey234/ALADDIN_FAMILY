# ML Handoff: Build 201 (iOS) + сервер + RAG v1

Документ для другой ML-системы / команды: что уже сделано, что делать дальше, без обучения на переписке пользователей и без сбора ПД для fine-tune.

---

## 0. Контекст продукта (обязательно прочитать)

| Принцип | Значение |
|---------|----------|
| Позиционирование | **«Помощник по безопасности ALADDIN»**, не универсальный ChatGPT |
| Обучение на чатах | **Не делаем** — ни на телефоне, ни датасет из диалогов на сервер |
| ПД для fine-tune | **Не собираем** |
| Облако AI | Opt-in: «Облачный AI-помощник» (`ai_data_sharing_enabled`) — уходит **текущий вопрос** (после PII-redact), не история для тренировки |
| RAG v1 (план) | Индекс **статического** FAQ/docs на сервере, без датасета из чатов |

---

## 1. Build 201 — что уже в коммите (iOS)

### 1.1 Краши (приоритет P0)

**Симптомы TestFlight build 200:**

| ID | Тип | Причина |
|----|-----|---------|
| A | SIGABRT, Combine `@Published` | `storeSyncPhase` / sync с фонового потока + петля `UnifiedOfflineStore` → `SyncEngine` |
| B | Watchdog `0x8BADF00D` | Main thread lock Combine во время SwiftUI layout |
| C | malloc corruption при layout | Часто следствие A/B (испорченная куча) |

**Исправления build 201:**

- `UnifiedOfflineStore.swift`: все записи `@Published` только через `MainActor`; CoreData fetch через `viewContext.perform`; убраны лишние `SyncEngine.publish` на каждый push.
- `OfflineManager.swift` (`SyncEngine`): **удалена** подписка `bindUnifiedOfflineStore` (петля); `publish()` коалесится на main (~80 ms).
- `06_AIAssistantScreen.swift`: debounce SyncEngine events (200 ms) — из build 199; fix `onChange` для iOS 15.

**QA после установки 201:** онбординг → AI Assistant → свайп/чат 2–3 мин → фон/возврат; не должно быть вылетов.

### 1.2 AI Assistant (P0)

| Файл | Изменение |
|------|-----------|
| `NetworkManager.swift` | Retry **502/503** (до 2 попыток, backoff 1s/2s) |
| `ai_sfm_http_chat.py` | Regex «что ты» не ловит «что ты знаешь о …»; off-topic с упоминанием темы |
| `06_AIAssistantScreen.swift` | Текст в поле при голосе; нет auto-send без opt-in; сообщения 502 |
| `SpeechManager` / `SpeechRecognizerFactory` | Прогрев разрешений; ru live → cloud STT; статус «Подключаю микрофон…» |

### 1.3 Номер сборки 202

- `Core/Config/AppConfig.swift` — `buildNumber`, `minimumClientBuildForApiContract`
- `Info.plist` — `CFBundleVersion`
- `ALADDIN.xcodeproj` — `CURRENT_PROJECT_VERSION` (все конфигурации)
- `Tests/UnitTests/AppConfigTests.swift`

---

## 2. Сервер — задачи для ML/backend (P0, параллельно TestFlight)

### Задача S1: Стабильность Hermes (главный «мозг» для свободных вопросов)

- **Цель:** снизить 502 и пустые ответы.
- **Файлы:** `security/api/routers/ai_assistant_router.py`, `security/services/hermes_client.py`, env `AI_BACKEND=hermes`.
- **DoD:**
  - `POST /api/ai/assistant/chat` при intent `general` / `app_help` сначала Hermes skill `aladdin-security-kb`.
  - При падении Hermes → SFM rules (`ai_sfm_http_chat.py`), не 502 без тела.
  - Healthcheck Hermes в deploy playbook.
- **Не делать:** отправлять чаты пользователей в fine-tune.

### Задача S2: SFM только fallback

- **Цель:** rule-based ответы не подменяют LLM при живом Hermes.
- **DoD:** логи `intent=… path=hermes|sfm`; метрика % ответов с `tools_used` containing `hermes`.

### Задача S3: Smoke-набор

- **Файл:** `tools/smoke_ai_eval50.py` (уже есть).
- **DoD:** 50 промптов зелёные на staging; отдельно: «что ты знаешь о X» → off-topic, не шаблон «я помощник VPN».

---

## 3. Продукт / копирайт (P1)

### Задача P1: UI и тексты

- Заголовок: «AI Помощник» + подзаголовок «Помощник по безопасности семьи» (уже в локализации).
- Не использовать «универсальный ИИ», «ChatGPT», «обучается на ваших сообщениях».
- Баннер при `grounded: false`: шаблон по продукту ALADDIN (клиент build 201).

### Задача P2: Opt-in

- Тоггл в настройках: **«Облачный AI-помощник»** (ключ `ai_data_sharing_enabled`).
- Политика: облако = ответ на вопрос, не обучение.

---

## 4. RAG v1 — план на 6–8 недель (без ПД, без fine-tune)

### Фаза R1 (недели 1–2): Статический KB

| # | Задача | Владелец | DoD |
|---|--------|----------|-----|
| R1.1 | Собрать корпус: FAQ keys из `UnifiedFAQCatalog`, `LocalizationManager` app_help, onboarding, тарифы, E2EE howto | Content + ML | `docs/kb/` или JSON, версия `kb_v1` |
| R1.2 | Chunking ~300–800 токенов, metadata: `id`, `locale`, `topic` | ML | Скрипт ingest |
| R1.3 | Embeddings + vector store (pgvector / Qdrant) | Backend | Индекс `aladdin_kb_v1` |
| R1.4 | Retrieve top-k по запросу | Backend | API internal `kb_search(q)` |

**Данные пользователей в индекс не класть.**

### Фаза R2 (недели 3–4): Ответ с цитатами

| # | Задача | DoD |
|---|--------|-----|
| R2.1 | Prompt: question + chunks + `llm_context_policy=kb_rag_v1` | Ответ только из chunks |
| R2.2 | Ответ API: `grounded: true`, `sources: ["faq_…"]` | iOS показывает бейдж |
| R2.3 | Fallback: нет chunks → Hermes → SFM | Как сейчас |

### Фаза R3 (недели 5–6): Агрегаты защиты (уже частично есть)

| # | Задача | DoD |
|---|--------|-----|
| R3.1 | `AISFMContextBuilder` + `sfm_aggregates` в prompt | Цифры только из aggregates |
| R3.2 | Запрет raw logs в LLM (`strip_forbidden_llm_params`) | Аудит payload |

### Фаза R4 (недели 7–8): QA и rollout

| # | Задача | DoD |
|---|--------|-----|
| R4.1 | Расширить `smoke_ai_eval50` + 100 off-topic | Precision off-topic |
| R4.2 | A/B: RAG vs rules-only | Метрики CSAT / retry rate |
| R4.3 | Feature flag `AI_RAG_ENABLED` на сервере | Rollback без релиза iOS |

---

## 5. Явно НЕ делать (blacklist)

- Fine-tune на переписке из приложения.
- Хранение полной истории чатов на сервере для обучения.
- Отправка сырых логов семьи / CoreData в LLM.
- Обещание ответов на любые темы (космос, медицина и т.д.) без disclaimer.

---

## 6. Приоритеты (итоговая очередь)

1. **P0** — TestFlight build **201** на устройствах, регрессия крашей A/B/C.
2. **P0** — Сервер: Hermes up, 502 < 1% на smoke.
3. **P1** — Копирайт «помощник по безопасности».
4. **P2** — RAG v1 фазы R1–R2 (статический KB).
5. **Отложено** — fine-tune, персональная долгая память на сервере.

---

## 7. Ключевые пути в репозитории

```
mobile_apps/ALADDIN_iOS/
  Screens/06_AIAssistantScreen.swift      # AI UI
  Core/Offline/UnifiedOfflineStore.swift  # crash fix
  Core/Offline/OfflineManager.swift       # SyncEngine
  Core/Network/NetworkManager.swift       # 502 retry
  security/services/ai_sfm_http_chat.py   # SFM rules
  security/api/routers/ai_assistant_router.py  # Hermes routing
  security/services/ai_llm_prompt_builder.py   # aggregates_only_v1
  Screens/13_SupportScreen.swift          # UnifiedFAQCatalog
  tools/smoke_ai_eval50.py
```

---

## 8. Вопросы к product owner (если блокер)

1. RAG v1 только ru или ru+en с первого дня?
2. Нужен ли отдельный toggle «Использовать базу знаний ALADDIN» или достаточно облачного AI?
3. Hermes: OpenRouter credits / self-hosted — какой SLA для TestFlight?

---

*Версия документа: build 201 handoff, 2026-05-22.*
