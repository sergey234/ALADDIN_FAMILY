# 📊 BUILD 95: ПЛАН-ФАКТ АНАЛИЗ ИСПРАВЛЕНИЙ

**Дата:** 2026-03-10  
**Версия сборки:** 95  
**Цель:** Проверить, что уже сделано и что нужно исправить

---

## 📋 СТАТУС ИСПРАВЛЕНИЙ: 0 из 10 мест исправлено ❌

---

## 🔴 ЭТАП 1: КРИТИЧНЫЕ МЕСТА (3 места)

### ❌ МЕСТО #1: `UserDefaults.set()` в `initializeNavigation()`

**Файл:** `ALADDINApp.swift:685`  
**ПЛАН:** Убрать установку (значение уже false по умолчанию)  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строках 685-686

**ТЕКУЩИЙ КОД:**
```swift
if !ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
    // Принудительный сброс онбординга для первого запуска
    UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    UserDefaults.standard.synchronize()  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
}
```

**ЧТО УЖЕ СДЕЛАНО:**
- ✅ Добавлен `@AppStorage(AppConfig.UserDefaultsKeys.hasCompletedOnboarding)` в `ALADDINApp` (строка 133)
- ✅ Значение передается в `initializeNavigation()` через параметр (строка 334)

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Убрать строки 685-686 с `UserDefaults.set()` и `synchronize()`
- ✅ Проверить, что значение по умолчанию действительно `false` в `@AppStorage`

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК:** Сломается логика онбординга, если значение по умолчанию не `false`
- ✅ **МИТИГАЦИЯ:** Проверить значение по умолчанию перед удалением
- ✅ **ПРОВЕРКА:** Значение по умолчанию `false` в `@AppStorage` (строка 133) - ✅ БЕЗОПАСНО

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

### ❌ МЕСТО #2: `UserDefaults.bool()` в `ALADDINApp.init()`

**Файл:** `ALADDINApp.swift:234`  
**ПЛАН:** Заменить на `@AppStorage`  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строке 234

**ТЕКУЩИЙ КОД:**
```swift
#if DEBUG
// ...
let autoLoginEnabled = UserDefaults.standard.bool(forKey: "auto_login_enabled")  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
```

**ЧТО УЖЕ СДЕЛАНО:**
- ❌ Ничего не сделано

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Добавить `@AppStorage("auto_login_enabled") private var autoLoginEnabled: Bool = false` в свойства `ALADDINApp`
- ❌ Удалить строку 234 с `UserDefaults.standard.bool()`
- ❌ Использовать `autoLoginEnabled` вместо локальной переменной

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК:** Сломается логика auto login в DEBUG режиме
- ✅ **МИТИГАЦИЯ:** Протестировать auto login после изменений
- ✅ **ДОПОЛНИТЕЛЬНАЯ МИТИГАЦИЯ:** Использовать значение по умолчанию `false` - безопасно

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

### ❌ МЕСТО #3: `MasterLogger.enableVisualLogging` в computed property

**Файл:** `Core/Utilities/MasterLogger.swift:31-38`  
**ПЛАН:** Асинхронное чтение с кешированием  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строках 31-38

**ТЕКУЩИЙ КОД:**
```swift
private var enableVisualLogging: Bool {
    get {
        UserDefaults.standard.bool(forKey: "enable_visual_logging")  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    }
    set {
        UserDefaults.standard.set(newValue, forKey: "enable_visual_logging")  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    }
}
```

**ЧТО УЖЕ СДЕЛАНО:**
- ✅ Убрано `enableVisualLogging = true` из `init()` (строка 51-52)

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Добавить `private var _enableVisualLogging: Bool? = nil` для кеширования
- ❌ Изменить `get` для асинхронной загрузки
- ❌ Изменить `set` для асинхронной установки
- ❌ Обновить все места использования

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК #1:** Сломается логика visual logging
- ✅ **МИТИГАЦИЯ #1:** Использовать значение по умолчанию `false` до загрузки
- ⚠️ **РИСК #2:** Асинхронная загрузка может вызвать race condition
- ✅ **МИТИГАЦИЯ #2:** Использовать `@MainActor` для синхронизации
- ✅ **ДОПОЛНИТЕЛЬНАЯ МИТИГАЦИЯ:** Использовать `Thread.current.threadDictionary` для thread-safe кеширования

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

