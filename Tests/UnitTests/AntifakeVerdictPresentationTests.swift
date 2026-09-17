import XCTest
@testable import ALADDIN

final class AntifakeVerdictPresentationTests: XCTestCase {

    func testInsufficientDataHidesRiskMeter() {
        let verdict = SecurityVerdict(
            verdict: .insufficientData,
            confidence: 0,
            reasons: ["text_too_short"],
            source: "real_agent",
            agent: "fake_news_detection_agent"
        )
        let presentation = verdict.presentation
        XCTAssertFalse(presentation.showsRiskMeter)
        XCTAssertEqual(presentation.verdictTitleKey, "antifake_verdict_insufficient_data")
        XCTAssertEqual(presentation.sourceBadgeKey, "antifake_verdict_source_ai")
    }

    func testLikelyRealLowFakeRisk() {
        let verdict = SecurityVerdict(
            verdict: .likelyReal,
            confidence: 0.15,
            reasons: ["no_suspicious_patterns"],
            source: "real_agent"
        )
        let presentation = verdict.presentation
        XCTAssertTrue(presentation.showsRiskMeter)
        XCTAssertEqual(presentation.riskPercent, 15)
        XCTAssertEqual(presentation.riskLevelKey, "antifake_risk_low")
    }

    func testLikelyFakeHighFakeRisk() {
        let verdict = SecurityVerdict(
            verdict: .likelyFake,
            confidence: 0.87,
            reasons: ["scam"],
            source: "real_agent"
        )
        let presentation = verdict.presentation
        XCTAssertEqual(presentation.riskPercent, 87)
        XCTAssertEqual(presentation.riskLevelKey, "antifake_risk_high")
    }

    func testLocalizedReasonStripsRulesPrefix() {
        let verdict = SecurityVerdict(
            verdict: .uncertain,
            confidence: 0.4,
            reasons: ["rules:urgency_manipulation"],
            source: "ensemble_text"
        )
        let l10n = LocalizationManager()
        l10n.currentLanguage = .english
        let text = verdict.presentation.localizedReason(
            "rules:urgency_manipulation",
            localizationManager: l10n
        )
        XCTAssertFalse(text.contains("rules:"))
        XCTAssertNotEqual(text, "rules:urgency_manipulation")
        XCTAssertNotEqual(text, "urgency_manipulation")
    }
}
