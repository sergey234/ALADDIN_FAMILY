# TODO: Realtime, Offline & Collaboration Plan
**Дата:** 30 апреля 2026 (обновлено: 1 мая 2026 — продуктовые решения по навигации / языку / аналитике)  
**Цель:** Сделать ALADDIN более живым, современным и удобным (особенно семейный чат и AI-помощник)  
**Статус:** В работе (обновлено по фактическому состоянию кода)  
**От:** Senior iOS Architect (15+ лет опыта)

---

## 🔥 Высокий приоритет (W25–W26)

- [x] **1. AI Token Streaming + Resume после reconnect**  
  **Статус:** DONE (Phase 1 + 2)  
  Реализовано: `AIStreamingService.swift` (с resume, offline state, auto-restore), обновлены `AIAssistantViewModel`, `APIService`, `AppConfig`. Экран `06_AIAssistantScreen.swift` поддерживает плавное появление токенов.

- [x] **2. Реализовать uploadMedia + медиа в семейном чате** (Infrastructure + UI)  
  **Статус:** DONE (базовый production-ready функционал)  
  Создано:
  - `MediaUploadManager.swift` (очередь, offline, progress, retry)
  - `MediaMessageBubble.swift` (универсальный компонент для image/video/voice)
  - Полноценная `uploadMedia` в `APIService.swift` (multipart + progress)
  - Интеграция в `23_FamilyChatScreen.swift` (голос/камера/галерея, отправка, отображение)
  - Поддержка `mediaThumbnailUrl` в модели и UI, ужесточение WS parsing (`message`/`payload`, snake/camel)
  *Осталось по UX:* продуктовая полировка (опционально).

- [x] **3. Unified Offline Layer v2**  
  **Статус:** DONE (formal DoD закрыт)  
  Сделано:
  - `UnifiedOfflineStore` без цикла инициализации с `OfflineManager`
  - Программная Core Data модель (`UnifiedOfflineManagedObjectModel`) и `UnifiedOfflineRecord`
  - Делегирование runtime offline-потока в unified слой, счётчики pending и sync order
  - `FamilyChatOfflineManager`: unified + fallback cache в `UserDefaults`
  - `performFullSync` с push pending + pull remote + retry/backoff + conflict policy
  - Строгая sync identity (`user_id` required, no guest fallback)
  - AI checkpoint upsert/collapse в unified store
  Formal closure:
  - Legacy runtime-хвост изолирован: авто-очередь in-memory из `OfflineManager.execute(...)` выключена как primary path
  - Финальный e2e протокол reconnect/conflict/identity зафиксирован как completed
  - Документ formal DoD: `docs/P3_UNIFIED_OFFLINE_E2E_PROTOCOL.md`

---

## 🟡 Средний приоритет (W26–W27)

- [x] **4. Полноценный Presence**  
  **Статус:** DONE (v1 production-ready; требуется обычный manual regression перед релизом)  
  Реализовано: WS connection status callbacks, typing/presence payload tolerance, stale typing prune TTL, reconnect cleanup, status badge в UI.

- [x] **5. Sign in with Apple + Magic Links**  
  **Статус:** DONE (v1 production-ready)  
  Реализовано: API endpoints/models, `SignInWithAppleButton`, magic-link request/consume, deep link parsing, unified session persistence.

- [ ] **6. Декларативные правила доступа**  
  **Статус:** DEFERRED (по решению текущего цикла)  
  Причина: приоритет на realtime/offline/auth stability и sync-unification. Вернуться отдельной итерацией.

---

## 🔄 Долгосрочное улучшение (W28+)

- [x] **7. Thin Reactive Layer (Combine + SyncEngine)**  
  **Статус:** DONE (formal DoD закрыт)  
  Реализовано:
  - Базовый `SyncEngine` (offline/familyChat/aiStreaming/family/settings/networkProtection)
  - Интеграция в `FamilyChat`, `AIAssistant`, `Family`, `Settings`, `NetworkProtection`
  - Покрытие “non-heavy” экранов и модалок (`Screens/Views/*`, `Shared/Components/Modals/*`) по контракту `pending/syncing/synced/error/local`
  Formal closure:
  - Регламент публикации новых sync API-потоков закреплён
  - Документ enforcement: `docs/P7_SYNCENGINE_PUBLISHING_RULES.md`

---

## 🧭 UX-расширение Home: переключение AI/Family чатов

