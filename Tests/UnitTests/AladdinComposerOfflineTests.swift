import XCTest
@testable import ALADDIN

final class AladdinComposerOfflineTests: XCTestCase {
    func testComposerLineCount_emptyIsOne() {
        XCTAssertEqual(AladdinComposerMetrics.lineCount(for: "", width: 280), 1)
    }

    func testComposerLineCount_clampsToFive() {
        let text = Array(repeating: "word word word word word word", count: 20).joined(separator: "\n")
        XCTAssertEqual(AladdinComposerMetrics.lineCount(for: text, width: 200), 5)
    }

    func testComposerLineCount_newlines() {
        XCTAssertEqual(AladdinComposerMetrics.lineCount(for: "a\nb\nc", width: 400), 3)
    }

    func testLeadTime_wrapsMidnight() {
        let lead = LocalDailyReminderMath.leadTime(bedtimeHour: 0, bedtimeMinute: 10, minutesBefore: 30)
        XCTAssertEqual(lead.hour, 23)
        XCTAssertEqual(lead.minute, 40)
    }

    func testLeadTime_sameEvening() {
        let lead = LocalDailyReminderMath.leadTime(bedtimeHour: 22, bedtimeMinute: 30, minutesBefore: 30)
        XCTAssertEqual(lead.hour, 22)
        XCTAssertEqual(lead.minute, 0)
    }

    func testNextFire_pastSlotGoesTomorrow() {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(secondsFromGMT: 0)!
        let now = cal.date(from: DateComponents(year: 2026, month: 9, day: 10, hour: 23, minute: 0))!
        let fire = LocalDailyReminderMath.nextFire(hour: 22, minute: 0, now: now, calendar: cal)
        XCTAssertEqual(cal.component(.day, from: fire), 11)
        XCTAssertEqual(cal.component(.hour, from: fire), 22)
    }

    func testNextFire_futureSlotToday() {
        var cal = Calendar(identifier: .gregorian)
        cal.timeZone = TimeZone(secondsFromGMT: 0)!
        let now = cal.date(from: DateComponents(year: 2026, month: 9, day: 10, hour: 18, minute: 0))!
        let fire = LocalDailyReminderMath.nextFire(hour: 22, minute: 0, now: now, calendar: cal)
        XCTAssertEqual(cal.component(.day, from: fire), 10)
        XCTAssertEqual(cal.component(.hour, from: fire), 22)
    }

    func testBundledCatalogHasThreeStories() {
        let stories = BundledSleepStories.catalog()
        XCTAssertEqual(stories.map(\.id), ["cloud", "garden", "stars"])
        XCTAssertNotNil(BundledSleepStories.script(id: "cloud"))
    }

    func testMergedKeepsBundleWhenApiEmptyAudio() {
        let api = [
            WellnessSleepStoryDTO(id: "cloud", title: "API Cloud", durationMin: 9, audioUrl: nil),
            WellnessSleepStoryDTO(id: "river", title: "River", durationMin: 8, audioUrl: "https://example.com/r.m4a"),
        ]
        let merged = BundledSleepStories.merged(apiStories: api)
        XCTAssertEqual(merged.first?.id, "cloud")
        XCTAssertEqual(merged.last?.id, "river")
        XCTAssertTrue(merged.contains(where: { $0.id == "garden" }))
    }

    func testResolvePresence_textFocusForcesFocused() {
        XCTAssertEqual(
            CompanionHeroLayout.resolvePresence(
                messagesEmpty: true,
                isVoiceActive: false,
                userPinnedChrome: false,
                immersiveEnabled: true,
                pinMode: .alwaysStandard,
                isTextInputFocused: true
            ),
            .focused
        )
    }

    func testResolvePresence_textFocusWinsOverVoice() {
        XCTAssertEqual(
            CompanionHeroLayout.resolvePresence(
                messagesEmpty: true,
                isVoiceActive: true,
                userPinnedChrome: false,
                immersiveEnabled: true,
                pinMode: .auto,
                isTextInputFocused: true
            ),
            .focused
        )
    }
}

private final class MockOutboundDeliverer: AladdinOutboundDelivering, @unchecked Sendable {
    var checkins: [WellnessCheckinDraft] = []
    var habits: [FamilyHabitRemindersConfig] = []
    var failCheckin = false

    func deliverCheckin(_ draft: WellnessCheckinDraft) async throws {
        if failCheckin { throw URLError(.notConnectedToInternet) }
        checkins.append(draft)
    }

    func deliverHabitConfig(_ config: FamilyHabitRemindersConfig) async throws {
        habits.append(config)
    }
}

private final class AuthFailOutboundDeliverer: AladdinOutboundDelivering, @unchecked Sendable {
    func deliverCheckin(_ draft: WellnessCheckinDraft) async throws {
        throw NetworkError.unauthorized("expired")
    }

    func deliverHabitConfig(_ config: FamilyHabitRemindersConfig) async throws {
        throw NetworkError.unauthorized("expired")
    }
}

