# 🎯 BUILD 107: ПЛАН ДЕЙСТВИЙ И TODO СПИСОК

**Дата:** 2026-03-11  
**Build:** 107  
**Статус:** 🔴 **КРИТИЧЕСКИЙ КРАШ - ТРЕБУЕТСЯ НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ**

---

## 🔍 АНАЛИЗ: МЫ ХОДИМ ПО КРУГУ?

### ✅ **ЧТО ГОВОРИТ ИСТОРИЯ:**

#### **BUILD 102 (документация говорит):**
- ✅ "Добавлен `@MainActor` к классам `AnalyticsManager` и `ComponentAnalytics`"

#### **РЕАЛЬНЫЙ КОД (BUILD 107):**
- ❌ `ComponentAnalytics` - **НЕТ `@MainActor`!**
- ❌ `AnalyticsManager` - **НЕТ `@MainActor`!**

### 🔴 **ВЫВОД:**

**ДА, МЫ ХОДИМ ПО КРУГУ!**

**Причины:**
1. Исправления были запланированы в документах, но **НЕ ПРИМЕНЕНЫ** в коде
2. Или были применены, но потом **ОТКАТИЛИСЬ**
3. Или применялись частично, но не полностью

**Доказательства:**
- Документы BUILD 102-106 говорят про `@MainActor`
- Реальный код BUILD 107 показывает отсутствие `@MainActor`
- Краш продолжается с той же ошибкой

---

## 🎯 СТРАТЕГИЯ: КАК ПОНЯТЬ ПРОБЛЕМУ НА РЕАЛЬНОМ УСТРОЙСТВЕ?

### 🔍 **ПРОБЛЕМА: В СИМУЛЯТОРЕ ВСЕ РАБОТАЕТ!**

**Почему симулятор не показывает проблему:**
1. **Больший размер стека** - симулятор более терпим к рекурсии
2. **Медленнее выполнение** - Dictionary создается медленнее, успевает переключиться на main thread
3. **Другая архитектура** - симулятор использует x86_64, реальное устройство - ARM64
4. **Другая версия iOS** - симулятор может использовать другую версию runtime

**Почему реальное устройство крашится:**
1. **Меньший размер стека** - быстрее переполняется при рекурсии
2. **Быстрее выполнение** - Dictionary создается быстрее, не успевает переключиться на main thread
3. **Строже проверки** - реальное устройство строже проверяет thread safety
4. **Другая архитектура** - ARM64 имеет другие особенности работы с памятью

---

## 📋 ПЛАН ДЕЙСТВИЙ: ДИАГНОСТИКА + ИСПРАВЛЕНИЕ

### 🎯 **ЭТАП 1: ДИАГНОСТИКА (ПОНИМАНИЕ ПРОБЛЕМЫ)**

#### **Задача 1.1: Добавить логирование для понимания thread context**

**Цель:** Понять, на каком thread создается Dictionary

**Что логировать:**
1. Thread ID и имя при создании Dictionary
2. Call stack при создании Dictionary
3. Время создания Dictionary
4. Контекст вызова (какой метод вызвал)

**Где логировать:**
- `ComponentAnalytics.trackComponentToggle()` - начало метода
- `ComponentAnalytics.trackSettingToggle()` - начало метода
- `AnalyticsManager.trackEvent()` - начало метода
- Внутри Dictionary literal creation

**Код логирования:**
```swift
func trackComponentToggle(componentId: String, enabled: Bool) {
    // ✅ ДИАГНОСТИКА: Логирование thread context
    let threadInfo = """
    🔍 [ComponentAnalytics.trackComponentToggle] Thread Info:
    - Thread.isMainThread: \(Thread.isMainThread)
    - Thread.current.name: \(Thread.current.name ?? "unknown")
    - Thread.current.threadID: \(Thread.current.hashValue)
    - Call stack: \(Thread.callStackSymbols.prefix(5).joined(separator: "\n"))
    """
    print(threadInfo)
    
    // Создание Dictionary
    let parameters: [String: Any] = [
        "component_id": componentId,
        "enabled": enabled,
        "timestamp": Date().timeIntervalSince1970
    ]
    
    // ✅ ДИАГНОСТИКА: Логирование после создания Dictionary
    print("✅ [ComponentAnalytics] Dictionary создан на thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    analyticsManager.trackEvent("component_toggle", parameters: parameters)
}
```

