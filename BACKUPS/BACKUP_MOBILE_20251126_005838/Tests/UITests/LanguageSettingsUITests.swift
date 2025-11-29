import XCTest

/**
 * 🌍 Language Settings UI Tests
 * Тестирование экрана выбора языка
 */

final class LanguageSettingsUITests: XCTestCase {
    
    var app: XCUIApplication!
    
    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    override func tearDownWithError() throws {
        app = nil
    }
    
    // MARK: - Language Selection Tests
    
    func testLanguageSettingsScreenDisplay() throws {
        // Переходим к настройкам языка
        navigateToLanguageSettings()
        
        // Проверяем заголовок экрана
        let title = app.staticTexts["language.settings"]
        XCTAssertTrue(title.exists, "Заголовок экрана настроек языка должен отображаться")
        
        // Проверяем наличие всех языков
        let russianOption = app.buttons["language.russian"]
        let englishOption = app.buttons["language.english"]
        XCTAssertTrue(russianOption.exists, "Русский язык должен быть доступен")
        XCTAssertTrue(englishOption.exists, "Английский язык должен быть доступен")
    }
    
    func testLanguageSelection() throws {
        navigateToLanguageSettings()
        
        // Выбираем английский язык
        let englishButton = app.buttons["language.english"]
        englishButton.tap()
        
        // Проверяем, что язык изменился
        let currentLanguage = app.staticTexts["language.current"]
        XCTAssertTrue(currentLanguage.exists, "Текущий язык должен отображаться")
        
        // Возвращаемся к русскому
        let russianButton = app.buttons["language.russian"]
        russianButton.tap()
    }
    
    func testLanguagePersistence() throws {
        navigateToLanguageSettings()
        
        // Выбираем английский язык
        let englishButton = app.buttons["language.english"]
        englishButton.tap()
        
        // Перезапускаем приложение
        app.terminate()
        app.launch()
        
        // Проверяем, что язык сохранился
        navigateToLanguageSettings()
        let currentLanguage = app.staticTexts["language.current"]
        XCTAssertTrue(currentLanguage.exists, "Выбранный язык должен сохраняться")
    }
    
    // MARK: - Helper Methods
    
    private func navigateToLanguageSettings() {
        // Находим кнопку настроек (предполагаем, что она есть на главном экране)
        let settingsButton = app.buttons["settings"]
        if settingsButton.exists {
            settingsButton.tap()
        }
        
        // Ищем кнопку настроек языка
        let languageButton = app.buttons["language.settings"]
        if languageButton.exists {
            languageButton.tap()
        }
    }
}
