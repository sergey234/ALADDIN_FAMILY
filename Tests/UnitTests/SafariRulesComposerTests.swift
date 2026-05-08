import XCTest
@testable import ALADDIN

final class SafariRulesComposerTests: XCTestCase {

    func testComposeCategoriesWhenBothCardsDisabledReturnsEmpty() {
        let result = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: false,
            socialEnabled: false,
            sitesCategories: [.adult, .violence]
        )

        XCTAssertTrue(result.isEmpty)
    }

    func testComposeCategoriesWhenSitesEnabledIncludesSitesPreset() {
        let result = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: true,
            socialEnabled: false,
            sitesCategories: [.adult, .violence, .gambling]
        )

        XCTAssertEqual(Set(result), Set([.adult, .violence, .gambling]))
    }

    func testComposeCategoriesWhenSocialEnabledIncludesSocialMedia() {
        let result = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: false,
            socialEnabled: true,
            sitesCategories: [.adult, .violence]
        )

        XCTAssertEqual(Set(result), Set([.socialMedia]))
    }

    func testComposeCategoriesDeduplicatesSocialMediaAcrossSources() {
        let result = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: true,
            socialEnabled: true,
            sitesCategories: [.adult, .socialMedia]
        )

        XCTAssertEqual(Set(result), Set([.adult, .socialMedia]))
        XCTAssertEqual(result.filter { $0 == .socialMedia }.count, 1)
    }
}
