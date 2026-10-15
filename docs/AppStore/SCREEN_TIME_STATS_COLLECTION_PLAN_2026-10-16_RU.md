# План: сбор и показ статистики Screen Time (DeviceActivity)

**Дата:** 2026-10-16  
**Репо:** `ALADDIN_iOS` · Bundle `ai.aladdin` · App Group `group.ai.aladdin`  
**Канон entitlement / Distribution:** [`FAMILY_CONTROLS_DISTRIBUTION_IMPLEMENTATION_PLAN_2026-09-09_RU.md`](FAMILY_CONTROLS_DISTRIBUTION_IMPLEMENTATION_PLAN_2026-09-09_RU.md)  
**Честность UI (уже):** `./scripts/verify_parental_time_stats_honesty.sh` → PASS  

**Цель этого документа:** наилучший путь, чтобы **факт использования** (сегодня / по приложениям) собирался легально по правилам Apple и отображался во всех нужных местах ALADDIN — без моков.

---

## 0. GATES (до большого кода)

| # | Gate | DoD |
|---|------|-----|
| G1 | Apple **Family Controls Distribution** Assigned на main + Monitor (+ Report для статистики UI) | Capability на App ID |
| G2 | Entitlement `com.apple.developer.family-controls` в main + extensions | В подписанном `.app` / `.appex` |
| G3 | Targets в Xcode: Monitor + Report (минимум для stats) | Embedded в Archive |
| G4 | Авторизация Screen Time на **устройстве ребёнка** | `AuthorizationCenter` = approved |
| G5 | Выбор apps/categories через `FamilyActivityPicker` → App Group | Opaque tokens, не сырые bundle id |
| G6 | `fetchRealScreenTimeStats()` возвращает **не** `[]` на child после дня использования | Device QA |
| G7 | UI без mock; claims только после G6 | `allowsSystemFamilyControls` + copy |
| G8 | Privacy: данные только для parental control, не реклама/трекинг | Review Notes + Privacy Nutrition |

Пока G1–G3 нет — **нельзя** обещать «статистика считается везде» в Store / тарифах.

---

## 1. Разрешено ли Apple?

**Да — для родительского контроля**, через официальный **Screen Time API** (`FamilyControls` + `ManagedSettings` + `DeviceActivity`).

| Можно | Нельзя |
|-------|--------|
| Лимиты / блокировка **выбранных** приложений и категорий на устройстве ребёнка | Тихий сбор usage всех apps без Screen Time auth |
| Показ родителю отчётов через **Device Activity Report** | Использовать Screen Time данные для рекламы / продаже трекерам |
| Заявлять в App Store **после** Distribution + QA | Писать «блокируем Instagram» в текущей App Store сборке без entitlement/extensions |
| Хранить агрегированные минуты в App Group для UI ALADDIN | Скрапить чужие apps через приватные API / Accessibility «шпион» |

Официально:

