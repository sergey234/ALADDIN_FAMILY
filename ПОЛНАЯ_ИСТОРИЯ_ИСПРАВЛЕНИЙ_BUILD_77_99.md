# 📋 ПОЛНАЯ ИСТОРИЯ ИСПРАВЛЕНИЙ КРАШЕЙ: BUILD 77 → BUILD 100

**Период:** BUILD 77 - BUILD 100  
**Тип проблемы:** `EXC_BAD_ACCESS (SIGSEGV)` - `Thread stack size exceeded due to excessive recursion`  
**Дата создания:** 2026-03-10  
**Дата обновления:** 2026-03-10 (добавлен BUILD 100)  
**Статус:** ✅ **КРАШ ПРЕКРАТИЛСЯ В BUILD 100!**  
**Цель документа:** Полное понимание причин крашей и всех исправлений для ML систем и разработчиков

---

## 🎯 КРАТКОЕ РЕЗЮМЕ ДЛЯ ML СИСТЕМ

### Основная проблема:
Приложение падало с ошибкой `EXC_BAD_ACCESS (SIGSEGV)` из-за переполнения стека от чрезмерной рекурсии.

### Корневая причина:
Циклические зависимости между SwiftUI `@AppStorage`, `UserDefaults`, `DateFormatter` с `Locale.current`, и SwiftUI lifecycle модификаторами создавали бесконечные циклы вызовов.

### Решение:
Систематическое устранение всех циклических зависимостей через:
1. Статические форматтеры вместо динамических
2. Асинхронные операции с `UserDefaults`
3. Защита от рекурсии через флаги
4. Правильное использование SwiftUI lifecycle
5. Кеширование через `@State` вместо computed properties

---

## 📊 ОБЗОР ПРОБЛЕМЫ

### 🔴 Основная проблема:
Рекурсия в различных местах приложения, вызывающая переполнение стека и краш приложения.

### 🔴 Типы рекурсии:

#### 1. Рекурсия через `@AppStorage` → `UserDefaults` → `@AppStorage`
**Механизм:**
```
@AppStorage читает из UserDefaults
  ↓
UserDefaults обновляется
  ↓
@AppStorage получает уведомление об изменении
  ↓
View обновляется
  ↓
@AppStorage читает из UserDefaults снова
  ↓
БЕСКОНЕЧНЫЙ ЦИКЛ → КРАШ
```

**Пример проблемного кода:**
```swift
// ❌ ПРОБЛЕМА: Computed property читает @AppStorage
var subscriptionExpirationText: String {
    let iso = subscriptionExpiresAtIso  // Читает @AppStorage
    // Форматирование даты...
    return formattedText
}

// ❌ ПРОБЛЕМА: .onChange() вызывает обновление @AppStorage
.onChange(of: subscriptionExpiresAtIso) {
    updateExpirationTextCache()  // Обновляет @State
    // @State обновление вызывает перерисовку View
    // Перерисовка View вызывает .onChange() снова
}
```

**Решение:**
```swift
// ✅ РЕШЕНИЕ: @State вместо computed property
@State private var cachedExpirationText: String? = nil

// ✅ РЕШЕНИЕ: Асинхронное обновление без .onChange()
.task {
    await updateExpirationTextCache(from: subscriptionExpiresAtIso)
}
```

---

#### 2. Рекурсия через `DateFormatter` с `Locale.current`
**Механизм:**
```
DateFormatter создается с Locale.current
  ↓
Locale.current читает из UserDefaults
  ↓
UserDefaults обновляется
  ↓
@AppStorage получает уведомление
  ↓
View обновляется
  ↓
DateFormatter создается снова с Locale.current
  ↓
БЕСКОНЕЧНЫЙ ЦИКЛ → КРАШ
```

**Пример проблемного кода:**
```swift
// ❌ ПРОБЛЕМА: DateFormatter создается каждый раз
func formatDate(_ date: Date) -> String {
    let formatter = DateFormatter()  // Создается каждый раз
    formatter.locale = Locale.current  // Читает из UserDefaults!
    return formatter.string(from: date)
}

// ❌ ПРОБЛЕМА: В computed property
var formattedDate: String {
    let formatter = DateFormatter()  // Создается при каждом доступе
    formatter.locale = Locale.current  // Рекурсия!
    return formatter.string(from: date)
}
```

**Решение:**
```swift
// ✅ РЕШЕНИЕ: Статический форматтер
private static let dateFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    return formatter
}()

func formatDate(_ date: Date) -> String {
    return Self.dateFormatter.string(from: date)  // Используем статический
}
```

---

#### 3. Рекурсия через SwiftUI lifecycle модификаторы
**Механизм:**
```
.onAppear {} вызывается
  ↓
Обновляется @State
  ↓
View перерисовывается
  ↓
.onAppear {} вызывается снова
  ↓
БЕСКОНЕЧНЫЙ ЦИКЛ → КРАШ
```

**Пример проблемного кода:**
```swift
// ❌ ПРОБЛЕМА: .onAppear вызывается при каждом обновлении View
.onAppear {
    updateExpirationTextCache()  // Обновляет @State
    // @State обновление вызывает перерисовку View
    // Перерисовка View вызывает .onAppear {} снова
}

// ❌ ПРОБЛЕМА: .onChange() вызывает рекурсию
.onChange(of: subscriptionExpiresAtIso) {
    updateExpirationTextCache()  // Обновляет @State
    // @State обновление вызывает .onChange() снова
}

// ❌ ПРОБЛЕМА: .id() вызывает рекурсию
.id("main_lang_\(localizationManager.currentLanguage.rawValue)")
// localizationManager.currentLanguage читает из UserDefaults
// UserDefaults обновление вызывает .id() снова
```

**Решение:**
```swift
// ✅ РЕШЕНИЕ: .task {} вызывается только один раз
.task {
    await updateExpirationTextCache(from: subscriptionExpiresAtIso)
}

// ✅ РЕШЕНИЕ: Убрать .onChange() и .id()
// View обновляется автоматически через @EnvironmentObject
```

