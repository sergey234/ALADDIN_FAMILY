# 🔇 ДОКУМЕНТАЦИЯ: ТИХИЙ РЕЖИМ И РЕЖИМЫ УВЕДОМЛЕНИЙ

**Статус:** ✅ **ПОЛНОСТЬЮ РЕАЛИЗОВАНО**  
**Дата проверки:** 2025-11-01

---

## 📍 ГДЕ НАХОДИТСЯ ТИХИЙ РЕЖИМ

### 🎛️ Экран настроек уведомлений:
**Файл:** `Screens/NotificationSettingsScreen.swift`  
**Навигация:** Настройки → Уведомления  
**Путь:** `SettingsScreen` → `NotificationSettingsScreen`

---

## 🔇 ВИДЫ ТИХОГО РЕЖИМА

### 1. **ТИХИЙ РЕЖИМ** (Quiet Mode) 🔇

**Описание:** Уведомления без звука и баннера, только badge

**Расположение:**
- Раздел "ЗВУК И BADGE"
- Toggle: "Тихий режим"
- Иконка: 🔇
- Переменная: `settings.quietModeEnabled`

**Как работает:**
```swift
// Если тихий режим включен - только badge, без звука и баннера
if isQuietHours {
    completionHandler([.badge])  // Только красный значок на иконке
} else {
    // Обычный режим с баннером и звуком
    let options: [.banner, .sound, .badge]
    completionHandler(options)
}
```

**Статус:** ✅ Реализовано

---

### 2. **ТИХИЕ ЧАСЫ** (Quiet Hours) 🌙

**Описание:** Автоматическое отключение звука и баннера в указанное время

**Расположение:**
- Раздел "ТИХИЕ ЧАСЫ"
- Toggle: "Включить тихие часы"
- Иконка: 🌙
- Настройки времени: "Начало" и "Конец"

**Параметры:**
- `quietHoursEnabled: Bool` - включение/выключение
- `quietHoursStart: String = "22:00"` - начало тихих часов
- `quietHoursEnd: String = "08:00"` - конец тихих часов

**Как работает:**
```swift
// Проверяем тихий режим
let isQuietMode = notificationSettings.quietModeEnabled
let currentHour = Calendar.current.component(.hour, from: now)
let quietStart = Int(notificationSettings.quietHoursStart.split(separator: ":").first ?? "22") ?? 22
let quietEnd = Int(notificationSettings.quietHoursEnd.split(separator: ":").first ?? "8") ?? 8
let isQuietHours = isQuietMode && (currentHour >= quietStart || currentHour < quietEnd)

// Если сейчас тихие часы - только badge
if isQuietHours {
    completionHandler([.badge])
}
```

**Статус:** ✅ Реализовано

---

### 3. **НЕ БЕСПОКОИТЬ** (Do Not Disturb) 🔕

**Описание:** Полностью отключает уведомления на указанное время

**Расположение:**
- Раздел "ДОПОЛНИТЕЛЬНЫЕ РЕЖИМЫ"
- Toggle: "Не беспокоить"
- Иконка: 🔕
- DatePicker: выбор времени окончания режима

**Параметры:**
- `doNotDisturbMode: Bool` - включение/выключение
- `doNotDisturbUntil: Date?` - время окончания режима

**Как работает:**
```swift
// Проверяем режим "Не беспокоить"
if notificationSettings.doNotDisturbMode {
    if let until = notificationSettings.doNotDisturbUntil, now < until {
        // Режим активен - не показываем ничего
        completionHandler([])  // Полностью отключено
        return
    } else {
        // Время истекло - отключаем режим автоматически
        notificationSettings.doNotDisturbMode = false
        notificationSettings.doNotDisturbUntil = nil
        saveSettings()
    }
}
```

**Статус:** ✅ Реализовано с автоматическим отключением

---

### 4. **ТОЛЬКО ВАЖНЫЕ** (Important Only) 🎯

**Описание:** Показывать только угрозы безопасности, остальные в тихий режим

**Расположение:**
- Раздел "ДОПОЛНИТЕЛЬНЫЕ РЕЖИМЫ"
- Toggle: "Только важные"
- Иконка: 🎯
- Переменная: `settings.importantOnlyMode`

**Как работает:**
```swift
// Проверяем режим "Только важные"
if notificationSettings.importantOnlyMode {
    let isImportant = notificationType == "threat" || notificationType == "warning"
    if !isImportant {
        // Не важное уведомление - тихий режим (только badge)
        completionHandler([.badge])
        onNotificationReceived?(notification)  // Все равно сохраняем в список
        return
    }
}
```

**Важные уведомления:**
- `threat` - угрозы безопасности
- `warning` - предупреждения

**Статус:** ✅ Реализовано

---

### 5. **ТОЛЬКО ВЫСОКИЙ ПРИОРИТЕТ** (High Priority Only) ⭐

**Описание:** Показывать только уведомления высокого приоритета

**Расположение:**
- Раздел "ДОПОЛНИТЕЛЬНЫЕ РЕЖИМЫ"
- Toggle: "Только высокий приоритет"
- Иконка: ⭐
- Переменная: `settings.highPriorityOnly`

**Как работает:**
```swift
// Проверяем приоритет
if notificationSettings.highPriorityOnly {
    let priorityString = userInfo["priority"] as? String
    let priority = priorityString != nil ? NotificationPriority(from: priorityString!) : NotificationPriority.high
    if priority != .high {
        // Не высокий приоритет - тихий режим
        completionHandler([.badge])
        onNotificationReceived?(notification)
        return
    }
}
```

