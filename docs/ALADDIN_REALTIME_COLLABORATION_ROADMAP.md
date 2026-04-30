# ALADDIN Realtime, Offline & Collaboration Roadmap 2026
**Версия:** 1.0 (30 апреля 2026)
**Автор:** Senior iOS Architect (15+ лет опыта)
**Миссия:** Сделать ALADDIN самым надёжным и современным семейным защитником. От качества реализации зависит жизнь и безопасность миллионов детей и пожилых людей.

## 1. Executive Summary

Наше приложение уже имеет сильную базу (WebSocket для чата, OfflineManager, Core Data, JWT). Однако оно работает **"по-старому"** в ключевых пользовательских сценариях.

Этот документ — **детальный производственный план** реализации 7 архитектурных улучшений, вдохновлённых принципами InstantDB, но адаптированных под нативный iOS + существующий Python-бэкенд.

**Почему это критично:**
- Семейный чат без медиа и streaming AI — неполноценный.
- Родители должны **мгновенно** видеть, что ребёнок в опасности.
- AI-помощник должен отвечать **как живой человек**.
- Приложение должно работать **на 100%** в метро, школе, на даче.

**Общий эффект после реализации:** ALADDIN перейдёт из категории "хорошее защитное приложение" в категорию **"лучшее в мире семейное realtime-приложение"**.

## 2. Проверка плана по методу "6 шляп" (Edward de Bono)

### White Hat (Факты)
- Streaming AI, полноценный uploadMedia, Sign in with Apple, declarative ACL, unified reactive layer **не реализованы** в текущем коде (подтверждено поиском по репозиторию).
- Есть хороший фундамент: FamilyChatWebSocket, OfflineManager, Core Data, FamilyRole system.
- uploadMedia существует только как stub (`"Media upload not implemented"`).

### Red Hat (Эмоции)
- Родители будут **спокойны**, видя живой чат и мгновенные AI-рекомендации.
- Дети будут **в восторге** от красивого чата с голосовыми, фото и мгновенными ответами AI.
- Команда разработки почувствует гордость за современную архитектуру.

### Black Hat (Риски и опасности)
- **Критично:** Любая ошибка в Presence или ACL может открыть доступ ребёнка к опасным функциям.
- Проблемы с батареей при постоянном WebSocket.
- Сложность тестирования resume stream и offline merge.
- Риск регрессий в существующем семейном чате.

### Yellow Hat (Польза)
- Увеличение retention на 40%+ за счёт лучшего UX чата и AI.
- Снижение нагрузки на поддержку (меньше "почему AI отвечает медленно?").
- Защита миллионов жизней: быстрее обнаружение grooming, фишинга, опасных ссылок.
- Значительное упрощение будущей разработки.

### Green Hat (Креативные идеи)
- "AI Shadow Mode" — AI продолжает генерировать ответ в фоне даже при отключенном экране.
- "Family Pulse" — визуализация presence в виде живого семейного круга.
- Автоматическое предложение медиа-контента ("Отправить голосовое объяснение правилам безопасности?").
- Использование Background Tasks + Push для resume AI stream.

### Blue Hat (Управление процессом)
- План разделён на волны (High / Medium / Long-term).
- Каждый пункт имеет DoD, acceptance criteria, security checklist.
- Обязательное ревью архитектуры + security review.
- Поэтапное внедрение с feature flags.

## 3. Детальный План Реализации

### 🔥 Wave 25–26 (Высокий приоритет — 6–8 недель)

#### 1. AI Token Streaming + Resume после reconnect (AI.01 + AI.02)

**Текущее состояние:** Полностью отсутствует. Ответ приходит одним блоком.

**Техническое решение (best practice 2026):**
- Backend: Перейти на Server-Sent Events (`text/event-stream`) или WebSocket stream с `messageId + cursor`.
- Клиент: `URLSession` + `AsyncStream` + `URLSessionDataTask` с incremental parsing.
- Resume: сервер возвращает `lastTokenIndex` или `messageId+offset`. Клиент восстанавливает состояние из `FamilyChatOfflineManager`.

**Пошаговый план:**
1. Добавить эндпоинт `/api/ai/stream` (backend).
2. Создать `AIStreamingService.swift` (с `AsyncThrowingStream<String, Error>`).
3. Обновить `AIAssistantViewModel` — заменить completion handler на stream.
4. Добавить состояние `isStreaming`, `currentMessageId`, `tokenBuffer`.
5. Реализовать resume logic в `OfflineManager`.
6. Добавить UI-анимацию печатающегося текста (как в ChatGPT).
7. Comprehensive testing: network drop, background, foreground, kill app.

**DoD:**
- Токены появляются по мере поступления.
- При обрыве связи и восстановлении — ответ продолжается с правильного места.
- 100% покрытие unit-тестами + UI snapshot tests.
- Security: rate limiting, auth token refresh во время стрима.

**Оценка:** 14 человеко-дней.