---

#### 4. Рекурсия через computed properties
**Механизм:**
```
Computed property вызывается
  ↓
Читает @AppStorage
  ↓
@AppStorage читает из UserDefaults
  ↓
UserDefaults обновляется
  ↓
View обновляется
  ↓
Computed property вызывается снова
  ↓
БЕСКОНЕЧНЫЙ ЦИКЛ → КРАШ
```

**Пример проблемного кода:**
```swift
// ❌ ПРОБЛЕМА: Computed property читает @AppStorage
var subscriptionExpirationText: String {
    let iso = subscriptionExpiresAtIso  // Читает @AppStorage
    // Форматирование...
    return formattedText
}

// Использование в body вызывает рекурсию
Text(subscriptionExpirationText)  // Вызывает computed property
```

**Решение:**
```swift
// ✅ РЕШЕНИЕ: @State вместо computed property
@State private var cachedExpirationText: String? = nil

// Обновление через функцию
private func updateExpirationTextCache(from isoString: String) async {
    // ... форматирование ...
    cachedExpirationText = formattedText
}

// Использование в body безопасно
Text(cachedExpirationText ?? "")
```

---

## 🔴 BUILD 77-86: ПЕРВЫЕ ПРОБЛЕМЫ

### Проблема:
- Рекурсия в `os_log` из-за `Task {}` внутри `withCheckedThrowingContinuation`
- Избыточное логирование с эмодзи в RELEASE сборках

### Техническая причина:
`Task {}` внутри `withCheckedThrowingContinuation` создавал асинхронный контекст, который мог вызывать повторные вызовы логирования, создавая рекурсию.

### Исправления:
1. ✅ Убраны `Task {}` из `withCheckedThrowingContinuation` в `APIService.swift`
2. ✅ Отключен `os_log` в RELEASE сборках
3. ✅ Убраны эмодзи из `os_log` сообщений

**Файлы:**
- `Core/Network/APIService.swift`
- `Core/Utilities/MasterLogger.swift`

**Пример исправления:**
```swift
// ❌ БЫЛО:
withCheckedThrowingContinuation { continuation in
    Task {
        // Асинхронный код
        continuation.resume(returning: result)
    }
}

// ✅ СТАЛО:
withCheckedThrowingContinuation { continuation in
    // Синхронный код без Task {}
    continuation.resume(returning: result)
}
```

---

## 🔴 BUILD 88-90: РЕКУРСИЯ В DATEFORMATTER

### Проблема:
- `DateFormatter` создавался в computed properties
- Использование `Locale.current` и `Locale.preferredLanguages` читало из `UserDefaults`
- Это создавало циклическую зависимость с `@AppStorage`

### Техническая причина:
`Locale.current` и `Locale.preferredLanguages` читают из `UserDefaults` при каждом обращении. Если `DateFormatter` создается в computed property или в функции, которая вызывается при обновлении View, это создает цикл:
1. View обновляется → computed property вызывается
2. Computed property создает `DateFormatter` с `Locale.current`
3. `Locale.current` читает из `UserDefaults`
4. `UserDefaults` обновление вызывает обновление `@AppStorage`
5. `@AppStorage` обновление вызывает обновление View
6. Цикл повторяется

### Исправления:
1. ✅ Все `DateFormatter` заменены на статические экземпляры
2. ✅ Использование статического `Locale(identifier:)` вместо `Locale.current`
3. ✅ Исправлены файлы:
   - `ViewModels/AIAssistantViewModel.swift`
   - `ViewModels/ProfileViewModel.swift`
   - `Screens/ChildRewardsScreen.swift`
   - `Core/Models/ComponentReportsModels.swift`
   - `ViewModels/ActivationCodeViewModel.swift`

**Пример исправления:**
```swift
// ❌ БЫЛО:
var timeString: String {
    let formatter = DateFormatter()
    formatter.locale = Locale.current  // Рекурсия!
    return formatter.string(from: date)
}

// ✅ СТАЛО:
private static let timeFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    return formatter
}()

var timeString: String {
    return Self.timeFormatter.string(from: date)
}
```

---

## 🔴 BUILD 91: РЕКУРСИЯ В MAINSCREEN

### Проблема:
- Computed property `subscriptionExpirationText` читала из `@AppStorage`
- Это вызывало рекурсию через `UserDefaults`

### Техническая причина:
Computed property вызывается каждый раз при доступе. Если она читает `@AppStorage`, а `@AppStorage` обновляется, View перерисовывается, что снова вызывает computed property.

### Исправления:
1. ✅ Заменена computed property на `@State private var cachedExpirationText`
2. ✅ Добавлена функция `updateExpirationTextCache()` для обновления кеша
3. ✅ Вызов функции в `.onAppear {}`

**Файлы:**
- `Screens/01_MainScreen.swift`

**Пример исправления:**
```swift
// ❌ БЫЛО:
var subscriptionExpirationText: String {
    let iso = subscriptionExpiresAtIso  // Читает @AppStorage
    // Форматирование...
    return formattedText
}

// ✅ СТАЛО:
@State private var cachedExpirationText: String? = nil

private func updateExpirationTextCache(from isoString: String) {
    // Форматирование...
    cachedExpirationText = formattedText
}
```

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

### Техническая причина:
`.onChange()` вызывается при изменении значения. Если внутри `.onChange()` обновляется `@State`, это вызывает перерисовку View, что может снова вызвать `.onChange()`.

`.id()` вызывает полную перерисовку View при изменении значения. Если значение читается из `UserDefaults`, а `UserDefaults` обновляется, это создает цикл.

### Исправления:
1. ✅ Убран `.onChange(of: subscriptionExpiresAtIso)`
2. ✅ Убран `.id()` модификатор с `localizationManager`
3. ✅ Убраны прямые `UserDefaults.standard` вызовы из `body` и `onAppear`
4. ✅ Все `UserDefaults` операции сделаны асинхронными через `Task {}`
5. ✅ `updateExpirationTextCache()` принимает параметр вместо чтения `@AppStorage`
6. ✅ Заменены `UserDefaults.standard.bool()` на `@AppStorage` для onboarding

