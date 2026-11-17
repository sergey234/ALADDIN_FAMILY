# Краши watchdog 8BADF00D — сводка сборок 27→32 (Day Journal + Keychain + SimpleHome body + LocalizationManager)

**App:** `ai.aladdin` · **Version:** 1.0.2 · **Team:** B3WGHSWL79  
**Канон релиза:** `docs/RELEASE_BUILD_PROMPT.md`  
**Дата сводки:** 2026-11-17

Это **не** старый продуктовый «Crash Detection» (падение авто / CMMotion). Здесь — **системные kill** приложения (watchdog) и то, что мы чинили в TF-сборках.

---

## Как ловить логи

| Источник | Что даёт | Ограничение |
|----------|----------|-------------|
| Системный `.ips` (Загрузки / Analytics) | Истина: `0x8BADF00D`, стек, thermal | Не попадает сам в UI |
| Настройки → «Диагностика (Crash Logs)» | lifecycle / startup / unclean terminate | **С build 29 в Release скрыто** (`#if DEBUG`) |
| `aladdin_diagnostics_*.txt` | Часто пустой `last_crash_log` при SIGKILL | Норма для watchdog |

SIGKILL / FRONTBOARD watchdog **нельзя** поймать `NSSetUncaughtExceptionHandler`.

---

## Хронология по сборкам

### Build 27 — до Journal-фикса

| | |
|--|--|
| **Проблема** | На устройстве зависание / kill при **Day Journal** («Где телефон» / дневник дня). |
| **Симптом** | После открытия журнала UI «встаёт»; перезапуск; в diagnostics — *Inferred unclean termination*. |
| **Гипотеза тогда** | Тяжёлый SwiftUI re-diff + аватары / карта / GPS. |
| **Что ещё в 27** | Policy A antifake (trial), SSL pin, heroes, geofence logs — **не** первопричина Journal hang. |
| **Коммит** | `5cadbed9` feat(build 27)… |

### Build 28 — фикс Journal (Image / UIKit)

| | |
|--|--|
| **Проблема (IPS ранее)** | `0x8BADF00D` · main thread · SwiftUI `Image.NamedImageProvider.==` / ForEach при живом GPS. |
| **Решение в коде** | `WhereIsPhoneScreen`: UIKit-аватар (`JournalAvatarUIImageView`), LazyVStack, отложенный тяжёлый контент, trip map по тапу, убран `.id(memberAvatarEpoch)` с горячего пути. |
| **Коммит** | `e401e2e0` feat(build 28): fix Day Journal 8BADF00D… |
| **Итог на устройстве** | Journal-путь улучшен, но **новый IPS 2026-11-17** показал **другую** причину (см. ниже). Поэтому казалось, что «5 правок не помогают» — это был **второй** класс бага. |

### Build 28 — IPS `ALADDIN-2026-11-17-014852.ips` (не Journal)

| Поле | Значение |
|------|----------|
| Build | **28** · 1.0.2 |
| Устройство | iPhone SE 2 (`iPhone12,8`) · iOS 26.7 |
| Тип | `EXC_CRASH` / `SIGKILL` · **`0x8BADF00D`** |
| Смысл | *Failed to terminate gracefully after 5.0s* · `WatchdogEvent: process-exit` |
| Main thread | **`SecItemCopyMatching`** (Keychain → securityd) |
| Выше по стеку | SwiftUI `ScrollView` → `ZStack` → layout / body |
| Термал | **Thermal State: serious** (усиливает таймаут) |
| Diagnostics txt | Пустой crash log + unclean termination — ожидаемо |

**Корневая причина:** каждый get `AppConfig.authToken` ходил в Keychain. Чтение токена из SwiftUI `body`/layout при выходе = блокировка main > 5 с → watchdog.

### Build 29 — фикс Keychain hot-path + скрытие диагностики

