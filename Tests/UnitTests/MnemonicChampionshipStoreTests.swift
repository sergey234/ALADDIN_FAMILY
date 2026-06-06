import XCTest
@testable import ALADDIN

final class MnemonicChampionshipStoreTests: XCTestCase {

    private var suite: UserDefaults!

    override func setUp() {
        super.setUp()
        suite = UserDefaults(suiteName: "test.mnemo.championship.\(UUID().uuidString)")!
    }

    override func tearDown() {
        suite = nil
        super.tearDown()
    }

    func testConstants_matchJuniorMemoryChampionshipFormat() {
        XCTAssertEqual(MnemonicChampionshipStore.itemCount, 20)
        XCTAssertEqual(MnemonicChampionshipStore.timeLimitSeconds, 300)
        XCTAssertEqual(MnemonicChampionshipStore.itemId, "games.05")
        XCTAssertEqual(MnemonicChampionshipStore.journeyPegEmojis.count, 20)
    }

    func testRecordResult_updatesPersonalBestOnlyWhenHigher() {
        let store = MnemonicChampionshipStore(defaults: suite)
        XCTAssertEqual(store.personalBest(childId: "child-a"), 0)

        let first = store.recordResult(correctCount: 12, elapsedStudySeconds: 180, childId: "child-a")
        XCTAssertEqual(first.correctCount, 12)
        XCTAssertTrue(first.isPersonalBest)
        XCTAssertEqual(store.personalBest(childId: "child-a"), 12)

        let second = store.recordResult(correctCount: 10, elapsedStudySeconds: 200, childId: "child-a")
        XCTAssertFalse(second.isPersonalBest)
        XCTAssertEqual(store.personalBest(childId: "child-a"), 12)

        let third = store.recordResult(correctCount: 18, elapsedStudySeconds: 290, childId: "child-a")
        XCTAssertTrue(third.isPersonalBest)
        XCTAssertEqual(store.personalBest(childId: "child-a"), 18)
    }

    func testMakeSequence_isDeterministicWithSeed() {
        let store = MnemonicChampionshipStore(defaults: suite)
        let a = store.makeSequence(seed: 42)
        let b = store.makeSequence(seed: 42)
        XCTAssertEqual(a, b)
        XCTAssertEqual(Set(a).count, MnemonicChampionshipStore.itemCount)
    }

    func testUnlock_afterCapstoneCompletion() {
        let tracker = MnemonicSkillTracker(defaults: suite)
        let store = MnemonicChampionshipStore(defaults: suite)
        XCTAssertFalse(store.isUnlocked(childId: "child-unlock"))
        tracker.recordCapstoneCompleted(childId: "child-unlock")
        XCTAssertTrue(store.isUnlocked(childId: "child-unlock"))
    }
}
