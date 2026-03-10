# 🔧 BUILD 95: ФИНАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЯ РЕКУРСИИ

**Дата:** 2026-03-10  
**Версия сборки:** 95 → 96  
**Цель:** Полностью избавиться от рекурсии раз и навсегда

---

## 🎯 СТРАТЕГИЯ: ГИБРИДНЫЙ ПОДХОД

**Этап 1:** Быстрое исправление критичных мест (1-2 часа)  
**Этап 2:** Профилактика новых проблем (2-3 часа)  
**Этап 3:** Долгосрочное решение (3-4 дня)

---

## 🔴 ЭТАП 1: КРИТИЧНЫЕ ИСПРАВЛЕНИЯ (СЕЙЧАС)

### ❌ ПРОБЛЕМА #1: `UserDefaults.set()` в `initializeNavigation()`

**Файл:** `ALADDINApp.swift:685`  
**Проблема:** Вызывает обновление `@AppStorage` → рекурсия

**ТЕКУЩИЙ КОД:**
```swift
if !ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
    // Принудительный сброс онбординга для первого запуска
    UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)  // ❌ ПРОБЛЕМА!
    UserDefaults.standard.synchronize()
}
```

**ИСПРАВЛЕНИЕ #1.1: Асинхронная установка через Task**
```swift
if !ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
    // ✅ BUILD 96: Асинхронная установка для предотвращения рекурсии
    Task { @MainActor in
        // Используем @AppStorage через ALADDINApp, но это статический метод
        // Поэтому используем асинхронную установку через DispatchQueue
        DispatchQueue.main.async {
            UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            UserDefaults.standard.synchronize()
        }
    }
}
```

**ИСПРАВЛЕНИЕ #1.2: Убрать установку вообще (РЕКОМЕНДУЕТСЯ)**
```swift
if !ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
    // ✅ BUILD 96: Убрано UserDefaults.set() - значение уже false по умолчанию в @AppStorage
    // Не нужно устанавливать false, так как @AppStorage уже имеет значение по умолчанию false
    // Это предотвращает рекурсию через обновление @AppStorage
}
```

**РЕКОМЕНДАЦИЯ:** Исправление #1.2 (убрать установку вообще)

---

### ❌ ПРОБЛЕМА #2: `MasterLogger.enableVisualLogging` читается в `body`

**Файл:** `Core/Utilities/MasterLogger.swift:33, 163`  
**Проблема:** Computed property вызывает `UserDefaults.bool()` → может вызвать рекурсию

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

// Используется в:
if enableVisualLogging {  // ← Вызывается в body или init()
    visualLogger.log(...)
}
```

**ИСПРАВЛЕНИЕ #2.1: Кеширование значения**
```swift
class MasterLogger {
    // ✅ BUILD 96: Кешированное значение для предотвращения рекурсии
    private var _enableVisualLogging: Bool? = nil
    
    private var enableVisualLogging: Bool {
        get {
            if let cached = _enableVisualLogging {
                return cached
            }
            let value = UserDefaults.standard.bool(forKey: "enable_visual_logging")
            _enableVisualLogging = value
            return value
        }
        set {
            _enableVisualLogging = newValue
            // ✅ Асинхронная установка для предотвращения рекурсии
            Task { @MainActor in
                DispatchQueue.main.async {
                    UserDefaults.standard.set(newValue, forKey: "enable_visual_logging")
                }
            }
        }
    }
}
```

**ИСПРАВЛЕНИЕ #2.2: Асинхронное чтение (РЕКОМЕНДУЕТСЯ)**
```swift
class MasterLogger {
    // ✅ BUILD 96: Асинхронное чтение для предотвращения рекурсии
    private var _enableVisualLogging: Bool = false
    
    func getEnableVisualLogging() -> Bool {
        return _enableVisualLogging
    }
    
    func setEnableVisualLogging(_ value: Bool) {
        _enableVisualLogging = value
        // Асинхронная установка
        Task { @MainActor in
            DispatchQueue.main.async {
                UserDefaults.standard.set(value, forKey: "enable_visual_logging")
            }
        }
    }
    
    // Загрузка значения при первом использовании
    private func loadEnableVisualLogging() {
        Task { @MainActor in
            _enableVisualLogging = UserDefaults.standard.bool(forKey: "enable_visual_logging")
        }
    }
}
```

**РЕКОМЕНДАЦИЯ:** Исправление #2.2 (асинхронное чтение)

---

### ❌ ПРОБЛЕМА #3: `UserDefaults.bool()` в `ALADDINApp.init()`

**Файл:** `ALADDINApp.swift:234`  
**Проблема:** Вызывается синхронно в `init()` → может вызвать рекурсию

**ТЕКУЩИЙ КОД:**
```swift
#if DEBUG
// ...
let autoLoginEnabled = UserDefaults.standard.bool(forKey: "auto_login_enabled")  // ❌ ПРОБЛЕМА!
```

**ИСПРАВЛЕНИЕ #3.1: Асинхронное чтение**
```swift
#if DEBUG
// ✅ BUILD 96: Асинхронное чтение для предотвращения рекурсии
Task { @MainActor in
    let autoLoginEnabled = UserDefaults.standard.bool(forKey: "auto_login_enabled")
    // Использовать значение здесь
}
```

**ИСПРАВЛЕНИЕ #3.2: Использовать @AppStorage (РЕКОМЕНДУЕТСЯ)**
```swift
// ✅ BUILD 96: Используем @AppStorage вместо UserDefaults для предотвращения рекурсии
@AppStorage("auto_login_enabled") private var autoLoginEnabled: Bool = false

