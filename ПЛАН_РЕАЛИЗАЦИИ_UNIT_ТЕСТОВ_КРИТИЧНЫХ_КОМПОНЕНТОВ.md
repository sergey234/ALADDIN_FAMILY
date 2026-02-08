# 📋 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ UNIT ТЕСТОВ ДЛЯ КРИТИЧНЫХ КОМПОНЕНТОВ

**Дата создания:** 2026-02-06  
**Версия:** 1.0  
**Оценка времени:** 4-6 часов  
**Статус:** 📝 План готов к реализации

---

## 🎯 ЦЕЛЬ

Создать unit тесты для 4 критичных компонентов iOS приложения:
1. **PaymentQRViewModel** - платежи (критично!)
2. **CrashDetectionManager** - обнаружение аварий (критично!)
3. **SecurityManager** - безопасность (критично!)
4. **ParentalControlViewModel** - родительский контроль (критично!)

---

## 📊 ОБЩАЯ СТРУКТУРА ПЛАНА

### **Этапы реализации:**
1. ✅ Подготовка инфраструктуры (30 минут)
2. ✅ Тесты для PaymentQRViewModel (1.5 часа)
3. ✅ Тесты для CrashDetectionManager (1.5 часа)
4. ✅ Тесты для SecurityManager (1 час)
5. ✅ Тесты для ParentalControlViewModel (1 час)
6. ✅ Финальная проверка и документация (30 минут)

**ИТОГО:** 6 часов

---

## 📝 ДЕТАЛЬНЫЙ ПЛАН ПО ПУНКТАМ

---

## 1️⃣ ЭТАП 1: ПОДГОТОВКА ИНФРАСТРУКТУРЫ (30 минут)

### **1.1 Создать протокол APIServiceProtocol (15 минут)**

**Файл:** `Core/Network/APIServiceProtocol.swift`

**Задачи:**
- [ ] Создать протокол `APIServiceProtocol`
- [ ] Определить методы для PaymentQRViewModel:
  - `createQRPayment(request:completion:)`
  - `checkQRPaymentStatus(paymentId:completion:)`
- [ ] Определить методы для CrashDetectionManager:
  - `setupCrashDetection(latitude:longitude:radius:completion:)`
  - `sendCrashAlert(latitude:longitude:severity:completion:)`
  - `startCrashDetectionMonitoring(completion:)`
  - `stopCrashDetectionMonitoring(completion:)`
  - `sendCrashDetectionData(accelerometer:gyroscope:speed:location:completion:)`
  - `getCrashDetectionStatus(completion:)`
- [ ] Определить методы для ParentalControlViewModel:
  - `getComponentStatus(componentId:completion:)`
  - `updateComponentStatus(componentId:isEnabled:completion:)`

**Код:**
```swift
protocol APIServiceProtocol {
    // Payment QR
    func createQRPayment(request: CreateQRPaymentRequest, completion: @escaping (Result<CreateQRPaymentResponse, Error>) -> Void)
    func checkQRPaymentStatus(paymentId: String, completion: @escaping (Result<CheckQRPaymentStatusResponse, Error>) -> Void)
    
    // Crash Detection
    func setupCrashDetection(latitude: Double, longitude: Double, radius: Double, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void)
    func sendCrashAlert(latitude: Double, longitude: Double, severity: String, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void)
    func startCrashDetectionMonitoring(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void)
    func stopCrashDetectionMonitoring(completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void)
    func sendCrashDetectionData(accelerometer: [String: Any], gyroscope: [String: Any], speed: Double, location: [String: Any], completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void)
    func getCrashDetectionStatus(completion: @escaping (Result<APIResponse<CrashDetectionStatus>, Error>) -> Void)
    
    // Parental Control
    func getComponentStatus(componentId: String, completion: @escaping (Result<ComponentStatusResponse, Error>) -> Void)
    func updateComponentStatus(componentId: String, isEnabled: Bool, completion: @escaping (Result<APIResponse<Bool>, Error>) -> Void)
}
```

---

### **1.2 Обновить APIService и MockAPIService (10 минут)**

**Файлы:**
- `Core/Network/APIService.swift`
- `Core/Network/MockAPIService.swift`

**Задачи:**
- [ ] Добавить `extension APIService: APIServiceProtocol {}`
- [ ] Добавить `extension MockAPIService: APIServiceProtocol {}`
- [ ] Убедиться, что все методы реализованы

