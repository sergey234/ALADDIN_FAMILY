import XCTest
@testable import ALADDIN

final class FamilyChatLocalHiddenStoreTests: XCTestCase {
    private let suiteName = "FamilyChatLocalHiddenStoreTests"

    override func tearDown() {
        UserDefaults(suiteName: suiteName)?.removePersistentDomain(forName: suiteName)
        super.tearDown()
    }

    func testHidePersistsAndFilters() {
        let defaults = UserDefaults(suiteName: suiteName)!
        XCTAssertFalse(FamilyChatLocalHiddenStore.isHidden("MSG_1", defaults: defaults))
        FamilyChatLocalHiddenStore.hide(messageId: "MSG_1", defaults: defaults)
        XCTAssertTrue(FamilyChatLocalHiddenStore.isHidden("MSG_1", defaults: defaults))
    }

    func testDeleteForEveryoneWindow() {
        let iso = ISO8601DateFormatter()
        iso.formatOptions = [.withInternetDateTime]
        let recent = iso.string(from: Date().addingTimeInterval(-3600))
        let old = iso.string(from: Date().addingTimeInterval(-36 * 3600))
        XCTAssertTrue(FamilyChatLocalHiddenStore.canDeleteForEveryone(isCurrentUser: true, rawTimestamp: recent))
        XCTAssertFalse(FamilyChatLocalHiddenStore.canDeleteForEveryone(isCurrentUser: true, rawTimestamp: old))
        XCTAssertFalse(FamilyChatLocalHiddenStore.canDeleteForEveryone(isCurrentUser: false, rawTimestamp: recent))
    }
}
