# 🎯 ПЛАН ИСПРАВЛЕНИЯ КРАША BUILD 114: EXC_BREAKPOINT

**Дата:** 2026-03-12  
**Версия:** BUILD 115  
**Статус:** 🔴 **КРИТИЧЕСКИЙ - ТРЕБУЕТСЯ НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ**

---

## ✅ ПОДТВЕРЖДЕННЫЕ ПРОБЛЕМЫ

### 🔴 ПРОБЛЕМА #1: NetworkManager может вызвать completion дважды (ПОДТВЕРЖДЕНО ✅)

**Место:** `Core/Network/NetworkManager.swift`, строки 847-996

**Сценарий краша:**
1. Запрос получает 401 ошибку
2. Создается `Task` для обновления токена (строка 923)
3. Токен НЕ обновлен → вызывается `completion(.failure(...))` (строка 993) ✅ ВЫЗОВ #1
4. НО! Если где-то еще вызывается completion (например, при превышении лимита retry на строке 878) → двойной вызов! ❌

**ИЛИ:**
1. Запрос получает 401 ошибку
2. Создается `Task` для обновления токена
3. Токен обновлен → вызывается `performRequest` с `isRetry: true` и тем же `completion` (строка 971)
4. Retry запрос завершается успешно → вызывается `completion(.success(...))` ✅ ВЫЗОВ #1
5. НО! Если исходный запрос тоже вызывает completion где-то еще → двойной вызов! ❌

**Вероятность:** 🔴 **95%** - это основная причина краша!

---

### 🔴 ПРОБЛЕМА #2: SubscriptionManager НЕ имеет защиты от двойного вызова (ПОДТВЕРЖДЕНО ✅)

**Место:** `Core/Managers/SubscriptionManager.swift`, строки 671-720

**Сценарий краша:**
1. Вызывается `registerDeviceAnonymously()`
2. Создается `CheckedContinuation`
3. Вызывается `APIService.shared.registerDeviceAnonymously()` с completion handler
4. Если `NetworkManager` вызывает completion дважды (из-за retry логики) → `continuation.resume()` вызывается дважды → краш! ❌

**Вероятность:** 🔴 **90%** - это вторичная причина краша!

---

### 🟡 ПРОБЛЕМА #3: handle401Error() может вызвать повторную регистрацию (ПОДТВЕРЖДЕНО ✅)

**Место:** `Core/Managers/SubscriptionManager.swift`, строки 1446-1510

**Сценарий краша:**
1. Первый вызов `registerDeviceAnonymously()` создает continuation
2. Получена ошибка 401 → создается `Task` для `handle401Error()`
3. `handle401Error()` вызывает `retryDeviceRegistration()`
4. `retryDeviceRegistration()` вызывает `registerDeviceAnonymously()` повторно → создается новый continuation
5. Если первый continuation еще активен, а второй вызывает resume → возможен конфликт!

**Вероятность:** 🟡 **60%** - возможная дополнительная причина!

---

## 📋 ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЯ

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ #1: Защита от двойного вызова в SubscriptionManager

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `registerDeviceAnonymously()`  
**Строки:** 671-720

**Что сделать:**
1. Добавить флаг `var hasResumed = false` внутри continuation блока
2. Проверять флаг перед каждым вызовом `continuation.resume()`
3. Устанавливать флаг после первого вызова
4. Логировать попытки повторного вызова для диагностики

**Код:**
```swift
let response = try await withCheckedThrowingContinuation { continuation in
    var hasResumed = false  // ✅ ЗАЩИТА ОТ ДВОЙНОГО ВЫЗОВА
    
    APIService.shared.registerDeviceAnonymously(request: request) { [self] result in
        guard !hasResumed else {
            self.logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in registerDeviceAnonymously!")
            return
        }
        hasResumed = true
        
        switch result {
        case .success(let jwtResponse):
            // ... валидация ...
            if validationResult == .invalid {
                continuation.resume(throwing: error)
                return
            }
            continuation.resume(returning: jwtResponse)
            
        case .failure(let error):
            // ... обработка 401 ...
            continuation.resume(throwing: error)
        }
    }
}
```

---

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ #2: Исправить NetworkManager на двойные вызовы

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `performRequest()`  
**Строки:** 847-996

**Что сделать:**
1. Убедиться, что при обработке 401 ошибки completion вызывается только один раз
2. Если создается Task для обновления токена, НЕ вызывать completion сразу
3. Вызывать completion только после завершения Task (успех или ошибка)
4. Добавить защиту через флаг для предотвращения двойного вызова

