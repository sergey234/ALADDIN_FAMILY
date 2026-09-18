import XCTest
@testable import ALADDIN

final class VoiceIntentRouterTests: XCTestCase {

    func testLinkOnlyOpensAntifakeWithoutDictatingURL() {
        let r = VoiceIntentRouter.parse("ссылка")
        XCTAssertEqual(r.intent, .antifakeURL)
        XCTAssertTrue(r.remainder.isEmpty)
        XCTAssertTrue(r.shouldOpenAntifake)
        XCTAssertTrue(r.antifakePrefill.isEmpty)
    }

    func testCheckLinkPhrase() {
        let r = VoiceIntentRouter.parse("проверь ссылку")
        XCTAssertEqual(r.intent, .antifakeURL)
        XCTAssertTrue(r.shouldOpenAntifake)
    }

    func testLinkPrefixRU() {
        let r = VoiceIntentRouter.parse("ссылка https://evil.example/phish")
        XCTAssertEqual(r.intent, .antifakeURL)
        XCTAssertEqual(r.intentTag, "intent_antifake_url")
        XCTAssertEqual(r.remainder, "https://evil.example/phish")
        XCTAssertEqual(r.fullTranscript, "ссылка https://evil.example/phish")
    }

    func testLinkAliasSTTTypo() {
        let r = VoiceIntentRouter.parse("сылка https://t.me/x")
        XCTAssertEqual(r.intent, .antifakeURL)
        XCTAssertTrue(r.remainder.contains("t.me"))
    }

    func testCheckPrefixEN() {
        let r = VoiceIntentRouter.parse("check this message looks fake")
        XCTAssertEqual(r.intent, .securityCheck)
        XCTAssertEqual(r.remainder, "this message looks fake")
    }

    func testMultiWordRemind() {
        let r = VoiceIntentRouter.parse("не забыть позвонить в школу")
        XCTAssertEqual(r.intent, .remind)
        XCTAssertEqual(r.remainder, "позвонить в школу")
    }

    func testIdeaPrefix() {
        let r = VoiceIntentRouter.parse("идея добавить виджет статуса")
        XCTAssertEqual(r.intent, .idea)
        XCTAssertEqual(r.remainder, "добавить виджет статуса")
    }

    func testIncidentPrefix() {
        let r = VoiceIntentRouter.parse("тревога странный звонок с банка")
        XCTAssertEqual(r.intent, .incident)
        XCTAssertTrue(r.remainder.contains("банк"))
    }

    func testStatusPrefix() {
        let r = VoiceIntentRouter.parse("статус")
        XCTAssertEqual(r.intent, .status)
        XCTAssertTrue(r.remainder.isEmpty)
    }

    func testBreakPrefix() {
        let r = VoiceIntentRouter.parse("перерыв")
        XCTAssertEqual(r.intent, .breakSegment)
    }

    func testDefaultNoteWithoutPrefix() {
        let r = VoiceIntentRouter.parse("работаю над схемой вознаграждения")
        XCTAssertEqual(r.intent, .note)
        XCTAssertEqual(r.remainder, "работаю над схемой вознаграждения")
        XCTAssertEqual(r.intentTag, "intent_note")
    }

    func testMidSentenceCheckIsNotIntent() {
        let r = VoiceIntentRouter.parse("Сегодня проверка дома прошла нормально")
        XCTAssertEqual(r.intent, .note)
        XCTAssertFalse(r.shouldOpenAntifake)
    }

    func testLeadingOnlyLinkInLongSentence() {
        let r = VoiceIntentRouter.parse("ссылка https://ok.ru/x потом ещё текст")
        XCTAssertEqual(r.intent, .antifakeURL)
        XCTAssertTrue(r.shouldOpenAntifake)
    }

    func testEmptyAndWhitespace() {
        XCTAssertEqual(VoiceIntentRouter.parse("   ").intent, .note)
        XCTAssertEqual(VoiceIntentRouter.parse("").intent, .note)
    }

    func testPunctuationOnPrefix() {
        let r = VoiceIntentRouter.parse("проверка, вот этот текст")
        XCTAssertEqual(r.intent, .securityCheck)
        XCTAssertEqual(r.remainder, "вот этот текст")
    }

    func testCaseInsensitiveEN() {
        let r = VoiceIntentRouter.parse("LINK https://a.com")
        XCTAssertEqual(r.intent, .antifakeURL)
    }

    func testShouldOpenAntifakeOnlyForLinkAndCheck() {
        XCTAssertTrue(VoiceIntentRouter.parse("ссылка x").shouldOpenAntifake)
        XCTAssertTrue(VoiceIntentRouter.parse("проверка x").shouldOpenAntifake)
        XCTAssertFalse(VoiceIntentRouter.parse("идея x").shouldOpenAntifake)
        XCTAssertFalse(VoiceIntentRouter.parse("тревога x").shouldOpenAntifake)
    }
}