| Решение | Файлы |
|---------|--------|
| In-memory cache `authToken`; get после warm/set без `SecItem*` | `Core/Config/AppConfig.swift` |
| `warmAuthTokenCache()` в `init` + deferred bootstrap | `ALADDINApp.swift` |
| DEBUG: warning при fill на main; счётчик `secItemCopyMatchingCallCount` | `KeychainManager.swift` |
| SessionExpired → `AppConfig.authToken = nil` | `ALADDINApp.swift` |
| Убран двойной Keychain load в Family | `Screens/02_FamilyScreen.swift` |
| Unit: get после set/warm не зовёт SecItem | `Tests/UnitTests/AppConfigTests.swift` |
| «Диагностика (Crash Logs)» только DEBUG | `Screens/05_SettingsScreen.swift` |
| Journal-фиксы **не откатывали** | `WhereIsPhoneScreen` (с 28) |

---

## Две разные проблемы (не путать)

```text
A) Day Journal hang     → Image/ForEach/GPS re-diff     → фикс UI в build 28
B) Exit/background kill → SecItemCopyMatching in body   → cache token в build 29
```

Оба дают **`0x8BADF00D`**, но стеки разные.

---

## Build 29 — IPS `ALADDIN-2026-11-17-032822.ips`: A и B — один класс

| Поле | Значение |
|------|----------|
| Build | **29** · iPhone SE 2 (`iPhone12,8`) · iOS 26.7 · uptime 113 s |
| Тип | `0x8BADF00D` · `process-exit` · Foreground · Thermal fair |
| Main thread | `_UIHostingView.layoutSubviews → render → PlatformViewChild → UILabel traitCollectionDidChange` · **ни одного кадра нашего кода, нет SecItem** |

Сводка всех ноябрьских IPS (builds 24, 25, 27, 28, 29) — **одно устройство, один класс**:

- каждый раз main thread внутри SwiftUI render (`ViewGraphRootValueUpdater.render`), верхний кадр каждый раз другой (ButtonBehavior, ResolvedTextFilter, Image ==, SecItem, UILabel traits);
- `Elapsed application CPU` для `process-exit` ≈ **5 s из 5 s окна** (4.6–5.3) — main **считал** всё окно, а не ждал; это верно и для build 28 (SecItem был кадром-снимком, не причиной; кэш токена всё равно полезен);
- в `aladdin_diagnostics_1794865855.txt` у убитых сессий build 27/28 после `active` **нет** `willResignActive`/`inactive` — UI завис на экране **до** того, как пользователь закрыл приложение.

