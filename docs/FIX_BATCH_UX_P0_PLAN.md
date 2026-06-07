# FIX BATCH UX P0 — финальный план (2026-06-07)

Статус: **утверждён к реализации**  
Трекер задач: `.cursor/BATCH_UX_FIX_TODO.md`  
Рабочий корень: `ALADDIN_iOS`

---

## Подтверждение предположений (повторная проверка кода)

| # | Предположение | Вердикт | Доказательство |
|---|---------------|---------|----------------|
| 1 | Ошибка на Child Rewards — `CancellationError`, не «сеть» | ✅ **Верно** | `errorMessage = error.localizedDescription` в `ChildRewardsViewModel.load`; баннер в `ChildRewardsScreen.errorBanner` |
| 2 | Причина — отмена `Task` при уходе с экрана | ✅ **Верно** | `onAppear { Task { await runInitialLoad() } }` — неструктурированная задача; при `dismiss`/`goBack` SwiftUI отменяет `.task`, но здесь **не** `.task` |
| 3 | `withTimeout` + `cancelAll()` может маскировать таймаут | ⚠️ **Частично** | Таймаут бросает `NetworkError.timeout`, но отмена **внешней** задачи всё равно даёт `CancellationError` |
| 4 | Tournament на английском — mock-файл в target | ✅ **Верно** | `project.pbxproj` → `path = Screens/Views/FamilyTournamentView.swift` (hardcoded EN, Mom/Dad, score 1247) |
| 5 | Правильный Tournament с API и RU — не в сборке | ✅ **Верно** | `Screens/FamilyTournamentView.swift` — локализация, API, `goBack()`, но **не** в `PBXSourcesBuildPhase` |
| 6 | EN при «русской раскладке» — из-за клавиатуры | ❌ **Нет** | Язык UI = `LocalizationManager` / настройки приложения; EN на Tournament из-за **wrong file**, не раскладки |
| 7 | Dark Web 35/9 — не iOS-mock | ✅ **Верно** | `GET /api/reports/dark-web/stats` → SQL `COUNT(*)` из `darkweb.darkweb_leaks` |
| 8 | Dark Web — не персональные данные пользователя | ✅ **Верно** | SQL **без** `WHERE user_id` (параметр `user_id` в сигнатуре есть, в запросе **не используется**) |
| 9 | Dark Web — двойной источник stats | ✅ **Верно** | `DarkWebMonitoringModal`: сначала `applyFrom(components:)`, потом `loadData()`; `onReceive` может перезаписать API агрегатором |
| 10 | OB_02 title y=412 | ✅ **Верно** | `14_OnboardingScreen.swift` `OnboardingFigmaAnchor` case 1 |
| 11 | Правильный Tournament — все ключи локализации есть | ⚠️ **Неполно** | Ключи `join_tournament`, `loading_leaderboard` **отсутствуют** в `LocalizationManager` — нужно добавить в батч |

---

## Порядок батчей

```
Batch A (P0) → Tournament Xcode + smoke
Batch B (P0) → OB_02 title −28pt
Batch C (P1) → Child Rewards CancellationError (лучшее решение)
Batch D (P2) → AI copy «Умный помощник офлайн…»
Batch E (P1) → Dark Web prod-only data (backend + iOS)
```

---

## Batch A — Family Tournament (P0)

### Проблема
В production-сборке подключён прототип `Screens/Views/FamilyTournamentView.swift`:
- Hardcoded EN: "Family Tournament", "Mom", "Dad", 1247 points
- Нет кнопки «Назад» → зависание (только `NavigationManager`, без swipe-back)
- Нет API `/api/gamification/tournaments*`

### Решение
1. **Xcode:** заменить file ref на `Screens/FamilyTournamentView.swift`
2. **Удалить или исключить** `Screens/Views/FamilyTournamentView.swift` из target (оставить в репо с пометкой deprecated или удалить)
3. **Локализация:** добавить в `LocalizationManager` (RU + EN):
   - `join_tournament` — «Присоединиться к турниру» / "Join tournament"
   - `loading_leaderboard` — «Загружаем рейтинг…» / "Loading leaderboard…"
4. Smoke:
   - RU: заголовок «🏆 Турнир семьи», empty state на RU
   - EN: «🏆 Family Tournament»
   - Кнопка ← возвращает на Child Rewards
   - Pull-to-refresh не блокирует UI

### DoD
- [ ] В `pbxproj` только один `FamilyTournamentView.swift` (Screens/)
- [ ] Нет строк "Mom"/"Daily Challenge" на экране
- [ ] `navigationManager.goBack()` работает
- [ ] API вызывается (или empty state, не fake leaderboard)

---

## Batch B — Onboarding OB_02 (P0, 5 мин)

### Проблема
Заголовок «Ваш персональный агент безопасности» нужно поднять ещё на 1 строку.

### Решение
`14_OnboardingScreen.swift` → `OnboardingFigmaAnchor` **case 1**:
- `title.y`: **412 → 384** (−28pt, одна строка)
- Опционально: `scrim.origin.y` **504 → 476** если title наезжает на градиент (проверить на SE + 15 Pro)

### DoD
- [ ] Вся фраза «Ваш персональный агент безопасности» визуально выше
- [ ] Нет clip на 3 строки title

