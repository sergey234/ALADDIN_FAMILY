# 🔧 BUILD 95: ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЯ ВСЕХ 10 МЕСТ

**Дата:** 2026-03-10  
**Версия сборки:** 95 → 96  
**Цель:** Полностью избавиться от рекурсии, исправив все 10 проблемных мест

---

## 📊 ОБЩАЯ СТАТИСТИКА

- **Критичных мест:** 3 (вызывают краш сейчас)
- **Проблемных мест:** 7 (могут вызвать краш в будущем)
- **Всего мест:** 10
- **Оценка времени:** 4-6 часов работы
- **Риск:** Средний (требует тестирования)

---

## 🔴 ЭТАП 1: КРИТИЧНЫЕ МЕСТА (3 места) - ПРИОРИТЕТ 1

### ❌ МЕСТО #1: `UserDefaults.set()` в `initializeNavigation()`

**Файл:** `ALADDINApp.swift:685`  
**Тип:** Критичное (вызывает краш BUILD 95)  
**Время:** 15 минут  
**Риск:** Низкий

**ТЕКУЩИЙ КОД:**
```swift
if !ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
    // Принудительный сброс онбординга для первого запуска
    UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)  // ❌ ПРОБЛЕМА!
    UserDefaults.standard.synchronize()
}
```

**ПРОБЛЕМА:**
- Вызывается из `onAppear` → `initializeNavigation()`
- Обновляет `@AppStorage hasCompletedOnboarding` → вызывает перерисовку → рекурсия

**РЕШЕНИЕ:**
```swift
if !ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
    // ✅ BUILD 96: Убрано UserDefaults.set() - значение уже false по умолчанию в @AppStorage
    // Не нужно устанавливать false, так как @AppStorage уже имеет значение по умолчанию false
    // Это предотвращает рекурсию через обновление @AppStorage
}
```

**ШАГИ:**
1. Удалить строки 685-686
2. Добавить комментарий с объяснением
3. Проверить, что значение по умолчанию действительно false

**ТЕСТИРОВАНИЕ:**
- Проверить первый запуск приложения
- Убедиться, что онбординг показывается
- Проверить, что нет краша

**РИСКИ:**
- ⚠️ Если значение по умолчанию не false, может сломаться логика онбординга
- ✅ Митигация: Проверить значение по умолчанию перед удалением

---

### ❌ МЕСТО #2: `UserDefaults.bool()` в `ALADDINApp.init()`

**Файл:** `ALADDINApp.swift:234`  
**Тип:** Критичное (вызывает краш BUILD 95)  
**Время:** 20 минут  
**Риск:** Средний

**ТЕКУЩИЙ КОД:**
```swift
#if DEBUG
// ...
let autoLoginEnabled = UserDefaults.standard.bool(forKey: "auto_login_enabled")  // ❌ ПРОБЛЕМА!
```

**ПРОБЛЕМА:**
- Вызывается синхронно в `init()`
- Может вызвать рекурсию при инициализации View

**РЕШЕНИЕ:**
```swift
// ✅ BUILD 96: Используем @AppStorage вместо UserDefaults для предотвращения рекурсии
@AppStorage("auto_login_enabled") private var autoLoginEnabled: Bool = false

#if DEBUG
// Использовать autoLoginEnabled здесь
#endif
```

**ШАГИ:**
1. Добавить `@AppStorage("auto_login_enabled")` в свойства `ALADDINApp`
2. Удалить строку 234 с `UserDefaults.standard.bool()`
3. Использовать `autoLoginEnabled` вместо локальной переменной

**ТЕСТИРОВАНИЕ:**
- Проверить DEBUG режим
- Убедиться, что auto login работает
- Проверить, что нет краша

**РИСКИ:**
- ⚠️ Может сломаться логика auto login в DEBUG режиме
- ✅ Митигация: Протестировать auto login после изменений

---

### ❌ МЕСТО #3: `MasterLogger.enableVisualLogging` в computed property

**Файл:** `Core/Utilities/MasterLogger.swift:31-38`  
**Тип:** Критичное (вызывает краш BUILD 95)  
**Время:** 30 минут  
**Риск:** Средний

**ТЕКУЩИЙ КОД:**
```swift
private var enableVisualLogging: Bool {
    get {
        UserDefaults.standard.bool(forKey: "enable_visual_logging")  // ❌ ПРОБЛЕМА!
    }
    set {
        UserDefaults.standard.set(newValue, forKey: "enable_visual_logging")
    }
}
```

