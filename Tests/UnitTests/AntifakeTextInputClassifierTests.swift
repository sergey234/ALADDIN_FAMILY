import XCTest
@testable import ALADDIN

final class AntifakeTextInputClassifierTests: XCTestCase {

    func testClassifyHTTPSURL() {
        let kind = AntifakeTextInputClassifier.classify("https://example.com/news?id=1")
        guard case .url(let url) = kind else {
            return XCTFail("expected url")
        }
        XCTAssertEqual(url, "https://example.com/news?id=1")
    }

    func testClassifyWWWURLAddsScheme() {
        let kind = AntifakeTextInputClassifier.classify("www.youtube.com/watch?v=abc")
        guard case .url(let url) = kind else {
            return XCTFail("expected url")
        }
        XCTAssertTrue(url.hasPrefix("https://"))
        XCTAssertTrue(url.contains("youtube.com"))
    }

    func testClassifyPhoneNumber() {
        let kind = AntifakeTextInputClassifier.classify("+7 (900) 123-45-67")
        guard case .phone(let phone) = kind else {
            return XCTFail("expected phone")
        }
        XCTAssertTrue(phone.contains("900"))
    }

    func testClassifyPlainText() {
        let kind = AntifakeTextInputClassifier.classify("12+12=25?")
        guard case .text(let text) = kind else {
            return XCTFail("expected text")
        }
        XCTAssertEqual(text, "12+12=25?")
    }

    func testExtractURLFromSingleLine() {
        XCTAssertEqual(
            AntifakeTextInputClassifier.extractURL(from: "https://t.me/channel/post"),
            "https://t.me/channel/post"
        )
    }
}
