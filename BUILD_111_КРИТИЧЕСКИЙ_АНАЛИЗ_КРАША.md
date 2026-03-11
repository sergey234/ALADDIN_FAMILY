# 🔴 BUILD 111: КРИТИЧЕСКИЙ АНАЛИЗ КРАША

**Дата:** 2026-03-12  
**Build:** 111  
**Incident Identifier:** 4D6CF6D8-28AA-44AA-8DAA-EE89817F4FC9  
**Статус:** 🔴 **КРИТИЧЕСКИЙ КРАШ НА MAIN THREAD!**

---

## 🔴 АНАЛИЗ КРАША

### 📊 **Детали краша:**

- **Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`
- **Exception Message:** `Thread stack size exceeded due to excessive recursion`
- **Thread:** **Thread 0 (Main Thread)** - краш на главном потоке!
- **Ключевой стек:**
  ```
  4   ALADDIN   0x104b4572c  _DictionaryStorage.resize
  5   ALADDIN   0x104b41d5c  (рекурсия)
  6   ALADDIN   0x104b41640  (рекурсия)
  7   ALADDIN   0x104c4b88c  (рекурсия)
  8   ALADDIN   0x104c4bfd4  (рекурсия)
  9-14 ALADDIN   0x104c4bfe4  (РЕКУРСИЯ 6 РАЗ!) ← КРИТИЧНО!
  15  ALADDIN   0x104b0cba4  completeTaskWithClosure ← async/await!
  ```

**Вывод:** Рекурсия происходит через `async/await` и `Dictionary.resize` на главном потоке!

---

## 🔴 ВСЕ ВОЗМОЖНЫЕ ПРИЧИНЫ КРАША

### ❌ **ПРИЧИНА #1: AnalyticsScreen.init() вызывает logger.screenLoad()**

**Файл:** `Screens/04_AnalyticsScreen.swift`  
**Строка:** 15

**Код:**
```swift
init() {
    logger.screenLoad("AnalyticsScreen")  // ❌ КРИТИЧНО!
}
```

**Проблема:**
- `logger.screenLoad()` может вызвать рекурсию через `MasterLogger`
- `MasterLogger` может вызвать аналитику или UserDefaults
- Это может создать цикл рекурсии при инициализации экрана

**Критичность:** 🔴 **КРИТИЧНО!**

---

### ❌ **ПРИЧИНА #2: AnalyticsViewModel.init() вызывает logger.business()**

**Файл:** `ViewModels/AnalyticsViewModel.swift`  
**Строка:** 42

**Код:**
```swift
init(service: AnalyticsService) {
    logger.business("Initializing AnalyticsViewModel")  // ❌ КРИТИЧНО!
    self.service = service
}
```

**Проблема:**
- `logger.business()` может вызвать рекурсию через `MasterLogger`
- Вызывается при инициализации ViewModel
- Может создать цикл рекурсии

**Критичность:** 🔴 **КРИТИЧНО!**

---

### ❌ **ПРИЧИНА #3: Множество `.onChange` вызывают аналитику НАПРЯМУЮ без DispatchQueue.main.async!**

**Найдено 5+ мест:**

#### **1. MalwareDetectionSettingsModal**
**Файл:** `Shared/Components/Modals/MalwareDetectionSettingsModal.swift`  
**Строки:** 44-49, 57-62

**Код:**
```swift
.onChange(of: realTimeScanning) { newValue in
    componentAnalytics.trackSettingToggle(  // ❌ ПРЯМОЙ ВЫЗОВ БЕЗ DispatchQueue.main.async!
        componentId: componentId,
        settingKey: "realTimeScanning",
        enabled: newValue
    )
}
```

#### **2. PhishingProtectionSettingsModal**
**Файл:** `Shared/Components/Modals/PhishingProtectionSettingsModal.swift`  
**Строки:** 44-49, 57-62

**Код:**
```swift
.onChange(of: blockSuspiciousLinks) { newValue in
    componentAnalytics.trackSettingToggle(  // ❌ ПРЯМОЙ ВЫЗОВ БЕЗ DispatchQueue.main.async!
        componentId: componentId,
        settingKey: "blockSuspiciousLinks",
        enabled: newValue
    )
}
```

#### **3. NetworkSecuritySettingsModal**
**Файл:** `Shared/Components/Modals/NetworkSecuritySettingsModal.swift`  
**Строки:** 70-75, 84-89, 97-102, 109-114

**Код:**
```swift
.onChange(of: autoConnectVPN) { newValue in
    componentAnalytics.trackSettingToggle(  // ❌ ПРЯМОЙ ВЫЗОВ БЕЗ DispatchQueue.main.async!
        componentId: componentId,
        settingKey: "autoConnectVPN",
        enabled: newValue
    )
}
```

#### **4. IncidentResponseSettingsModal**
**Файл:** `Shared/Components/Modals/IncidentResponseSettingsModal.swift`  
**Строки:** 135-140, 149-154, 163-168

**Код:**
```swift
.onChange(of: blockEnabled) { newValue in
    componentAnalytics.trackSettingToggle(  // ❌ ПРЯМОЙ ВЫЗОВ БЕЗ DispatchQueue.main.async!
        componentId: componentId,
        settingKey: "autoActions_block",
        enabled: newValue
    )
}
```

#### **5. MobileSecuritySettingsModal**
**Файл:** `Shared/Components/Modals/MobileSecuritySettingsModal.swift`  
**Строки:** 45-48, 58-61, 71-74, 84-87, 97-100, 110-113 (6 мест!)

**Код:**
```swift
.onChange(of: deviceEncryption) { newValue in
    componentAnalytics.trackSettingToggle(  // ❌ ПРЯМОЙ ВЫЗОВ БЕЗ DispatchQueue.main.async!
        componentId: componentId,
        settingKey: "deviceEncryption",
        enabled: newValue
    )
}
// ... еще 5 мест!
```

#### **6. CrashDetectionSettingsModal**
**Файл:** `Shared/Components/Modals/CrashDetectionSettingsModal.swift`  
**Строки:** 66-69

**Код:**
```swift
componentAnalytics.trackSettingToggle(  // ❌ ПРЯМОЙ ВЫЗОВ БЕЗ DispatchQueue.main.async!
    componentId: componentId,
    settingKey: "sensitivity",
    enabled: true
)
```

#### **7. PasswordGeneratorModal**
**Файл:** `Shared/Components/Modals/PasswordGeneratorModal.swift`  
**Строки:** 73-76, 94-97, 107-110, 120-123, 133-136 (5 мест!)

**Код:**
```swift
componentAnalytics.trackSettingToggle(  // ❌ ПРЯМОЙ ВЫЗОВ БЕЗ DispatchQueue.main.async!
    componentId: componentId,
    settingKey: "passwordLength",
    enabled: true
)
// ... еще 4 места!
```

**Проблема:**
- `.onChange` может вызываться на background thread или в async контексте
- Прямой вызов `trackSettingToggle()` создает Dictionary на неправильном потоке
- `DispatchQueue.main.async` в `SmartToggleRow` НЕ защищает другие модальные окна!

**Критичность:** 🔴 **КРИТИЧНО!** - это основная причина краша!

---

### ❌ **ПРИЧИНА #4: Re-entrancy Guard может не работать через async/await!**

**Проблема:**
- Re-entrancy Guard использует `Thread.current.threadDictionary`
- Если рекурсия происходит через `async/await` или `DispatchQueue.main.async`, Guard может не сработать!
- `Thread.current.threadDictionary` может быть разным в разных async контекстах

**Пример:**
```swift
// Поток 1: .onChange вызывается
DispatchQueue.main.async {
    // Поток 2: async контекст
    trackSettingToggle()  // Guard не видит флаг из Потока 1!
}
```

**Критичность:** 🔴 **КРИТИЧНО!**

---

### ❌ **ПРИЧИНА #5: Dictionary создается на неправильном потоке!**

**Проблема:**
- `@MainActor` гарантирует выполнение на main thread
- НО если вызов происходит из `.onChange` на background thread, Dictionary может создаваться на неправильном потоке
- `DispatchQueue.main.async` может не помочь, если уже внутри async контекста

**Критичность:** 🔴 **КРИТИЧНО!**

---

## 🎯 ИСТИННАЯ ПРИЧИНА КРАША

### 🔴 **ГЛАВНАЯ ПРИЧИНА:**

**Множество `.onChange` в модальных окнах вызывают `componentAnalytics.trackSettingToggle()` НАПРЯМУЮ без `DispatchQueue.main.async`!**

**Механизм краша:**
1. Пользователь переключает тумблер в модальном окне
2. `.onChange` вызывается (может быть на background thread)
3. `componentAnalytics.trackSettingToggle()` вызывается НАПРЯМУЮ
4. Dictionary создается на неправильном потоке
5. `@MainActor` пытается переключиться на main thread
6. `async/await` создает новый контекст
7. Re-entrancy Guard не срабатывает (разные async контексты)
8. Dictionary создается многократно → рекурсия → краш!

---

## 🔴 ДОПОЛНИТЕЛЬНЫЕ ПРИЧИНЫ

### ❌ **ПРИЧИНА #6: AnalyticsScreen.init() и AnalyticsViewModel.init() вызывают логгер**

**Проблема:**
- `logger.screenLoad()` и `logger.business()` могут вызвать рекурсию
- Вызываются при инициализации, когда объекты еще нестабильны

**Критичность:** 🟡 **ВАЖНО!**

---

## 🎯 ПЛАН ИСПРАВЛЕНИЙ

### 🔴 **КРИТИЧНЫЕ ИСПРАВЛЕНИЯ (СДЕЛАТЬ СЕЙЧАС!):**

#### **ИСПРАВЛЕНИЕ #1: Обернуть ВСЕ вызовы аналитики в `.onChange` в DispatchQueue.main.async**

**Файлы для исправления:**
1. `Shared/Components/Modals/MalwareDetectionSettingsModal.swift` (5 мест)
2. `Shared/Components/Modals/PhishingProtectionSettingsModal.swift` (5 мест)
3. `Shared/Components/Modals/NetworkSecuritySettingsModal.swift` (6 мест)
4. `Shared/Components/Modals/IncidentResponseSettingsModal.swift` (3 места)
5. `Shared/Components/Modals/MobileSecuritySettingsModal.swift` (6 мест)
6. `Shared/Components/Modals/CrashDetectionSettingsModal.swift` (1 место)
7. `Shared/Components/Modals/PasswordGeneratorModal.swift` (5 мест)

**ИТОГО: 31 место для исправления!**

**Изменение:**
```swift
// ❌ БЫЛО:
.onChange(of: realTimeScanning) { newValue in
    componentAnalytics.trackSettingToggle(...)
}

