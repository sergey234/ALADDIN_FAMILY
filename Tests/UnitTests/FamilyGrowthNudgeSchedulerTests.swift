import XCTest
@testable import ALADDIN

final class FamilyGrowthNudgeSchedulerTests: XCTestCase {
    private var calendar: Calendar {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(identifier: "Europe/Moscow")!
        return cal
    }

    private func date(_ day: Int, _ hour: Int) -> Date {
        calendar.date(from: DateComponents(year: 2026, month: 11, day: day, hour: hour))!
    }

    func testSchedulesDay2AndDay3At18ForSmallFamily() {
        let decision = FamilyGrowthNudgeScheduler.decide(
            rosterUsed: 1, isCreator: true, alreadyDone: false,
            anchor: date(18, 10), now: date(18, 10), calendar: calendar
        )
        XCTAssertEqual(decision, .schedule([
            .init(day: 2, fireDate: date(20, 18)),
            .init(day: 3, fireDate: date(21, 18)),
        ]))
    }

    func testSkipsPastSlots() {
        let decision = FamilyGrowthNudgeScheduler.decide(
            rosterUsed: 2, isCreator: true, alreadyDone: false,
            anchor: date(18, 10), now: date(20, 19), calendar: calendar
        )
        XCTAssertEqual(decision, .schedule([.init(day: 3, fireDate: date(21, 18))]))
    }

    func testCancelsOnceFamilyReachesThree() {
        let decision = FamilyGrowthNudgeScheduler.decide(
            rosterUsed: 3, isCreator: true, alreadyDone: false,
            anchor: date(18, 10), now: date(19, 10), calendar: calendar
        )
        XCTAssertEqual(decision, .cancel)
    }

    func testIgnoresInvitedMembersAndFinishedNudge() {
        XCTAssertEqual(FamilyGrowthNudgeScheduler.decide(
            rosterUsed: 1, isCreator: false, alreadyDone: false,
            anchor: date(18, 10), now: date(18, 10), calendar: calendar
        ), .ignore)
        XCTAssertEqual(FamilyGrowthNudgeScheduler.decide(
            rosterUsed: 1, isCreator: true, alreadyDone: true,
            anchor: date(18, 10), now: date(18, 10), calendar: calendar
        ), .ignore)
        XCTAssertEqual(FamilyGrowthNudgeScheduler.decide(
            rosterUsed: 1, isCreator: true, alreadyDone: false,
            anchor: date(18, 10), now: date(22, 10), calendar: calendar
        ), .ignore)
    }
}
