# 🚨 PHASE 3.1 - ИСПРАВЛЕНИЕ onChange КРАШЕЙ

## 📋 ОБЩИЙ АНАЛИЗ ПРОБЛЕМЫ

**Краш происходит из-за бесконечной рекурсии при разрешении типов SwiftUI, вызванной onChange наблюдателями.**

### 🔍 Найденные проблемные места:

1. **onChange для notificationManager** (строки 136-142)
2. **onChange для selectedTheme** (строки 147-150)
3. **onChange для tariffManager** (строки 130-134)
4. **onChange в секции уведомлений** (строки 532-548)

### 🎯 Цепочка краша:
```
View инициализация → onAppear → установка @State → срабатывает onChange → изменение @State → перестроение View → повтор инициализации → БЕСКОНЕЧНАЯ РЕКУРСИЯ
```

---

## 🛠️ ПЛАН ИСПРАВЛЕНИЯ

### **ФАЗА 1: УБРАТЬ ВСЕ onChange НАБЛЮДАТЕЛИ**

#### **1.1 Убрать onChange для tariffManager**
```swift
// ❌ УБРАТЬ ЭТО:
.onChange(of: tariffManager.currentTariff) { newTariff in
    cachedProtectionLevel = 0.0
    cachedTariffId = newTariff.rawValue
    lastProtectionLevelCalculation = Date.distantPast
}
```

#### **1.2 Убрать onChange для notificationManager**
```swift
// ❌ УБРАТЬ ЭТО:
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

#### **1.3 Убрать onChange для selectedTheme**
```swift
// ❌ УБРАТЬ ЭТО:
.onChange(of: selectedTheme) { newTheme in
    UserDefaults.standard.set(newTheme.rawValue, forKey: "selected_theme")
    applyTheme(newTheme)
}
```

#### **1.4 Убрать onChange в секции уведомлений**
```swift
// ❌ УБРАТЬ ЭТО:
.onChange(of: isSecurityNotificationsEnabled) { newValue in
    updateSecurityNotifications(enabled: newValue)
}
.onChange(of: isSoundNotificationsEnabled) { newValue in
    updateSoundNotifications(enabled: newValue)
}
```

---

### **ФАЗА 2: ЗАМЕНИТЬ onChange НА ЯВНОЕ УПРАВЛЕНИЕ**

#### **2.1 Для тарифов:**
- Оставить кэширование в getCachedProtectionLevel()
- Добавить ручной сброс кэша при необходимости

#### **2.2 Для уведомлений:**
```swift
// ✅ ЗАМЕНИТЬ НА:
settingRow(
    icon: "bell.fill",
    title: localizationManager.localized("push_notifications"),
    subtitle: localizationManager.localized("push_notifications_subtitle"),
    isEnabled: $isSecurityNotificationsEnabled
)
// Убрать .onChange - обновление будет происходить только через пользовательское действие
```

#### **2.3 Для темы:**
- Сохранение темы при переключении в cycleTheme()
- Убрать реактивное сохранение

---

### **ФАЗА 3: УПРОСТИТЬ onAppear**

#### **3.1 Оставить только необходимую инициализацию:**
```swift
.onAppear {
    // ✅ Только инициализация из UserDefaults
    if let savedThemeRaw = UserDefaults.standard.string(forKey: "selected_theme"),
       let savedTheme = ThemeMode(rawValue: savedThemeRaw) {
        selectedTheme = savedTheme
    }

    // ✅ Только вызов initializeNotifications (без установки @State)
    initializeNotifications()
}
```

---

### **ФАЗА 4: ИСПРАВИТЬ ФУНКЦИИ УПРАВЛЕНИЯ**

#### **4.1 Исправить cycleTheme:**
```swift
private func cycleTheme() {
    let allThemes = ThemeMode.allCases
    if let currentIndex = allThemes.firstIndex(of: selectedTheme) {
        let nextIndex = (currentIndex + 1) % allThemes.count
        selectedTheme = allThemes[nextIndex]

        // ✅ Добавить сохранение здесь
        UserDefaults.standard.set(selectedTheme.rawValue, forKey: "selected_theme")
        applyTheme(selectedTheme)
    }
}
```

#### **4.2 Создать функции для явного обновления уведомлений:**
```swift
private func toggleSecurityNotifications() {
    let newValue = !isSecurityNotificationsEnabled
    isSecurityNotificationsEnabled = newValue
    updateSecurityNotifications(enabled: newValue)
}

private func toggleSoundNotifications() {
    let newValue = !isSoundNotificationsEnabled
    isSoundNotificationsEnabled = newValue
    updateSoundNotifications(enabled: newValue)
}
```

---

## 🎯 РЕЗУЛЬТАТ

### **После исправления:**
- ❌ **Убраны все onChange наблюдатели**
- ✅ **Оставлена простая инициализация в onAppear**
- ✅ **Переход к явному управлению через пользовательские действия**
- ✅ **Нет рекурсии и race conditions**

### **Тестирование:**
1. Запуск приложения - нет крашей
2. Переход в настройки - стабильная работа
3. Переключение настроек - корректное обновление
4. Смена темы - сохранение в UserDefaults

---

## 📊 КОНТРОЛЬНЫЙ СПИСОК

- [ ] Убрать 4 onChange наблюдателя из body
- [ ] Убрать 2 onChange из секции уведомлений
- [ ] Упростить onAppear блок
- [ ] Исправить cycleTheme функцию
- [ ] Протестировать на устройстве
- [ ] Подтвердить отсутствие крашей