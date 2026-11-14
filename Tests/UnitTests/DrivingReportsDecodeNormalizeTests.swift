import XCTest
@testable import ALADDIN

/// Contract: GET /api/reports/driving must feed `[DrivingReport]` decoder.
final class DrivingReportsDecodeNormalizeTests: XCTestCase {

    func testRawArrayPassthrough() throws {
        let raw = Data(#"[ {"id":"1"} ]"#.utf8)
        let out = NetworkManager.normalizeDrivingReportsListPayload(
            path: "/api/reports/driving?period=week",
            data: raw
        )
        XCTAssertEqual(out, raw)
    }

    func testBoolStubBecomesEmptyArray() throws {
        let stub = Data(#"{"success":true,"data":true,"message":"Driving reports available"}"#.utf8)
        let out = NetworkManager.normalizeDrivingReportsListPayload(
            path: "/api/reports/driving?userId=MEM_X&period=week",
            data: stub
        )
        XCTAssertEqual(out, Data("[]".utf8))
    }

    func testEnvelopeDataArrayUnwrapped() throws {
        let env = Data(#"{"success":true,"data":[{"id":"t1"}]}"#.utf8)
        let out = NetworkManager.normalizeDrivingReportsListPayload(
            path: "/api/reports/driving",
            data: env
        )
        let json = try XCTUnwrap(out.flatMap { try? JSONSerialization.jsonObject(with: $0) as? [[String: Any]] })
        XCTAssertEqual(json.first?["id"] as? String, "t1")
    }

    func testStatsPathNotNormalized() {
        let stub = Data(#"{"success":true,"data":true}"#.utf8)
        let out = NetworkManager.normalizeDrivingReportsListPayload(
            path: "/api/reports/driving/stats?period=week",
            data: stub
        )
        XCTAssertNil(out)
    }
}
