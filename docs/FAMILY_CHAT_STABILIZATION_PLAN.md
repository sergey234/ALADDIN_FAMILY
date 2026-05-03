# План стабилизации семейного чата (TestFlight / реальное устройство)

Цель: убрать ложное «Не удалось загрузить сообщения. Проверьте подключение к интернету» при живой сети, снизить лавину `AttributeGraph: cycle detected`, стабилизировать UI после отправки и polling.

Контекст: ключ `family_chat_error_loading` сейчас используется как «универсальная» ошибка для чата (в т.ч. при не-сетевых сбоях), поэтому пользователь видит вводящее в заблуждение сообщение про интернет.

Примечание по JWT: исправлен разбор поля `exp` (Int/NSNumber) и человекочитаемый вывод в логах (дни/часы вместо огромного числа секунд).

### Сделано в коде (итерация стабилизации)

- Ключи `family_chat_error_network` / `_auth` / `_data` / `_family_missing` + маппинг `NetworkError` в `localizedLoadFailureMessage`.
- `presentChatError` / `dismissChatError` + строка `🔎 Семейный чат [контекст] алерт: …` в консоль.
- Debounce typing через `Task` + `Task.sleep`, отмена при `onDisappear` и при отправке.
- `MessageBubbleView`: параметр `replyPreview`, в ленте передаётся превью ответа без `allMessages: messages`.
- Алерт: `FamilyChatUserErrorAlert` + `.alert(item:)`.
- Polling и prune typing: `onReceive(Timer.publish…)` вместо `Timer { [self] in … }`.
- Silent `loadMessages`: токен поколения — устаревшие ответы не затирают ленту.
- `JWTTokenManager`: общий `expirationUnixSeconds`, исправлен `getTokenExpirationDate`.

---

## Фаза A — Диагностика и правда об ошибке

1. **Развести типы ошибок и тексты**  
   В `23_FamilyChatScreen.swift` (и при необходимости в `APIService` / маппинг `NetworkError`) не подставлять `family_chat_error_loading` для: декодирования, 401/403, пустого `familyId`, таймаута, отмены задачи, SSL pinning. Добавить ключи локализации (RU/EN) с нейтральными формулировками («Не удалось обновить ленту», «Сессия устарела — войдите снова» и т.д.).

2. **Логирование при показе алерта**  
   Одна строка в лог: `NetworkError` / HTTP code / endpoint / `silent` flag — чтобы в следующем TestFlight сразу видеть реальную причину, а не только UI-текст.

---

## Фаза B — SwiftUI: циклы и порядок обновлений

3. **Typing и `messageText`**  
   Убрать синхронные сетевые вызовы из прямого пути `onChange(of: messageText)`: debounce на главной очереди (`Task` + отмена предыдущего, или `DispatchWorkItem`), вызов `sendTypingIndicator` / REST typing только после паузы; пустой текст — только `sendStopTyping` без лишнего REST.

4. **Список сообщений**  
   Проверить `MessageBubbleView`: не дергать родительский state изнутри вычислений, завязанных на `allMessages` (при необходимости передавать только `replyPreview: FamilyChatMessage?` вместо всего массива). Снизить число зависимостей `ForEach` от полного `messages`.

5. **Алерт**  
   Упростить связку `errorMessage` + `.alert`: например отдельный `showErrorAlert` + `lastErrorText`, или `item:`-based alert, чтобы не дублировать чтение `errorMessage` в `isPresented` и `message` в одном такте.

6. **Таймеры**  
   Пересмотреть `Timer` в `View` с замыканием `[self]`: по возможности заменить на `TimelineView` / `onReceive(timer)` из Combine с отменой в `onDisappear`, чтобы не плодить устаревшие захваты и лишние тики под нагрузкой.

---

## Фаза C — Производительность и нагрузка

7. **Polling**  
   Увеличить интервал при фоне / при ошибках, пауза при активной отправке, коалесcing: не запускать `loadMessages(silent:)` если предыдущий ещё в полёте.

8. **Метрики экрана**  
   Точечно отключить или порог для тяжёлых метрик на экране чата (FPS/memory), если они шлются слишком часто и мешают главному потоку.

9. **Профилирование**  
   Один прогон Instruments (SwiftUI + Time Profiler) на устройстве на сценарии: открыть чат → набрать текст → отправить → подождать 2 цикла polling.

---

## Фаза D — Верификация

10. **Чеклист QA**  
    Симулятор + физическое устройство + TestFlight: холодный старт, фон/foreground, слабая сеть (Network Link Conditioner), быстрая серия отправок, смена языка.

11. **JWT лог (косметика)**  
    Исправить отображение оставшегося времени жизни токена в логах (единицы времени / переполнение).

---

## Список задач (чеклист)

- [x] A1: Маппинг ошибок чата — отдельные ключи локализации вместо одного `family_chat_error_loading` для не-сетевых случаев
- [x] A2: Диагностический лог при показе алерта (контекст, текст, `underlying`, silent при загрузке)
- [x] B1: Debounce typing — убрать синхронную сеть из `onChange(messageText)`
- [x] B2: `replyPreview` в `MessageBubbleView` вместо `allMessages: messages`
- [x] B3: Алерт через `Identifiable` + `.alert(item:)`
- [x] B4: Автообновление через `onReceive(Timer.publish…)` вместо `Timer` + `[self]`
- [x] C1: Отбрасывание устаревших silent-ответов `loadMessages` (токен поколения)
- [x] C2: Смягчить нагрузку метрик на экране чата при необходимости (глобальный throttle FPS/памяти в `MetricsService` + интервал FPS в `PerformanceMonitor`)
- [x] C3: Instruments — сценарий в `docs/MASTER_STABILIZATION_AND_PRODUCT_PLAN.md` (блок E‑Instruments)
- [x] D1: QA-матрица — блок E‑QA в том же мастер-плане
- [x] D2: JWT: разбор `exp` + человекочитаемый лог TTL
