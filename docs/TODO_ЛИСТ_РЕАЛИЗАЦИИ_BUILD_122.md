# 📋 ДЕТАЛЬНЫЙ TODO ЛИСТ РЕАЛИЗАЦИИ BUILD 122

**Дата:** 16 марта 2026  
**Build:** 122  
**Статус:** 🚀 **ГОТОВО К РЕАЛИЗАЦИИ**

---

## 📊 ОБЩАЯ СТАТИСТИКА

| Категория | Количество | Время |
|-----------|------------|-------|
| **Критичных задач (🔴)** | 10 | ~60 минут |
| **Важных задач (🟡)** | 5 | ~60 минут |
| **Рекомендуемых (🟢)** | 1 | ~5 минут |
| **Тестирование (🧪)** | 6 | ~30 минут |
| **ИТОГО** | **22** | **~2.75 часа** |

---

## 🔴 ЭТАП 1: ВОССТАНОВЛЕНИЕ ТОКЕНА ПЕРЕД ЗАПРОСАМИ (КРИТИЧНО)

**Приоритет:** 🔴 КРИТИЧНО  
**Время:** 15 минут  
**Риск:** Низкий

### ☐ ЭТАП 1.1: Добавить восстановление токена в NetworkManager.get()

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `get<T: Decodable>(...)`  
**Строка:** ~246 (после проверки `requiresAuth`)

**Код для добавления:**
```swift
// ✅ BUILD 122: Восстановление токена перед запросом
if requiresAuth {
    // ✅ ВОССТАНОВЛЕНИЕ: Пытаемся восстановить токен из SubscriptionManager
    if AppConfig.authToken == nil {
        if let token = SubscriptionManager.shared.currentToken {
            AppConfig.authToken = token.token
            #if DEBUG
            logger.business("✅ NetworkManager.get: Токен восстановлен из SubscriptionManager")
            #endif
        }
    }
    
    guard let token = AppConfig.authToken else {
        // ... существующий код ...
    }
}
```

**Проверка:**
- [ ] Код добавлен
- [ ] Логирование только в DEBUG
- [ ] Не вызывает UserDefaults
- [ ] Безопасно для main thread

---

### ☐ ЭТАП 1.2: Добавить восстановление токена в NetworkManager.post()

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `post<T: Decodable, B: Encodable>(...)`  
**Строка:** ~300 (после проверки `requiresAuth`)

**Код:** Аналогично ЭТАП 1.1

**Проверка:**
- [ ] Код добавлен
- [ ] Логирование только в DEBUG
- [ ] Не вызывает UserDefaults
- [ ] Безопасно для main thread

---

### ☐ ЭТАП 1.3: Добавить восстановление токена в NetworkManager.put()

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `put<T: Decodable, B: Encodable>(...)`

**Код:** Аналогично ЭТАП 1.1

**Проверка:**
- [ ] Код добавлен
- [ ] Логирование только в DEBUG
- [ ] Не вызывает UserDefaults
- [ ] Безопасно для main thread

---

### ☐ ЭТАП 1.4: Добавить восстановление токена в NetworkManager.patch()

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `patch<T: Decodable, B: Encodable>(...)`

**Код:** Аналогично ЭТАП 1.1

**Проверка:**
- [ ] Код добавлен
- [ ] Логирование только в DEBUG
- [ ] Не вызывает UserDefaults
- [ ] Безопасно для main thread

---

### ☐ ЭТАП 1.5: Добавить восстановление токена в NetworkManager.delete()

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `delete<T: Decodable>(...)`

**Код:** Аналогично ЭТАП 1.1

**Проверка:**
- [ ] Код добавлен
- [ ] Логирование только в DEBUG
- [ ] Не вызывает UserDefaults
- [ ] Безопасно для main thread

---

## 🔴 ЭТАП 2: УМНАЯ ОБРАБОТКА 403 С ЗАЩИТОЙ ПОДПИСКИ (КРИТИЧНО!)

**Приоритет:** 🔴 КРИТИЧНО!  
**Время:** 45 минут  
**Риск:** Высокий → Средний (после исправлений)

### ☐ ЭТАП 2.1: Изменить обработку 403 в JWTErrorRecovery.analyzeNetworkError()

**Файл:** `Core/Managers/JWTErrorRecovery.swift`  
**Метод:** `analyzeNetworkError()`  
**Строка:** ~102 (case 403)