---

## Batch C — Child Rewards CancellationError (P1) — **лучшее решение**

### Корневая причина
Сырой `error.localizedDescription` пробрасывается в UI; `CancellationError` — штатная отмена, не ошибка для пользователя.

### Лучшее решение (комбинированное, в порядке важности)

#### C1. Lifecycle — `.task` вместо `onAppear` + `Task` (**главный фикс**)
```swift
.task(id: effectiveChildId) {
    await runInitialLoad()
}
```
- Убрать `Task { await runInitialLoad() }` из `onAppear`
- При уходе с экрана задача отменяется **без** баннера

#### C2. Фильтр «тихих» ошибок (страховка)
В `ChildRewardsViewModel.load` и `ChildRewardsScreen.onReceive($errorMessage)`:
```swift
private func isIgnorableLoadError(_ error: Error) -> Bool {
    if error is CancellationError { return true }
    if let url = error as? URLError, url.code == .cancelled { return true }
    return false
}
```
→ не устанавливать `errorMessage` / `loadErrorMessage`

#### C3. Человеческие сообщения
| Ситуация | Ключ |
|----------|------|
| Таймаут 12с | `child_rewards_error_generic` |
| 401 / нет токена | новый или существующий auth key |
| 404 | `child_rewards_error_resource_not_found` |
| Прочее сеть | `child_rewards_error_generic` |

#### C4. `withTimeout` — оставить, но не полагаться только на него
Текущая реализация корректно бросает `NetworkError.timeout`. Менять `cancelAll()` не обязательно после C1+C2.

#### C5. Убрать дубли загрузки
- `runInitialLoad` guard `isInitialLoadInFlight` — оставить
- Retry: тот же `.task` refresh или `await runInitialLoad()` внутри structured task

### Не делать
- Не показывать английский `CancellationError` пользователю
- Не увеличивать таймаут >15с без метрик (сначала C1+C2)

### DoD
- [ ] «Зашёл → сразу назад» — **нет** баннера
- [ ] «Остался 15с, API down» — RU «Не удалось загрузить награды…»
- [ ] Retry работает без `CancellationError`

---

## Batch D — AI copy (P2)

### Выбранный вариант
**Баннер:** «Умный помощник офлайн — включите в Настройках»

### Файлы
| Ключ / файл | RU | EN (предложение) |
|-------------|-----|------------------|
| `ai_consent_banner_title` | Умный помощник офлайн — включите в Настройках | Smart assistant is offline — turn on in Settings |
| `ai_consent_banner_action` | Включить в настройках | Turn on in Settings |
| `ai_error_consent_required` | Включите умного помощника в Настройках, чтобы отправлять вопросы | Turn on the smart assistant in Settings to send questions |
| `AIOutboundTextGate.swift` | синхрон с `ai_error_consent_required` | — |
| `05_SettingsScreen` | заголовок тумблера → ключ `ai_data_sharing_title` | "AI assistant & 3 heroes" |

Новый ключ `ai_data_sharing_title`: «AI-помощник и 3 героя» (вынести из хардкода).

### DoD
- [ ] Нет строки «Облачный AI-помощник» в user-facing UI
- [ ] Баннер на Companion + AI Assistant обновлён
- [ ] Settings title локализован

---

## Batch E — Dark Web prod-only (P1, backend + iOS)

### Проблема prod
- `darkweb.darkweb_leaks` — глобальный COUNT без user scope
- Scan endpoints пишут события в ту же таблицу → раздувают «утечки»
- iOS: `applyFrom(components:)` может показать цифры до/вместо API

### Backend (обязательно для «только истина»)
1. `get_dark_web_stats`: `WHERE user_id = :uid` (или `family_id` через JWT)
2. `get_dark_web_leaks/list`: тот же scope
3. Разделить **breach records** vs **scan audit events** (отдельная таблица или `event_type`)
4. Аудит текущих 35 rows на сервере — demo или реальные breaches

### iOS
1. **Убрать** отображение stats из `applyFrom` для Dark Web (только `loadData()`)
2. Передавать `user_id` в query если API поддержит
3. Empty state: 0 утечек + CTA «Запустить проверку»
4. Подпись: `dark_web_data_source_server` — «Данные с сервера ALADDIN»

### DoD
- [ ] Новый пользователь без сканов → 0 / 0
- [ ] Числа меняются только после реального scan пользователя
- [ ] Нет перезаписи API агрегатором analytics

---

## Риски и зависимости

| Риск | Митигация |
|------|-----------|
| Два `struct FamilyTournamentView` — конфликт компиляции | Удалить/переименовать Views/ копию |
| Dark Web backend требует деплой | Batch E.1 отдельный коммит + smoke на staging |
| Tournament API пустой | Empty state (уже в Screens/) — OK для prod |
| Figma OB_02 drift | После y=384 — скрин vs Figma node OB_02 |

---

## Оценка времени

| Batch | Время |
|-------|-------|
| A Tournament | 1–2 ч |
| B OB_02 | 15 мин |
| C Child Rewards | 1 ч |
| D AI copy | 30 мин |
| E Dark Web | 3–5 ч (с backend) |

**Рекомендуемый старт:** A + B в одном PR, затем C, D, E.