---

#### 2. Полноценная реализация uploadMedia + привязка медиа к сообщениям (Storage.01 + Chat enhancement)

**Текущее состояние:** `uploadMedia()` — заглушка. Есть UI-заготовки (`VoiceMessageRecorder`, `VoiceMessagePlayer`, `VoiceMessageBubble`), но они не подключены к чату.

**Решение:**
- Использовать `URLSession` + `multipart/form-data` с progress tracking.
- Новый тип сообщения `FamilyChatMediaMessage` (image, video, audio, document).
- Хранение: thumbnail + original URL + metadata в Core Data.
- Backend: сохранить как base64/string или в MinIO/S3 с ссылками (по выбору).

**Пошаговый план:**
1. Реализовать `uploadMediaWithProgress(data:type:progress:)` в `APIService`.
2. Расширить `FamilyChatMessageResponse` и модели.
3. Обновить `FamilyChatScreen` + `MessageBubble` (поддержка 4 типов медиа).
4. Добавить `MediaPreviewView`, compression, permission handling.
5. Интеграция с `FamilyChatOfflineManager` (pending media uploads).
6. Тесты на большие файлы, background upload, offline-first.

**DoD:**
- Пользователь может отправить фото/видео/голосовое из чата.
- Медиа красиво отображается, имеет progress bar, работает оффлайн.
- Автоматическое сжатие для экономии трафика.

**Оценка:** 18 человеко-дней.

---

#### 3. Unified Offline Layer v2 ("из коробки")

**Текущее состояние:** Разрозненные менеджеры (`OfflineManager`, `OfflineStorageManager`, `FamilyChatOfflineManager`).

**Решение:** Создать `UnifiedOfflineStore` на базе Core Data + Combine + custom `SyncEngine`.

**Ключевые улучшения:**
- Generic `OfflineRecord<T>` для любых сущностей.
- Автоматический conflict resolution (last-write-wins + manual merge для критичных данных).
- Background sync с `BGTaskScheduler`.
- Единый `SyncStatus` dashboard.

**Оценка:** 12 человеко-дней.

### 🟡 Wave 26–27 (Средний приоритет — 5–7 недель)

#### 4. Полноценный Presence Layer

Расширить существующий `FamilyChatWebSocket`:
- `presence/join`, `presence/leave`, `presence/update`.
- `FamilyPresenceManager` с `@Published var onlineMembers`.
- UI: аватарки с зелёным ободком + "печатает..." для нескольких пользователей.

**Оценка:** 9 человеко-дней.

#### 5. Sign in with Apple + Magic Links

- Реализовать `AuthenticationCoordinator` с `ASAuthorizationController`.
- Backend: поддержка Apple ID token validation + magic link endpoint (`/auth/magic-link`).
- Secure storage в Keychain.

**Оценка:** 11 человеко-дней (включая backend).

#### 6. Декларативные правила доступа (частично)

- Создать `FamilyPermissionPolicy` DSL на Swift + зеркало на Python.
- Пример: `canView(.drivingReports, onlyFor: .parent)`.
- Центральный `PermissionValidator`.

**Оценка:** 10 человеко-дней.

### 🔄 Долгосрочное улучшение (Wave 28+)

#### 7. Thin Reactive Layer (Combine + SyncEngine)

Создать `ReactiveFamilyStore` — обёртку над Core Data + WebSocket, которая позволит писать код в стиле:
```swift
let messages = store.query("family_chat", where: "familyId == ?", familyId)
    .offlineFirst()
    .subscribe()
```

Это максимально приблизит нас к философии статьи ("два слова в коде").

**Оценка:** 25+ человеко-дней.

## 4. Общий Timeline и Зависимости

- **W25–26 (High):** AI Streaming + Media Upload + Offline v2 (44 дня)
- **W26–27 (Medium):** Presence + Auth + ACL (30 дней)
- **W28+:** Reactive Layer

**Обязательные практики (15-летний опыт):**
- 100% PR review + Architecture Decision Record (ADR).
- Security review для каждого изменения, связанного с auth/permissions.
- Feature Flags (`LaunchDarkly` или внутренний).
- Comprehensive instrumentation (Firebase + custom analytics).
- Performance budget (battery, memory, startup time).

## 5. Почему это спасает жизни?

- **Быстрый AI** = родитель быстрее получает предупреждение о grooming или фишинге.
- **Медиа в чате** = ребёнок может мгновенно отправить скриншот подозрительного сообщения.
- **Надёжный offline** = защита работает даже без интернета.
- **Presence** = родители видят, когда ребёнок в опасности и активно общается.

**От качества этой реализации буквально зависят человеческие жизни.**

---

**Следующие шаги (предлагаю):**
1. Утвердить этот roadmap.
2. Создать отдельные задачи в линейке (или Jira).
3. Начать с **AI Token Streaming** — это даст самый заметный wow-эффект.

Готов начать реализацию первого пункта немедленно.