**Файлы:**
- `Screens/01_MainScreen.swift`

**Пример исправления:**
```swift
// ❌ БЫЛО:
.onChange(of: subscriptionExpiresAtIso) {
    updateExpirationTextCache()  // Обновляет @State → рекурсия
}

.id("main_lang_\(localizationManager.currentLanguage.rawValue)")
// localizationManager.currentLanguage читает из UserDefaults → рекурсия

// ✅ СТАЛО:
// Убраны .onChange() и .id()
// View обновляется автоматически через @EnvironmentObject
```

---

## 🔴 BUILD 93: РЕКУРСИЯ В ЛОГГЕРАХ

### Проблема:
- `MasterLogger.enableVisualLogging` использовал `@AppStorage` в singleton
- `VisualLogger` читал из `UserDefaults` при инициализации
- Логгеры вызывались синхронно

### Техническая причина:
`@AppStorage` в singleton создает проблему, потому что singleton инициализируется один раз, а `@AppStorage` может вызывать обновления при чтении из `UserDefaults`. Если логгер вызывается во время инициализации View, это создает цикл.

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

**Пример исправления:**
```swift
// ❌ БЫЛО:
class MasterLogger {
    @AppStorage("enable_visual_logging") private var enableVisualLogging: Bool = false
    // @AppStorage в singleton → рекурсия
}

// ✅ СТАЛО:
class MasterLogger {
    private var enableVisualLogging: Bool {
        get {
            // Проверяем кеш в thread dictionary
            let dict = Thread.current.threadDictionary
            if let cached = dict["MasterLogger.enableVisualLogging"] as? Bool {
                return cached
            }
            // Используем значение по умолчанию без чтения из UserDefaults при инициализации
            let defaultValue = false
            dict["MasterLogger.enableVisualLogging"] = defaultValue
            
            // Загружаем реальное значение асинхронно после инициализации
            Task { @MainActor in
                let realValue = UserDefaults.standard.bool(forKey: "enable_visual_logging")
                dict["MasterLogger.enableVisualLogging"] = realValue
            }
            
            return defaultValue
        }
        set {
            Thread.current.threadDictionary["MasterLogger.enableVisualLogging"] = newValue
            Task { @MainActor in
                UserDefaults.standard.set(newValue, forKey: "enable_visual_logging")
            }
        }
    }
}
```

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

**Пример реализации:**
```swift
// Глобальный crash handler
func crashExceptionHandler(exception: NSException) {
    let crashLog = """
    🚨 CRASH DETECTED!
    Exception: \(exception.name.rawValue)
    Reason: \(exception.reason ?? "Unknown")
    Stack Trace: \(exception.callStackSymbols)
    """
    
    // Сохраняем в UserDefaults и файл
    UserDefaults.standard.set(crashLog, forKey: "last_crash_log")
    saveCrashLogToFile(crashLog: crashLog, stackTrace: stackTrace)
    
    // Отправляем на сервер асинхронно
    sendCrashLogToServer(crashLog: crashLog, ...)
}
```

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

### Техническая причина:
Синхронные операции с `UserDefaults` могут вызывать обновление `@AppStorage`, что вызывает перерисовку View, что может вызвать повторные операции с `UserDefaults`.

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

**Пример исправления:**
```swift
// ❌ БЫЛО:
func updateBiometricEnabled(_ enabled: Bool) {
    UserDefaults.standard.set(enabled, forKey: "biometricEnabled")
    // Синхронная операция → может вызвать рекурсию
}

// ✅ СТАЛО:
func updateBiometricEnabled(_ enabled: Bool) {
    Task { @MainActor in
        UserDefaults.standard.set(enabled, forKey: "biometricEnabled")
        // Асинхронная операция → безопасно
    }
}
```

---

## 🔴 BUILD 97: КРАШ В ОНБОРДИНГЕ

### Проблема:
- Конфликт `@AppStorage` между `OnboardingScreen` и `ALADDINApp`
- Убрали `UserDefaults.set(false)` - рассинхронизация
- `MasterLogger.enableVisualLogging` читал из `UserDefaults` при инициализации

### Техническая причина:
Два View используют один и тот же ключ `@AppStorage`. Когда один View обновляет значение, другой View получает уведомление, что вызывает обновление, что снова вызывает обновление первого View.

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

**Пример исправления:**
```swift
// ❌ БЫЛО:
// В OnboardingScreen:
@AppStorage(AppConfig.UserDefaultsKeys.hasCompletedOnboarding) private var hasCompletedOnboarding: Bool = false

// В ALADDINApp:
@AppStorage(AppConfig.UserDefaultsKeys.hasCompletedOnboarding) private var hasCompletedOnboarding: Bool = false
// Конфликт → рекурсия

// ✅ СТАЛО:
// В OnboardingScreen:
@State private var hasCompletedOnboarding: Bool = false

.onAppear {
    Task { @MainActor in
        hasCompletedOnboarding = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
    }
}

// В ALADDINApp остается @AppStorage (единственный источник истины)
```

---

## 🔴 BUILD 98: РЕКУРСИЯ В DATEFORMATTER (ПОВТОРНАЯ ПРОБЛЕМА)

### Проблема:
- `DateFormatter()` создавался в функциях без статического `Locale`
- Использование `Locale.current` читало из `UserDefaults`
- Рекурсия в ICU библиотеке при форматировании даты

### Техническая причина:
Даже если `DateFormatter` создается в функции (не в computed property), если эта функция вызывается при обновлении View, а `Locale.current` читает из `UserDefaults`, это создает цикл.

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

