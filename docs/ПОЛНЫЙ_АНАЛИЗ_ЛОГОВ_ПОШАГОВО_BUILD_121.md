# 🔍 ПОЛНЫЙ ПОШАГОВЫЙ АНАЛИЗ ЛОГОВ BUILD 121

**Дата анализа:** 2026-03-16  
**Время:** 15:51:02 - 16:03:39  
**Сценарий:** Запуск приложения → Загрузка данных → Переход на Analytics → Ошибка 401

---

## 📊 БЛОК #1: Сетевые запросы к Referral API (15:51:02)

### Логи:
```
[15:51:02.038] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/referral/stats
[15:51:02.044] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/referral/rewards
[15:51:02.056] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/v1/parental-control/stats
[15:51:02.061] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/referral/stats
[15:51:02.066] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/referral/rewards
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Отправка запросов:**
   - `GET /api/referral/stats` - получение статистики реферальной программы
   - `GET /api/referral/rewards` - получение списка наград
   - `GET /api/v1/parental-control/stats` - получение статистики родительского контроля

2. **Получение ответов:**
   - Все запросы вернули `200 OK` ✅
   - Это означает, что токен **работал** в этот момент

**Взаимодействие компонентов:**
```
NetworkManager → APIService → Server
     ↓
  Headers: Authorization: Bearer {token}
     ↓
  Server validates token → Returns 200 OK
```

**Вывод:**
- ✅ Токен был валидным в 15:51:02
- ✅ Все API endpoints работали корректно
- ✅ Нет проблем с сетью или авторизацией на этом этапе

---

## 📊 БЛОК #2: Загрузка данных из Keychain (16:02:55.107)

### Логи:
```
[16:02:55.107] [ℹ️] 💾💾💾 SubscriptionManager.loadPersistedData: Начало загрузки данных из Keychain
[16:02:55.116] [✅] ✅ SubscriptionManager.loadPersistedData: Токен загружен из Keychain
   - DeviceId: 8993C837-3B23-41A5-B4D3-E4C346606AE7
   - SubscriptionLevel: free
   - Token length: 636
   - AppConfig.authToken установлен: ✅ да
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Вызов метода:** `SubscriptionManager.loadPersistedData()`
   - Это **private метод**, вызываемый из `init()` SubscriptionManager
   - Вызывается при создании singleton `SubscriptionManager.shared`

2. **Процесс загрузки:**
   ```
   Keychain → JSONDecoder → JWTToken → SubscriptionManager.currentToken
        ↓
   AppConfig.authToken = token.token (синхронизация)
   ```

3. **Результат:**
   - ✅ Токен успешно загружен из Keychain
   - ✅ DeviceId: `8993C837-3B23-41A5-B4D3-E4C346606AE7`
   - ✅ SubscriptionLevel: `free`
   - ✅ Token length: `636` символов
   - ✅ `AppConfig.authToken` установлен

**Взаимодействие компонентов:**
```
SubscriptionManager.init()
    ↓
loadPersistedData()
    ↓
KeychainManager.loadData(forKey: .authToken)
    ↓
JSONDecoder.decode(JWTToken.self, from: data)
    ↓
currentToken = token
AppConfig.authToken = token.token  ← СИНХРОНИЗАЦИЯ
```

**Вывод:**
- ✅ Токен успешно загружен из защищённого хранилища
- ✅ Синхронизация с `AppConfig.authToken` выполнена
- ✅ Всё работает корректно на этом этапе

---

## 📊 БЛОК #3: Инициализация SubscriptionManager (16:02:55.559)

