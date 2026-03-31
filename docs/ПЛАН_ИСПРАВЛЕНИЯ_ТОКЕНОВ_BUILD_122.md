# 📋 ПОЛНЫЙ ПЛАН ИСПРАВЛЕНИЯ ПРОБЛЕМЫ С ТОКЕНАМИ - BUILD 122

**Дата:** 16 марта 2026  
**Build:** 122  
**Цель:** Исправить проблему с 403 ошибками и добавить refresh token для device tokens

---

## 🎯 ОБЗОР ПЛАНА

### Проблемы:
1. ❌ Токен может отсутствовать в `AppConfig.authToken`, даже если есть в `SubscriptionManager`
2. ❌ Нет автоматической перерегистрации при 403 ошибке
3. ❌ Device tokens не имеют refresh token (требует изменений на сервере)

### Решения:
1. ✅ Восстановление токена перед запросами (КРИТИЧНО)
2. ✅ Автоматическая перерегистрация при 403 (ВАЖНО)
3. ✅ Добавление refresh token для device tokens (СЕРВЕР + КЛИЕНТ)

---

## 📊 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

### ✅ ЧТО УЖЕ ЕСТЬ:

**1. Синхронизация токенов:**
- ✅ При сохранении: `AppConfig.authToken = token.token` в `storeToken()`
- ✅ При загрузке: `AppConfig.authToken = token.token` в `loadPersistedData()`

**2. Refresh token для обычных пользователей:**
- ✅ `/api/auth/login` возвращает `refresh_token`
- ✅ `/api/auth/register` возвращает `refresh_token`
- ✅ `/api/auth/refresh` работает для обычных пользователей

**3. Защита от рекурсии (из BUILD 77-114):**
- ✅ Статические форматтеры с статическим Calendar
- ✅ Асинхронные операции с UserDefaults
- ✅ Глобальные флаги с NSLock
- ✅ @MainActor для аналитики
- ✅ Serial Dispatch Queue для логгеров

### ❌ ЧЕГО НЕТ:

**1. Восстановление токена перед запросами:**
- ❌ NetworkManager не проверяет SubscriptionManager перед запросом
- ❌ Если токен потерялся в AppConfig → сразу ошибка

**2. Автоматическая перерегистрация при 403:**
- ❌ JWTErrorRecovery только уведомляет пользователя
- ❌ Нет автоматической перерегистрации

**3. Refresh token для device tokens:**
- ❌ `/api/auth/register-device` НЕ возвращает `refresh_token`
- ❌ `JWTDeviceRegisterResponse` не содержит `refresh_token`
- ❌ Нет обновления device tokens через refresh

---

## 🏗️ АРХИТЕКТУРНЫЕ ПРИНЦИПЫ (ИЗ BUILD 77-114)

### 🛡️ ЗОЛОТЫЕ ПРАВИЛА:

1. **Объекты рождаются в тишине:** Никакой логики в `init()`
2. **Словарь — это риск:** Любой общий словарь обязан иметь `NSLock`
3. **UI — это фасад:** Обновляй данные UI мгновенно, сохраняй в фон асинхронно
4. **Изоляция:** Диагностика (Логи/Аналитика) не должна знать друг о друге
5. **@MainActor для UI данных:** Все операции со словарями на main thread
6. **Асинхронный разрыв:** Запись в `UserDefaults` должна быть асинхронной
7. **Глобальные флаги с NSLock:** Защита от рекурсии при пересоздании View
8. **Статические форматтеры:** Все `DateFormatter` со статическим Calendar

---

## 📝 ПЛАН РЕАЛИЗАЦИИ

### ЭТАП 1: ВОССТАНОВЛЕНИЕ ТОКЕНА ПЕРЕД ЗАПРОСАМИ (КРИТИЧНО)

**Приоритет:** 🔴 КРИТИЧНО  
**Время:** 15 минут  
**Риск:** Низкий (только добавление проверки)

#### Шаг 1.1: Добавить восстановление токена в NetworkManager.get()

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `get<T: Decodable>(...)`

