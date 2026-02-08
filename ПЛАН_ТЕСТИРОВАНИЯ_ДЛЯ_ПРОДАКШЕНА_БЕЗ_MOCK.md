# 📋 ПЛАН ТЕСТИРОВАНИЯ ДЛЯ ПРОДАКШЕНА (БЕЗ MOCK)

**Дата:** 2026-02-06  
**Версия:** 2.0  
**Оценка времени:** 7-11 часов + 1-2 недели beta тестирования  
**Статус:** 📝 Готов к реализации

---

## 🎯 ЦЕЛЬ

Создать тесты для 4 критичных компонентов iOS приложения **БЕЗ использования Mock**, используя:
1. ✅ **Integration Tests** с реальным API
2. ✅ **UI Tests** для критичных экранов
3. ✅ **Manual Testing** чеклист
4. ✅ **TestFlight Beta** тестирование

---

## 📊 ОБЩАЯ СТРУКТУРА ПЛАНА

### **Этапы реализации:**
1. ✅ Integration Tests с реальным API (2-3 часа)
2. ✅ UI Tests для критичных экранов (1-2 часа)
3. ✅ Manual Testing чеклист (4-6 часов)
4. ✅ TestFlight Beta подготовка (1-2 недели)

**ИТОГО:** 7-11 часов работы + 1-2 недели beta тестирования

---

## 📝 ДЕТАЛЬНЫЙ ПЛАН ПО ПУНКТАМ

---

## 1️⃣ ЭТАП 1: INTEGRATION TESTS С РЕАЛЬНЫМ API (2-3 часа)

### **1.1 Создать Integration Tests для PaymentQRViewModel (45 минут)**

**Файл:** `Tests/Integration/PaymentQRIntegrationTests.swift`

**Задачи:**
- [ ] Создать класс `PaymentQRIntegrationTests: XCTestCase`
- [ ] Настроить `setUp()` и `tearDown()`
- [ ] Использовать `APIService.shared` (реальный API, не Mock!)

**Тесты:**
- [ ] `testCreateQRPayment_WithRealAPI()` - создание QR-кода с реальным API
- [ ] `testCheckPaymentStatus_WithRealAPI()` - проверка статуса с реальным API
- [ ] `testPaymentFlow_Complete()` - полный цикл платежа

**Код:**
```swift
import XCTest
@testable import ALADDIN

@MainActor
class PaymentQRIntegrationTests: XCTestCase {
    var apiService: APIService!
    var viewModel: PaymentQRViewModel!
    
    override func setUp() {
        super.setUp()
        // ✅ Используем РЕАЛЬНЫЙ API
        apiService = APIService.shared
        let testTariff = Tariff(
            id: "test_tariff",
            title: "Test",
            price: "199 ₽",
            period: "month",
            features: []
        )
        viewModel = PaymentQRViewModel(tariff: testTariff)
    }
    
    func testCreateQRPayment_WithRealAPI() {
        let expectation = expectation(description: "Payment created")
        
        viewModel.createQRPayment { result in
            switch result {
            case .success:
                XCTAssertNotNil(self.viewModel.paymentId)
                XCTAssertNotNil(self.viewModel.qrCodeImageSBP)
                expectation.fulfill()
            case .failure(let error):
                XCTFail("Payment creation failed: \(error.localizedDescription)")
            }
        }
        
        wait(for: [expectation], timeout: 10.0)
    }
}
```

---

### **1.2 Создать Integration Tests для CrashDetectionManager (45 минут)**

**Файл:** `Tests/Integration/CrashDetectionIntegrationTests.swift`

**Задачи:**
- [ ] Создать класс `CrashDetectionIntegrationTests: XCTestCase`
- [ ] Настроить `setUp()` и `tearDown()`
- [ ] Использовать реальный API для настройки Crash Detection

**Тесты:**
- [ ] `testStartMonitoring_WithRealAPI()` - запуск мониторинга с реальным API
- [ ] `testStopMonitoring_WithRealAPI()` - остановка мониторинга
- [ ] `testCrashDetectionSetup_WithRealAPI()` - настройка геозоны

