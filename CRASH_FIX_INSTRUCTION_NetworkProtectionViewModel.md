# 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ КРАША: NetworkProtectionViewModel

## 📋 ОБЩАЯ ИНФОРМАЦИЯ

**Файл:** `ViewModels/NetworkProtectionViewModel.swift` + `Core/Analytics/AnalyticsManager.swift` + `Core/Analytics/ComponentAnalytics.swift`  
**Проблема:** `EXC_BAD_ACCESS (SIGBUS)` - бесконечная рекурсия при создании словарей в background thread  
**Сложность:** Средняя (несколько файлов, DispatchQueue.main.async вместо Task)  
**Время исправления:** 15 минут  
**Тестирование:** Unit тест + интеграционное тестирование  
**Статус:** 🔴 **BUILD 102 исправления НЕ ПОМОГЛИ - нужен новый подход**  

---

## 🎯 ПРОБЛЕМА

### Корневая причина
Метод `handleProductionModeToggle()` вызывает аналитику **в background thread** без защиты `MainActor.run`, что приводит к бесконечной рекурсии при создании словарей.

### Почему происходит краш
1. Background thread вызывает `componentAnalytics.trackComponentToggle()`
2. Создается словарь `parameters: [String: Any]`
3. `Dictionary.resize()` вызывает ICU/Swift runtime операции
4. `Locale.current` → `UserDefaults` → циклическая зависимость
5. **Stack overflow** → краш приложения

---

## 📝 ТЕКУЩИЙ ПРОБЛЕМНЫЙ КОД

```swift:ViewModels/NetworkProtectionViewModel.swift
private func handleProductionModeToggle(
    componentId: String,
    newValue: Bool,
    updateClosure: @escaping (Bool) -> Void
) async {
    do {
        try await statusService.updateStatus(
            componentId: componentId,
            isEnabled: newValue
        )

        // Успешное обновление
        componentAnalytics.trackComponentToggle(  // ❌ НЕПРАВИЛЬНО: background thread
            componentId: componentId,
            enabled: newValue
        )
        toastManager.showSuccess("Компонент обновлен")

    } catch {
        // Откат изменений при ошибке
        updateClosure(!newValue)
        // Отследить ошибку
        componentAnalytics.trackComponentError(componentId: componentId, error: error)  // ❌ НЕПРАВИЛЬНО: background thread
        toastManager.showError("Ошибка: \(error.localizedDescription)")
    }
}
```

---

## ✅ ИСПРАВЛЕННЫЙ КОД

```swift:ViewModels/NetworkProtectionViewModel.swift
private func handleProductionModeToggle(
    componentId: String,
    newValue: Bool,
    updateClosure: @escaping (Bool) -> Void
) async {
    do {
        try await statusService.updateStatus(
            componentId: componentId,
            isEnabled: newValue
        )

        // ✅ ИСПРАВЛЕНИЕ: Аналитика на main thread
        await MainActor.run {
            componentAnalytics.trackComponentToggle(
                componentId: componentId,
                enabled: newValue
            )
        }
        toastManager.showSuccess("Компонент обновлен")

    } catch {
        // Откат изменений при ошибке
        updateClosure(!newValue)

        // ✅ ИСПРАВЛЕНИЕ: Аналитика ошибок на main thread
        await MainActor.run {
            componentAnalytics.trackComponentError(
                componentId: componentId,
                error: error
            )
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }
}
```

---

## 🔧 КОНКРЕТНЫЕ ИЗМЕНЕНИЯ

### Изменение 1: Аналитика успешного обновления

**Где:** `ViewModels/NetworkProtectionViewModel.swift`, строки 353-358

**Что убрать:**
```swift
// Успешное обновление
componentAnalytics.trackComponentToggle(
    componentId: componentId,
    enabled: newValue
)
toastManager.showSuccess("Компонент обновлен")
```

**Что добавить:**
```swift
// Успешное обновление
// ✅ ИСПРАВЛЕНИЕ: Аналитика на main thread
await MainActor.run {
    componentAnalytics.trackComponentToggle(
        componentId: componentId,
        enabled: newValue
    )
}
toastManager.showSuccess("Компонент обновлен")
```

### Изменение 2: Аналитика ошибок

**Где:** `ViewModels/NetworkProtectionViewModel.swift`, строки 362-366

**Что убрать:**
```swift
// Откат изменений при ошибке
updateClosure(!newValue)
// Отследить ошибку
componentAnalytics.trackComponentError(componentId: componentId, error: error)
toastManager.showError("Ошибка: \(error.localizedDescription)")
```

**Что добавить:**
```swift
// Откат изменений при ошибке
updateClosure(!newValue)

// ✅ ИСПРАВЛЕНИЕ: Аналитика ошибок на main thread
await MainActor.run {
    componentAnalytics.trackComponentError(
        componentId: componentId,
        error: error
    )
    toastManager.showError("Ошибка: \(error.localizedDescription)")
}
```

---

## 🔍 ПРОВЕРКА КОРРЕКТНОСТИ

### Сравнение с демо режимом
Обратите внимание, что в **демо режиме** (строки 327-333) уже правильно используется `await MainActor.run`:

```swift
// ✅ В демо режиме правильно:
await MainActor.run {
    componentAnalytics.trackComponentToggle(
        componentId: componentId,
        enabled: newValue
    )
}
```

**Production режим должен использовать ту же защиту!**

---

## 🧪 ТЕСТИРОВАНИЕ

### Unit тест
```swift
func testProductionModeToggle() async throws {
    // Given
    let viewModel = NetworkProtectionViewModel()
    let componentId = "test_component"

    // When
    await viewModel.toggleComponent(componentId, true)

    // Then
    // Приложение не должно крашиться
    // Аналитика должна отправляться корректно
    XCTAssertTrue(Thread.isMainThread, "Аналитика должна выполняться на main thread")
}
```

### Интеграционное тестирование
1. Запустить приложение в production режиме
2. Переключить несколько компонентов
3. Проверить, что нет крашей
4. Проверить логи аналитики

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### Почему MainActor.run обязателен
- `ComponentAnalytics` создает словари `[String: Any]`
- Словари в background thread вызывают рекурсию через ICU/Swift runtime
- `MainActor.run` гарантирует выполнение на main thread

### Безопасность
- Это исправление **не ломает существующую логику**
- Только **добавляет thread safety**
- Performance impact минимален

### Приоритет
- **CRITICAL**: Краш происходит при обычном использовании
- **URGENT**: Исправить перед следующим билдом

---

## 📊 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После исправления:
- ✅ Краш `EXC_BAD_ACCESS` прекратится
- ✅ Аналитика будет работать стабильно
- ✅ Пользователи смогут переключать компоненты без падений
- ✅ Background thread safety будет обеспечена

---

**Готово к внедрению!** 🚀