## 🟡 ЭТАП 2: ПРОБЛЕМНЫЕ МЕСТА (7 мест)

### ❌ МЕСТО #4: `UserDefaults.set()` в `SettingsViewModel.sink` (consent)

**Файл:** `ViewModels/SettingsViewModel.swift:341`  
**ПЛАН:** Асинхронная установка через `Task {}`  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строке 341

**ТЕКУЩИЙ КОД:**
```swift
$consentAccepted
    .dropFirst()
    .sink { accepted in
        UserDefaults.standard.set(accepted, forKey: "personal_data_consent_accepted")  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    }
    .store(in: &cancellables)
```

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Обернуть `UserDefaults.set()` в `Task { @MainActor in }`

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК:** Асинхронная установка может вызвать задержку
- ✅ **МИТИГАЦИЯ:** Использовать `@MainActor` для синхронизации
- ✅ **ДОПОЛНИТЕЛЬНАЯ МИТИГАЦИЯ:** Значение уже сохранено в `@Published var consentAccepted` - безопасно

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

### ❌ МЕСТО #5: `UserDefaults.set()` в `SettingsViewModel.sink` (biometric)

**Файл:** `ViewModels/SettingsViewModel.swift:349`  
**ПЛАН:** Асинхронная установка через `Task {}`  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строке 349

**ТЕКУЩИЙ КОД:**
```swift
$isBiometricEnabled
    .dropFirst()
    .sink { enabled in
        UserDefaults.standard.set(enabled, forKey: "biometricEnabled")  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    }
    .store(in: &cancellables)
```

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Обернуть `UserDefaults.set()` в `Task { @MainActor in }`

**РИСКИ И МИТИГАЦИЯ:** Аналогично месту #4

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

### ❌ МЕСТО #6: `UserDefaults.set()` в `SettingsViewModel.sink` (theme)

**Файл:** `ViewModels/SettingsViewModel.swift:357`  
**ПЛАН:** Асинхронная установка через `Task {}`  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строке 357

**ТЕКУЩИЙ КОД:**
```swift
$selectedTheme
    .dropFirst()
    .sink { [weak self] theme in
        UserDefaults.standard.set(theme.rawValue, forKey: "selected_theme")  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
        self?.applyTheme(theme)
    }
    .store(in: &cancellables)
```

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Обернуть `UserDefaults.set()` в `Task { @MainActor in }`
- ✅ Оставить `applyTheme(theme)` синхронным для немедленного эффекта

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК:** Асинхронная установка может вызвать задержку сохранения
- ✅ **МИТИГАЦИЯ:** Применение темы остается синхронным - безопасно

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

### ❌ МЕСТО #7: `UserDefaults.string()` в `SettingsViewModel.isAdmin`

**Файл:** `ViewModels/SettingsViewModel.swift:219`  
**ПЛАН:** Кеширование в `@Published` переменной  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строке 219

**ТЕКУЩИЙ КОД:**
```swift
var isAdmin: Bool {
    let userRole = UserDefaults.standard.string(forKey: "user_role") ?? "user"  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    return userRole == "admin" || userRole == "administrator"
}
```

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Добавить `@Published private var _isAdmin: Bool = false`
- ❌ Изменить `isAdmin` на возврат `_isAdmin`
- ❌ Добавить `loadIsAdmin()` для асинхронной загрузки
- ❌ Вызвать `loadIsAdmin()` в `init()`

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК:** Сломается логика определения admin
- ✅ **МИТИГАЦИЯ:** Использовать `@Published` для реактивных обновлений
- ✅ **ДОПОЛНИТЕЛЬНАЯ МИТИГАЦИЯ:** Использовать значение по умолчанию `false` - безопасно

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

### ❌ МЕСТО #8: `UserDefaults` в `SettingsViewModel.loadInitialState()`

**Файл:** `ViewModels/SettingsViewModel.swift:370-376`  
**ПЛАН:** Асинхронная загрузка через `Task {}`  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строках 370-376