---

#### **Задача 1.2: Добавить логирование в SmartToggleRow.onChange**

**Цель:** Понять, на каком thread вызывается `.onChange`

**Код логирования:**
```swift
.onChange(of: isOn) { newValue in
    // ✅ ДИАГНОСТИКА: Логирование thread context в onChange
    let threadInfo = """
    🔍 [SmartToggleRow.onChange] Thread Info:
    - Thread.isMainThread: \(Thread.isMainThread)
    - Thread.current.name: \(Thread.current.name ?? "unknown")
    - ComponentId: \(componentId)
    - SettingKey: \(settingKey)
    - NewValue: \(newValue)
    """
    print(threadInfo)
    
    // Логируем событие переключения
    componentAnalytics.trackSettingToggle(...)
}
```

---

#### **Задача 1.3: Добавить логирование в NetworkProtectionViewModel**

**Цель:** Понять, на каком thread вызывается `toggleComponent`

**Код логирования:**
```swift
private func toggleComponent(...) async {
    // ✅ ДИАГНОСТИКА: Логирование thread context
    print("🔍 [NetworkProtectionViewModel.toggleComponent] Thread до await: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    try await statusService.updateStatus(...)
    
    print("🔍 [NetworkProtectionViewModel.toggleComponent] Thread после await: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    await MainActor.run {
        print("🔍 [NetworkProtectionViewModel.toggleComponent] Thread внутри await MainActor.run: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
        componentAnalytics.trackComponentToggle(...)
    }
}
```

---

### 🎯 **ЭТАП 2: ИСПРАВЛЕНИЕ (ПРИМЕНЕНИЕ РЕШЕНИЯ)**

#### **Задача 2.1: Добавить `@MainActor` к `ComponentAnalytics`**

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Изменения:**
```swift
// ❌ БЫЛО:
class ComponentAnalytics {
    // ...
}

// ✅ СТАЛО:
@MainActor
class ComponentAnalytics {
    // ...
}
```

**Почему это важно:**
- Гарантирует выполнение всех методов на main thread
- Dictionary создается на main thread автоматически
- Решает проблему раз и навсегда

---

#### **Задача 2.2: Добавить `@MainActor` к `AnalyticsManager`**

**Файл:** `Core/Analytics/AnalyticsManager.swift`

**Изменения:**
```swift
// ❌ БЫЛО:
class AnalyticsManager {
    // ...
}

// ✅ СТАЛО:
@MainActor
class AnalyticsManager {
    // ...
}
```

**Почему это важно:**
- Гарантирует thread safety для всех операций
- Предотвращает создание Dictionary в background thread

---

#### **Задача 2.3: Исправить `SmartToggleRow.onChange`**

**Файл:** `Shared/Components/SmartToggleRow.swift`

**Изменения:**
```swift
// ❌ БЫЛО:
.onChange(of: isOn) { newValue in
    componentAnalytics.trackSettingToggle(
        componentId: componentId,
        settingKey: settingKey,
        enabled: newValue
    )
}

// ✅ СТАЛО:
.onChange(of: isOn) { newValue in
    // ✅ ИСПРАВЛЕНИЕ: Гарантируем выполнение на main thread
    DispatchQueue.main.async {
        componentAnalytics.trackSettingToggle(
            componentId: componentId,
            settingKey: settingKey,
            enabled: newValue
        )
    }
}
```

**Почему это важно:**
- `.onChange` может вызываться на background thread
- `DispatchQueue.main.async` гарантирует выполнение на main thread
- Даже если `ComponentAnalytics` имеет `@MainActor`, лучше быть явным

---

