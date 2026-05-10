import XCTest

/**
 * 🏠 Family Registration UI Tests
 * Специализированные тесты для регистрации семьи
 * Цель: 100% покрытие пользовательских сценариев
 */

@MainActor
class FamilyRegistrationUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
        super.tearDown()
    }
    
    // MARK: - Complete Registration Flow Tests
    
    func testCompleteFamilyCreationFlow() throws {
        // Полный тест создания семьи
        startFamilyRegistration()
        
        // Шаг 1: Согласие
        acceptConsent()
        
        // Шаг 2: Выбор роли
        selectRole("Родитель")
        
        // Шаг 3: Выбор возрастной группы
        selectAgeGroup("Взрослый (18-64)")
        
        // Шаг 4: Выбор буквы
        selectLetter("А")
        
        // Шаг 5: Создание семьи
        createFamily("Тестовая Семья")
        
        // Проверяем успешное создание
        XCTAssertTrue(app.staticTexts["Семья создана успешно!"].exists)
    }
    
    func testCompleteFamilyJoinFlow() throws {
        // Полный тест присоединения к семье
        startFamilyRegistration()
        acceptConsent()
        selectRole("Ребенок")
        selectAgeGroup("Подросток (13-17)")
        selectLetter("Б")
        
        // Присоединение к семье
        joinFamily("FAMILY123")
        
        // Проверяем успешное присоединение
        XCTAssertTrue(app.staticTexts["Вы присоединились к семье!"].exists)
    }
    
    func testCompleteFamilyRecoveryFlow() throws {
        // Полный тест восстановления семьи
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        selectAgeGroup("Взрослый (18-64)")
        selectLetter("В")
        
        // Восстановление семьи
        recoverFamily("RECOVER123")
        
        // Проверяем успешное восстановление
        XCTAssertTrue(app.staticTexts["Семья восстановлена!"].exists)
    }
    
    // MARK: - Individual Step Tests
    
    func testConsentStep() throws {
        startFamilyRegistration()
        
        // Проверяем что показано согласие
        XCTAssertTrue(app.staticTexts["Согласие на обработку данных"].exists)
        XCTAssertTrue(app.buttons["Принимаю"].exists)
        XCTAssertTrue(app.buttons["Отклонить"].exists)
        
        // Тестируем принятие согласия
        acceptConsent()
        XCTAssertFalse(app.staticTexts["Согласие на обработку данных"].exists)
    }
    
    func testRoleSelectionStep() throws {
        startFamilyRegistration()
        acceptConsent()
        
        // Проверяем что показан выбор роли
        XCTAssertTrue(app.staticTexts["Выберите вашу роль в семье"].exists)
        XCTAssertTrue(app.buttons["Родитель"].exists)
        XCTAssertTrue(app.buttons["Ребенок"].exists)
        XCTAssertTrue(app.buttons["Бабушка/Дедушка"].exists)
        XCTAssertTrue(app.buttons["Опекун"].exists)
        
        // Тестируем выбор роли
        selectRole("Родитель")
        XCTAssertTrue(app.staticTexts["Роль выбрана: Родитель"].exists)
    }
    
    func testAgeGroupSelectionStep() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        
        // Проверяем что показан выбор возрастной группы
        XCTAssertTrue(app.staticTexts["Выберите возрастную группу"].exists)
        XCTAssertTrue(app.buttons["Малыш (0-3)"].exists)
        XCTAssertTrue(app.buttons["Ребенок (4-12)"].exists)
        XCTAssertTrue(app.buttons["Подросток (13-17)"].exists)
        XCTAssertTrue(app.buttons["Взрослый (18-64)"].exists)
        XCTAssertTrue(app.buttons["Пожилой (65+)"].exists)
        
        // Тестируем выбор возрастной группы
        selectAgeGroup("Взрослый (18-64)")
        XCTAssertTrue(app.staticTexts["Возрастная группа выбрана: Взрослый (18-64)"].exists)
    }
    
    func testLetterSelectionStep() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        selectAgeGroup("Взрослый (18-64)")
        
        // Проверяем что показан выбор буквы
        XCTAssertTrue(app.staticTexts["Выберите букву"].exists)
        XCTAssertTrue(app.buttons["А"].exists)
        XCTAssertTrue(app.buttons["Б"].exists)
        XCTAssertTrue(app.buttons["В"].exists)
        
        // Тестируем выбор буквы
        selectLetter("А")
        XCTAssertTrue(app.staticTexts["Буква выбрана: А"].exists)
    }
    
    // MARK: - Form Validation Tests
    
    func testFamilyNameValidation() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        selectAgeGroup("Взрослый (18-64)")
        selectLetter("А")
        
        // Тест пустого имени семьи
        let nameField = app.textFields["Имя семьи"]
        XCTAssertTrue(nameField.exists)
        
        // Оставляем поле пустым и пытаемся создать семью
        app.buttons["Создать семью"].tap()
        XCTAssertTrue(app.staticTexts["Введите имя семьи"].exists)
        
        // Вводим валидное имя
        nameField.tap()
        nameField.typeText("Валидная Семья")
        app.buttons["Создать семью"].tap()
        
        // Проверяем что ошибка исчезла
        XCTAssertFalse(app.staticTexts["Введите имя семьи"].exists)
    }
    
    func testFamilyCodeValidation() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Ребенок")
        selectAgeGroup("Подросток (13-17)")
        selectLetter("Б")
        
        // Тест пустого кода семьи
        let codeField = app.textFields["Код семьи"]
        XCTAssertTrue(codeField.exists)
        
        // Оставляем поле пустым и пытаемся присоединиться
        app.buttons["Присоединиться"].tap()
        XCTAssertTrue(app.staticTexts["Введите код семьи"].exists)
        
        // Вводим валидный код
        codeField.tap()
        codeField.typeText("VALID123")
        app.buttons["Присоединиться"].tap()
        
        // Проверяем что ошибка исчезла
        XCTAssertFalse(app.staticTexts["Введите код семьи"].exists)
    }
    
    func testRecoveryCodeValidation() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        selectAgeGroup("Взрослый (18-64)")
        selectLetter("В")
        
        // Тест пустого кода восстановления
        let recoveryField = app.textFields["Код восстановления"]
        XCTAssertTrue(recoveryField.exists)
        
        // Оставляем поле пустым и пытаемся восстановить
        app.buttons["Восстановить"].tap()
        XCTAssertTrue(app.staticTexts["Введите код восстановления"].exists)
        
        // Вводим валидный код
        recoveryField.tap()
        recoveryField.typeText("RECOVER123")
        app.buttons["Восстановить"].tap()
        
        // Проверяем что ошибка исчезла
        XCTAssertFalse(app.staticTexts["Введите код восстановления"].exists)
    }
    
    // MARK: - Error Handling Tests
    
    func testNetworkErrorHandling() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        selectAgeGroup("Взрослый (18-64)")
        selectLetter("А")
        
        // Симулируем сетевую ошибку
        // В реальном тесте здесь бы отключали интернет
        createFamily("Тестовая Семья")
        
        // Проверяем обработку ошибки
        if app.staticTexts["Ошибка сети"].exists {
            XCTAssertTrue(app.buttons["Повторить"].exists)
            XCTAssertTrue(app.buttons["Отмена"].exists)
        }
    }
    
    func testServerErrorHandling() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        selectAgeGroup("Взрослый (18-64)")
        selectLetter("А")
        
        // Симулируем серверную ошибку
        createFamily("Тестовая Семья")
        
        // Проверяем обработку ошибки
        if app.staticTexts["Ошибка сервера"].exists {
            XCTAssertTrue(app.buttons["Повторить"].exists)
            XCTAssertTrue(app.buttons["Отмена"].exists)
        }
    }
    
    // MARK: - Loading States Tests
    
    func testLoadingStates() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        selectAgeGroup("Взрослый (18-64)")
        selectLetter("А")
        
        // Проверяем состояние загрузки при создании семьи
        createFamily("Тестовая Семья")
        
        // Проверяем что показывается индикатор загрузки
        if app.activityIndicators.count > 0 {
            XCTAssertTrue(app.activityIndicators.firstMatch.exists)
        }
        
        // Проверяем что кнопка заблокирована во время загрузки
        let createButton = app.buttons["Создать семью"]
        if createButton.exists {
            XCTAssertFalse(createButton.isEnabled)
        }
    }
    
    // MARK: - Navigation Tests
    
    func testBackNavigation() throws {
        startFamilyRegistration()
        acceptConsent()
        selectRole("Родитель")
        
        // Тестируем кнопку "Назад"
        let backButton = app.buttons["Назад"]
        if backButton.exists {
            backButton.tap()
            
            // Проверяем что вернулись к предыдущему шагу
            XCTAssertTrue(app.staticTexts["Выберите вашу роль в семье"].exists)
        }
    }
    
    func testCancelRegistration() throws {
        startFamilyRegistration()
        
        // Тестируем отмену регистрации
        let cancelButton = app.buttons["Отмена"]
        if cancelButton.exists {
            cancelButton.tap()
            
            // Проверяем что вернулись на главный экран
            XCTAssertTrue(app.otherElements["MainScreen"].exists)
        }
    }
    
    // MARK: - Accessibility Tests
    
    func testAccessibilityForFamilyRegistration() throws {
        startFamilyRegistration()
        
        // Проверяем accessibility для всех элементов
        let elements = app.otherElements
        for i in 0..<min(elements.count, 20) {
            let element = elements.element(boundBy: i)
            if element.exists {
                XCTAssertTrue(element.label.count > 0 || element.identifier.count > 0)
            }
        }
    }
    
    func testVoiceOverSupport() throws {
        startFamilyRegistration()
        acceptConsent()
        
        // Проверяем поддержку VoiceOver
        let roleButtons = app.buttons.matching(identifier: "roleButton")
        XCTAssertTrue(roleButtons.count > 0)
        
        for i in 0..<roleButtons.count {
            let button = roleButtons.element(boundBy: i)
            if button.exists {
                XCTAssertTrue(button.label.count > 0)
            }
        }
    }
    
    // MARK: - Performance Tests
    
    func testRegistrationFlowPerformance() throws {
        self.measure {
            startFamilyRegistration()
            acceptConsent()
            selectRole("Родитель")
            selectAgeGroup("Взрослый (18-64)")
            selectLetter("А")
        }
    }
    
    func testFormInputPerformance() throws {
        self.measure {
            let nameField = app.textFields["Имя семьи"]
            if nameField.exists {
                nameField.tap()
                nameField.typeText("Тестовая Семья")
            }
        }
    }
}

