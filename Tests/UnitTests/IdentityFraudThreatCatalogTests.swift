import XCTest
@testable import ALADDIN

final class IdentityFraudThreatCatalogTests: XCTestCase {

    func testCatalogHasTwelveThreats() {
        XCTAssertEqual(IdentityFraudThreat.allCases.count, 12)
    }

    func testThreatIdsAreSequential() {
        let ids = IdentityFraudThreat.allCases.map(\.rawValue)
        XCTAssertEqual(ids.first, "frd-01")
        XCTAssertEqual(ids.last, "frd-12")
    }

    func testEachThreatHasLocalizationKeys() {
        for threat in IdentityFraudThreat.allCases {
            XCTAssertTrue(threat.titleKey.hasPrefix("identity_hub_frd_"))
            XCTAssertTrue(threat.pipelineKey.hasPrefix("identity_hub_frd_"))
            XCTAssertFalse(threat.systemImage.isEmpty)
        }
    }

    func testIdentityTheftRoutesToDetectTab() {
        XCTAssertEqual(IdentityFraudThreat.frd01.route, .identityTab(.detect))
    }

    func testFakeWebsitesRouteToAntifakeUrlMode() {
        XCTAssertEqual(
            IdentityFraudThreat.frd05.route,
            .antifakeTab(.text, textMode: .url)
        )
    }

    func testCallSocialEngineeringRoutesToCallTab() {
        XCTAssertEqual(
            IdentityFraudThreat.frd04.route,
            .antifakeTab(.call, textMode: nil)
        )
    }
}