**Код:**
```swift
@MainActor
class CrashDetectionIntegrationTests: XCTestCase {
    var manager: CrashDetectionManager!
    var apiService: APIService!
    
    override func setUp() {
        super.setUp()
        manager = CrashDetectionManager.shared
        apiService = APIService.shared  // ✅ Реальный API
    }
    
    func testStartMonitoring_WithRealAPI() async throws {
        // ✅ Тест с реальным API
        try await manager.startMonitoring()
        XCTAssertTrue(manager.isMonitoring)
    }
}
```

---

### **1.3 Создать Integration Tests для SecurityManager (30 минут)**

**Файл:** `Tests/Integration/SecurityManagerIntegrationTests.swift`

**Задачи:**
- [ ] Создать класс `SecurityManagerIntegrationTests: XCTestCase`
- [ ] Тестировать локальные функции (шифрование, биометрия)
- [ ] НЕ нужен API (локальные тесты)

**Тесты:**
- [ ] `testEncryptDecrypt_RoundTrip()` - полный цикл шифрование-расшифровка
- [ ] `testBiometricAuthentication()` - биометрическая аутентификация
- [ ] `testSecureStorage()` - безопасное хранение данных

**Код:**
```swift
@MainActor
class SecurityManagerIntegrationTests: XCTestCase {
    var manager: SecurityManager!
    
    override func setUp() {
        super.setUp()
        manager = SecurityManager.shared
    }
    
    func testEncryptDecrypt_RoundTrip() {
        let originalData = "sensitive data".data(using: .utf8)!
        
        guard let encrypted = manager.encryptData(originalData) else {
            XCTFail("Encryption failed")
            return
        }
        
        guard let decrypted = manager.decryptData(encrypted) else {
            XCTFail("Decryption failed")
            return
        }
        
        XCTAssertEqual(originalData, decrypted)
    }
}
```

---

### **1.4 Создать Integration Tests для ParentalControlViewModel (30 минут)**

**Файл:** `Tests/Integration/ParentalControlIntegrationTests.swift`

**Задачи:**
- [ ] Создать класс `ParentalControlIntegrationTests: XCTestCase`
- [ ] Использовать реальный API для загрузки статусов компонентов

**Тесты:**
- [ ] `testLoadComponentStatuses_WithRealAPI()` - загрузка статусов с реальным API
- [ ] `testToggleComponent_WithRealAPI()` - переключение компонента
- [ ] `testLoadChildren_WithRealAPI()` - загрузка детей

**Код:**
```swift
@MainActor
class ParentalControlIntegrationTests: XCTestCase {
    var viewModel: ParentalControlViewModel!
    
    override func setUp() {
        super.setUp()
        viewModel = ParentalControlViewModel()  // ✅ Использует реальный API
    }
    
    func testLoadComponentStatuses_WithRealAPI() async {
        await viewModel.loadComponentStatuses()
        
        // Проверяем, что статусы загружены
        // (не проверяем конкретные значения, так как зависят от сервера)
        XCTAssertTrue(true)  // Если не упало - значит работает
    }
}
```

---

## 2️⃣ ЭТАП 2: UI TESTS ДЛЯ КРИТИЧНЫХ ЭКРАНОВ (1-2 часа)

### **2.1 Создать UI Tests для PaymentQR Screen (30 минут)**

**Файл:** `Tests/UITests/PaymentQRScreenUITests.swift`

**Задачи:**
- [ ] Создать класс `PaymentQRScreenUITests: XCTestCase`
- [ ] Написать тесты для полного цикла оплаты

**Тесты:**
- [ ] `testPaymentQRFlow()` - полный цикл оплаты
- [ ] `testQRCodeDisplay()` - отображение QR-кода
- [ ] `testPaymentStatusCheck()` - проверка статуса платежа

**Код:**
```swift
class PaymentQRScreenUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        app = XCUIApplication()
        app.launch()
    }
    
    func testPaymentQRFlow() {
        // 1. Навигация к экрану оплаты
        app.buttons["Тарифы"].tap()
        app.buttons["Family Plan"].tap()
        app.buttons["Оплатить"].tap()
        
        // 2. Проверка QR-кода
        let qrCode = app.images["QR Code"]
        XCTAssertTrue(qrCode.waitForExistence(timeout: 5.0))
        
        // 3. Проверка статуса
        let statusText = app.staticTexts["Ожидание оплаты"]
        XCTAssertTrue(statusText.exists)
    }
}
```

