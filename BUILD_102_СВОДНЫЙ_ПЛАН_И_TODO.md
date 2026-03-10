# 📋 BUILD 102: СВОДНЫЙ ПЛАН ИСПРАВЛЕНИЙ И TODO ЛИСТ

**Дата:** 2026-03-11  
**Build:** 102  
**Статус:** 🔴 **ГОТОВ К РЕАЛИЗАЦИИ**  
**Цель:** Исправить краш с тумблерами БЕЗ костылей, используя правильную архитектуру

---

## 🎯 ЦЕЛЬ ИСПРАВЛЕНИЙ

### Проблема:
- Краш при переключении тумблеров на реальном устройстве
- `Dictionary.resize` рекурсия в background thread
- `parameters ?? [:]` создает Dictionary в background thread
- Отсутствие `@MainActor` на классах аналитики

### Решение:
- Добавить `@MainActor` к классам аналитики
- Убрать костыли с `Task { await MainActor.run }`
- Убрать `parameters ?? [:]` из `trackEvent()`
- Упростить логику NetworkProtectionViewModel

### Результат:
- ✅ Все операции автоматически на main thread
- ✅ Нет костылей с `await MainActor.run`
- ✅ Нет проблем с Dictionary в background thread
- ✅ Нет рекурсии
- ✅ Соответствует best practices Apple

---

## 📋 СВОДНЫЙ ПЛАН ИСПРАВЛЕНИЙ

### 🔴 ПРИОРИТЕТ 1: КРИТИЧЕСКИЙ (5 минут)

#### ЗАДАЧА 1: Исправить `AnalyticsManager.trackEvent()`

**Файл:** `Core/Analytics/AnalyticsManager.swift`  
**Строки:** 47-51  
**Время:** 5 минут  
**Приоритет:** 🔴 Критический

**Что исправить:**
1. ✅ Добавить `@MainActor` к классу `AnalyticsManager`
2. ✅ Убрать `parameters ?? [:]` из `print()` (строка 50)
3. ✅ Убрать `parameters?.description` из `logger.business()` (строка 48)
4. ✅ Использовать условную проверку вместо nil-coalescing operator

**Текущий код:**
```swift
class AnalyticsManager {
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        logger.business("Analytics: Event - \(eventName) with params: \(parameters?.description ?? "none")")
        #if DEBUG
        print("📊 Event: \(eventName), params: \(parameters ?? [:])")  // ❌ Dictionary создается здесь!
        #endif
    }
}
```

**Исправленный код:**
```swift
@MainActor  // ✅ ДОБАВЛЯЕМ
class AnalyticsManager {
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        // ✅ Создаем строку описания БЕЗ создания Dictionary
        let paramsDescription: String
        if let params = parameters {
            paramsDescription = String(describing: params)
        } else {
            paramsDescription = "none"
        }
        
        logger.business("Analytics: Event - \(eventName) with params: \(paramsDescription)")
        #if DEBUG
        if let params = parameters {
            print("📊 Event: \(eventName), params: \(params)")
        } else {
            print("📊 Event: \(eventName), params: none")
        }
        #endif
    }
}
```

**Проверка:**
- ✅ Убрать `parameters ?? [:]` - не создавать Dictionary literal
- ✅ Использовать условную проверку вместо nil-coalescing operator
- ✅ Все операции автоматически на main thread благодаря `@MainActor`

---

### 🟡 ПРИОРИТЕТ 2: ВЫСОКИЙ (15 минут)

#### ЗАДАЧА 2: Исправить `ComponentAnalytics`

**Файл:** `Core/Analytics/ComponentAnalytics.swift`  
**Время:** 10 минут  
**Приоритет:** 🟡 Высокий