**Текущий код:**
```swift
case 403:
    logger.business("🚫 DEFENSIVE JWT: 403 Forbidden - insufficient permissions")
    return .userNotification  // ❌ Только уведомление
```

**Новый код:**
```swift
case 403:
    logger.business("🔄 DEFENSIVE JWT: 403 Forbidden - проверяем подписку")
    
    // ✅ BUILD 122: КРИТИЧНО - Проверяем уровень подписки перед перерегистрацией
    let currentLevel = SubscriptionManager.shared.getCurrentLevel()
    
    if currentLevel != .free {
        // ✅ У пользователя есть платная подписка или триал
        logger.business("🔄 У пользователя активная подписка (\(currentLevel)) - восстанавливаем")
        return .silentRetry  // ✅ Будет обработано в executeStrategy
    } else {
        // ✅ Только для FREE пользователей - перерегистрация безопасна
        logger.business("🔄 FREE пользователь - перерегистрация безопасна")
        return .silentRetry  // ✅ Будет обработано в executeStrategy
    }
```

**Также нужно обновить executeStrategy для обработки 403:**
```swift
case .silentRetry:
    // ✅ BUILD 122: Для 403 ошибки - умная обработка
    if let networkError = error as? NetworkError,
       case .httpError(403) = networkError {
        let currentLevel = SubscriptionManager.shared.getCurrentLevel()
        
        if currentLevel != .free {
            // ✅ Восстанавливаем подписку
            Task.detached { @MainActor in
                let refreshed = await JWTTokenManager.shared.refreshTokenIfNeeded()
                if !refreshed {
                    await SubscriptionManager.shared.restoreSubscriptionFromServer()
                }
            }
        } else {
            // ✅ Перерегистрация для FREE
            Task.detached { @MainActor in
                await SubscriptionManager.shared.performDeviceRegistration()
            }
        }
    } else {
        // Существующая логика для других ошибок
        try await performSilentRetry()
    }
```

**Проверка:**
- [ ] Код обновлен в analyzeNetworkError()
- [ ] Код обновлен в executeStrategy()
- [ ] Проверка уровня подписки работает
- [ ] Используется Task.detached для тяжелых операций

---

### ☐ ЭТАП 2.2: Добавить метод restoreSubscriptionFromServer() в SubscriptionManager

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `restoreSubscriptionFromServer()` (новый)

**Код:**
```swift
// ✅ BUILD 122: Восстановление подписки с сервера (защита от потери подписки)
func restoreSubscriptionFromServer() async {
    guard let deviceId = currentToken?.deviceId else {
        // Нет deviceId → перерегистрация (только для FREE)
        logger.business("⚠️ Нет deviceId - перерегистрация")
        await performDeviceRegistration()
        return
    }
    
    logger.business("🔄 Восстановление подписки с сервера для deviceId: \(deviceId)")
    
    // ✅ Запрашиваем текущую подписку с сервера
    // Используем существующий метод getSubscriptionStatus()
    // Но нужно получить userId из токена
    guard let userId = currentToken?.deviceId else {
        logger.error("❌ Не удалось получить userId из токена")
        await performDeviceRegistration()
        return
    }
    
    APIService.shared.getSubscriptionStatus(userId: userId) { [weak self] result in
        Task { @MainActor [weak self] in
            guard let self = self else { return }
            
            switch result {
            case .success(let statusResponse):
                // ✅ Восстанавливаем подписку из ответа сервера
                logger.business("✅ Подписка восстановлена с сервера")
                
                // Преобразуем SubscriptionStatusSummaryResponse в SubscriptionStatus
                // и обновляем токен
                // TODO: Реализовать преобразование
                
            case .failure(let error):
                // ✅ Если не удалось → перерегистрация (только для FREE)
                logger.error("❌ Не удалось восстановить подписку: \(error.localizedDescription)")
                logger.business("⚠️ Перерегистрация устройства")
                await self.performDeviceRegistration()
            }
        }
    }
}
```

**Проверка:**
- [ ] Метод добавлен
- [ ] Использует существующий endpoint
- [ ] Обрабатывает ошибки
- [ ] Логирование для диагностики

---

### ☐ ЭТАП 2.3: Добавить защиту от бесконечных циклов в performDeviceRegistration()

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `performDeviceRegistration()`  
**Строка:** ~263

**Текущий код:**
```swift
private func performDeviceRegistration() async {
    // ... существующий код без защиты от циклов ...
}
```