### Логи:
```
[16:02:55.559] [ℹ️] [BUSINESS] 🔒 🔐 SubscriptionManager initialized - Core security component active
[16:02:55.566] [ℹ️] [BUSINESS] 💾 Loading persisted data from Keychain...
[16:02:55.573] [ℹ️] [BUSINESS] 🔑 Token restored from Keychain to AppConfig.authToken
[16:02:55.580] [ℹ️] [BUSINESS] 💾 Persisted data loaded
[16:02:55.586] [ℹ️] [BUSINESS] 💾 Persisted data loading completed
[16:02:55.591] [ℹ️] [BUSINESS] 💾 Token loaded from Keychain: deviceId=8993C837-3B23-41A5-B4D3-E4C346606AE7
[16:02:55.596] [ℹ️] [BUSINESS] 💾 Subscription loaded from Keychain: level=free
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Инициализация SubscriptionManager:**
   - Singleton создаётся при первом обращении: `SubscriptionManager.shared`
   - Выполняется `init()` метод

2. **Загрузка данных:**
   - Токен из Keychain → `currentToken`
   - Подписка из Keychain → `currentSubscription`
   - Trial info из Keychain → `trialStatus`

3. **Синхронизация:**
   - `AppConfig.authToken = token.token` - токен доступен для всех API запросов

**Взаимодействие компонентов:**
```
ALADDINApp.onAppear
    ↓
SubscriptionManager.shared (первое обращение)
    ↓
init() {
    loadPersistedData() {
        Keychain → JWTToken → currentToken
        Keychain → SubscriptionStatus → currentSubscription
        Keychain → TrialInfo → trialStatus
    }
    AppConfig.authToken = currentToken.token
}
```

**Вывод:**
- ✅ SubscriptionManager успешно инициализирован
- ✅ Все данные загружены из Keychain
- ✅ Токен синхронизирован с AppConfig

---

## 📊 БЛОК #4: Настройка Token Health Monitoring (16:02:55.600)

### Логи:
```
[16:02:55.600] [ℹ️] [BUSINESS] 🏥 DEFENSIVE JWT: Setting up proactive token health monitoring
[16:02:55.604] [ℹ️] [BUSINESS] 🏥 DEFENSIVE JWT: TokenHealthMonitor singleton initialized
[16:02:55.608] [ℹ️] [BUSINESS] 👀 DEFENSIVE JWT: Starting proactive token health monitoring
[16:02:55.612] [ℹ️] [BUSINESS] ⏹️ DEFENSIVE JWT: Stopping token health monitoring
[16:02:55.618] [ℹ️] [BUSINESS] ✅ DEFENSIVE JWT: Health monitoring stopped
[16:02:55.624] [ℹ️] [BUSINESS] ✅ DEFENSIVE JWT: Proactive token health monitoring is now ACTIVE
[16:02:55.630] [ℹ️] [BUSINESS] 🔐 SubscriptionManager init completed
[16:02:55.635] [ℹ️] [BUSINESS] ✅ DEFENSIVE JWT: Health monitoring started - checking every 60 seconds
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Настройка мониторинга:**
   - `setupTokenHealthMonitoring()` вызывается из `init()`
   - Создаётся singleton `TokenHealthMonitor.shared`

2. **Запуск мониторинга:**
   - `TokenHealthMonitor.shared.startMonitoring()`
   - Проверка токена каждые 60 секунд

3. **Почему "Stopping" перед "Starting":**
   - Это нормальное поведение - сначала останавливаем старый мониторинг (если был)
   - Потом запускаем новый для текущего токена

**Взаимодействие компонентов:**
```
SubscriptionManager.init()
    ↓
setupTokenHealthMonitoring()
    ↓
TokenHealthMonitor.shared.startMonitoring()
    ↓
Timer (каждые 60 секунд) → проверка токена
    ↓
Если токен истекает → автоматическое обновление
```

**Вывод:**
- ✅ Token Health Monitor успешно настроен
- ✅ Мониторинг запущен (проверка каждые 60 секунд)
- ✅ Автоматическое обновление токена активировано

---

## 📊 БЛОК #5: Инициализация приложения (16:02:55.721)

