import XCTest
@testable import ALADDIN

final class DeviceThreatCatalogTests: XCTestCase {

    func testCyberCatalogHasTenThreats() {
        XCTAssertEqual(DeviceCyberThreat.allCases.count, 10)
    }

    func testMobileCatalogHasTenThreats() {
        XCTAssertEqual(DeviceMobileThreat.allCases.count, 10)
    }

    func testIoTCatalogHasTenThreats() {
        XCTAssertEqual(DeviceIoTThreat.allCases.count, 10)
    }

    func testVirusRoutesToCyberTab() {
        XCTAssertEqual(DeviceCyberThreat.cyb01.route, .deviceTab(.cyber))
    }

    func testBackdoorRoutesToComponentsTab() {
        XCTAssertEqual(DeviceCyberThreat.cyb08.route, .deviceTab(.components))
    }

    func testSmishingRoutesToAntifakeText() {
        XCTAssertEqual(
            DeviceMobileThreat.mob04.route,
            .antifakeTab(.text, textMode: .text)
        )
    }

    func testIoTRoutesToIoTTab() {
        XCTAssertEqual(DeviceIoTThreat.iot03.route, .deviceTab(.iot))
    }
}
