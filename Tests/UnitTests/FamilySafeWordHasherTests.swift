import XCTest
@testable import ALADDIN

final class FamilySafeWordHasherTests: XCTestCase {
    func testNormalizeCollapsesWhitespaceAndCase() {
        XCTAssertEqual(FamilySafeWordHasher.normalizePhrase("  Blue   Moon  "), "blue moon")
    }

    func testValidateRequiresTwoWords() {
        XCTAssertEqual(FamilySafeWordHasher.validatePhrase("x"), "phrase_too_short")
        XCTAssertEqual(FamilySafeWordHasher.validatePhrase("singleword"), "phrase_need_two_words")
        XCTAssertNil(FamilySafeWordHasher.validatePhrase("blue moon"))
    }

    func testHashAndVerifyRoundTrip() {
        let first = FamilySafeWordHasher.hashPhrase("blue moon")
        XCTAssertTrue(
            FamilySafeWordHasher.verifyPhrase("BLUE  moon", saltHex: first.saltHex, hashHex: first.hashHex)
        )
        XCTAssertFalse(
            FamilySafeWordHasher.verifyPhrase("red sun", saltHex: first.saltHex, hashHex: first.hashHex)
        )
    }

    func testDeterministicWithFixedSalt() {
        let salt = String(repeating: "ab", count: 16)
        let a = FamilySafeWordHasher.hashPhrase("blue moon", saltHex: salt)
        let b = FamilySafeWordHasher.hashPhrase("blue moon", saltHex: salt)
        XCTAssertEqual(a.hashHex, b.hashHex)
    }
}