**ПРОБЛЕМА:**
- Computed property вызывается в `body` или `init()`
- Может вызвать рекурсию с другими `@AppStorage`

**РЕШЕНИЕ:**
```swift
// ✅ BUILD 96: Кешированное значение для предотвращения рекурсии
private var _enableVisualLogging: Bool? = nil

private var enableVisualLogging: Bool {
    get {
        if let cached = _enableVisualLogging {
            return cached
        }
        // Асинхронная загрузка при первом использовании
        Task { @MainActor in
            _enableVisualLogging = UserDefaults.standard.bool(forKey: "enable_visual_logging")
        }
        return false // Значение по умолчанию
    }
    set {
        _enableVisualLogging = newValue
        // Асинхронная установка для предотвращения рекурсии
        Task { @MainActor in
            UserDefaults.standard.set(newValue, forKey: "enable_visual_logging")
        }
    }
}
```

**ШАГИ:**
1. Добавить `_enableVisualLogging` для кеширования
2. Изменить `get` для асинхронной загрузки
3. Изменить `set` для асинхронной установки
4. Обновить все места использования

**ТЕСТИРОВАНИЕ:**
- Проверить включение/выключение visual logging
- Убедиться, что значение сохраняется
- Проверить, что нет краша

**РИСКИ:**
- ⚠️ Может сломаться логика visual logging
- ⚠️ Асинхронная загрузка может вызвать race condition
- ✅ Митигация: Использовать `@MainActor` для синхронизации

---

## 🟡 ЭТАП 2: ПРОБЛЕМНЫЕ МЕСТА (7 мест) - ПРИОРИТЕТ 2

### ❌ МЕСТО #4: `UserDefaults.set()` в `SettingsViewModel.sink` (consent)

**Файл:** `ViewModels/SettingsViewModel.swift:341`  
**Тип:** Проблемное (может вызвать краш в будущем)  
**Время:** 15 минут  
**Риск:** Низкий

**ТЕКУЩИЙ КОД:**
```swift
$consentAccepted
    .dropFirst()
    .sink { accepted in
        UserDefaults.standard.set(accepted, forKey: "personal_data_consent_accepted")  // ❌ ПРОБЛЕМА!
    }
    .store(in: &cancellables)
```

**ПРОБЛЕМА:**
- Вызывается из `sink` в `init()`
- Может вызвать рекурсию с `@AppStorage` в View

**РЕШЕНИЕ:**
```swift
$consentAccepted
    .dropFirst()
    .sink { accepted in
        // ✅ BUILD 96: Асинхронная установка для предотвращения рекурсии
        Task { @MainActor in
            UserDefaults.standard.set(accepted, forKey: "personal_data_consent_accepted")
        }
    }
    .store(in: &cancellables)
```

**ШАГИ:**
1. Обернуть `UserDefaults.set()` в `Task { @MainActor in }`
2. Проверить, что значение сохраняется

**ТЕСТИРОВАНИЕ:**
- Проверить сохранение consent
- Убедиться, что значение сохраняется после перезапуска

**РИСКИ:**
- ⚠️ Асинхронная установка может вызвать задержку
- ✅ Митигация: Использовать `@MainActor` для синхронизации

---

### ❌ МЕСТО #5: `UserDefaults.set()` в `SettingsViewModel.sink` (biometric)

**Файл:** `ViewModels/SettingsViewModel.swift:349`  
**Тип:** Проблемное (может вызвать краш в будущем)  
**Время:** 15 минут  
**Риск:** Низкий

**ТЕКУЩИЙ КОД:**
```swift
$isBiometricEnabled
    .dropFirst()
    .sink { enabled in
        UserDefaults.standard.set(enabled, forKey: "biometricEnabled")  // ❌ ПРОБЛЕМА!
    }
    .store(in: &cancellables)
```

**РЕШЕНИЕ:**
```swift
$isBiometricEnabled
    .dropFirst()
    .sink { enabled in
        // ✅ BUILD 96: Асинхронная установка для предотвращения рекурсии
        Task { @MainActor in
            UserDefaults.standard.set(enabled, forKey: "biometricEnabled")
        }
    }
    .store(in: &cancellables)
```

