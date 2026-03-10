# 📋 ПОЛНАЯ ИСТОРИЯ ИСПРАВЛЕНИЙ КРАШЕЙ: BUILD 77 → BUILD 99

**Период:** BUILD 77 - BUILD 99  
**Тип проблемы:** `EXC_BAD_ACCESS (SIGSEGV)` - `Thread stack size exceeded due to excessive recursion`  
**Дата создания:** 2026-03-10  
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

## 🔴 BUILD 99: ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ РЕКУРСИИ В MAINSCREEN

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
| Другие файлы | 20+ | Различные |

---

## ✅ КЛЮЧЕВЫЕ ПРИНЦИПЫ ИСПРАВЛЕНИЙ

### 1. Статические форматтеры

**Принцип:** Все `DateFormatter` должны быть статическими и использовать статический `Locale`.

**Почему:**
- `DateFormatter` создание - дорогая операция
- `Locale.current` читает из `UserDefaults` при каждом обращении
- Статический форматтер создается один раз и переиспользуется

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
private static let dateFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    return formatter
}()

// ❌ НЕПРАВИЛЬНО:
let formatter = DateFormatter()  // Создается каждый раз
formatter.locale = Locale.current  // Читает из UserDefaults
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

### 3. Защита от рекурсии

**Принцип:** Использовать флаги для предотвращения повторных вызовов функций.

**Почему:**
- Функции могут вызываться рекурсивно через обновление View
- Флаги предотвращают повторные вызовы
- `defer` гарантирует сброс флага даже при ошибке

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
@State private var isUpdating: Bool = false

private func updateSomething() async {
    guard !isUpdating else { return }
    isUpdating = true
    defer { 
        Task { @MainActor in
            isUpdating = false
        }
    }
    // ... код обновления ...
}

// ❌ НЕПРАВИЛЬНО:
private func updateSomething() {
    // Нет защиты → может вызвать рекурсию
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

## 🎯 РЕКОМЕНДАЦИИ ДЛЯ БУДУЩИХ РАЗРАБОТЧИКОВ

### ✅ ЧТО ДЕЛАТЬ:

1. **Всегда используйте статические форматтеры**
   - Создавайте `DateFormatter` как `static let`
   - Используйте `Locale(identifier:)` вместо `Locale.current`

2. **Всегда делайте операции с `UserDefaults` асинхронными**
   - Обертывайте в `Task { @MainActor in }`
   - Используйте `await` для асинхронных операций

3. **Используйте защиту от рекурсии**
   - Добавляйте флаги для предотвращения повторных вызовов
   - Используйте `defer` для гарантированного сброса флагов

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
2. **Динамическое создание форматтеров** с `Locale.current`
3. **Синхронные операции** с `UserDefaults` в критичных местах
4. **Неправильное использование SwiftUI lifecycle** модификаторов

### Решение:

Систематическое устранение всех циклических зависимостей через:
1. Статические форматтеры
2. Асинхронные операции
3. Защиту от рекурсии
4. Правильное использование SwiftUI lifecycle
5. Кеширование через `@State`

### Результат:

- ✅ Все известные проблемы с рекурсией исправлены
- ✅ Добавлена диагностика для анализа крашей
- ✅ Установлены принципы для предотвращения будущих проблем

---

## 🔍 ДЛЯ ML СИСТЕМ: КЛЮЧЕВЫЕ МЕТКИ

**Тип проблемы:** Рекурсия через циклические зависимости  
**Корневая причина:** SwiftUI `@AppStorage` + `UserDefaults` + `DateFormatter` + lifecycle  
**Решение:** Статические форматтеры + асинхронность + защита от рекурсии + правильный lifecycle  
**Статус:** ✅ Исправлено в BUILD 99  
**Принципы:** 5 ключевых принципов установлены для предотвращения будущих проблем

---

**ГОТОВО! Документ содержит всю необходимую информацию для понимания крашей и их причин.** 📋
