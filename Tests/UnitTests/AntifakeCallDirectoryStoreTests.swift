import XCTest
@testable import ALADDIN

/// D-07 — identified[] labels vs blocked[] silence on Call Directory extension.
final class AntifakeCallDirectoryStoreTests: XCTestCase {

    func testMergeDeltaBlockedRemovesFromIdentified() {
        let existing = AntifakeCallDirectorySnapshot(
            identifiedNumbers: [
                AntifakeCallDirectoryIdentifiedEntry(phoneNumber: 7_900_123_4567, label: "Possible scam?"),
                AntifakeCallDirectoryIdentifiedEntry(phoneNumber: 7_495_123_4567, label: "Possible scam?")
            ],
            blockedNumbers: [],
            updatedAt: Date(timeIntervalSince1970: 1_700_000_000)
        )
        let merged = AntifakeCallDirectoryStore.mergeDelta(
            existing: existing,
            identified: [
                AntifakeCallDirectoryIdentifiedEntry(phoneNumber: 7_800_555_3535, label: "Possible scam?")
            ],
            blocked: [7_900_123_4567],
            serverUpdatedAt: Date(timeIntervalSince1970: 1_700_000_100)
        )
        XCTAssertEqual(merged.blockedNumbers, [7_900_123_4567])
        XCTAssertEqual(merged.identifiedNumbers.map(\.phoneNumber), [7_495_123_4567, 7_800_555_3535])
        XCTAssertFalse(merged.identifiedNumbers.contains { $0.phoneNumber == 7_900_123_4567 })
    }

    func testParsePhoneNumberAcceptsE164Digits() {
        XCTAssertEqual(AntifakeCallDirectoryStore.parsePhoneNumber("+7 (900) 123-45-67"), 7_900_123_4567)
        XCTAssertNil(AntifakeCallDirectoryStore.parsePhoneNumber("123"))
    }

    func testRelocalizeKnownDefaultLabelUsesCurrentLocale() {
        let ru = "Возможный мошенник?"
        let en = "Possible scam?"
        XCTAssertEqual(
            AntifakeCallDirectoryLabelPolicy.relocalizeIfKnownDefault(ru, currentDefault: en),
            en
        )
        XCTAssertEqual(
            AntifakeCallDirectoryLabelPolicy.relocalizeIfKnownDefault(en, currentDefault: ru),
            ru
        )
        XCTAssertEqual(
            AntifakeCallDirectoryLabelPolicy.relocalizeIfKnownDefault("Custom bank scam", currentDefault: en),
            "Custom bank scam"
        )
    }
}
