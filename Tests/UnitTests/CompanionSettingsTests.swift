import XCTest
@testable import ALADDIN

final class CompanionSettingsTests: XCTestCase {
    override func tearDown() {
        UserDefaults.standard.removeObject(forKey: "companion_vedic_wisdom_enabled_v1")
        super.tearDown()
    }

    func testChildNeverGetsWisdom() {
        XCTAssertFalse(CompanionSettings.defaultVedicWisdomEnabled(ageBand: "child"))
        CompanionSettings.setCachedVedicWisdomEnabled(true, ageBand: "child")
        XCTAssertFalse(CompanionSettings.cachedVedicWisdomEnabled(ageBand: "child"))
    }

    func testTeenDefaultWisdomOnWhenUnset() {
        XCTAssertTrue(CompanionSettings.defaultVedicWisdomEnabled(ageBand: "teen"))
        XCTAssertTrue(CompanionSettings.cachedVedicWisdomEnabled(ageBand: "teen"))
    }

    func testHumorHintKeys() {
        XCTAssertEqual(CompanionSettings.humorHintKey(for: "genie"), "companion_humor_hint_genie")
    }
}