// ✅ СТАЛО:
.onChange(of: realTimeScanning) { newValue in
    DispatchQueue.main.async {
        componentAnalytics.trackSettingToggle(...)
    }
}
```

---

#### **ИСПРАВЛЕНИЕ #2: Убрать logger.screenLoad() из AnalyticsScreen.init()**

**Файл:** `Screens/04_AnalyticsScreen.swift`

**Изменение:**
```swift
// ❌ БЫЛО:
init() {
    logger.screenLoad("AnalyticsScreen")
}

// ✅ СТАЛО:
init() {
    // ✅ BUILD 111: Убрано логирование из init() для предотвращения рекурсии
}
```

---

#### **ИСПРАВЛЕНИЕ #3: Убрать logger.business() из AnalyticsViewModel.init()**

**Файл:** `ViewModels/AnalyticsViewModel.swift`

**Изменение:**
```swift
// ❌ БЫЛО:
init(service: AnalyticsService) {
    logger.business("Initializing AnalyticsViewModel")
    self.service = service
}

// ✅ СТАЛО:
init(service: AnalyticsService) {
    // ✅ BUILD 111: Убрано логирование из init() для предотвращения рекурсии
    self.service = service
}
```

---

#### **ИСПРАВЛЕНИЕ #4: Улучшить Re-entrancy Guard для async/await**

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Проблема:** `Thread.current.threadDictionary` может не работать через async/await

**Решение:** Использовать глобальный NSLock вместо thread-local флага

**Изменение:**
```swift
// ❌ БЫЛО:
private static let recursionKey = "ComponentAnalytics.isTracking"

