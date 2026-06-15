import XCTest
@testable import ALADDIN

final class MnemonicSRSStoreTests: XCTestCase {

    func testRecordSuccess_advancesBoxAndSchedulesNextReview() {
        let suite = UserDefaults(suiteName: "test.mnemo.srs.\(UUID().uuidString)")!
        let store = MnemonicSRSStore(defaults: suite)
        let now = Date(timeIntervalSince1970: 1_700_000_000)
        store.scheduleInitial(itemId: "study.01", now: now)
        store.recordSuccess(itemId: "study.01", now: now)
        XCTAssertEqual(store.dueItems(category: ChildCategoryKey.study, now: now).count, 0)
    }

    func testRecordFailure_resetsBoxAndSchedulesTomorrow() {
        let suite = UserDefaults(suiteName: "test.mnemo.srs.fail.\(UUID().uuidString)")!
        let store = MnemonicSRSStore(defaults: suite)
        let now = Date(timeIntervalSince1970: 1_700_000_000)
        store.recordSuccess(itemId: "study.02", now: now)
        store.recordSuccess(itemId: "study.02", now: now)
        store.recordFailure(itemId: "study.02", now: now)
        let due = store.dueItems(category: ChildCategoryKey.study, now: now)
        XCTAssertTrue(due.contains("study.02"))
    }

    func testDueItems_filtersByCategoryPrefix() {
        let suite = UserDefaults(suiteName: "test.mnemo.srs.due.\(UUID().uuidString)")!
        let store = MnemonicSRSStore(defaults: suite)
        let now = Date(timeIntervalSince1970: 1_700_000_000)
        store.scheduleInitial(itemId: "games.05", now: now)
        store.scheduleInitial(itemId: "study.03", now: now)
        XCTAssertEqual(store.dueToday(category: ChildCategoryKey.games, now: now), 1)
        XCTAssertEqual(store.dueToday(category: ChildCategoryKey.study, now: now), 1)
    }

    func testSkillTracker_levelsProgress() {
        let suite = UserDefaults(suiteName: "test.mnemo.skill.\(UUID().uuidString)")!
        let tracker = MnemonicSkillTracker(defaults: suite)
        XCTAssertEqual(tracker.currentLevel(), .novice)
        tracker.recordSuccessfulRecall(count: 10)
        XCTAssertEqual(tracker.currentLevel(), .apprentice)
        tracker.recordAnchorPlaced(count: 20)
        XCTAssertEqual(tracker.currentLevel(), .champion)
    }

    func testStudyJourneyStop_isSemanticNotHash() {
        XCTAssertEqual(MnemonicStudyTechniqueMap.journeyStop(for: "study.01"), 1)
        XCTAssertEqual(MnemonicStudyTechniqueMap.journeyStop(for: "study.15"), 15)
    }

    func testDeepLinkRouter_parsesReviewCategory() {
        let url = URL(string: "aladdin://mnemo/review?category=games")!
        XCTAssertEqual(MnemoDeepLinkRouter.parseReviewCategory(from: url), ChildCategoryKey.games)
        XCTAssertEqual(MnemoDeepLinkRouter.shortName(for: ChildCategoryKey.study), "study")
    }

    func testNotificationScheduler_primaryCategoryPicksHighestDueCount() {
        let suite = UserDefaults(suiteName: "test.mnemo.scheduler.\(UUID().uuidString)")!
        let store = MnemonicSRSStore(defaults: suite)
        let now = Date(timeIntervalSince1970: 1_700_000_000)
        store.scheduleInitial(itemId: "games.05", now: now)
        store.scheduleInitial(itemId: "study.01", now: now)
        store.scheduleInitial(itemId: "study.02", now: now)
        store.uiTestForceDue(itemId: "games.05", now: now)
        store.uiTestForceDue(itemId: "study.01", now: now)
        store.uiTestForceDue(itemId: "study.02", now: now)

        let scheduler = MnemonicNotificationScheduler(srsStore: store)
        XCTAssertEqual(MnemonicNotificationScheduler.totalDueCount(store: store, now: now), 3)
        XCTAssertEqual(MnemonicNotificationScheduler.primaryReviewCategory(store: store, now: now), ChildCategoryKey.study)
        _ = scheduler
    }

    func testICloudSync_optInPersistsFlag() {
        let suite = UserDefaults(suiteName: "test.mnemo.icloud.\(UUID().uuidString)")!
        let store = MnemonicSRSStore(defaults: suite)
        XCTAssertFalse(store.isICloudSyncEnabled)
        store.isICloudSyncEnabled = true
        XCTAssertTrue(store.isICloudSyncEnabled)
        let reloaded = MnemonicSRSStore(defaults: suite)
        XCTAssertTrue(reloaded.isICloudSyncEnabled)
    }

    func testUnifiedDueItems_andRecallMasteryPercent() {
        let suite = UserDefaults(suiteName: "test.mnemo.srs.unified.\(UUID().uuidString)")!
        let store = MnemonicSRSStore(defaults: suite)
        let now = Date(timeIntervalSince1970: 1_700_000_000)
        store.scheduleInitial(itemId: "games.05", now: now)
        store.scheduleInitial(itemId: "study.03", now: now)
        XCTAssertEqual(store.unifiedDueToday(now: now), 2)
        XCTAssertEqual(store.unifiedDueItems(now: now).count, 2)
        XCTAssertEqual(store.categoryId(for: "games.05"), ChildCategoryKey.games)
        XCTAssertEqual(store.categoryId(for: "study.03"), ChildCategoryKey.study)
        XCTAssertEqual(store.recallMasteryPercent(itemId: "games.05"), 0)
        store.recordSuccess(itemId: "games.05", now: now)
        XCTAssertEqual(store.recallMasteryPercent(itemId: "games.05"), 25)
    }
}
