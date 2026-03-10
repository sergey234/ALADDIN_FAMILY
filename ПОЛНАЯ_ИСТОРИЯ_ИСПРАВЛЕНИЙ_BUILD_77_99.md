# 📋 ПОЛНАЯ ИСТОРИЯ ИСПРАВЛЕНИЙ КРАШЕЙ: BUILD 77 → BUILD 99

**Период:** BUILD 77 - BUILD 99  
**Тип проблемы:** `EXC_BAD_ACCESS (SIGSEGV)` - `Thread stack size exceeded due to excessive recursion`  
**Дата создания:** 2026-03-10

---

## 📊 ОБЗОР ПРОБЛЕМЫ

### 🔴 Основная проблема:
Рекурсия в различных местах приложения, вызывающая переполнение стека и краш приложения.

### 🔴 Типы рекурсии:
1. **Рекурсия через `@AppStorage` → `UserDefaults` → `@AppStorage`**
2. **Рекурсия через `DateFormatter` с `Locale.current`**
3. **Рекурсия через SwiftUI lifecycle модификаторы (`.onChange()`, `.id()`)**
4. **Рекурсия через computed properties**

---

## 🔴 BUILD 77-86: ПЕРВЫЕ ПРОБЛЕМЫ

### Проблема:
- Рекурсия в `os_log` из-за `Task {}` внутри `withCheckedThrowingContinuation`
- Избыточное логирование с эмодзи в RELEASE сборках

### Исправления:
1. ✅ Убраны `Task {}` из `withCheckedThrowingContinuation` в `APIService.swift`
2. ✅ Отключен `os_log` в RELEASE сборках
3. ✅ Убраны эмодзи из `os_log` сообщений

**Файлы:**
- `Core/Network/APIService.swift`
- `Core/Utilities/MasterLogger.swift`

---

## 🔴 BUILD 88-90: РЕКУРСИЯ В DATEFORMATTER

### Проблема:
- `DateFormatter` создавался в computed properties
- Использование `Locale.current` и `Locale.preferredLanguages` читало из `UserDefaults`
- Это создавало циклическую зависимость с `@AppStorage`

### Исправления:
1. ✅ Все `DateFormatter` заменены на статические экземпляры
2. ✅ Использование статического `Locale(identifier:)` вместо `Locale.current`
3. ✅ Исправлены файлы:
   - `ViewModels/AIAssistantViewModel.swift`
   - `ViewModels/ProfileViewModel.swift`
   - `Screens/ChildRewardsScreen.swift`
   - `Core/Models/ComponentReportsModels.swift`
   - `ViewModels/ActivationCodeViewModel.swift`

---

## 🔴 BUILD 91: РЕКУРСИЯ В MAINSCREEN

### Проблема:
- Computed property `subscriptionExpirationText` читала из `@AppStorage`
- Это вызывало рекурсию через `UserDefaults`

### Исправления:
1. ✅ Заменена computed property на `@State private var cachedExpirationText`
2. ✅ Добавлена функция `updateExpirationTextCache()` для обновления кеша
3. ✅ Вызов функции в `.onAppear {}`

**Файлы:**
- `Screens/01_MainScreen.swift`

**Проблема этого решения:**
- `.onAppear {}` вызывается при каждом обновлении View
- Обновление `@State` вызывает перерисовку View
- Это может вызвать рекурсию (исправлено в BUILD 99)

---

## 🔴 BUILD 92: РЕКУРСИЯ ЧЕРЕЗ SWIFTUI МОДИФИКАТОРЫ

### Проблема:
- `.onChange(of: subscriptionExpiresAtIso)` вызывал рекурсию
- `.id("main_lang_\(localizationManager.currentLanguage.rawValue)")` вызывал рекурсию
- Прямые вызовы `UserDefaults.standard` в `body` и `onAppear`

### Исправления:
1. ✅ Убран `.onChange(of: subscriptionExpiresAtIso)`
2. ✅ Убран `.id()` модификатор с `localizationManager`
3. ✅ Убраны прямые `UserDefaults.standard` вызовы из `body` и `onAppear`
4. ✅ Все `UserDefaults` операции сделаны асинхронными через `Task {}`
5. ✅ `updateExpirationTextCache()` принимает параметр вместо чтения `@AppStorage`
6. ✅ Заменены `UserDefaults.standard.bool()` на `@AppStorage` для onboarding

**Файлы:**
- `Screens/01_MainScreen.swift`

---

## 🔴 BUILD 93: РЕКУРСИЯ В ЛОГГЕРАХ

### Проблема:
- `MasterLogger.enableVisualLogging` использовал `@AppStorage` в singleton
- `VisualLogger` читал из `UserDefaults` при инициализации
- Логгеры вызывались синхронно