**Что исправить:**
1. ✅ Добавить `@MainActor` к классу `ComponentAnalytics`
2. ✅ Убрать `Task { await MainActor.run }` из всех методов:
   - `trackComponentToggle()` (строка 27)
   - `trackComponentSettingsOpened()` (строка 48)
   - `trackComponentSettingsSaved()` (строка 64)
   - `trackSettingToggle()` (строка 81)
   - `trackComponentError()` (строка 103)
   - `trackComponentStatusLoaded()` (строка 123)
   - `trackComponentUsage()` (строка 143)
   - `trackComponentScreenView()` (строка 163)

**Текущий код:**
```swift
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        Task {  // ❌ Костыль!
            await MainActor.run {
                let parameters: [String: Any] = [...]
                analyticsManager.trackEvent(...)
            }
        }
    }
}
```

**Исправленный код:**
```swift
@MainActor  // ✅ ДОБАВЛЯЕМ
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // ✅ УБИРАЕМ Task { await MainActor.run }
        // Автоматически на main thread благодаря @MainActor
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}
```

**Проверка:**
- ✅ Убрать `Task { await MainActor.run }` из всех методов
- ✅ Dictionary создается на main thread автоматически благодаря `@MainActor`
- ✅ Код проще и понятнее

---

#### ЗАДАЧА 3: Исправить `NetworkProtectionViewModel`

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Время:** 10 минут  
**Приоритет:** 🟡 Высокий

**Что исправить:**
1. ✅ Убрать `await MainActor.run` из `handleProductionModeToggle()`:
   - Строка 354: `trackComponentToggle()` - убрать `await MainActor.run`
   - Строка 358: `toastManager.showSuccess()` - убрать `await MainActor.run`
   - Строка 362: `updateClosure(!newValue)` - убрать `await MainActor.run`
   - Строка 364: `trackComponentError()` и `toastManager.showError()` - убрать `await MainActor.run`
2. ✅ Убрать разделение на demo/production mode - единая логика

**Текущий код:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func handleProductionModeToggle(...) async {
        try await statusService.updateStatus(...)
        
        // ❌ ИЗБЫТОЧНО: await MainActor.run в @MainActor классе
        await MainActor.run {
            componentAnalytics.trackComponentToggle(...)
        }
        toastManager.showSuccess(...)  // ❌ БЕЗ await MainActor.run
    }
}
```

**Исправленный код:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func toggleComponent(...) async {
        // Защита от повторного переключения
        // ... защита ...
        
        // Оптимистичное обновление UI
        // ✅ Автоматически на main thread благодаря @MainActor
        updateClosure(newValue)
        
        // Единая логика для всех режимов
        do {
            try await statusService.updateStatus(
                componentId: componentId,
                isEnabled: newValue
            )
            
            // Успешное обновление
            // ✅ Автоматически на main thread благодаря @MainActor
            componentAnalytics.trackComponentToggle(
                componentId: componentId,
                enabled: newValue
            )
            toastManager.showSuccess("Компонент обновлен")
            
        } catch {
            // Откат изменений при ошибке
            // ✅ Автоматически на main thread благодаря @MainActor
            updateClosure(!newValue)
            componentAnalytics.trackComponentError(componentId: componentId, error: error)
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }
}
```

**Проверка:**
- ✅ Убрать `await MainActor.run` - класс уже `@MainActor`
- ✅ Убрать разделение на demo/production mode - единая логика
- ✅ Все операции автоматически на main thread

---

### ✅ ПРИОРИТЕТ 3: ПРОВЕРКА (5 минут)

#### ЗАДАЧА 4: Компиляция и проверка

**Время:** 5 минут  
**Приоритет:** ✅ Проверка

**Что проверить:**
1. ✅ Скомпилировать проект
2. ✅ Проверить отсутствие ошибок компиляции
3. ✅ Проверить соответствие demo mode
4. ✅ Убедиться, что все операции выполняются на main thread
5. ✅ Проверить, что MainScreen не затронут

---

## 📋 TODO ЛИСТ

### ✅ ЗАДАЧА 1: Исправить AnalyticsManager.trackEvent()