**Новый код:**
```swift
// ✅ BUILD 122: Защита от бесконечных циклов
private var registrationAttempts: Int = 0
private let maxRegistrationAttempts: Int = 3
private let registrationLock = NSLock()  // ✅ Защита от race condition

private func performDeviceRegistration() async {
    // ✅ BUILD 122: Проверка количества попыток
    registrationLock.lock()
    guard registrationAttempts < maxRegistrationAttempts else {
        registrationLock.unlock()
        logger.error("❌ Превышено максимальное количество попыток регистрации (\(maxRegistrationAttempts))")
        return
    }
    registrationAttempts += 1
    registrationLock.unlock()
    
    let logger = MasterLogger.shared
    logger.business("📱 DEFENSIVE JWT: Выполняем регистрацию устройства (попытка \(registrationAttempts)/\(maxRegistrationAttempts))")
    
    do {
        try await registerDeviceAnonymously()
        logger.business("✅ DEFENSIVE JWT: Регистрация устройства прошла успешно")
        
        // ✅ Сброс счетчика при успехе
        registrationLock.lock()
        registrationAttempts = 0
        registrationLock.unlock()
        
        // Проверяем, что токен был установлен
        if let token = currentToken {
            logger.business("✅ DEFENSIVE JWT: Токен успешно установлен после регистрации")
            JWTEventLogger.logDeviceRegistration(success: true, error: nil, deviceId: token.deviceId)
        }
    } catch {
        logger.error("❌ DEFENSIVE JWT: Регистрация устройства провалилась: \(error.localizedDescription)")
        
        // ✅ Сброс счетчика при ошибке (чтобы не блокировать навсегда)
        registrationLock.lock()
        if registrationAttempts >= maxRegistrationAttempts {
            registrationAttempts = 0  // Сброс для следующей попытки через время
        }
        registrationLock.unlock()
        
        JWTEventLogger.logDeviceRegistration(success: false, error: error.localizedDescription, deviceId: "unknown")
    }
}
```

**Проверка:**
- [ ] Счетчик попыток добавлен
- [ ] NSLock для thread-safety
- [ ] Сброс счетчика при успехе
- [ ] Логирование попыток

---

### ☐ ЭТАП 2.4: Протестировать сохранение триала при 403 ошибке

**Тест:** TRIAL пользователь (день 5 из 14) → 403 → триал сохраняется

**Сценарий:**
1. Создать TRIAL пользователя (день 5 из 14)
2. Симулировать 403 ошибку
3. Проверить: НЕ произошла перерегистрация
4. Проверить: использован refresh token или восстановление с сервера
5. Проверить: триал сохранен (день 5 из 14)
6. Проверить: запрос успешен

**Проверка:**
- [ ] Тест выполнен
- [ ] Триал сохранен
- [ ] Запрос успешен

---

### ☐ ЭТАП 2.5: Протестировать сохранение Premium подписки при 403 ошибке

**Тест:** Premium пользователь → 403 → Premium сохраняется

**Сценарий:**
1. Создать Premium пользователя
2. Симулировать 403 ошибку
3. Проверить: НЕ произошла перерегистрация
4. Проверить: использован refresh token или восстановление с сервера
5. Проверить: Premium подписка сохранена
6. Проверить: запрос успешен

**Проверка:**
- [ ] Тест выполнен
- [ ] Premium подписка сохранена
- [ ] Запрос успешен

---

## 🟢 ЭТАП 3: ПРОВЕРКА СИНХРОНИЗАЦИИ ПРИ ИНИЦИАЛИЗАЦИИ (РЕКОМЕНДУЕТСЯ)

**Приоритет:** 🟢 РЕКОМЕНДУЕТСЯ  
**Время:** 5 минут  
**Риск:** Низкий

### ☐ ЭТАП 3.1: Добавить проверку синхронизации в initializeOnAppStart()

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `initializeOnAppStart()`  
**Строка:** После `loadPersistedData()`

**Код:**
```swift
func initializeOnAppStart() async {
    // ... существующий код ...
    
    loadPersistedData()
    
    // ✅ BUILD 122: Проверка синхронизации токена с AppConfig
    if let token = currentToken {
        if AppConfig.authToken == nil {
            AppConfig.authToken = token.token
            logger.business("✅ Токен синхронизирован с AppConfig при инициализации")
        } else if AppConfig.authToken != token.token {
            // Токены не совпадают - обновляем AppConfig
            AppConfig.authToken = token.token
            logger.business("⚠️ Токены не совпадали - обновлен AppConfig")
        }
    }
    
    // ... остальной код ...
}
```