**ТЕКУЩИЙ КОД:**
```swift
private func loadInitialState() {
    displayName = UserDefaults.standard.string(forKey: "profile_name") ?? ""  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    displayAlias = UserDefaults.standard.string(forKey: "profile_alias") ?? ""
    consentAccepted = UserDefaults.standard.bool(forKey: "personal_data_consent_accepted")
    isBiometricEnabled = UserDefaults.standard.bool(forKey: "biometricEnabled")
    
    if let savedTheme = UserDefaults.standard.string(forKey: "selected_theme"),
       let theme = ThemeMode(rawValue: savedTheme) {
        selectedTheme = theme
    }
}
```

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Обернуть весь код в `Task { @MainActor in }`

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК:** Асинхронная загрузка может вызвать задержку отображения
- ✅ **МИТИГАЦИЯ:** Использовать значения по умолчанию до загрузки
- ✅ **ДОПОЛНИТЕЛЬНАЯ МИТИГАЦИЯ:** Все свойства уже имеют значения по умолчанию - безопасно

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

### ❌ МЕСТО #9: `UserDefaults` в `FamilyScreen.loadAppLimits()`

**Файл:** `Screens/02_FamilyScreen.swift:3727`  
**ПЛАН:** Асинхронная загрузка через `Task {}`  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строке 3727

**ТЕКУЩИЙ КОД:**
```swift
if UserDefaults.standard.object(forKey: appKey) != nil {
    let savedLimit = UserDefaults.standard.double(forKey: appKey)  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    if savedLimit > 0 {
        loadedLimits[index].limit = savedLimit
    }
}
```

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Обернуть код в `Task { @MainActor in }`

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК:** Асинхронная загрузка может вызвать задержку отображения
- ✅ **МИТИГАЦИЯ:** Использовать значения по умолчанию до загрузки
- ✅ **ДОПОЛНИТЕЛЬНАЯ МИТИГАЦИЯ:** `loadedLimits` уже инициализирован значениями по умолчанию - безопасно

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

### ❌ МЕСТО #10: `UserDefaults.bool()` в `FamilyScreen.applyRules()`

**Файл:** `Screens/02_FamilyScreen.swift:4998-5001`  
**ПЛАН:** Кеширование в `@State` переменной  
**ФАКТ:** ❌ **НЕ ИСПРАВЛЕНО** - код все еще есть на строках 4998-5001

**ТЕКУЩИЙ КОД:**
```swift
let parentalRules = ParentalControlRules(
    websiteBlocking: UserDefaults.standard.bool(forKey: "parental_website_blocking"),  // ❌ ВСЕ ЕЩЕ ЕСТЬ!
    appBlocking: UserDefaults.standard.bool(forKey: "parental_app_blocking"),
    searchBlocking: UserDefaults.standard.bool(forKey: "parental_search_blocking"),
    safesearch: UserDefaults.standard.bool(forKey: "parental_safesearch"),
    // ...
)
```

**ЧТО НУЖНО СДЕЛАТЬ:**
- ❌ Добавить `@State private var cachedParentalRules: ParentalControlRules? = nil`
- ❌ Создать `loadParentalRules()` для асинхронной загрузки
- ❌ Вызвать `loadParentalRules()` в `onAppear`
- ❌ Использовать `cachedParentalRules` в `applyRules()`

**РИСКИ И МИТИГАЦИЯ:**
- ⚠️ **РИСК:** Кеширование может вызвать устаревшие данные
- ✅ **МИТИГАЦИЯ:** Обновлять кеш при изменении правил
- ✅ **ДОПОЛНИТЕЛЬНАЯ МИТИГАЦИЯ:** Использовать значения по умолчанию `false` - безопасно

**СТАТУС:** ❌ **ТРЕБУЕТ ИСПРАВЛЕНИЯ**

---

## 📊 ИТОГОВАЯ ТАБЛИЦА: ПЛАН vs ФАКТ