**ШАГИ:** Аналогично месту #4

**ТЕСТИРОВАНИЕ:** Аналогично месту #4

**РИСКИ:** Аналогично месту #4

---

### ❌ МЕСТО #6: `UserDefaults.set()` в `SettingsViewModel.sink` (theme)

**Файл:** `ViewModels/SettingsViewModel.swift:357`  
**Тип:** Проблемное (может вызвать краш в будущем)  
**Время:** 15 минут  
**Риск:** Низкий

**ТЕКУЩИЙ КОД:**
```swift
$selectedTheme
    .dropFirst()
    .sink { [weak self] theme in
        UserDefaults.standard.set(theme.rawValue, forKey: "selected_theme")  // ❌ ПРОБЛЕМА!
        self?.applyTheme(theme)
    }
    .store(in: &cancellables)
```

**РЕШЕНИЕ:**
```swift
$selectedTheme
    .dropFirst()
    .sink { [weak self] theme in
        // ✅ BUILD 96: Асинхронная установка для предотвращения рекурсии
        Task { @MainActor in
            UserDefaults.standard.set(theme.rawValue, forKey: "selected_theme")
        }
        self?.applyTheme(theme) // Применяем тему синхронно для немедленного эффекта
    }
    .store(in: &cancellables)
```

**ШАГИ:** Аналогично месту #4

**ТЕСТИРОВАНИЕ:**
- Проверить изменение темы
- Убедиться, что тема применяется сразу
- Проверить сохранение темы

**РИСКИ:**
- ⚠️ Асинхронная установка может вызвать задержку сохранения
- ✅ Митигация: Применение темы остается синхронным

---

### ❌ МЕСТО #7: `UserDefaults.string()` в `SettingsViewModel.isAdmin`

**Файл:** `ViewModels/SettingsViewModel.swift:219`  
**Тип:** Проблемное (может вызвать краш в будущем)  
**Время:** 20 минут  
**Риск:** Средний

**ТЕКУЩИЙ КОД:**
```swift
var isAdmin: Bool {
    let userRole = UserDefaults.standard.string(forKey: "user_role") ?? "user"  // ❌ ПРОБЛЕМА!
    return userRole == "admin" || userRole == "administrator"
}
```

**ПРОБЛЕМА:**
- Computed property вызывается в `body` View
- Может вызвать рекурсию

**РЕШЕНИЕ:**
```swift
// ✅ BUILD 96: Кешированное значение для предотвращения рекурсии
@Published private var _isAdmin: Bool = false

var isAdmin: Bool {
    return _isAdmin
}

private func loadIsAdmin() {
    Task { @MainActor in
        let userRole = UserDefaults.standard.string(forKey: "user_role") ?? "user"
        _isAdmin = userRole == "admin" || userRole == "administrator"
    }
}
```

**ШАГИ:**
1. Добавить `@Published private var _isAdmin`
2. Изменить `isAdmin` на возврат `_isAdmin`
3. Добавить `loadIsAdmin()` для асинхронной загрузки
4. Вызвать `loadIsAdmin()` в `init()`

**ТЕСТИРОВАНИЕ:**
- Проверить определение роли admin
- Убедиться, что значение обновляется

**РИСКИ:**
- ⚠️ Может сломаться логика определения admin
- ✅ Митигация: Использовать `@Published` для реактивных обновлений

---

### ❌ МЕСТО #8: `UserDefaults` в `SettingsViewModel.loadInitialState()`

**Файл:** `ViewModels/SettingsViewModel.swift:370-376`  
**Тип:** Проблемное (может вызвать краш в будущем)  
**Время:** 25 минут  
**Риск:** Средний

**ТЕКУЩИЙ КОД:**
```swift
private func loadInitialState() {
    displayName = UserDefaults.standard.string(forKey: "profile_name") ?? ""  // ❌ ПРОБЛЕМА!
    displayAlias = UserDefaults.standard.string(forKey: "profile_alias") ?? ""
    consentAccepted = UserDefaults.standard.bool(forKey: "personal_data_consent_accepted")
    isBiometricEnabled = UserDefaults.standard.bool(forKey: "biometricEnabled")
    
    if let savedTheme = UserDefaults.standard.string(forKey: "selected_theme"),
       let theme = ThemeMode(rawValue: savedTheme) {
        selectedTheme = theme
    }
}
```

