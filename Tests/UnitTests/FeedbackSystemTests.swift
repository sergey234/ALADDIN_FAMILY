import XCTest
@testable import ALADDIN

@MainActor
final class FeedbackSystemTests: XCTestCase {

    private var virtualUptime: TimeInterval = 10_000

    override func setUp() {
        super.setUp()
        virtualUptime = 10_000
        let fs = FeedbackSystem.shared
        fs.resetDebounceStateForUnitTests()
        fs.uptime = { [unowned self] in self.virtualUptime }
    }

    override func tearDown() {
        FeedbackSystem.shared.resetDebounceStateForUnitTests()
        FeedbackSystem.shared.uptime = { ProcessInfo.processInfo.systemUptime }
        super.tearDown()
    }

    func testDebounceDropsRapidNormalSignals() {
        let fs = FeedbackSystem.shared
        XCTAssertTrue(fs.signal(.success))
        virtualUptime += FeedbackSystem.debounceInterval * 0.5
        XCTAssertFalse(fs.signal(.success, options: FeedbackOptions(priority: .normal)))
    }

    func testDebounceAllowsAfterWindow() {
        let fs = FeedbackSystem.shared
        XCTAssertTrue(fs.signal(.selection))
        virtualUptime += FeedbackSystem.debounceInterval + 0.01
        XCTAssertTrue(fs.signal(.selection))
    }

    func testCriticalBypassesDebounce() {
        let fs = FeedbackSystem.shared
        XCTAssertTrue(fs.signal(.success))
        virtualUptime += 0.01
        XCTAssertTrue(
            fs.signal(
                .error,
                options: FeedbackOptions(priority: .critical)
            )
        )
    }

    func testHigherPriorityPreemptsWithinWindow() {
        let fs = FeedbackSystem.shared
        XCTAssertTrue(fs.signal(.success, options: FeedbackOptions(priority: .normal)))
        virtualUptime += 0.02
        XCTAssertTrue(fs.signal(.warning, options: FeedbackOptions(priority: .high)))
    }

    func testEqualPriorityDoesNotPreemptWithinWindow() {
        let fs = FeedbackSystem.shared
        XCTAssertTrue(fs.signal(.success, options: FeedbackOptions(priority: .normal)))
        virtualUptime += 0.02
        XCTAssertFalse(fs.signal(.error, options: FeedbackOptions(priority: .normal)))
    }
}
