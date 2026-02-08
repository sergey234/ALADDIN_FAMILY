# ✅ TODO ЛИСТ: UNIT ТЕСТЫ ДЛЯ КРИТИЧНЫХ КОМПОНЕНТОВ

**Дата создания:** 2026-02-06  
**Версия:** 1.0  
**Оценка времени:** 4-6 часов  
**Статус:** 📝 Готов к выполнению

---

## 📋 ОБЩИЙ ПРОГРЕСС

**Выполнено:** 0/67 задач (0%)  
**Осталось:** 67 задач  
**Оценка времени:** 6 часов

---

## ✅ ЭТАП 1: ПОДГОТОВКА ИНФРАСТРУКТУРЫ (30 минут)

**Прогресс:** 0/3 задач (0%)

### **1.1 Создать протокол APIServiceProtocol (15 минут)**
- [ ] Создать файл `Core/Network/APIServiceProtocol.swift`
- [ ] Определить методы для PaymentQRViewModel:
  - [ ] `createQRPayment(request:completion:)`
  - [ ] `checkQRPaymentStatus(paymentId:completion:)`
- [ ] Определить методы для CrashDetectionManager:
  - [ ] `setupCrashDetection(latitude:longitude:radius:completion:)`
  - [ ] `sendCrashAlert(latitude:longitude:severity:completion:)`
  - [ ] `startCrashDetectionMonitoring(completion:)`
  - [ ] `stopCrashDetectionMonitoring(completion:)`
  - [ ] `sendCrashDetectionData(accelerometer:gyroscope:speed:location:completion:)`
  - [ ] `getCrashDetectionStatus(completion:)`
- [ ] Определить методы для ParentalControlViewModel:
  - [ ] `getComponentStatus(componentId:completion:)`
  - [ ] `updateComponentStatus(componentId:isEnabled:completion:)`

### **1.2 Обновить APIService и MockAPIService (10 минут)**
- [ ] Добавить `extension APIService: APIServiceProtocol {}` в `Core/Network/APIService.swift`
- [ ] Добавить `extension MockAPIService: APIServiceProtocol {}` в `Core/Network/MockAPIService.swift`
- [ ] Проверить, что все методы реализованы
- [ ] Убедиться, что код компилируется

### **1.3 Создать Mock реализации для зависимостей (5 минут)**
- [ ] Создать директорию `Tests/UnitTests/Mocks/`
- [ ] Создать `Tests/UnitTests/Mocks/MockLocationManager.swift`
- [ ] Создать `Tests/UnitTests/Mocks/MockComponentStatusService.swift`
- [ ] Добавить базовые Mock структуры

---

## ✅ ЭТАП 2: ТЕСТЫ ДЛЯ PaymentQRViewModel (1.5 часа)

**Прогресс:** 0/7 групп тестов (0%)

### **2.1 Создать файл тестов (5 минут)**
- [ ] Создать `Tests/UnitTests/PaymentQRViewModelTests.swift`
- [ ] Создать класс `PaymentQRViewModelTests: XCTestCase`
- [ ] Настроить `setUp()` метод
- [ ] Настроить `tearDown()` метод
- [ ] Создать Mock APIService

### **2.2 Тесты инициализации (10 минут)**
- [ ] `testInitialization_WithValidTariff()` - инициализация с валидным тарифом
- [ ] `testInitialization_WithInvalidTariff()` - инициализация с невалидным тарифом
- [ ] `testInitialState()` - проверка начального состояния

### **2.3 Тесты создания QR-кода (20 минут)**
- [ ] `testCreateQRPayment_Success()` - успешное создание QR-кода
- [ ] `testCreateQRPayment_NetworkError()` - ошибка сети
- [ ] `testCreateQRPayment_ServerError()` - ошибка сервера
- [ ] `testCreateQRPayment_InvalidResponse()` - невалидный ответ

