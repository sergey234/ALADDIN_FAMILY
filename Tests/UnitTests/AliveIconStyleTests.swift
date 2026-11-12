import XCTest
@testable import ALADDIN

final class AliveIconStyleTests: XCTestCase {
    func testAssetNamesGlyphAndBlackNoBlue() {
        XCTAssertEqual(
            AliveIconID.profile.assetName(for: .aliveBlue),
            "ICON_G1_A01_Profile_Glyph"
        )
        XCTAssertEqual(
            AliveIconID.fabLocate.assetName(for: .aliveBlue),
            "ICON_G1_A11_FabLocate_Glyph"
        )
        XCTAssertEqual(
            AliveIconID.fabLocate.assetName(for: .aliveBlack),
            "ICON_G1_A11_FabLocate_Black"
        )
        XCTAssertNil(AliveIconID.check.assetName(for: .legacy))
    }

    func testAllWave1IdsUseGlyphNotBlue() {
        let ids: [AliveIconID] = [
            .profile, .notif, .devices, .protect, .tariff, .premium,
            .check, .child, .whereFamily, .chipFamily, .fabLocate, .kids,
            .unicorn, .settings, .analytics, .senior60, .simpleHome,
            .aiFriends, .menu, .fullApp,
            .tariffFree, .tariffPersonal, .tariffFamily, .tariffTrial,
            .famMembers, .famChat, .famGroups, .famInvite,
            .mapDriving
        ]
        for id in ids {
            let gold = id.assetName(for: .aliveBlue)
            let black = id.assetName(for: .aliveBlack)
            XCTAssertNotNil(gold)
            XCTAssertNotNil(black)
            XCTAssertTrue(gold!.hasSuffix("_Glyph"), "\(id) gold must be Glyph, got \(gold!)")
            XCTAssertFalse(gold!.contains("_Blue"), "Blue disc removed from canon")
            XCTAssertTrue(black!.hasSuffix("_Black"))
        }
    }

    func testUnicornAssetNames() {
        XCTAssertEqual(
            AliveIconID.unicorn.assetName(for: .aliveBlue),
            "ICON_G1_U01_Unicorn_Glyph"
        )
        XCTAssertEqual(
            AliveIconID.unicorn.assetName(for: .aliveBlack),
            "ICON_G1_U01_Unicorn_Black"
        )
        XCTAssertNil(AliveIconID.unicorn.assetName(for: .legacy))
    }

    func testSettingsM04AssetNames() {
        XCTAssertEqual(
            AliveIconID.settings.assetName(for: .aliveBlue),
            "ICON_G1_M04_Settings_Glyph"
        )
        XCTAssertEqual(
            AliveIconID.settings.assetName(for: .aliveBlack),
            "ICON_G1_M04_Settings_Black"
        )
        XCTAssertNil(AliveIconID.settings.assetName(for: .legacy))
    }

    func testAnalyticsM03AndSeniorM02AssetNames() {
        XCTAssertEqual(
            AliveIconID.analytics.assetName(for: .aliveBlue),
            "ICON_G1_M03_Analytics_Glyph"
        )
        XCTAssertEqual(
            AliveIconID.analytics.assetName(for: .aliveBlack),
            "ICON_G1_M03_Analytics_Black"
        )
        XCTAssertEqual(
            AliveIconID.senior60.assetName(for: .aliveBlue),
            "ICON_G1_M02_Senior60_Glyph"
        )
        XCTAssertEqual(
            AliveIconID.senior60.assetName(for: .aliveBlack),
            "ICON_G1_M02_Senior60_Black"
        )
        XCTAssertNil(AliveIconID.analytics.assetName(for: .legacy))
        XCTAssertNil(AliveIconID.senior60.assetName(for: .legacy))
    }

    func testSimpleHomeM05AssetNames() {
        XCTAssertEqual(
            AliveIconID.simpleHome.assetName(for: .aliveBlue),
            "ICON_G1_M05_SimpleHome_Glyph"
        )
        XCTAssertEqual(
            AliveIconID.simpleHome.assetName(for: .aliveBlack),
            "ICON_G1_M05_SimpleHome_Black"
        )
        XCTAssertNil(AliveIconID.simpleHome.assetName(for: .legacy))
    }

    func testTitlesRUCanon() {
        XCTAssertEqual(AliveIconDiscStyle.legacy.titleRU, "Классика")
        XCTAssertEqual(AliveIconDiscStyle.aliveBlue.titleRU, "Золото")
        XCTAssertEqual(AliveIconDiscStyle.aliveBlack.titleRU, "Значки")
    }
}