---

### **1.3 Создать Mock реализации для зависимостей (5 минут)**

**Файл:** `Tests/UnitTests/Mocks/`

**Задачи:**
- [ ] Создать `MockLocationManager.swift` (для CrashDetectionManager)
- [ ] Создать `MockComponentStatusService.swift` (для ParentalControlViewModel)
- [ ] Создать базовые структуры для Mock объектов

---

## 2️⃣ ЭТАП 2: ТЕСТЫ ДЛЯ PaymentQRViewModel (1.5 часа)

### **2.1 Создать файл тестов (5 минут)**

**Файл:** `Tests/UnitTests/PaymentQRViewModelTests.swift`

**Задачи:**
- [ ] Создать класс `PaymentQRViewModelTests: XCTestCase`
- [ ] Настроить `setUp()` и `tearDown()`
- [ ] Создать Mock APIService

---

### **2.2 Тесты инициализации (10 минут)**

**Тесты:**
- [ ] `testInitialization_WithValidTariff()` - инициализация с валидным тарифом
- [ ] `testInitialization_WithInvalidTariff()` - инициализация с невалидным тарифом
- [ ] `testInitialState()` - проверка начального состояния

**Что проверяет:**
- ✅ ViewModel создается с правильным тарифом
- ✅ Начальное состояние правильное (isLoading = false, errorMessage = nil)
- ✅ Обработка невалидных тарифов

---

### **2.3 Тесты создания QR-кода (20 минут)**

**Тесты:**
- [ ] `testCreateQRPayment_Success()` - успешное создание QR-кода
- [ ] `testCreateQRPayment_NetworkError()` - ошибка сети
- [ ] `testCreateQRPayment_ServerError()` - ошибка сервера
- [ ] `testCreateQRPayment_InvalidResponse()` - невалидный ответ

**Что проверяет:**
- ✅ QR-код создается успешно
- ✅ Правильная обработка ошибок
- ✅ Обновление состояния (isLoading, errorMessage)
- ✅ Сохранение paymentId и expiresAt

---

### **2.4 Тесты проверки статуса платежа (20 минут)**

**Тесты:**
- [ ] `testCheckPaymentStatus_Success_Pending()` - статус "pending"
- [ ] `testCheckPaymentStatus_Success_Completed()` - статус "completed"
- [ ] `testCheckPaymentStatus_Success_Failed()` - статус "failed"
- [ ] `testCheckPaymentStatus_NetworkError()` - ошибка сети
- [ ] `testCheckPaymentStatus_Expired()` - платеж истек

**Что проверяет:**
- ✅ Правильная обработка всех статусов
- ✅ Обновление UI при изменении статуса
- ✅ Обработка истечения платежа
- ✅ Автоматическая остановка проверки при завершении

---

### **2.5 Тесты автоматической проверки (15 минут)**

**Тесты:**
- [ ] `testStartAutoCheck()` - запуск автоматической проверки
- [ ] `testStopAutoCheck()` - остановка автоматической проверки
- [ ] `testAutoCheck_StopsOnCompletion()` - остановка при завершении
- [ ] `testAutoCheck_StopsOnError()` - остановка при ошибке

**Что проверяет:**
- ✅ Таймер запускается правильно
- ✅ Таймер останавливается правильно
- ✅ Правильная обработка завершения платежа

---

### **2.6 Тесты выбора метода оплаты (10 минут)**

**Тесты:**
- [ ] `testSelectPaymentMethod_SBP()` - выбор СБП
- [ ] `testSelectPaymentMethod_SberPay()` - выбор СберPay
- [ ] `testSelectPaymentMethod_Card()` - выбор карты
- [ ] `testCurrentQRImage_ReturnsCorrectImage()` - правильный QR-код для метода

**Что проверяет:**
- ✅ Правильное переключение методов
- ✅ Правильный QR-код для каждого метода

---

### **2.7 Тесты обработки ошибок (10 минут)**

**Тесты:**
- [ ] `testHandleError_ShowsAlert()` - показ алерта при ошибке
- [ ] `testHandleError_NetworkError()` - обработка сетевой ошибки
- [ ] `testHandleError_ServerError()` - обработка ошибки сервера
- [ ] `testHandleError_Timeout()` - обработка таймаута

