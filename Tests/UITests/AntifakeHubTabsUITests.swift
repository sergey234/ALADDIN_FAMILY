import XCTest

/// Q-02 — Antifake Hub: 4 tabs smoke (text · audio · video · call).
@MainActor
final class AntifakeHubTabsUITests: XCTestCase {

    private var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = [
            "-UITestSkipOnboarding",
            "-UITestAntifakeHubSmoke",
            "--uitesting"
        ]
        app.launch()
    }

    override func tearDownWithError() throws {
        app = nil
        try super.tearDownWithError()
    }

    func testHubFourTabsVisibleAndSelectable() throws {
        let hub = app.otherElements["antifake_hub_root"]
        XCTAssertTrue(hub.waitForExistence(timeout: 15))

        let tabs: [(id: String, panel: String)] = [
            ("text", "antifake_text_check_button"),
            ("audio", "antifake_audio_panel"),
            ("video", "antifake_video_panel"),
            ("call", "antifake_call_panel"),
        ]

        for tab in tabs {
            let tabButton = app.buttons["antifake_hub_tab_\(tab.id)"]
            XCTAssertTrue(tabButton.waitForExistence(timeout: 5), "missing tab \(tab.id)")
            tabButton.tap()
            let panel = app.otherElements[tab.panel]
            XCTAssertTrue(
                panel.waitForExistence(timeout: 8),
                "panel \(tab.panel) not visible for tab \(tab.id)"
            )
        }
    }
}
