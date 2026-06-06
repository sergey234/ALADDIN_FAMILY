import XCTest
@testable import ALADDIN

final class MnemonicCapstoneStoreTests: XCTestCase {

    private var suite: UserDefaults!

    override func setUp() {
        super.setUp()
        suite = UserDefaults(suiteName: "test.mnemo.capstone.\(UUID().uuidString)")!
    }

    override func tearDown() {
        suite = nil
        super.tearDown()
    }

    func testRecordCompletion_persistsTopicAndDuration() {
        let store = MnemonicCapstoneStore(defaults: suite)
        XCTAssertFalse(store.hasCompleted(childId: "child-cap"))
        let record = store.recordCompletion(topicIndex: 2, teachBackSeconds: 95, childId: "child-cap")
        XCTAssertEqual(record.topicIndex, 2)
        XCTAssertEqual(record.teachBackSeconds, 95)
        XCTAssertTrue(store.hasCompleted(childId: "child-cap"))
    }

    func testCapstoneCompletion_unlocksChampionLevel() {
        let tracker = MnemonicSkillTracker(defaults: suite)
        XCTAssertEqual(tracker.currentLevel(childId: "child-champ"), .novice)
        tracker.recordCapstoneCompleted(childId: "child-champ")
        XCTAssertEqual(tracker.currentLevel(childId: "child-champ"), .champion)
    }

    func testTeachBackDuration_isThreeMinutes() {
        XCTAssertEqual(MnemonicCapstoneStore.teachBackDurationSeconds, 180)
        XCTAssertEqual(MnemonicCapstoneStore.itemId, "study.26")
        XCTAssertEqual(MnemonicCapstoneStore.topicLocalizationKeys.count, 6)
    }
}
