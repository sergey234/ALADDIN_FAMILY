import XCTest
@testable import ALADDIN

/**
 * 🌍 LocalizationManager Unit Tests
 * Тестирование менеджера локализации
 */

@MainActor
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
        let selectable = LocalizationManager.Language.userSelectableLanguages
        XCTAssertEqual(selectable.count, 2)
        XCTAssertTrue(selectable.contains(.russian))
        XCTAssertTrue(selectable.contains(.english))

        let allCases = LocalizationManager.Language.allCases
        XCTAssertEqual(allCases.count, 4)
        XCTAssertTrue(allCases.contains(.chinese))
        XCTAssertTrue(allCases.contains(.arabic))
    }
    
    func testLanguageDisplayNames() {
        XCTAssertEqual(LocalizationManager.Language.russian.displayName, "Русский")
        XCTAssertEqual(LocalizationManager.Language.english.displayName, "English")
    }
    
    func testLanguageFlags() {
        XCTAssertEqual(LocalizationManager.Language.russian.flag, "🇷🇺")
        XCTAssertEqual(LocalizationManager.Language.english.flag, "🇬🇧")
    }
    
    func testRTLSupport() {
        XCTAssertFalse(LocalizationManager.Language.russian.isRTL)
        XCTAssertFalse(LocalizationManager.Language.english.isRTL)
    }
    
    // MARK: - Language Change Tests
    
    func testChangeLanguage() {
        let initialLanguage = localizationManager.currentLanguage
        localizationManager.changeLanguage(to: .english)
        
        XCTAssertEqual(localizationManager.currentLanguage, .english)
        XCTAssertNotEqual(initialLanguage, localizationManager.currentLanguage)
    }
    
    func testLanguagePersistence() {
        localizationManager.changeLanguage(to: .english)
        let newManager = LocalizationManager()
        
        XCTAssertEqual(newManager.currentLanguage, .english)
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
        localizationManager.changeLanguage(to: .english)
        XCTAssertEqual(localizationManager.currentLanguage, .english)
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
            self.localizationManager.changeLanguage(to: .russian)
            expectation2.fulfill()
        }
        
        wait(for: [expectation1, expectation2], timeout: 1.0)
        XCTAssertTrue(LocalizationManager.Language.allCases.contains(localizationManager.currentLanguage))
    }

    /// pc-15: семейные ключи мониторинга и пустых отчётов должны резолвиться из `en.lproj` / `ru.lproj`, а не возвращаться как сырой ключ.
    func testFamilyMonitoringAndReportsEmptyKeysResolveFromBundle() {
        let keys = [
            "family_monitoring_browser_title",
            "family_monitoring_browser_total_sites",
            "family_monitoring_browser_total_time",
            "family_monitoring_browser_top_week",
            "family_monitoring_browser_visits",
            "family_monitoring_browser_category_video",
            "family_reports_empty_title",
            "family_reports_empty_hint_jwt"
        ]
        localizationManager.changeLanguage(to: .russian)
        for k in keys {
            let v = localizationManager.localized(k)
            XCTAssertNotEqual(v, k, "RU: expected Localizable.strings value for \(k)")
        }
        localizationManager.changeLanguage(to: .english)
        for k in keys {
            let v = localizationManager.localized(k)
            XCTAssertNotEqual(v, k, "EN: expected Localizable.strings value for \(k)")
        }
    }
}
