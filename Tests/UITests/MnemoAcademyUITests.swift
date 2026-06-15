import XCTest

/// MNEMO-B8-T03 + B15-T03: Mnemo Academy catalog, SRS, semester lock, deeplink.
@MainActor
final class MnemoAcademyUITests: XCTestCase {

    private var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
    }

    override func tearDownWithError() throws {
        app = nil
        try super.tearDownWithError()
    }

    private func launchMnemo(extraArguments: [String] = []) {
        app.launchArguments = [
            "-UITestSkipOnboarding",
            "-UITestMnemoAcademy",
            "--uitesting"
        ] + extraArguments
        app.launch()
    }

    private func waitForChildContentRoot(timeout: TimeInterval = 20) -> XCUIElement {
        let root = app.otherElements["aladdin_root_child_content"]
        XCTAssertTrue(root.waitForExistence(timeout: timeout), "Child content screen should appear")
        return root
    }

    private func waitForLessonPhaseHeader(timeout: TimeInterval = 6) -> Bool {
        app.otherElements["child_mnemo_lesson_phase_header"].waitForExistence(timeout: timeout)
    }

    // MARK: - B8-T03

    func testMnemoAcademyBannerAndFourPhases() throws {
        launchMnemo()
        _ = waitForChildContentRoot()

        let banner = app.otherElements["child_mnemo_academy_banner"]
        XCTAssertTrue(banner.waitForExistence(timeout: 12), "Mnemo academy banner should be visible")

        XCTAssertTrue(app.staticTexts["child_mnemo_brand_title"].waitForExistence(timeout: 8))
        XCTAssertTrue(app.otherElements["child_mnemo_phase_label_0"].waitForExistence(timeout: 8))
        XCTAssertTrue(app.otherElements["child_mnemo_phase_label_1"].waitForExistence(timeout: 8))
        XCTAssertTrue(app.otherElements["child_mnemo_phase_label_2"].waitForExistence(timeout: 8))
        XCTAssertTrue(app.otherElements["child_mnemo_phase_label_3"].waitForExistence(timeout: 8))
    }

    func testMnemoSRSBadgeOpensLessonWithPhaseHeader() throws {
        launchMnemo()
        _ = waitForChildContentRoot()

        let srsBadge = app.buttons["child_mnemo_srs_due_badge"]
        XCTAssertTrue(srsBadge.waitForExistence(timeout: 15), "SRS due badge should appear for seeded games.05")

        srsBadge.tap()

        XCTAssertTrue(waitForLessonPhaseHeader(timeout: 12), "Lesson should show 4-phase mnemo header")
    }

    // MARK: - B15-T03

    func testSemesterLockBannerWhenForcedLocked() throws {
        launchMnemo(extraArguments: ["-UITestMnemoSemesterLocked"])
        _ = waitForChildContentRoot()

        let lockBanner = app.otherElements["child_mnemo_semester_locked"]
        XCTAssertTrue(lockBanner.waitForExistence(timeout: 12), "Semester lock banner should appear when forced locked")

        XCTAssertTrue(app.otherElements["child_mnemo_semester_progress"].waitForExistence(timeout: 8))
        XCTAssertTrue(app.otherElements["child_mnemo_academy_banner"].waitForExistence(timeout: 8))
    }

    func testLockedSemesterBlocksSRSAndItemOpen() throws {
        launchMnemo(extraArguments: ["-UITestMnemoSemesterLocked"])
        _ = waitForChildContentRoot()

        let itemProgress = app.otherElements["child_content_item_progress_games.05"]
        XCTAssertTrue(itemProgress.waitForExistence(timeout: 15), "Seeded games.05 row should load")

        let srsBadge = app.buttons["child_mnemo_srs_due_badge"]
        if srsBadge.waitForExistence(timeout: 8) {
            srsBadge.tap()
            XCTAssertFalse(waitForLessonPhaseHeader(timeout: 4), "SRS tap must not open lesson when semester locked")
        }

        itemProgress.tap()
        XCTAssertFalse(waitForLessonPhaseHeader(timeout: 4), "Locked item tap must not open lesson")
        XCTAssertTrue(app.alerts.firstMatch.waitForExistence(timeout: 4), "Locked item tap should show semester alert")
    }

    func testMnemoReviewDeepLinkDoesNotBypassSemesterLock() throws {
        launchMnemo(extraArguments: ["-UITestMnemoSemesterLocked"])
        _ = waitForChildContentRoot()

        guard let url = URL(string: "aladdin://mnemo/review?category=games") else {
            XCTFail("Invalid mnemo review deeplink URL")
            return
        }
        if #available(iOS 16.4, *) {
            app.open(url)
        } else {
            throw XCTSkip("XCUIApplication.open(URL) requires iOS 16.4+")
        }

        XCTAssertTrue(app.otherElements["child_mnemo_semester_locked"].waitForExistence(timeout: 12))
        XCTAssertTrue(app.otherElements["aladdin_root_child_content"].exists)
        XCTAssertFalse(waitForLessonPhaseHeader(timeout: 4), "Deeplink must not auto-open lesson when locked")
    }
}
