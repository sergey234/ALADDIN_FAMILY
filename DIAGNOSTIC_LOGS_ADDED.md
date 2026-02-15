# ✅ ДИАГНОСТИЧЕСКИЕ ЛОГИ ДОБАВЛЕНЫ

**Дата:** 2026-02-14  
**Версия:** Build 36

---

## 📋 ЧТО ДОБАВЛЕНО

### 1. ✅ Счетчики перерисовок

**Добавлены статические счетчики:**
```swift
#if DEBUG
private static var bodyCallCount: Int = 0
private static var settingsContentCallCount: Int = 0
#endif
```

**Цель:** Отслеживать, сколько раз вызываются `body` и `settingsContent()`

---

### 2. ✅ Расширенные логи в `body`

**Добавлено:**
- Счетчик вызовов `body` (#1, #2, #3...)
- Все `@StateObject` менеджеры
- Все основные `@State` переменные
- Thread.isMainThread

**Логи:**
```
🔴 SETTINGS: body вычисляется - НАЧАЛО (#1)
🔴 SETTINGS: Thread.isMainThread = true
🔴 SETTINGS: notificationManager = ...
🔴 SETTINGS: securityManager = ...
🔴 SETTINGS: featuresManager = ...
🔴 SETTINGS: tariffManager = ...
🔴 SETTINGS: isNetworkProtectionEnabled = ...
🔴 SETTINGS: isSecurityNotificationsEnabled = ...
🔴 SETTINGS: isSoundNotificationsEnabled = ...
🔴 SETTINGS: isBiometricEnabled = ...
🔴 SETTINGS: selectedTheme = ...
🔴 SETTINGS: showProfileEdit = ...
🔴 SETTINGS: localizationManager.currentLanguage = ...
```

**Цель:** Понять, какие переменные изменяются между перерисовками

---

### 3. ✅ Расширенные логи в `settingsContent()`

**Добавлено:**
- Счетчик вызовов `settingsContent()` (#1, #2, #3...)
- Все EnvironmentObject и StateObject
- Computed properties (safeLanguageCode, safeCurrentTariff)
- Stack trace (первые 5 строк)

**Логи:**
```
🔴 SETTINGS: settingsContent() вызывается (#1)
🔴 SETTINGS: Thread.isMainThread = true
🔴 SETTINGS: localizationManager доступен = true
🔴 SETTINGS: localizationManager.currentLanguage = ...
🔴 SETTINGS: tariffManager.currentTariff = ...
🔴 SETTINGS: notificationManager.notificationSettings = ...
🔴 SETTINGS: safeLanguageCode = ...
🔴 SETTINGS: safeCurrentTariff = ...
🔴 SETTINGS: Stack trace:
  [стек вызовов]
```

**Цель:** Понять, что вызывает перерисовки и откуда они идут

---

### 4. ✅ Логи в `onChange` наблюдателях

**Добавлено:**
```swift
.onChange(of: notificationManager.notificationSettings.securityEnabled) { newValue in
    #if DEBUG
    print("🟡 SETTINGS: onChange securityEnabled = \(newValue)")
    #endif
    isSecurityNotificationsEnabled = newValue
}
.onChange(of: notificationManager.notificationSettings.soundEnabled) { newValue in
    #if DEBUG
    print("🟡 SETTINGS: onChange soundEnabled = \(newValue)")
    #endif
    isSoundNotificationsEnabled = newValue
}
```

**Цель:** Понять, вызывают ли `onChange` наблюдатели перерисовки

---

### 5. ✅ Расширенные логи в `onAppear`

**Добавлено:**
- Все `@State` переменные при появлении View

**Логи:**
```
🔴 SETTINGS: onAppear вызван
🔴 SETTINGS: notificationManager = ...
🔴 SETTINGS: notificationSettings = ...
🔴 SETTINGS: Все @State переменные:
  - isNetworkProtectionEnabled = ...
  - isSecurityNotificationsEnabled = ...
  - isSoundNotificationsEnabled = ...
  - isBiometricEnabled = ...
  - selectedTheme = ...
```

**Цель:** Понять начальное состояние всех переменных

---

### 6. ✅ Логи в `onDisappear`

**Добавлено:**
```swift
.onDisappear {
    #if DEBUG
    print("🔴 SETTINGS: onDisappear вызван")
    #endif
}
```

**Цель:** Отслеживать, когда View исчезает

---

## 🎯 ЧТО ЭТО ДАСТ

### 1. Понимание причин множественных перерисовок:

**Вопросы, на которые ответят логи:**
- Сколько раз вызывается `body`?
- Сколько раз вызывается `settingsContent()`?
- Какие переменные изменяются между перерисовками?
- Вызывают ли `onChange` наблюдатели перерисовки?
- Откуда идут вызовы (stack trace)?

### 2. Диагностика краша:

**Если краш происходит:**
- До какого лога доходит выполнение?
- Какие переменные были изменены перед крашем?
- Есть ли проблемы с доступом к EnvironmentObject?

### 3. Оптимизация производительности:

**Если краш не происходит, но страница медленная:**
- Какие переменные вызывают лишние перерисовки?
- Можно ли оптимизировать `onChange` наблюдатели?
- Можно ли использовать `.id()` для стабилизации?

---

## 📊 КАК ИСПОЛЬЗОВАТЬ

### 1. Пересоберите проект:
- Clean Build Folder (⇧⌘K)
- Пересоберите проект (⌘B)

### 2. Запустите на реальном устройстве:
- Перейдите на страницу Настройки
- Соберите все логи

### 3. Проанализируйте логи:

**Ищите:**
- Сколько раз появляется `body вычисляется - НАЧАЛО (#X)`
- Сколько раз появляется `settingsContent() вызывается (#X)`
- Появляются ли `🟡 SETTINGS: onChange ...`
- Изменяются ли переменные между перерисовками

**Пример анализа:**
```
🔴 SETTINGS: body вычисляется - НАЧАЛО (#1)
🔴 SETTINGS: isSecurityNotificationsEnabled = false
🔴 SETTINGS: body вычисляется - НАЧАЛО (#2)
🟡 SETTINGS: onChange securityEnabled = true  ← Это вызвало перерисовку!
🔴 SETTINGS: isSecurityNotificationsEnabled = true
```

---

## ✅ РЕЗУЛЬТАТ

**Все диагностические логи добавлены!**

Теперь при следующем запуске вы увидите:
- Сколько раз перерисовывается View
- Какие переменные изменяются
- Что вызывает перерисовки
- Откуда идут вызовы (stack trace)

**Это поможет:**
1. Понять причину множественных перерисовок
2. Найти источник краша (если он есть)
3. Оптимизировать производительность

---

**Дата:** 2026-02-14  
**Версия:** Build 36
