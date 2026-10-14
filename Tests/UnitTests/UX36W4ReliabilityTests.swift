import XCTest
@testable import ALADDIN

/// UX-36 W4 — human soft-fail for companion / crash / no raw HTTP in UI.
final class UX36W4ReliabilityTests: XCTestCase {

    func testCompanionErrorMapper_maps504ToHumanMessage() {
        let loc = LocalizationManager.shared
        let mapped = CompanionErrorMapper.message(
            for: NetworkError.httpError(504),
            localizationManager: loc
        )
        XCTAssertEqual(mapped, loc.localized("companion_error_hero_unavailable"))
        XCTAssertFalse(mapped.lowercased().contains("504"))
        XCTAssertFalse(mapped.lowercased().contains("http"))
    }

    func testCompanionErrorMapper_mapsTimeoutToHumanMessage() {
        let loc = LocalizationManager.shared
        let mapped = CompanionErrorMapper.message(
            for: NetworkError.timeout,
            localizationManager: loc
        )
        XCTAssertEqual(mapped, loc.localized("companion_error_hero_unavailable"))
    }

    func testCrashDetectionError_locationOffersSettings() {
        let presentation = CrashDetectionError.locationUnavailable.reliabilityPresentation
        XCTAssertTrue(presentation.offerOpenSettings)
        XCTAssertFalse(presentation.message.lowercased().contains("http"))
    }

    func testCrashDetectionError_accelerometerNoSettings() {
        let presentation = CrashDetectionError.accelerometerUnavailable.reliabilityPresentation
        XCTAssertFalse(presentation.offerOpenSettings)
    }
}