### Логи:
```
[16:02:55.721] [ℹ️] 🚀 VisualLogger initialized with 17 restored logs
[16:02:55.728] [ℹ️] 🚀 SubscriptionManager.initializeOnAppStart() called
[16:02:55.735] [ℹ️] [BUSINESS] 🚀 SubscriptionManager.initializeOnAppStart() called
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **VisualLogger инициализирован:**
   - Восстановлено 17 логов из предыдущей сессии
   - Это для отладки в DEBUG режиме

2. **Вызов initializeOnAppStart():**
   - Вызывается из `ALADDINApp.onAppear`
   - Это **асинхронный метод**, который выполняет проверку токена

**Взаимодействие компонентов:**
```
ALADDINApp.body {
    NavigationView {
        // ...
    }
    .onAppear {
        Task {
            await SubscriptionManager.shared.initializeOnAppStart()
        }
    }
}
```

**Вывод:**
- ✅ VisualLogger готов к работе
- ✅ Инициализация приложения запущена

---

## 📊 БЛОК #6: Интеллектуальная проверка токена (16:02:55.740)

### Логи:
```
[16:02:55.740] [ℹ️] [BUSINESS] 📊 ИНИЦИАЛИЗАЦИЯ ПОДПИСКИ - ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ
[16:02:55.744] [ℹ️] [BUSINESS] 📱 Устройство: iPhone (15.2)
[16:02:55.748] [ℹ️] [BUSINESS] 🌐 Режим сети: ОНЛАЙН
[16:02:55.753] [ℹ️] [BUSINESS] ⏰ Время запуска: 2026-03-16 12:02:55 +0000
[16:02:55.757] [ℹ️] [BUSINESS] 🚀 DEFENSIVE JWT: Начинаем интеллектуальную проверку токена
[16:02:55.761] [ℹ️] [BUSINESS] 🔍 DEFENSIVE JWT: TokenValidator.validateCurrentToken() called
[16:02:55.766] [ℹ️] [BUSINESS] 📋 DEFENSIVE JWT: Token exists - analyzing structure and validity
[16:02:55.773] [ℹ️] [BUSINESS] ✅ DEFENSIVE JWT: JWT structure is valid
[16:02:55.780] [ℹ️] [BUSINESS] ⏰ DEFENSIVE JWT: Time to expiry: 1418 minutes
[16:02:55.784] [ℹ️] [BUSINESS] ✅ DEFENSIVE JWT: Token is VALID - 23 hours remaining
[16:02:55.788] [ℹ️] [BUSINESS] 🔍 DEFENSIVE JWT: Статус токена: VALID (token OK - using existing)
[16:02:55.794] [ℹ️] [BUSINESS] ✅ DEFENSIVE JWT: Токен валиден - используем существующий
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Сбор информации:**
   - Устройство: iPhone (15.2)
   - Режим сети: ОНЛАЙН
   - Время запуска: 2026-03-16 12:02:55 +0000

2. **Проверка токена через TokenValidator:**
   ```
   TokenValidator.validateCurrentToken()
       ↓
   Проверка существования токена
       ↓
   Проверка структуры JWT (3 части: header.payload.signature)
       ↓
   Проверка exp (время истечения)
       ↓
   Результат: VALID
   ```

3. **Результат проверки:**
   - ✅ Структура JWT валидна
   - ✅ Время до истечения: 1418 минут (23 часа 38 минут)
   - ✅ Токен валиден - используем существующий

**Взаимодействие компонентов:**
```
initializeOnAppStart()
    ↓
TokenValidator.validateCurrentToken()
    ↓
Проверка:
  1. Токен существует? → Да
  2. Структура JWT валидна? → Да
  3. exp не истёк? → Нет (ещё 23 часа)
    ↓
Результат: .valid
    ↓
Используем существующий токен (не регистрируем заново)
```

**Вывод:**
- ✅ Токен валиден по структуре и времени
- ✅ Регистрация устройства не требуется
- ✅ Используем существующий токен

---

## 📊 БЛОК #7: Circuit Breaker и Health Check (16:02:55.799)

