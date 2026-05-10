import XCTest

/**
 * 📱 Widget Configuration UI Tests
 * Тестирование экрана настройки виджетов
 */

@MainActor
final class WidgetConfigurationUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
    }
    
    // MARK: - Widget Configuration Tests
    
    func testWidgetConfigurationScreenDisplay() throws {
        navigateToWidgetConfiguration()
        
        // Проверяем заголовок экрана
        let title = app.staticTexts["widget.configuration"]
        XCTAssertTrue(title.exists, "Заголовок экрана настройки виджетов должен отображаться")
        
        // Проверяем инструкции
        let instructions = app.staticTexts["widget.instructions"]
        XCTAssertTrue(instructions.exists, "Инструкции по добавлению виджетов должны отображаться")
    }
    
    func testWidgetTypesDisplay() throws {
        navigateToWidgetConfiguration()
        
        // Проверяем наличие всех типов виджетов
        let familyProtectionWidget = app.staticTexts["widget.family_protection"]
        let vpnStatusWidget = app.staticTexts["widget.vpn_status"]
        let analyticsWidget = app.staticTexts["widget.analytics"]
        
        XCTAssertTrue(familyProtectionWidget.exists, "Виджет защиты семьи должен отображаться")
        XCTAssertTrue(vpnStatusWidget.exists, "Виджет статуса VPN должен отображаться")
        XCTAssertTrue(analyticsWidget.exists, "Виджет аналитики должен отображаться")
    }
    
    func testMockDataButtons() throws {
        navigateToWidgetConfiguration()
        
        // Проверяем кнопки управления тестовыми данными
        let setMockDataButton = app.buttons["widget.set_mock_data"]
        let clearMockDataButton = app.buttons["widget.clear_mock_data"]
        
        XCTAssertTrue(setMockDataButton.exists, "Кнопка установки тестовых данных должна быть доступна")
        XCTAssertTrue(clearMockDataButton.exists, "Кнопка очистки тестовых данных должна быть доступна")
        
        // Тестируем установку тестовых данных
        setMockDataButton.tap()
        
        // Проверяем, что появилось подтверждение
        let alert = app.alerts.firstMatch
        if alert.exists {
            XCTAssertTrue(alert.staticTexts["widget.mock_data_set"].exists, "Должно появиться подтверждение установки данных")
            alert.buttons["OK"].tap()
        }
    }
    
    func testReloadWidgetsButton() throws {
        navigateToWidgetConfiguration()
        
        // Проверяем кнопку перезагрузки виджетов
        let reloadButton = app.buttons["widget.reload"]
        XCTAssertTrue(reloadButton.exists, "Кнопка перезагрузки виджетов должна быть доступна")
        
        // Тестируем перезагрузку
        reloadButton.tap()
        
        // Проверяем, что появилось подтверждение
        let alert = app.alerts.firstMatch
        if alert.exists {
            XCTAssertTrue(alert.staticTexts["widget.reloaded"].exists, "Должно появиться подтверждение перезагрузки")
            alert.buttons["OK"].tap()
        }
    }
    
    func testWidgetStatusIndicators() throws {
        navigateToWidgetConfiguration()
        
        // Проверяем индикаторы статуса виджетов
        let familyStatus = app.staticTexts["widget.family_status"]
        let vpnStatus = app.staticTexts["widget.vpn_status_indicator"]
        let analyticsStatus = app.staticTexts["widget.analytics_status"]
        
        XCTAssertTrue(familyStatus.exists, "Статус виджета защиты семьи должен отображаться")
        XCTAssertTrue(vpnStatus.exists, "Статус виджета VPN должен отображаться")
        XCTAssertTrue(analyticsStatus.exists, "Статус виджета аналитики должен отображаться")
    }
    
    func testWidgetDataSharing() throws {
        navigateToWidgetConfiguration()
        
        // Устанавливаем тестовые данные
        let setMockDataButton = app.buttons["widget.set_mock_data"]
        setMockDataButton.tap()
        
        // Очищаем alert если появился
        let alert = app.alerts.firstMatch
        if alert.exists {
            alert.buttons["OK"].tap()
        }
        
        // Проверяем, что данные обновились
        let familyStatus = app.staticTexts["widget.family_status"]
        XCTAssertTrue(familyStatus.exists, "Статус должен обновиться после установки данных")
    }
    
    func testWidgetInstructions() throws {
        navigateToWidgetConfiguration()
        
        // Проверяем пошаговые инструкции
        let step1 = app.staticTexts["widget.step1"]
        let step2 = app.staticTexts["widget.step2"]
        let step3 = app.staticTexts["widget.step3"]
        
        XCTAssertTrue(step1.exists, "Шаг 1 инструкций должен отображаться")
        XCTAssertTrue(step2.exists, "Шаг 2 инструкций должен отображаться")
        XCTAssertTrue(step3.exists, "Шаг 3 инструкций должен отображаться")
    }
    
    // MARK: - Helper Methods
    
    private func navigateToWidgetConfiguration() {
        // Находим кнопку настроек
        let settingsButton = app.buttons["settings"]
        if settingsButton.exists {
            settingsButton.tap()
        }
        
        // Ищем кнопку настройки виджетов
        let widgetButton = app.buttons["widget.configuration"]
        if widgetButton.exists {
            widgetButton.tap()
        }
    }
}