final class AladdinOutboundQueueTests: XCTestCase {
    func testEnqueueAndFlushCheckin() async {
        let defaults = UserDefaults(suiteName: "ux-co-queue-\(UUID().uuidString)")!
        defaults.removePersistentDomain(forName: defaults.dictionaryRepresentation().keys.joined())
        let mock = MockOutboundDeliverer()
        let queue = AladdinOutboundQueue(defaults: defaults, deliverer: mock)
        let draft = WellnessCheckinDraft(mood: "ok", sleepHours: 7, stressLevel: 2, savedAt: Date())
        await queue.enqueueCheckin(draft)
        let remaining = await queue.flush()
        XCTAssertEqual(remaining, 0)
        XCTAssertEqual(mock.checkins.count, 1)
        XCTAssertEqual(mock.checkins.first?.mood, "ok")
    }

    func testFailedFlushKeepsJob() async {
        let defaults = UserDefaults(suiteName: "ux-co-queue-fail-\(UUID().uuidString)")!
        let mock = MockOutboundDeliverer()
        mock.failCheckin = true
        let queue = AladdinOutboundQueue(defaults: defaults, deliverer: mock)
        await queue.enqueueCheckin(WellnessCheckinDraft(mood: "sad", sleepHours: 5, stressLevel: 4, savedAt: Date()))
        let remaining = await queue.flush()
        XCTAssertEqual(remaining, 1)
        XCTAssertTrue(await queue.hasPendingCheckin())
    }

    func testHabitConfigLastWriteWins() async {
        let defaults = UserDefaults(suiteName: "ux-co-queue-habit-\(UUID().uuidString)")!
        let mock = MockOutboundDeliverer()
        let queue = AladdinOutboundQueue(defaults: defaults, deliverer: mock)
        var first = FamilyHabitRemindersConfig.empty
        var water = first.schedule(for: .water)
        water.enabled = true
        first.setSchedule(water, for: .water)
        var second = first
        var wind = second.schedule(for: .windDown)
        wind.enabled = true
        second.setSchedule(wind, for: .windDown)
        await queue.enqueueHabitConfig(first)
        await queue.enqueueHabitConfig(second)
        XCTAssertEqual(await queue.pendingCount(), 1)
        _ = await queue.flush()
        XCTAssertEqual(mock.habits.count, 1)
        XCTAssertTrue(mock.habits[0].schedule(for: .windDown).enabled)
    }

    func testPermanentAuthFailureIsDroppedOnFlush() async {
        let defaults = UserDefaults(suiteName: "ux-co-queue-auth-\(UUID().uuidString)")!
        let queue = AladdinOutboundQueue(defaults: defaults, deliverer: AuthFailOutboundDeliverer())
        await queue.enqueueCheckin(WellnessCheckinDraft(mood: "ok", sleepHours: 7, stressLevel: 1, savedAt: Date()))
        let remaining = await queue.flush()
        XCTAssertEqual(remaining, 0)
        XCTAssertFalse(await queue.hasPendingCheckin())
    }

    func testErrorPolicy_authIsNotEnqueueable() {
        XCTAssertFalse(AladdinOutboundErrorPolicy.shouldEnqueue(NetworkError.unauthorized(nil)))
        XCTAssertFalse(AladdinOutboundErrorPolicy.shouldEnqueue(NetworkError.forbidden(nil)))
        XCTAssertTrue(AladdinOutboundErrorPolicy.shouldEnqueue(URLError(.notConnectedToInternet)))
        XCTAssertTrue(AladdinOutboundErrorPolicy.shouldEnqueue(NetworkError.internalServerError(nil)))
    }

    func testBackoffDelayGrowsAndCaps() {
        XCTAssertEqual(AladdinOutboundBackoff.delaySeconds(afterFailures: 1), 2)
        XCTAssertEqual(AladdinOutboundBackoff.delaySeconds(afterFailures: 3), 8)
        XCTAssertEqual(AladdinOutboundBackoff.delaySeconds(afterFailures: 20), AladdinOutboundBackoff.maxSeconds)
    }

    func testFlushSkipsDuringBackoffWindow() async {
        let defaults = UserDefaults(suiteName: "ux-co-queue-backoff-\(UUID().uuidString)")!
        let mock = MockOutboundDeliverer()
        mock.failCheckin = true
        let queue = AladdinOutboundQueue(defaults: defaults, deliverer: mock)
        let t0 = Date(timeIntervalSince1970: 1_700_000_000)
        await queue.enqueueCheckin(WellnessCheckinDraft(mood: "ok", sleepHours: 7, stressLevel: 1, savedAt: t0))
        _ = await queue.flush(now: t0)
        XCTAssertNotNil(await queue.backoffUntil(now: t0))
        mock.failCheckin = false
        let stillPending = await queue.flush(now: t0.addingTimeInterval(0.5))
        XCTAssertEqual(stillPending, 1)
        XCTAssertEqual(mock.checkins.count, 0)
        let cleared = await queue.flush(now: t0.addingTimeInterval(10))
        XCTAssertEqual(cleared, 0)
        XCTAssertEqual(mock.checkins.count, 1)
    }
}