**Код:**
```swift
// ✅ BUILD 122: Восстановление токена перед запросом
if requiresAuth {
    // ✅ ВОССТАНОВЛЕНИЕ: Пытаемся восстановить токен из SubscriptionManager
    if AppConfig.authToken == nil {
        if let token = SubscriptionManager.shared.currentToken {
            AppConfig.authToken = token.token
            logger.business("✅ NetworkManager.get: Токен восстановлен из SubscriptionManager")
        }
    }
    
    guard let token = AppConfig.authToken else {
        logger.error("❌ NetworkManager.get: Токен отсутствует - требуется регистрация устройства")
        completion(.failure(NetworkError.unauthorized("Токен авторизации отсутствует")))
        return
    }
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
}
```

**Защита от рекурсии:**
- ✅ Проверка выполняется синхронно (чтение из памяти)
- ✅ Не вызывает UserDefaults
- ✅ Не вызывает логирование в критических местах
- ✅ Безопасно для main thread

#### Шаг 1.2: Добавить восстановление токена в NetworkManager.post()

**Файл:** `Core/Network/NetworkManager.swift`  
**Метод:** `post<T: Decodable, B: Encodable>(...)`

**Код:** Аналогично шагу 1.1

#### Шаг 1.3: Добавить восстановление токена в остальные методы

**Файлы:** `Core/Network/NetworkManager.swift`  
**Методы:** `put()`, `patch()`, `delete()`

**Код:** Аналогично шагу 1.1

**Проверка:**
- ✅ Все методы с `requiresAuth: true` проверяют токен
- ✅ Восстановление происходит перед проверкой
- ✅ Логирование только в DEBUG режиме

---

### ЭТАП 2: УМНАЯ ОБРАБОТКА 403 С ЗАЩИТОЙ ПОДПИСКИ (КРИТИЧНО!)

**Приоритет:** 🔴 КРИТИЧНО!  
**Время:** 45 минут  
**Риск:** Высокий (может потерять подписку при неправильной реализации)

#### ⚠️ ВАЖНО: ПРОБЛЕМА ПРОСТОЙ ПЕРЕРЕГИСТРАЦИИ

**Проблема:**
- Простая перерегистрация через `/register-device` создает **FREE подписку**
- Это **потеряет триал или платную подписку** пользователя!
- Пользователь с Premium подпиской получит FREE после 403 ошибки

**Решение:**
- ✅ Проверять уровень подписки перед перерегистрацией
- ✅ Использовать refresh token для платных пользователей
- ✅ Восстанавливать подписку с сервера при необходимости
- ✅ Перерегистрация только для FREE пользователей

#### Шаг 2.1: Изменить обработку 403 в JWTErrorRecovery

**Файл:** `Core/Managers/JWTErrorRecovery.swift`  
**Метод:** `analyzeNetworkError()`

**Код:**
```swift
case 403:
    logger.business("🔄 DEFENSIVE JWT: 403 Forbidden - проверяем подписку")
    
    // ✅ BUILD 122: КРИТИЧНО - Проверяем уровень подписки перед перерегистрацией
    let currentLevel = SubscriptionManager.shared.getCurrentLevel()
    
    if currentLevel != .free {
        // ✅ У пользователя есть платная подписка или триал
        // ✅ Используем refresh token или восстанавливаем с сервера
        logger.business("🔄 У пользователя активная подписка (\(currentLevel)) - восстанавливаем")
        Task { @MainActor in
            // 1. Пытаемся обновить через refresh token
            let refreshed = await JWTTokenManager.shared.refreshTokenIfNeeded()
            
            if !refreshed {
                // 2. Если refresh не удался, восстанавливаем с сервера
                await SubscriptionManager.shared.restoreSubscriptionFromServer()
            }
        }
        return .silentRetry
    } else {
        // ✅ Только для FREE пользователей - перерегистрация безопасна
        logger.business("🔄 FREE пользователь - перерегистрация безопасна")
        Task { @MainActor in
            await SubscriptionManager.shared.performDeviceRegistration()
        }
        return .silentRetry
    }
```

**Защита от рекурсии:**
- ✅ Используется `Task { @MainActor in }` (из BUILD 103-104)
- ✅ Выполнение на main thread
- ✅ Проверка уровня подписки перед перерегистрацией
- ✅ Защита от бесконечных циклов через счетчик попыток (шаг 2.3)

