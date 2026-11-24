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

    func testCloseChoiceKeepsTwoHoursAndMorning() {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(secondsFromGMT: 0)!
        let morning = calendar.date(from: DateComponents(year: 2026, month: 11, day: 24, hour: 6, minute: 0))!
        let afterDawn = ChildPhoneCloseChoice.untilMorning.endsAt(now: morning, calendar: calendar)
        XCTAssertEqual(calendar.component(.hour, from: afterDawn), 7)
        XCTAssertEqual(calendar.component(.day, from: afterDawn), 24)

        let evening = calendar.date(from: DateComponents(year: 2026, month: 11, day: 24, hour: 20, minute: 0))!
        let nextMorning = ChildPhoneCloseChoice.untilMorning.endsAt(now: evening, calendar: calendar)
        XCTAssertEqual(calendar.component(.day, from: nextMorning), 25)
        XCTAssertEqual(calendar.component(.hour, from: nextMorning), 7)

        let twoHours = ChildPhoneCloseChoice.twoHours.endsAt(now: evening, calendar: calendar)
        XCTAssertEqual(twoHours.timeIntervalSince(evening), 2 * 60 * 60)
    }

    func testIoTKindIndependentFromPhone() {
        DevicePauseScheduler.schedulePause(deviceId: camId, kind: .iot)
        XCTAssertTrue(DevicePauseScheduler.isPaused(camId))
        XCTAssertFalse(DevicePauseScheduler.isPaused(phoneId))
    }
}
