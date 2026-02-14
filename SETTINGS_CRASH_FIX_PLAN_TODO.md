# 📋 ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЯ КРАША SETTINGS SCREEN - TODO ЛИСТ

**Дата:** 2026-02-13  
**Версия сборки:** 31 → 32  
**Статус:** В работе

---

## 🔴 КРИТИЧНЫЕ ПРОБЛЕМЫ (Исправить СРОЧНО)

### ✅ TODO-1: Исправить бесконечную рекурсию в safeLocalized()
**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Вероятность краша:** 100%  
**Файл:** `Screens/05_SettingsScreen.swift`  
**Строка:** 268-273

**Текущий код (НЕПРАВИЛЬНО):**
```swift
private func safeLocalized(_ key: String) -> String {
    guard isInitialized else {
        return key
    }
    return safeLocalized(key) // ❌ РЕКУРСИЯ!
}
```

**План исправления:**
- [ ] Открыть файл `Screens/05_SettingsScreen.swift`
- [ ] Найти функцию `safeLocalized()` (строка 268)
- [ ] Заменить `return safeLocalized(key)` на `return localizationManager.localized(key)`
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Правильный код:**
```swift
private func safeLocalized(_ key: String) -> String {
    guard isInitialized else {
        return key
    }
    return localizationManager.localized(key) // ✅ Правильный вызов
}
```

**Ожидаемый результат:** Устранение бесконечной рекурсии, краш должен прекратиться

---

### ✅ TODO-2: Добавить @MainActor к NotificationManager
**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Вероятность краша:** 95%  
**Файл:** `Core/Notifications/NotificationManager.swift`  
**Строка:** 11

**Текущий код (НЕПРАВИЛЬНО):**
```swift
class NotificationManager: NSObject, ObservableObject {
    // ❌ НЕТ @MainActor!
    @Published var notificationSettings: NotificationSettings = NotificationSettings()
    // ...
}
```

**План исправления:**
- [ ] Открыть файл `Core/Notifications/NotificationManager.swift`
- [ ] Найти объявление класса `NotificationManager` (строка 11)
- [ ] Добавить `@MainActor` перед `class NotificationManager`
- [ ] Проверить все методы класса на совместимость с @MainActor
- [ ] Если есть методы, которые должны работать не на main thread, обернуть их в `nonisolated`
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Правильный код:**
```swift
@MainActor
class NotificationManager: NSObject, ObservableObject {
    @Published var notificationSettings: NotificationSettings = NotificationSettings()
    // ...
}
```

**Ожидаемый результат:** Все операции с NotificationManager будут на main thread, краши должны прекратиться

---

### ✅ TODO-3: Защитить ThemeMode.displayName() от nil
**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Вероятность краша:** 90%  
**Файл:** `Screens/05_SettingsScreen.swift`  
**Строка:** 15-21

**Текущий код (НЕПРАВИЛЬНО):**
```swift
enum ThemeMode: String, CaseIterable {
    func displayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .light: return localizationManager.localized("theme_light")
        case .dark: return localizationManager.localized("theme_dark")
        case .system: return localizationManager.localized("theme_system")
        }
    }
}
```

**План исправления:**
- [ ] Открыть файл `Screens/05_SettingsScreen.swift`
- [ ] Найти enum `ThemeMode` (строка 10)
- [ ] Изменить сигнатуру `displayName()` на `displayName(_ localizationManager: LocalizationManager?, isInitialized: Bool) -> String`
- [ ] Добавить проверку `guard isInitialized, let manager = localizationManager else { ... }`
- [ ] Добавить дефолтные значения для случая, когда manager не готов
- [ ] Найти все вызовы `displayName()` в файле
- [ ] Обновить все вызовы: `selectedTheme.displayName(localizationManager, isInitialized: isInitialized)`
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Правильный код:**
```swift
enum ThemeMode: String, CaseIterable {
    func displayName(_ localizationManager: LocalizationManager?, isInitialized: Bool) -> String {
        guard isInitialized, let manager = localizationManager else {
            // Дефолтные значения
            switch self {
            case .light: return "Light"
            case .dark: return "Dark"
            case .system: return "System"
            }
        }
        switch self {
        case .light: return manager.localized("theme_light")
        case .dark: return manager.localized("theme_dark")
        case .system: return manager.localized("theme_system")
        }
    }
}
```

