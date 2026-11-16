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