- [ ] **8. Лёгкое переключение чатов на главном экране (AI ↔ Family)**  
  **Статус:** PLANNED (без изменения backend-контрактов)  
  **Цель UX:** переключение должно быть *заметным рядом с чатом*, но *не визуально навязчивым*.

  **Рекомендуемая реализация (этап 1 — базовый безопасный):**
  - Segmented switch в верхней части chat-блока на Home: `AI чат | Семейный чат`
  - Спокойный визуальный стиль (secondary background, умеренный контраст, без агрессивных акцентов)
  - Сохранение последнего выбора в `UserDefaults`
  - Опция в Settings: “Чат по умолчанию” (`AI / Family / Последний`)

  **Этап 2 (после стабилизации):**
  - Smart default (контекстный приоритет):
    - новые family события → `Family` first
    - активная AI-сессия → `AI` first

  **Альтернативы (бэклог / по результатам QA):**
  - Tabs “2 чата” внутри Home с памятью последнего активного
  - Карточки с drag-to-prioritize (персонализация порядка)
  - Двухрядный переключатель/компоновка — только если базовый сегмент не решит UX полностью

  **Границы реализации (чтобы не ломать текущий план 1–7):**
  - Только UI/shell/navigation слой
  - Без изменений API, WS, offline и auth контрактов
  - Обязательный regression smoke: chat send/media/typing/reconnect + AI stream resume

---

## Продуктовые решения (согласовано): навигация, язык чатов, экран аналитики

Зафиксировано для последующей реализации в коде (связано с UX локализации и честными состояниями данных, не только с realtime).

### A. Меню быстрой навигации в настройках (верхний список экранов)

- **Решение:** в **production-сборке** **не показывать** пользователю служебные пункты (разработческие / недоделанные маршруты): например «Загрузка», «Тест настроек», «Набор тестов», «Запасные настройки», отдельный маршрут ввода кода приглашения, если он только для отладки, и т.п.
- **Обоснование:** для пользователя они часто не несут ценности и ведут в пустой UI или зависание; для проверок достаточно **DEBUG** или отдельного внутреннего режима.
- [ ] **Задача реализации:** whitelist экранов для production-меню + `#if DEBUG` для полного списка при необходимости (`ALADDINNavigationBar` / `NavigationManager.ALADDINScreen`).

### B. Язык ответов в чатах = язык приложения

- **Решение (продукт):** если в настройках выбран **English**, тексты ответов и подсказок в **AI-ассистенте** — на английском; если **русский** — на русском.
- **Расширение того же правила:** **семейный чат** — приоритет отображения и формулировок (подписи, системные сообщения, ошибки, где применимо — отправляемый/ожидаемый язык контента в связке с API) выстраивается **от языка приложения**, по той же логике, что и AI-чат (единое правило для пользователя).
- [ ] **Задача реализации:** проброс языка в запросы AI/streaming + локализация строк + для Family Chat — ключи/контракт с сервером там, где уже есть `locale`/предпочтение языка.
- **Примечание:** серверные fallback и статические подсказки должны уважать выбранный язык, иначе правило обходится на стороне API.

### C. Экран аналитики — честно различать состояния (текст + цвет)

Один общий текст «Нет данных» для всех случаев **не использовать**, если по факту разные причины.

| Состояние | Смысл для пользователя | UX (ориентир) |
|-----------|------------------------|----------------|
| Успешная загрузка, массив пустой | За выбранный период **событий не было** | Нейтральное сообщение («Событий не было» / эквивалент EN), без красного как об ошибке |
| Ошибка сети / сервера / парсинга | Данные **не удалось загрузить** | Сообщение об ошибке + **Повторить**, заметное отличие от «пустого успеха» |
| Офлайн или только кэш | Данные **могут быть неполными** | Отдельный индикатор (офлайн / из кэша), не смешивать с «ноль событий» |

- [ ] **Задача реализации:** в `AnalyticsScreen` / `AnalyticsViewModel` / `RemoteAnalyticsService` явно различать `emptySuccess`, `error`, `offlineOrStale`; разные ключи локализации для RU/EN и разная цветовая семантика (например зелёный/нейтральный vs предупреждение vs ошибка).

---

## Дополнительная информация

- **Главный вывод:** Полная миграция на BaaS (InstantDB и подобные) **была бы ошибкой**. Будем улучшать существующий стек точечно.
- Полный детальный roadmap находится в файле: `ALADDIN_REALTIME_COLLABORATION_ROADMAP.md`
- Матрица traceability обновлена: `PLAN_ITEM_TRACEABILITY_MATRIX_FULL.md`
- Проверочные гейты по изменениям: `xcodebuild` и `localization_lint` пройдены.

---

**Как пользоваться:** Ставьте `- [x]` когда задача выполнена.

**Прогресс (по факту кода):**
- DONE: 6 из 7 (пункты 1, 2, 3, 4, 5, 7)
- IN PROGRESS: 0 из 7
- DEFERRED: 1 из 7 (пункт 6)

**Следующий приоритет:** пройти manual QA protocol (presence / AI resume / magic-link / Apple Sign-In / cross-screen settings sync) и проставить done/not done статусы.

**Бэклог по согласованным решениям (см. раздел «Продуктовые решения» выше):** навигация production-меню, язык AI + семейного чата, дифференциация состояний аналитики.

**Детальный чеклист с разбором 1–7 и отслеживанием:** `docs/TODO_APP_UX_LOCALIZATION_ANALYTICS_NAV.md`