### Исправления:
1. ✅ `MasterLogger.enableVisualLogging` заменен на computed property с `UserDefaults.standard`
2. ✅ Убрана инициализация `enableVisualLogging = true` из `init()`
3. ✅ Все вызовы `MasterLogger.shared.business` и `MasterLogger.shared.performance` обернуты в `Task {}`
4. ✅ `VisualLogger.loadLogsFromUserDefaults()` вынесен в `loadLogsAsync()`
5. ✅ Убран `.id()` модификатор из `ALADDINApp.mainAppContent()`
6. ✅ Убраны ранние вызовы `VisualLogger.shared.log()` из `init()`

**Файлы:**
- `Core/Utilities/MasterLogger.swift`
- `Core/Utilities/VisualLogger.swift`
- `ALADDINApp.swift`

---

## 🔴 BUILD 94: ДИАГНОСТИКА И PRE-CRASH STATE

### Проблема:
- Недостаточно диагностики для анализа крашей на реальных устройствах

### Добавлено:
1. ✅ Глобальный crash handler в `AppDelegate.swift`
2. ✅ Сохранение crash logs в `UserDefaults` и файлы
3. ✅ Отправка crash reports на сервер
4. ✅ Memory warning handler
5. ✅ Pre-crash state saving (периодическое сохранение состояния)
6. ✅ Функции для получения crash logs: `getCrashLogs()`, `getAllCrashLogs()`, `getCrashLogsFromFiles()`

**Файлы:**
- `AppDelegate.swift`
- `ALADDINApp.swift`

---

## 🔴 BUILD 95: ДОПОЛНИТЕЛЬНЫЕ ДИАГНОСТИЧЕСКИЕ ИНСТРУМЕНТЫ

### Добавлено:
1. ✅ `RecursionMonitor` - мониторинг глубины рекурсии
2. ✅ `StackSizeMonitor` - мониторинг размера стека
3. ✅ `MonitoredUserDefaults` - обертка для мониторинга `UserDefaults`
4. ✅ `MonitoredAppStorage` - обертка для мониторинга `@AppStorage`
5. ✅ `CrashLogsView` - UI для просмотра crash logs в приложении

**Файлы:**
- `Core/Diagnostics/RecursionMonitor.swift` (новый)
- `Core/Diagnostics/StackSizeMonitor.swift` (новый)
- `Core/Diagnostics/MonitoredUserDefaults.swift` (новый)
- `Core/Diagnostics/MonitoredAppStorage.swift` (новый)
- `Screens/CrashLogsView.swift` (новый)

---

## 🔴 BUILD 96: ИСПРАВЛЕНИЯ В SETTINGS И FAMILY SCREENS

### Проблема:
- Синхронные операции с `UserDefaults` в `SettingsViewModel`
- Синхронные операции с `UserDefaults` в `FamilyScreen`

### Исправления:
1. ✅ Все `UserDefaults.standard.set()` обернуты в `Task { @MainActor in }` в `SettingsViewModel`
2. ✅ `loadInitialState()` в `SettingsViewModel` обернут в `Task { @MainActor in }`
3. ✅ `loadIsAdmin()` сделан асинхронным с кешированием
4. ✅ `loadAppLimits()` в `FamilyScreen` обернут в `Task { @MainActor in }`
5. ✅ Добавлен кеш `cachedParentalRules` в `FamilyParentalControlSettingsModal`
6. ✅ Исправлен `MasterLogger.enableVisualLogging` с thread-safe кешированием через `Thread.current.threadDictionary`
7. ✅ Убрано `UserDefaults.set(false)` из `ALADDINApp.initializeNavigation()` (предотвращает рекурсию)

**Файлы:**
- `ViewModels/SettingsViewModel.swift`
- `Screens/02_FamilyScreen.swift`
- `Core/Utilities/MasterLogger.swift`
- `ALADDINApp.swift`

---

## 🔴 BUILD 97: КРАШ В ОНБОРДИНГЕ

### Проблема:
- Конфликт `@AppStorage` между `OnboardingScreen` и `ALADDINApp`
- Убрали `UserDefaults.set(false)` - рассинхронизация
- `MasterLogger.enableVisualLogging` читал из `UserDefaults` при инициализации

### Исправления:
1. ✅ Вернули установку `false` в `initializeNavigation()` (асинхронно)
2. ✅ Исправили `MasterLogger.enableVisualLogging` (не читать из `UserDefaults` при инициализации)
3. ✅ Разрешили конфликт `@AppStorage` между `OnboardingScreen` и `ALADDINApp`
   - Заменили `@AppStorage` на `@State` в `OnboardingScreen`
   - Синхронизация через `onAppear` и `Task { @MainActor in }`

**Файлы:**
- `ALADDINApp.swift`
- `Core/Utilities/MasterLogger.swift`
- `Screens/14_OnboardingScreen.swift`

---

## 🔴 BUILD 98: РЕКУРСИЯ В DATEFORMATTER (ПОВТОРНАЯ ПРОБЛЕМА)

### Проблема:
- `DateFormatter()` создавался в функциях без статического `Locale`
- Использование `Locale.current` читало из `UserDefaults`
- Рекурсия в ICU библиотеке при форматировании даты