- [Requesting the Family Controls entitlement](https://developer.apple.com/documentation/familycontrols/requesting-the-family-controls-entitlement)
- [Screen Time Technology Frameworks](https://developer.apple.com/documentation/screentimeapi)
- [Configuring Family Controls](https://developer.apple.com/documentation/xcode/configuring-family-controls)

**Важно:** сейчас в `ALADDIN.entitlements` **нет** `family-controls`; в App Store build `AppStoreBuildPolicy.allowsSystemFamilyControls = false`. Это правильно для текущей отправки Guideline 2.1.

---

## 2. Было → Будет

### Было (факт на 2026-10-16)

| Слой | Состояние |
|------|-----------|
| Usage «1h 36m / Instagram 18 min» | UI-моки / пустой empty (моки убраны) |
| `parental_time_stats` | Никто не писал реальные данные |
| `fetchRealScreenTimeStats()` | `return []` |
| Extensions Screen Time | **Нет** (есть ContentBlocker / CallDirectory / Share / Widgets) |
| Entitlement FC | **Нет** |
| Лимиты / расписание / сон | Сохраняются в UserDefaults (+ sync настроек) — это **правила**, не usage |
| Показ | Empty: «Лимиты сохранены. Факт использования…» |

### Будет (после реализации)

| Слой | Состояние |
|------|-----------|
| На устройстве **ребёнка** | Auth → Monitor считает пороги/день → Report отдаёт usage выбранных apps |
| App Group `group.ai.aladdin` | Кэш: total used, per-app minutes, `source=device_activity`, дата дня |
| `fetchRealScreenTimeStats()` | Читает App Group / Report bridge → `[AppUsageStatistics]` |
| UI Семья / Advanced | Реальные «использовано / лимит» RU/EN |
| Родительский iPhone | Видит агрегаты после sync (push/API или локально если тот же device в demo) |
| Store claims | Только в билде с G1–G7 PASS |

---

## 3. Архитектура «куда присоединить» (наилучший путь)

```
[Родитель iPhone]                    [Ребёнок iPhone]
 FamilyActivityPicker  --selection-->  AuthorizationCenter
 сохранение tokens (App Group /        ManagedSettingsStore (shield/лимиты)
 server encrypted)                     DeviceActivityMonitor (thresholds)
        |                                      |
        |                              DeviceActivityReport (UI/отчёт)
        |                                      |
        +------ sync settings (:8002) ---------+
        |                                      |
 FamilyTimeControlModal  <--- App Group / API --+
 AdvancedProtection card
 FamilyDayStrip (used/limit)
```

### Роли компонентов Apple

| Компонент | Bundle ID (канон) | Зачем для статистики |
|-----------|-------------------|----------------------|
| Main app | `ai.aladdin` | Auth UI, picker, чтение кэша, показ |
| **Device Activity Monitor** | `ai.aladdin.DeviceActivityMonitor` | События лимитов/расписания; может писать дневные агрегаты в App Group |
| **Device Activity Report** | `ai.aladdin.DeviceActivityReport` | **Главный источник UI-статистики** (системный отчёт по выбранным apps) |
| Shield Configuration | `ai.aladdin.ShieldConfiguration` | Блокировка (не stats, но тот же FC трек) |

**Рекомендация v1 для статистики:** Monitor + Report (+ main FC).  
Shield — параллельно по Distribution-плану (блокировка), не блокер для «цифр сегодня», но нужен для полноценного parental product.

### Единый мост данных (ALADDIN)

Новый тонкий слой (имя условное):

`Core/Family/ScreenTimeUsageStore.swift`

- Читает/пишет App Group (`group.ai.aladdin`) ключ вроде `screen_time_usage_v1`
- Поля: `dayStart`, `totalSeconds`, `apps: [{tokenId/hash, displayName?, seconds, limitSeconds?}]`, `source: device_activity`, `updatedAt`
- `ParentalControlManager.fetchRealScreenTimeStats()` → маппит в `[AppUsageStatistics]`
- При успехе пишет совместимый `UserDefaults`/`App Group` словарь `parental_time_stats` с **`source=device_activity`** (уже ждёт UI)

Monitor/Report extensions **только** пишут в App Group (не в main UserDefaults напрямую, если другой process — App Group обязателен).

---

## 4. Какие приложения можно мониторить?

Через **`FamilyActivityPicker`** родитель (или настройка на child) выбирает:

| Тип | Примеры | Как в API |
|-----|---------|-----------|
| Конкретные приложения | Instagram, TikTok, YouTube, Telegram, Discord, игры… | `ApplicationToken` (opaque) |
| Категории Screen Time | Соцсети, Игры, Развлечения… | `ActivityCategoryToken` |
| Веб-домены (ограниченно) | Отдельные web domains в FamilyControls | `WebDomainToken` где применимо |

**Ограничения Apple:**

- Нет произвольного «списка всех bundle id мира» без picker/tokens.
- Имена apps в Report — по правилам системы; не всегда «красивый» Instagram string с родителя без selection context.
- Системные/критичные apps Apple может не отдавать так же, как сторонние.
- Мониторинг возможен **на устройстве, где выдана Screen Time authorization** (обычно профиль ребёнка).
- Родитель **не** видит живой Screen Time чужого iPhone «из облака Apple» — только то, что ALADDIN сам синхронизирует (наш API) или то, что показывает система на том устройстве.

**Практический v1 набор для ALADDIN UI (как сейчас в модалке):**

1. Instagram  
2. TikTok  
3. Общий экран (сумма выбранных / total device — что отдаст Report)  
4. Остальные выбранные apps — список «ещё N» или полный scroll later  

Лимиты в `AppLimitsSettingsModal` должны стать **привязкой к токенам picker**, а не только к строкам `"Instagram"`.

---

## 5. Куда вставлять в приложение (все места)

### 5.1. Обязательные точки (usage)

| # | Место | Файл / символ | Что сделать |
|---|-------|---------------|-------------|
| 1 | Мост данных | **NEW** `Core/Family/ScreenTimeUsageStore.swift` | App Group read/write + day rollover |
| 2 | API менеджера | `ParentalControlManager.fetchRealScreenTimeStats()` | Читать store, не `[]` |
| 3 | Модалка времени | `Screens/02_FamilyScreen.swift` → `FamilyTimeControlModal` | Уже: empty / `device_activity` cache — оставить; после данных покажет цифры |
| 4 | Advanced карточка | `Screens/AdvancedProtectionSettingsScreen.swift` → `familyTimeControlCard` / `loadFamilyStats` | Уже фильтр `source=device_activity`; подтянуть локализацию «—» → реальные |
| 5 | Сохранение лимитов ↔ tokens | `AppLimitsSettingsModal` + NEW picker flow | Лимиты минут на token, не только имя |
| 6 | Child apply | `ParentalControlManager.applyPulledParentalSettingsLocally` / `applyFamilyControlsPipelineIfPossible` | После auth стартовать Monitor schedule + обновить Report context |
| 7 | Readiness UI | `Screens/07_ParentalControlScreen.swift` (уже `refreshFamilyControlsReadiness`) | Баннер: auth / extension missing / OK |
| 8 | Policy gate | `Core/Config/AppConfig.swift` → `AppStoreBuildPolicy.allowsSystemFamilyControls` | `true` в App Store **только** после QA |
| 9 | Entitlements | `ALADDIN.entitlements` + extension entitlements | `com.apple.developer.family-controls` + App Group |
| 10 | Xcode targets | `ALADDIN.xcodeproj` | NEW: DeviceActivityMonitor, DeviceActivityReport |
| 11 | Honesty gate | `scripts/verify_parental_time_stats_honesty.sh` | Обновить: разрешить writer из ScreenTimeUsageStore; запретить mock |

### 5.2. Желательные точки (после v1 stats)

| # | Место | Зачем |
|---|-------|--------|
| 12 | `Shared/Components/FamilyDayStripView.swift` | Chip «Экран»: `used / limit` вместо только лимита |
| 13 | Sync на `:8002` | Опционально: агрегат «ребёнок → родитель» (минуты/день, без сырых токенов) |
| 14 | Еженедельный семейный отчёт (FVP P2) | Сводка за 7 дней из store/API |
| 15 | `ParentalControlViewModel.screenTimeToday` | Сейчас заглушка `"2:45"` / `"..."` — заменить чтением store (если экран покажет) |

### 5.3. Не путать (это НЕ Screen Time usage)

| Место | Что там на самом деле |
|-------|------------------------|
| Модалка геолокации «Детальная статистика за сегодня» | События геозоны |
| `Core/Analytics/AnalyticsService` `DeviceActivity` struct | Другая модель аналитики устройств (не Apple Screen Time) |
| `Screens/FamilyModals.swift` | **Не в target** — не трогать / не оживлять моки |

### 5.4. Порядок «присоединения» в коде (инженерный)

1. App Group schema + `ScreenTimeUsageStore`  
2. DeviceActivityReport extension → пишет дневной snapshot в App Group  
3. DeviceActivityMonitor → thresholds + optional mid-day refresh trigger  
4. `fetchRealScreenTimeStats()` читает store  
5. UI уже подписан на этот путь (`FamilyTimeControlModal.applyTimeStatistics`)  
6. Parent sync (если нужен remote) — отдельный API endpoint, только агрегаты  
7. Claims / tariff copy / Review Notes  

---

## 6. Чеклист задач (исполняемый)

### Фаза A — Владелец / Apple (без кода UI)

- [ ] **A1** Утвердить: stats v1 = Monitor + **Report** (+ main FC)  
- [ ] **A2** Зафиксировать Bundle ID: `ai.aladdin.DeviceActivityMonitor`, `ai.aladdin.DeviceActivityReport`  
- [ ] **A3** Account Holder подаёт Family Controls **Distribution** (main + Monitor + Report) — тексты в Distribution-плане §5  
- [ ] **A4** Не обещать Screen Time в текущем App Review письме  
- [ ] **A5** Дождаться Assigned  

### Фаза B — Инфраструктура Xcode

- [ ] **B1** App IDs + App Group на extensions  
- [ ] **B2** Targets Monitor + Report в `ALADDIN.xcodeproj`, embed в main  
- [ ] **B3** Entitlement `family-controls` + App Group на main/extensions  
- [ ] **B4** Provisioning profiles Distribution  
- [ ] **B5** `assessFamilyControlsReadiness()` видит plugins (`deviceactivity` в `builtInPlugIns`)  

### Фаза C — Сбор данных

- [ ] **C1** `ScreenTimeUsageStore` (App Group, day key, source)  
- [ ] **C2** Report extension: контекст выбранных apps → агрегат за сегодня  
- [ ] **C3** Monitor: schedule 00:00–23:59 + threshold events → refresh store  
- [ ] **C4** `fetchRealScreenTimeStats()` → store (не `[]`)  
- [ ] **C5** `FamilyActivityPicker` flow + сохранение selection (App Group / Keychain / server)  
- [ ] **C6** Связка AppLimits ↔ tokens (Instagram/TikTok = selected tokens)  
- [ ] **C7** Child pipeline: auth → startMonitoring → report available  

### Фаза D — UI / продукт

- [ ] **D1** FamilyTimeControlModal: реальные цифры + локализованные ч/мин (уже форматтер)  
- [ ] **D2** AdvancedProtection metrics card  
- [ ] **D3** FamilyDayStrip used/limit (опционально v1.1)  
- [ ] **D4** Parental readiness banner (нет auth / нет extension / OK)  
- [ ] **D5** Copy RU/EN: честные claims только после device QA  
- [ ] **D6** Обновить `verify_parental_time_stats_honesty.sh` под реальный writer  

### Фаза E — QA и релиз

- [ ] **E1** Device QA: 2 iPhone (parent + child), день использования выбранных apps  
- [ ] **E2** Проверка: модалка Семья показывает used/limit без EN `h/min` сырьём  
- [ ] **E3** Проверка: без auth — empty, не мок  
- [ ] **E4** Archive entitlements dump  
- [ ] **E5** Включить `allowsSystemFamilyControls` в App Store build  
- [ ] **E6** TestFlight → Submit следующей версии  

---

## 7. Что увидит пользователь после

| Экран | До | После |
|-------|----|-------|
| Семья → Управление временем → «Статистика сегодня» | Empty / раньше мок | `1 ч 36 мин / 3 ч`, Instagram/TikTok used/limit |
| Advanced → Screen Time card | `— / —` | Те же агрегаты |
| День семьи (полоска) | Только лимит «3 ч в день» | (v1.1) «1 ч 36 мин / 3 ч» |
| Ребёнок: превышение лимита | Нет системного shield | Shield + событие Monitor |
| App Store текст | Не обещаем Screen Time | Обещаем только то, что прошло E1–E4 |

---

## 8. Риски

| Риск | Митигация |
|------|-----------|
| Apple долго одобряет Distribution | Подать параллельно; UI empty честный |
| Report API сложный / мало данных без selection | Picker обязателен до показа цифр |
| Путаница parent vs child device | Stats pipeline только на child role; parent читает sync |
| Снова завезли моки | Honesty script + запрет fallback `"1h 36m"` |
| Guideline 2.1 на текущей отправке | FC claims **выкл** до отдельного релиза |

---

## 9. Рекомендуемый порядок владельцу (топ-3 варианта)

| Вариант | Суть | Когда выбирать |
|---------|------|----------------|
| **★ A — Stats-first (Report+Monitor)** | Сначала цифры в UI, shield следом | Нужна честная «Статистика сегодня» |
| B — Full FC v1 (Monitor+Shield+Report) | Блокировка + статистика одним релизом | Полный parental USP |
| C — Только Monitor без Report | Лимиты/события без красивых графиков | Быстрее, но UI статистики бедный |

**Рекомендация:** ★ **A**, опираясь на уже готовый честный UI + Distribution-план; Shield не откладывать надолго (тот же entitlement-трек).

---

## 10. Связанные файлы (якоря)

- `Core/Managers/ParentalControlManager.swift` — auth, pipeline, `fetchRealScreenTimeStats`  
- `Screens/02_FamilyScreen.swift` — `FamilyTimeControlModal`, persist лимитов  
- `Screens/AdvancedProtectionSettingsScreen.swift` — metrics card  
- `Shared/Components/FamilyDayStripView.swift` — лимит дня  
- `Shared/Utilities/ParentalScreenTimeFormat.swift` — локализация длительностей  
- `Core/Config/AppConfig.swift` — `AppStoreBuildPolicy`  
- `docs/AppStore/FAMILY_CONTROLS_DISTRIBUTION_IMPLEMENTATION_PLAN_2026-09-09_RU.md` — заявки Apple  
- `scripts/verify_parental_time_stats_honesty.sh` — gate против моков  

---

## 11. Статус сейчас (одна строка)

**Инфраструктуры Screen Time для сбора usage нет; UI честно пустой и готов принять `source=device_activity`. Следующий шаг владельца: A1–A3 (решение + подача Distribution), затем B–E по чеклисту.**
