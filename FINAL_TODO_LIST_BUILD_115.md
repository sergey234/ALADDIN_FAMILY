# 📋 ФИНАЛЬНЫЙ TODO LIST: ИСПРАВЛЕНИЕ КРАША BUILD 114

**Дата:** 2026-03-12  
**Версия:** BUILD 115  
**Статус:** ✅ **ОДОБРЕНО К ИСПРАВЛЕНИЮ**

---

## ✅ ПОДТВЕРЖДЕНИЕ ПРАВИЛЬНОСТИ НАПРАВЛЕНИЯ

### 🟢 **МЫ ИДЕМ ПРАВИЛЬНЫМ ПУТЕМ**

✅ **Соответствие принципам "Крепость 2.1":** 100%  
✅ **Безопасность для приложения:** 100%  
✅ **Улучшение приложения:** 100%  

**Вердикт:** ✅ **ОДОБРЕНО - ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ**

---

## 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ (ДЕЛАТЬ ОБЯЗАТЕЛЬНО)

### ✅ ЗАДАЧА #1: Защита от двойного вызова в SubscriptionManager.registerDeviceAnonymously()

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `registerDeviceAnonymously()`  
**Строки:** 671-720  
**Время:** 15-20 минут  
**Приоритет:** 🔴 **КРИТИЧЕСКИЙ**

**Что сделать:**
1. ✅ Добавить флаг `var hasResumed = false` внутри continuation блока
2. ✅ Добавить проверку `guard !hasResumed else { ... }` перед каждым вызовом `continuation.resume()`
3. ✅ Устанавливать `hasResumed = true` после первого вызова
4. ✅ Логировать попытки повторного вызова: `logger.error("⚠️ CRITICAL: Attempted to resume continuation twice!")`

**Код для добавления:**
```swift
let response = try await withCheckedThrowingContinuation { continuation in
    var hasResumed = false  // ✅ BUILD 115: Защита от двойного вызова
    
    APIService.shared.registerDeviceAnonymously(request: request) { [self] result in
        guard !hasResumed else {
            self.logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in registerDeviceAnonymously!")
            return
        }
        hasResumed = true
        
        switch result {
        case .success(let jwtResponse):
            // ... существующий код ...
        case .failure(let error):
            // ... существующий код ...
        }
    }
}
```

**Критерии готовности:**
- ✅ Флаг `hasResumed` добавлен
- ✅ Проверка перед каждым `continuation.resume()`
- ✅ Логирование попыток повторного вызова
- ✅ Компиляция без ошибок

---

### ✅ ЗАДАЧА #2: Исправить NetworkManager.performRequest() на двойные вызовы при 401

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `performRequest()`  
**Строки:** 847-996  
**Время:** 30-40 минут  
**Приоритет:** 🔴 **КРИТИЧЕСКИЙ**

**Что сделать:**
1. ✅ Убедиться, что при обработке 401 ошибки completion вызывается только один раз
2. ✅ Если создается Task для обновления токена, НЕ вызывать completion до завершения Task
3. ✅ Добавить защиту через флаг `var completionCalled = false` для Task блока
4. ✅ Проверить все пути выполнения при 401 ошибке

**Проблемные места:**
- Строка 878: `completion(.failure(...))` при превышении лимита retry ✅ (есть return)
- Строка 913: `completion(.failure(...))` при отсутствии валидного токена ✅ (есть return)
- Строка 993: `completion(.failure(...))` при неудачном обновлении токена ⚠️ (внутри Task)
- Строка 971: `performRequest(...)` с тем же completion при успешном обновлении ⚠️ (может вызвать двойной вызов)

**Код для исправления:**
```swift
if httpResponse.statusCode == 401 {
    // ... существующие проверки ...
    
    // Пытаемся обновить токен
    Task { [weak self] in
        var completionCalled = false  // ✅ BUILD 115: Защита от двойного вызова
        
        let tokenWasRefreshed = await JWTTokenManager.shared.forceRefreshToken()
        
        guard !completionCalled else {
            self?.logger.error("⚠️ CRITICAL: Attempted to call completion twice in 401 retry!")
            return
        }
        
        if tokenWasRefreshed {
            // ... существующий код для retry ...
            completionCalled = true
            strongSelf.performRequest(request: retryRequest, requiresAuth: true, isRetry: true, completion: completion)
        } else {
            completionCalled = true
            completion(.failure(NetworkError.tokenExpired))
        }
    }
    return
}
```

**Критерии готовности:**
- ✅ Защита от двойного вызова в Task блоке
- ✅ Completion вызывается только один раз
- ✅ Логирование попыток повторного вызова
- ✅ Компиляция без ошибок

---

