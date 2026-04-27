import XCTest
@testable import ALADDIN

final class ParentActivityDailyAggregatorTests: XCTestCase {

    func testBuildTrendPoints_sevenDays_oldestFirst_andTodayValues() {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(secondsFromGMT: 0)!
        let suite = UserDefaults(suiteName: "test.pad.series.\(UUID().uuidString)")!
        let now = cal.date(from: DateComponents(year: 2026, month: 4, day: 26, hour: 15))!
        let agg = ParentActivityDailyAggregator(defaults: suite, calendar: cal)

        agg.recordOpen(at: now)
        agg.recordCompletion(at: now)

        let series = agg.buildTrendPoints(lastDays: 7, now: now, todayUsedSeconds: 120)
        XCTAssertEqual(series.count, 7)
        XCTAssertEqual(series.first?.opens, 0)
        XCTAssertEqual(series.last?.opens, 1)
        XCTAssertEqual(series.last?.completions, 1)
        XCTAssertEqual(series.last?.usedSeconds, 120)

        let twoDaysAgo = cal.date(byAdding: .day, value: -2, to: cal.startOfDay(for: now))!
        agg.recordOpen(at: twoDaysAgo)
        agg.recordOpen(at: twoDaysAgo)

        let series2 = agg.buildTrendPoints(lastDays: 7, now: now, todayUsedSeconds: 120)
        let past = series2.first { cal.isDate($0.dayStart, inSameDayAs: twoDaysAgo) }
        XCTAssertEqual(past?.opens, 2)
    }

    func testCloseDay_recordsScreenTimeForCompletedDay() throws {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(secondsFromGMT: 0)!
        let suite = UserDefaults(suiteName: "test.pad.close.\(UUID().uuidString)")!
        let now = cal.date(from: DateComponents(year: 2026, month: 5, day: 10, hour: 10))!
        let agg = ParentActivityDailyAggregator(defaults: suite, calendar: cal)
        let pastStart = cal.date(byAdding: .day, value: -3, to: cal.startOfDay(for: now))!
        agg.closeDay(atStartOfDay: pastStart, totalUsedSeconds: 600)

        let series = agg.buildTrendPoints(lastDays: 10, now: now, todayUsedSeconds: 0)
        let match = try XCTUnwrap(series.first { cal.isDate($0.dayStart, inSameDayAs: pastStart) })
        XCTAssertEqual(match.usedSeconds, 600)
    }
}