**ПРОБЛЕМА:**
- Вызывается из `init()`
- Может вызвать рекурсию при инициализации ViewModel

**РЕШЕНИЕ:**
```swift
private func loadInitialState() {
    // ✅ BUILD 96: Асинхронная загрузка для предотвращения рекурсии
    Task { @MainActor in
        displayName = UserDefaults.standard.string(forKey: "profile_name") ?? ""
        displayAlias = UserDefaults.standard.string(forKey: "profile_alias") ?? ""
        consentAccepted = UserDefaults.standard.bool(forKey: "personal_data_consent_accepted")
        isBiometricEnabled = UserDefaults.standard.bool(forKey: "biometricEnabled")
        
        if let savedTheme = UserDefaults.standard.string(forKey: "selected_theme"),
           let theme = ThemeMode(rawValue: savedTheme) {
            selectedTheme = theme
        }
    }
}
```

**ШАГИ:**
1. Обернуть весь код в `Task { @MainActor in }`
2. Проверить, что значения загружаются

**ТЕСТИРОВАНИЕ:**
- Проверить загрузку всех значений
- Убедиться, что значения отображаются в UI

**РИСКИ:**
- ⚠️ Асинхронная загрузка может вызвать задержку отображения
- ✅ Митигация: Использовать значения по умолчанию до загрузки

---

### ❌ МЕСТО #9: `UserDefaults` в `FamilyScreen.loadAppLimits()`

**Файл:** `Screens/02_FamilyScreen.swift:3727`  
**Тип:** Проблемное (может вызвать краш в будущем)  
**Время:** 20 минут  
**Риск:** Низкий

**ТЕКУЩИЙ КОД:**
```swift
if UserDefaults.standard.object(forKey: appKey) != nil {
    let savedLimit = UserDefaults.standard.double(forKey: appKey)  // ❌ ПРОБЛЕМА!
    if savedLimit > 0 {
        loadedLimits[index].limit = savedLimit
    }
}
```

**ПРОБЛЕМА:**
- Вызывается из `loadAppLimits()` в `body` или `onAppear`
- Может вызвать рекурсию

**РЕШЕНИЕ:**
```swift
// ✅ BUILD 96: Асинхронная загрузка для предотвращения рекурсии
Task { @MainActor in
    if UserDefaults.standard.object(forKey: appKey) != nil {
        let savedLimit = UserDefaults.standard.double(forKey: appKey)
        if savedLimit > 0 {
            loadedLimits[index].limit = savedLimit
        }
    }
}
```

**ШАГИ:**
1. Обернуть код в `Task { @MainActor in }`
2. Проверить, что лимиты загружаются

**ТЕСТИРОВАНИЕ:**
- Проверить загрузку лимитов приложений
- Убедиться, что лимиты отображаются

**РИСКИ:**
- ⚠️ Асинхронная загрузка может вызвать задержку отображения
- ✅ Митигация: Использовать значения по умолчанию до загрузки

---

### ❌ МЕСТО #10: `UserDefaults.bool()` в `FamilyScreen.applyRules()`

**Файл:** `Screens/02_FamilyScreen.swift:4998-5001`  
**Тип:** Проблемное (может вызвать краш в будущем)  
**Время:** 20 минут  
**Риск:** Низкий

**ТЕКУЩИЙ КОД:**
```swift
let parentalRules = ParentalControlRules(
    websiteBlocking: UserDefaults.standard.bool(forKey: "parental_website_blocking"),  // ❌ ПРОБЛЕМА!
    appBlocking: UserDefaults.standard.bool(forKey: "parental_app_blocking"),
    searchBlocking: UserDefaults.standard.bool(forKey: "parental_search_blocking"),
    safesearch: UserDefaults.standard.bool(forKey: "parental_safesearch"),
    // ...
)
```

**ПРОБЛЕМА:**
- Вызывается из `applyRules()` в `body` или `onAppear`
- Может вызвать рекурсию

