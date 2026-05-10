import XCTest

/// W4-4 G13: `ChildContentScreen` — progress / loading / empty / error и идентификаторы для визуальной проверки.
@MainActor
final class ChildContentProgressUITests: XCTestCase {

    private var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = [
            "-UITestSkipOnboarding",
            "-UITestChildContentW4_4",
            "--uitesting"
        ]
        app.launch()
    }

    override func tearDownWithError() throws {
        app = nil
        try super.tearDownWithError()
    }

    func testChildContentRootAndProgressOrEmpty() throws {
        let root = app.otherElements["aladdin_root_child_content"]
        XCTAssertTrue(root.waitForExistence(timeout: 18), "Child content screen should be shown under UITest flag")

        // Wait until one of: loading, error, empty, or category-level progress
        var satisfied = false
        let deadline = Date().addingTimeInterval(25)
        while Date() < deadline, !satisfied {
            if app.otherElements["child_content_loading"].exists
                || app.otherElements["child_content_error"].exists
                || app.otherElements["child_content_empty_state"].exists
                || app.otherElements["child_content_overall_progress"].exists {
                satisfied = true
                break
            }
            RunLoop.current.run(until: Date().addingTimeInterval(0.2))
        }
        XCTAssertTrue(satisfied, "Expected loading, error, empty, or overall progress to appear")
    }
}
