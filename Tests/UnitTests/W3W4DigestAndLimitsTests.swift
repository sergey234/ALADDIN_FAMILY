import XCTest
@testable import ALADDIN

/// W3-3 / W3-4: readback for local time cap + digest line formatting.
final class W3W4DigestAndLimitsTests: XCTestCase {

    private let dailyLimitKey = "content.time.dailyLimitSec"

    override func tearDown() {
        LocalizationManager.forcedLanguage = nil
        super.tearDown()
    }

    func testTimeTrackerSetDailyLimitMinutesReadback() {
        let defaults = UserDefaults.standard
        let previous = defaults.integer(forKey: dailyLimitKey)
        defer {
            if defaults.object(forKey: dailyLimitKey) != nil {
                defaults.set(previous, forKey: dailyLimitKey)
            }
        }

        let tracker = TimeTracker.shared
        tracker.setDailyLimitMinutes(120)
        XCTAssertEqual(tracker.dailyLimitSec, 120 * 60)

        tracker.setDailyLimitMinutes(3)
        XCTAssertEqual(tracker.dailyLimitSec, 5 * 60, "minimum 5 minutes")

        tracker.setDailyLimitMinutes(60 * 30)
        XCTAssertEqual(tracker.dailyLimitSec, 24 * 60 * 60, "clamped to 24h")
    }

    func testActivityDigestServiceFormatsLines() {
        LocalizationManager.forcedLanguage = .english
        let loc = LocalizationManager.shared
        let snap = ParentDashboardSnapshot(
            totalOpens: 0,
            totalCompletions: 0,
            completionRate: 0,
            currentStreakDays: 4,
            remainingTimeSecToday: 600,
            unlockedAchievements: []
        )
        let day = ParentDashboardDayPoint(
            id: "d1",
            dayStart: Date(timeIntervalSince1970: 1_700_000_000),
            opens: 3,
            completions: 2,
            usedSeconds: 3_660
        )
        let lines = ActivityDigestService.buildDigestLines(
            snapshot: snap,
            todayPoint: day,
            localizationManager: loc
        )
        XCTAssertEqual(lines.count, 2)
        XCTAssertTrue(lines[0].contains("3"), "opens: \(lines[0])")
        XCTAssertTrue(lines[0].contains("2"), "completions: \(lines[0])")
        XCTAssertTrue(lines[0].contains("61"), "used minutes: \(lines[0])")
        XCTAssertTrue(lines[1].contains("4"), "streak: \(lines[1])")
    }
}