#if DEBUG
// Использовать autoLoginEnabled здесь
#endif
```

**РЕКОМЕНДАЦИЯ:** Исправление #3.2 (использовать @AppStorage)

---

## 🟡 ЭТАП 2: ПРОФИЛАКТИКА (ПОСЛЕ ИСПРАВЛЕНИЙ)

### 📋 ПРАВИЛА ДЛЯ РАЗРАБОТЧИКОВ

**❌ ЗАПРЕЩЕНО:**
1. Использовать `UserDefaults.standard` в `init()` View
2. Использовать `UserDefaults.standard` в `body` View синхронно
3. Использовать `UserDefaults.standard` в `onAppear` синхронно
4. Смешивать `@AppStorage` и `UserDefaults.standard` для одного ключа

**✅ РАЗРЕШЕНО:**
1. Использовать `@AppStorage` в View
2. Использовать `Task {}` для асинхронных операций `UserDefaults`
3. Использовать `UserDefaults` в ViewModel или Manager
4. Использовать кеширование для предотвращения повторных чтений

---

### 🔍 АВТОМАТИЧЕСКИЕ ПРОВЕРКИ

**Добавить в `.swiftlint.yml`:**
```yaml
disabled_rules:
  - trailing_whitespace

opt_in_rules:
  - custom_rules

custom_rules:
  no_userdefaults_in_view_init:
    name: "No UserDefaults in View init"
    regex: '(init\(\)|var body: some View).*UserDefaults\.standard'
    message: "Не используйте UserDefaults.standard в init() или body View. Используйте @AppStorage или Task {}"
    severity: error
```

---

## 🟢 ЭТАП 3: ДОЛГОСРОЧНОЕ РЕШЕНИЕ (БУДУЩЕЕ)

### 🏗️ СОЗДАНИЕ `SettingsManager`

**Файл:** `Core/Managers/SettingsManager.swift`
```swift
import Foundation
import Combine
import SwiftUI

/// Централизованный менеджер настроек для предотвращения рекурсии
@MainActor
class SettingsManager: ObservableObject {
    static let shared = SettingsManager()
    
    // Published свойства для реактивных обновлений
    @Published var hasCompletedOnboarding: Bool = false
    @Published var enableVisualLogging: Bool = false
    @Published var autoLoginEnabled: Bool = false
    
    private let userDefaults = UserDefaults.standard
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        loadSettings()
        setupObservers()
    }
    
    private func loadSettings() {
        hasCompletedOnboarding = userDefaults.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        enableVisualLogging = userDefaults.bool(forKey: "enable_visual_logging")
        autoLoginEnabled = userDefaults.bool(forKey: "auto_login_enabled")
    }
    
    private func setupObservers() {
        // Автоматическое сохранение при изменении
        $hasCompletedOnboarding
            .dropFirst()
            .sink { [weak self] value in
                self?.userDefaults.set(value, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            }
            .store(in: &cancellables)
        
        $enableVisualLogging
            .dropFirst()
            .sink { [weak self] value in
                self?.userDefaults.set(value, forKey: "enable_visual_logging")
            }
            .store(in: &cancellables)
        
        $autoLoginEnabled
            .dropFirst()
            .sink { [weak self] value in
                self?.userDefaults.set(value, forKey: "auto_login_enabled")
            }
            .store(in: &cancellables)
    }
}
```

**Использование в View:**
```swift
@StateObject private var settingsManager = SettingsManager.shared

var body: some View {
    if settingsManager.hasCompletedOnboarding {
        MainScreen()
    } else {
        OnboardingScreen()
    }
}
```

---

## 📊 ЧЕКЛИСТ ИСПРАВЛЕНИЙ

### 🔴 КРИТИЧНЫЕ (сделать сейчас):
- [ ] Убрать `UserDefaults.set()` из `initializeNavigation()` (ALADDINApp.swift:685)
- [ ] Сделать `MasterLogger.enableVisualLogging` асинхронным (MasterLogger.swift:33)
- [ ] Заменить `UserDefaults.bool()` на `@AppStorage` в `ALADDINApp.init()` (ALADDINApp.swift:234)

### 🟡 ПРОФИЛАКТИКА (сделать после критичных):
- [ ] Создать правила для разработчиков
- [ ] Добавить автоматические проверки (SwiftLint)
- [ ] Протестировать на реальном устройстве

### 🟢 ДОЛГОСРОЧНО (сделать в будущем):
- [ ] Создать `SettingsManager` singleton
- [ ] Рефакторинг всех View для использования `SettingsManager`
- [ ] Unit тесты для проверки отсутствия рекурсии

---

## ✅ ПЛАН ДЕЙСТВИЙ

1. **СЕЙЧАС:** Исправить 3 критичных места
2. **СЕГОДНЯ:** Протестировать на реальном устройстве
3. **СЕГОДНЯ:** Отправить BUILD 96
4. **ЭТА НЕДЕЛЯ:** Создать правила и автоматические проверки
5. **СЛЕДУЮЩИЕ 2 НЕДЕЛИ:** Создать `SettingsManager` и рефакторинг

---

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После исправления критичных мест:
- ✅ Краш BUILD 95 должен быть исправлен
- ✅ Рекурсия в `initializeNavigation()` должна исчезнуть
- ✅ Рекурсия в `MasterLogger` должна исчезнуть
- ✅ Рекурсия в `ALADDINApp.init()` должна исчезнуть

**Готов приступить к исправлениям!**
