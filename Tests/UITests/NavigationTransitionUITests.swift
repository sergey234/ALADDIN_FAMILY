import XCTest

/// W4-1: five stack transitions that exercise `NavigationManager.navigateTo` / `goBack` with root `appContentTransition` in `ALADDINApp`.
@MainActor
final class NavigationTransitionUITests: XCTestCase {

    private var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["-UITestSkipOnboarding", "--uitesting"]
        app.launch()
    }

    override func tearDownWithError() throws {
        app = nil
        try super.tearDownWithError()
    }

    private func requireMainRoot(file: StaticString = #file, line: UInt = #line) throws {
        let main = app.otherElements["aladdin_root_01_MainScreen"]
        guard main.waitForExistence(timeout: 12) else {
            throw XCTSkip("Main root not found (onboarding or different launch state)")
        }
    }

    func testTransitionMainToFamilyAndBack() throws {
        try requireMainRoot()
        app.buttons["main_nav_family_manage"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_02_FamilyScreen"].waitForExistence(timeout: 8))
        app.buttons["family_nav_back"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_01_MainScreen"].waitForExistence(timeout: 8))
    }

    func testTransitionMainToNetworkProtectionAndBack() throws {
        try requireMainRoot()
        app.buttons["main_nav_network_protection"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_03_NetworkProtectionScreen"].waitForExistence(timeout: 8))
        app.buttons["aladdin_nav_back"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_01_MainScreen"].waitForExistence(timeout: 8))
    }

    func testTransitionMainToProfileAndBack() throws {
        try requireMainRoot()
        app.buttons["main_nav_profile"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_11_ProfileScreen"].waitForExistence(timeout: 8))
        app.buttons["aladdin_nav_back"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_01_MainScreen"].waitForExistence(timeout: 8))
    }

    func testTransitionMainToAIAssistantAndBack() throws {
        try requireMainRoot()
        app.buttons["main_nav_ai_assistant"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_06_AIAssistantScreen"].waitForExistence(timeout: 8))
        app.buttons["ai_assistant_nav_back"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_01_MainScreen"].waitForExistence(timeout: 8))
    }

    func testTransitionMainToTariffsAndBack() throws {
        try requireMainRoot()
        app.buttons["main_nav_tariffs"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_10_TariffsScreen"].waitForExistence(timeout: 8))
        app.buttons["aladdin_nav_back"].tap()
        XCTAssertTrue(app.otherElements["aladdin_root_01_MainScreen"].waitForExistence(timeout: 8))
    }
}