### **2.4 Тесты проверки статуса платежа (20 минут)**
- [ ] `testCheckPaymentStatus_Success_Pending()` - статус "pending"
- [ ] `testCheckPaymentStatus_Success_Completed()` - статус "completed"
- [ ] `testCheckPaymentStatus_Success_Failed()` - статус "failed"
- [ ] `testCheckPaymentStatus_NetworkError()` - ошибка сети
- [ ] `testCheckPaymentStatus_Expired()` - платеж истек

### **2.5 Тесты автоматической проверки (15 минут)**
- [ ] `testStartAutoCheck()` - запуск автоматической проверки
- [ ] `testStopAutoCheck()` - остановка автоматической проверки
- [ ] `testAutoCheck_StopsOnCompletion()` - остановка при завершении
- [ ] `testAutoCheck_StopsOnError()` - остановка при ошибке

### **2.6 Тесты выбора метода оплаты (10 минут)**
- [ ] `testSelectPaymentMethod_SBP()` - выбор СБП
- [ ] `testSelectPaymentMethod_SberPay()` - выбор СберPay
- [ ] `testSelectPaymentMethod_Card()` - выбор карты
- [ ] `testCurrentQRImage_ReturnsCorrectImage()` - правильный QR-код для метода

### **2.7 Тесты обработки ошибок (10 минут)**
- [ ] `testHandleError_ShowsAlert()` - показ алерта при ошибке
- [ ] `testHandleError_NetworkError()` - обработка сетевой ошибки
- [ ] `testHandleError_ServerError()` - обработка ошибки сервера
- [ ] `testHandleError_Timeout()` - обработка таймаута

---

## ✅ ЭТАП 3: ТЕСТЫ ДЛЯ CrashDetectionManager (1.5 часа)

**Прогресс:** 0/6 групп тестов (0%)

### **3.1 Создать файл тестов (5 минут)**
- [ ] Создать `Tests/UnitTests/CrashDetectionManagerTests.swift`
- [ ] Создать класс `CrashDetectionManagerTests: XCTestCase`
- [ ] Настроить `setUp()` метод
- [ ] Настроить `tearDown()` метод
- [ ] Создать Mock APIService и Mock LocationManager

### **3.2 Тесты инициализации (10 минут)**
- [ ] `testInitialization()` - проверка инициализации
- [ ] `testInitialState()` - проверка начального состояния
- [ ] `testSetupMotionManager()` - настройка MotionManager

### **3.3 Тесты запуска мониторинга (20 минут)**
- [ ] `testStartMonitoring_Success()` - успешный запуск
- [ ] `testStartMonitoring_AccelerometerUnavailable()` - акселерометр недоступен
- [ ] `testStartMonitoring_LocationUnavailable()` - геолокация недоступна
- [ ] `testStartMonitoring_AlreadyRunning()` - уже запущен
- [ ] `testStartMonitoring_APISetupFails()` - ошибка настройки API

### **3.4 Тесты остановки мониторинга (15 минут)**
- [ ] `testStopMonitoring_Success()` - успешная остановка
- [ ] `testStopMonitoring_NotRunning()` - остановка когда не запущен
- [ ] `testStopMonitoring_ClearsState()` - очистка состояния

### **3.5 Тесты обнаружения краша (25 минут)**
- [ ] `testDetectCrash_GForceAboveThreshold()` - G-сила выше порога
- [ ] `testDetectCrash_GForceBelowThreshold()` - G-сила ниже порога
- [ ] `testDetectCrash_TriggersCountdown()` - запуск обратного отсчета
- [ ] `testDetectCrash_SendsAlertToAPI()` - отправка алерта на API
- [ ] `testDetectCrash_CallsEmergencyServices()` - вызов экстренных служб

### **3.6 Тесты отправки данных сенсоров (15 минут)**
- [ ] `testSendSensorData_Success()` - успешная отправка
- [ ] `testSendSensorData_NetworkError()` - ошибка сети
- [ ] `testSendSensorData_Interval()` - правильный интервал отправки

---

## ✅ ЭТАП 4: ТЕСТЫ ДЛЯ SecurityManager (1 час)

