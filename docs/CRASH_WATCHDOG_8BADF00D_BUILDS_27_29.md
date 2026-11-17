# Краши watchdog 8BADF00D — сводка сборок 27→29 (Day Journal + Keychain)

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

---

## Связанные артефакты владельца

- `~/Downloads/ALADDIN-2026-11-17-014852.ips`
- `~/Downloads/aladdin_diagnostics_1794865855.txt`
- ASC capture helper: `scripts/asc_capture_10_screens_prepare.sh`
