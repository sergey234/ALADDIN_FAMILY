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

    func testCallDirectoryCardOnlyOnCallTab() throws {
        let hub = app.otherElements["antifake_hub_root"]
        XCTAssertTrue(hub.waitForExistence(timeout: 15))

        let cdCard = app.otherElements["antifake_call_directory_card"]

        app.buttons["antifake_hub_tab_text"].tap()
        XCTAssertFalse(cdCard.waitForExistence(timeout: 2), "Call Directory card must not appear on Text tab")

        app.buttons["antifake_hub_tab_audio"].tap()
        XCTAssertFalse(cdCard.exists, "Call Directory card must not appear on Voice tab")

        app.buttons["antifake_hub_tab_video"].tap()
        XCTAssertFalse(cdCard.exists, "Call Directory card must not appear on Video tab")

        app.buttons["antifake_hub_tab_call"].tap()
        XCTAssertTrue(cdCard.waitForExistence(timeout: 5), "Call Directory card must appear on Call tab")

        XCTAssertTrue(app.otherElements["antifake_call_section_recording"].waitForExistence(timeout: 3))
        XCTAssertTrue(app.otherElements["antifake_call_section_incoming"].waitForExistence(timeout: 3))
    }

    func testFamilyReportsCollapsedByDefault() throws {
        let hub = app.otherElements["antifake_hub_root"]
        XCTAssertTrue(hub.waitForExistence(timeout: 15))

        XCTAssertTrue(app.otherElements["antifake_family_reports_section"].waitForExistence(timeout: 5))

        let header = app.buttons["antifake_family_reports_header"]
        XCTAssertTrue(header.waitForExistence(timeout: 3))

        let emptyLabel = app.staticTexts
            .matching(NSPredicate(format: "identifier == %@", "antifake_family_reports_empty"))
            .firstMatch
        XCTAssertFalse(emptyLabel.exists, "Empty state should not show while collapsed")

        header.tap()
        // After expand, loading or empty/content may appear — section stays visible.
        XCTAssertTrue(app.otherElements["antifake_family_reports_section"].exists)
    }
}
