import XCTest
@testable import ALADDIN

final class DeviceEicarScanTests: XCTestCase {

    func testEicarPayloadIsNonEmpty() {
        XCTAssertFalse(DeviceScanSourceValidator.eicarPayload.isEmpty)
    }

    func testEicarPayloadContainsStandardMarker() {
        let text = String(data: DeviceScanSourceValidator.eicarPayload, encoding: .utf8)
        XCTAssertEqual(text, "EICAR-STANDARD-ANTIVIRUS-TEST-FILE")
    }

    func testMockSourceRejectedForDeviceScan() {
        let scan = DeviceAgentScanResult(
            source: "mock",
            agent: "test"
        )
        XCTAssertThrowsError(try scan.validateForProduction()) { error in
            guard case SecurityVerdictValidationError.mockSourceRejected = error else {
                return XCTFail("Expected mockSourceRejected")
            }
        }
    }

    func testRealAgentSourceAcceptedWhenThreatsPresent() {
        let scan = DeviceAgentScanResult(
            threatsFound: 1,
            threats: [DeviceScanThreatItem(id: "eicar-test", name: "EICAR")],
            source: "real_agent",
            agent: "malware_detection_agent"
        )
        XCTAssertNoThrow(try scan.validateForProduction())
        XCTAssertFalse(scan.isClean)
    }
}