#### **Задача 2.4: Убрать лишний `await MainActor.run` из `toggleComponent`**

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`

**Изменения:**
```swift
// ❌ БЫЛО:
await MainActor.run {
    componentAnalytics.trackComponentToggle(
        componentId: componentId,
        enabled: newValue
    )
    
    if AppConfig.authToken == nil {
        toastManager.showSuccess("Компонент обновлен (демо режим)")
    } else {
        toastManager.showSuccess("Компонент обновлен")
    }
}

// ✅ СТАЛО:
// Убрать await MainActor.run - ComponentAnalytics теперь @MainActor
componentAnalytics.trackComponentToggle(
    componentId: componentId,
    enabled: newValue
)

if AppConfig.authToken == nil {
    toastManager.showSuccess("Компонент обновлен (демо режим)")
} else {
    toastManager.showSuccess("Компонент обновлен")
}
```

**Почему это важно:**
- `ComponentAnalytics` теперь `@MainActor`, поэтому `await MainActor.run` избыточен
- Упрощает код
- Предотвращает потенциальные проблемы с async контекстом

---

### 🎯 **ЭТАП 3: ТЕСТИРОВАНИЕ (ПРОВЕРКА ИСПРАВЛЕНИЙ)**

#### **Задача 3.1: Тестирование на симуляторе**

**Действия:**
1. Запустить приложение на симуляторе
2. Открыть NetworkProtectionScreen
3. Переключить все тумблеры (10 штук)
4. Проверить логи - все должно быть на MAIN thread
5. Убедиться, что нет крашей

---

#### **Задача 3.2: Тестирование на реальном устройстве**

**Действия:**
1. Собрать приложение для реального устройства
2. Установить через TestFlight или прямое подключение
3. Открыть NetworkProtectionScreen
4. Переключить все тумблеры (10 штук)
5. Проверить логи - все должно быть на MAIN thread
6. Убедиться, что нет крашей
7. Мониторить краши в течение 24-48 часов

---

#### **Задача 3.3: Анализ логов**

**Что проверять:**
1. Все вызовы `trackComponentToggle` должны быть на MAIN thread
2. Все вызовы `trackSettingToggle` должны быть на MAIN thread
3. Все создания Dictionary должны быть на MAIN thread
4. Не должно быть вызовов на BACKGROUND thread

**Критерии успеха:**
- ✅ 100% вызовов на MAIN thread
- ✅ 0 крашей при переключении тумблеров
- ✅ 0 крашей в течение 48 часов

---

## 📋 TODO СПИСОК ЗАДАЧ

### 🔴 **КРИТИЧНЫЕ ЗАДАЧИ (СДЕЛАТЬ СЕЙЧАС):**

- [ ] **TODO 1:** Добавить логирование в `ComponentAnalytics.trackComponentToggle()` для диагностики thread context
- [ ] **TODO 2:** Добавить логирование в `ComponentAnalytics.trackSettingToggle()` для диагностики thread context
- [ ] **TODO 3:** Добавить логирование в `AnalyticsManager.trackEvent()` для диагностики thread context
- [ ] **TODO 4:** Добавить логирование в `SmartToggleRow.onChange` для диагностики thread context
- [ ] **TODO 5:** Добавить логирование в `NetworkProtectionViewModel.toggleComponent()` для диагностики thread context
- [ ] **TODO 6:** Добавить `@MainActor` к `ComponentAnalytics` классу
- [ ] **TODO 7:** Добавить `@MainActor` к `AnalyticsManager` классу
- [ ] **TODO 8:** Исправить `SmartToggleRow.onChange` - обернуть в `DispatchQueue.main.async`
- [ ] **TODO 9:** Убрать лишний `await MainActor.run` из `NetworkProtectionViewModel.toggleComponent()`
- [ ] **TODO 10:** Протестировать на симуляторе - проверить логи
- [ ] **TODO 11:** Собрать для реального устройства - проверить логи
- [ ] **TODO 12:** Протестировать на реальном устройстве - переключить все тумблеры
- [ ] **TODO 13:** Мониторить краши в течение 48 часов

---

### 🟡 **ВАЖНЫЕ ЗАДАЧИ (СДЕЛАТЬ ПОСЛЕ КРИТИЧНЫХ):**

- [ ] **TODO 14:** Проверить все другие места, где вызывается `ComponentAnalytics`
- [ ] **TODO 15:** Проверить все другие места, где вызывается `AnalyticsManager`
- [ ] **TODO 16:** Добавить unit-тесты для проверки thread safety
- [ ] **TODO 17:** Добавить интеграционные тесты для проверки отсутствия крашей
- [ ] **TODO 18:** Обновить документацию с правильными примерами использования

---

### 🟢 **УЛУЧШЕНИЯ (СДЕЛАТЬ ПОСЛЕ ВАЖНЫХ):**

- [ ] **TODO 19:** Оптимизировать логирование (убрать избыточные логи после исправления)
- [ ] **TODO 20:** Добавить метрики для отслеживания thread safety
- [ ] **TODO 21:** Создать чек-лист для предотвращения подобных проблем в будущем

---

## 🎯 ИДЕАЛЬНАЯ СТРУКТУРА ДЛЯ РЕАЛЬНОГО УСТРОЙСТВА

### ✅ **ПРИНЦИПЫ:**

#### **1. Все классы аналитики должны быть `@MainActor`**

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class ComponentAnalytics {
    // Все методы автоматически на main thread
}

@MainActor
class AnalyticsManager {
    // Все методы автоматически на main thread
}
```

