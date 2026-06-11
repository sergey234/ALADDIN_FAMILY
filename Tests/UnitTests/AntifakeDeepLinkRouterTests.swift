import XCTest
@testable import ALADDIN

final class AntifakeDeepLinkRouterTests: XCTestCase {

    func testRecognizesAntifakeCheckDeepLink() {
        let url = URL(string: "aladdin://antifake/check")!
        XCTAssertTrue(AntifakeDeepLinkRouter.isAntifakeCheckDeepLink(url))
    }

    func testRejectsUnrelatedDeepLinks() {
        let url = URL(string: "aladdin://mnemo/review?category=games")!
        XCTAssertFalse(AntifakeDeepLinkRouter.isAntifakeCheckDeepLink(url))
    }

    func testParsesModeHint() {
        let url = URL(string: "aladdin://antifake/check?mode=url")!
        XCTAssertEqual(AntifakeDeepLinkRouter.parseModeHint(from: url), .url)
    }

    func testBuildsCheckURLWithMode() {
        let url = AntifakeDeepLinkRouter.checkURL(mode: .text)
        XCTAssertEqual(url.host, "antifake")
        XCTAssertTrue(url.absoluteString.contains("mode=text"))
    }
}