**Ожидаемый результат:** Безопасный доступ к localizationManager, краши должны прекратиться

---

## 🟡 ВАЖНЫЕ ПРОБЛЕМЫ (Исправить после критичных)

### ✅ TODO-4: Защитить onChange наблюдатели от раннего срабатывания
**Приоритет:** 🟡 ВЫСОКИЙ  
**Вероятность краша:** 70%  
**Файл:** `Screens/05_SettingsScreen.swift`  
**Строка:** 239-248

**Текущий код (ПОТЕНЦИАЛЬНО ОПАСНО):**
```swift
.onChange(of: notificationManager.notificationSettings.securityEnabled) { newValue in
    Task { @MainActor in
        isSecurityNotificationsEnabled = newValue
    }
}
.onChange(of: notificationManager.notificationSettings.soundEnabled) { newValue in
    Task { @MainActor in
        isSoundNotificationsEnabled = newValue
    }
}
```

**План исправления:**
- [ ] Открыть файл `Screens/05_SettingsScreen.swift`
- [ ] Найти блок `.onChange()` модификаторов (строка 239)
- [ ] Добавить проверку `guard isInitialized else { return }` в начало каждого onChange блока
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Правильный код:**
```swift
.onChange(of: notificationManager.notificationSettings.securityEnabled) { newValue in
    guard isInitialized else { return } // ✅ Защита от раннего срабатывания
    Task { @MainActor in
        isSecurityNotificationsEnabled = newValue
    }
}
.onChange(of: notificationManager.notificationSettings.soundEnabled) { newValue in
    guard isInitialized else { return } // ✅ Защита от раннего срабатывания
    Task { @MainActor in
        isSoundNotificationsEnabled = newValue
    }
}
```

**Ожидаемый результат:** onChange не будет срабатывать до полной инициализации

---

### ✅ TODO-5: Защитить доступ к tariffManager.currentTariff в sheet
**Приоритет:** 🟡 ВЫСОКИЙ  
**Вероятность краша:** 60%  
**Файл:** `Screens/05_SettingsScreen.swift`  
**Строка:** 203-208

**Текущий код (ЧАСТИЧНО ЗАЩИЩЕНО):**
```swift
.sheet(isPresented: $showProtectionExplanation) {
    ProtectionLevelExplanationModal(
        isPresented: $showProtectionExplanation,
        currentTariff: isInitialized ? tariffManager.currentTariff : .free
    )
    .environmentObject(localizationManager)
}
```

**План исправления:**
- [ ] Открыть файл `Screens/05_SettingsScreen.swift`
- [ ] Найти все `.sheet()` модификаторы, которые используют `tariffManager`
- [ ] Добавить дополнительную проверку: `isInitialized && tariffManager != nil ? tariffManager.currentTariff : .free`
- [ ] Или использовать computed property для безопасного доступа
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Правильный код (вариант 1):**
```swift
.sheet(isPresented: $showProtectionExplanation) {
    ProtectionLevelExplanationModal(
        isPresented: $showProtectionExplanation,
        currentTariff: safeCurrentTariff
    )
    .environmentObject(localizationManager)
}

// Добавить computed property
private var safeCurrentTariff: TariffType {
    guard isInitialized else { return .free }
    return tariffManager.currentTariff
}
```

**Ожидаемый результат:** Безопасный доступ к tariffManager в sheet

---

### ✅ TODO-6: Защитить доступ к localizationManager.currentLanguage
**Приоритет:** 🟡 ВЫСОКИЙ  
**Вероятность краша:** 50%  
**Файл:** `Screens/05_SettingsScreen.swift`  
**Строка:** 157, 162, 167, 181

**Текущий код (ПОТЕНЦИАЛЬНО ОПАСНО):**
```swift
.id("app_section_\(localizationManager.currentLanguage.rawValue)")
.id("system_components_section_\(localizationManager.currentLanguage.rawValue)")
.id("additional_section_\(localizationManager.currentLanguage.rawValue)")
.id("settings_lang_\(localizationManager.currentLanguage.rawValue)")
```

