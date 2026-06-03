import XCTest

/// r100-0-05 / r100-2-12 — embedded wellness: Hub → exercise → outcome skip → Hub (CompanionHome).
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
        let companionRoot = app.otherElements["aladdin_root_companion_home"]
        XCTAssertTrue(companionRoot.waitForExistence(timeout: 15))

        let wellnessTab = app.buttons["companion_home_tab_1"]
        XCTAssertTrue(wellnessTab.waitForExistence(timeout: 5))
        wellnessTab.tap()

        let hub = app.otherElements["wellness_hub_embedded_root"]
        XCTAssertTrue(hub.waitForExistence(timeout: 12))

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
            app.buttons.matching(identifier: "wellness_hub_back").firstMatch.tap()
        }

        XCTAssertTrue(hub.waitForExistence(timeout: 10))
        XCTAssertTrue(companionRoot.exists)
        XCTAssertFalse(app.tabBars.firstMatch.exists && app.tabBars.buttons["Main"].exists)
    }
}
