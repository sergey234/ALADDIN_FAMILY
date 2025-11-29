# Конкретные места для очистки и оптимизации

## 🗑️ 1. СТАРЫЕ ЗАГЛУШКИ (не используются нигде)

### 📍 Файл: `Screens/02_FamilyScreen.swift`

#### **Место 1: Переменные (строки 7-10)**
```swift
@State private var showContentFilterModal = false   // строка 7
@State private var showTimeControlModal = false     // строка 8
@State private var showMonitoringModal = false      // строка 9
@State private var showSafetyModal = false          // строка 10
```
**Проблема:** Эти переменные объявлены, но **НИКОГДА НЕ ИСПОЛЬЗУЮТСЯ** (никто не вызывает `showContentFilterModal = true`)

---

#### **Место 2: Sheet модификаторы (строки 270-280)**
```swift
.sheet(isPresented: $showContentFilterModal) {      // строка 270
    ContentFilterModal(isPresented: $showContentFilterModal)  // строка 271
}
.sheet(isPresented: $showTimeControlModal) {        // строка 273
    TimeControlModal(isPresented: $showTimeControlModal)      // строка 274
}
.sheet(isPresented: $showMonitoringModal) {         // строка 276
    MonitoringModal(isPresented: $showMonitoringModal)       // строка 277
}
.sheet(isPresented: $showSafetyModal) {              // строка 279
    SafetyModal(isPresented: $showSafetyModal)                // строка 280
}
```
**Проблема:** Эти модалы привязаны, но **НИКОГДА НЕ ОТКРЫВАЮТСЯ** (переменные всегда `false`)

---

#### **Место 3: Структуры модалов (строки 1760-1860)**
```swift
struct ContentFilterModal: View {                    // строка 1760
    // Простая заглушка - только текст
}

struct TimeControlModal: View {                      // строка 1786
    // Простая заглушка - только текст
}

struct MonitoringModal: View {                       // строка 1812
    // Простая заглушка - только текст
}

struct SafetyModal: View {                           // строка 1838
    // Простая заглушка - только текст
}
```
**Проблема:** Эти структуры объявлены, но **НИКОГДА НЕ ИСПОЛЬЗУЮТСЯ**

---

## 🔄 2. ДУБЛИРОВАНИЕ МОДАЛОВ

### **Проблема:**
Одинаковые модалы в двух местах с разными названиями!

#### **📍 Место 1: `02_FamilyScreen.swift` (используются)**
```swift
FamilyContentBlockModal      // строка 287 - работает ✅
FamilyTimeControlModal       // строка 290 - работает ✅
FamilyMonitoringModal        // строка 293 - работает ✅
FamilyLocationModal          // строка 296 - работает ✅
FamilyReportsModal           // строка 299 - работает ✅
FamilyAdditionalModal        // строка 302 - работает ✅
```

#### **📍 Место 2: `07_ParentalControlScreen.swift` (дубликаты)**
```swift
ParentalContentBlockModal    // строка 95 - дубликат ❌
ParentalTimeControlModal     // строка 98 - дубликат ❌
ParentalMonitoringModal      // строка 101 - дубликат ❌
ParentalLocationModal        // строка 104 - дубликат ❌
ParentalReportsModal         // строка 107 - дубликат ❌
ParentalAdditionalModal      // строка 110 - дубликат ❌
```

**Проблема:**
- Те же функции, те же данные, те же окна
- Но с разными названиями (`Family*` vs `Parental*`)
- **Результат:** Дублирование кода, больше размер приложения

---

## ✅ 3. ЧТО ДЕЛАТЬ

### **ШАГ 1: Удалить старые заглушки**

**В файле `02_FamilyScreen.swift`:**

1. **Удалить строки 7-10:**
   ```swift
   @State private var showContentFilterModal = false
   @State private var showTimeControlModal = false
   @State private var showMonitoringModal = false
   @State private var showSafetyModal = false
   ```

2. **Удалить строки 270-280:**
   ```swift
   .sheet(isPresented: $showContentFilterModal) { ... }
   .sheet(isPresented: $showTimeControlModal) { ... }
   .sheet(isPresented: $showMonitoringModal) { ... }
   .sheet(isPresented: $showSafetyModal) { ... }
   ```

3. **Удалить строки 1760-1860:**
   ```swift
   struct ContentFilterModal: View { ... }
   struct TimeControlModal: View { ... }
   struct MonitoringModal: View { ... }
   struct SafetyModal: View { ... }
   ```

---

### **ШАГ 2: Убрать дублирование модалов**

**В файле `07_ParentalControlScreen.swift`:**

**Вариант А (РЕКОМЕНДУЮ):** Заменить `Parental*` на `Family*`
```swift
// Было:
ParentalContentBlockModal(...)     // строка 95

// Стало:
FamilyContentBlockModal(...)       // использовать те же модалы
```

**Вариант Б:** Если `ParentalControlScreen` больше не нужен - можно его убрать полностью

---

### **ШАГ 3: Исправить клик на Папа/Мама**

**В файле `02_FamilyScreen.swift`:**

**Сейчас (строка 54-78):**
```swift
private func navigateToMemberScreen(role: FamilyMemberCard.FamilyRole) {
    switch role {
    case .parent:
        navigationManager.navigateTo(.parentalControl)  // ❌ Неправильно
    }
}
```

**Нужно сделать:**
```swift
private func navigateToMemberScreen(role: FamilyMemberCard.FamilyRole) {
    switch role {
    case .parent:
        // Показать профиль родителя (статистика, защита)
        // Например: модал или переход на профиль
    case .child:
        navigationManager.navigateTo(.childInterface)  // ✅ Правильно
    case .elderly:
        navigationManager.navigateTo(.elderlyInterface)  // ✅ Правильно
    }
}
```

---

## 📊 ИТОГО

### **Удалить:**
- ✅ 4 переменные `@State` (строки 7-10)
- ✅ 4 `.sheet` модификатора (строки 270-280)
- ✅ 4 структуры модалов (строки 1760-1860)
- ✅ 6 дубликатов `Parental*` модалов в `07_ParentalControlScreen.swift`

### **Исправить:**
- ✅ Логику клика на Папа/Мама (строка 54)

### **Результат:**
- ✅ Меньше кода (~150 строк)
- ✅ Нет дублирования
- ✅ Понятнее логика

