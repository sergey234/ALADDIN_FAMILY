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

    func testPostCallCheckDeepLinkDistinctFromTextCheck() {
        let postCall = URL(string: "aladdin://antifake/call-check")!
        let text = URL(string: "aladdin://antifake/check")!
        XCTAssertTrue(AntifakeDeepLinkRouter.isPostCallCheckDeepLink(postCall))
        XCTAssertFalse(AntifakeDeepLinkRouter.isPostCallCheckDeepLink(text))
    }

    func testRecognizesUniversalAntifakeLink() {
        let url = URL(string: "https://aladdin-ai.ru/antifake.html?text=hello")!
        XCTAssertTrue(AntifakeDeepLinkRouter.isUniversalAntifakeLink(url))
        XCTAssertTrue(AntifakeDeepLinkRouter.isAntifakeCheckDeepLink(url))
    }

    func testParsesWebPrefillFromUniversalLink() {
        let url = URL(string: "https://aladdin-ai.ru/antifake.html?text=scam%20sms")!
        let payload = AntifakeDeepLinkRouter.parseWebPrefill(from: url)
        XCTAssertEqual(payload?.mode, .text)
        XCTAssertEqual(payload?.value, "scam sms")
    }

    func testParsesSharedVerdictFromUniversalLink() {
        let url = URL(string: "https://aladdin-ai.ru/antifake.html?verdict=likely_fake&confidence=0.9")!
        let parsed = AntifakeDeepLinkRouter.parseSharedVerdict(from: url)
        XCTAssertEqual(parsed?.verdict, "likely_fake")
        XCTAssertEqual(parsed?.confidence, 0.9)
    }
}