#### Шаг 2.2: Добавить метод восстановления подписки с сервера

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `restoreSubscriptionFromServer()`

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
    APIService.shared.getSubscriptionStatus { [weak self] result in
        Task { @MainActor [weak self] in
            guard let self = self else { return }
            
            switch result {
            case .success(let status):
                // ✅ Восстанавливаем подписку из ответа сервера
                logger.business("✅ Подписка восстановлена: \(status.level)")
                await self.updateSubscriptionStatus(status)
                
                // ✅ Обновляем токен с правильной подпиской
                if let newToken = await self.refreshTokenWithSubscription(status) {
                    await self.storeToken(newToken)
                    logger.business("✅ Токен обновлен с правильной подпиской")
                }
                
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

#### Шаг 2.3: Добавить защиту от бесконечных циклов в SubscriptionManager

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `performDeviceRegistration()`

**Код:**
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
        
        // Обработка ошибок (существующий код)
        // ...
    }
}
```

**Защита от рекурсии:**
- ✅ NSLock для thread-safety (из BUILD 100-114)
- ✅ Счетчик попыток с ограничением
- ✅ Сброс счетчика при успехе
- ✅ Логирование для диагностики

#### Шаг 2.3: Добавить задержку между попытками (опционально)

**Код:**
```swift
// ✅ BUILD 122: Задержка между попытками (опционально)
if registrationAttempts > 1 {
    let delay = Double(registrationAttempts) * 1.0  // 1s, 2s, 3s
    try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
}
```

---

### ЭТАП 3: ПРОВЕРКА СИНХРОНИЗАЦИИ ПРИ ИНИЦИАЛИЗАЦИИ (РЕКОМЕНДУЕТСЯ)

**Приоритет:** 🟢 РЕКОМЕНДУЕТСЯ  
**Время:** 5 минут  
**Риск:** Низкий

#### Шаг 3.1: Добавить проверку синхронизации в initializeOnAppStart()

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `initializeOnAppStart()`

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

**Защита от рекурсии:**
- ✅ Проверка выполняется один раз при инициализации
- ✅ Не вызывает UserDefaults напрямую
- ✅ Безопасно для main thread

---

### ЭТАП 4: ДОБАВЛЕНИЕ REFRESH TOKEN ДЛЯ DEVICE TOKENS (СЕРВЕР + КЛИЕНТ)

**Приоритет:** 🟡 ВАЖНО  
**Время:** 60 минут (30 сервер + 30 клиент)  
**Риск:** Средний (требует изменений на сервере)

#### Шаг 4.1: Изменить серверный endpoint register-device

**Файл:** `app/routers/auth_router.py` (или `device_endpoints.py`)  
**Метод:** `register_device_anonymously()`

**Текущий код:**
```python
@router.post("/register-device", response_model=JWTDeviceRegisterResponse)
async def register_device_anonymously(...):
    # ... существующий код ...
    
    access_token = create_access_token(token_data)
    
    # ❌ НЕТ refresh_token!
    response = JWTDeviceRegisterResponse(
        token=access_token,
        deviceId=request.deviceId,
        expiresAt=datetime.utcnow() + timedelta(hours=24),
        subscription=SubscriptionStatus(**subscription_data)
    )
    
    return response
```

**Новый код:**
```python
@router.post("/register-device", response_model=JWTDeviceRegisterResponse)
async def register_device_anonymously(...):
    # ... существующий код ...
    
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
    
    return response
```

**Проверка:**
- ✅ Refresh token создается с типом "device_refresh"
- ✅ Срок действия: 30 дней
- ✅ Используется та же функция `create_refresh_token()`

#### Шаг 4.2: Обновить модель ответа на сервере

**Файл:** `device_endpoints.py` (или соответствующий файл с моделями)

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
- ✅ `refresh_token` опциональный (для обратной совместимости)
- ✅ Если сервер не вернет refresh_token → клиент продолжит работать

#### Шаг 4.3: Обновить модель ответа на клиенте

**Файл:** `Core/Models/SubscriptionModels.swift`

**Текущий код:**
```swift
struct JWTDeviceRegisterResponse: Codable {
    let token: String
    let deviceId: String
    let expiresAt: String
    let registeredAt: String
    let subscription: DeviceRegistrationSubscription
    // ❌ НЕТ refresh_token!
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
- ✅ `refreshToken` опциональный
- ✅ Правильный маппинг snake_case → camelCase

#### Шаг 4.4: Сохранить refresh token в клиенте

**Файл:** `Core/Managers/SubscriptionManager.swift`  
**Метод:** `registerDeviceAnonymously()`

**Код:**
```swift
// ✅ BUILD 122: Сохранение refresh token для device tokens
if let refreshToken = response.refreshToken {
    KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
    logger.business("✅ Refresh token сохранен в Keychain для device token")
} else {
    logger.business("⚠️ Refresh token не получен от сервера (обратная совместимость)")
}
```

**Защита от рекурсии:**
- ✅ Сохранение в Keychain (асинхронно, не вызывает UserDefaults)
- ✅ Логирование только в DEBUG режиме

#### Шаг 4.5: Обновить логику refresh token для device tokens

**Файл:** `Core/Security/JWTTokenManager.swift`  
**Метод:** `refreshTokenIfNeeded()`

**Текущий код:**
```swift
func refreshTokenIfNeeded() async -> Bool {
    // ... проверка токена ...
    
    // Получаем refresh token
    guard let refreshToken = keychainManager.loadString(forKey: .refreshToken) else {
        print("❌ JWT: Refresh token не найден в Keychain")
        return false  // ❌ Не обновляется, но и не перерегистрируется
    }
    
    // ... обновление токена ...
}
```

**Новый код:**
```swift
func refreshTokenIfNeeded() async -> Bool {
    // ... проверка токена ...
    
    // Получаем refresh token
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
    
    // ... обновление токена через /api/auth/refresh ...
}
```

**Защита от рекурсии:**
- ✅ Проверка типа токена перед перерегистрацией
- ✅ Используется существующий метод `performDeviceRegistration()` с защитой от циклов
- ✅ Логирование только в DEBUG режиме

#### Шаг 4.6: Обновить endpoint /api/auth/refresh для device tokens

**Файл:** `app/routers/auth_router.py`  
**Метод:** `refresh_token()`

**Текущий код:**
```python
@router.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    # ... декодирование refresh token ...
    
    # Проверяем тип токена
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена"
        )
    
    # ... создание новых токенов ...
}
```

**Новый код:**
```python
@router.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    # ... декодирование refresh token ...
    
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
- ✅ Поддержка типа "device_refresh"
- ✅ Использование "sub" для device tokens
- ✅ Сохранение device_id в новом токене
- ✅ Создание нового refresh token для device tokens

---

## 🛡️ ЗАЩИТА ОТ РЕКУРСИИ (ИЗ BUILD 77-114)

### Принципы, которые нужно соблюдать:

#### 1. Асинхронный разрыв для UserDefaults
```swift
// ✅ ПРАВИЛЬНО:
Task { @MainActor in
    UserDefaults.standard.set(value, forKey: "key")
}

// ❌ НЕПРАВИЛЬНО:
UserDefaults.standard.set(value, forKey: "key")  // Синхронно
```

#### 2. @MainActor для UI операций
```swift
// ✅ ПРАВИЛЬНО:
Task { @MainActor in
    await SubscriptionManager.shared.performDeviceRegistration()
}

// ❌ НЕПРАВИЛЬНО:
Task {
    await MainActor.run {
        // ...
    }
}
```

#### 3. NSLock для защиты словарей
```swift
// ✅ ПРАВИЛЬНО:
private let lock = NSLock()

func someMethod() {
    lock.lock()
    defer { lock.unlock() }
    // Работа с общими данными
}
```

#### 4. Глобальные флаги с NSLock для защиты от рекурсии
```swift
// ✅ ПРАВИЛЬНО:
private var isUpdatingGlobal: Bool = false
private let updateLock = NSLock()

func update() async {
    updateLock.lock()
    guard !isUpdatingGlobal else {
        updateLock.unlock()
        return
    }
    isUpdatingGlobal = true
    updateLock.unlock()
    
    defer {
        updateLock.lock()
        isUpdatingGlobal = false
        updateLock.unlock()
    }
    // ...
}
```

#### 5. Тихий старт (Silent Startup)
```swift
// ✅ ПРАВИЛЬНО:
// Никаких логов в init()
// Никаких тяжелых операций в init()

// ❌ НЕПРАВИЛЬНО:
init() {
    logger.business("Initializing...")  // ❌ Логи в init()
    UserDefaults.standard.set(...)  // ❌ UserDefaults в init()
}
```

#### 6. Изоляция диагностики
```swift
// ✅ ПРАВИЛЬНО:
// Логгер не вызывает аналитику
// Аналитика не вызывает логгер
// Используется только системный print для диагностики

// ❌ НЕПРАВИЛЬНО:
logger.business("Event") {
    analytics.trackEvent(...)  // ❌ Логгер вызывает аналитику
}
```

---

## 📋 ЧЕКЛИСТ РЕАЛИЗАЦИИ

### ЭТАП 1: Восстановление токена (КРИТИЧНО)
- [ ] Добавить восстановление в `NetworkManager.get()`
- [ ] Добавить восстановление в `NetworkManager.post()`
- [ ] Добавить восстановление в `NetworkManager.put()`
- [ ] Добавить восстановление в `NetworkManager.patch()`
- [ ] Добавить восстановление в `NetworkManager.delete()`
- [ ] Проверить логирование (только DEBUG)
- [ ] Проверить отсутствие рекурсии

### ЭТАП 2: Умная обработка 403 с защитой подписки (КРИТИЧНО!)
- [ ] Изменить обработку 403 в `JWTErrorRecovery.analyzeNetworkError()` (проверка уровня подписки)
- [ ] Добавить метод `restoreSubscriptionFromServer()` в `SubscriptionManager`
- [ ] Добавить метод `refreshTokenWithSubscription()` в `SubscriptionManager`
- [ ] Добавить счетчик попыток в `SubscriptionManager`
- [ ] Добавить NSLock для защиты счетчика
- [ ] Добавить логирование попыток
- [ ] Добавить сброс счетчика при успехе
- [ ] Проверить защиту от бесконечных циклов
- [ ] Проверить использование `Task { @MainActor in }`
- [ ] **КРИТИЧНО:** Протестировать сохранение триала при 403
- [ ] **КРИТИЧНО:** Протестировать сохранение Premium подписки при 403

### ЭТАП 3: Проверка синхронизации (РЕКОМЕНДУЕТСЯ)
- [ ] Добавить проверку в `initializeOnAppStart()`
- [ ] Проверить отсутствие рекурсии
- [ ] Проверить логирование

### ЭТАП 4: Refresh token для device tokens (СЕРВЕР + КЛИЕНТ)
- [ ] **СЕРВЕР:**
  - [ ] Изменить `register_device_anonymously()` для создания refresh token
  - [ ] Обновить модель `JWTDeviceRegisterResponse` (добавить `refresh_token`)
  - [ ] Обновить `refresh_token()` для поддержки `device_refresh`
  - [ ] Проверить обратную совместимость
- [ ] **КЛИЕНТ:**
  - [ ] Обновить модель `JWTDeviceRegisterResponse` (добавить `refreshToken`)
  - [ ] Сохранить refresh token в `registerDeviceAnonymously()`
  - [ ] Обновить `refreshTokenIfNeeded()` для device tokens
  - [ ] Проверить обратную совместимость

---

## 🧪 ТЕСТИРОВАНИЕ

### Тест 1: Восстановление токена
```
1. Сохранить токен в SubscriptionManager
2. Удалить токен из AppConfig
3. Вызвать API запрос
4. Проверить: токен восстановлен, запрос успешен
```

### Тест 2: Умная обработка 403 (FREE пользователь)
```
1. FREE пользователь отправляет запрос с истекшим токеном
2. Получить 403 ошибку
3. Проверить: автоматическая перерегистрация выполнена
4. Проверить: запрос повторен с новым токеном
5. Проверить: запрос успешен
6. Проверить: подписка осталась FREE
```

### Тест 2.1: Умная обработка 403 (TRIAL пользователь)
```
1. TRIAL пользователь (день 5 из 14) отправляет запрос с истекшим токеном
2. Получить 403 ошибку
3. Проверить: НЕ произошла перерегистрация
4. Проверить: использован refresh token или восстановление с сервера
5. Проверить: триал сохранен (день 5 из 14)
6. Проверить: запрос успешен
```

### Тест 2.2: Умная обработка 403 (Premium пользователь)
```
1. Premium пользователь отправляет запрос с истекшим токеном
2. Получить 403 ошибку
3. Проверить: НЕ произошла перерегистрация
4. Проверить: использован refresh token или восстановление с сервера
5. Проверить: Premium подписка сохранена
6. Проверить: запрос успешен
```

### Тест 3: Защита от бесконечных циклов
```
1. Симулировать 3 неудачные попытки перерегистрации
2. Проверить: после 3 попыток перерегистрация прекращена
3. Проверить: ошибка показана пользователю
```

### Тест 4: Refresh token для device tokens
```
1. Зарегистрировать устройство
2. Проверить: refresh token сохранен в Keychain
3. Дождаться истечения access token
4. Проверить: токен обновлен через refresh token
5. Проверить: новый refresh token сохранен
```

### Тест 5: Обратная совместимость
```
1. Подключиться к старому серверу (без refresh_token)
2. Проверить: приложение работает
3. Проверить: перерегистрация работает как fallback
```

---

## 📊 ОЦЕНКА РИСКОВ

### Низкий риск:
- ✅ Восстановление токена (только чтение из памяти)
- ✅ Проверка синхронизации (один раз при инициализации)

### Высокий риск:
- ⚠️ **Автоматическая перерегистрация (КРИТИЧНО!)** - может потерять подписку
  - ✅ **РЕШЕНИЕ:** Проверка уровня подписки перед перерегистрацией
  - ✅ **РЕШЕНИЕ:** Восстановление подписки с сервера для платных пользователей

### Средний риск:
- ⚠️ Refresh token для device tokens (требует изменений на сервере)

### Меры предосторожности:
- ✅ Защита от бесконечных циклов (счетчик попыток)
- ✅ NSLock для thread-safety
- ✅ Обратная совместимость (опциональные поля)
- ✅ Логирование для диагностики
- ✅ Тестирование перед деплоем

---

## 🚀 ПОРЯДОК ВЫПОЛНЕНИЯ

### Фаза 1: Быстрые исправления (30 минут)
1. ✅ ЭТАП 1: Восстановление токена (15 минут)
2. ✅ ЭТАП 3: Проверка синхронизации (5 минут)
3. ✅ Тестирование (10 минут)

### Фаза 2: Умная обработка 403 с защитой подписки (45 минут)
1. ✅ ЭТАП 2: Умная обработка 403 (45 минут)
   - Изменить обработку 403 (проверка уровня подписки)
   - Добавить метод восстановления подписки
   - Добавить защиту от циклов
2. ✅ Тестирование (15 минут)
   - Тест FREE пользователя
   - Тест TRIAL пользователя (критично!)
   - Тест Premium пользователя (критично!)

### Фаза 3: Refresh token (60 минут)
1. ✅ ЭТАП 4: Refresh token для device tokens (60 минут)
2. ✅ Тестирование (20 минут)
3. ✅ Деплой на сервер (10 минут)

**Общее время:** ~2.75 часа (добавлено время на защиту подписки)

---

## 📝 ПРИМЕЧАНИЯ

### Важные моменты:
1. **Обратная совместимость:** Все изменения должны быть обратно совместимы
2. **Защита от рекурсии:** Соблюдать все принципы из BUILD 77-114
3. **Логирование:** Только в DEBUG режиме для критических мест
4. **Тестирование:** Обязательно протестировать все сценарии перед деплоем

### После реализации:
1. ✅ Обновить документацию
2. ✅ Создать commit с описанием изменений
3. ✅ Отправить в GitHub
4. ✅ Деплой на сервер (для refresh token)

---

**Дата:** 16 марта 2026  
**Build:** 122  
**Статус:** План готов к реализации
