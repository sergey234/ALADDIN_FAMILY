import XCTest
@testable import ALADDIN

@MainActor
final class SafariCardsIntegrationTests: XCTestCase {

    func testFlowSitesOnThenSocialOnProducesUnion() {
        let sitesPreset: [ContentBlockerCategory] = [.adult, .violence, .gambling]

        let afterSites = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: true,
            socialEnabled: false,
            sitesCategories: sitesPreset
        )
        XCTAssertEqual(Set(afterSites), Set(sitesPreset))

        let afterSocial = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: true,
            socialEnabled: true,
            sitesCategories: sitesPreset
        )
        XCTAssertEqual(Set(afterSocial), Set(sitesPreset + [.socialMedia]))
    }

    func testFlowSocialOnlyThenDisableClearsUnion() {
        let sitesPreset: [ContentBlockerCategory] = [.adult, .violence]

        let socialOnly = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: false,
            socialEnabled: true,
            sitesCategories: sitesPreset
        )
        XCTAssertEqual(Set(socialOnly), Set([.socialMedia]))

        let allOff = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: false,
            socialEnabled: false,
            sitesCategories: sitesPreset
        )
        XCTAssertTrue(allOff.isEmpty)
    }

    func testFlowChangingSitesPresetKeepsSocialAndReplacesSites() {
        let initialPreset: [ContentBlockerCategory] = [.adult, .violence]
        let newPreset: [ContentBlockerCategory] = [.forums, .fileSharing]

        let initialUnion = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: true,
            socialEnabled: true,
            sitesCategories: initialPreset
        )
        XCTAssertEqual(Set(initialUnion), Set(initialPreset + [.socialMedia]))

        let updatedUnion = AdvancedProtectionSettingsScreen.composeSafariCategories(
            sitesEnabled: true,
            socialEnabled: true,
            sitesCategories: newPreset
        )
        XCTAssertEqual(Set(updatedUnion), Set(newPreset + [.socialMedia]))
        XCTAssertFalse(updatedUnion.contains(.adult))
        XCTAssertFalse(updatedUnion.contains(.violence))
    }
}