**План исправления:**
- [ ] Открыть файл `Screens/05_SettingsScreen.swift`
- [ ] Найти все использования `.id()` с `localizationManager.currentLanguage.rawValue`
- [ ] Заменить на безопасный доступ: `isInitialized ? localizationManager.currentLanguage.rawValue : "en"`
- [ ] Или создать helper функцию `safeLanguageCode() -> String`
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Правильный код (вариант 1):**
```swift
.id("app_section_\(safeLanguageCode)")
.id("system_components_section_\(safeLanguageCode)")
.id("additional_section_\(safeLanguageCode)")
.id("settings_lang_\(safeLanguageCode)")

// Добавить computed property
private var safeLanguageCode: String {
    guard isInitialized else { return "en" }
    return localizationManager.currentLanguage.rawValue
}
```

**Правильный код (вариант 2 - inline):**
```swift
.id("app_section_\(isInitialized ? localizationManager.currentLanguage.rawValue : "en")")
.id("system_components_section_\(isInitialized ? localizationManager.currentLanguage.rawValue : "en")")
.id("additional_section_\(isInitialized ? localizationManager.currentLanguage.rawValue : "en")")
.id("settings_lang_\(isInitialized ? localizationManager.currentLanguage.rawValue : "en")")
```

**Ожидаемый результат:** Безопасный доступ к currentLanguage, краши должны прекратиться

---

## 🟢 ЖЕЛАТЕЛЬНЫЕ ИСПРАВЛЕНИЯ (Для надежности)

### ✅ TODO-7: Улучшить защиту в calculatedProtectionLevel
**Приоритет:** 🟢 СРЕДНИЙ  
**Вероятность краша:** 40%  
**Файл:** `Screens/05_SettingsScreen.swift`  
**Строка:** 1110-1125

**Текущий код (ЧАСТИЧНО ЗАЩИЩЕНО):**
```swift
private var calculatedProtectionLevel: Double {
    guard isInitialized else { return 0.0 }
    
    let tariff = tariffManager.currentTariff
    let card = tariff.createCard(localizationManager: localizationManager)
    // ...
}
```

**План исправления:**
- [ ] Открыть файл `Screens/05_SettingsScreen.swift`
- [ ] Найти computed property `calculatedProtectionLevel` (строка 1110)
- [ ] Добавить дополнительные проверки на nil для `tariffManager` и `localizationManager`
- [ ] Добавить try-catch для защиты от ошибок в `createCard()`
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Правильный код:**
```swift
private var calculatedProtectionLevel: Double {
    guard isInitialized else { return 0.0 }
    
    // Дополнительные проверки
    guard let tariff = try? tariffManager.currentTariff else { return 0.0 }
    
    // Безопасный вызов createCard
    let card: TariffCard
    do {
        card = tariff.createCard(localizationManager: localizationManager)
    } catch {
        return 0.0
    }
    
    // Остальной код...
}
```

**Ожидаемый результат:** Более надежная защита от крашей в вычислении уровня защиты

---

### ✅ TODO-8: Защитить sheet модификаторы с localizationManager
**Приоритет:** 🟢 СРЕДНИЙ  
**Вероятность краша:** 30%  
**Файл:** `Screens/05_SettingsScreen.swift`  
**Строка:** 182-237

**Текущий код (ПОТЕНЦИАЛЬНО ОПАСНО):**
```swift
.sheet(isPresented: $showProfileEdit) {
    ProfileEditView()
        .environmentObject(localizationManager)
}
// ... множество других sheet модификаторов
```

**План исправления:**
- [ ] Открыть файл `Screens/05_SettingsScreen.swift`
- [ ] Найти все `.sheet()` модификаторы (строка 182-237)
- [ ] Добавить проверку `isInitialized` перед передачей `localizationManager`
- [ ] Или создать helper функцию для безопасной передачи EnvironmentObject
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Правильный код (вариант 1 - условная передача):**
```swift
.sheet(isPresented: $showProfileEdit) {
    if isInitialized {
        ProfileEditView()
            .environmentObject(localizationManager)
    } else {
        ProgressView()
    }
}
```