**Что проверяет:**
- ✅ Правильное отображение ошибок
- ✅ Правильные сообщения об ошибках
- ✅ Правильная обработка всех типов ошибок

---

## 3️⃣ ЭТАП 3: ТЕСТЫ ДЛЯ CrashDetectionManager (1.5 часа)

### **3.1 Создать файл тестов (5 минут)**

**Файл:** `Tests/UnitTests/CrashDetectionManagerTests.swift`

**Задачи:**
- [ ] Создать класс `CrashDetectionManagerTests: XCTestCase`
- [ ] Настроить `setUp()` и `tearDown()`
- [ ] Создать Mock APIService и Mock LocationManager

---

### **3.2 Тесты инициализации (10 минут)**

**Тесты:**
- [ ] `testInitialization()` - проверка инициализации
- [ ] `testInitialState()` - проверка начального состояния
- [ ] `testSetupMotionManager()` - настройка MotionManager

**Что проверяет:**
- ✅ Manager создается правильно
- ✅ Начальное состояние правильное (isMonitoring = false)
- ✅ MotionManager настроен правильно

---

### **3.3 Тесты запуска мониторинга (20 минут)**

**Тесты:**
- [ ] `testStartMonitoring_Success()` - успешный запуск
- [ ] `testStartMonitoring_AccelerometerUnavailable()` - акселерометр недоступен
- [ ] `testStartMonitoring_LocationUnavailable()` - геолокация недоступна
- [ ] `testStartMonitoring_AlreadyRunning()` - уже запущен
- [ ] `testStartMonitoring_APISetupFails()` - ошибка настройки API

**Что проверяет:**
- ✅ Мониторинг запускается правильно
- ✅ Правильная обработка ошибок
- ✅ Правильная настройка геозоны
- ✅ Правильный вызов API

---

### **3.4 Тесты остановки мониторинга (15 минут)**

**Тесты:**
- [ ] `testStopMonitoring_Success()` - успешная остановка
- [ ] `testStopMonitoring_NotRunning()` - остановка когда не запущен
- [ ] `testStopMonitoring_ClearsState()` - очистка состояния

**Что проверяет:**
- ✅ Мониторинг останавливается правильно
- ✅ Состояние очищается
- ✅ Таймеры останавливаются

---

### **3.5 Тесты обнаружения краша (25 минут)**

**Тесты:**
- [ ] `testDetectCrash_GForceAboveThreshold()` - G-сила выше порога
- [ ] `testDetectCrash_GForceBelowThreshold()` - G-сила ниже порога
- [ ] `testDetectCrash_TriggersCountdown()` - запуск обратного отсчета
- [ ] `testDetectCrash_SendsAlertToAPI()` - отправка алерта на API
- [ ] `testDetectCrash_CallsEmergencyServices()` - вызов экстренных служб

**Что проверяет:**
- ✅ Правильное обнаружение краша (порог 3.0 G)
- ✅ Правильный запуск обратного отсчета (10 секунд)
- ✅ Правильная отправка данных на сервер
- ✅ Правильный вызов экстренных служб

---

### **3.6 Тесты отправки данных сенсоров (15 минут)**

**Тесты:**
- [ ] `testSendSensorData_Success()` - успешная отправка
- [ ] `testSendSensorData_NetworkError()` - ошибка сети
- [ ] `testSendSensorData_Interval()` - правильный интервал отправки

**Что проверяет:**
- ✅ Данные отправляются правильно
- ✅ Правильный интервал отправки (каждую секунду)
- ✅ Правильная обработка ошибок

---

## 4️⃣ ЭТАП 4: ТЕСТЫ ДЛЯ SecurityManager (1 час)

### **4.1 Создать файл тестов (5 минут)**

**Файл:** `Tests/UnitTests/SecurityManagerTests.swift`

**Задачи:**
- [ ] Создать класс `SecurityManagerTests: XCTestCase`
- [ ] Настроить `setUp()` и `tearDown()`
- [ ] Настроить Mock Keychain

---

### **4.2 Тесты инициализации (10 минут)**

**Тесты:**
- [ ] `testInitialization()` - проверка инициализации
- [ ] `testInitialState()` - проверка начального состояния
- [ ] `testCheckBiometricAvailability()` - проверка доступности биометрии

