import XCTest
@testable import ALADDIN

final class FamilyChildThreatCatalogTests: XCTestCase {

    func testChildCatalogHasSeventeenThreats() {
        XCTAssertEqual(FamilyChildThreat.allCases.count, 17)
    }

    func testMonitoringDetailRoutesToFamilyRoot() {
        XCTAssertEqual(FamilyChildThreat.chd01.route, .familyRoot)
    }

    func testGroomingRoutesToAntifakeText() {
        XCTAssertEqual(
            FamilyChildThreat.chd14.route,
            .antifakeTab(.text, textMode: .text)
        )
    }

    func testInappropriateAdsRoutesToNetworkProtection() {
        XCTAssertEqual(FamilyChildThreat.chd12.route, .networkProtection)
    }

    func testCyberbullyingRoutesToParentalControl() {
        XCTAssertEqual(FamilyChildThreat.chd02.route, .parentalControl)
    }
}
