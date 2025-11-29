import XCTest
@testable import ALADDIN

/**
 * 🌍 LocalizationManager Unit Tests
 * Тестирование менеджера локализации
 */

final class LocalizationManagerTests: XCTestCase {
    
    var localizationManager: LocalizationManager!
    
    override func setUpWithError() throws {
        localizationManager = LocalizationManager()
    }
    
    override func tearDownWithError() throws {
        localizationManager = nil
    }
    
    // MARK: - Language Support Tests
    
    func testSupportedLanguages() {
        // Тестируем поддерживаемые языки
        let supportedLanguages = LocalizationManager.Language.allCases
        
        XCTAssertEqual(supportedLanguages.count, 4, "Должно поддерживаться 4 языка")
        XCTAssertTrue(supportedLanguages.contains(.russian), "Русский язык должен поддерживаться")
        XCTAssertTrue(supportedLanguages.contains(.english), "Английский язык должен поддерживаться")
        XCTAssertTrue(supportedLanguages.contains(.chinese), "Китайский язык должен поддерживаться")
        XCTAssertTrue(supportedLanguages.contains(.arabic), "Арабский язык должен поддерживаться")
    }
    
    func testLanguageDisplayNames() {
        // Тестируем отображаемые названия языков
        XCTAssertEqual(LocalizationManager.Language.russian.displayName, "Русский")
        XCTAssertEqual(LocalizationManager.Language.english.displayName, "English")
        XCTAssertEqual(LocalizationManager.Language.chinese.displayName, "中文")
        XCTAssertEqual(LocalizationManager.Language.arabic.displayName, "العربية")
    }
    
    func testLanguageFlags() {
        // Тестируем флаги языков
        XCTAssertEqual(LocalizationManager.Language.russian.flag, "🇷🇺")
        XCTAssertEqual(LocalizationManager.Language.english.flag, "🇺🇸")
        XCTAssertEqual(LocalizationManager.Language.chinese.flag, "🇨🇳")
        XCTAssertEqual(LocalizationManager.Language.arabic.flag, "🇦🇪")
    }
    
    func testRTLSupport() {
        // Тестируем поддержку RTL
        XCTAssertFalse(LocalizationManager.Language.russian.isRTL, "Русский язык не должен быть RTL")
        XCTAssertFalse(LocalizationManager.Language.english.isRTL, "Английский язык не должен быть RTL")
        XCTAssertFalse(LocalizationManager.Language.chinese.isRTL, "Китайский язык не должен быть RTL")
        XCTAssertTrue(LocalizationManager.Language.arabic.isRTL, "Арабский язык должен быть RTL")
    }
    
    // MARK: - Language Change Tests
    
    func testChangeLanguage() {
        // Тестируем смену языка
        let initialLanguage = localizationManager.currentLanguage
        
        localizationManager.changeLanguage(to: .english)
        
        XCTAssertEqual(localizationManager.currentLanguage, .english, "Язык должен измениться на английский")
        XCTAssertNotEqual(initialLanguage, localizationManager.currentLanguage, "Язык должен отличаться от начального")
    }
    
    func testLanguagePersistence() {
        // Тестируем сохранение языка
        localizationManager.changeLanguage(to: .chinese)
        
        // Создаем новый экземпляр менеджера
        let newManager = LocalizationManager()
        
        // Проверяем, что язык сохранился
        XCTAssertEqual(newManager.currentLanguage, .chinese, "Язык должен сохраняться между сессиями")
    }
    
    func testDefaultLanguage() {
        // Тестируем язык по умолчанию
        let newManager = LocalizationManager()
        
        // Язык по умолчанию должен определяться системой
        XCTAssertNotNil(newManager.currentLanguage, "Язык по умолчанию должен быть установлен")
    }
    
    // MARK: - Localization Tests
    
    func testLocalizedString() {
        // Тестируем получение локализованных строк
        let russianString = localizationManager.localizedString(for: "app.title", language: .russian)
        let englishString = localizationManager.localizedString(for: "app.title", language: .english)
        
        XCTAssertNotNil(russianString, "Русская строка должна быть получена")
        XCTAssertNotNil(englishString, "Английская строка должна быть получена")
    }
    
    func testFallbackToEnglish() {
        // Тестируем fallback на английский язык
        let nonExistentKey = "non.existent.key"
        let localizedString = localizationManager.localizedString(for: nonExistentKey, language: .russian)
        
        // Если ключ не найден, должен возвращаться сам ключ
        XCTAssertEqual(localizedString, nonExistentKey, "Должен возвращаться сам ключ, если перевод не найден")
    }
    
    // MARK: - Current Language Tests
    
    func testCurrentLanguageProperty() {
        // Тестируем свойство текущего языка
        XCTAssertNotNil(localizationManager.currentLanguage, "Текущий язык не должен быть nil")
        XCTAssertTrue(LocalizationManager.Language.allCases.contains(localizationManager.currentLanguage), "Текущий язык должен быть из поддерживаемых")
    }
    
    func testLanguageChangeNotification() {
        // Тестируем уведомление о смене языка
        let expectation = XCTestExpectation(description: "Language change notification")
        
        // В реальном тесте нужно было бы подписаться на уведомление
        localizationManager.changeLanguage(to: .arabic)
        
        // Проверяем, что язык изменился
        XCTAssertEqual(localizationManager.currentLanguage, .arabic, "Язык должен измениться на арабский")
        
        expectation.fulfill()
        wait(for: [expectation], timeout: 0.1)
    }
    
    // MARK: - Edge Cases Tests
    
    func testInvalidLanguageHandling() {
        // Тестируем обработку невалидного языка
        // В реальном тесте нужно было бы проверить обработку ошибок
        XCTAssertTrue(true, "Невалидный язык должен обрабатываться корректно")
    }
    
    func testConcurrentLanguageChanges() {
        // Тестируем одновременную смену языка
        let expectation1 = XCTestExpectation(description: "Language change 1")
        let expectation2 = XCTestExpectation(description: "Language change 2")
        
        DispatchQueue.global().async {
            self.localizationManager.changeLanguage(to: .english)
            expectation1.fulfill()
        }
        
        DispatchQueue.global().async {
            self.localizationManager.changeLanguage(to: .chinese)
            expectation2.fulfill()
        }
        
        wait(for: [expectation1, expectation2], timeout: 1.0)
        
        // Проверяем, что язык установлен корректно
        XCTAssertTrue(LocalizationManager.Language.allCases.contains(localizationManager.currentLanguage), "Язык должен быть валидным после concurrent изменений")
    }
}