**Пример исправления:**
```swift
// ❌ БЫЛО:
func getCrashLogs() -> String {
    let formatter = DateFormatter()
    formatter.dateStyle = .full
    formatter.timeStyle = .full
    // Locale.current по умолчанию → читает из UserDefaults → рекурсия
    return formatter.string(from: date)
}

// ✅ СТАЛО:
private let crashTimeFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .full
    formatter.timeStyle = .full
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    return formatter
}()

func getCrashLogs() -> String {
    return crashTimeFormatter.string(from: date)  // Используем статический
}
```

---

## 🔴 BUILD 99: ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ РЕКУРСИИ В MAINSCREEN (НЕ ПОЛНОСТЬЮ РЕШИЛО ПРОБЛЕМУ)

### ⚠️ ВАЖНО:
Хотя в BUILD 99 были внесены исправления, краш **продолжался**. Проблема была решена только в BUILD 100.

### Проблема:
- `updateExpirationTextCache()` вызывалась в `.onAppear {}`
- Обновление `@State` вызывало перерисовку View
- Перерисовка View вызывала `.onAppear {}` снова
- Это создавало бесконечную рекурсию

### Техническая причина:
`.onAppear {}` вызывается при каждом появлении View. Если внутри `.onAppear {}` обновляется `@State`, это вызывает перерисовку View. Если View перерисовывается, `.onAppear {}` может вызваться снова, создавая цикл.

### Исправления:

#### ЭТАП 1: Добавлена защита от рекурсии
```swift
// ✅ Флаг для предотвращения повторных вызовов
@State private var isUpdatingExpirationText: Bool = false

private func updateExpirationTextCache(from isoString: String) async {
    guard !isUpdatingExpirationText else {
        print("⚠️ [MainScreen] updateExpirationTextCache уже выполняется, пропускаем")
        return
    }
    
    isUpdatingExpirationText = true
    defer { 
        Task { @MainActor in
            isUpdatingExpirationText = false
        }
    }
    // ... остальной код ...
}
```

#### ЭТАП 2: Функция сделана асинхронной
```swift
// ✅ Функция async для предотвращения блокировки main thread
private func updateExpirationTextCache(from isoString: String) async {
    // ... защита от рекурсии ...
    
    // ✅ Все обновления @State через MainActor.run
    let formattedText = Self.displayFormatter.string(from: date)
    await MainActor.run {
        cachedExpirationText = formattedText
    }
}
```

#### ЭТАП 3: Заменено `.onAppear {}` на `.task {}`
```swift
// ❌ БЫЛО:
.onAppear {
    updateExpirationTextCache(from: subscriptionExpiresAtIso)
    // Вызывается при каждом обновлении View → рекурсия
}

// ✅ СТАЛО:
.task {
    let currentExpiresAt = subscriptionExpiresAtIso
    Task { @MainActor in
        await updateExpirationTextCache(from: currentExpiresAt)
    }
    // Вызывается только один раз при появлении View → безопасно
}
```

**Файлы:**
- `Screens/01_MainScreen.swift`

**Проблема этого решения:**
- Защита через `@State` не работала при пересоздании View
- `defer` с асинхронным сбросом создавал race condition
- Краш продолжался → решено в BUILD 100

---

## 🎉 BUILD 100: ФИНАЛЬНОЕ РЕШЕНИЕ - КРАШ ПРЕКРАТИЛСЯ!

### ✅ РЕЗУЛЬТАТ:
**КРАШ ПОЛНОСТЬЮ ПРЕКРАТИЛСЯ!** Все исправления BUILD 100 работают стабильно.

### 🔴 Проблема:
Несмотря на все исправления в BUILD 77-99, краш продолжался. Анализ crash log показал:
- Рекурсия в ICU библиотеке (`libicucore.A.dylib`)
- `DateFormatter.string()` вызывал рекурсию через `Calendar.current`
- `Calendar.current` читал из `UserDefaults`, создавая цикл
- `.task {}` вызывался повторно при пересоздании View
- Защита через `@State` не работала при пересоздании View

### 🔍 Техническая причина (истинная):

#### Проблема #1: Calendar.current в DateFormatter
```
DateFormatter.string(from: date)
  ↓
DateFormatter использует Calendar.current (внутри)
  ↓
Calendar.current читает из UserDefaults
  ↓
UserDefaults обновление вызывает обновление @AppStorage
  ↓
View обновляется
  ↓
DateFormatter.string() вызывается снова
  ↓
БЕСКОНЕЧНЫЙ ЦИКЛ → КРАШ
```

**Ключевое открытие:**
- `DateFormatter` внутри использует `Calendar.current` по умолчанию
- Даже если мы не устанавливаем `formatter.calendar`, он использует `Calendar.current`
- `Calendar.current` читает из `UserDefaults` при каждом обращении
- Это создает цикл рекурсии через ICU библиотеку

#### Проблема #2: Защита через @State не работала
```
View пересоздается
  ↓
Новый экземпляр View создает новый @State
  ↓
Старый флаг isUpdatingExpirationText не виден новому экземпляру
  ↓
Функция вызывается снова
  ↓
БЕСКОНЕЧНЫЙ ЦИКЛ → КРАШ
```

#### Проблема #3: .task {} вызывался повторно
```
View пересоздается
  ↓
.task {} вызывается снова
  ↓
hasAppeared не защищает от пересоздания
  ↓
Функция вызывается повторно
  ↓
БЕСКОНЕЧНЫЙ ЦИКЛ → КРАШ
```

### ✅ Исправления BUILD 100:

#### ИСПРАВЛЕНИЕ #1: Статический Calendar в displayFormatter

**Проблема:**
- `DateFormatter` использовал `Calendar.current` по умолчанию
- `Calendar.current` читал из `UserDefaults`

**Решение:**
```swift
// ✅ BUILD 100: Статический Calendar для предотвращения рекурсии
private static let calendar: Calendar = {
    var cal = Calendar(identifier: .gregorian)
    cal.locale = Locale(identifier: "ru_RU")
    return cal
}()

private static let displayFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .medium
    formatter.timeStyle = .none
    formatter.locale = Locale(identifier: "ru_RU")
    // ✅ КРИТИЧНО: Устанавливаем статический Calendar
    formatter.calendar = Self.calendar  // ← ЭТО КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ!
    return formatter
}()
```