**Статус:** 🔴 Ожидает выполнения  
**Приоритет:** Критический  
**Время:** 5 минут  
**Файл:** `Core/Analytics/AnalyticsManager.swift`

**Чек-лист:**
- [ ] Открыть файл `Core/Analytics/AnalyticsManager.swift`
- [ ] Найти класс `AnalyticsManager` (строка 1)
- [ ] Добавить `@MainActor` к классу
- [ ] Найти функцию `trackEvent()` (строка 47)
- [ ] Заменить `parameters?.description ?? "none"` на условную проверку
- [ ] Заменить `parameters ?? [:]` на условную проверку в `print()`
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Ожидаемый результат:**
- ✅ Класс `AnalyticsManager` имеет `@MainActor`
- ✅ Нет `parameters ?? [:]` в коде
- ✅ Нет `parameters?.description` в коде
- ✅ Все операции автоматически на main thread

---

### ✅ ЗАДАЧА 2: Исправить ComponentAnalytics

**Статус:** 🔴 Ожидает выполнения  
**Приоритет:** Высокий  
**Время:** 10 минут  
**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Чек-лист:**
- [ ] Открыть файл `Core/Analytics/ComponentAnalytics.swift`
- [ ] Найти класс `ComponentAnalytics` (строка 9)
- [ ] Добавить `@MainActor` к классу
- [ ] Найти метод `trackComponentToggle()` (строка 27)
- [ ] Убрать `Task { await MainActor.run }` из метода
- [ ] Найти метод `trackComponentSettingsOpened()` (строка 48)
- [ ] Убрать `Task { await MainActor.run }` из метода
- [ ] Найти метод `trackComponentSettingsSaved()` (строка 64)
- [ ] Убрать `Task { await MainActor.run }` из метода
- [ ] Найти метод `trackSettingToggle()` (строка 81)
- [ ] Убрать `Task { await MainActor.run }` из метода
- [ ] Найти метод `trackComponentError()` (строка 103)
- [ ] Убрать `Task { await MainActor.run }` из метода
- [ ] Найти метод `trackComponentStatusLoaded()` (строка 123)
- [ ] Убрать `Task { await MainActor.run }` из метода
- [ ] Найти метод `trackComponentUsage()` (строка 143)
- [ ] Убрать `Task { await MainActor.run }` из метода
- [ ] Найти метод `trackComponentScreenView()` (строка 163)
- [ ] Убрать `Task { await MainActor.run }` из метода
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Ожидаемый результат:**
- ✅ Класс `ComponentAnalytics` имеет `@MainActor`
- ✅ Нет `Task { await MainActor.run }` в методах
- ✅ Dictionary создается на main thread автоматически
- ✅ Код проще и понятнее

---

### ✅ ЗАДАЧА 3: Исправить NetworkProtectionViewModel

**Статус:** 🔴 Ожидает выполнения  
**Приоритет:** Высокий  
**Время:** 10 минут  
**Файл:** `ViewModels/NetworkProtectionViewModel.swift`

**Чек-лист:**
- [ ] Открыть файл `ViewModels/NetworkProtectionViewModel.swift`
- [ ] Найти функцию `handleProductionModeToggle()` (строка 342)
- [ ] Найти строку 354: `trackComponentToggle()` - убрать `await MainActor.run`
- [ ] Найти строку 358: `toastManager.showSuccess()` - убрать `await MainActor.run`
- [ ] Найти строку 362: `updateClosure(!newValue)` - убрать `await MainActor.run`
- [ ] Найти строку 364: `trackComponentError()` и `toastManager.showError()` - убрать `await MainActor.run`
- [ ] Убрать разделение на demo/production mode - объединить логику
- [ ] Удалить функцию `handleDemoModeToggle()` (если есть)
- [ ] Удалить функцию `handleProductionModeToggle()` (если есть)
- [ ] Создать единую функцию `toggleComponent()` для всех режимов
- [ ] Сохранить файл
- [ ] Проверить компиляцию