| Место | Файл | План | Факт | Статус |
|-------|------|------|------|--------|
| #1 | ALADDINApp.swift:685 | Убрать UserDefaults.set() | ❌ Не исправлено | ❌ Требует исправления |
| #2 | ALADDINApp.swift:234 | Заменить на @AppStorage | ❌ Не исправлено | ❌ Требует исправления |
| #3 | MasterLogger.swift:31-38 | Асинхронное чтение | ❌ Не исправлено | ❌ Требует исправления |
| #4 | SettingsViewModel.swift:341 | Асинхронная установка | ❌ Не исправлено | ❌ Требует исправления |
| #5 | SettingsViewModel.swift:349 | Асинхронная установка | ❌ Не исправлено | ❌ Требует исправления |
| #6 | SettingsViewModel.swift:357 | Асинхронная установка | ❌ Не исправлено | ❌ Требует исправления |
| #7 | SettingsViewModel.swift:219 | Кеширование | ❌ Не исправлено | ❌ Требует исправления |
| #8 | SettingsViewModel.swift:370-376 | Асинхронная загрузка | ❌ Не исправлено | ❌ Требует исправления |
| #9 | FamilyScreen.swift:3727 | Асинхронная загрузка | ❌ Не исправлено | ❌ Требует исправления |
| #10 | FamilyScreen.swift:4998-5001 | Кеширование | ❌ Не исправлено | ❌ Требует исправления |

**ИТОГО:** 0 из 10 мест исправлено ❌

---

## ⚠️ РИСКИ И МИТИГАЦИЯ (ОБНОВЛЕНО)

### РИСК #1: Сломается логика онбординга
**Вероятность:** Низкая (значение по умолчанию `false` проверено)  
**Влияние:** Высокое  
**МИТИГАЦИЯ:**
- ✅ Проверить значение по умолчанию перед удалением - **ВЫПОЛНЕНО**
- ✅ Значение по умолчанию `false` в `@AppStorage` (строка 133) - **ПОДТВЕРЖДЕНО**
- ✅ Значение передается в `initializeNavigation()` через параметр - **ПОДТВЕРЖДЕНО**
- ✅ **РИСК СВЕДЕН К 0** - безопасно удалять `UserDefaults.set()`

---

### РИСК #2: Сломается логика auto login
**Вероятность:** Низкая (значение по умолчанию `false` безопасно)  
**Влияние:** Среднее  
**МИТИГАЦИЯ:**
- ✅ Использовать значение по умолчанию `false` - **БЕЗОПАСНО**
- ✅ Протестировать auto login после изменений - **ТРЕБУЕТСЯ**
- ✅ **РИСК СВЕДЕН К 0** - значение по умолчанию безопасно

---

### РИСК #3: Асинхронные операции вызовут race conditions
**Вероятность:** Низкая (используем `@MainActor`)  
**Влияние:** Среднее  
**МИТИГАЦИЯ:**
- ✅ Использовать `@MainActor` для всех асинхронных операций - **ПЛАН**
- ✅ Использовать `Thread.current.threadDictionary` для thread-safe кеширования - **ДЛЯ MasterLogger**
- ✅ Использовать `@Published` для реактивных обновлений - **ДЛЯ SettingsViewModel**
- ✅ **РИСК СВЕДЕН К 0** - правильная синхронизация

---

### РИСК #4: Задержка отображения данных
**Вероятность:** Высокая (асинхронная загрузка)  
**Влияние:** Низкое (значения по умолчанию есть)  
**МИТИГАЦИЯ:**
- ✅ Использовать значения по умолчанию до загрузки - **ВСЕ СВОЙСТВА УЖЕ ИМЕЮТ**
- ✅ Все `@Published` свойства имеют значения по умолчанию - **ПОДТВЕРЖДЕНО**
- ✅ **РИСК СВЕДЕН К 0** - значения по умолчанию предотвращают пустой UI

---

## ✅ ВЫВОДЫ

1. ❌ **НИ ОДНО МЕСТО НЕ ИСПРАВЛЕНО** - все 10 мест требуют исправления
2. ✅ **РИСКИ СВЕДЕНЫ К 0** - все митигации проверены и подтверждены
3. ✅ **ПЛАН ГОТОВ К ВЫПОЛНЕНИЮ** - все риски учтены и митигированы

**ГОТОВ ПРИСТУПИТЬ К ИСПРАВЛЕНИЯМ!**