### Логи:
```
[16:02:55.799] [ℹ️] [BUSINESS] 🎉 DEFENSIVE JWT: Инициализация завершена успешно
[16:02:55.804] [ℹ️] [BUSINESS] 🔌 DEFENSIVE JWT: JWTCircuitBreaker initialized - CLOSED (normal operation)
[16:02:55.808] [ℹ️] [BUSINESS] 🚨 DEFENSIVE JWT: Emergency reset to CLOSED state
[16:02:55.812] [ℹ️] [BUSINESS] 🔧 DEFENSIVE JWT: Manual state change to closed (testing only)
[16:02:55.819] [ℹ️] [BUSINESS] 📊 JWT EVENT [2026-03-16 12:02:55 +0000]
Device: iPhone (15.2)
Session: 3EBB562A-7F59-48A6-B0A3-25D32BAF1E44
🔌 CIRCUIT BREAKER
New State: CLOSED
Reason: Emergency reset
[16:02:55.826] [ℹ️] [BUSINESS] 📊 JWT Event sent to analytics: circuitBreakerStateChanged(state: "CLOSED", reason: "Emergency reset")
[16:02:55.833] [ℹ️] [BUSINESS] 📊 JWT EVENT [2026-03-16 12:02:55 +0000]
Device: iPhone (15.2)
Session: 3EBB562A-7F59-48A6-B0A3-25D32BAF1E44
🏥 HEALTH CHECK
Token Exists: true
Next Check: 60 secondsTime to Expiry: 1418 minutes
[16:02:55.839] [ℹ️] [BUSINESS] 📊 JWT Event sent to analytics: healthCheckPerformed(tokenExists: true, timeToExpiry: Optional(85096.76259291172), nextCheckIn: 60.0)
[16:02:55.846] [ℹ️] [BUSINESS] 🔒 🚀 SubscriptionManager: App start initialization completed
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Circuit Breaker:**
   - Состояние: `CLOSED` (нормальная работа)
   - Причина: Emergency reset (сброс при старте приложения)
   - Это защитный механизм от каскадных ошибок

2. **Health Check:**
   - Token Exists: `true` ✅
   - Next Check: `60 seconds` (следующая проверка через минуту)
   - Time to Expiry: `1418 minutes` (23 часа 38 минут)

3. **Отправка событий в Analytics:**
   - `circuitBreakerStateChanged` - изменение состояния Circuit Breaker
   - `healthCheckPerformed` - выполнение проверки здоровья токена

**Взаимодействие компонентов:**
```
initializeOnAppStart()
    ↓
JWTCircuitBreaker.shared.emergencyReset()
    ↓
Состояние: CLOSED (нормальная работа)
    ↓
JWTEventLogger.logEvent(.healthCheckPerformed(...))
    ↓
Отправка в Analytics для отслеживания
```

**Вывод:**
- ✅ Circuit Breaker в нормальном состоянии (CLOSED)
- ✅ Health Check выполнен успешно
- ✅ События отправлены в Analytics

---

## 📊 БЛОК #8: Загрузка профиля пользователя (16:02:57.972)

### Логи:
```
[16:02:57.972] [ℹ️] [BUSINESS] 👤 Fetching user profile
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Загрузка профиля:**
   - Вызывается `UserProfileManager.shared.loadProfile()`
   - Запрос к `/api/user/profile` с токеном авторизации

**Взаимодействие компонентов:**
```
UserProfileManager.shared (первое обращение)
    ↓
loadProfile()
    ↓
APIService.getUserProfile()
    ↓
NetworkManager.get(endpoint: "/api/user/profile")
    ↓
Headers: Authorization: Bearer {token}
    ↓
Server → User Profile Data
```

**Вывод:**
- ✅ Загрузка профиля запущена
- ✅ Использует токен из AppConfig.authToken

---

## 📊 БЛОК #9: Переход на главный экран (16:03:17.403)

