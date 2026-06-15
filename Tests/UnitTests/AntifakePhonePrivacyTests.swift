import XCTest
@testable import ALADDIN

final class AntifakePhonePrivacyTests: XCTestCase {

    func testPhoneLogHashMatchesServerContract() {
        let hash = AntifakePhonePrivacy.phoneLogHash("+7 (495) 123-45-67")
        XCTAssertEqual(hash.count, 16)
        XCTAssertEqual(hash, AntifakePhonePrivacy.phoneLogHash("74951234567"))
        XCTAssertNotEqual(hash, "empty")
    }

    func testPhoneLogHashEmpty() {
        XCTAssertEqual(AntifakePhonePrivacy.phoneLogHash(""), "empty")
    }

    func testRedactPhonesInText() {
        let redacted = AntifakePhonePrivacy.redactPhonesInText("call from +7 916 123-45-67 ok")
        XCTAssertFalse(redacted.contains("916"))
        XCTAssertTrue(redacted.contains("[phone]"))
    }
}