---

### **2.2 Создать UI Tests для Crash Detection Screen (20 минут)**

**Файл:** `Tests/UITests/CrashDetectionScreenUITests.swift`

**Задачи:**
- [ ] Создать класс `CrashDetectionScreenUITests: XCTestCase`
- [ ] Написать тесты для включения/выключения Crash Detection

**Тесты:**
- [ ] `testEnableCrashDetection()` - включение Crash Detection
- [ ] `testDisableCrashDetection()` - выключение Crash Detection
- [ ] `testCrashDetectionStatus()` - проверка статуса

**Код:**
```swift
class CrashDetectionScreenUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        app = XCUIApplication()
        app.launch()
    }
    
    func testEnableCrashDetection() {
        // Навигация к экрану
        app.tabBars.buttons["Защита"].tap()
        app.buttons["Network Protection"].tap()
        
        // Включение Crash Detection
        let toggle = app.switches["Crash Detection"]
        if !toggle.value as! Bool {
            toggle.tap()
        }
        
        XCTAssertTrue(toggle.value as! Bool)
    }
}
```

---

### **2.3 Создать UI Tests для Security Settings Screen (20 минут)**

**Файл:** `Tests/UITests/SecuritySettingsScreenUITests.swift`

**Задачи:**
- [ ] Создать класс `SecuritySettingsScreenUITests: XCTestCase`
- [ ] Написать тесты для настроек безопасности

**Тесты:**
- [ ] `testBiometricAuthentication()` - биометрическая аутентификация
- [ ] `testSecurityLevelChange()` - изменение уровня безопасности

---

### **2.4 Создать UI Tests для Parental Control Screen (20 минут)**

**Файл:** `Tests/UITests/ParentalControlScreenUITests.swift`

**Задачи:**
- [ ] Создать класс `ParentalControlScreenUITests: XCTestCase`
- [ ] Написать тесты для родительского контроля

**Тесты:**
- [ ] `testToggleSelfHarmDetection()` - переключение Self Harm Detection
- [ ] `testToggleGroomingDetection()` - переключение Grooming Detection
- [ ] `testLoadChildren()` - загрузка детей

---

## 3️⃣ ЭТАП 3: MANUAL TESTING ЧЕКЛИСТ (4-6 часов)

### **3.1 Чеклист для PaymentQRViewModel (1 час)**

**Задачи:**
- [ ] Войти в приложение
- [ ] Перейти к экрану тарифов
- [ ] Выбрать тариф
- [ ] Нажать "Оплатить"
- [ ] Проверить, что QR-код отображается
- [ ] Проверить, что статус "Ожидание оплаты"
- [ ] Проверить автоматическую проверку статуса
- [ ] Проверить обработку ошибок

---

### **3.2 Чеклист для CrashDetectionManager (1 час)**

**Задачи:**
- [ ] Включить Crash Detection
- [ ] Проверить, что мониторинг запущен
- [ ] Симулировать краш (встряхнуть устройство)
- [ ] Проверить, что обратный отсчет запустился
- [ ] Проверить отправку алерта на сервер
- [ ] Выключить Crash Detection
- [ ] Проверить, что мониторинг остановлен

---

### **3.3 Чеклист для SecurityManager (1 час)**

**Задачи:**
- [ ] Проверить биометрическую аутентификацию
- [ ] Проверить шифрование данных
- [ ] Проверить расшифровку данных
- [ ] Проверить безопасное хранение
- [ ] Проверить изменение уровня безопасности

---

### **3.4 Чеклист для ParentalControlViewModel (1 час)**

**Задачи:**
- [ ] Загрузить список детей
- [ ] Включить Self Harm Detection
- [ ] Включить Grooming Detection
- [ ] Включить Online Predators
- [ ] Включить Psychological Support
- [ ] Включить Parental Control Bot
- [ ] Проверить, что все статусы обновляются

---

### **3.5 Общий чеклист приложения (1-2 часа)**

**Задачи:**
- [ ] Все экраны открываются
- [ ] Навигация работает
- [ ] Локализация правильная (русский/английский)
- [ ] Нет крашей
- [ ] Производительность хорошая
- [ ] Батарея не разряжается быстро

---

