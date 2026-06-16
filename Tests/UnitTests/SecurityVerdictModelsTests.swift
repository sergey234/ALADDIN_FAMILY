import XCTest
@testable import ALADDIN

final class SecurityVerdictModelsTests: XCTestCase {

    func testDecodeValidVerdict() throws {
        let json = """
        {
          "verdict": "likely_fake",
          "confidence": 0.91,
          "reasons": ["suspicious domain"],
          "source": "real_agent",
          "agent": "fake_news_detection_agent",
          "job_id": null,
          "checked_at": "2026-06-10T12:00:00.000Z",
          "premium_required": false
        }
        """
        let verdict = try SecurityVerdictParsers.decodeVerdict(from: Data(json.utf8))
        XCTAssertEqual(verdict.verdict, .likelyFake)
        XCTAssertEqual(verdict.confidence, 0.91, accuracy: 0.001)
        XCTAssertEqual(verdict.source, "real_agent")
        XCTAssertTrue(verdict.isLikelyThreat)
    }

    func testRejectMockSource() throws {
        let json = """
        {"verdict":"likely_real","confidence":1,"reasons":[],"source":"sfm_mock","premium_required":false}
        """
        XCTAssertThrowsError(try SecurityVerdictParsers.decodeVerdict(from: Data(json.utf8))) { error in
            XCTAssertEqual(error as? SecurityVerdictValidationError, .mockSourceRejected("sfm_mock"))
        }
    }

    func testDecodeJobEnqueue() throws {
        let json = """
        {"job_id":"abc-123","status":"queued"}
        """
        let job = try SecurityVerdictParsers.decodeJobEnqueue(from: Data(json.utf8))
        XCTAssertEqual(job.jobId, "abc-123")
        XCTAssertEqual(job.status, .queued)
    }

    func testPremiumGate403DetailObject() {
        let json = """
        {"detail":{"error":"premium_required","message":"Antifake checks require Premium subscription","premium_required":true}}
        """
        let outcome = PremiumGateHandler.outcome(httpStatus: 403, data: Data(json.utf8))
        XCTAssertEqual(outcome, .premiumRequired(message: "Antifake checks require Premium subscription"))
        XCTAssertTrue(outcome.requiresUpgrade)
    }

    func testPremiumGate403GenericForbidden() {
        let json = """
        {"detail":"Access denied"}
        """
        let outcome = PremiumGateHandler.outcome(httpStatus: 403, data: Data(json.utf8))
        XCTAssertEqual(outcome, .forbidden(message: "Access denied"))
    }

    func testNetworkErrorPremiumRequired() {
        let error = NetworkError.forbidden("premium_required: upgrade plan")
        XCTAssertTrue(error.isPremiumRequired)
        XCTAssertEqual(PremiumGateHandler.outcome(from: error), .premiumRequired(message: "premium_required: upgrade plan"))
    }

    func testDecodeJobPollPending() throws {
        let json = """
        {"job_id":"abc-123","status":"queued","type":"audio"}
        """
        let outcome = try SecurityVerdictParsers.decodeJobPoll(from: Data(json.utf8))
        guard case .pending(let pending) = outcome else {
            return XCTFail("expected pending")
        }
        XCTAssertEqual(pending.jobId, "abc-123")
        XCTAssertEqual(pending.status, .queued)
    }

    func testAntifakeCheckFailureHandlerPremium403() {
        let error = NetworkError.forbidden("premium_required: Antifake checks require Premium subscription")
        let presentation = AntifakeCheckFailureHandler.present(
            error: error,
            localizationManager: LocalizationManager()
        )
        XCTAssertTrue(presentation.requiresPremiumUpgrade)
        XCTAssertNotNil(presentation.errorMessage)
    }

    func testAntifakeCheckFailureHandlerVerdictPremiumFlag() {
        let error = SecurityVerdictPremiumRequiredError(message: "Upgrade plan")
        let presentation = AntifakeCheckFailureHandler.present(
            error: error,
            localizationManager: LocalizationManager()
        )
        XCTAssertTrue(presentation.requiresPremiumUpgrade)
        XCTAssertEqual(presentation.errorMessage, "Upgrade plan")
    }

    func testDecodeJobEnqueueCompleted() throws {
        let json = """
        {
          "job_id": "abc-123",
          "status": "completed",
          "verdict": "likely_real",
          "confidence": 0.88,
          "reasons": ["natural voice"],
          "source": "real_agent",
          "premium_required": false
        }
        """
        let result = try SecurityVerdictParsers.decodeJobEnqueueResult(from: Data(json.utf8))
        guard case .completed(let verdict) = result else {
            return XCTFail("expected completed")
        }
        XCTAssertEqual(verdict.verdict, .likelyReal)
    }

    func testDecodeInsufficientDataVerdict() throws {
        let json = """
        {
          "verdict": "insufficient_data",
          "confidence": 0.0,
          "fake_risk": 0.0,
          "reasons": ["text_too_short"],
          "source": "real_agent",
          "agent": "fake_news_detection_agent",
          "premium_required": false
        }
        """
        let verdict = try SecurityVerdictParsers.decodeVerdict(from: Data(json.utf8))
        XCTAssertEqual(verdict.verdict, .insufficientData)
        XCTAssertEqual(verdict.confidence, 0, accuracy: 0.001)
        XCTAssertEqual(verdict.fakeRisk, 0, accuracy: 0.001)
    }
}
