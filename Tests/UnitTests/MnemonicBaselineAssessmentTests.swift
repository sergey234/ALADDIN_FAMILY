import XCTest
@testable import ALADDIN

final class MnemonicBaselineAssessmentTests: XCTestCase {

    private var suite: UserDefaults!

    override func setUp() {
        super.setUp()
        suite = UserDefaults(suiteName: "test.mnemo.baseline.\(UUID().uuidString)")!
    }

    override func tearDown() {
        suite = nil
        super.tearDown()
    }

    func testRawScorePercent_mapsCorrectCountToHundredScale() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        XCTAssertEqual(assessment.rawScorePercent(correctCount: 0), 0)
        XCTAssertEqual(assessment.rawScorePercent(correctCount: 3), 60)
        XCTAssertEqual(assessment.rawScorePercent(correctCount: 5), 100)
    }

    func testRecordResult_persistsLatestSession() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        let result = assessment.recordResult(correctCount: 4, elapsedStudySeconds: 75, childId: "child-baseline")
        XCTAssertEqual(result.correctCount, 4)
        XCTAssertEqual(result.rawScorePercent, 80)
        XCTAssertEqual(result.memoryQuotient, 86)
        XCTAssertEqual(assessment.latestResult(childId: "child-baseline")?.correctCount, 4)
        XCTAssertEqual(assessment.latestMemoryQuotient(childId: "child-baseline"), 86)
        XCTAssertEqual(assessment.allResults(childId: "child-baseline").count, 1)
    }

    func testMemoryQuotient_perfectRecallFasterStudyScoresHigher() {
        let fast = MnemonicBaselineAssessment.memoryQuotient(correctCount: 5, elapsedStudySeconds: 0)
        let slow = MnemonicBaselineAssessment.memoryQuotient(correctCount: 5, elapsedStudySeconds: 120)
        XCTAssertEqual(fast, 100)
        XCTAssertEqual(slow, 100)
        let fastPartial = MnemonicBaselineAssessment.memoryQuotient(correctCount: 4, elapsedStudySeconds: 0)
        let slowPartial = MnemonicBaselineAssessment.memoryQuotient(correctCount: 4, elapsedStudySeconds: 120)
        XCTAssertEqual(fastPartial, 95)
        XCTAssertEqual(slowPartial, 80)
        XCTAssertGreaterThan(fastPartial, slowPartial)
    }

    func testMemoryQuotient_speedBonusScalesWithStudyTime() {
        let atHalf = MnemonicBaselineAssessment.memoryQuotient(correctCount: 3, elapsedStudySeconds: 60)
        let atFull = MnemonicBaselineAssessment.memoryQuotient(correctCount: 3, elapsedStudySeconds: 120)
        XCTAssertEqual(atHalf, 68)
        XCTAssertEqual(atFull, 60)
        XCTAssertGreaterThan(atHalf, atFull)
    }

    func testMemoryQuotient_zeroRecallReturnsZero() {
        XCTAssertEqual(MnemonicBaselineAssessment.memoryQuotient(correctCount: 0, elapsedStudySeconds: 10), 0)
    }

    func testMemoryQuotient_isBoundedZeroToHundred() {
        let mq = MnemonicBaselineAssessment.memoryQuotient(correctCount: 5, elapsedStudySeconds: -5)
        XCTAssertEqual(mq, 100)
    }

    func testShouldOffer_falseAfterFirstCompletionUntilRetestWindow() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        let now = Date(timeIntervalSince1970: 1_700_000_000)
        XCTAssertNil(assessment.latestResult(childId: "child-a"))
        _ = assessment.recordResult(
            correctCount: 5,
            elapsedStudySeconds: 42,
            childId: "child-a",
            completedAt: now
        )
        XCTAssertFalse(assessment.shouldOffer(childId: "child-a", now: now))
        XCTAssertEqual(assessment.daysUntilRetest(childId: "child-a", now: now), 90)
    }

    func testQuarterlyRetest_dueAfterNinetyDays() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        let calendar = Calendar.current
        let completed = calendar.date(from: DateComponents(year: 2024, month: 1, day: 10))!
        _ = assessment.recordResult(
            correctCount: 4,
            elapsedStudySeconds: 60,
            childId: "child-q",
            completedAt: completed
        )
        let tooSoon = calendar.date(byAdding: .day, value: 89, to: completed)!
        XCTAssertFalse(assessment.isQuarterlyRetestDue(childId: "child-q", now: tooSoon))

        let due = calendar.date(byAdding: .day, value: 90, to: completed)!
        XCTAssertTrue(assessment.isQuarterlyRetestDue(childId: "child-q", now: due))
        XCTAssertEqual(assessment.offerKind(childId: "child-q", now: due), .quarterlyRetest)
    }

    func testQuarterlyRetest_blockedWhenSessionExistsInCurrentQuarter() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        let calendar = Calendar.current
        let first = calendar.date(from: DateComponents(year: 2024, month: 1, day: 5))!
        let second = calendar.date(from: DateComponents(year: 2024, month: 3, day: 28))!
        _ = assessment.recordResult(
            correctCount: 5,
            elapsedStudySeconds: 30,
            childId: "child-cap",
            completedAt: first
        )
        _ = assessment.recordResult(
            correctCount: 5,
            elapsedStudySeconds: 20,
            childId: "child-cap",
            completedAt: second
        )
        let attemptSameQuarter = calendar.date(from: DateComponents(year: 2024, month: 3, day: 30))!
        XCTAssertTrue(assessment.hasSession(inCalendarQuarterOf: attemptSameQuarter, childId: "child-cap"))
        XCTAssertFalse(assessment.isQuarterlyRetestDue(childId: "child-cap", now: attemptSameQuarter))
    }

    func testTrendPoints_exposesMQOnlyWithoutWords() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        let calendar = Calendar.current
        let first = calendar.date(from: DateComponents(year: 2024, month: 2, day: 1))!
        let second = calendar.date(from: DateComponents(year: 2024, month: 8, day: 1))!
        let firstResult = assessment.recordResult(
            correctCount: 3,
            elapsedStudySeconds: 80,
            childId: "child-trend",
            completedAt: first
        )
        let secondResult = assessment.recordResult(
            correctCount: 5,
            elapsedStudySeconds: 40,
            childId: "child-trend",
            completedAt: second
        )
        let points = assessment.trendPoints(childId: "child-trend", calendar: calendar)
        XCTAssertEqual(points.count, 2)
        XCTAssertEqual(points[0].memoryQuotient, firstResult.memoryQuotient)
        XCTAssertEqual(points[1].memoryQuotient, secondResult.memoryQuotient)
        XCTAssertTrue(points.allSatisfy { $0.quarterLabel.hasPrefix("Q") })
        XCTAssertEqual(
            assessment.memoryQuotientDelta(childId: "child-trend"),
            secondResult.memoryQuotient - firstResult.memoryQuotient
        )
    }

    func testWordLocalizationKeys_hasFiveEntries() {
        XCTAssertEqual(MnemonicBaselineAssessment.wordLocalizationKeys.count, 5)
        XCTAssertEqual(MnemonicBaselineAssessment.wordCount, 5)
        XCTAssertEqual(MnemonicBaselineAssessment.timeLimitSeconds, 120)
        XCTAssertEqual(MnemonicBaselineAssessment.retestIntervalDays, 90)
    }

    func testMemoryQuotientDelta_nilUntilSecondSession() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        XCTAssertNil(assessment.memoryQuotientDelta(childId: "child-delta"))
        _ = assessment.recordResult(correctCount: 3, elapsedStudySeconds: 90, childId: "child-delta")
        XCTAssertNil(assessment.memoryQuotientDelta(childId: "child-delta"))
        _ = assessment.recordResult(correctCount: 5, elapsedStudySeconds: 30, childId: "child-delta")
        XCTAssertNotNil(assessment.memoryQuotientDelta(childId: "child-delta"))
    }

    func testQuarterLabel_formatsQuarterAndTwoDigitYear() {
        let calendar = Calendar.current
        let date = calendar.date(from: DateComponents(year: 2026, month: 5, day: 15))!
        XCTAssertEqual(MnemonicBaselineAssessment.quarterLabel(for: date, calendar: calendar), "Q2 '26")
    }

    func testNextRetestDate_defersWhenQuarterAlreadyHasSession() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        let calendar = Calendar.current
        let first = calendar.date(from: DateComponents(year: 2024, month: 1, day: 1))!
        let retestInQuarter = calendar.date(from: DateComponents(year: 2024, month: 3, day: 15))!
        _ = assessment.recordResult(
            correctCount: 4,
            elapsedStudySeconds: 50,
            childId: "child-next",
            completedAt: first
        )
        _ = assessment.recordResult(
            correctCount: 5,
            elapsedStudySeconds: 40,
            childId: "child-next",
            completedAt: retestInQuarter
        )
        let now = calendar.date(from: DateComponents(year: 2024, month: 3, day: 20))!
        let next = assessment.nextRetestDate(childId: "child-next", now: now)
        XCTAssertNotNil(next)
        if let next {
            XCTAssertGreaterThanOrEqual(
                calendar.component(.month, from: next),
                4
            )
        }
    }

    func testDaysUntilRetest_countsDownAfterBaseline() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        let calendar = Calendar.current
        let completed = calendar.date(from: DateComponents(year: 2025, month: 1, day: 1))!
        _ = assessment.recordResult(
            correctCount: 5,
            elapsedStudySeconds: 20,
            childId: "child-days",
            completedAt: completed
        )
        let after30 = calendar.date(byAdding: .day, value: 30, to: completed)!
        XCTAssertEqual(assessment.daysUntilRetest(childId: "child-days", now: after30), 60)
    }

    func testRecordResult_persistsQuickLatestMQKey() {
        let assessment = MnemonicBaselineAssessment(defaults: suite)
        _ = assessment.recordResult(correctCount: 5, elapsedStudySeconds: 10, childId: "child-mq-key")
        let quickKey = "child.mnemo.mq.latest.v1.child-mq-key"
        XCTAssertEqual(suite.integer(forKey: quickKey), 100)
    }

    func testSessionResult_decodesLegacyPayloadWithoutStoredMQ() throws {
        let json = """
        {
            "correctCount": 4,
            "wordCount": 5,
            "rawScorePercent": 80,
            "elapsedStudySeconds": 60,
            "completedAt": 1700000000
        }
        """.data(using: .utf8)!
        let decoded = try JSONDecoder().decode(MnemonicBaselineAssessment.SessionResult.self, from: json)
        XCTAssertEqual(decoded.memoryQuotient, 88)
    }
}