**Что проверяет:**
- ✅ Manager создается правильно
- ✅ Начальное состояние правильное
- ✅ Правильная проверка биометрии

---

### **4.3 Тесты биометрической аутентификации (15 минут)**

**Тесты:**
- [ ] `testAuthenticateWithBiometrics_Success()` - успешная аутентификация
- [ ] `testAuthenticateWithBiometrics_Failure()` - неудачная аутентификация
- [ ] `testAuthenticateWithBiometrics_Unavailable()` - биометрия недоступна
- [ ] `testAuthenticateWithBiometrics_Cancelled()` - отмена пользователем

**Что проверяет:**
- ✅ Правильная аутентификация
- ✅ Правильная обработка ошибок
- ✅ Правильная обработка отмены

---

### **4.4 Тесты шифрования данных (20 минут)**

**Тесты:**
- [ ] `testEncryptData_Success()` - успешное шифрование
- [ ] `testDecryptData_Success()` - успешная расшифровка
- [ ] `testEncryptDecrypt_RoundTrip()` - полный цикл шифрование-расшифровка
- [ ] `testEncryptData_InvalidKey()` - невалидный ключ
- [ ] `testDecryptData_InvalidData()` - невалидные данные

**Что проверяет:**
- ✅ Правильное шифрование (AES-GCM)
- ✅ Правильная расшифровка
- ✅ Правильная обработка ошибок
- ✅ Правильное управление ключами

---

### **4.5 Тесты безопасного хранения (10 минут)**

**Тесты:**
- [ ] `testStoreSecureData_Success()` - успешное сохранение
- [ ] `testRetrieveSecureData_Success()` - успешное получение
- [ ] `testDeleteSecureData_Success()` - успешное удаление
- [ ] `testStoreSecureData_EncryptionFails()` - ошибка шифрования

**Что проверяет:**
- ✅ Правильное сохранение данных
- ✅ Правильное получение данных
- ✅ Правильное удаление данных
- ✅ Правильная обработка ошибок

---

## 5️⃣ ЭТАП 5: ТЕСТЫ ДЛЯ ParentalControlViewModel (1 час)

### **5.1 Создать файл тестов (5 минут)**

**Файл:** `Tests/UnitTests/ParentalControlViewModelTests.swift`

**Задачи:**
- [ ] Создать класс `ParentalControlViewModelTests: XCTestCase`
- [ ] Настроить `setUp()` и `tearDown()`
- [ ] Создать Mock ComponentStatusService

---

### **5.2 Тесты инициализации (10 минут)**

**Тесты:**
- [ ] `testInitialization()` - проверка инициализации
- [ ] `testInitialState()` - проверка начального состояния
- [ ] `testLoadChildren()` - загрузка детей

**Что проверяет:**
- ✅ ViewModel создается правильно
- ✅ Начальное состояние правильное
- ✅ Дети загружаются правильно

---

### **5.3 Тесты загрузки статусов компонентов (15 минут)**

**Тесты:**
- [ ] `testLoadComponentStatuses_Success()` - успешная загрузка
- [ ] `testLoadComponentStatuses_NetworkError()` - ошибка сети
- [ ] `testLoadComponentStatuses_DemoMode()` - демо-режим
- [ ] `testLoadComponentStatuses_ParallelLoading()` - параллельная загрузка

**Что проверяет:**
- ✅ Статусы загружаются правильно
- ✅ Правильная обработка ошибок
- ✅ Правильная работа в демо-режиме
- ✅ Правильная параллельная загрузка

---

### **5.4 Тесты переключения компонентов (20 минут)**

**Тесты:**
- [ ] `testToggleSelfHarmDetection_Enable()` - включение Self Harm Detection
- [ ] `testToggleSelfHarmDetection_Disable()` - выключение Self Harm Detection
- [ ] `testToggleGroomingDetection()` - переключение Grooming Detection
- [ ] `testToggleOnlinePredators()` - переключение Online Predators
- [ ] `testTogglePsychologicalSupport()` - переключение Psychological Support
- [ ] `testToggleParentalControlBot()` - переключение Parental Control Bot
- [ ] `testToggle_NetworkError()` - ошибка сети при переключении

**Что проверяет:**
- ✅ Правильное переключение всех 5 компонентов
- ✅ Правильная обработка ошибок
- ✅ Правильное обновление состояния
- ✅ Правильный откат при ошибке

