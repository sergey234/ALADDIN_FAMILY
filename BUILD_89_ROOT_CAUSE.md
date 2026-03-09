# 🚨 КОРЕННАЯ ПРИЧИНА КРАША BUILD 89
## ПРОБЛЕМА: DateFormatter в computed property вызывает рекурсию!

**Дата:** 2026-03-10  
**Версия:** BUILD 89  
**Exception:** EXC_BAD_ACCESS (SIGSEGV) - Thread stack size exceeded due to excessive recursion

---

## 🔴 КРИТИЧЕСКОЕ ОТКРЫТИЕ

### **Стек краша показывает:**
```
11  Foundation            -[NSDateFormatter stringForObjectValue:] + 140
12  ALADDIN               0x10295a110  ← subscriptionExpirationText
13  ALADDIN               0x10295b3ac  ← subscriptionExpirationText
14  ALADDIN               0x1029e6b1c  ← subscriptionExpirationText
15  ALADDIN               0x1029b2a74  ← subscriptionExpirationText
16  ALADDIN               0x1029b27f4  ← subscriptionExpirationText
17  ALADDIN               0x1029b2f2c  ← РЕКУРСИЯ НАЧИНАЕТСЯ
18-23 ALADDIN             0x1029b2f3c  ← ПОВТОР (множество раз)
```

**Вывод:**
- 🔴 Рекурсия происходит в `DateFormatter.string(from:)`
- 🔴 Адрес `0x1029b2f3c` повторяется множество раз
- 🔴 Это НОВАЯ проблема - не связана с Locale.preferredLanguages!
- 🔴 Проблема в `subscriptionExpirationText` computed property

---

## 🎯 КОРЕННАЯ ПРИЧИНА

### **Проблемный код в `MainScreen.swift`:**

```swift
private var subscriptionExpirationText: String? {
    guard !subscriptionExpiresAtIso.isEmpty else { return nil }
    
    let isoFormatter = ISO8601DateFormatter()
    isoFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    
    var parsedDate = isoFormatter.date(from: subscriptionExpiresAtIso)
    if parsedDate == nil {
        isoFormatter.formatOptions = [.withInternetDateTime]
        parsedDate = isoFormatter.date(from: subscriptionExpiresAtIso)
    }
    guard let date = parsedDate else { return nil }
    
    let displayFormatter = DateFormatter()  // ❌ ПРОБЛЕМА!
    displayFormatter.dateStyle = .medium
    displayFormatter.timeStyle = .none
    displayFormatter.locale = Locale.current  // ❌ МОЖЕТ ВЫЗЫВАТЬ РЕКУРСИЮ!
    return displayFormatter.string(from: date)
}
```

### **Почему это вызывает рекурсию:**

1. `subscriptionExpirationText` - computed property который читает `@AppStorage("subscription_expires_at_iso")`
2. `DateFormatter()` создается **каждый раз** когда вызывается computed property
3. `Locale.current` может читать из UserDefaults для получения локали
4. Когда `@AppStorage` читается, SwiftUI может вызвать `UserDefaults.objectForKey()`
5. `Locale.current` также может вызывать `UserDefaults.objectForKey()` для чтения языковых настроек
6. `DateFormatter.string(from:)` может вызывать форматирование которое снова читает локали
7. Это создает **рекурсивный цикл**:
   - `@AppStorage` → `UserDefaults.objectForKey()` 
   - → `Locale.current` → `UserDefaults.objectForKey()` 
   - → `DateFormatter.string(from:)` → форматирование → локали
   - → `@AppStorage` → ...

---

## ✅ РЕШЕНИЕ

### **Исправить `subscriptionExpirationText`:**

1. **Использовать статический DateFormatter** - не создавать каждый раз
2. **Использовать статический Locale** - не использовать `Locale.current`
3. **Кэшировать результат** - не вычислять каждый раз
4. **Использовать `@State` вместо computed property** - обновлять только при изменении `@AppStorage`

### **Рекомендуемое исправление:**

```swift
// ✅ ДОЛЖНО БЫТЬ:
private static let displayFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .medium
    formatter.timeStyle = .none
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    return formatter
}()

private var subscriptionExpirationText: String? {
    guard !subscriptionExpiresAtIso.isEmpty else { return nil }
    
    let isoFormatter = ISO8601DateFormatter()
    isoFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    
    var parsedDate = isoFormatter.date(from: subscriptionExpiresAtIso)
    if parsedDate == nil {
        isoFormatter.formatOptions = [.withInternetDateTime]
        parsedDate = isoFormatter.date(from: subscriptionExpiresAtIso)
    }
    guard let date = parsedDate else { return nil }
    
    return Self.displayFormatter.string(from: date)  // Используем статический formatter
}
```

---

## 📋 ПЛАН ИСПРАВЛЕНИЯ

1. ✅ Создать статический `DateFormatter` в `MainScreen`
2. ✅ Использовать статический `Locale(identifier: "ru_RU")` вместо `Locale.current`
3. ✅ Использовать статический formatter в `subscriptionExpirationText`
4. ✅ Протестировать компиляцию
5. ✅ Проверить что рекурсия устранена

---

**Дата создания:** 2026-03-10  
**Автор:** AI Assistant  
**Версия:** 1.0
