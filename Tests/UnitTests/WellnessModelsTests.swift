import XCTest
@testable import ALADDIN

final class WellnessModelsTests: XCTestCase {
    func testDecodePillarsResponse() throws {
        let json = """
        {"pillars":["humanistic","behavioral"],"age_band":"child"}
        """
        let resp = try JSONDecoder().decode(WellnessPillarsResponse.self, from: Data(json.utf8))
        XCTAssertEqual(resp.ageBand, "child")
        XCTAssertEqual(Set(resp.pillars), ["humanistic", "behavioral"])
    }

    func testChildAllowedPillars() {
        let allowed = WellnessPillar.allowed(for: "child")
        XCTAssertEqual(allowed.map(\.rawValue), ["humanistic", "behavioral"])
    }

    func testDecodeOutcomePostResponse() throws {
        let json = """
        {"ok":true,"outcome":{"id":1,"pillar":"humanistic","helpful":5,"created_at":"2026-06-01T00:00:00"}}
        """
        let resp = try JSONDecoder().decode(WellnessOutcomePostResponse.self, from: Data(json.utf8))
        XCTAssertTrue(resp.ok)
        XCTAssertEqual(resp.outcome?.helpful, 5)
        XCTAssertEqual(resp.outcome?.pillar, "humanistic")
    }
}