**Статус:** ✅ Реализовано

---

### 6. **ОГРАНИЧЕНИЕ ЧАСТОТЫ** (Frequency Limiting) 📊

**Описание:** Ограничение количества уведомлений в час

**Расположение:**
- Раздел "ДОПОЛНИТЕЛЬНЫЕ РЕЖИМЫ"
- Toggle: "Ограничение частоты"
- Stepper: выбор максимального количества (1-60 в час)

**Параметры:**
- `maxNotificationsPerHour: Int?` - максимум уведомлений в час (nil = без ограничений)

**Как работает:**
```swift
// Проверяем частоту уведомлений
if let maxPerHour = notificationSettings.maxNotificationsPerHour {
    let notificationsInLastHour = countNotificationsInLastHour()
    if notificationsInLastHour >= maxPerHour {
        // Превышен лимит - не показываем
        completionHandler([])  // Полностью скрыто
        return
    }
}
```

**Статус:** ✅ Реализовано с трекингом частоты

---

## 🎛️ ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ

### 🔊 Звук

**Расположение:** Раздел "ЗВУК И BADGE"  
**Переменная:** `settings.soundEnabled`  
**Функция:** Включает/выключает звуковые уведомления

### 🔴 Badge

**Расположение:** Раздел "ЗВУК И BADGE"  
**Переменная:** `settings.badgeEnabled`  
**Функция:** Включает/выключает красный значок на иконке приложения

---

## 📋 СТРУКТУРА НАСТРОЕК

```swift
struct NotificationSettings: Codable, Equatable {
    // Типы уведомлений
    var securityEnabled: Bool = true      // 🛡️ Безопасность
    var familyEnabled: Bool = true         // 👨‍👩‍👧‍👦 Семья
    var vpnEnabled: Bool = true            // 🔒 VPN
    var aiEnabled: Bool = true             // 🤖 AI Помощник
    var bypassEnabled: Bool = true         // 🚨 Попытки обхода
    
    // Звук и Badge
    var soundEnabled: Bool = true          // 🔊 Звук
    var badgeEnabled: Bool = true         // 🔴 Badge
    
    // Тихий режим
    var quietModeEnabled: Bool = false     // 🔇 Тихий режим
    var quietHoursEnabled: Bool = false    // 🌙 Тихие часы
    var quietHoursStart: String = "22:00"  // Начало тихих часов
    var quietHoursEnd: String = "08:00"    // Конец тихих часов
    
    // Дополнительные режимы
    var importantOnlyMode: Bool = false     // 🎯 Только важные
    var doNotDisturbMode: Bool = false     // 🔕 Не беспокоить
    var doNotDisturbUntil: Date?           // Время окончания DND
    var highPriorityOnly: Bool = false     // ⭐ Только высокий приоритет
    var maxNotificationsPerHour: Int?      // 📊 Ограничение частоты
}
```

---

## 🔄 ЛОГИКА РАБОТЫ

### Приоритет проверок (сверху вниз):

1. **"Не беспокоить"** - полностью отключает все уведомления
2. **"Только важные"** - показывает только угрозы и предупреждения
3. **"Только высокий приоритет"** - фильтрует по приоритету
4. **"Ограничение частоты"** - ограничивает количество в час
5. **"Тихие часы"** - проверяет текущее время
6. **"Тихий режим"** - применяется если включен тихий режим или тихие часы активны
7. **Звук** - включается/выключается отдельно

---

## 💾 СОХРАНЕНИЕ НАСТРОЕК

**Механизм:**
- ✅ Сохранение в `UserDefaults` через JSON encoding
- ✅ Автоматическое сохранение при изменении
- ✅ Загрузка при запуске приложения

**Файл:** `Core/Notifications/NotificationManager.swift`
- Метод `saveSettings()` - сохранение
- Метод `loadSettings()` - загрузка

---

## ✅ ИТОГОВЫЙ СТАТУС

| Режим | Статус | Описание |
|-------|--------|----------|
| Тихий режим | ✅ | Уведомления без звука и баннера |
| Тихие часы | ✅ | Автоматический режим по времени |
| Не беспокоить | ✅ | Полное отключение на время |
| Только важные | ✅ | Фильтр по типу уведомлений |
| Только высокий приоритет | ✅ | Фильтр по приоритету |
| Ограничение частоты | ✅ | Лимит уведомлений в час |
| Звук | ✅ | Включение/выключение звука |
| Badge | ✅ | Включение/выключение значка |

---

## 🎯 ГДЕ НАЙТИ В ПРИЛОЖЕНИИ

1. **Открыть приложение**
2. **Настройки** → Экран настроек
3. **Уведомления** → Открыть настройки уведомлений
4. **Выбрать режим:**
   - Раздел "ЗВУК И BADGE" → "Тихий режим"
   - Раздел "ТИХИЕ ЧАСЫ" → "Включить тихие часы"
   - Раздел "ДОПОЛНИТЕЛЬНЫЕ РЕЖИМЫ" → Другие режимы

---

**Документ создан:** 2025-11-01  
**Проект:** ALADDIN iOS Mobile Security App  
**Статус:** ✅ ВСЕ РЕЖИМЫ РЕАЛИЗОВАНЫ И РАБОТАЮТ