**Проверка:**
- [ ] Код добавлен
- [ ] Проверка выполняется один раз
- [ ] Не вызывает UserDefaults напрямую
- [ ] Безопасно для main thread

---

## 🟡 ЭТАП 4: REFRESH TOKEN ДЛЯ DEVICE TOKENS (СЕРВЕР + КЛИЕНТ)

**Приоритет:** 🟡 ВАЖНО  
**Время:** 60 минут (30 сервер + 30 клиент)  
**Риск:** Средний

### ☐ ЭТАП 4.1 (СЕРВЕР): Изменить register_device_anonymously() для создания refresh token

**Файл:** `app/routers/device_endpoints.py` (или `auth_router.py`)  
**Метод:** `register_device_anonymously()`  
**Строка:** ~97 (после создания access_token)

**Текущий код:**
```python
access_token = create_access_token(token_data)

# ❌ НЕТ refresh_token!
response = JWTDeviceRegisterResponse(
    token=access_token,
    deviceId=request.deviceId,
    expiresAt=datetime.utcnow() + timedelta(hours=24),
    subscription=SubscriptionStatus(**subscription_data)
)
```

**Новый код:**
```python
access_token = create_access_token(token_data)

# ✅ BUILD 122: Создание refresh token для device tokens
refresh_token_data = {
    "sub": device_user.id,
    "device_id": request.deviceId,
    "type": "device_refresh",  # ✅ Тип токена для device refresh
    "exp": datetime.utcnow() + timedelta(days=30)  # 30 дней
}
refresh_token = create_refresh_token(refresh_token_data)

# ✅ BUILD 122: Обновляем модель ответа
response = JWTDeviceRegisterResponse(
    token=access_token,
    refresh_token=refresh_token,  # ✅ ДОБАВЛЕНО
    deviceId=request.deviceId,
    expiresAt=datetime.utcnow() + timedelta(hours=24),
    subscription=SubscriptionStatus(**subscription_data)
)
```

**Проверка:**
- [ ] Refresh token создается
- [ ] Тип токена: "device_refresh"
- [ ] Срок действия: 30 дней
- [ ] Используется create_refresh_token()

---

### ☐ ЭТАП 4.2 (СЕРВЕР): Обновить модель JWTDeviceRegisterResponse

**Файл:** `app/routers/device_endpoints.py` (или models)  
**Модель:** `JWTDeviceRegisterResponse`

**Текущий код:**
```python
class JWTDeviceRegisterResponse(BaseModel):
    token: str
    deviceId: str
    expiresAt: datetime
    subscription: SubscriptionStatus
    # ❌ НЕТ refresh_token!
```

**Новый код:**
```python
class JWTDeviceRegisterResponse(BaseModel):
    token: str
    refresh_token: Optional[str] = None  # ✅ BUILD 122: Опциональный для обратной совместимости
    deviceId: str
    expiresAt: datetime
    subscription: SubscriptionStatus
```

**Проверка:**
- [ ] Поле refresh_token добавлено
- [ ] Опциональное (для обратной совместимости)
- [ ] Тип: Optional[str]

---

### ☐ ЭТАП 4.3 (СЕРВЕР): Обновить /api/auth/refresh для поддержки device_refresh

**Файл:** `app/routers/auth_router.py`  
**Метод:** `refresh_token()`  
**Строка:** ~352 (проверка типа токена)

**Текущий код:**
```python
# Проверяем тип токена
if payload.get("type") != "refresh":
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный тип токена"
    )
```

