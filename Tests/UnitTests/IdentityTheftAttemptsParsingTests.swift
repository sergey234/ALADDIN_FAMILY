import XCTest
@testable import ALADDIN

final class IdentityTheftAttemptsParsingTests: XCTestCase {

    func testDecodeAttemptsEnvelope() throws {
        let json = """
        {
          "attempts": [
            {
              "id": "abc-123",
              "dataType": "snils",
              "requestSource": "detect",
              "timestamp": "2026-06-10T12:00:00.000Z",
              "action": "suspicious",
              "severity": "high",
              "details": {"request_source": "detect", "matches": "1"}
            }
          ],
          "total": 1,
          "source": "real_agent"
        }
        """
        let envelope = try JSONDecoder.componentReportsDecoder.decode(
            IdentityTheftAttemptsEnvelope.self,
            from: Data(json.utf8)
        )
        XCTAssertEqual(envelope.attempts.count, 1)
        XCTAssertEqual(envelope.attempts.first?.requestSource, "detect")
        XCTAssertEqual(envelope.attempts.first?.action, .suspicious)
        XCTAssertFalse(IdentityTheftResponseGuard.rejectsMock(source: envelope.source))
    }

    func testRejectMockAttemptsSource() {
        XCTAssertTrue(IdentityTheftResponseGuard.rejectsMock(source: "sfm_mock"))
        XCTAssertFalse(IdentityTheftResponseGuard.rejectsMock(source: "real_agent"))
    }

    func testDecodeAttemptDetailsString() throws {
        let json = """
        {
          "id": "x1",
          "dataType": "passport",
          "requestSource": "api",
          "timestamp": "2026-06-10T12:00:00.000Z",
          "action": "blocked",
          "severity": "medium",
          "details": "manual review"
        }
        """
        let attempt = try JSONDecoder.componentReportsDecoder.decode(
            IdentityTheftAttempt.self,
            from: Data(json.utf8)
        )
        XCTAssertEqual(attempt.details, "manual review")
    }
}