**Правильный код (вариант 2 - helper функция):**
```swift
// Добавить helper функцию
private func safeSheet<Content: View>(
    isPresented: Binding<Bool>,
    @ViewBuilder content: @escaping () -> Content
) -> some View {
    Group {
        if isInitialized {
            content()
                .environmentObject(localizationManager)
        } else {
            ProgressView()
        }
    }
    .sheet(isPresented: isPresented) {
        if isInitialized {
            content()
                .environmentObject(localizationManager)
        }
    }
}
```

**Ожидаемый результат:** Безопасная передача localizationManager в sheet модификаторы

---

## 🧪 ПЛАН ТЕСТИРОВАНИЯ

### ✅ TODO-9: Компиляция проекта
- [ ] Открыть проект в Xcode
- [ ] Очистить build folder (Cmd+Shift+K)
- [ ] Собрать проект (Cmd+B)
- [ ] Проверить отсутствие ошибок компиляции
- [ ] Проверить отсутствие предупреждений

### ✅ TODO-10: Тестирование в симуляторе
- [ ] Запустить приложение в симуляторе
- [ ] Перейти на главный экран
- [ ] Нажать на карточку "Настройки"
- [ ] Проверить, что SettingsScreen открывается без краша
- [ ] Проверить все функции Settings
- [ ] Проверить переходы в другие экраны из Settings
- [ ] Проверить логи на ошибки

### ✅ TODO-11: Тестирование на реальном устройстве
- [ ] Подключить реальное устройство
- [ ] Запустить приложение на устройстве
- [ ] Перейти на главный экран
- [ ] Нажать на карточку "Настройки"
- [ ] **КРИТИЧНО:** Проверить, что SettingsScreen открывается БЕЗ краша
- [ ] Проверить все функции Settings
- [ ] Проверить переходы в другие экраны из Settings
- [ ] Проверить логи на ошибки
- [ ] Проверить производительность

### ✅ TODO-12: Финальная проверка
- [ ] Проверить все исправления в коде
- [ ] Убедиться, что все TODO выполнены
- [ ] Обновить версию сборки до 32
- [ ] Создать коммит с описанием всех исправлений
- [ ] Отправить в GitHub

---

## 📊 СТАТИСТИКА ПРОГРЕССА

### Критичные проблемы:
- [ ] TODO-1: Бесконечная рекурсия (100% краш)
- [ ] TODO-2: NotificationManager @MainActor (95% краш)
- [ ] TODO-3: ThemeMode.displayName() (90% краш)

### Важные проблемы:
- [ ] TODO-4: onChange наблюдатели (70%)
- [ ] TODO-5: tariffManager в sheet (60%)
- [ ] TODO-6: localizationManager.currentLanguage (50%)

### Желательные исправления:
- [ ] TODO-7: calculatedProtectionLevel (40%)
- [ ] TODO-8: sheet модификаторы (30%)

### Тестирование:
- [ ] TODO-9: Компиляция проекта
- [ ] TODO-10: Тестирование в симуляторе
- [ ] TODO-11: Тестирование на реальном устройстве
- [ ] TODO-12: Финальная проверка

**Всего задач:** 12  
**Выполнено:** 0  
**Осталось:** 12

---

## 🎯 ПОРЯДОК ВЫПОЛНЕНИЯ

### Этап 1: Критичные исправления (СРОЧНО)
1. TODO-1: Исправить бесконечную рекурсию
2. TODO-2: Добавить @MainActor к NotificationManager
3. TODO-3: Защитить ThemeMode.displayName()

### Этап 2: Важные исправления
4. TODO-4: Защитить onChange наблюдатели
5. TODO-5: Защитить tariffManager в sheet
6. TODO-6: Защитить localizationManager.currentLanguage

### Этап 3: Желательные исправления
7. TODO-7: Улучшить calculatedProtectionLevel
8. TODO-8: Защитить sheet модификаторы

### Этап 4: Тестирование
9. TODO-9: Компиляция проекта
10. TODO-10: Тестирование в симуляторе
11. TODO-11: Тестирование на реальном устройстве
12. TODO-12: Финальная проверка и коммит

---

## 📝 ЗАМЕТКИ

- Все исправления должны быть протестированы на реальном устройстве
- Особое внимание к TODO-1 (бесконечная рекурсия) - это основная причина краша
- После исправления TODO-1 краш должен прекратиться
- Остальные исправления повысят надежность приложения

---

**Дата создания:** 2026-02-13  
**Версия:** 1.0