**Новый код:**
```python
# ✅ BUILD 122: Поддержка device_refresh токенов
token_type = payload.get("type")
if token_type not in ["refresh", "device_refresh"]:  # ✅ ДОБАВЛЕНО device_refresh
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный тип токена"
    )

# ✅ BUILD 122: Для device tokens используем sub вместо user_id
if token_type == "device_refresh":
    user_id = payload.get("sub") or payload.get("device_id")
    email = None  # Device tokens не имеют email
else:
    user_id = payload.get("user_id") or payload.get("id")
    email = payload.get("email")

if not user_id:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Токен не содержит необходимых данных"
    )

# Создаем новые токены
token_data = {
    "user_id": user_id,
    "id": user_id,
    "sub": user_id,  # ✅ Для device tokens
    "email": email,
    "device_id": payload.get("device_id"),  # ✅ Сохраняем device_id
    "type": "device_auth" if token_type == "device_refresh" else "access"  # ✅ Тип нового токена
}

access_token = create_access_token(token_data, expires_delta=timedelta(hours=24))

# ✅ BUILD 122: Создаем новый refresh token для device tokens
if token_type == "device_refresh":
    new_refresh_token_data = {
        "sub": user_id,
        "device_id": payload.get("device_id"),
        "type": "device_refresh",
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    new_refresh_token = create_refresh_token(new_refresh_token_data)
else:
    new_refresh_token = create_refresh_token(token_data)

return RefreshTokenResponse(
    access_token=access_token,
    refresh_token=new_refresh_token,
    expires_in=86400,
    token_type="Bearer"
)
```

**Проверка:**
- [ ] Поддержка типа "device_refresh"
- [ ] Использование "sub" для device tokens
- [ ] Сохранение device_id
- [ ] Создание нового refresh token

---

### ☐ ЭТАП 4.4 (КЛИЕНТ): Обновить модель JWTDeviceRegisterResponse

**Файл:** `Core/Models/SubscriptionModels.swift`  
**Модель:** `JWTDeviceRegisterResponse`

**Текущий код:**
```swift
struct JWTDeviceRegisterResponse: Codable {
    let token: String
    let deviceId: String
    let expiresAt: String
    let registeredAt: String
    let subscription: DeviceRegistrationSubscription
    // ❌ НЕТ refreshToken!
}
```

**Новый код:**
```swift
struct JWTDeviceRegisterResponse: Codable {
    let token: String
    let refreshToken: String?  // ✅ BUILD 122: Опциональный для обратной совместимости
    let deviceId: String
    let expiresAt: String
    let registeredAt: String
    let subscription: DeviceRegistrationSubscription
    
    /// ✅ BUILD 122: Маппинг snake_case (сервер) → camelCase (клиент)
    enum CodingKeys: String, CodingKey {
        case token
        case refreshToken = "refresh_token"  // ✅ Маппинг
        case deviceId = "device_id"
        case expiresAt = "expires_at"
        case registeredAt = "registered_at"
        case subscription
    }
}
```

**Проверка:**
- [ ] Поле refreshToken добавлено
- [ ] Опциональное (String?)
- [ ] Правильный маппинг snake_case → camelCase

---

### ☐ ЭТАП 4.5 (КЛИЕНТ): Сохранить refresh token в registerDeviceAnonymously()

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `registerDeviceAnonymously()`  
**Строка:** ~815 (после storeToken)

**Код:**
```swift
await storeToken(jwtToken)

// ✅ BUILD 122: Сохранение refresh token для device tokens
if let refreshToken = response.refreshToken {
    KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
    logger.business("✅ Refresh token сохранен в Keychain для device token")
} else {
    logger.business("⚠️ Refresh token не получен от сервера (обратная совместимость)")
}
```

**Проверка:**
- [ ] Refresh token сохраняется в Keychain
- [ ] Логирование только в DEBUG
- [ ] Обработка отсутствия refresh token

---

### ☐ ЭТАП 4.6 (КЛИЕНТ): Обновить refreshTokenIfNeeded() для device tokens

**Файл:** `Core/Security/JWTTokenManager.swift`  
**Метод:** `refreshTokenIfNeeded()`

**Текущий код:**
```swift
guard let refreshToken = keychainManager.loadString(forKey: .refreshToken) else {
    print("❌ JWT: Refresh token не найден в Keychain")
    return false  // ❌ Не обновляется, но и не перерегистрируется
}
```

**Новый код:**
```swift
guard let refreshToken = keychainManager.loadString(forKey: .refreshToken) else {
    print("⚠️ JWT: Refresh token не найден в Keychain - возможно device token")
    
    // ✅ BUILD 122: Для device tokens перерегистрируем устройство
    // Только если это device token (проверяем тип токена)
    if let currentToken = AppConfig.authToken,
       let payload = decodeJWT(currentToken),
       payload["type"] as? String == "device_auth" {
        print("🔄 JWT: Device token без refresh token - перерегистрируем устройство")
        await SubscriptionManager.shared.performDeviceRegistration()
        return true
    }
    
    return false
}
```

