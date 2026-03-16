# 🔍 КРИТИЧЕСКАЯ ПРОБЛЕМА: ТОКЕН ХРАНИТСЯ В РАЗНЫХ KEYCHAIN!

**Дата:** 2026-03-14  
**Проблема:** TokenManager не находит токен, потому что ищет в другом Keychain

---

## 🚨 НАЙДЕНА ПРОБЛЕМА!

### **Проблема: ДВА РАЗНЫХ KEYCHAIN!**

#### **1. SubscriptionManager хранит токен:**
```swift
// Core/Managers/SubscriptionManager.swift
private let keychainService = "com.aladdin.subscription"  // ← ДРУГОЙ SERVICE!
private let tokenKey = "jwt_token"                        // ← ДРУГОЙ KEY!
```

**Как хранит:**
- Service: `"com.aladdin.subscription"`
- Key: `"jwt_token"`
- Формат: `JWTToken` (структура с полями: deviceId, subscriptionLevel, token)
- Методы: `saveToKeychain()` и `loadFromKeychain()` (свои методы!)

#### **2. TokenManager ищет токен:**
```swift
// Core/Managers/TokenManager.swift
keychainManager.loadString(forKey: .authToken)  // ← ИЩЕТ В ДРУГОМ KEYCHAIN!
```

**Как ищет:**
- Service: `Bundle.main.bundleIdentifier ?? "family.aladdin.ios"`  // ← ДРУГОЙ SERVICE!
- Key: `"auth_token"` (из enum KeychainManager.Key.authToken)      // ← ДРУГОЙ KEY!
- Формат: Просто строка (String)
- Методы: `KeychainManager.shared.loadString()` (другие методы!)

#### **3. KeychainManager использует:**
```swift
// Core/Security/KeychainManager.swift
private let service = Bundle.main.bundleIdentifier ?? "family.aladdin.ios"  // ← ДРУГОЙ SERVICE!
enum Key {
    case authToken = "auth_token"  // ← ДРУГОЙ KEY!
}
```

---

## 📊 СРАВНЕНИЕ

| Параметр | SubscriptionManager | TokenManager | KeychainManager |
|----------|---------------------|--------------|-----------------|
| **Service** | `"com.aladdin.subscription"` | `"family.aladdin.ios"` | `"family.aladdin.ios"` |
| **Key** | `"jwt_token"` | `"auth_token"` | `"auth_token"` |
| **Формат** | `JWTToken` (структура) | `String` | `String` |
| **Методы** | `saveToKeychain()` / `loadFromKeychain()` | `KeychainManager.shared.loadString()` | `loadString()` |

**ВЫВОД:** Это РАЗНЫЕ хранилища! Токен хранится в одном месте, а ищется в другом!

---

## 🔍 ЧТО ПРОИСХОДИТ

### **Реальная цепочка:**

1. **Регистрация/Логин:**
   - `FamilyRegistrationViewModel.saveTokens()` сохраняет токен в `KeychainManager` (ключ `"auth_token"`)
   - Но потом `SubscriptionManager.storeToken()` сохраняет токен в СВОЙ Keychain (ключ `"jwt_token"`)

2. **Загрузка при старте:**
   - `SubscriptionManager.loadPersistedData()` загружает токен из СВОЕГО Keychain (`"jwt_token"`)
   - Восстанавливает в `AppConfig.authToken`
   - Но это происходит ПОСЛЕ того, как `AnalyticsViewModel.load()` уже проверил токен!

3. **Проверка в AnalyticsViewModel:**
   - `TokenManager.checkTokenAvailability()` ищет токен в `KeychainManager` (ключ `"auth_token"`)
   - Но токен хранится в `SubscriptionManager` Keychain (ключ `"jwt_token"`)
   - **Результат:** Токен не найден! ❌

---

## ✅ РЕШЕНИЕ

### **Вариант 1: Проверять SubscriptionManager.currentToken (РЕКОМЕНДУЕТСЯ)**

Изменить `TokenManager.checkTokenAvailability()`:
```swift
func checkTokenAvailability() -> TokenAvailability {
    // 1. Проверяем токен в AppConfig
    if let token = AppConfig.authToken, !token.isEmpty {
        return .available(token)
    }
    
    // 2. Проверяем токен в SubscriptionManager (ГЛАВНОЕ ХРАНИЛИЩЕ!)
    if let subscriptionToken = SubscriptionManager.shared.currentToken {
        AppConfig.authToken = subscriptionToken.token  // Восстанавливаем в AppConfig
        return .available(subscriptionToken.token)
    }
    
    // 3. Проверяем KeychainManager (fallback)
    if let keychainToken = keychainManager.loadString(forKey: .authToken),
       !keychainToken.isEmpty {
        AppConfig.authToken = keychainToken
        return .available(keychainToken)
    }
    
    return .notFound
}
```

### **Вариант 2: Использовать тот же Keychain**

Изменить `TokenManager` чтобы использовать тот же Keychain, что и `SubscriptionManager`:
```swift
// Использовать loadFromKeychain из SubscriptionManager
```

### **Вариант 3: Синхронизировать токены**

При сохранении токена в `SubscriptionManager`, также сохранять в `KeychainManager`:
```swift
// В SubscriptionManager.storeToken()
KeychainManager.shared.save(token.token, forKey: .authToken)  // Дублировать
```

---

## 🎯 РЕКОМЕНДАЦИЯ

**Использовать Вариант 1** - проверять `SubscriptionManager.currentToken` первым делом, потому что:
1. ✅ Это главное хранилище токена
2. ✅ Токен уже загружен в память (быстрее)
3. ✅ Не требует изменения архитектуры
4. ✅ Минимальные изменения кода

---

## 📝 ПОЧЕМУ ЛОГОВ НЕТ?

Логи диагностики не появляются, потому что:
1. ❓ Код не выполняется (возможно, `#if DEBUG` не активен)
2. ❓ Логи фильтруются (консоль не показывает print)
3. ❓ Код не компилируется или не добавлен в проект

Но главная проблема - **TokenManager ищет токен не там, где он хранится!**

---

## 🔧 ЧТО ДЕЛАТЬ

1. **Исправить TokenManager** - проверять `SubscriptionManager.currentToken` первым делом
2. **Убрать кнопку "Войти"** - она не нужна, если пользователь авторизован
3. **Проверить логи** - после исправления должны появиться логи диагностики

---

**Статус:** ✅ Проблема найдена, решение готово