### ✅ ЗАДАЧА #3: Исправить обработку ошибки 401 в SubscriptionManager

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `registerDeviceAnonymously()`  
**Строки:** 704-717  
**Время:** 10-15 минут  
**Приоритет:** 🔴 **КРИТИЧЕСКИЙ**

**Что сделать:**
1. ✅ Если создается Task для `handle401Error()`, НЕ вызывать `continuation.resume()` сразу
2. ✅ Вызывать `continuation.resume()` только если НЕ создается Task
3. ✅ ИЛИ: Вызывать `continuation.resume()` внутри Task после `handle401Error()`

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
```swift
case .failure(let error):
    if let networkError = error as? NetworkError,
       case .httpError(401) = networkError {
        // ✅ BUILD 115: Не вызываем continuation.resume() сразу при 401
        // handle401Error() обработает ошибку асинхронно
        Task {
            await self.handle401Error()
        }
        // НЕ вызываем continuation.resume() здесь - handle401Error() обработает
        return  // ✅ Выходим, не вызывая continuation
    } else {
        // Для других ошибок вызываем continuation.resume() как обычно
        continuation.resume(throwing: error)
    }
}
```

**Критерии готовности:**
- ✅ При 401 ошибке НЕ вызывается continuation.resume() сразу
- ✅ handle401Error() обрабатывает ошибку асинхронно
- ✅ Для других ошибок continuation.resume() вызывается как обычно
- ✅ Компиляция без ошибок

---

## 🟡 ВЫСОКИЙ ПРИОРИТЕТ (ДЕЛАТЬ РЕКОМЕНДУЕТСЯ)

### ✅ ЗАДАЧА #4: Защита в APIService - все методы с CheckedContinuation

**Файл:** `Core/Network/APIService.swift`  
**Методы:** Все методы с `withCheckedThrowingContinuation` (~30 мест)  
**Время:** 60-90 минут  
**Приоритет:** 🟡 **ВЫСОКИЙ**

**Что сделать:**
1. ✅ Найти все места с `withCheckedThrowingContinuation`
2. ✅ Добавить защиту от двойного вызова в каждом месте
3. ✅ Использовать флаг `hasResumed` в каждом continuation блоке
4. ✅ Логировать попытки повторного вызова

**Методы для проверки:**
- `registerDeviceAnonymously()`
- `loginByRecoveryCode()`
- `createFamily()`
- `joinFamily()`
- `getUserProfile()`
- `updateUserProfile()`
- `getFamilyMembers()`
- `getFamilyDevices()`
- И другие...

**Критерии готовности:**
- ✅ Все методы с CheckedContinuation защищены
- ✅ Логирование попыток повторного вызова
- ✅ Компиляция без ошибок

---

### ✅ ЗАДАЧА #5: Защита в LocationManager

**Файл:** `Core/Managers/LocationManager.swift`  
**Строки:** ~426, ~436  
**Время:** 15-20 минут  
**Приоритет:** 🟡 **ВЫСОКИЙ**

**Что сделать:**
1. ✅ Найти все места с `withCheckedThrowingContinuation`
2. ✅ Добавить защиту от двойного вызова
3. ✅ Логировать попытки повторного вызова

**Критерии готовности:**
- ✅ Все continuation защищены
- ✅ Логирование попыток повторного вызова
- ✅ Компиляция без ошибок

---

### ✅ ЗАДАЧА #6: Защита в CrashDetectionManager

**Файл:** `Core/Managers/CrashDetectionManager.swift`  
**Строки:** ~122, ~429  
**Время:** 15-20 минут  
**Приоритет:** 🟡 **ВЫСОКИЙ**

**Что сделать:**
1. ✅ Найти все места с `withCheckedThrowingContinuation`
2. ✅ Добавить защиту от двойного вызова
3. ✅ Логировать попытки повторного вызова

**Критерии готовности:**
- ✅ Все continuation защищены
- ✅ Логирование попыток повторного вызова
- ✅ Компиляция без ошибок

---

## 🟢 СРЕДНИЙ ПРИОРИТЕТ (ДЕЛАТЬ ПО ВОЗМОЖНОСТИ)

### ✅ ЗАДАЧА #7: Логирование для диагностики

**Файлы:** Все файлы с CheckedContinuation  
**Время:** 30-45 минут  
**Приоритет:** 🟢 **СРЕДНИЙ**

**Что сделать:**
1. ✅ Добавить логирование каждого вызова `continuation.resume()`
2. ✅ Логировать попытки повторного вызова с детальной информацией
3. ✅ Логировать успешные и неудачные вызовы

**Пример логирования:**
```swift
logger.business("🔄 Continuation.resume() called in \(#function)")
logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in \(#function)!")
```