### Исправления:
1. ✅ Исправлен `getCrashLogs()` - добавлен статический `crashTimeFormatter` с `Locale(identifier: "ru_RU")`
2. ✅ Исправлен `RelativeDateTimeFormatter` в `SubscriptionManager` - заменен `Locale.current` на `Locale(identifier: "ru_RU")`
3. ✅ Исправлен `DateFormatter` в `AppDelegate` crash handler - добавлен статический `crashLogFormatter`
4. ✅ Исправлен `DateFormatter` в `FamilyScreen` Button actions - добавлен статический `timeFormatter`
5. ✅ Добавлены статические форматтеры в `ScheduleSettingsModal` и `SleepTimeSettingsModal`

**Файлы:**
- `ALADDINApp.swift`
- `Core/Managers/SubscriptionManager.swift`
- `AppDelegate.swift`
- `Screens/02_FamilyScreen.swift`

---

## 🔴 BUILD 99: ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ РЕКУРСИИ В MAINSCREEN

### Проблема:
- `updateExpirationTextCache()` вызывалась в `.onAppear {}`
- Обновление `@State` вызывало перерисовку View
- Перерисовка View вызывала `.onAppear {}` снова
- Это создавало бесконечную рекурсию

### Исправления:
1. ✅ **ЭТАП 1:** Добавлена защита от рекурсии
   - Флаг `@State private var isUpdatingExpirationText: Bool = false`
   - Проверка флага перед вызовом функции
   - Использование `defer` для гарантированного сброса флага

2. ✅ **ЭТАП 2:** Функция сделана асинхронной
   - Функция `updateExpirationTextCache()` сделана `async`
   - Все обновления `@State` выполняются через `MainActor.run`
   - Вызов функции обернут в `Task { @MainActor in }`

3. ✅ **ЭТАП 3:** Заменено `.onAppear {}` на `.task {}`
   - `.task {}` вызывается только один раз при появлении View
   - Это предотвращает повторные вызовы при обновлении View

**Файлы:**
- `Screens/01_MainScreen.swift`

---

## 📊 СТАТИСТИКА ИСПРАВЛЕНИЙ

### По типам проблем:

| Тип проблемы | Количество исправлений | Builds |
|--------------|------------------------|--------|
| Рекурсия через `@AppStorage` | 15+ | 91, 92, 93, 96, 97 |
| Рекурсия через `DateFormatter` | 10+ | 88-90, 98 |
| Рекурсия через SwiftUI модификаторы | 5+ | 92 |
| Рекурсия через логгеры | 5+ | 93 |
| Рекурсия через lifecycle | 3 | 99 |

### По файлам:

| Файл | Количество исправлений |
|------|------------------------|
| `Screens/01_MainScreen.swift` | 8+ |
| `Core/Utilities/MasterLogger.swift` | 5+ |
| `ALADDINApp.swift` | 6+ |
| `Screens/02_FamilyScreen.swift` | 4+ |
| `AppDelegate.swift` | 3+ |
| `ViewModels/SettingsViewModel.swift` | 3+ |
| `Core/Managers/SubscriptionManager.swift` | 2+ |
| Другие файлы | 20+ |

---

## ✅ КЛЮЧЕВЫЕ ПРИНЦИПЫ ИСПРАВЛЕНИЙ

### 1. Статические форматтеры
- Все `DateFormatter` должны быть статическими
- Использовать `Locale(identifier:)` вместо `Locale.current`

### 2. Асинхронность
- Все операции с `UserDefaults` должны быть асинхронными
- Использовать `Task { @MainActor in }` для обновления `@State`

### 3. Защита от рекурсии
- Использовать флаги для предотвращения повторных вызовов
- Использовать `defer` для гарантированного сброса флагов

### 4. SwiftUI lifecycle
- Использовать `.task {}` вместо `.onAppear {}` когда возможно
- Избегать `.onChange()` и `.id()` с `@AppStorage`

### 5. Кеширование
- Использовать `@State` вместо computed properties для кеширования
- Использовать thread-safe кеширование через `Thread.current.threadDictionary`

---

## 🎯 РЕЗУЛЬТАТЫ

### До исправлений:
- ❌ Краши при каждом запуске приложения
- ❌ Рекурсия в различных местах
- ❌ Нет диагностики для анализа крашей

### После исправлений (BUILD 99):
- ✅ Все известные проблемы с рекурсией исправлены
- ✅ Добавлена диагностика для анализа крашей
- ✅ Все операции с `UserDefaults` асинхронные
- ✅ Все `DateFormatter` статические
- ✅ Защита от рекурсии в критичных местах

---

## 📝 ВЫВОДЫ

1. **Проблема была комплексной** - рекурсия возникала в разных местах по разным причинам
2. **Исправления были постепенными** - каждая сборка исправляла новые проблемы
3. **Системный подход** - использование единых принципов для всех исправлений
4. **Диагностика критична** - добавление инструментов для анализа помогло найти проблемы

---

**ГОТОВО!** 📋