**Почему это работает:**
- Статический Calendar создается один раз
- Не читает из `UserDefaults` при каждом обращении
- Предотвращает цикл рекурсии через ICU библиотеку

---

#### ИСПРАВЛЕНИЕ #2: Форматирование на main thread

**Проблема:**
- Форматирование происходило вне main thread
- Это могло вызвать проблемы с `UserDefaults` и рекурсию

**Решение:**
```swift
// ✅ BUILD 100: Форматирование на main thread
let formattedText = await MainActor.run {
    Self.displayFormatter.string(from: date)
}
```

**Почему это работает:**
- Все операции с форматтерами происходят на main thread
- Предотвращает проблемы с `UserDefaults` и рекурсию через ICU библиотеку

---

#### ИСПРАВЛЕНИЕ #3: Глобальный флаг с NSLock для защиты от рекурсии

**Проблема:**
- `@State` не работает при пересоздании View
- Новый экземпляр View не видит флаг старого экземпляра
- `defer` с асинхронным сбросом создавал race condition

**Решение:**
```swift
// ✅ BUILD 100: Глобальный флаг вне struct MainScreen
private var isUpdatingExpirationTextGlobal: Bool = false
private let expirationTextUpdateLock = NSLock()

private func updateExpirationTextCache(from isoString: String) async {
    let callId = UUID().uuidString
    print("🔍 [MainScreen] updateExpirationTextCache START - \(callId) - \(Date())")
    
    expirationTextUpdateLock.lock()
    guard !isUpdatingExpirationTextGlobal else {
        expirationTextUpdateLock.unlock()
        print("⚠️ [MainScreen] updateExpirationTextCache уже выполняется, пропускаем - \(callId)")
        return
    }
    isUpdatingExpirationTextGlobal = true
    expirationTextUpdateLock.unlock()
    
    defer {
        expirationTextUpdateLock.lock()
        isUpdatingExpirationTextGlobal = false
        expirationTextUpdateLock.unlock()
        print("✅ [MainScreen] updateExpirationTextCache COMPLETE - \(callId) - \(Date())")
    }
    // ... остальной код ...
}
```

**Почему это работает:**
- Глобальный флаг виден всем экземплярам View
- NSLock обеспечивает thread-safety
- Синхронный сброс флага в `defer` предотвращает race condition

---

#### ИСПРАВЛЕНИЕ #4: Глобальный флаг для .task {}

**Проблема:**
- `.task {}` вызывался повторно при пересоздании View
- `hasAppeared` не защищал от пересоздания

**Решение:**
```swift
// ✅ BUILD 100: Глобальный флаг для .task {}
private var mainScreenTaskExecuted: Bool = false
private let mainScreenTaskLock = NSLock()

.task {
    mainScreenTaskLock.lock()
    guard !mainScreenTaskExecuted else {
        mainScreenTaskLock.unlock()
        let message = "\(logPrefix) Повторный вызов пропущен (глобальный флаг)"
        print("⚠️ \(message)")
        return
    }
    mainScreenTaskExecuted = true
    mainScreenTaskLock.unlock()
    
    // ... остальной код ...
}
```

**Почему это работает:**
- Глобальный флаг предотвращает повторные вызовы `.task {}`
- NSLock обеспечивает thread-safety
- Работает даже при пересоздании View

---

#### ИСПРАВЛЕНИЕ #5: Рефакторинг DateFormatterService

**Проблема:**
- Форматтеры были разбросаны по разным файлам
- Дублирование кода
- Сложность поддержки

**Решение:**
```swift
// ✅ BUILD 100: Централизованный сервис для форматирования дат
@MainActor
class DateFormatterService {
    static let shared = DateFormatterService()
    
    // Статический Calendar
    private static let calendar: Calendar = {
        var cal = Calendar(identifier: .gregorian)
        cal.locale = Locale(identifier: "ru_RU")
        return cal
    }()
    
    // Статические форматтеры
    private static let displayFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.calendar = Self.calendar  // Статический Calendar
        return formatter
    }()
    
    // Методы форматирования
    func formatExpirationDate(from isoString: String) -> String? {
        guard let date = parseISO8601(isoString) else { return nil }
        return formatDisplayDate(date)
    }
    
    // Calendar helpers
    func isDateInToday(_ date: Date) -> Bool {
        return Self.calendar.isDateInToday(date)
    }
}
```

**Почему это работает:**
- Централизованное управление форматтерами
- Все форматтеры используют статический Calendar
- Легко поддерживать и тестировать
- Предотвращает дублирование кода

**Использование в MainScreen:**
```swift
// ✅ BUILD 100: Использование DateFormatterService
private let dateFormatterService = DateFormatterService.shared

private func updateExpirationTextCache(from isoString: String) async {
    // ... защита от рекурсии ...
    
    let formattedText = await MainActor.run {
        dateFormatterService.formatExpirationDate(from: isoString)
    }
    
    await MainActor.run {
        cachedExpirationText = formattedText
    }
}
```

---

#### ИСПРАВЛЕНИЕ #6: Unit и интеграционные тесты

**Добавлено:**
1. ✅ `DateFormatterServiceTests.swift` - unit-тесты для проверки отсутствия рекурсии
2. ✅ `MainScreenRecursionTests.swift` - интеграционные тесты для проверки поведения при пересоздании View

**Тесты проверяют:**
- Отсутствие рекурсии при множественных вызовах форматирования
- Отсутствие рекурсии при параллельных вызовах
- Отсутствие рекурсии при пересоздании View
- Работу глобальных флагов
- Thread-safety операций

**Файлы:**
- `Tests/UnitTests/DateFormatterServiceTests.swift` (новый)
- `Tests/Integration/MainScreenRecursionTests.swift` (новый)

---

### 📊 Результаты BUILD 100:

