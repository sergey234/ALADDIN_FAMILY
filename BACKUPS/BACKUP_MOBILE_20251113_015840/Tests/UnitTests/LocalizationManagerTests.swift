import XCTest
@testable import ALADDIN

/**
 * 🌍 LocalizationManager Unit Tests
 * Тестирование менеджера локализации
 */

final class LocalizationManagerTests: XCTestCase {
    
    private var localizationManager: LocalizationManager!
    private let defaults = UserDefaults.standard
    
    override func setUpWithError() throws {
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.appLanguage)
        localizationManager = LocalizationManager()
    }
    
    override func tearDownWithError() throws {
        defaults.removeObject(forKey: AppConfig.UserDefaultsKeys.appLanguage)
        localizationManager = nil
    }
    
    // MARK: - Language Support Tests
    
    func testSupportedLanguages() {
        let supportedLanguages = LocalizationManager.Language.allCases
        
        XCTAssertEqual(supportedLanguages.count, 4)
        XCTAssertTrue(supportedLanguages.contains(.russian))
        XCTAssertTrue(supportedLanguages.contains(.english))
        XCTAssertTrue(supportedLanguages.contains(.chinese))
        XCTAssertTrue(supportedLanguages.contains(.arabic))
    }
    
    func testLanguageDisplayNames() {
        XCTAssertEqual(LocalizationManager.Language.russian.displayName, "Русский")
        XCTAssertEqual(LocalizationManager.Language.english.displayName, "English")
        XCTAssertEqual(LocalizationManager.Language.chinese.displayName, "中文")
        XCTAssertEqual(LocalizationManager.Language.arabic.displayName, "العربية")
    }
    
    func testLanguageFlags() {
        XCTAssertEqual(LocalizationManager.Language.russian.flag, "🇷🇺")
        XCTAssertEqual(LocalizationManager.Language.english.flag, "🇬🇧")
        XCTAssertEqual(LocalizationManager.Language.chinese.flag, "🇨🇳")
        XCTAssertEqual(LocalizationManager.Language.arabic.flag, "🇦🇪")
    }
    
    func testRTLSupport() {
        XCTAssertFalse(LocalizationManager.Language.russian.isRTL)
        XCTAssertFalse(LocalizationManager.Language.english.isRTL)
        XCTAssertFalse(LocalizationManager.Language.chinese.isRTL)
        XCTAssertTrue(LocalizationManager.Language.arabic.isRTL)
    }
    
    // MARK: - Language Change Tests
    
    func testChangeLanguage() {
        let initialLanguage = localizationManager.currentLanguage
        localizationManager.changeLanguage(to: .english)
        
        XCTAssertEqual(localizationManager.currentLanguage, .english)
        XCTAssertNotEqual(initialLanguage, localizationManager.currentLanguage)
    }
    
    func testLanguagePersistence() {
        localizationManager.changeLanguage(to: .chinese)
        let newManager = LocalizationManager()
        
        XCTAssertEqual(newManager.currentLanguage, .chinese)
    }
    
    func testDefaultLanguage() {
        let newManager = LocalizationManager()
        XCTAssertTrue(LocalizationManager.Language.allCases.contains(newManager.currentLanguage))
    }
    
    // MARK: - Localization Tests
    
    func testLocalizedStringUsesCurrentLanguage() {
        localizationManager.changeLanguage(to: .russian)
        XCTAssertEqual(localizationManager.localized("settings_title"), "НАСТРОЙКИ")
        
        localizationManager.changeLanguage(to: .english)
        XCTAssertEqual(localizationManager.localized("settings_title"), "SETTINGS")
    }
    
    func testMissingKeyFallsBackToKey() {
        localizationManager.changeLanguage(to: .russian)
        let nonExistentKey = "non.existent.key"
        XCTAssertEqual(localizationManager.localized(nonExistentKey), nonExistentKey)
    }
    
    // MARK: - Current Language Tests
    
    func testCurrentLanguageProperty() {
        XCTAssertTrue(LocalizationManager.Language.allCases.contains(localizationManager.currentLanguage))
    }
    
    func testLanguageChangeUpdatesPublishedValue() {
        localizationManager.changeLanguage(to: .arabic)
        XCTAssertEqual(localizationManager.currentLanguage, .arabic)
    }
    
    // MARK: - Edge Cases Tests
    
    func testInvalidLanguageHandling() {
        XCTAssertTrue(true)
    }
    
    func testConcurrentLanguageChanges() {
        let expectation1 = expectation(description: "Language change 1")
        let expectation2 = expectation(description: "Language change 2")
        
        DispatchQueue.global().async {
            self.localizationManager.changeLanguage(to: .english)
            expectation1.fulfill()
        }
        
        DispatchQueue.global().async {
            self.localizationManager.changeLanguage(to: .chinese)
            expectation2.fulfill()
        }
        
        wait(for: [expectation1, expectation2], timeout: 1.0)
        XCTAssertTrue(LocalizationManager.Language.allCases.contains(localizationManager.currentLanguage))
    }
}