**Проверка:**
- [ ] Проверка типа токена
- [ ] Перерегистрация для device tokens
- [ ] Логирование для диагностики

---

## 🧪 ТЕСТИРОВАНИЕ

### ☐ ТЕСТ 1: Восстановление токена

**Сценарий:**
1. Сохранить токен в SubscriptionManager
2. Удалить токен из AppConfig
3. Вызвать API запрос
4. Проверить: токен восстановлен, запрос успешен

**Проверка:**
- [ ] Тест выполнен
- [ ] Токен восстановлен
- [ ] Запрос успешен

---

### ☐ ТЕСТ 2: Умная обработка 403 (FREE пользователь)

**Сценарий:**
1. FREE пользователь отправляет запрос с истекшим токеном
2. Получить 403 ошибку
3. Проверить: автоматическая перерегистрация выполнена
4. Проверить: запрос повторен с новым токеном
5. Проверить: запрос успешен
6. Проверить: подписка осталась FREE

**Проверка:**
- [ ] Тест выполнен
- [ ] Перерегистрация работает
- [ ] Подписка FREE сохранена

---

### ☐ ТЕСТ 3: Умная обработка 403 (TRIAL пользователь)

**Сценарий:**
1. TRIAL пользователь (день 5 из 14) отправляет запрос с истекшим токеном
2. Получить 403 ошибку
3. Проверить: НЕ произошла перерегистрация
4. Проверить: использован refresh token или восстановление с сервера
5. Проверить: триал сохранен (день 5 из 14)
6. Проверить: запрос успешен

**Проверка:**
- [ ] Тест выполнен
- [ ] Триал сохранен
- [ ] Запрос успешен

---

### ☐ ТЕСТ 4: Умная обработка 403 (Premium пользователь)

**Сценарий:**
1. Premium пользователь отправляет запрос с истекшим токеном
2. Получить 403 ошибку
3. Проверить: НЕ произошла перерегистрация
4. Проверить: использован refresh token или восстановление с сервера
5. Проверить: Premium подписка сохранена
6. Проверить: запрос успешен

**Проверка:**
- [ ] Тест выполнен
- [ ] Premium подписка сохранена
- [ ] Запрос успешен

---

### ☐ ТЕСТ 5: Refresh token для device tokens

**Сценарий:**
1. Зарегистрировать устройство
2. Проверить: refresh token сохранен в Keychain
3. Дождаться истечения access token
4. Проверить: токен обновлен через refresh token
5. Проверить: новый refresh token сохранен

**Проверка:**
- [ ] Тест выполнен
- [ ] Refresh token работает
- [ ] Новый refresh token сохранен

---

### ☐ ТЕСТ 6: Обратная совместимость

**Сценарий:**
1. Подключиться к старому серверу (без refresh_token)
2. Проверить: приложение работает
3. Проверить: перерегистрация работает как fallback

**Проверка:**
- [ ] Тест выполнен
- [ ] Обратная совместимость работает
- [ ] Fallback работает

---

## 📊 ПРОГРЕСС РЕАЛИЗАЦИИ

### Статистика:

- **Всего задач:** 22
- **Выполнено:** 0
- **В процессе:** 0
- **Осталось:** 22

### По приоритетам:

- **🔴 Критичных:** 10 (0 выполнено)
- **🟡 Важных:** 5 (0 выполнено)
- **🟢 Рекомендуемых:** 1 (0 выполнено)
- **🧪 Тестирование:** 6 (0 выполнено)

---

## 🚀 ПОРЯДОК ВЫПОЛНЕНИЯ

### Фаза 1: Быстрые исправления (30 минут)
1. ✅ ЭТАП 1: Восстановление токена (15 минут)
2. ✅ ЭТАП 3: Проверка синхронизации (5 минут)
3. ✅ Тестирование (10 минут)

### Фаза 2: Умная обработка 403 (45 минут)
1. ✅ ЭТАП 2: Умная обработка 403 (45 минут)
2. ✅ Тестирование (15 минут)

### Фаза 3: Refresh token (60 минут)
1. ✅ ЭТАП 4: Refresh token для device tokens (60 минут)
2. ✅ Тестирование (20 минут)
3. ✅ Деплой на сервер (10 минут)

**Общее время:** ~2.75 часа

---

**Дата:** 16 марта 2026  
**Статус:** 🚀 **ГОТОВО К РЕАЛИЗАЦИИ**