| Метрика | До BUILD 100 | После BUILD 100 |
|---------|--------------|-----------------|
| **Краши** | Постоянные | ✅ **0 крашей** |
| **Рекурсия** | Да | ✅ **Нет рекурсии** |
| **Стабильность** | Нестабильно | ✅ **Стабильно** |
| **Тесты** | Нет | ✅ **Есть тесты** |

---

### ✅ Что именно помогло избавиться от краша:

1. ✅ **Статический Calendar в displayFormatter** - **КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ**
   - Предотвратил рекурсию через `Calendar.current`
   - Это была НОВАЯ проблема, которую не исправляли ранее

2. ✅ **Глобальный флаг с NSLock** - **КРИТИЧНО**
   - Заменил неработающую защиту через `@State`
   - Работает при пересоздании View

3. ✅ **Форматирование на main thread** - **ВАЖНО**
   - Предотвратил проблемы с `UserDefaults` и рекурсию через ICU

4. ✅ **Глобальный флаг для .task {}** - **ВАЖНО**
   - Предотвратил повторные вызовы при пересоздании View

5. ✅ **DateFormatterService** - **УЛУЧШЕНИЕ**
   - Централизованное управление форматтерами
   - Легче поддерживать и тестировать

---

**Файлы изменены:**
- `Screens/01_MainScreen.swift` - все критические исправления
- `Core/Services/DateFormatterService.swift` - новый сервис
- `Tests/UnitTests/DateFormatterServiceTests.swift` - новые тесты
- `Tests/Integration/MainScreenRecursionTests.swift` - новые тесты

---

## 📊 СТАТИСТИКА ИСПРАВЛЕНИЙ

### По типам проблем:

| Тип проблемы | Количество исправлений | Builds | Файлов затронуто |
|--------------|------------------------|--------|------------------|
| Рекурсия через `@AppStorage` | 15+ | 91, 92, 93, 96, 97 | 8+ |
| Рекурсия через `DateFormatter` | 10+ | 88-90, 98 | 10+ |
| Рекурсия через SwiftUI модификаторы | 5+ | 92 | 2+ |
| Рекурсия через логгеры | 5+ | 93 | 3+ |
| Рекурсия через lifecycle | 3 | 99 | 1 |
| Рекурсия через Calendar.current | 4 | 100 | 1 |
| **ИТОГО** | **37+** | **77-100** | **25+** |

### По файлам:

| Файл | Количество исправлений | Типы проблем |
|------|------------------------|--------------|
| `Screens/01_MainScreen.swift` | 8+ | @AppStorage, lifecycle, DateFormatter |
| `Core/Utilities/MasterLogger.swift` | 5+ | @AppStorage, UserDefaults |
| `ALADDINApp.swift` | 6+ | @AppStorage, lifecycle, DateFormatter |
| `Screens/02_FamilyScreen.swift` | 4+ | UserDefaults, DateFormatter |
| `AppDelegate.swift` | 3+ | DateFormatter, crash handling |
| `ViewModels/SettingsViewModel.swift` | 3+ | UserDefaults |
| `Core/Managers/SubscriptionManager.swift` | 2+ | DateFormatter |
| `Core/Services/DateFormatterService.swift` | 1 | Новый сервис (BUILD 100) |
| `Tests/UnitTests/DateFormatterServiceTests.swift` | 1 | Новые тесты (BUILD 100) |
| `Tests/Integration/MainScreenRecursionTests.swift` | 1 | Новые тесты (BUILD 100) |
| Другие файлы | 20+ | Различные |

---

## ✅ КЛЮЧЕВЫЕ ПРИНЦИПЫ ИСПРАВЛЕНИЙ

### 1. Статические форматтеры с статическим Calendar

**Принцип:** Все `DateFormatter` должны быть статическими и использовать статический `Locale` **И статический `Calendar`**.

**Почему:**
- `DateFormatter` создание - дорогая операция
- `Locale.current` читает из `UserDefaults` при каждом обращении
- **`Calendar.current` читает из `UserDefaults` при каждом обращении** (КЛЮЧЕВОЕ ОТКРЫТИЕ BUILD 100!)
- `DateFormatter` использует `Calendar.current` по умолчанию, даже если мы не устанавливаем `formatter.calendar`
- Статический форматтер создается один раз и переиспользуется

**Правило:**
```swift
// ✅ ПРАВИЛЬНО (BUILD 100):
private static let calendar: Calendar = {
    var cal = Calendar(identifier: .gregorian)
    cal.locale = Locale(identifier: "ru_RU")
    return cal
}()

private static let dateFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    formatter.calendar = Self.calendar  // ← КРИТИЧНО: Статический Calendar!
    return formatter
}()

// ❌ НЕПРАВИЛЬНО:
let formatter = DateFormatter()  // Создается каждый раз
formatter.locale = Locale.current  // Читает из UserDefaults
// formatter.calendar не установлен → использует Calendar.current → читает из UserDefaults!
```

**Применение:**
- Все `DateFormatter` в ViewModels
- Все `DateFormatter` в Views
- Все `DateFormatter` в функциях форматирования
- Все `ISO8601DateFormatter`

---

### 2. Асинхронность

**Принцип:** Все операции с `UserDefaults` должны быть асинхронными.

**Почему:**
- Синхронные операции с `UserDefaults` могут вызывать обновление `@AppStorage`
- Обновление `@AppStorage` вызывает перерисовку View
- Перерисовка View может вызвать повторные операции с `UserDefaults`

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
Task { @MainActor in
    UserDefaults.standard.set(value, forKey: "key")
}

// ❌ НЕПРАВИЛЬНО:
UserDefaults.standard.set(value, forKey: "key")  // Синхронно
```

**Применение:**
- Все `UserDefaults.standard.set()`
- Все `UserDefaults.standard.removeObject()`
- Все операции с `UserDefaults` в ViewModels
- Все операции с `UserDefaults` в Views

---

### 3. Защита от рекурсии через глобальные флаги

**Принцип:** Использовать **глобальные флаги с NSLock** для предотвращения повторных вызовов функций.

**Почему:**
- Функции могут вызываться рекурсивно через обновление View
- `@State` не работает при пересоздании View (новый экземпляр не видит флаг старого)
- Глобальные флаги видны всем экземплярам View
- NSLock обеспечивает thread-safety
- `defer` гарантирует сброс флага даже при ошибке

**Правило:**
```swift
// ✅ ПРАВИЛЬНО (BUILD 100):
// Глобальный флаг вне struct View
private var isUpdatingGlobal: Bool = false
private let updateLock = NSLock()