**Ожидаемый результат:**
- ✅ Нет `await MainActor.run` в `@MainActor` классе
- ✅ Единая логика для всех режимов
- ✅ Все операции автоматически на main thread
- [ ] Код проще и понятнее

---

### ✅ ЗАДАЧА 4: Компиляция и проверка

**Статус:** 🔴 Ожидает выполнения  
**Приоритет:** Проверка  
**Время:** 5 минут

**Чек-лист:**
- [ ] Скомпилировать проект (`xcodebuild build`)
- [ ] Проверить отсутствие ошибок компиляции
- [ ] Проверить отсутствие предупреждений компиляции
- [ ] Проверить, что MainScreen не затронут
- [ ] Проверить, что DateFormatterService не затронут
- [ ] Проверить, что глобальные флаги не затронуты
- [ ] Проверить соответствие demo mode
- [ ] Убедиться, что все операции выполняются на main thread

**Ожидаемый результат:**
- ✅ Проект компилируется без ошибок
- ✅ Нет предупреждений компиляции
- ✅ MainScreen работает правильно
- ✅ Все исправления применены

---

## 🎯 ИТОГОВАЯ СТАТИСТИКА

| Задача | Файл | Время | Приоритет | Статус |
|--------|------|-------|-----------|--------|
| 1. Исправить AnalyticsManager | AnalyticsManager.swift | 5 мин | Критический | 🔴 Ожидает |
| 2. Исправить ComponentAnalytics | ComponentAnalytics.swift | 10 мин | Высокий | 🔴 Ожидает |
| 3. Исправить NetworkProtectionViewModel | NetworkProtectionViewModel.swift | 10 мин | Высокий | 🔴 Ожидает |
| 4. Компиляция и проверка | - | 5 мин | Проверка | 🔴 Ожидает |
| **ИТОГО** | **3 файла** | **30 минут** | - | **0/4 выполнено** |

---

## ✅ ЧТО НЕ ТРОГАТЬ (КРИТИЧНО!)

### MainScreen остается без изменений

**Файл:** `Screens/01_MainScreen.swift`

**Почему:**
- MainScreen работает правильно
- Исправления BUILD 100 остаются без изменений
- Краш НЕ вернется

**Что НЕ менять:**
- ❌ НЕ менять `DateFormatterService` - работает правильно
- ❌ НЕ менять глобальные флаги с NSLock - работают правильно
- ❌ НЕ менять статический Calendar - это ключевое исправление BUILD 100
- ❌ НЕ менять `await MainActor.run` в async функции - это правильно!

---

## 📊 ПРОВЕРОЧНЫЙ ЧЕК-ЛИСТ

### После выполнения всех задач:

- [ ] `AnalyticsManager` имеет `@MainActor`
- [ ] `ComponentAnalytics` имеет `@MainActor`
- [ ] Нет `Task { await MainActor.run }` в методах аналитики
- [ ] Нет `await MainActor.run` в `NetworkProtectionViewModel` (кроме async функций)
- [ ] Нет `parameters ?? [:]` в `trackEvent()`
- [ ] Нет разделения на demo/production mode
- [ ] Проект компилируется без ошибок
- [ ] MainScreen не затронут
- [ ] DateFormatterService не затронут
- [ ] Глобальные флаги не затронуты

---

## 🎯 РЕЗУЛЬТАТ

### После выполнения всех задач:

- ✅ Все операции автоматически на main thread
- ✅ Нет костылей с `await MainActor.run`
- ✅ Нет проблем с Dictionary в background thread
- ✅ Нет рекурсии
- ✅ Соответствует best practices Apple
- ✅ Краш на MainScreen НЕ вернется
- ✅ Краш с тумблерами исправлен

---

**Статус:** 🔴 **ГОТОВ К РЕАЛИЗАЦИИ**  
**Рекомендация:** Выполнить все задачи по порядку, проверить компиляцию после каждой задачи
