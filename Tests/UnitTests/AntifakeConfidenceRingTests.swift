import XCTest
@testable import ALADDIN

final class AntifakeConfidenceRingTests: XCTestCase {

    func testMediaVariantUsesRingPercent() {
        let verdict = SecurityVerdict(
            verdict: .likelyFake,
            confidence: 0.73,
            reasons: ["deepfake_signal"],
            source: "real_agent"
        )
        let presentation = verdict.presentation
        XCTAssertEqual(presentation.riskPercent, 73)
        XCTAssertTrue(presentation.showsRiskMeter)
    }

    func testProvenanceDecodeFromAPI() throws {
        let json = """
        {
          "verdict": "uncertain",
          "confidence": 0.4,
          "reasons": ["document_agent_unavailable"],
          "source": "rule_engine",
          "provenance": { "status": "found", "issuer": "Adobe PDF Library" }
        }
        """.data(using: .utf8)!
        let verdict = try SecurityVerdictParsers.decodeVerdict(from: json)
        XCTAssertEqual(verdict.provenance?.status, .found)
        XCTAssertEqual(verdict.provenance?.issuer, "Adobe PDF Library")
    }
}