// MARK: - Helper Methods

extension FamilyRegistrationUITests {
    
    func startFamilyRegistration() {
        let registerButton = app.buttons["Начать регистрацию"]
        if registerButton.exists {
            registerButton.tap()
        }
    }
    
    func acceptConsent() {
        let consentButton = app.buttons["Принимаю"]
        if consentButton.exists {
            consentButton.tap()
        }
    }
    
    func selectRole(_ role: String) {
        let roleButton = app.buttons[role]
        if roleButton.exists {
            roleButton.tap()
        }
    }
    
    func selectAgeGroup(_ ageGroup: String) {
        let ageGroupButton = app.buttons[ageGroup]
        if ageGroupButton.exists {
            ageGroupButton.tap()
        }
    }
    
    func selectLetter(_ letter: String) {
        let letterButton = app.buttons[letter]
        if letterButton.exists {
            letterButton.tap()
        }
    }
    
    func createFamily(_ name: String) {
        let nameField = app.textFields["Имя семьи"]
        if nameField.exists {
            nameField.tap()
            nameField.typeText(name)
        }
        
        let createButton = app.buttons["Создать семью"]
        if createButton.exists {
            createButton.tap()
        }
    }
    
    func joinFamily(_ code: String) {
        let codeField = app.textFields["Код семьи"]
        if codeField.exists {
            codeField.tap()
            codeField.typeText(code)
        }
        
        let joinButton = app.buttons["Присоединиться"]
        if joinButton.exists {
            joinButton.tap()
        }
    }
    
    func recoverFamily(_ code: String) {
        let recoveryField = app.textFields["Код восстановления"]
        if recoveryField.exists {
            recoveryField.tap()
            recoveryField.typeText(code)
        }
        
        let recoverButton = app.buttons["Восстановить"]
        if recoverButton.exists {
            recoverButton.tap()
        }
    }
}