---

### **5.5 Тесты обновления статусов (10 минут)**

**Тесты:**
- [ ] `testUpdateStatusForComponent_SelfHarm()` - обновление статуса Self Harm
- [ ] `testUpdateStatusForComponent_Grooming()` - обновление статуса Grooming
- [ ] `testUpdateStatusForComponent_OnlinePredators()` - обновление статуса Online Predators

**Что проверяет:**
- ✅ Правильное обновление статусов
- ✅ Правильное обновление UI

---

## 6️⃣ ЭТАП 6: ФИНАЛЬНАЯ ПРОВЕРКА И ДОКУМЕНТАЦИЯ (30 минут)

### **6.1 Запуск всех тестов (10 минут)**

**Задачи:**
- [ ] Запустить все тесты через Xcode (Cmd+U)
- [ ] Проверить, что все тесты проходят
- [ ] Исправить ошибки, если есть

---

### **6.2 Проверка покрытия кода (10 минут)**

**Задачи:**
- [ ] Включить Code Coverage в Xcode
- [ ] Проверить покрытие для каждого компонента
- [ ] Убедиться, что покрытие >80% для критичных методов

---

### **6.3 Документация (10 минут)**

**Задачи:**
- [ ] Обновить README с информацией о тестах
- [ ] Добавить комментарии к тестам
- [ ] Создать краткую документацию по запуску тестов

---

## 📋 TODO ЛИСТ (ЭЛЕКТРОННЫЙ ВАРИАНТ)

### ✅ **ЭТАП 1: ПОДГОТОВКА ИНФРАСТРУКТУРЫ (30 минут)**

- [ ] **1.1** Создать протокол `APIServiceProtocol` (15 мин)
  - [ ] Создать файл `Core/Network/APIServiceProtocol.swift`
  - [ ] Определить методы для PaymentQRViewModel
  - [ ] Определить методы для CrashDetectionManager
  - [ ] Определить методы для ParentalControlViewModel
  
- [ ] **1.2** Обновить APIService и MockAPIService (10 мин)
  - [ ] Добавить `extension APIService: APIServiceProtocol {}`
  - [ ] Добавить `extension MockAPIService: APIServiceProtocol {}`
  - [ ] Проверить, что все методы реализованы
  
- [ ] **1.3** Создать Mock реализации для зависимостей (5 мин)
  - [ ] Создать `Tests/UnitTests/Mocks/MockLocationManager.swift`
  - [ ] Создать `Tests/UnitTests/Mocks/MockComponentStatusService.swift`
  - [ ] Создать базовые структуры для Mock объектов

---

### ✅ **ЭТАП 2: ТЕСТЫ ДЛЯ PaymentQRViewModel (1.5 часа)**

- [ ] **2.1** Создать файл тестов (5 мин)
  - [ ] Создать `Tests/UnitTests/PaymentQRViewModelTests.swift`
  - [ ] Настроить `setUp()` и `tearDown()`
  - [ ] Создать Mock APIService
  
- [ ] **2.2** Тесты инициализации (10 мин)
  - [ ] `testInitialization_WithValidTariff()`
  - [ ] `testInitialization_WithInvalidTariff()`
  - [ ] `testInitialState()`
  
- [ ] **2.3** Тесты создания QR-кода (20 мин)
  - [ ] `testCreateQRPayment_Success()`
  - [ ] `testCreateQRPayment_NetworkError()`
  - [ ] `testCreateQRPayment_ServerError()`
  - [ ] `testCreateQRPayment_InvalidResponse()`
  
- [ ] **2.4** Тесты проверки статуса платежа (20 мин)
  - [ ] `testCheckPaymentStatus_Success_Pending()`
  - [ ] `testCheckPaymentStatus_Success_Completed()`
  - [ ] `testCheckPaymentStatus_Success_Failed()`
  - [ ] `testCheckPaymentStatus_NetworkError()`
  - [ ] `testCheckPaymentStatus_Expired()`
  
- [ ] **2.5** Тесты автоматической проверки (15 мин)
  - [ ] `testStartAutoCheck()`
  - [ ] `testStopAutoCheck()`
  - [ ] `testAutoCheck_StopsOnCompletion()`
  - [ ] `testAutoCheck_StopsOnError()`
  