Apple: «the main thread’s backtrace doesn’t always contain the source of the issue» — [Addressing watchdog terminations](https://developer.apple.com/documentation/xcode/addressing-watchdog-terminations). Чинить верхний кадр — бесполезно.

### Где на самом деле краш (подтверждено владельцем 2026-11-17)

Путь воспроизведения — **всегда один**:

```text
Главная (Aladdin start) → дверь «Где семья» (WhereIsPhoneScreen, карта)
  → тап по СВОЕМУ аватару на карте → лист «Журнал дня» (memberDetailSheet)
  → через ~1–2 мин UI «встаёт» → пользователь смахивает → 0x8BADF00D process-exit
```

### Корневой механизм (по коду, build 29)

1. `WhereIsPhoneScreen` держит `@StateObject liveLocation = FamilyMapLiveLocationController.shared` — **весь** объект.
2. `FamilyMapLiveLocationController.didUpdateLocations` на **каждый** GPS-фикс писал в `@Published` без проверки «изменилось ли»: `accuracyMeters` (всегда), `isPreciseLocationEnabled` (всегда то же значение), `coordinate`, `updatedAt`, `speedKmh`. `@Published` шлёт `objectWillChange` даже при равном значении.
3. После «Обновить точку» (`requestFreshFix`) — `kCLLocationAccuracyBest` + `distanceFilter = none` → фиксы ~1/с.
4. Каждый фикс → пересчёт **всего** `body` WhereIsPhoneScreen, а лист журнала строится внутри этого body (`.sheet(item: $selectedMember) { memberDetailSheet(member) }`) → пересобираются два сегментных `Picker` (UISegmentedControl/UILabel), DatePicker, Slider, аватары, ForEach поездок/мест.
5. Плюс под листом продолжала крутиться бесконечная пульсация дверей и карусель SimpleHome (главная лежит под листом «Где семья»).
6. A13 (SE 2) + нагрев → main thread занят на 100 % → экран не отвечает → смахивание → 5 s без ответа → kill.

Это объясняет **все** стеки: build 27 `Image ==`/`ForEach` (аватары журнала), build 29 `PlatformViewChild → UILabel traits` (сегментные Picker журнала), build 25/28 разные листья того же render. Build 28 (`journalNearPlaceSnapshot`, UIKit-аватар) уменьшил вес одного кадра, но **не** частоту пересчётов — поэтому краш остался.

### Build 30 — что сделано (TF 1.0.2 / 30, `feat(build 30)` на master; симулятор-смоук владельца 2026-11-17 OK, Device QA SE 2 — ⏳)

| # | Изменение | Файлы | Зачем |
|---|-----------|-------|-------|
| 1 | **GPS на паузе, пока открыт «Журнал дня»**: `setOverlayPaused(true)` в `onAppear` листа, `false` в `onDisappear`; возобновление только если карта ещё открыта (`active`); в паузе `requestFreshFix`/смена разрешения не запускают GPS, «запоздавшие» фиксы отбрасываются | `Screens/FamilySafetyRemainderHub.swift`, `Screens/WhereIsPhoneScreen.swift` | **Главный фикс.** Журнал показывает снимок, карта под листом не видна — живые фиксы там только жгли CPU |
| 2 | Публикация только при реальном изменении: `isPreciseLocationEnabled`, `authStatus`, `speedKmh`; `accuracyMeters` — корзины по 5 м | `Screens/FamilySafetyRemainderHub.swift` | На самой карте пересчётов в разы меньше; бейдж «±N м» остаётся честным |
| 3 | `.decorativePulse()` вместо `withAnimation(.repeatForever)` в `onAppear`; пульс стоп при: лист поверх главной, не-active, Reduce Motion, Low Power, thermal ≥ serious | `Core/UX/DecorativeMotion.swift`, `Screens/SimpleHomeScreen.swift` | Главная не рендерит кадры под листом «Где семья → Журнал» |
| 4 | Карусель героя пропускает смену кадра, пока поверх открыт лист / приложение не active / горячо / Low Power | `Screens/SimpleHomeScreen.swift` | То же; на видимой главной карусель работает как раньше (6.5 s) |
| 5 | Убран `repeatForever` с эмодзи статуса (4 места), мёртвый `value: true` | `02_FamilyScreen`, `FamilyModals`, оба `FamilyMemberCard` | Тот же анти-паттерн, профилактика |
| 6 | MetricKit: hang/crash/CPU-диагностики → `Documents/MetricKit/*.json` (Файлы → ALADDIN), строка в lifecycle trace | `Core/Monitoring/HangDiagnosticsRecorder.swift`, `ALADDINApp.swift` | Следующий зависон придёт со стеком **нашего** кода, а не листа UIKit |
| 7 | Unit-тесты политики анимаций (5 кейсов) | `Tests/UnitTests/DecorativeMotionPolicyTests.swift` | |
| 8 | Регистрация 3 новых файлов | `ALADDIN.xcodeproj/project.pbxproj` (`DMOT*`, `HANGR*`, `DMOTT*`) | `plutil -lint` OK |

Static verify: `xcrun swiftc -parse` по всем изменённым файлам — OK. **Сборка / симулятор / устройство — не запускались** (ждёт GO владельца).

### Было → стало

| | Было (build 27–29) | Стало (build 30) |
|---|---|---|
| Журнал дня открыт | GPS ~1 фикс/с → каждый фикс пересобирает карту + журнал | GPS на паузе, журнал статичен, пересчётов от GPS 0 |
| Карта «Где семья» | Пересчёт на каждый фикс, даже если ничего не поменялось | Только при реальной смене точки/точности ≥ 5 м |
| Главная под листом | Пульс дверей и карусель крутятся невидимо | Стоят, пока лист открыт |
| Пользователь | Журнал «замерзает», телефон греется, приложение вылетает | Журнал листается, после закрытия — точка снова живая |
| Диагностика | `.ips` без нашего кода | + MetricKit JSON в Файлах |

Для пользователя ничего не исчезло: точка на карте живая, «Обновить точку» работает, карусель на главной меняется каждые 6.5 s. Пока открыт журнал, точка «замирает» на последнем значении (журнал и так показывает снимок); фоновые значимые перемещения (`LocationManager` SLC) не трогали.

### Коммит

Только на `master`, только файлы из таблицы выше + этот документ. Не включать прочие незакоммиченные правки рабочей копии (Chat, Buttons, DevicePairingModal, `.cursor/…`), `telegram_stars_shop_bot/`, `.env`, VPN handoff. Push — по «GO на push»; номер сборки — по «GO на bump» (+1 от фактического `CFBundleVersion`).

**Закрытие (не «нет конкретного кадра», а):** iPhone SE 2: Где семья → свой аватар → Журнал дня, «Обновить точку» перед открытием, 10 мин листать / переключать «Сегодня / Неделя / Свой период», затем свернуть и смахнуть → нет нового `0x8BADF00D`; Instruments (Hangs + SwiftUI) без зависаний > 250 ms и без пересчётов body от `liveLocation` при открытом журнале; `Documents/MetricKit/` без `hangDiagnostics` за сутки.

---

## Build 30 — краш НЕ закрыт (Device, 2026-11-17 13:26–13:28)

IPS: `ALADDIN-2026-11-17-132620.ips`, `…132649.ips`, `…132811.ips` · все **1.0.2 (30)** · iPhone SE 2 · iOS 26.7 · `0x8BADF00D process-exit` · app CPU **5.08–5.34 s из 5 s** · жизнь процесса **50 s / 25 s / 75 s** · thermal fair / fair / **serious**. Владелец: Журнал дня — краш всегда; карта «Где семья» — 1 из 3.

Бинарь CI-артефакта `ALADDIN-IPA` (run `44047438056`) — UUID `6EDD5624-0F42-3D4A-BD4E-AD44768E2884` = UUID в IPS. Символов нет (stripped), функции опознаны по строковым литералам рядом с адресами (`/tmp/b30/strs.py`, adrp+add → `__cstring`).

| IPS | Main thread (сверху вниз) | Наш код |
|-----|---------------------------|---------|
| 132620 | `Button initializeWithCopy` → `DynamicBody.updateValue` → render | нет |
| **132649** | `replacingOccurrences` ← `FamilyLocalStore` (JWT payload decode) ← **`SimpleHomeScreen` body** (`pay_pains_family_strip`) ← `ScrollView` ← `ZStack` ← render | **да** |
| 132811 | `libswiftObservation` → `StaticBody.updateValue` → render | нет |

### Что не предусмотрели в build 28–30

1. **Главная (SimpleHome) делает I/O в `body`.** `payPainsFamilyStrip` → `FamilyLocalStore.loadPersistedMembers()` → `validatePersistedRosterAgainstCurrentFamily()` → `loadPersistedFamilyId()` → `currentJWTUserId()` → **`KeychainManager.loadString(.authToken)` напрямую (в обход кэша build 29)** + base64/`replacingOccurrences`/`JSONSerialization` JWT + ещё Keychain (scoped `family_id`) + `JSONDecoder` ростера; плюс `subscriptionManager.effectiveFamilyDisplay()` → `persistedLocalRosterCount()` → второй `JSONDecoder`. Это на **каждый** пересчёт body главной.
2. **«Где семья» — `.sheet` внутри body главной** (`SimpleHomeScreen.swift` ~155–172), а `WhereIsPhoneScreen(isPresented:onLeaveToNavigate:)` хранит замыкание → SwiftUI не может сравнить вью (closures non-diffable) → **любой** пересчёт главной (publish `SubscriptionManager` / `LocalizationManager` / @State) заново считает весь хаб карты **и** открытый Журнал дня. Build 30 убрал только один источник (GPS); остальные `@EnvironmentObject` публикации остались.
3. Build 29 закэшировал `AppConfig.authToken`, но `FamilyLocalStore.currentJWTUserId()` читает Keychain сам — тот же класс, что build 28 (`SecItemCopyMatching`).
4. Симулятор не воспроизводит: M-серия Mac в разы быстрее A13, Keychain в симуляторе — файл, нет живого GPS/термала.

Build 30 правки на карте только **уменьшают** публикации (dedupe) и ставят GPS на паузу под журналом — новой работы не добавляют. Крах на карте 1/3 — тот же механизм (п.1–2), шанс выше при нагреве (IPS 132811 thermal serious).

### Локализация (EN в приложении, телефон RU-регион)

| Где | Баг | Причина |
|-----|-----|---------|
| Журнал дня, чип даты «С вторника, 17 ноября» | RU дни/месяцы в EN | `dayJournalDateLabel` → `Locale.autoupdatingCurrent` (локаль телефона), а не `LocalizationManager.locale` |
| Карта, «Последняя точка» как имя точки | RU текст в EN | `WherePhoneLastPointStore.save(name: mapPointName ?? localized("where_phone_map_card_title"))` — **сохраняется переведённая строка**, потом показывается как имя |
| Неделя / Свой период | проверить `DatePicker` и подписи периода | `environment(\.locale)` есть в корне; лист — проверить на устройстве |

### План build 31 (код)

1. SimpleHome: снимок полоски семьи в `@State`, обновлять на `onAppear` + `FamilyMembersUpdated`; `effectiveFamilyDisplay(localRosterCount:)` из снимка. В body — 0 Keychain / JSON.
2. `FamilyLocalStore`: `currentJWTUserId()` через `AppConfig.authToken` (memory) + memo payload по токену; memo `loadPersistedFamilyId()` по uid (сброс в persist/clear); memo decode ростера по `Data`.
3. Изолировать лист «Где семья» от пересчётов главной: обёртка `Equatable` (`.equatable()`), без хранения замыканий-строителей.
4. Журнал дня — отдельная `struct` со снимком входных данных (не наблюдает `liveLocation`, не пересчитывается от хаба).
5. Локализация: дата журнала из `LocalizationManager.shared.locale`; не сохранять переведённый fallback как имя точки; `friendlyPointName` мапит старые RU/EN fallback-строки.
6. Доказательства до TF: MetricKit JSON с телефона (`Файлы → ALADDIN → MetricKit`) + Instruments (SwiftUI + Hangs) на SE 2 по сценарию журнала.

### Build 31 — что сделано (TF 1.0.2 / 31, коммит `7851780f` на master, 2026-11-17)

| # | Было | Стало | Файл |
|---|------|-------|------|
| 1 | `body` главной: `loadPersistedMembers()` + `effectiveFamilyDisplay()` (Keychain + JWT + JSON) на каждый рендер | `@State` снимок (`familyStripRosterCount`, `familyStripFirstName`), обновление в `onAppear` + `FamilyMembersUpdated`; `effectiveFamilyDisplay(localRosterCount:)` | `Screens/SimpleHomeScreen.swift` |
| 2 | Каждый вызов: Keychain + base64/JSON токена, 2 чтения Keychain для `family_id`, декод ростера ×2 | memo payload по строке токена; memo `family_id` по uid (сброс: `persistFamilyId`, clear, `RecoveryCodeStorageManager` save/delete); memo декода ростера по `Data` | `Core/Managers/FamilyLocalStore.swift`, `Core/Security/RecoveryCodeStorageManager.swift` |
| 3 | `WhereIsPhoneScreen` (хранит замыкание) пересчитывался целиком на каждый рендер главной | `WherePhoneSheetHost: Equatable` + `.equatable()` — родитель больше не дёргает лист | `Screens/SimpleHomeScreen.swift` |
| 5 | Дата журнала / недели — локаль телефона; DatePicker — локаль телефона; «Последняя точка»/«Вы» из сохранённого имени | `dayJournalDateLabel(locale:)` / `weekStartLabel(locale:)` = язык приложения; `.environment(\.locale)` на DatePicker журнала и календаря; `friendlyPointName` переводит сохранённые RU/EN fallback-строки | `Screens/WhereIsPhoneScreen.swift` |

Отклонено от плана:
- **п.2:** `currentJWTUserId()` оставлен на Keychain, не на `AppConfig.authToken`. Регистрация (`FamilyRegistrationViewModel`) и refresh (`JWTTokenManager`) пишут токен в Keychain напрямую и сразу зовут `reconcileFamilyContextWithCurrentJWT()` — кэш `AppConfig` там отстаёт (отдельный латентный баг, не чинили без GO). Горячий путь из `body` убран п.1.
- **п.4 (журнал в отдельную struct):** отложен до Instruments. Это перенос ~300 строк с десятком `@State` в mega-file; п.1+3 уже снимают оба доказанных усилителя. Делать, если Instruments покажет пересчёт журнала от `liveLocation`.

Static: `swiftc -parse` 5 файлов OK · `verify_capabilities_wave3_static.sh` ALL OK. Тест: `FamilyLocalStorePersistenceTests.testLoadPersistedFamilyIdSeesRecoveryCodeWrite` (+ сброс memo в setUp/tearDown).

### Build 31 — коммит и CI

| Что | Значение |
|-----|----------|
| Коммит | `7851780f feat(build 31): fix 8BADF00D — no Keychain/JWT/JSON in SimpleHome body, isolate family sheet, journal locale` |
| Push | `master` → `git@github.com:sergey234/ALADDIN_FAMILY.git` (`c502d4e4..7851780f`) |
| CI | `check-secrets.yml` «Build and Upload to App Store», run `44062666545` (статус — `gh run view 44062666545`) |
| Bump 30→31 | 7× `Info.plist` (app, CallDirectory, DeviceActivityMonitor, DeviceActivityReport, ShieldConfiguration, ShieldAction, ContentFilter) · 24× `CURRENT_PROJECT_VERSION` · `AppConfig.buildNumber` + `minimumClientBuildForApiContract` · `AppConfigTests` · `RELEASE_BUILD_PROMPT.md` / `ML_SYSTEM_HANDOFF_ASC_VERSION_BUILD_RU.md` (PREV 31 / NEXT 32) |
| Деплой сервера | Не нужен — правки только iOS |
| Не в коммите | бот, `.env`, VPN handoff §32, посторонние правки (Chat, Buttons, DevicePairingModal, `.cursor`, xcuserdata) |
| Instruments на SE 2 | Не проводился до TF — владелец собирает в Xcode сам; доказательство = Device QA TF 31 ниже |

### Кэш токена после refresh — проверено, риска нет

Опасение: `JWTTokenManager` refresh и `FamilyRegistrationViewModel.saveTokens` пишут токен прямо в Keychain, а кэш `AppConfig.authToken` остаётся старым.
Проверка кода: оба пути сразу обновляют кэш (`publishAccessTokenRefreshToClients` → `AppConfig.authToken`; регистрация — `AppConfig.authToken = accessToken`). Остаток: refresh обновляет кэш через `DispatchQueue.main.async` — повтор после 401, сделанный в ту же долю секунды, может уйти со старым токеном и получить ещё один 401. На краш и данные не влияет; отдельной задачей не делаем (при правках сети — присваивать синхронно).
`FamilyLocalStore.currentJWTUserId()` всё равно читает Keychain: `reconcileFamilyContextWithCurrentJWT()` вызывается между записью в Keychain и обновлением кэша.

### Итог: эволюция гипотез 27 → 31

| Build | Что считали причиной | Что сделали | Результат на SE 2 |
|-------|----------------------|-------------|-------------------|
| 27 | Тяжёлые `Image` / UIKit в журнале | — | краш |
| 28 | Журнал строит всё сразу | LazyVStack, отложенный heavy-контент | краш (стек SecItem) |
| 29 | Keychain `authToken` в body | кэш токена в памяти + warm на старте | краш |
| 30 | Живой GPS пересчитывает журнал | пауза GPS под журналом, дедуп publish, стоп декоративной анимации под sheet, MetricKit | краш (IPS: `SimpleHome.body` → `FamilyLocalStore` Keychain/JWT) |
| 31 | Главная под листом пересчитывает body с I/O + лист без diff | снимок плашки, memo FamilyLocalStore, `WherePhoneSheetHost: Equatable`, локаль журнала | симулятор OK (лог 14:22–14:24) |
| 32 | Разбор каждого участника семьи строил **весь** словарь переводов ×2 | `LocalizationManager()` → `.shared` в Codable/VM | ✅ **краша нет** (владелец, 2026-11-17) |

---

## ✅ Итог: что реально помогло (закрыто 2026-11-17, TF 32)

Владелец подтвердил на устройстве: после TF **32** краш 8BADF00D не повторяется.

**Первопричина:** `LocalizationManager()` создавался заново при разборе **каждого** участника семьи (`FamilyRole` / `ProtectionStatus` Codable) — полный словарь ~21k строк ×2 на участника, несколько раз на кадр главной. Главный поток уходил в CPU ~5 с → watchdog.

**Что помогло (по вкладу):**

1. **Build 32 — решающий фикс:** `LocalizationManager()` → `LocalizationManager.shared` в Codable семьи и VM (`d25f8bd6`).
2. **Build 31 — снял лишнюю нагрузку с body:** без Keychain/JWT/JSON в `SimpleHome.body`, memo `FamilyLocalStore`, `WherePhoneSheetHost: Equatable` (`7851780f`). Без него 32 тоже помог бы, но кадр оставался бы тяжёлым.
3. **Build 29–30 — гигиена, не корень:** кэш `authToken`, пауза GPS под журналом, дедуп publish. Полезно, но краш оставался.

**Что не помогло само по себе:** правки картинок/LazyVStack (28), кэш токена (29) — лечили симптомы из верхушки стека.

**Урок (правило на будущее):**
- В Release-коде **никогда** `LocalizationManager()` — только `.shared` (кроме `#Preview`). Проверка: `rg -n "LocalizationManager\(\)" --glob '*.swift' Core Screens Shared ViewModels Components UI` — на 2026-11-17 все попадания внутри `*_Previews: PreviewProvider` (в Release не исполняются).
- Верхушка стека IPS (Keychain, Image) ≠ причина: смотреть, **кто держит CPU** (симулятор + `STARTUP_TRACE` повторных `init`).
- Body SwiftUI — без I/O (Keychain, JWT, JSON decode).

---

## Build 32 — корень CPU: `LocalizationManager()` в разборе семьи (2026-11-17)

**Как нашли:** лог симулятора build 31 (14:24:11 / :15 / :18) — при каждом переходе на вкладку «Вождение» `STARTUP_TRACE: LocalizationManager.init BEGIN/END`. Поиск `LocalizationManager()` в рабочем коде.

**Главное:** `FamilyMemberCard.FamilyRole` и `FamilyMemberCard.ProtectionStatus` (`Screens/FamilyModals.swift`, `init(from decoder:)`) создавали **новый** `LocalizationManager()` на каждое декодирование значения. `FamilyMemberData` содержит оба поля → разбор ростера из N участников = **2×N полных построений словаря (~21k строк)**. В build 30 `SimpleHome.body` разбирал ростер 2–3 раза на кадр → это и есть ~5 с CPU в IPS (`FamilyLocalStore` в стеке — верхушка, словарь — тело работы).

| Место | Было | Стало |
|-------|------|-------|
| `FamilyModals.swift` `FamilyRole` / `ProtectionStatus` Codable, `AgeGroup.fromStoredValue` | `LocalizationManager()` на каждый вызов | `LocalizationManager.shared` |
| `02_FamilyScreen.swift` `AgeGroup.fromStoredValue` | то же | `.shared` |
| `PaymentQRViewModel` (`displayName`, `compactDisplayName`, `localized`, `localizedFormat`, init fallback) | новый словарь на **каждую** строку | `.shared` |
| VM по умолчанию: `DrivingReports`, `AICategories`, `IdentityTheft/Monitor/Detect`, `AntifakeMediaCheck`, `DarkWebMonitoring`, `PrivacyReports` | `= LocalizationManager()` | `= .shared` |

Не трогали: `.environmentObject(LocalizationManager())` в `#Preview` / `PreviewProvider` (в Release не исполняются).
Семантика та же: новый экземпляр читал язык из UserDefaults, `shared` держит тот же язык; класс не `@MainActor`, `localized()` под lock.
Static: `swiftc -parse` 11 файлов OK; mega-files — точечно, `wc -l` без изменений.

---

## Можно ли проверить на симуляторе?

| Проверка | Сим | Устройство / TestFlight |
|----------|-----|-------------------------|
| Unit-тесты кэша токена | Да | — |
| Settings без пункта Диагностика (Release) | Да (после сборки Release/TF) | Да |
| Полный IPS `process-exit` + SecItem + thermal | Редко / нет | **Да — канон доказательства** |
| Journal scroll + GPS | Частично | Да |

**Вывод:** сим — smoke G2/G4 и unit; **закрытие краша B** — новый `.ips` на телефоне после TF **29** без SecItem в стеке watchdog.

---

## Чеклист Device QA после TF 29

1. Установить build **29**.
2. Пройти SimpleHome → Где семья / Journal → свернуть / убить приложение при «теплом» телефоне.
3. Снять новый `.ips` при повторе (если будет) — стек **не** должен начинаться с `SecItemCopyMatching` из UI body.
4. Настройки: пункта «Диагностика» **нет** (Release).
5. Journal: нет зависания как на 27.

## Чеклист Device QA после TF 31 (SE 2)

1. Установить build **31** (Настройки → О приложении / TestFlight: 1.0.2 (31)).
2. Главная → «Обновить точку» → «Где семья» (карта): 3 входа подряд — без краша (на 30 было 1 из 3).
3. Свой аватар → «Журнал дня»: 10 мин переключать День / Неделя / Свой период, скролл; затем свернуть и смахнуть приложение — без краша.
4. Повторить п.3 на «тёплом» телефоне (после зарядки / навигации) — thermal fair/serious был у всех IPS build 30.
5. Язык приложения EN: дата «Tuesday, November 17» (не «вторник, 17 ноября»), «Last point» / «You», DatePicker «Свой период» и календарь — английские месяцы.
6. Плашка семьи на главной: «Семья · N из M» и инициал совпадают с экраном Семья; после добавления участника обновляется.
7. Если краш: `.ips` из Аналитики + JSON из «Файлы → ALADDIN → MetricKit» → в этот файл новой секцией «Build 31 — IPS».

---

## Связанные артефакты владельца

- `~/Downloads/ALADDIN-2026-11-17-014852.ips`
- `~/Downloads/ALADDIN-2026-11-17-032822.ips` (build 29)
- `~/Downloads/ALADDIN-2026-11-17-132620.ips`, `…132649.ips`, `…132811.ips` (build 30, SE 2, iOS 26.7)
- IPA build 30 для символизации: CI run `44047438056`, артефакт `ALADDIN-IPA`, UUID `6EDD5624-0F42-3D4A-BD4E-AD44768E2884`
- `~/Downloads/aladdin_diagnostics_1794865855.txt`
- ASC capture helper: `scripts/asc_capture_10_screens_prepare.sh`