**Прогресс:** 0/5 групп тестов (0%)

### **4.1 Создать файл тестов (5 минут)**
- [ ] Создать `Tests/UnitTests/SecurityManagerTests.swift`
- [ ] Создать класс `SecurityManagerTests: XCTestCase`
- [ ] Настроить `setUp()` метод
- [ ] Настроить `tearDown()` метод
- [ ] Настроить Mock Keychain

### **4.2 Тесты инициализации (10 минут)**
- [ ] `testInitialization()` - проверка инициализации
- [ ] `testInitialState()` - проверка начального состояния
- [ ] `testCheckBiometricAvailability()` - проверка доступности биометрии

### **4.3 Тесты биометрической аутентификации (15 минут)**
- [ ] `testAuthenticateWithBiometrics_Success()` - успешная аутентификация
- [ ] `testAuthenticateWithBiometrics_Failure()` - неудачная аутентификация
- [ ] `testAuthenticateWithBiometrics_Unavailable()` - биометрия недоступна
- [ ] `testAuthenticateWithBiometrics_Cancelled()` - отмена пользователем

### **4.4 Тесты шифрования данных (20 минут)**
- [ ] `testEncryptData_Success()` - успешное шифрование
- [ ] `testDecryptData_Success()` - успешная расшифровка
- [ ] `testEncryptDecrypt_RoundTrip()` - полный цикл шифрование-расшифровка
- [ ] `testEncryptData_InvalidKey()` - невалидный ключ
- [ ] `testDecryptData_InvalidData()` - невалидные данные

### **4.5 Тесты безопасного хранения (10 минут)**
- [ ] `testStoreSecureData_Success()` - успешное сохранение
- [ ] `testRetrieveSecureData_Success()` - успешное получение
- [ ] `testDeleteSecureData_Success()` - успешное удаление
- [ ] `testStoreSecureData_EncryptionFails()` - ошибка шифрования

---

## ✅ ЭТАП 5: ТЕСТЫ ДЛЯ ParentalControlViewModel (1 час)

**Прогресс:** 0/5 групп тестов (0%)

### **5.1 Создать файл тестов (5 минут)**
- [ ] Создать `Tests/UnitTests/ParentalControlViewModelTests.swift`
- [ ] Создать класс `ParentalControlViewModelTests: XCTestCase`
- [ ] Настроить `setUp()` метод
- [ ] Настроить `tearDown()` метод
- [ ] Создать Mock ComponentStatusService

### **5.2 Тесты инициализации (10 минут)**
- [ ] `testInitialization()` - проверка инициализации
- [ ] `testInitialState()` - проверка начального состояния
- [ ] `testLoadChildren()` - загрузка детей

### **5.3 Тесты загрузки статусов компонентов (15 минут)**
- [ ] `testLoadComponentStatuses_Success()` - успешная загрузка
- [ ] `testLoadComponentStatuses_NetworkError()` - ошибка сети
- [ ] `testLoadComponentStatuses_DemoMode()` - демо-режим
- [ ] `testLoadComponentStatuses_ParallelLoading()` - параллельная загрузка

### **5.4 Тесты переключения компонентов (20 минут)**
- [ ] `testToggleSelfHarmDetection_Enable()` - включение Self Harm Detection
- [ ] `testToggleSelfHarmDetection_Disable()` - выключение Self Harm Detection
- [ ] `testToggleGroomingDetection()` - переключение Grooming Detection
- [ ] `testToggleOnlinePredators()` - переключение Online Predators
- [ ] `testTogglePsychologicalSupport()` - переключение Psychological Support
- [ ] `testToggleParentalControlBot()` - переключение Parental Control Bot
- [ ] `testToggle_NetworkError()` - ошибка сети при переключении

### **5.5 Тесты обновления статусов (10 минут)**
- [ ] `testUpdateStatusForComponent_SelfHarm()` - обновление статуса Self Harm
- [ ] `testUpdateStatusForComponent_Grooming()` - обновление статуса Grooming
- [ ] `testUpdateStatusForComponent_OnlinePredators()` - обновление статуса Online Predators