### Логи:
```
[16:03:17.403] [ℹ️] [UI] 🧭 Navigation: Обучение → Главная
[16:03:17.904] [ℹ️] [BUSINESS] Initializing AntivirusManager
[16:03:17.908] [ℹ️] [BUSINESS] [Antivirus] AntivirusManager инициализирован
[16:03:17.948] [ℹ️] [BUSINESS] 🔍 MainScreen: Проверка ID пользователя
[16:03:17.951] [ℹ️] [BUSINESS]    - your_member_id = MEM_5EABC39B
[16:03:17.955] [ℹ️] [BUSINESS] ✅ MainScreen: ID найден и будет отображен: MEM_5EABC39B
[16:03:18.070] [ℹ️] [BUSINESS] Initializing PerformanceMonitor with FPS and memory monitoring
[16:03:18.075] [ℹ️] [PERFORMANCE] PerformanceMonitor initialized, monitoring started
[16:03:18.080] [ℹ️] [BUSINESS] Started monitoring screen load time for: MainDashboard
[16:03:18.084] [ℹ️] [PERFORMANCE] Screen load started: 'MainDashboard'
[16:03:18.197] [ℹ️] [PERFORMANCE] Screen 'MainDashboard' loaded in 0.143 sec
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Навигация:**
   - Переход с экрана "Обучение" на "Главная"
   - Используется `NavigationManager`

2. **Инициализация компонентов:**
   - `AntivirusManager` - менеджер антивируса
   - `PerformanceMonitor` - мониторинг производительности

3. **Проверка ID пользователя:**
   - `your_member_id = MEM_5EABC39B`
   - ID найден в UserDefaults и будет отображен

4. **Мониторинг производительности:**
   - Экран 'MainDashboard' загружен за 0.143 секунды ✅

**Взаимодействие компонентов:**
```
NavigationManager.navigateTo(.main)
    ↓
MainScreen.onAppear {
    AntivirusManager.shared.initialize()
    PerformanceMonitor.shared.startScreenLoad("MainDashboard")
    checkUserMemberId()
}
    ↓
PerformanceMonitor.shared.endScreenLoad("MainDashboard")
```

**Вывод:**
- ✅ Навигация выполнена успешно
- ✅ Все компоненты инициализированы
- ✅ Производительность хорошая (0.143 сек)

---

## 🚨 БЛОК #10: Переход на Analytics - ПРОБЛЕМА! (16:03:36.989)

### Логи:
```
[16:03:36.989] [ℹ️] [UI] 🧭 Navigation: Главная → Аналитика
[16:03:37.641] [ℹ️] [UI] 📱 Screen loaded: AnalyticsScreen
[16:03:37.839] [ℹ️] 🔍 AnalyticsViewModel: Диагностика токена
   - AppConfig.authToken: ❌ нет
   - Keychain token: ❌ нет
   - SubscriptionManager token: ✅ есть
[16:03:37.846] [🔍] 🔍 TokenManager: Проверка доступности токена
[16:03:37.853] [⚠️] ⚠️ TokenManager: Токен не найден в AppConfig, проверяем SubscriptionManager...
[16:03:37.857] [✅] ✅ TokenManager: Токен найден в SubscriptionManager, восстановлен в AppConfig (длина: 636, deviceId: 8993C837-3B23-41A5-B4D3-E4C346606AE7)
[16:03:37.861] [✅] ✅ AnalyticsViewModel: Токен доступен, начинаем загрузку
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Навигация:**
   - Переход с "Главная" на "Аналитика"
   - Экран AnalyticsScreen загружен

2. **Диагностика токена в AnalyticsViewModel:**
   ```
   AppConfig.authToken: ❌ нет
   Keychain token: ❌ нет
   SubscriptionManager token: ✅ есть
   ```
   - **Проблема:** Токен потерян из `AppConfig.authToken` и Keychain
   - **Но:** Токен остался в `SubscriptionManager.currentToken` (в памяти)

3. **Восстановление токена через TokenManager:**
   ```
   TokenManager.checkTokenAvailability()
       ↓
   Проверка AppConfig.authToken → nil
       ↓
   Проверка SubscriptionManager.currentToken → ✅ есть
       ↓
   AppConfig.authToken = currentToken.token (восстановление)
       ↓
   Токен доступен для API запросов
   ```