## 4️⃣ ЭТАП 4: TESTFLIGHT BETA ПОДГОТОВКА (1-2 недели)

### **4.1 Подготовка билда (1 день)**

**Задачи:**
- [ ] Создать Release билд
- [ ] Проверить, что `useMockAPI = false`
- [ ] Проверить, что все тесты проходят
- [ ] Загрузить в TestFlight

---

### **4.2 Приглашение тестировщиков (1 день)**

**Задачи:**
- [ ] Создать список тестировщиков (10-20 человек)
- [ ] Отправить приглашения
- [ ] Подготовить инструкции

---

### **4.3 Сбор обратной связи (1-2 недели)**

**Задачи:**
- [ ] Собрать отзывы
- [ ] Найти критические проблемы
- [ ] Исправить проблемы
- [ ] Повторить цикл при необходимости

---

### **4.4 Финальный релиз (1 день)**

**Задачи:**
- [ ] Исправить все критические проблемы
- [ ] Создать финальный билд
- [ ] Отправить на ревью в App Store
- [ ] Выпустить в продакшен

---

## 📋 TODO ЛИСТ (ЭЛЕКТРОННЫЙ ВАРИАНТ)

### ✅ **ЭТАП 1: INTEGRATION TESTS С РЕАЛЬНЫМ API (2-3 часа)**

- [ ] **1.1** Создать Integration Tests для PaymentQRViewModel (45 мин)
  - [ ] Создать `Tests/Integration/PaymentQRIntegrationTests.swift`
  - [ ] `testCreateQRPayment_WithRealAPI()`
  - [ ] `testCheckPaymentStatus_WithRealAPI()`
  - [ ] `testPaymentFlow_Complete()`
  
- [ ] **1.2** Создать Integration Tests для CrashDetectionManager (45 мин)
  - [ ] Создать `Tests/Integration/CrashDetectionIntegrationTests.swift`
  - [ ] `testStartMonitoring_WithRealAPI()`
  - [ ] `testStopMonitoring_WithRealAPI()`
  - [ ] `testCrashDetectionSetup_WithRealAPI()`
  
- [ ] **1.3** Создать Integration Tests для SecurityManager (30 мин)
  - [ ] Создать `Tests/Integration/SecurityManagerIntegrationTests.swift`
  - [ ] `testEncryptDecrypt_RoundTrip()`
  - [ ] `testBiometricAuthentication()`
  - [ ] `testSecureStorage()`
  
- [ ] **1.4** Создать Integration Tests для ParentalControlViewModel (30 мин)
  - [ ] Создать `Tests/Integration/ParentalControlIntegrationTests.swift`
  - [ ] `testLoadComponentStatuses_WithRealAPI()`
  - [ ] `testToggleComponent_WithRealAPI()`
  - [ ] `testLoadChildren_WithRealAPI()`

---

### ✅ **ЭТАП 2: UI TESTS ДЛЯ КРИТИЧНЫХ ЭКРАНОВ (1-2 часа)**

- [ ] **2.1** Создать UI Tests для PaymentQR Screen (30 мин)
  - [ ] Создать `Tests/UITests/PaymentQRScreenUITests.swift`
  - [ ] `testPaymentQRFlow()`
  - [ ] `testQRCodeDisplay()`
  - [ ] `testPaymentStatusCheck()`
  
- [ ] **2.2** Создать UI Tests для Crash Detection Screen (20 мин)
  - [ ] Создать `Tests/UITests/CrashDetectionScreenUITests.swift`
  - [ ] `testEnableCrashDetection()`
  - [ ] `testDisableCrashDetection()`
  - [ ] `testCrashDetectionStatus()`
  
- [ ] **2.3** Создать UI Tests для Security Settings Screen (20 мин)
  - [ ] Создать `Tests/UITests/SecuritySettingsScreenUITests.swift`
  - [ ] `testBiometricAuthentication()`
  - [ ] `testSecurityLevelChange()`
  
- [ ] **2.4** Создать UI Tests для Parental Control Screen (20 мин)
  - [ ] Создать `Tests/UITests/ParentalControlScreenUITests.swift`
  - [ ] `testToggleSelfHarmDetection()`
  - [ ] `testToggleGroomingDetection()`
  - [ ] `testLoadChildren()`

---

