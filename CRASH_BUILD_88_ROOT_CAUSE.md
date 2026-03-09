# 🚨 КОРЕННАЯ ПРИЧИНА КРАША BUILD 88

## ПРОБЛЕМА: Рекурсия в `subscriptionExpirationText` через `Locale.preferredLanguages`

**Дата:** 2026-03-10  
**Версия:** BUILD 88  
**Exception:** EXC_BAD_ACCESS (SIGSEGV) - Thread stack size exceeded due to excessive recursion

---

## 🔴 КРИТИЧЕСКОЕ ОТКРЫТИЕ

### **Стек краша показывает:**
```
17  Foundation          -[NSUserDefaults objectForKey:] + 60
18  SwiftUI             AppStorage.wrappedValue.getter + 44
19  ALADDIN             0x10140a868  ← subscriptionExpirationText
20  ALADDIN             0x1013d679c  ← subscriptionExpirationText
21  ALADDIN             0x1013d651c  ← subscriptionExpirationText
22  ALADDIN             0x1013d6c54  ← РЕКУРСИЯ НАЧИНАЕТСЯ
23-31 ALADDIN           0x1013d6c64  ← ПОВТОР (множество раз)
```

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
    
    let displayFormatter = DateFormatter()
    displayFormatter.dateStyle = .medium
    displayFormatter.timeStyle = .none
    displayFormatter.locale = Locale(identifier: Locale.preferredLanguages.first ?? "ru_RU") // ❌ ПРОБЛЕМА!
    return displayFormatter.string(from: date)
}
```

### **Почему это вызывает рекурсию:**

1. `subscriptionExpirationText` - computed property который читает `@AppStorage("subscription_expires_at_iso")`
2. `Locale.preferredLanguages` **читает из UserDefaults** для получения предпочтительных языков
3. Когда `@AppStorage` читается, SwiftUI может вызвать `UserDefaults.objectForKey()`
4. `Locale.preferredLanguages` также вызывает `UserDefaults.objectForKey()` для чтения языковых настроек
5. Это создает **рекурсивный цикл**:
   - `@AppStorage` → `UserDefaults.objectForKey()` 
   - → `Locale.preferredLanguages` → `UserDefaults.objectForKey()` 
   - → `@AppStorage` → ...

---

## ✅ РЕШЕНИЕ

### **Исправить `subscriptionExpirationText`:**

1. **Убрать `Locale.preferredLanguages`** - использовать статический locale или `Locale.current`
2. **Кэшировать результат** - не вычислять каждый раз
3. **Использовать `@State` вместо computed property** - обновлять только при изменении `@AppStorage`

### **Рекомендуемое исправление:**

```swift
// ❌ БЫЛО (вызывает рекурсию):
displayFormatter.locale = Locale(identifier: Locale.preferredLanguages.first ?? "ru_RU")

// ✅ ДОЛЖНО БЫТЬ:
displayFormatter.locale = Locale.current // Или Locale(identifier: "ru_RU")
```

---

## 📋 ПЛАН ИСПРАВЛЕНИЯ

1. ✅ Заменить `Locale.preferredLanguages.first` на `Locale.current` в `subscriptionExpirationText`
2. ✅ Проверить другие места где используется `Locale.preferredLanguages` в computed properties
3. ✅ Протестировать компиляцию
4. ✅ Проверить что рекурсия устранена

---

**Дата создания:** 2026-03-10  
**Автор:** AI Assistant  
**Версия:** 1.0
