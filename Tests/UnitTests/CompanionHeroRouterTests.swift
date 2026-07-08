import XCTest
@testable import ALADDIN

final class CompanionHeroRouterTests: XCTestCase {
    override func tearDown() {
        UserDefaults.standard.removeObject(forKey: CompanionHeroRouter.userOverrideKey)
        UserDefaults.standard.removeObject(forKey: CompanionHeroRouter.selectedCharacterKey)
        UserDefaults.standard.removeObject(forKey: "current_user_role")
        UserDefaults.standard.removeObject(forKey: "companion_senior_entry")
        WellnessSessionStore.setActivePillar(nil)
        super.tearDown()
    }

    func testChildDefaultsToUnicorn() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "child"),
            "unicorn"
        )
    }

    func testTeenDefaultsToAladdin() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "teen"),
            "aladdin"
        )
    }

    func testParentDefaultsToAladdin() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "parent"),
            "aladdin"
        )
    }

    func testSeniorEntryDefaultsToAladdin() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "senior", entryPoint: .seniorQuick),
            "aladdin"
        )
    }

    func testWindDownTeenRoutesGenie() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "teen", entryPoint: .windDown),
            "genie"
        )
    }

    func testWindDownChildStaysUnicorn() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "child", entryPoint: .windDown),
            "unicorn"
        )
    }

    func testExamRoutesAladdin() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "teen", entryPoint: .exam),
            "aladdin"
        )
    }

    func testReflectiveTeenRoutesGenie() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "teen", entryPoint: .reflective),
            "genie"
        )
    }

    func testUserOverrideWins() {
        CompanionHeroRouter.markUserOverride(characterId: "genie")
        XCTAssertEqual(
            CompanionHeroRouter.resolve(ageBand: "child"),
            "genie"
        )
    }

    func testApplyDefaultIfNeededSkipsWhenOverride() {
        CompanionHeroRouter.markUserOverride(characterId: "genie")
        let applied = CompanionHeroRouter.applyDefaultIfNeeded()
        XCTAssertEqual(applied, "genie")
        XCTAssertEqual(
            UserDefaults.standard.string(forKey: CompanionHeroRouter.selectedCharacterKey),
            "genie"
        )
    }

    func testApplyDefaultIfNeededWritesRoutedId() {
        CompanionHeroRouter.clearUserOverride()
        let applied = CompanionHeroRouter.applyDefaultIfNeeded(
            entryPoint: .conversation,
            allowedCharacterIds: CompanionHeroRouter.allHeroIDs
        )
        XCTAssertEqual(applied, CompanionHeroRouter.resolve())
    }

    func testAllowedListFiltersInvalidPick() {
        XCTAssertEqual(
            CompanionHeroRouter.resolve(
                ageBand: "teen",
                allowedCharacterIds: ["unicorn"]
            ),
            "unicorn"
        )
    }
}
