import XCTest
@testable import ALADDIN

final class AntifakeTLSRoutingTests: XCTestCase {
    func testProductionBaseURLUsesPinnedHost() {
        XCTAssertTrue(AntifakeTLSRouting.validatesProductionRouting())
    }

    func testAntifakeEndpointsAreRelativePaths() {
        XCTAssertTrue(AntifakeTLSRouting.allEndpointsAreRelativeAntifakePaths())
    }

    @MainActor
    func testNetworkManagerPinsProductionDomain() {
        let manager = NetworkManager()
        XCTAssertTrue(manager.isSSLPinningEnabled)
        XCTAssertTrue(manager.pinnedDomains.contains(AntifakeTLSRouting.pinnedAPIHost))
    }
}