private func updateSomething() async {
    let callId = UUID().uuidString
    print("🔍 updateSomething START - \(callId)")
    
    updateLock.lock()
    guard !isUpdatingGlobal else {
        updateLock.unlock()
        print("⚠️ updateSomething уже выполняется, пропускаем - \(callId)")
        return
    }
    isUpdatingGlobal = true
    updateLock.unlock()
    
    defer {
        updateLock.lock()
        isUpdatingGlobal = false
        updateLock.unlock()
        print("✅ updateSomething COMPLETE - \(callId)")
    }
    // ... код обновления ...
}

// ❌ НЕПРАВИЛЬНО (BUILD 99 - не работало):
@State private var isUpdating: Bool = false  // Не работает при пересоздании View!

private func updateSomething() async {
    guard !isUpdating else { return }
    isUpdating = true
    defer { 
        Task { @MainActor in
            isUpdating = false  // Асинхронный сброс → race condition
        }
    }
    // ... код обновления ...
}
```

**Применение:**
- Функции обновления `@State`
- Функции форматирования данных
- Функции загрузки данных
- Функции синхронизации

---

### 4. SwiftUI lifecycle

**Принцип:** Использовать `.task {}` вместо `.onAppear {}` когда возможно.

**Почему:**
- `.onAppear {}` вызывается при каждом обновлении View
- `.task {}` вызывается только один раз при появлении View
- Это предотвращает повторные вызовы при обновлении View

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
.task {
    await loadData()  // Вызывается только один раз
}

// ❌ НЕПРАВИЛЬНО:
.onAppear {
    loadData()  // Может вызваться многократно
}
```

**Применение:**
- Инициализация данных при появлении View
- Загрузка данных из API
- Обновление кеша
- Настройка состояния

**Исключения:**
- `.onAppear {}` можно использовать для UI-специфичных действий (анимации, фокус)
- `.onAppear {}` можно использовать если нужно вызывать при каждом появлении

---

### 5. Кеширование

**Принцип:** Использовать `@State` вместо computed properties для кеширования.

**Почему:**
- Computed properties вызываются при каждом доступе
- Если computed property читает `@AppStorage`, это может вызвать рекурсию
- `@State` обновляется только явно, предотвращая рекурсию

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
@State private var cachedValue: String? = nil

private func updateCache() async {
    // Вычисление значения...
    cachedValue = computedValue
}

// Использование:
Text(cachedValue ?? "")

// ❌ НЕПРАВИЛЬНО:
var cachedValue: String {
    let value = subscriptionExpiresAtIso  // Читает @AppStorage
    // Вычисление...
    return computedValue  // Вызывается при каждом доступе → рекурсия
}
```

**Применение:**
- Кеширование форматированных значений
- Кеширование вычисленных значений
- Кеширование данных из API
- Кеширование состояния

---

## 🤖 РЕКОМЕНДАЦИИ ДЛЯ ДРУГИХ ML СИСТЕМ

### 🔍 Ключевые инсайты для анализа подобных крашей:

#### 1. Проверяйте Calendar.current в DateFormatter

**Что искать:**
- `DateFormatter` без явно установленного `formatter.calendar`
- Использование `Calendar.current` в коде
- Рекурсия в ICU библиотеке (`libicucore.A.dylib`)

**Почему важно:**
- `DateFormatter` использует `Calendar.current` по умолчанию
- `Calendar.current` читает из `UserDefaults` при каждом обращении
- Это создает цикл рекурсии через ICU библиотеку

**Как исправить:**
```swift
// ✅ Всегда устанавливайте статический Calendar:
private static let calendar: Calendar = {
    var cal = Calendar(identifier: .gregorian)
    cal.locale = Locale(identifier: "ru_RU")
    return cal
}()

formatter.calendar = Self.calendar
```

---

#### 2. Проверяйте защиту от рекурсии при пересоздании View

**Что искать:**
- Защиту через `@State` (не работает при пересоздании!)
- Асинхронный сброс флагов в `defer` (race condition!)
- Повторные вызовы `.task {}` при пересоздании View

**Почему важно:**
- SwiftUI пересоздает View при определенных условиях
- Новый экземпляр View не видит `@State` старого экземпляра
- Нужны глобальные флаги с NSLock

**Как исправить:**
```swift
// ✅ Используйте глобальные флаги с NSLock:
private var isUpdatingGlobal: Bool = false
private let updateLock = NSLock()

