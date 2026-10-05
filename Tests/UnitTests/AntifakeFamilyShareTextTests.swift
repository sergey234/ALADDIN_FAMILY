import XCTest
@testable import ALADDIN

final class ElderlyScamCallPolicyTests: XCTestCase {
    func testFullScreenForEveryFamilyRole() {
        XCTAssertTrue(ElderlyScamCallPolicy.showsFullScreen(role: "elderly"))
        XCTAssertTrue(ElderlyScamCallPolicy.showsFullScreen(role: "parent"))
        XCTAssertTrue(ElderlyScamCallPolicy.showsFullScreen(role: "child"))
        XCTAssertTrue(ElderlyScamCallPolicy.showsFullScreen(role: "teenager"))
        XCTAssertFalse(ElderlyScamCallPolicy.showsFullScreen(role: nil))
        XCTAssertFalse(ElderlyScamCallPolicy.showsFullScreen(role: "guest"))
    }

    func testCalmDoesNotSend() {
        XCTAssertFalse(ElderlyScamCallPolicy.sendsFamilyAlert(pressedMoneyOrCode: false))
        XCTAssertTrue(ElderlyScamCallPolicy.sendsFamilyAlert(pressedMoneyOrCode: true))
    }

    func testRepeatGuardIsSeconds() {
        XCTAssertFalse(ElderlyScamCallPolicy.allowsAnotherSend(lastSentAt: 100, now: 105))
        XCTAssertTrue(ElderlyScamCallPolicy.allowsAnotherSend(lastSentAt: 100, now: 109))
        XCTAssertLessThan(ElderlyScamCallPolicy.repeatGuardSeconds, 60)
    }
}

final class AntifakeFamilyShareTextTests: XCTestCase {
    func testBuildIncludesVerdictAndReasonsRU() {
        let verdict = SecurityVerdict(
            verdict: .likelyFake,
            confidence: 0.9,
            reasons: ["urgency_manipulation"],
            reasonsHuman: ["Просьба срочно перевести деньги"],
            summaryHuman: "Похоже на мошенничество.",
            source: "ensemble_text"
        )
        let l10n = LocalizationManager()
        l10n.currentLanguage = .russian
        let text = AntifakeFamilyShareText.build(verdict: verdict, localizationManager: l10n)
        XCTAssertTrue(text.contains("ALADDIN"))
        XCTAssertTrue(text.contains("90%") || text.contains("90"))
        XCTAssertTrue(text.contains("Просьба срочно перевести деньги"))
        XCTAssertTrue(text.contains("Похоже на мошенничество."))
    }

    func testBuildENUsesEnglishFooter() {
        let verdict = SecurityVerdict(
            verdict: .uncertain,
            confidence: 0.4,
            reasons: ["uncertain"],
            source: "ensemble_text"
        )
        let l10n = LocalizationManager()
        l10n.currentLanguage = .english
        let text = AntifakeFamilyShareText.build(verdict: verdict, localizationManager: l10n)
        XCTAssertTrue(text.lowercased().contains("helper") || text.lowercased().contains("estimate"))
    }
}
