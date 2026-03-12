# 🔍 ДЕТАЛЬНЫЙ АНАЛИЗ КРАША BUILD 114: EXC_BREAKPOINT (SIGTRAP)

**Дата:** 2026-03-12 13:41:27  
**Версия:** BUILD 114 (1.0.0)  
**Устройство:** iPhone SE (2nd gen) - iPhone12,8  
**OS:** iPhone OS 26.1  
**Статус:** 🔴 **КРИТИЧЕСКИЙ КРАШ**

---

## 📊 ОСНОВНАЯ ИНФОРМАЦИЯ О КРАШЕ

### Тип исключения:
```
Exception Type:  EXC_BREAKPOINT (SIGTRAP)
Exception Codes: 0x0000000000000001, 0x00000001851f18c0
Termination Reason: SIGNAL; [5]
```

**Что это значит:**
- `EXC_BREAKPOINT` - это **не обычный краш**, а **принудительное прерывание** из-за **assertion failure**
- Swift runtime обнаружил **нарушение инварианта** и принудительно остановил выполнение
- Это **защитный механизм** Swift для предотвращения более серьезных проблем

---

## 🔍 АНАЛИЗ STACK TRACE

### Thread 0 (Main Thread) - КРАШ:

```
0   libswiftCore.dylib             _assertionFailure(_:_:file:line:flags:) + 172
1   libswift_Concurrency.dylib     CheckedContinuation.resume(throwing:) + 320
2   ALADDIN                        0x10493bda4  (0x1043f4000 + 5537188)
3   ALADDIN                        0x104430ff9  (0x1043f4000 + 249849)
4   ALADDIN                        0x10472259d  (0x1043f4000 + 3335581)
5   ALADDIN                        0x104430ff9  (0x1043f4000 + 249849)
6   libswift_Concurrency.dylib     completeTaskWithClosure(...)
```

### Ключевые адреса:
- `0x10493bda4` - **Основной код краша** (offset +5537188 от базового адреса)
- `0x104430ff9` - **Повторяется дважды** (offset +249849) - **ПОДОЗРИТЕЛЬНО!**
- `0x10472259d` - **Промежуточный вызов** (offset +3335581)

---

## 🎯 ПРИЧИНА КРАША

### **ДВОЙНОЙ ВЫЗОВ `CheckedContinuation.resume()`**

**Что произошло:**
1. Используется `withCheckedThrowingContinuation` для асинхронной операции
2. `continuation.resume()` был вызван **ДВА РАЗА**:
   - Первый раз: успешный вызов
   - Второй раз: попытка вызвать снова (ошибка или повторный вызов)

**Почему это краш:**
- `CheckedContinuation` - это **одноразовый** механизм
- После первого вызова `resume()`, continuation **завершается**
- Попытка вызвать `resume()` второй раз вызывает **assertion failure**
- Swift runtime принудительно останавливает выполнение

---

## 🔍 ГДЕ ИСКАТЬ ПРОБЛЕМУ

