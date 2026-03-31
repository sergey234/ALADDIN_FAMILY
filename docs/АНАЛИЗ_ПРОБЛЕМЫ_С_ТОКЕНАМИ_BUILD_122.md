# 🔍 ПОЛНЫЙ АНАЛИЗ ПРОБЛЕМЫ С ТОКЕНАМИ - BUILD 122

**Дата:** 16 марта 2026  
**Проблема:** `/api/family/stats` возвращает 403 (требуется токен)  
**Вопрос:** Где токены? Почему их нет? Почему не обновляются?

---

## 📋 СОДЕРЖАНИЕ

1. [Где хранятся токены](#где-хранятся-токены)
2. [Как получаются токены](#как-получаются-токены)
3. [Как обновляются токены](#как-обновляются-токены)
4. [Где используются токены](#где-используются-токены)
5. [Почему токены могут отсутствовать](#почему-токены-могут-отсутствовать)
6. [Проблемы в текущей реализации](#проблемы-в-текущей-реализации)
7. [Решения](#решения)

---

## 🔐 ГДЕ ХРАНЯТСЯ ТОКЕНЫ

### 1. **Keychain (основное хранилище)**
```swift
// Core/Security/KeychainManager.swift
KeychainManager.shared.save(token, forKey: .authToken)
KeychainManager.shared.loadString(forKey: .authToken)
```

**Ключи:**
- `.authToken` - основной токен авторизации
- `.refreshToken` - токен для обновления

### 2. **AppConfig (для NetworkManager)**
```swift
// Core/Config/AppConfig.swift
static var authToken: String? {
    get {
        // Сначала Keychain
        if let keychainToken = KeychainManager.shared.loadString(forKey: .authToken) {
            return keychainToken
        }
        // Fallback на UserDefaults
        return UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.authToken)
    }
    set {
        if let token = newValue {
            KeychainManager.shared.save(token, forKey: .authToken)
            UserDefaults.standard.set(token, forKey: AppConfig.UserDefaultsKeys.authToken)
        } else {
            KeychainManager.shared.delete(forKey: .authToken)
            UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
        }
    }
}
```

### 3. **SubscriptionManager (в памяти)**
```swift
// Core/Managers/SubscriptionManager.swift
@Published private(set) var currentToken: JWTToken?
```

**Хранилище:**
- Keychain (персистентное)
- `currentToken` (в памяти)

---

## 📱 КАК ПОЛУЧАЮТСЯ ТОКЕНЫ

### 1. **Регистрация устройства (при первом запуске)**

**Цепочка вызовов:**
```
ALADDINApp.swift (onAppear)
  ↓
SubscriptionManager.initializeOnAppStart()
  ↓
TokenValidator.validateCurrentToken()
  ↓
performDeviceRegistration() (если токена нет)
  ↓
registerDeviceAnonymously()
  ↓
APIService.registerDeviceAnonymously()
  ↓
POST /api/auth/register-device
  ↓
storeToken(jwtToken) → AppConfig.authToken = token.token
```

**Код:**
```swift
// Core/Managers/SubscriptionManager.swift:263
private func performDeviceRegistration() async {
    do {
        try await registerDeviceAnonymously()
        // Токен сохраняется в storeToken()
    } catch {
        // Обработка ошибок
    }
}

// Core/Managers/SubscriptionManager.swift:683
func registerDeviceAnonymously() async throws -> JWTToken {
    let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
    let request = DeviceRegisterRequest(deviceId: deviceId, deviceType: "ios")
    
    let response = try await withCheckedThrowingContinuation { continuation in
        APIService.shared.registerDeviceAnonymously(request: request) { result in
            // Обработка ответа
        }
    }
    
    // Сохранение токена
    await storeToken(jwtToken)
    return jwtToken
}
```

### 2. **Загрузка из Keychain (при перезапуске)**

```swift
// Core/Managers/SubscriptionManager.swift:960
private func loadPersistedData() {
    if let tokenData = loadFromKeychain(key: tokenKey),
       let token = try? JSONDecoder().decode(JWTToken.self, from: tokenData) {
        currentToken = token
        // ✅ КРИТИЧНО: Также восстанавливаем токен в AppConfig
        AppConfig.authToken = token.token
    }
}
```

---

## 🔄 КАК ОБНОВЛЯЮТСЯ ТОКЕНЫ

### 1. **Автоматическое обновление (JWTTokenManager)**

```swift
// Core/Security/JWTTokenManager.swift:121
func refreshTokenIfNeeded() async -> Bool {
    guard let accessToken = keychainManager.loadString(forKey: .authToken) else {
        return false
    }
    
    if !isTokenExpired(accessToken) {
        return false // Токен валиден
    }
    
    // Токен истёк - обновляем через refresh token
    guard let refreshToken = keychainManager.loadString(forKey: .refreshToken) else {
        return false
    }
    
    return await directRefreshTokenRequest(refreshToken: refreshToken)
}
```

**Проблема:** Refresh token может отсутствовать для device tokens!

### 2. **Обновление через NetworkManager**

```swift
// Core/Network/NetworkManager.swift:230
func get<T: Decodable>(...) {
    Task {
        _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
        // Продолжаем запрос
    }
}
```

### 3. **Перерегистрация устройства (если refresh token отсутствует)**

```swift
// Core/Managers/SubscriptionManager.swift:328
private func refreshTokenSilently() async {
    // Пока что просто перерегистрируем устройство
    await performDeviceRegistration()
}
```

---

## 🌐 ГДЕ ИСПОЛЬЗУЮТСЯ ТОКЕНЫ

### 1. **NetworkManager (добавление заголовка Authorization)**

```swift
// Core/Network/NetworkManager.swift:246
if requiresAuth {
    guard let token = AppConfig.authToken else {
        completion(.failure(NetworkError.unauthorized("Токен авторизации отсутствует")))
        return
    }
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
}
```

### 2. **API Endpoints, требующие авторизации**

**Пример: `/api/family/stats`**
```swift
// ViewModels/MainViewModel.swift:215
apiService.getFamilyStats { result in
    // Запрос требует токен
}

// Core/Network/APIService.swift
func getFamilyStats(completion: @escaping (Result<FamilyStatsResponse, Error>) -> Void) {
    networkManager.get(endpoint: AppConfig.Endpoint.familyStats, completion: completion)
    // requiresAuth: true (по умолчанию)
}
```

**Сервер:**
```python
# app/routers/family.py:179
@router.get("/stats", response_model=FamilyStatsResponse)
async def get_family_stats(
    current_user: dict = Depends(get_current_user)  # ✅ Требуется токен
):
    user_id = current_user["id"]
    # ...
```

---

## ❌ ПОЧЕМУ ТОКЕНЫ МОГУТ ОТСУТСТВОВАТЬ

### 1. **Токен не был получен при регистрации**

**Причины:**
- Ошибка сети при регистрации
- Ошибка сервера (500, 503)
- Ошибка валидации (422)
- Таймаут запроса

**Код:**
```swift
// Core/Managers/SubscriptionManager.swift:281
catch {
    // Ошибка регистрации - токен не сохранён
    // Приложение может продолжить работу без токена
}
```

### 2. **Токен был удалён**

**Причины:**
- `clearToken()` был вызван
- Ошибка при сохранении в Keychain
- Проблемы с Keychain (iOS security)

**Код:**
```swift
// Core/Managers/SubscriptionManager.swift:348
func clearToken() async {
    KeychainManager.shared.delete(forKey: .authToken)
    KeychainManager.shared.delete(forKey: .refreshToken)
    currentToken = nil
    AppConfig.authToken = nil
}
```

### 3. **Токен не синхронизирован между хранилищами**

**Проблема:**
- Токен есть в `SubscriptionManager.currentToken`
- Но отсутствует в `AppConfig.authToken`
- NetworkManager использует `AppConfig.authToken`

**Код:**
```swift
// Проблема: storeToken() вызывается, но AppConfig.authToken может не обновиться
func storeToken(_ token: JWTToken) async {
    currentToken = token
    AppConfig.authToken = token.token  // ✅ Должно работать, но может быть race condition
}
```

### 4. **Токен истёк и не обновляется**

**Причины:**
- Refresh token отсутствует (для device tokens)
- Ошибка при обновлении токена
- Сетевая ошибка при refresh

**Код:**
```swift
// Core/Security/JWTTokenManager.swift:142
guard let refreshToken = keychainManager.loadString(forKey: .refreshToken) else {
    print("❌ JWT: Refresh token не найден в Keychain")
    return false  // ❌ ПРОБЛЕМА: Не обновляется, но и не перерегистрируется
}
```

### 5. **Race condition при инициализации**

**Проблема:**
- `initializeOnAppStart()` выполняется асинхронно
- Запросы могут начаться до завершения регистрации
- `AppConfig.authToken` ещё не установлен

---

## 🐛 ПРОБЛЕМЫ В ТЕКУЩЕЙ РЕАЛИЗАЦИИ

### 1. **Device tokens не имеют refresh token**

**Проблема:**
- Device registration возвращает только access token
- Refresh token не сохраняется
- При истечении токена обновление невозможно

**Решение:** Нужно либо:
- Добавить refresh token для device tokens
- Или автоматически перерегистрировать устройство при истечении

### 2. **Нет синхронизации между SubscriptionManager и AppConfig**

**Проблема:**
- `SubscriptionManager.currentToken` может быть установлен
- Но `AppConfig.authToken` может быть nil
- NetworkManager не может использовать токен

**Решение:** Гарантировать синхронизацию:
```swift
func storeToken(_ token: JWTToken) async {
    currentToken = token
    AppConfig.authToken = token.token  // ✅ Уже есть, но нужно проверить
    // Добавить проверку после установки
    assert(AppConfig.authToken != nil, "Токен должен быть установлен в AppConfig")
}
```

### 3. **Нет проверки токена перед запросами**

**Проблема:**
- Запросы могут отправляться без токена
- Ошибка 403 возвращается, но не обрабатывается
- Нет автоматической перерегистрации

**Решение:** Добавить проверку:
```swift
func get<T: Decodable>(...) {
    // Проверяем токен перед запросом
    if requiresAuth {
        if AppConfig.authToken == nil {
            // Пытаемся восстановить из SubscriptionManager
            if let token = SubscriptionManager.shared.currentToken {
                AppConfig.authToken = token.token
            } else {
                // Токена нет - нужно зарегистрировать устройство
                completion(.failure(NetworkError.unauthorized("Требуется регистрация устройства")))
                return
            }
        }
    }
}
```

### 4. **Нет обработки 403 ошибки с перерегистрацией**

**Проблема:**
- При 403 ошибке нет автоматической перерегистрации
- Пользователь видит ошибку, но не знает что делать

**Решение:** Добавить обработку:
```swift
func performRequest(...) {
    // При 403 ошибке - пытаемся перерегистрировать устройство
    if httpResponse.statusCode == 403 {
        Task {
            await SubscriptionManager.shared.performDeviceRegistration()
            // Повторяем запрос
        }
    }
}
```

---

## ✅ РЕШЕНИЯ

### 1. **Гарантировать синхронизацию токенов**

```swift
// Core/Managers/SubscriptionManager.swift
func storeToken(_ token: JWTToken) async {
    currentToken = token
    AppConfig.authToken = token.token
    
    // ✅ ДОБАВИТЬ: Проверка после установки
    if AppConfig.authToken == nil {
        logger.error("❌ КРИТИЧНО: Токен не установлен в AppConfig после storeToken()")
        // Повторная попытка
        AppConfig.authToken = token.token
    }
    
    // Сохранение в Keychain
    if let data = try? JSONEncoder().encode(token) {
        saveToKeychain(data: data, key: tokenKey)
    }
}
```

### 2. **Восстановление токена из SubscriptionManager в NetworkManager**

```swift
// Core/Network/NetworkManager.swift
func get<T: Decodable>(...) {
    if requiresAuth {
        // ✅ ДОБАВИТЬ: Восстановление токена из SubscriptionManager
        if AppConfig.authToken == nil {
            if let token = SubscriptionManager.shared.currentToken {
                AppConfig.authToken = token.token
                logger.business("✅ Токен восстановлен из SubscriptionManager")
            }
        }
        
        guard let token = AppConfig.authToken else {
            logger.error("❌ Токен отсутствует - требуется регистрация устройства")
            completion(.failure(NetworkError.unauthorized("Токен авторизации отсутствует")))
            return
        }
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    }
}
```

### 3. **Автоматическая перерегистрация при 403**

```swift
// Core/Network/NetworkManager.swift
func performRequest(...) {
    // ✅ ДОБАВИТЬ: Обработка 403 с перерегистрацией
    if httpResponse.statusCode == 403 {
        logger.business("🔄 Обнаружена ошибка 403 - пытаемся перерегистрировать устройство")
        Task {
            await SubscriptionManager.shared.performDeviceRegistration()
            // Повторяем запрос (опционально)
        }
    }
}
```

### 4. **Проверка токена при инициализации**

```swift
// Core/Managers/SubscriptionManager.swift
func initializeOnAppStart() async {
    // ✅ ДОБАВИТЬ: Проверка синхронизации после загрузки
    loadPersistedData()
    
    // Проверяем, что токен синхронизирован
    if let token = currentToken, AppConfig.authToken == nil {
        AppConfig.authToken = token.token
        logger.business("✅ Токен синхронизирован с AppConfig при инициализации")
    }
}
```

### 5. **Добавить refresh token для device tokens**

**На сервере:**
```python
# app/routers/auth_router.py
@router.post("/register-device")
async def register_device(...):
    # ✅ ДОБАВИТЬ: Создание refresh token
    refresh_token = create_refresh_token(token_data)
    
    return JWTDeviceRegisterResponse(
        token=access_token,
        refresh_token=refresh_token,  # ✅ ДОБАВИТЬ
        # ...
    )
```

**В клиенте:**
```swift
// Core/Managers/SubscriptionManager.swift
func registerDeviceAnonymously() async throws -> JWTToken {
    // ✅ ДОБАВИТЬ: Сохранение refresh token
    if let refreshToken = response.refresh_token {
        KeychainManager.shared.save(refreshToken, forKey: .refreshToken)
    }
}
```

---

## 🎯 ПРИОРИТЕТНЫЕ ИСПРАВЛЕНИЯ

### 1. **КРИТИЧНО: Синхронизация токенов**
- ✅ Гарантировать установку `AppConfig.authToken` при `storeToken()`
- ✅ Восстановление токена из `SubscriptionManager` в `NetworkManager`

### 2. **ВАЖНО: Обработка 403 ошибки**
- ✅ Автоматическая перерегистрация при 403
- ✅ Логирование причины отсутствия токена

### 3. **РЕКОМЕНДУЕТСЯ: Refresh token для device tokens**
- ✅ Добавить refresh token на сервере
- ✅ Сохранять refresh token в клиенте
- ✅ Использовать refresh token для обновления

---

## 📊 ДИАГНОСТИКА

### Проверка наличия токена:

```swift
// Проверка в разных хранилищах
let keychainToken = KeychainManager.shared.loadString(forKey: .authToken)
let appConfigToken = AppConfig.authToken
let subscriptionToken = SubscriptionManager.shared.currentToken?.token

print("Keychain: \(keychainToken != nil ? "✅" : "❌")")
print("AppConfig: \(appConfigToken != nil ? "✅" : "❌")")
print("SubscriptionManager: \(subscriptionToken != nil ? "✅" : "❌")")
```

### Логирование:

```swift
// Добавить логирование при установке токена
func storeToken(_ token: JWTToken) async {
    logger.business("💾 Сохранение токена:")
    logger.business("   - DeviceId: \(token.deviceId)")
    logger.business("   - Token length: \(token.token.count)")
    logger.business("   - AppConfig.authToken до: \(AppConfig.authToken != nil ? "✅" : "❌")")
    
    AppConfig.authToken = token.token
    
    logger.business("   - AppConfig.authToken после: \(AppConfig.authToken != nil ? "✅" : "❌")")
}
```

---

## 📝 ИТОГ

**Основные проблемы:**
1. ❌ Токен может отсутствовать в `AppConfig.authToken`, даже если есть в `SubscriptionManager`
2. ❌ Нет автоматической перерегистрации при 403 ошибке
3. ❌ Device tokens не имеют refresh token
4. ❌ Нет проверки синхронизации токенов

**Решения:**
1. ✅ Гарантировать синхронизацию токенов
2. ✅ Восстановление токена из `SubscriptionManager` в `NetworkManager`
3. ✅ Автоматическая перерегистрация при 403
4. ✅ Добавить refresh token для device tokens

---

**Дата:** 16 марта 2026  
**Build:** 122  
**Статус:** Требуется исправление синхронизации токенов
