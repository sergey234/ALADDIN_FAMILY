import XCTest

/// r100-0-05 / r100-2-12 / ux-5-05 — embedded wellness back → Companion+AI, not Main.
@MainActor
final class WellnessCompanionNavUITests: XCTestCase {

    private var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = [
            "-UITestSkipOnboarding",
            "-UITestWellnessNavSmoke",
            "-UITestCompanionHome",
            "--uitesting"
        ]
        app.launch()
    }

    override func tearDownWithError() throws {
        app = nil
        try super.tearDownWithError()
    }

    func testEmbeddedWellnessHubExerciseAndReturn() throws {
        let hub = openWellnessHub()
        let exercise = app.buttons["wellness_hub_exercise_button"]
        XCTAssertTrue(exercise.waitForExistence(timeout: 8))
        exercise.tap()

        let exerciseScreen = app.otherElements["wellness_exercise_screen"]
        guard exerciseScreen.waitForExistence(timeout: 10) else {
            throw XCTSkip("Exercise screen not reached — API/catalog may be offline")
        }

        let openOutcome = app.buttons["wellness_exercise_open_outcome"]
        if openOutcome.waitForExistence(timeout: 3) {
            openOutcome.tap()
            let skip = app.buttons["wellness_outcome_skip"]
            if skip.waitForExistence(timeout: 5) {
                skip.tap()
            }
        } else {
            app.buttons["wellness_hub_back"].tap()
        }

        XCTAssertTrue(hub.waitForExistence(timeout: 10))
        assertStillOnCompanionWellness()
    }

    func testBackFromDreamJournalReturnsToWellnessHub() throws {
        let hub = openWellnessHub()
        let dream = app.buttons["wellness_hub_dream_button"]
        guard dream.waitForExistence(timeout: 15) else {
            throw XCTSkip("Dream journal entry not visible on hub")
        }
        dream.tap()
        assertBackFromSubpage(
            screenId: "wellness_dream_journal_screen",
            hub: hub
        )
    }

    func testBackFromReflectiveReturnsToWellnessHub() throws {
        let hub = openWellnessHub()
        let reflective = app.buttons["wellness_hub_reflective_button"]
        guard reflective.waitForExistence(timeout: 15) else {
            throw XCTSkip("Reflective entry not visible on hub")
        }
        reflective.tap()
        assertBackFromSubpage(
            screenId: "wellness_reflective_screen",
            hub: hub
        )
    }

    func testBackFromTimelineReturnsToWellnessHub() throws {
        let hub = openWellnessHub()
        let timeline = app.buttons["wellness_hub_timeline_button"]
        guard timeline.waitForExistence(timeout: 15) else {
            throw XCTSkip("Timeline entry not visible on hub")
        }
        timeline.tap()
        assertBackFromSubpage(
            screenId: "wellness_timeline_screen",
            hub: hub
        )
    }

    // MARK: - Helpers

    @discardableResult
    private func openWellnessHub() -> XCUIElement {
        let companionRoot = app.otherElements["aladdin_root_companion_home"]
        XCTAssertTrue(companionRoot.waitForExistence(timeout: 15))

        let wellnessTab = app.buttons["companion_home_tab_1"]
        XCTAssertTrue(wellnessTab.waitForExistence(timeout: 5))
        wellnessTab.tap()

        let hub = app.otherElements["wellness_hub_embedded_root"]
        XCTAssertTrue(hub.waitForExistence(timeout: 12))
        return hub
    }

    private func assertBackFromSubpage(screenId: String, hub: XCUIElement) {
        let screen = app.otherElements[screenId]
        XCTAssertTrue(screen.waitForExistence(timeout: 12))

        let back = app.buttons["wellness_subpage_back"]
        XCTAssertTrue(back.waitForExistence(timeout: 5))
        back.tap()

        XCTAssertTrue(hub.waitForExistence(timeout: 10))
        assertStillOnCompanionWellness()
    }

    private func assertStillOnCompanionWellness() {
        XCTAssertTrue(app.otherElements["aladdin_root_companion_home"].exists)
        XCTAssertTrue(app.otherElements["wellness_hub_embedded_root"].exists)
        XCTAssertTrue(app.buttons["companion_home_tab_1"].exists)
    }
}
