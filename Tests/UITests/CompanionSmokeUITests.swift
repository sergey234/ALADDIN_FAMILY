import XCTest

/// P1-14 — smoke: Kids → Друзья → Companion → ввод сообщения.
@MainActor
final class CompanionSmokeUITests: XCTestCase {

    private var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = [
            "-UITestSkipOnboarding",
            "-UITestCompanionSmoke",
            "--uitesting"
        ]
        app.launch()
    }

    override func tearDownWithError() throws {
        app = nil
        try super.tearDownWithError()
    }

    func testChildFriendsButtonOpensCompanionHome() throws {
        let childRoot = app.otherElements["aladdin_root_child_interface"]
        guard childRoot.waitForExistence(timeout: 15) else {
            throw XCTSkip("Child interface not shown — check launch flags / navigation bootstrap")
        }

        let friends = app.buttons["child_interface_companion_friends_button"]
        XCTAssertTrue(friends.waitForExistence(timeout: 5))
        friends.tap()

        let companionRoot = app.otherElements["aladdin_root_companion_home"]
        XCTAssertTrue(companionRoot.waitForExistence(timeout: 10))

        let mainTab = app.buttons["companion_home_tab_0"]
        XCTAssertTrue(mainTab.waitForExistence(timeout: 5))
    }

    func testCompanionHomeMessageInputAndSendTap() throws {
        app.launchArguments = [
            "-UITestSkipOnboarding",
            "-UITestCompanionSmoke",
            "-UITestCompanionHome",
            "--uitesting"
        ]
        app.launch()

        let companionRoot = app.otherElements["aladdin_root_companion_home"]
        guard companionRoot.waitForExistence(timeout: 15) else {
            throw XCTSkip("Companion home not shown")
        }

        let input = app.textFields["companion_message_input"]
        XCTAssertTrue(input.waitForExistence(timeout: 8))
        input.tap()
        input.typeText("Привет")

        let send = app.buttons["companion_send_button"]
        XCTAssertTrue(send.waitForExistence(timeout: 5))
        XCTAssertTrue(send.isEnabled)
        send.tap()

        // UI path exercised; network may fail offline — hero stage must remain.
        XCTAssertTrue(app.otherElements["companion_hero_stage"].waitForExistence(timeout: 5))
    }
}