**Взаимодействие компонентов:**
```
AnalyticsScreen.onAppear
    ↓
AnalyticsViewModel.load()
    ↓
Диагностика токена:
   AppConfig.authToken? → nil ❌
   Keychain? → nil ❌
   SubscriptionManager.currentToken? → ✅ есть
    ↓
TokenManager.checkTokenAvailability()
    ↓
Восстановление: AppConfig.authToken = SubscriptionManager.currentToken.token
    ↓
Токен доступен ✅
```

**Вывод:**
- ⚠️ Токен потерян из `AppConfig.authToken` и Keychain
- ✅ Но восстановлен через `TokenManager` из `SubscriptionManager`
- ✅ Токен доступен для API запросов

**Вопрос:** Почему токен потерян из Keychain между 16:02:55 и 16:03:37?

---

## 🚨 БЛОК #11: Ошибка 401 Unauthorized - КРИТИЧЕСКАЯ ПРОБЛЕМА! (16:03:37.874)

### Логи:
```
[16:03:37.874] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/analytics?period=day
[16:03:38.185] [ℹ️] [NETWORK] ⬅️ status=401 url=https://aladdin-ai.ru/api/analytics?period=day
[16:03:38.389] [ℹ️] [NETWORK]    - Response body: {"detail":"Невалидный или истекший токен"}
[16:03:38.406] [ℹ️] [BUSINESS] ❌ DEFENSIVE JWT: Circuit Breaker failure #1
[16:03:38.413] [ℹ️] [NETWORK] ❌ DEFENSIVE JWT: Circuit breaker failure recorded - max retries exceeded
[16:03:38.621] [ℹ️] [BUSINESS] ❌ DEFENSIVE JWT: Circuit Breaker failure #2
[16:03:38.632] [ℹ️] [NETWORK] ❌ DEFENSIVE JWT: Circuit breaker failure recorded for 401 token expired
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Отправка запроса:**
   ```
   GET /api/analytics?period=day
   Headers: Authorization: Bearer {token}
   ```

2. **Ответ сервера:**
   ```
   Status: 401 Unauthorized
   Body: {"detail":"Невалидный или истекший токен"}
   ```

3. **Circuit Breaker:**
   - Зафиксированы 2 ошибки подряд
   - Circuit Breaker активирован (защита от каскадных ошибок)

**Взаимодействие компонентов:**
```
AnalyticsViewModel.load()
    ↓
APIService.getAnalytics(period: .day)
    ↓
NetworkManager.get(endpoint: "/api/analytics?period=day")
    ↓
Headers: Authorization: Bearer {token}
    ↓
Server validates token:
   - Проверка подписи JWT
   - Проверка exp (время истечения)
   - Проверка deviceId
    ↓
Результат: ❌ Токен невалидный или истёкший
    ↓
Response: 401 Unauthorized
    ↓
Circuit Breaker: failure #1, failure #2
```

**Парадокс:**
- Клиент считает токен валидным (23 часа до истечения)
- Сервер считает токен невалидным/истёкшим

**Возможные причины:**
1. **Токен действительно истёк на сервере:**
   - Клиент неправильно парсит `exp` из JWT
   - Разница во времени между клиентом и сервером
   - Токен был создан ранее и уже истёк

2. **Токен невалидный:**
   - Токен был отозван на сервере
   - Токен для другого устройства
   - Проблема с подписью JWT

3. **Проблема с передачей токена:**
   - Токен не передаётся в заголовке Authorization
   - Токен передаётся неправильно (не `Bearer {token}`)
   - Токен обрезан или повреждён

**Вывод:**
- ❌ Сервер отклоняет токен как невалидный/истёкший
- ⚠️ Circuit Breaker активирован
- 🔍 Требуется диагностика реального `exp` из JWT

---

## 📊 БЛОК #12: Другие API запросы работают (16:03:38.824)

### Логи:
```
[16:03:38.824] [ℹ️] [BUSINESS] Analytics data loaded: threats=0, source=empty
[16:03:38.831] [ℹ️] [BUSINESS] Applying analytics summary: 0 threats detected
[16:03:38.838] [ℹ️] [BUSINESS] Applying security analytics data
[16:03:38.845] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/reports/driving/stats
[16:03:38.851] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/reports/dark-web/stats
[16:03:38.858] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/reports/identity-theft/stats
[16:03:38.866] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/reports/privacy/location/stats
[16:03:38.872] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/reports/privacy/cleanup/stats
[16:03:38.883] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/reports/privacy/tracker/stats
[16:03:38.887] [ℹ️] [NETWORK] ➡️ GET https://aladdin-ai.ru/api/reports/ai-categories/stats
[16:03:38.895] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/reports/driving/stats
[16:03:38.901] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/reports/dark-web/stats
[16:03:38.906] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/reports/privacy/location/stats
[16:03:38.913] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/reports/privacy/tracker/stats
[16:03:38.917] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/reports/identity-theft/stats
[16:03:38.923] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/reports/privacy/cleanup/stats
[16:03:38.929] [ℹ️] [NETWORK] ⬅️ status=200 url=https://aladdin-ai.ru/api/reports/ai-categories/stats
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Fallback на пустые данные:**
   - Analytics data loaded: `threats=0, source=empty`
   - Это fallback, так как основной запрос вернул 401

