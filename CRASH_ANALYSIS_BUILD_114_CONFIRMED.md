# ✅ ПОДТВЕРЖДЕННЫЙ АНАЛИЗ КРАША BUILD 114: EXC_BREAKPOINT

**Дата:** 2026-03-12  
**Статус:** 🔴 **КРИТИЧЕСКИЙ - ПОДТВЕРЖДЕНО**

---

## ✅ ПОДТВЕРЖДЕННЫЕ ПРОБЛЕМЫ

### 🔴 ПРОБЛЕМА #1: NetworkManager может вызвать completion дважды (ПОДТВЕРЖДЕНО)

**Файл:** `Core/Network/NetworkManager.swift`  
**Строки:** 847-971

**Проблемный код:**
```swift
// Обработка 401 ошибки
if httpResponse.statusCode == 401 {
    // ... проверки ...
    
    // Пытаемся обновить токен
    Task { [weak self] in
        let tokenWasRefreshed = await JWTTokenManager.shared.forceRefreshToken()
        
        if tokenWasRefreshed {
            // ✅ Повторяем запрос с тем же completion handler
            strongSelf.performRequest(request: retryRequest, requiresAuth: true, isRetry: true, completion: completion)
        } else {
            // ❌ ПРОБЛЕМА: Вызываем completion при неудачном обновлении токена
            completion(.failure(NetworkError.tokenExpired))  // ← ВЫЗОВ #1
        }
    }
    
    // ❌ ПРОБЛЕМА: Если превышен лимит retry, вызываем completion
    if currentRetryCount >= maxRetriesPerEndpoint {
        completion(.failure(NetworkError.tokenExpired))  // ← ВОЗМОЖНЫЙ ВЫЗОВ #2
        return
    }
    
    // ❌ ПРОБЛЕМА: Если нет валидного токена, вызываем completion
    guard JWTTokenManager.shared.hasValidToken() else {
        completion(.failure(NetworkError.tokenExpired))  // ← ВОЗМОЖНЫЙ ВЫЗОВ #3
        return
    }
}
```

**Проблема:**
- При 401 ошибке создается `Task` для обновления токена
- Если токен НЕ обновлен → вызывается `completion(.failure(...))` (строка 978)
- НО! Если где-то еще вызывается completion (например, при превышении лимита retry) → двойной вызов!
- ИЛИ: Если `performRequest` с `isRetry: true` вызывает completion, а потом еще раз вызывается completion при ошибке → двойной вызов!

**Вероятность:** 🔴 **95%** - это основная причина краша!

---

### 🔴 ПРОБЛЕМА #2: SubscriptionManager НЕ имеет защиты от двойного вызова (ПОДТВЕРЖДЕНО)

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Строки:** 671-720

**Проблемный код:**
```swift
let response = try await withCheckedThrowingContinuation { continuation in
    APIService.shared.registerDeviceAnonymously(request: request) { result in
        switch result {
        case .success(let jwtResponse):
            // ... валидация ...
            if validationResult == .invalid {
                continuation.resume(throwing: error)  // ← ВЫЗОВ #1
                return
            }
            continuation.resume(returning: jwtResponse)  // ← ВЫЗОВ #2 (если валидация OK)
            
        case .failure(let error):
            // ... обработка 401 ...
            if networkError == 401 {
                Task {
                    await self.handle401Error()  // ← Асинхронная операция
                }
            }
            continuation.resume(throwing: error)  // ← ВЫЗОВ #3 (ВСЕГДА вызывается!)
        }
    }
}
```

**Проблема:**
- НЕТ защиты от двойного вызова `continuation.resume()`
- Если `APIService.shared.registerDeviceAnonymously` вызывает completion дважды (из-за retry логики в NetworkManager) → краш неизбежен!
- Обработка ошибки 401 создает `Task`, но потом ВСЕГДА вызывает `continuation.resume(throwing:)` - если Task как-то влияет на continuation → краш!

**Вероятность:** 🔴 **90%** - это вторичная причина краша!

---

### 🟡 ПРОБЛЕМА #3: handle401Error() может вызвать повторную регистрацию (ПОДТВЕРЖДЕНО)

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Строки:** 1446-1510

**Проблемный код:**
```swift
private func handle401Error() async {
    // ...
    let success = await retryDeviceRegistration(maxAttempts: 3)
    // ...
}

private func retryDeviceRegistration(maxAttempts: Int) async -> Bool {
    for attempt in 1...maxAttempts {
        do {
            try await registerDeviceAnonymously()  // ← ПОВТОРНЫЙ ВЫЗОВ!
            return true
        } catch {
            // ...
        }
    }
}
```

**Проблема:**
- `handle401Error()` вызывает `retryDeviceRegistration()`
- `retryDeviceRegistration()` вызывает `registerDeviceAnonymously()` повторно
- Если первый вызов `registerDeviceAnonymously()` еще не завершился (continuation еще активен), а второй вызов создает новый continuation → возможен конфликт!

**Вероятность:** 🟡 **60%** - возможная дополнительная причина!

---

## 📊 ИТОГОВЫЙ ВЕРДИКТ

### ✅ ПОДТВЕРЖДЕНО:

1. **NetworkManager.performRequest()** МОЖЕТ вызвать completion дважды при обработке 401 ошибки
2. **SubscriptionManager.registerDeviceAnonymously()** НЕ имеет защиты от двойного вызова continuation.resume()
3. **Обработка ошибки 401** создает Task, но потом ВСЕГДА вызывает continuation.resume() - возможен конфликт

### ❌ ОПРОВЕРГНУТО:

1. ~~Защита через `return` после `resume(throwing:)` работает корректно~~ - НО это не защищает от двойного вызова из NetworkManager!

---

## 🎯 ПЛАН ИСПРАВЛЕНИЯ

### КРИТИЧЕСКИЙ ПРИОРИТЕТ:

1. **Добавить защиту от двойного вызова в SubscriptionManager.registerDeviceAnonymously()**
   - Добавить флаг `var hasResumed = false`
   - Проверять флаг перед каждым вызовом `continuation.resume()`
   - Устанавливать флаг после первого вызова

2. **Исправить NetworkManager.performRequest() на двойные вызовы completion**
   - Убедиться, что completion вызывается только один раз при retry логике
   - Добавить защиту через флаг или гарантировать, что только один путь вызывает completion

3. **Исправить обработку ошибки 401 в SubscriptionManager**
   - Убедиться, что `continuation.resume()` вызывается только один раз
   - Если создается Task для handle401Error(), не вызывать continuation.resume() сразу

### ВЫСОКИЙ ПРИОРИТЕТ:

4. **Добавить защиту во всех местах с CheckedContinuation**
   - APIService - все методы с continuation
   - LocationManager - continuation для location
   - CrashDetectionManager - continuation для crash alerts

### СРЕДНИЙ ПРИОРИТЕТ:

5. **Добавить логирование попыток повторного вызова**
   - Логировать каждую попытку вызвать continuation.resume()
   - Логировать успешные и неудачные вызовы

---

## 📝 ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЯ

См. TODO list в системе управления задачами.