---

## ✅ ЭТАП 6: ФИНАЛЬНАЯ ПРОВЕРКА И ДОКУМЕНТАЦИЯ (30 минут)

**Прогресс:** 0/3 задач (0%)

### **6.1 Запуск всех тестов (10 минут)**
- [ ] Запустить все тесты через Xcode (Cmd+U)
- [ ] Проверить, что все тесты проходят
- [ ] Исправить ошибки компиляции, если есть
- [ ] Исправить падающие тесты, если есть

### **6.2 Проверка покрытия кода (10 минут)**
- [ ] Включить Code Coverage в Xcode (Edit Scheme → Test → Options → Code Coverage)
- [ ] Запустить тесты с Code Coverage
- [ ] Проверить покрытие для PaymentQRViewModel (цель: >80%)
- [ ] Проверить покрытие для CrashDetectionManager (цель: >80%)
- [ ] Проверить покрытие для SecurityManager (цель: >80%)
- [ ] Проверить покрытие для ParentalControlViewModel (цель: >80%)

### **6.3 Документация (10 минут)**
- [ ] Обновить README с информацией о тестах
- [ ] Добавить комментарии к тестам (описание что тестирует каждый тест)
- [ ] Создать краткую документацию по запуску тестов
- [ ] Добавить информацию о Mock объектах

---

## 📊 СТАТИСТИКА ПРОГРЕССА

### **По этапам:**
- **Этап 1 (Подготовка):** 0/3 (0%)
- **Этап 2 (PaymentQRViewModel):** 0/7 (0%)
- **Этап 3 (CrashDetectionManager):** 0/6 (0%)
- **Этап 4 (SecurityManager):** 0/5 (0%)
- **Этап 5 (ParentalControlViewModel):** 0/5 (0%)
- **Этап 6 (Финальная проверка):** 0/3 (0%)

### **По компонентам:**
- **PaymentQRViewModel:** 0/7 групп тестов (0%)
- **CrashDetectionManager:** 0/6 групп тестов (0%)
- **SecurityManager:** 0/5 групп тестов (0%)
- **ParentalControlViewModel:** 0/5 групп тестов (0%)

### **Общий прогресс:**
- **Всего задач:** 67
- **Выполнено:** 0
- **Осталось:** 67
- **Процент выполнения:** 0%

---

## 🎯 ПРИОРИТЕТЫ

### **Критичные (начать с них):**
1. ✅ **Этап 1** - Подготовка инфраструктуры (обязательно для всех остальных)
2. ✅ **Этап 2** - PaymentQRViewModel (платежи - критично!)
3. ✅ **Этап 3** - CrashDetectionManager (обнаружение аварий - критично!)

### **Важные:**
4. ✅ **Этап 4** - SecurityManager (безопасность)
5. ✅ **Этап 5** - ParentalControlViewModel (родительский контроль)

### **Финальные:**
6. ✅ **Этап 6** - Финальная проверка и документация

---

## 📝 ЗАМЕТКИ

### **Важные моменты:**
- Использовать MockAPIService вместо реального API
- Использовать `XCTestExpectation` для async операций
- Убедиться, что тесты выполняются на MainActor для @MainActor классов
- Каждый тест должен быть независимым
- Правильно очищать состояние в `tearDown()`

### **Проблемы и решения:**
- [ ] Проблема: _________________ → Решение: _________________
- [ ] Проблема: _________________ → Решение: _________________

---

## 🚀 БЫСТРЫЙ СТАРТ

### **Первые шаги:**
1. ✅ Создать протокол `APIServiceProtocol` (Этап 1.1)
2. ✅ Обновить APIService и MockAPIService (Этап 1.2)
3. ✅ Создать Mock зависимости (Этап 1.3)
4. ✅ Начать с PaymentQRViewModel (Этап 2)

---

**Документ создан:** 2026-02-06  
**Статус:** 📝 Готов к выполнению  
**Следующий шаг:** Начать с Этапа 1.1