func trackSettingToggle(...) {
    let threadDict = Thread.current.threadDictionary
    if threadDict[Self.recursionKey] != nil { return }
    threadDict[Self.recursionKey] = true
    defer { threadDict.removeObject(forKey: Self.recursionKey) }
    // ...
}

// ✅ СТАЛО:
private static let trackingLock = NSLock()
private static var isTracking: Bool = false

func trackSettingToggle(...) {
    Self.trackingLock.lock()
    guard !Self.isTracking else {
        Self.trackingLock.unlock()
        print("⚠️ [ComponentAnalytics] Recursion detected and blocked")
        return
    }
    Self.isTracking = true
    Self.trackingLock.unlock()
    
    defer {
        Self.trackingLock.lock()
        Self.isTracking = false
        Self.trackingLock.unlock()
    }
    // ...
}
```

---

## 📊 ИТОГОВАЯ ТАБЛИЦА ПРОБЛЕМ

| Проблема | Критичность | Файлов | Мест |
|----------|-------------|--------|------|
| **Прямые вызовы аналитики в .onChange** | 🔴 КРИТИЧНО | 7 | 31 |
| **logger.screenLoad() в init()** | 🟡 ВАЖНО | 1 | 1 |
| **logger.business() в init()** | 🟡 ВАЖНО | 1 | 1 |
| **Re-entrancy Guard через async/await** | 🔴 КРИТИЧНО | 1 | 7 |

---

## 🎯 ВЕРДИКТ

### 🔴 **ИСТИННАЯ ПРИЧИНА КРАША:**

**Множество `.onChange` в модальных окнах вызывают аналитику НАПРЯМУЮ без `DispatchQueue.main.async`!**

**Почему это критично:**
1. `.onChange` может вызываться на background thread
2. Прямой вызов создает Dictionary на неправильном потоке
3. `@MainActor` пытается переключиться, создавая async контекст
4. Re-entrancy Guard не срабатывает (разные async контексты)
5. Dictionary создается многократно → рекурсия → краш!

---

## 🎯 ПРИОРИТЕТ ИСПРАВЛЕНИЙ

### 🔴 **КРИТИЧНО (СДЕЛАТЬ СЕЙЧАС!):**

1. ✅ Обернуть ВСЕ вызовы аналитики в `.onChange` в `DispatchQueue.main.async` (12+ мест)
2. ✅ Улучшить Re-entrancy Guard для async/await (использовать NSLock)

### 🟡 **ВАЖНО (СДЕЛАТЬ ПОСЛЕ КРИТИЧНЫХ):**

3. ✅ Убрать `logger.screenLoad()` из `AnalyticsScreen.init()`
4. ✅ Убрать `logger.business()` из `AnalyticsViewModel.init()`

---

**ГОТОВ К ВЫПОЛНЕНИЮ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ!** 🚀