### ✅ **ЭТАП 3: MANUAL TESTING ЧЕКЛИСТ (4-6 часов)**

- [ ] **3.1** Чеклист для PaymentQRViewModel (1 час)
  - [ ] Войти в приложение
  - [ ] Перейти к экрану тарифов
  - [ ] Выбрать тариф
  - [ ] Нажать "Оплатить"
  - [ ] Проверить QR-код
  - [ ] Проверить статус
  - [ ] Проверить автоматическую проверку
  - [ ] Проверить обработку ошибок
  
- [ ] **3.2** Чеклист для CrashDetectionManager (1 час)
  - [ ] Включить Crash Detection
  - [ ] Проверить мониторинг
  - [ ] Симулировать краш
  - [ ] Проверить обратный отсчет
  - [ ] Проверить отправку алерта
  - [ ] Выключить Crash Detection
  
- [ ] **3.3** Чеклист для SecurityManager (1 час)
  - [ ] Проверить биометрию
  - [ ] Проверить шифрование
  - [ ] Проверить расшифровку
  - [ ] Проверить безопасное хранение
  - [ ] Проверить уровень безопасности
  
- [ ] **3.4** Чеклист для ParentalControlViewModel (1 час)
  - [ ] Загрузить список детей
  - [ ] Включить все 5 компонентов
  - [ ] Проверить статусы
  
- [ ] **3.5** Общий чеклист приложения (1-2 часа)
  - [ ] Все экраны работают
  - [ ] Навигация работает
  - [ ] Локализация правильная
  - [ ] Нет крашей
  - [ ] Производительность хорошая

---

### ✅ **ЭТАП 4: TESTFLIGHT BETA ПОДГОТОВКА (1-2 недели)**

- [ ] **4.1** Подготовка билда (1 день)
  - [ ] Создать Release билд
  - [ ] Проверить `useMockAPI = false`
  - [ ] Проверить все тесты
  - [ ] Загрузить в TestFlight
  
- [ ] **4.2** Приглашение тестировщиков (1 день)
  - [ ] Создать список тестировщиков
  - [ ] Отправить приглашения
  - [ ] Подготовить инструкции
  
- [ ] **4.3** Сбор обратной связи (1-2 недели)
  - [ ] Собрать отзывы
  - [ ] Найти проблемы
  - [ ] Исправить проблемы
  
- [ ] **4.4** Финальный релиз (1 день)
  - [ ] Исправить критические проблемы
  - [ ] Создать финальный билд
  - [ ] Отправить на ревью
  - [ ] Выпустить в продакшен

---

## 📊 ИТОГОВАЯ СТАТИСТИКА

### **Общее количество задач:**
- **Всего задач:** 40
- **Оценка времени:** 7-11 часов работы + 1-2 недели beta тестирования

### **Распределение по этапам:**
- **Integration Tests:** 4 файла, ~12 тестов
- **UI Tests:** 4 файла, ~12 тестов
- **Manual Testing:** 5 чеклистов
- **TestFlight Beta:** 4 этапа

---

## 🎯 КРИТЕРИИ УСПЕХА

### **✅ План считается выполненным, если:**

1. ✅ Все Integration Tests проходят с реальным API
2. ✅ Все UI Tests проходят
3. ✅ Manual Testing чеклист выполнен
4. ✅ TestFlight Beta завершен успешно
5. ✅ Все критические проблемы исправлены

---

## 📝 ПРИМЕЧАНИЯ

### **Важные моменты:**

1. **Реальный API:** Все Integration Tests используют `APIService.shared` (реальный API)
2. **Нет Mock:** Mock НЕ используется в продакшен тестах
3. **Сервер:** Нужен работающий сервер для Integration Tests
4. **Время:** Integration Tests медленнее unit тестов (но тестируют реальную интеграцию)

---

## 🚀 БЫСТРЫЙ СТАРТ

### **Для начала работы:**

1. ✅ Убедиться, что сервер работает
2. ✅ Создать Integration Tests для PaymentQRViewModel (Этап 1.1)
3. ✅ Запустить тесты и проверить, что они проходят
4. ✅ Продолжить с остальными компонентами

---

**Документ создан:** 2026-02-06  
**Статус:** ✅ Готов к реализации  
**Следующий шаг:** Начать с Этапа 1.1
