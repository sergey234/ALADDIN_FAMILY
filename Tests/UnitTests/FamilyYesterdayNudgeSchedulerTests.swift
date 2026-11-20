import XCTest
@testable import ALADDIN

final class FamilyYesterdayNudgeSchedulerTests: XCTestCase {
    private var calendar: Calendar {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Europe/Moscow")!
        return cal
    }

    private func date(_ day: Int, _ hour: Int) -> Date {
        calendar.date(from: DateComponents(year: 2026, month: 11, day: day, hour: hour))!
    }

    func testSchedulesDay3At19WhenFamilyHasTwo() {
        let decision = FamilyYesterdayNudgeScheduler.decide(
            rosterUsed: 2,
            isEligibleRole: true,
            alreadyDone: false,
            memberId: "m1",
            memberName: "Мария",
            anchor: date(18, 10),
            now: date(18, 10),
            calendar: calendar
        )
        XCTAssertEqual(decision, .schedule(.init(
            fireDate: date(21, 19),
            memberId: "m1",
            memberName: "Мария"
        )))
    }

    func testCancelsWhenFamilyTooSmall() {
        let decision = FamilyYesterdayNudgeScheduler.decide(
            rosterUsed: 1,
            isEligibleRole: true,
            alreadyDone: false,
            memberId: "m1",
            memberName: "Мария",
            anchor: date(18, 10),
            now: date(18, 10),
            calendar: calendar
        )
        XCTAssertEqual(decision, .cancel)
    }

    func testIgnoresNonEligibleAndDoneAndPast() {
        XCTAssertEqual(FamilyYesterdayNudgeScheduler.decide(
            rosterUsed: 2, isEligibleRole: false, alreadyDone: false,
            memberId: "m1", memberName: "Мария",
            anchor: date(18, 10), now: date(18, 10), calendar: calendar
        ), .ignore)
        XCTAssertEqual(FamilyYesterdayNudgeScheduler.decide(
            rosterUsed: 2, isEligibleRole: true, alreadyDone: true,
            memberId: "m1", memberName: "Мария",
            anchor: date(18, 10), now: date(18, 10), calendar: calendar
        ), .ignore)
        XCTAssertEqual(FamilyYesterdayNudgeScheduler.decide(
            rosterUsed: 2, isEligibleRole: true, alreadyDone: false,
            memberId: "m1", memberName: "Мария",
            anchor: date(18, 10), now: date(22, 10), calendar: calendar
        ), .ignore)
    }

    func testDeepLinkContainsMember() {
        let link = FamilyYesterdayNudgeScheduler.deepLink(memberId: "abc-123")
        XCTAssertTrue(link.contains("location-history"))
        XCTAssertTrue(link.contains("member=abc-123"))
    }
}