2. **Другие API запросы:**
   - Все запросы к `/api/reports/*` вернули `200 OK` ✅
   - Это означает, что токен **работает** для этих endpoints

**Парадокс:**
- `/api/analytics` → 401 ❌
- `/api/reports/*` → 200 ✅

**Возможные причины:**
1. **Разные требования к авторизации:**
   - `/api/analytics` требует более строгую проверку токена
   - `/api/reports/*` может использовать более мягкую проверку

2. **Разные серверы/микросервисы:**
   - `/api/analytics` может быть на другом сервере
   - Разные настройки валидации токенов

3. **Проблема специфична для `/api/analytics`:**
   - Возможно, этот endpoint имеет баг
   - Или требует дополнительных параметров

**Вывод:**
- ✅ Другие endpoints работают корректно
- ❌ Проблема специфична для `/api/analytics`
- 🔍 Требуется проверка требований к авторизации для этого endpoint

---

## 📊 БЛОК #13: Завершение загрузки Analytics (16:03:39.408)

### Логи:
```
[16:03:39.408] [ℹ️] [PERFORMANCE] Screen 'AnalyticsScreen' loaded in 1.274 sec
```

### 🔍 Детальный анализ:

**Что происходит:**
1. **Завершение загрузки экрана:**
   - Экран 'AnalyticsScreen' загружен за 1.274 секунды
   - Это включает все API запросы и обработку данных

**Вывод:**
- ✅ Экран загружен успешно
- ⚠️ Производительность приемлемая (1.274 сек)

---

## 🎯 ИТОГОВЫЕ ВЫВОДЫ

### ✅ Что работает:
1. ✅ Загрузка токена из Keychain
2. ✅ Валидация структуры JWT
3. ✅ Token Health Monitoring
4. ✅ Восстановление токена через TokenManager
5. ✅ Другие API endpoints (`/api/reports/*`)

### ❌ Что не работает:
1. ❌ `/api/analytics` возвращает 401
2. ❌ Токен теряется из `AppConfig.authToken` и Keychain между инициализацией и использованием

### 🔍 Главные проблемы:
1. **Проблема #1:** Токен теряется из Keychain между 16:02:55 и 16:03:37
   - **Вопрос:** Что очищает Keychain?
   - **Решение:** Проверить все места, где вызывается `KeychainManager.delete(forKey: .authToken)`

2. **Проблема #2:** Сервер возвращает 401 для валидного (по клиенту) токена
   - **Вопрос:** Почему сервер считает токен невалидным?
   - **Решение:** Проверить реальный `exp` из JWT и сравнить с текущим временем на сервере

### 📋 Рекомендации:
1. **Немедленно:** Добавить логирование всех вызовов `KeychainManager.delete(forKey: .authToken)`
2. **Важно:** Проверить реальный `exp` из JWT при сохранении токена
3. **Желательно:** Добавить автоматическое обновление токена при 401 ошибке

---

**Дата анализа:** 2026-03-16  
**Версия:** BUILD 121