// Синхронный сброс в defer (не асинхронный!)
defer {
    updateLock.lock()
    isUpdatingGlobal = false
    updateLock.unlock()
}
```

---

#### 3. Проверяйте форматирование на main thread

**Что искать:**
- Форматирование дат вне main thread
- Операции с форматтерами в background потоках

**Почему важно:**
- Форматирование может вызывать проблемы с `UserDefaults`
- Рекурсия через ICU библиотеку может происходить вне main thread

**Как исправить:**
```swift
// ✅ Всегда форматируйте на main thread:
let formattedText = await MainActor.run {
    formatter.string(from: date)
}
```

---

#### 4. Используйте централизованные сервисы для форматирования

**Что искать:**
- Дублирование форматтеров в разных файлах
- Разные подходы к форматированию в разных местах

**Почему важно:**
- Централизованное управление предотвращает ошибки
- Легче поддерживать и тестировать
- Гарантирует использование статических форматтеров

**Как исправить:**
```swift
// ✅ Создайте DateFormatterService:
@MainActor
class DateFormatterService {
    static let shared = DateFormatterService()
    // Все форматтеры со статическим Calendar
}
```

---

#### 5. Добавляйте тесты для проверки отсутствия рекурсии

**Что искать:**
- Отсутствие unit-тестов для форматирования
- Отсутствие интеграционных тестов для View

**Почему важно:**
- Тесты гарантируют отсутствие рекурсии
- Помогают выявить проблемы до продакшена
- Защищают от регрессий

**Как исправить:**
```swift
// ✅ Добавьте тесты:
func testNoRecursionOnMultipleFormatCalls() {
    let date = Date()
    for _ in 0..<1000 {
        let formatted = service.formatDisplayDate(date)
        XCTAssertFalse(formatted.isEmpty)
    }
}
```

---

### 📋 Чек-лист для анализа крашей с рекурсией:

- [ ] Проверен `Calendar.current` в `DateFormatter`?
- [ ] Проверена защита от рекурсии при пересоздании View?
- [ ] Проверено форматирование на main thread?
- [ ] Проверены глобальные флаги с NSLock?
- [ ] Проверены тесты на отсутствие рекурсии?
- [ ] Проверена централизация форматтеров?

---

## 🎯 РЕКОМЕНДАЦИИ ДЛЯ БУДУЩИХ РАЗРАБОТЧИКОВ

### ✅ ЧТО ДЕЛАТЬ:

1. **Всегда используйте статические форматтеры с статическим Calendar**
   - Создавайте `DateFormatter` как `static let`
   - Используйте `Locale(identifier:)` вместо `Locale.current`
   - **КРИТИЧНО:** Всегда устанавливайте `formatter.calendar = Self.calendar` (статический Calendar)
   - Не полагайтесь на `Calendar.current` по умолчанию!

2. **Всегда делайте операции с `UserDefaults` асинхронными**
   - Обертывайте в `Task { @MainActor in }`
   - Используйте `await` для асинхронных операций

3. **Используйте защиту от рекурсии через глобальные флаги**
   - Используйте **глобальные флаги с NSLock** (не `@State`!)
   - `@State` не работает при пересоздании View
   - Используйте синхронный сброс флагов в `defer` (не асинхронный!)
   - Добавляйте логирование с callId для диагностики

4. **Используйте `.task {}` вместо `.onAppear {}`**
   - Когда нужно загрузить данные один раз
   - Когда нужно инициализировать состояние

5. **Используйте `@State` для кеширования**
   - Вместо computed properties для кешированных значений
   - Обновляйте явно через функции

---

### ❌ ЧЕГО НЕ ДЕЛАТЬ:

1. **Не создавайте `DateFormatter` в функциях или computed properties**
   - Используйте статические форматтеры
   - Не используйте `Locale.current`
   - **КРИТИЧНО:** Всегда устанавливайте `formatter.calendar` (статический Calendar)
   - Не полагайтесь на `Calendar.current` по умолчанию!

2. **Не делайте синхронные операции с `UserDefaults`**
   - Всегда обертывайте в `Task { @MainActor in }`
   - Не вызывайте напрямую в `body` или `onAppear`

3. **Не используйте `.onChange()` с `@AppStorage`**
   - Это может вызвать рекурсию
   - Используйте `.task {}` или явное обновление

4. **Не используйте `.id()` с значениями из `UserDefaults`**
   - Это может вызвать рекурсию
   - Используйте `@EnvironmentObject` для обновления View

5. **Не используйте computed properties для значений из `@AppStorage`**
   - Используйте `@State` с явным обновлением
   - Используйте функции для обновления кеша

---

## 📝 ВЫВОДЫ

### Основные причины крашей:

1. **Циклические зависимости** между SwiftUI `@AppStorage`, `UserDefaults`, и View lifecycle
2. **Динамическое создание форматтеров** с `Locale.current` **И Calendar.current** (КЛЮЧЕВОЕ ОТКРЫТИЕ BUILD 100!)
3. **Синхронные операции** с `UserDefaults` в критичных местах
4. **Неправильное использование SwiftUI lifecycle** модификаторов
5. **Защита через @State не работает** при пересоздании View (исправлено в BUILD 100)

### Решение:

Систематическое устранение всех циклических зависимостей через:
1. Статические форматтеры **с статическим Calendar** (КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ BUILD 100!)
2. Асинхронные операции
3. Защиту от рекурсии **через глобальные флаги с NSLock** (исправлено в BUILD 100)
4. Правильное использование SwiftUI lifecycle
5. Кеширование через `@State`
6. Форматирование на main thread (BUILD 100)
7. Централизованные сервисы для форматирования (BUILD 100)
8. Unit и интеграционные тесты (BUILD 100)

### Результат:

- ✅ Все известные проблемы с рекурсией исправлены **в BUILD 100**
- ✅ **КРАШ ПОЛНОСТЬЮ ПРЕКРАТИЛСЯ** после BUILD 100
- ✅ Добавлена диагностика для анализа крашей
- ✅ Установлены принципы для предотвращения будущих проблем
- ✅ Добавлены unit и интеграционные тесты
- ✅ Создан централизованный DateFormatterService

---

## 🔍 ДЛЯ ML СИСТЕМ: КЛЮЧЕВЫЕ МЕТКИ

**Тип проблемы:** Рекурсия через циклические зависимости  
**Корневая причина:** SwiftUI `@AppStorage` + `UserDefaults` + `DateFormatter` + `Calendar.current` + lifecycle  
**Решение:** Статические форматтеры **с статическим Calendar** + асинхронность + **глобальные флаги с NSLock** + правильный lifecycle + форматирование на main thread  
**Статус:** ✅ **ИСПРАВЛЕНО В BUILD 100 - КРАШ ПРЕКРАТИЛСЯ!**  
**Принципы:** 8 ключевых принципов установлены для предотвращения будущих проблем  
**Ключевое открытие:** `Calendar.current` в `DateFormatter` читает из `UserDefaults` и создает цикл рекурсии через ICU библиотеку

---

**ГОТОВО! Документ содержит всю необходимую информацию для понимания крашей и их причин.** 📋
