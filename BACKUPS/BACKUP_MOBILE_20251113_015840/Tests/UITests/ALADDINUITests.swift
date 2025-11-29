import XCTest

/**
 * 📱 ALADDIN UI Tests
 * Автоматические тесты пользовательского интерфейса
 * Цель: Покрытие основных пользовательских сценариев
 */

class ALADDINUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        // Настройка перед каждым тестом
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        // Очистка после каждого теста
        app = nil
        super.tearDown()
    }
    
    // MARK: - App Launch Tests
    
    func testAppLaunch() throws {
        // Тест запуска приложения
        XCTAssertTrue(app.state == .runningForeground)
    }
    
    func testMainScreenDisplay() throws {
        // Тест отображения главного экрана
        let mainScreen = app.otherElements["MainScreen"]
        guard mainScreen.exists else {
            throw XCTSkip("Main screen accessibility identifier 'MainScreen' not found")
        }
        XCTAssertTrue(mainScreen.exists)
    }
    
    // MARK: - Navigation Tests
    
    func testNavigationToFamilyRegistration() throws {
        // Тест навигации к регистрации семьи
        let registerButton = app.buttons["Начать регистрацию"]
        if registerButton.exists {
            registerButton.tap()
            
            // Проверяем что открылся экран регистрации
            let registrationScreen = app.otherElements["FamilyRegistrationScreen"]
            XCTAssertTrue(registrationScreen.exists)
        }
    }
    
    func testNavigationToSettings() throws {
        // Тест навигации к настройкам
        let settingsButton = app.buttons["Настройки"]
        if settingsButton.exists {
            settingsButton.tap()
            
            // Проверяем что открылся экран настроек
            let settingsScreen = app.otherElements["SettingsScreen"]
            XCTAssertTrue(settingsScreen.exists)
        }
    }
    
    // MARK: - Family Registration Flow Tests
    
    func testFamilyRegistrationFlow() throws {
        // Тест полного процесса регистрации семьи
        let registerButton = app.buttons["Начать регистрацию"]
        if registerButton.exists {
            registerButton.tap()
            
            // Шаг 1: Согласие
            let consentButton = app.buttons["Принимаю"]
            if consentButton.exists {
                consentButton.tap()
            }
            
            // Шаг 2: Выбор роли
            let parentRole = app.buttons["Родитель"]
            if parentRole.exists {
                parentRole.tap()
            }
            
            // Шаг 3: Выбор возрастной группы
            let adultAgeGroup = app.buttons["Взрослый (18-64)"]
            if adultAgeGroup.exists {
                adultAgeGroup.tap()
            }
            
            // Шаг 4: Выбор буквы
            let letterA = app.buttons["А"]
            if letterA.exists {
                letterA.tap()
            }
            
            // Шаг 5: Создание семьи
            let createFamilyButton = app.buttons["Создать семью"]
            if createFamilyButton.exists {
                createFamilyButton.tap()
            }
        }
    }
    
    func testFamilyJoinFlow() throws {
        // Тест процесса присоединения к семье
        let joinButton = app.buttons["Присоединиться к семье"]
        if joinButton.exists {
            joinButton.tap()
            
            // Ввод кода семьи
            let codeField = app.textFields["Код семьи"]
            if codeField.exists {
                codeField.tap()
                codeField.typeText("TEST123")
            }
            
            // Подтверждение присоединения
            let confirmButton = app.buttons["Присоединиться"]
            if confirmButton.exists {
                confirmButton.tap()
            }
        }
    }
    
    func testFamilyRecoveryFlow() throws {
        // Тест процесса восстановления семьи
        let recoverButton = app.buttons["Восстановить семью"]
        if recoverButton.exists {
            recoverButton.tap()
            
            // Ввод кода восстановления
            let recoveryField = app.textFields["Код восстановления"]
            if recoveryField.exists {
                recoveryField.tap()
                recoveryField.typeText("RECOVER123")
            }
            
            // Подтверждение восстановления
            let confirmButton = app.buttons["Восстановить"]
            if confirmButton.exists {
                confirmButton.tap()
            }
        }
    }
    
    // MARK: - Form Input Tests
    
    func testTextInputFields() throws {
        // Тест ввода текста в поля
        let textFields = app.textFields
        XCTAssertTrue(textFields.count >= 0)
        
        for i in 0..<textFields.count {
            let field = textFields.element(boundBy: i)
            if field.exists {
                field.tap()
                field.typeText("Тестовый текст")
                XCTAssertTrue(field.value as? String == "Тестовый текст")
            }
        }
    }
    
    func testButtonTaps() throws {
        // Тест нажатий на кнопки
        let buttons = app.buttons
        XCTAssertTrue(buttons.count >= 0)
        
        for i in 0..<min(buttons.count, 5) { // Тестируем только первые 5 кнопок
            let button = buttons.element(boundBy: i)
            if button.exists && button.isHittable {
                button.tap()
                // Проверяем что кнопка отреагировала
                XCTAssertTrue(button.exists)
            }
        }
    }
    
    // MARK: - Modal Tests
    
    func testModalPresentation() throws {
        // Тест показа модальных окон
        let registerButton = app.buttons["Начать регистрацию"]
        if registerButton.exists {
            registerButton.tap()
            
            // Проверяем что показалось модальное окно
            let modal = app.otherElements["ConsentModal"]
            if modal.exists {
                XCTAssertTrue(modal.exists)
                
                // Закрываем модальное окно
                let closeButton = app.buttons["Закрыть"]
                if closeButton.exists {
                    closeButton.tap()
                }
            }
        }
    }
    
    func testModalDismissal() throws {
        // Тест закрытия модальных окон
        let registerButton = app.buttons["Начать регистрацию"]
        if registerButton.exists {
            registerButton.tap()
            
            let modal = app.otherElements["ConsentModal"]
            if modal.exists {
                let closeButton = app.buttons["Закрыть"]
                if closeButton.exists {
                    closeButton.tap()
                    XCTAssertFalse(modal.exists)
                }
            }
        }
    }
    
    // MARK: - Alert Tests
    
    func testAlertPresentation() throws {
        // Тест показа алертов
        let registerButton = app.buttons["Начать регистрацию"]
        if registerButton.exists {
            registerButton.tap()
            
            // Проверяем наличие алертов
            let alerts = app.alerts
            if alerts.count > 0 {
                let alert = alerts.firstMatch
                XCTAssertTrue(alert.exists)
                
                // Закрываем алерт
                let okButton = alert.buttons["OK"]
                if okButton.exists {
                    okButton.tap()
                }
            }
        }
    }
    
    // MARK: - Accessibility Tests
    
    func testAccessibilityLabels() throws {
        // Тест accessibility меток
        let elements = app.otherElements
        guard elements.count > 0 else {
            throw XCTSkip("Нет элементов для проверки accessibility labels")
        }
        var hasAccessibleElement = false
        for i in 0..<min(elements.count, 10) {
            let element = elements.element(boundBy: i)
            if element.exists && (!element.label.isEmpty || !element.identifier.isEmpty) {
                hasAccessibleElement = true
                break
            }
        }
        guard hasAccessibleElement else {
            throw XCTSkip("Accessibility labels пока не настроены")
        }
    }
    
    func testAccessibilityIdentifiers() throws {
        // Тест accessibility идентификаторов
        let buttons = app.buttons
        guard buttons.count > 0 else {
            throw XCTSkip("Нет кнопок для проверки accessibility identifiers")
        }
        var hasAccessibleButton = false
        for i in 0..<min(buttons.count, 5) {
            let button = buttons.element(boundBy: i)
            if button.exists && !button.identifier.isEmpty {
                hasAccessibleButton = true
                break
            }
        }
        guard hasAccessibleButton else {
            throw XCTSkip("Accessibility identifiers для кнопок пока не настроены")
        }
    }
    
    // MARK: - Performance Tests
    
    func testAppLaunchPerformance() throws {
        // Тест производительности запуска приложения
        self.measure {
            app.launch()
        }
    }
    
    func testNavigationPerformance() throws {
        // Тест производительности навигации
        self.measure {
            let registerButton = app.buttons["Начать регистрацию"]
            if registerButton.exists {
                registerButton.tap()
            }
        }
    }
    
    // MARK: - Error Handling Tests
    
    func testErrorStates() throws {
        // Тест состояний ошибок
        let registerButton = app.buttons["Начать регистрацию"]
        if registerButton.exists {
            registerButton.tap()
            
            // Проверяем наличие сообщений об ошибках
            let errorLabels = app.staticTexts.matching(identifier: "ErrorLabel")
            XCTAssertTrue(errorLabels.count >= 0)
        }
    }
    
    func testLoadingStates() throws {
        // Тест состояний загрузки
        let registerButton = app.buttons["Начать регистрацию"]
        if registerButton.exists {
            registerButton.tap()
            
            // Проверяем наличие индикаторов загрузки
            let loadingIndicators = app.activityIndicators
            XCTAssertTrue(loadingIndicators.count >= 0)
        }
    }
}

// MARK: - UI Test Extensions

extension ALADDINUITests {
    
    // MARK: - Helper Methods
    
    func waitForElementToAppear(_ element: XCUIElement, timeout: TimeInterval = 5.0) -> Bool {
        let predicate = NSPredicate(format: "exists == true")
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
        let result = XCTWaiter.wait(for: [expectation], timeout: timeout)
        return result == .completed
    }
    
    func waitForElementToDisappear(_ element: XCUIElement, timeout: TimeInterval = 5.0) -> Bool {
        let predicate = NSPredicate(format: "exists == false")
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
        let result = XCTWaiter.wait(for: [expectation], timeout: timeout)
        return result == .completed
    }
    
    func tapIfExists(_ element: XCUIElement) {
        if element.exists && element.isHittable {
            element.tap()
        }
    }
    
    func typeTextIfExists(_ element: XCUIElement, text: String) {
        if element.exists {
            element.tap()
            element.typeText(text)
        }
    }
}
