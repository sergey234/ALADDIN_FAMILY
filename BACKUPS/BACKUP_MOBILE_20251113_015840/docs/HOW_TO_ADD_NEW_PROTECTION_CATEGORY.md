# 📝 ИНСТРУКЦИЯ: Как добавить новую категорию защиты

**Дата:** 2025-11-12  
**Версия:** 1.0  
**Статус:** ✅ Система спроектирована для легкого расширения

---

## ✅ ПОДТВЕРЖДЕНИЕ

**Вопрос:** Можно ли легко добавлять новые виды защиты от угроз?  
**Ответ:** ✅ ДА! Система использует гибкую архитектуру (Dictionary + Configuration)

---

## 🎯 КАК ДОБАВИТЬ НОВУЮ КАТЕГОРИЮ (3-4 ШАГА)

### Пример: Добавить "Квантовые угрозы"

---

### Шаг 1: Добавить case в enum

**Файл:** `Shared/Models/ThreatProtectionCategory.swift`

```swift
enum ThreatProtectionCategory: String, CaseIterable, Identifiable {
    // ... существующие ...
    case quantumThreats  // ← Просто добавляем новый case!
}
```

**Что нужно добавить:**
- `emoji` в switch
- `count` в switch
- `localizedTitle()` в switch
- `localizedThreats()` в switch

---

### Шаг 2: Добавить конфигурацию

**Файл:** `Shared/Models/ThreatProtectionCategory.swift` (в extension)

```swift
extension ThreatProtectionCategory {
    static var configurations: [ThreatProtectionCategory: CategoryConfiguration] {
        [
            // ... существующие ...
            .quantumThreats: CategoryConfiguration(
                requiredTariff: .premium,
                benefit: "Защита от квантовых атак",
                settingsScreen: .advancedProtection,
                group: .premium
            )
        ]
    }
}
```

**Всё!** Теперь автоматически работают:
- ✅ `requiredTariff`
- ✅ `benefit`
- ✅ `settingsScreen`
- ✅ `group`

---

### Шаг 3: Добавить локализацию

**Файл:** `Core/Localization/LocalizationManager.swift`

```swift
.russian: [
    // ... существующие ...
    "tariffs_threat_category_quantum": "Квантовые угрозы",
    "protection_benefit_quantum": "Защита от квантовых атак",
    "tariffs_threat_quantum_1": "Квантовый взлом",
    "tariffs_threat_quantum_2": "Квантовое шифрование",
    // ... остальные угрозы
]

.english: [
    // ... existing ...
    "tariffs_threat_category_quantum": "Quantum Threats",
    "protection_benefit_quantum": "Protection from quantum attacks",
    // ... остальные переводы
]
```

---

### Шаг 4: Добавить в группу (если нужно новую группу)

**Если нужна новая группа:**

**Файл:** `Shared/Models/ProtectionGroup.swift`

```swift
enum ProtectionGroup: String, CaseIterable {
    // ... существующие ...
    case quantum = "КВАНТУМ"  // ← Новая группа
    
    var icon: String {
        switch self {
        // ... существующие ...
        case .quantum: return "⚛️"
        }
    }
}
```

**Если добавляем в существующую группу:**
- ✅ Ничего делать не нужно! Автоматически появится через `category.group`

---

## ✅ РЕЗУЛЬТАТ

После этих 3-4 шагов новая категория автоматически появится:

1. ✅ В каталоге угроз (`ThreatProtectionScreen`)
2. ✅ В настройках защиты (`ThreatProtectionSettingsScreen`)
3. ✅ В галерее сценариев (если добавить сценарий)
4. ✅ В автоматической активации по тарифам
5. ✅ В проверке доступности
6. ✅ В мотивационных баннерах

---

## 🎯 ПРЕИМУЩЕСТВА ГИБКОЙ АРХИТЕКТУРЫ

### ❌ Старый подход (switch statements):
```swift
// При добавлении новой категории нужно обновить:
var requiredTariff: TariffType {
    switch self {
    case .cyberThreats: return .free
    // ... 9 cases
    case .quantumThreats: return .premium  // ← Нужно добавить
    }
}

var benefit: String {
    switch self {
    case .cyberThreats: return "..."
    // ... 9 cases
    case .quantumThreats: return "..."  // ← Нужно добавить
    }
}
// ... и так в 5+ местах!
```

**Проблемы:**
- Нужно обновить 5+ switch statements
- Легко забыть обновить какое-то место
- Сложно поддерживать

---

### ✅ Новый подход (Dictionary + Configuration):
```swift
// При добавлении новой категории:
static var configurations: [ThreatProtectionCategory: CategoryConfiguration] {
    [
        // ... существующие ...
        .quantumThreats: CategoryConfiguration(...)  // ← Всё в одном месте!
    ]
}
```

**Преимущества:**
- ✅ Всё в одном месте (конфигурация)
- ✅ Автоматически работает везде
- ✅ Легко поддерживать
- ✅ Невозможно забыть обновить

---

## 📋 ЧЕКЛИСТ ДОБАВЛЕНИЯ НОВОЙ КАТЕГОРИИ

- [ ] Добавить case в `ThreatProtectionCategory` enum
- [ ] Добавить `emoji` в switch
- [ ] Добавить `count` в switch
- [ ] Добавить `localizedTitle()` в switch
- [ ] Добавить `localizedThreats()` в switch
- [ ] Добавить конфигурацию в `configurations` Dictionary
- [ ] Добавить локализацию (RU + EN)
- [ ] Добавить угрозы в локализацию (если нужно)
- [ ] Протестировать отображение
- [ ] Протестировать автоматическую активацию

---

## 🎯 ПРИМЕР: Добавить "AI Threats"

### Шаг 1: Enum
```swift
enum ThreatProtectionCategory {
    // ...
    case aiThreats
}
```

### Шаг 2: Свойства
```swift
var emoji: String {
    switch self {
    // ...
    case .aiThreats: return "🤖"
    }
}

var count: Int {
    switch self {
    // ...
    case .aiThreats: return 8
    }
}
```

### Шаг 3: Конфигурация
```swift
static var configurations: [ThreatProtectionCategory: CategoryConfiguration] {
    [
        // ...
        .aiThreats: CategoryConfiguration(
            requiredTariff: .premium,
            benefit: "Защита от AI-атак и манипуляций",
            settingsScreen: .advancedProtection,
            group: .premium
        )
    ]
}
```

### Шаг 4: Локализация
```swift
"tariffs_threat_category_ai": "AI угрозы",
"protection_benefit_ai": "Защита от AI-атак и манипуляций",
```

**Всё!** Категория автоматически появится везде.

---

## ✅ ПОДТВЕРЖДЕНИЕ

**Вопрос:** Можно ли легко добавлять новые виды защиты?  
**Ответ:** ✅ ДА! Всего 3-4 простых шага

**Что предусмотрено:**
1. ✅ Гибкая архитектура (Dictionary + Configuration)
2. ✅ Автоматическая интеграция
3. ✅ Легкое расширение
4. ✅ Обратная совместимость

---

**Дата создания:** 2025-11-12  
**Статус:** ✅ Система готова к расширению