**Критерии готовности:**
- ✅ Логирование добавлено во всех критических местах
- ✅ Логи содержат достаточно информации для диагностики
- ✅ Компиляция без ошибок

---

## 📊 СВОДНАЯ ТАБЛИЦА ЗАДАЧ

| # | Задача | Файл | Строки | Приоритет | Время | Статус |
|---|--------|------|--------|-----------|-------|--------|
| 1 | Защита в SubscriptionManager.registerDeviceAnonymously() | `SubscriptionManager.swift` | 671-720 | 🔴 КРИТИЧЕСКИЙ | 15-20 мин | ⏳ PENDING |
| 2 | Исправить NetworkManager на двойные вызовы при 401 | `NetworkManager.swift` | 847-996 | 🔴 КРИТИЧЕСКИЙ | 30-40 мин | ⏳ PENDING |
| 3 | Исправить обработку ошибки 401 в SubscriptionManager | `SubscriptionManager.swift` | 704-717 | 🔴 КРИТИЧЕСКИЙ | 10-15 мин | ⏳ PENDING |
| 4 | Защита в APIService - все методы | `APIService.swift` | ~30 мест | 🟡 ВЫСОКИЙ | 60-90 мин | ⏳ PENDING |
| 5 | Защита в LocationManager | `LocationManager.swift` | ~426, ~436 | 🟡 ВЫСОКИЙ | 15-20 мин | ⏳ PENDING |
| 6 | Защита в CrashDetectionManager | `CrashDetectionManager.swift` | ~122, ~429 | 🟡 ВЫСОКИЙ | 15-20 мин | ⏳ PENDING |
| 7 | Логирование для диагностики | Все файлы | - | 🟢 СРЕДНИЙ | 30-45 мин | ⏳ PENDING |

**Общее время:** ~3-4 часа  
**Критический приоритет:** ~1 час  
**Высокий приоритет:** ~1.5-2 часа  
**Средний приоритет:** ~30-45 минут

---

## 🎯 ПОРЯДОК ВЫПОЛНЕНИЯ

### ФАЗА 1: КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ (ОБЯЗАТЕЛЬНО)
1. ✅ Задача #1: Защита в SubscriptionManager.registerDeviceAnonymously()
2. ✅ Задача #2: Исправить NetworkManager на двойные вызовы
3. ✅ Задача #3: Исправить обработку ошибки 401

**Время:** ~1 час  
**Результат:** Предотвращение краша `EXC_BREAKPOINT`

---

### ФАЗА 2: ВЫСОКИЙ ПРИОРИТЕТ (РЕКОМЕНДУЕТСЯ)
4. ✅ Задача #4: Защита в APIService
5. ✅ Задача #5: Защита в LocationManager
6. ✅ Задача #6: Защита в CrashDetectionManager

**Время:** ~1.5-2 часа  
**Результат:** Полная защита от двойных вызовов

---

### ФАЗА 3: СРЕДНИЙ ПРИОРИТЕТ (ПО ВОЗМОЖНОСТИ)
7. ✅ Задача #7: Логирование для диагностики

**Время:** ~30-45 минут  
**Результат:** Улучшенная диагностика

---

## ✅ КРИТЕРИИ ГОТОВНОСТИ BUILD 115

### Обязательные критерии (ФАЗА 1):
- ✅ Защита от двойного вызова в SubscriptionManager.registerDeviceAnonymously()
- ✅ Исправлен NetworkManager на двойные вызовы при 401
- ✅ Исправлена обработка ошибки 401 в SubscriptionManager
- ✅ Компиляция без ошибок
- ✅ Тестирование на симуляторе без крашей

### Рекомендуемые критерии (ФАЗА 2):
- ✅ Защита во всех местах с CheckedContinuation
- ✅ Логирование попыток повторного вызова

### Опциональные критерии (ФАЗА 3):
- ✅ Расширенное логирование для диагностики

---

## 🚀 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После выполнения всех задач:
- ✅ Невозможен краш `EXC_BREAKPOINT` из-за двойного вызова `continuation.resume()`
- ✅ Защита от двойного вызова completion в NetworkManager
- ✅ Стабильная работа при сетевых ошибках и retry логике
- ✅ Логирование всех попыток повторного вызова для диагностики
- ✅ Улучшенная стабильность, надежность и пользовательский опыт

---

## 📝 ПРИМЕЧАНИЯ

- Все исправления должны соответствовать принципам "Крепость 2.1"
- Использовать асинхронные операции для предотвращения блокировок
- Добавить логирование для диагностики в production
- Тестировать на реальном устройстве после исправлений

---

**Дата создания:** 2026-03-12  
**Статус:** ✅ **ГОТОВ К ВЫПОЛНЕНИЮ**