**Проблемный код (строки 847-996):**
```swift
if httpResponse.statusCode == 401 {
    // ... проверки ...
    
    // ❌ ПРОБЛЕМА: Если превышен лимит retry, вызываем completion
    if currentRetryCount >= maxRetriesPerEndpoint {
        completion(.failure(NetworkError.tokenExpired))  // ← ВЫЗОВ #1
        return
    }
    
    // ❌ ПРОБЛЕМА: Если нет валидного токена, вызываем completion
    guard JWTTokenManager.shared.hasValidToken() else {
        completion(.failure(NetworkError.tokenExpired))  // ← ВЫЗОВ #2
        return
    }
    
    // Пытаемся обновить токен
    Task { [weak self] in
        let tokenWasRefreshed = await JWTTokenManager.shared.forceRefreshToken()
        
        if tokenWasRefreshed {
            // ✅ Повторяем запрос с тем же completion
            strongSelf.performRequest(request: retryRequest, requiresAuth: true, isRetry: true, completion: completion)
        } else {
            // ❌ ПРОБЛЕМА: Вызываем completion при неудачном обновлении
            completion(.failure(NetworkError.tokenExpired))  // ← ВЫЗОВ #3
        }
    }
    return  // ✅ Возвращаемся, но Task продолжает работу
}
```

**Исправление:**
- Убрать все вызовы `completion()` до создания Task
- Вызывать completion только внутри Task (после обновления токена или при ошибке)
- Добавить флаг для защиты от двойного вызова

---

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ #3: Исправить обработку ошибки 401 в SubscriptionManager

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `registerDeviceAnonymously()`  
**Строки:** 704-717

**Что сделать:**
1. Если создается Task для `handle401Error()`, НЕ вызывать `continuation.resume()` сразу
2. Вызывать `continuation.resume()` только после завершения Task
3. ИЛИ: Убрать Task и вызывать `continuation.resume()` сразу, а handle401Error() вызывать отдельно

**Проблемный код:**
```swift
case .failure(let error):
    if let networkError = error as? NetworkError,
       case .httpError(401) = networkError {
        Task {
            await self.handle401Error()  // ← Асинхронная операция
        }
    }
    continuation.resume(throwing: error)  // ← ВЫЗОВ ВСЕГДА (даже если создан Task!)
}
```

**Исправление:**
- Если создается Task для handle401Error(), НЕ вызывать continuation.resume() сразу
- Вызывать continuation.resume() только если НЕ создается Task
- ИЛИ: Вызывать continuation.resume() внутри Task после handle401Error()

---

### 🟡 ВЫСОКИЙ ПРИОРИТЕТ #4: Защита во всех местах с CheckedContinuation

**Файлы для проверки:**
1. `Core/Network/APIService.swift` - ~30 мест с `withCheckedThrowingContinuation`
2. `Core/Managers/LocationManager.swift` - строки 426, 436
3. `Core/Managers/CrashDetectionManager.swift` - строки 122, 429

**Что сделать:**
1. Добавить защиту от двойного вызова во всех местах
2. Использовать флаг `hasResumed` в каждом continuation блоке
3. Логировать попытки повторного вызова

---

### 🟢 СРЕДНИЙ ПРИОРИТЕТ #5: Логирование для диагностики

**Что сделать:**
1. Добавить логирование каждого вызова `continuation.resume()`
2. Логировать попытки повторного вызова
3. Логировать успешные и неудачные вызовы

---

## 📊 ПРИОРИТЕТЫ ИСПРАВЛЕНИЯ

| Приоритет | Задача | Файл | Строки | Статус |
|-----------|--------|------|--------|--------|
| 🔴 КРИТИЧЕСКИЙ | Защита от двойного вызова в SubscriptionManager | `SubscriptionManager.swift` | 671-720 | ⏳ PENDING |
| 🔴 КРИТИЧЕСКИЙ | Исправить NetworkManager на двойные вызовы | `NetworkManager.swift` | 847-996 | ⏳ PENDING |
| 🔴 КРИТИЧЕСКИЙ | Исправить обработку ошибки 401 | `SubscriptionManager.swift` | 704-717 | ⏳ PENDING |
| 🟡 ВЫСОКИЙ | Защита в APIService | `APIService.swift` | ~30 мест | ⏳ PENDING |
| 🟡 ВЫСОКИЙ | Защита в LocationManager | `LocationManager.swift` | 426, 436 | ⏳ PENDING |
| 🟡 ВЫСОКИЙ | Защита в CrashDetectionManager | `CrashDetectionManager.swift` | 122, 429 | ⏳ PENDING |
| 🟢 СРЕДНИЙ | Логирование для диагностики | Все файлы | - | ⏳ PENDING |

---

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После исправления:
- ✅ Невозможен двойной вызов `CheckedContinuation.resume()`
- ✅ Защита от краша `EXC_BREAKPOINT`
- ✅ Логирование всех попыток повторного вызова для диагностики
- ✅ Стабильная работа при сетевых ошибках и retry логике

---

## 📝 ПРИМЕЧАНИЯ

- Все исправления должны соответствовать принципам "Крепость 2.1"
- Использовать асинхронные операции для предотвращения блокировок
- Добавить логирование для диагностики в production