- [ ] **2.6** Тесты выбора метода оплаты (10 мин)
  - [ ] `testSelectPaymentMethod_SBP()`
  - [ ] `testSelectPaymentMethod_SberPay()`
  - [ ] `testSelectPaymentMethod_Card()`
  - [ ] `testCurrentQRImage_ReturnsCorrectImage()`
  
- [ ] **2.7** Тесты обработки ошибок (10 мин)
  - [ ] `testHandleError_ShowsAlert()`
  - [ ] `testHandleError_NetworkError()`
  - [ ] `testHandleError_ServerError()`
  - [ ] `testHandleError_Timeout()`

---

### ✅ **ЭТАП 3: ТЕСТЫ ДЛЯ CrashDetectionManager (1.5 часа)**

- [ ] **3.1** Создать файл тестов (5 мин)
  - [ ] Создать `Tests/UnitTests/CrashDetectionManagerTests.swift`
  - [ ] Настроить `setUp()` и `tearDown()`
  - [ ] Создать Mock APIService и Mock LocationManager
  
- [ ] **3.2** Тесты инициализации (10 мин)
  - [ ] `testInitialization()`
  - [ ] `testInitialState()`
  - [ ] `testSetupMotionManager()`
  
- [ ] **3.3** Тесты запуска мониторинга (20 мин)
  - [ ] `testStartMonitoring_Success()`
  - [ ] `testStartMonitoring_AccelerometerUnavailable()`
  - [ ] `testStartMonitoring_LocationUnavailable()`
  - [ ] `testStartMonitoring_AlreadyRunning()`
  - [ ] `testStartMonitoring_APISetupFails()`
  
- [ ] **3.4** Тесты остановки мониторинга (15 мин)
  - [ ] `testStopMonitoring_Success()`
  - [ ] `testStopMonitoring_NotRunning()`
  - [ ] `testStopMonitoring_ClearsState()`
  
- [ ] **3.5** Тесты обнаружения краша (25 мин)
  - [ ] `testDetectCrash_GForceAboveThreshold()`
  - [ ] `testDetectCrash_GForceBelowThreshold()`
  - [ ] `testDetectCrash_TriggersCountdown()`
  - [ ] `testDetectCrash_SendsAlertToAPI()`
  - [ ] `testDetectCrash_CallsEmergencyServices()`
  
- [ ] **3.6** Тесты отправки данных сенсоров (15 мин)
  - [ ] `testSendSensorData_Success()`
  - [ ] `testSendSensorData_NetworkError()`
  - [ ] `testSendSensorData_Interval()`

---

### ✅ **ЭТАП 4: ТЕСТЫ ДЛЯ SecurityManager (1 час)**

- [ ] **4.1** Создать файл тестов (5 мин)
  - [ ] Создать `Tests/UnitTests/SecurityManagerTests.swift`
  - [ ] Настроить `setUp()` и `tearDown()`
  - [ ] Настроить Mock Keychain
  
- [ ] **4.2** Тесты инициализации (10 мин)
  - [ ] `testInitialization()`
  - [ ] `testInitialState()`
  - [ ] `testCheckBiometricAvailability()`
  
- [ ] **4.3** Тесты биометрической аутентификации (15 мин)
  - [ ] `testAuthenticateWithBiometrics_Success()`
  - [ ] `testAuthenticateWithBiometrics_Failure()`
  - [ ] `testAuthenticateWithBiometrics_Unavailable()`
  - [ ] `testAuthenticateWithBiometrics_Cancelled()`
  
- [ ] **4.4** Тесты шифрования данных (20 мин)
  - [ ] `testEncryptData_Success()`
  - [ ] `testDecryptData_Success()`
  - [ ] `testEncryptDecrypt_RoundTrip()`
  - [ ] `testEncryptData_InvalidKey()`
  - [ ] `testDecryptData_InvalidData()`
  
- [ ] **4.5** Тесты безопасного хранения (10 мин)
  - [ ] `testStoreSecureData_Success()`
  - [ ] `testRetrieveSecureData_Success()`
  - [ ] `testDeleteSecureData_Success()`
  - [ ] `testStoreSecureData_EncryptionFails()`

---

### ✅ **ЭТАП 5: ТЕСТЫ ДЛЯ ParentalControlViewModel (1 час)**