### 1. **SubscriptionManager.registerDeviceAnonymously()** (ВЫСОКИЙ ПРИОРИТЕТ)

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
            continuation.resume(throwing: error)  // ← ВОЗМОЖНЫЙ ВЫЗОВ #3
        }
    }
}
```

**Потенциальные проблемы:**
1. ✅ **Защита от двойного вызова есть** (строка 695: `return` после `resume(throwing:)`)
2. ❌ **НО:** Если `APIService.shared.registerDeviceAnonymously` вызывает completion **дважды** - краш неизбежен
3. ❌ **НО:** Если обработка ошибки 401 (строка 708) вызывает повторный вызов - краш неизбежен
4. ❌ **НО:** Если `validateJWTToken` вызывает completion где-то еще - краш неизбежен

---

### 2. **APIService.registerDeviceAnonymously()** (ВЫСОКИЙ ПРИОРИТЕТ)

**Файл:** `Core/Network/APIService.swift`  
**Строка:** 2703

**Проблемный код:**
```swift
func registerDeviceAnonymously(request: DeviceRegisterRequest, 
                               completion: @escaping (Result<JWTDeviceRegisterResponse, Error>) -> Void) {
    networkManager.post(endpoint: AppConfig.Endpoint.deviceRegister, 
                        body: request, 
                        requiresAuth: false, 
                        completion: completion)
}
```

**Потенциальные проблемы:**
1. ❓ **NetworkManager.post** может вызвать `completion` **дважды**:
   - Один раз при успехе
   - Второй раз при ошибке (если обработка ошибки не защищена)
   - Или при retry логике

---

### 3. **Другие места с CheckedContinuation** (СРЕДНИЙ ПРИОРИТЕТ)

**Файлы:**
- `Core/Managers/SubscriptionManager.swift` - строки 564, 1203
- `Core/Network/APIService.swift` - множество мест (169, 1221, 1231, и т.д.)
- `Core/Managers/LocationManager.swift` - строки 426, 436
- `Core/Managers/CrashDetectionManager.swift` - строки 122, 429

**Проблема:** Если любой из этих continuation вызывается дважды - краш неизбежен.

---

## 🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ПРОБЛЕМЫ

### Сценарий краша (наиболее вероятный):

1. **Пользователь запускает приложение**
2. **Вызывается `SubscriptionManager.initializeOnAppStart()`**
3. **Вызывается `registerDeviceAnonymously()`**
4. **Создается `CheckedContinuation`**
5. **Выполняется сетевой запрос через `APIService`**
6. **Сетевой запрос завершается успешно**
7. **Вызывается `continuation.resume(returning: jwtResponse)`** ✅
8. **НО:** Где-то еще (retry, timeout, error handler) вызывается `continuation.resume()` второй раз ❌
9. **Swift runtime обнаруживает двойной вызов**
10. **Вызывается `_assertionFailure`**
11. **Приложение крашится с `EXC_BREAKPOINT`**

---

## 🎯 ПЛАН ДЕЙСТВИЙ (БЕЗ ИСПРАВЛЕНИЯ)

### ШАГ 1: ИДЕНТИФИКАЦИЯ ТОЧНОГО МЕСТА КРАША

**Действия:**
1. ✅ Использовать символизацию crash log для определения точного адреса
2. ✅ Найти функцию по адресу `0x10493bda4` (offset +5537188)
3. ✅ Проверить, какой метод вызывает `continuation.resume()`

**Инструменты:**
- `atos` команда для символизации адресов
- Xcode Symbolication
- dSYM файл для BUILD 114

**Команда:**
```bash
atos -o ALADDIN.app.dSYM/Contents/Resources/DWARF/ALADDIN -arch arm64 0x10493bda4
```

---

### ШАГ 2: ПРОВЕРКА ВСЕХ МЕСТ С CheckedContinuation

**Действия:**
1. ✅ Найти все места, где используется `withCheckedThrowingContinuation`
2. ✅ Проверить каждый случай на возможность двойного вызова `resume()`
3. ✅ Проверить:
   - Есть ли защита через флаги?
   - Есть ли `return` после каждого `resume()`?
   - Может ли completion handler вызваться дважды?

**Файлы для проверки:**
- `Core/Managers/SubscriptionManager.swift` - 3 места
- `Core/Network/APIService.swift` - ~30 мест
- `Core/Managers/LocationManager.swift` - 2 места
- `Core/Managers/CrashDetectionManager.swift` - 2 места

---

### ШАГ 3: ПРОВЕРКА NetworkManager НА ДВОЙНЫЕ ВЫЗОВЫ

**Действия:**
1. ✅ Проверить `NetworkManager.post()` на возможность двойного вызова completion
2. ✅ Проверить retry логику - может ли она вызвать completion дважды?
3. ✅ Проверить timeout логику - может ли она вызвать completion дважды?
4. ✅ Проверить error handlers - могут ли они вызвать completion дважды?

**Файл:** `Core/Network/NetworkManager.swift`

**Что искать:**
- Множественные вызовы `completion(.success(...))` или `completion(.failure(...))`
- Отсутствие защиты через флаги
- Retry логика без проверки, был ли уже вызван completion

---

### ШАГ 4: ПРОВЕРКА ОБРАБОТКИ ОШИБОК 401

**Действия:**
1. ✅ Проверить `handle401Error()` - может ли он вызвать повторный вызов?
2. ✅ Проверить `Task { await self.handle401Error() }` - может ли он вызвать проблемы?
3. ✅ Проверить, не вызывается ли `continuation.resume()` после создания Task?

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Строки:** 704-715

**Проблема:**
```swift
if let networkError = error as? NetworkError,
   case .httpError(401) = networkError {
    self.logger.business("🚨 Обнаружена ошибка 401 при регистрации устройства")
    Task {
        await self.handle401Error()  // ← Может вызвать проблемы?
    }
} else {
    // ...
}
continuation.resume(throwing: error)  // ← Вызывается ВСЕГДА
```

**Вопрос:** Может ли `handle401Error()` вызвать повторный вызов `continuation.resume()`?

---

### ШАГ 5: ДОБАВЛЕНИЕ ЗАЩИТЫ ОТ ДВОЙНОГО ВЫЗОВА

**Действия:**
1. ✅ Добавить флаг `var hasResumed = false` в каждый continuation блок
2. ✅ Проверять флаг перед каждым вызовом `resume()`
3. ✅ Устанавливать флаг после первого вызова
4. ✅ Логировать попытки повторного вызова для диагностики

**Пример защиты:**
```swift
var hasResumed = false
let response = try await withCheckedThrowingContinuation { continuation in
    APIService.shared.registerDeviceAnonymously(request: request) { result in
        guard !hasResumed else {
            logger.error("⚠️ Attempted to resume continuation twice!")
            return
        }
        hasResumed = true
        
        switch result {
        case .success(let jwtResponse):
            continuation.resume(returning: jwtResponse)
        case .failure(let error):
            continuation.resume(throwing: error)
        }
    }
}
```

---

### ШАГ 6: ПРОВЕРКА ЛОГОВ ПЕРЕД КРАШЕМ

**Действия:**
1. ✅ Получить логи приложения за период до краша (13:33:01 - 13:41:27)
2. ✅ Искать сообщения о регистрации устройства
3. ✅ Искать сообщения об ошибках сети
4. ✅ Искать сообщения о валидации токена
5. ✅ Искать сообщения об ошибках 401

**Что искать в логах:**
- `📱 НАЧАЛО РЕГИСТРАЦИИ УСТРОЙСТВА АНОНИМНО`
- `✅ РЕГИСТРАЦИЯ УСТРОЙСТВА ПРОШЛА УСПЕШНО`
- `❌ Device registration failed`
- `🚨 Обнаружена ошибка 401`
- `✅ JWT токен прошел полную валидацию`
- `❌ JWT токен не прошел валидацию`

---

## 📊 ПРИОРИТЕТЫ ИСПРАВЛЕНИЯ

### 🔴 КРИТИЧЕСКИЙ ПРИОРИТЕТ:
1. **SubscriptionManager.registerDeviceAnonymously()** - добавить защиту от двойного вызова
2. **NetworkManager.post()** - проверить на двойные вызовы completion
3. **Обработка ошибки 401** - убедиться, что не вызывает повторный resume

### 🟡 ВЫСОКИЙ ПРИОРИТЕТ:
4. **Все места с CheckedContinuation** - добавить защиту везде
5. **LocationManager** - проверить на двойные вызовы
6. **CrashDetectionManager** - проверить на двойные вызовы

### 🟢 СРЕДНИЙ ПРИОРИТЕТ:
7. **APIService** - проверить все методы с continuation
8. **Добавить логирование** попыток повторного вызова для диагностики

---

## 🎯 ВЫВОДЫ

1. **Тип краша:** `EXC_BREAKPOINT` из-за двойного вызова `CheckedContinuation.resume()`
2. **Наиболее вероятное место:** `SubscriptionManager.registerDeviceAnonymously()`
3. **Причина:** Completion handler вызывается дважды (возможно из-за retry/timeout/error handling)
4. **Решение:** Добавить защиту от двойного вызова во всех местах с CheckedContinuation

**Статус:** 🔴 **ТРЕБУЕТСЯ НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ**

---

## 📝 ПРИМЕЧАНИЯ

- Краш произошел через **8 минут 26 секунд** после запуска приложения
- Это указывает на то, что проблема связана с **асинхронной операцией** (сетевой запрос)
- Повторяющийся адрес `0x104430ff9` в stack trace указывает на **рекурсивный вызов** или **повторную обработку**