**РЕШЕНИЕ:**
```swift
// ✅ BUILD 96: Кешированные значения для предотвращения рекурсии
@State private var cachedParentalRules: ParentalControlRules? = nil

private func loadParentalRules() {
    Task { @MainActor in
        cachedParentalRules = ParentalControlRules(
            websiteBlocking: UserDefaults.standard.bool(forKey: "parental_website_blocking"),
            appBlocking: UserDefaults.standard.bool(forKey: "parental_app_blocking"),
            searchBlocking: UserDefaults.standard.bool(forKey: "parental_search_blocking"),
            safesearch: UserDefaults.standard.bool(forKey: "parental_safesearch"),
            // ...
        )
    }
}

// Использовать cachedParentalRules вместо прямого чтения
```

**ШАГИ:**
1. Добавить `@State private var cachedParentalRules`
2. Создать `loadParentalRules()` для асинхронной загрузки
3. Вызвать `loadParentalRules()` в `onAppear`
4. Использовать `cachedParentalRules` в `applyRules()`

**ТЕСТИРОВАНИЕ:**
- Проверить применение правил родительского контроля
- Убедиться, что правила применяются правильно

**РИСКИ:**
- ⚠️ Кеширование может вызвать устаревшие данные
- ✅ Митигация: Обновлять кеш при изменении правил

---

## 📋 ПОСЛЕДОВАТЕЛЬНОСТЬ ВЫПОЛНЕНИЯ

### ФАЗА 1: Критичные места (1-1.5 часа)
1. ✅ Место #1: `ALADDINApp.swift:685` (15 мин)
2. ✅ Место #2: `ALADDINApp.swift:234` (20 мин)
3. ✅ Место #3: `MasterLogger.swift:31-38` (30 мин)
4. ✅ Тестирование критичных мест (15 мин)

### ФАЗА 2: Проблемные места (2-3 часа)
5. ✅ Место #4: `SettingsViewModel.swift:341` (15 мин)
6. ✅ Место #5: `SettingsViewModel.swift:349` (15 мин)
7. ✅ Место #6: `SettingsViewModel.swift:357` (15 мин)
8. ✅ Место #7: `SettingsViewModel.swift:219` (20 мин)
9. ✅ Место #8: `SettingsViewModel.swift:370-376` (25 мин)
10. ✅ Место #9: `FamilyScreen.swift:3727` (20 мин)
11. ✅ Место #10: `FamilyScreen.swift:4998-5001` (20 мин)
12. ✅ Тестирование проблемных мест (30 мин)

### ФАЗА 3: Финальное тестирование (1 час)
13. ✅ Полное тестирование на симуляторе
14. ✅ Полное тестирование на реальном устройстве
15. ✅ Проверка всех функций
16. ✅ Проверка отсутствия крашей

---

## ⚠️ РИСКИ И МИТИГАЦИЯ

### РИСК #1: Сломается логика онбординга
**Вероятность:** Средняя  
**Влияние:** Высокое  
**Митигация:** Проверить значение по умолчанию перед удалением

### РИСК #2: Сломается логика auto login
**Вероятность:** Низкая  
**Влияние:** Среднее  
**Митигация:** Протестировать auto login после изменений

### РИСК #3: Сломается логика visual logging
**Вероятность:** Средняя  
**Влияние:** Низкое  
**Митигация:** Использовать `@MainActor` для синхронизации

### РИСК #4: Асинхронные операции вызовут race conditions
**Вероятность:** Средняя  
**Влияние:** Среднее  
**Митигация:** Использовать `@MainActor` для всех асинхронных операций

### РИСК #5: Задержка отображения данных
**Вероятность:** Высокая  
**Влияние:** Низкое  
**Митигация:** Использовать значения по умолчанию до загрузки

### РИСК #6: Устаревшие данные в кеше
**Вероятность:** Низкая  
**Влияние:** Среднее  
**Митигация:** Обновлять кеш при изменении данных

---

## ✅ КРИТЕРИИ УСПЕХА

1. ✅ Все 10 мест исправлены
2. ✅ Нет крашей при запуске приложения
3. ✅ Все функции работают корректно
4. ✅ Нет рекурсии в логах
5. ✅ Приложение работает стабильно на реальном устройстве

---

## 📊 ОЦЕНКА ВРЕМЕНИ

- **Критичные места:** 1-1.5 часа
- **Проблемные места:** 2-3 часа
- **Тестирование:** 1 час
- **Итого:** 4-6 часов работы

---

## 🎯 ГОТОВНОСТЬ К НАЧАЛУ

Все места найдены, план составлен, риски проанализированы.  
**Готов приступить к исправлениям!**
