import XCTest
@testable import ALADDIN

final class DevicePauseSchedulerTests: XCTestCase {

    private let phoneId = "pause-test-phone"
    private let camId = "pause-test-cam"

    override func setUp() {
        super.setUp()
        DevicePauseScheduler.cancel(deviceId: phoneId)
        DevicePauseScheduler.cancel(deviceId: camId)
    }

    override func tearDown() {
        DevicePauseScheduler.cancel(deviceId: phoneId)
        DevicePauseScheduler.cancel(deviceId: camId)
        super.tearDown()
    }

    func testScheduleShowsRemainingAndCancelClears() {
        DevicePauseScheduler.schedulePause(deviceId: phoneId, kind: .familyPhone)
        XCTAssertTrue(DevicePauseScheduler.isPaused(phoneId))
        XCTAssertEqual(DevicePauseScheduler.remainingMinutes(deviceId: phoneId), 60)
        DevicePauseScheduler.cancel(deviceId: phoneId)
        XCTAssertFalse(DevicePauseScheduler.isPaused(phoneId))
    }

    func testIoTKindIndependentFromPhone() {
        DevicePauseScheduler.schedulePause(deviceId: camId, kind: .iot)
        XCTAssertTrue(DevicePauseScheduler.isPaused(camId))
        XCTAssertFalse(DevicePauseScheduler.isPaused(phoneId))
    }
}