**Почему:**
- Гарантирует thread safety
- Предотвращает создание Dictionary в background thread
- Соответствует best practices Swift Concurrency

---

#### **2. Все вызовы аналитики должны быть явными**

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
DispatchQueue.main.async {
    componentAnalytics.trackComponentToggle(...)
}

// ❌ НЕПРАВИЛЬНО:
componentAnalytics.trackComponentToggle(...)  // Может быть на background thread
```

**Почему:**
- Явность лучше неявности
- Гарантирует выполнение на main thread
- Легче отлаживать

---

#### **3. Все async функции в ViewModel должны быть `@MainActor`**

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    func toggleComponent(...) async {
        // Автоматически на main thread
        componentAnalytics.trackComponentToggle(...)  // Без await MainActor.run!
    }
}
```

**Почему:**
- `@MainActor` на классе гарантирует выполнение всех методов на main thread
- Не нужно вручную использовать `await MainActor.run`
- Код становится проще

---

#### **4. Все `.onChange` должны использовать `DispatchQueue.main.async`**

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
.onChange(of: isOn) { newValue in
    DispatchQueue.main.async {
        componentAnalytics.trackSettingToggle(...)
    }
}

// ❌ НЕПРАВИЛЬНО:
.onChange(of: isOn) { newValue in
    componentAnalytics.trackSettingToggle(...)  // Может быть на background thread
}
```

**Почему:**
- `.onChange` может вызываться на background thread
- `DispatchQueue.main.async` гарантирует выполнение на main thread
- Даже если класс `@MainActor`, лучше быть явным

---

## 📊 ГДЕ ПОСТАВИТЬ ЛОГИ

### 🔍 **КРИТИЧЕСКИЕ МЕСТА ДЛЯ ЛОГИРОВАНИЯ:**

#### **1. ComponentAnalytics.trackComponentToggle()**

**Место:** Начало метода, после создания Dictionary

**Код:**
```swift
func trackComponentToggle(componentId: String, enabled: Bool) {
    // ✅ ЛОГ 1: Thread context при входе в метод
    print("🔍 [ComponentAnalytics.trackComponentToggle] ENTRY - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    let parameters: [String: Any] = [
        "component_id": componentId,
        "enabled": enabled,
        "timestamp": Date().timeIntervalSince1970
    ]
    
    // ✅ ЛОГ 2: Thread context после создания Dictionary
    print("✅ [ComponentAnalytics.trackComponentToggle] Dictionary создан - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    analyticsManager.trackEvent("component_toggle", parameters: parameters)
    
    // ✅ ЛОГ 3: Thread context при выходе из метода
    print("✅ [ComponentAnalytics.trackComponentToggle] EXIT - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
}
```

---

#### **2. ComponentAnalytics.trackSettingToggle()**

**Место:** Начало метода, после создания Dictionary

**Код:**
```swift
func trackSettingToggle(componentId: String, settingKey: String, enabled: Bool) {
    // ✅ ЛОГ 1: Thread context при входе в метод
    print("🔍 [ComponentAnalytics.trackSettingToggle] ENTRY - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    let parameters: [String: Any] = [
        "component_id": componentId,
        "setting_key": settingKey,
        "enabled": enabled,
        "timestamp": Date().timeIntervalSince1970
    ]
    
    // ✅ ЛОГ 2: Thread context после создания Dictionary
    print("✅ [ComponentAnalytics.trackSettingToggle] Dictionary создан - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    analyticsManager.trackEvent("component_setting_toggle", parameters: parameters)
}
```

---

#### **3. SmartToggleRow.onChange**

**Место:** В начале замыкания `.onChange`

**Код:**
```swift
.onChange(of: isOn) { newValue in
    // ✅ ЛОГ: Thread context в onChange
    print("🔍 [SmartToggleRow.onChange] ENTRY - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND"), Component: \(componentId), Setting: \(settingKey)")
    
    DispatchQueue.main.async {
        print("✅ [SmartToggleRow.onChange] Внутри DispatchQueue.main.async - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
        componentAnalytics.trackSettingToggle(...)
    }
}
```

---

#### **4. NetworkProtectionViewModel.toggleComponent()**

**Место:** До и после `await`, внутри `await MainActor.run`

**Код:**
```swift
private func toggleComponent(...) async {
    // ✅ ЛОГ 1: Thread context до await
    print("🔍 [NetworkProtectionViewModel.toggleComponent] ДО await - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    try await statusService.updateStatus(...)
    
    // ✅ ЛОГ 2: Thread context после await
    print("🔍 [NetworkProtectionViewModel.toggleComponent] ПОСЛЕ await - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
    
    await MainActor.run {
        // ✅ ЛОГ 3: Thread context внутри await MainActor.run
        print("✅ [NetworkProtectionViewModel.toggleComponent] Внутри await MainActor.run - Thread: \(Thread.isMainThread ? "MAIN" : "BACKGROUND")")
        componentAnalytics.trackComponentToggle(...)
    }
}
```

---

## 🎯 КРИТЕРИИ УСПЕХА

### ✅ **ПОСЛЕ ИСПРАВЛЕНИЙ ДОЛЖНО БЫТЬ:**

1. ✅ **100% вызовов аналитики на MAIN thread**
   - Все логи показывают `Thread.isMainThread = true`
   - Нет вызовов на BACKGROUND thread

2. ✅ **0 крашей при переключении тумблеров**
   - Все тумблеры работают без крашей
   - Нет рекурсии `Dictionary.resize`

3. ✅ **0 крашей в течение 48 часов**
   - Мониторинг крашей показывает 0 инцидентов
   - Приложение работает стабильно

4. ✅ **Логи показывают правильный thread context**
   - Все создания Dictionary на MAIN thread
   - Все вызовы аналитики на MAIN thread

---

## 📝 ВЫВОДЫ

### 🔴 **МЫ ХОДИМ ПО КРУГУ:**

**ДА!** Документы говорят про `@MainActor`, но реальный код его НЕ имеет.

**Причины:**
1. Исправления были запланированы, но не применены
2. Или были применены, но откатились
3. Или применялись частично

**Решение:**
1. Применить исправления СЕЙЧАС
2. Добавить логирование для диагностики
3. Протестировать на реальном устройстве
4. Мониторить краши в течение 48 часов

---

### ✅ **ПРАВИЛЬНАЯ СТРАТЕГИЯ:**

1. **Диагностика:** Добавить логирование для понимания thread context
2. **Исправление:** Применить все исправления одновременно
3. **Тестирование:** Протестировать на реальном устройстве
4. **Мониторинг:** Отслеживать краши в течение 48 часов

---

**ГОТОВ К ВЫПОЛНЕНИЮ!** 🚀