- [ ] **5.1** Создать файл тестов (5 мин)
  - [ ] Создать `Tests/UnitTests/ParentalControlViewModelTests.swift`
  - [ ] Настроить `setUp()` и `tearDown()`
  - [ ] Создать Mock ComponentStatusService
  
- [ ] **5.2** Тесты инициализации (10 мин)
  - [ ] `testInitialization()`
  - [ ] `testInitialState()`
  - [ ] `testLoadChildren()`
  
- [ ] **5.3** Тесты загрузки статусов компонентов (15 мин)
  - [ ] `testLoadComponentStatuses_Success()`
  - [ ] `testLoadComponentStatuses_NetworkError()`
  - [ ] `testLoadComponentStatuses_DemoMode()`
  - [ ] `testLoadComponentStatuses_ParallelLoading()`
  
- [ ] **5.4** Тесты переключения компонентов (20 мин)
  - [ ] `testToggleSelfHarmDetection_Enable()`
  - [ ] `testToggleSelfHarmDetection_Disable()`
  - [ ] `testToggleGroomingDetection()`
  - [ ] `testToggleOnlinePredators()`
  - [ ] `testTogglePsychologicalSupport()`
  - [ ] `testToggleParentalControlBot()`
  - [ ] `testToggle_NetworkError()`
  
- [ ] **5.5** Тесты обновления статусов (10 мин)
  - [ ] `testUpdateStatusForComponent_SelfHarm()`
  - [ ] `testUpdateStatusForComponent_Grooming()`
  - [ ] `testUpdateStatusForComponent_OnlinePredators()`

---

### ✅ **ЭТАП 6: ФИНАЛЬНАЯ ПРОВЕРКА И ДОКУМЕНТАЦИЯ (30 минут)**

- [ ] **6.1** Запуск всех тестов (10 мин)
  - [ ] Запустить все тесты через Xcode (Cmd+U)
  - [ ] Проверить, что все тесты проходят
  - [ ] Исправить ошибки, если есть
  
- [ ] **6.2** Проверка покрытия кода (10 мин)
  - [ ] Включить Code Coverage в Xcode
  - [ ] Проверить покрытие для каждого компонента
  - [ ] Убедиться, что покрытие >80% для критичных методов
  
- [ ] **6.3** Документация (10 мин)
  - [ ] Обновить README с информацией о тестах
  - [ ] Добавить комментарии к тестам
  - [ ] Создать краткую документацию по запуску тестов

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### **Общее количество задач:**
- **Всего задач:** 67
- **Всего тестов:** ~40 unit тестов
- **Оценка времени:** 6 часов

### **Распределение по компонентам:**
- **PaymentQRViewModel:** 7 групп тестов, ~15 тестов
- **CrashDetectionManager:** 6 групп тестов, ~12 тестов
- **SecurityManager:** 5 групп тестов, ~8 тестов
- **ParentalControlViewModel:** 5 групп тестов, ~10 тестов

### **Покрытие:**
- **Критичные методы:** >80%
- **Обработка ошибок:** 100%
- **Бизнес-логика:** >90%

---

## 🎯 КРИТЕРИИ УСПЕХА

### **✅ План считается выполненным, если:**

1. ✅ Все 67 задач выполнены
2. ✅ Все ~40 тестов проходят успешно
3. ✅ Покрытие кода >80% для критичных методов
4. ✅ Все ошибки обработаны в тестах
5. ✅ Документация обновлена

---

## 📝 ПРИМЕЧАНИЯ

### **Важные моменты:**

1. **Mock объекты:** Использовать MockAPIService вместо реального API
2. **Async тесты:** Использовать `XCTestExpectation` для async операций
3. **MainActor:** Убедиться, что тесты выполняются на MainActor для @MainActor классов
4. **Изоляция:** Каждый тест должен быть независимым
5. **Очистка:** Правильно очищать состояние в `tearDown()`

---

## 🚀 БЫСТРЫЙ СТАРТ

### **Для начала работы:**

1. ✅ Создать протокол `APIServiceProtocol` (Этап 1.1)
2. ✅ Обновить APIService и MockAPIService (Этап 1.2)
3. ✅ Создать Mock зависимости (Этап 1.3)
4. ✅ Начать с PaymentQRViewModel (Этап 2)

---

**Документ создан:** 2026-02-06  
**Статус:** ✅ Готов к реализации  
**Следующий шаг:** Начать с Этапа 1.1
