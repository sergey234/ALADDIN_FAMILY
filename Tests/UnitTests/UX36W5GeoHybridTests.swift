import XCTest
@testable import ALADDIN

final class UX36W5GeoHybridTests: XCTestCase {

    func testGeofenceSoftNotifyThrottle_blocksRapidRepeat() {
        let suite = "ux36_w5_geo_\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suite)!
        defer { defaults.removePersistentDomain(forName: suite) }

        let region = "region-home"
        let t0 = Date(timeIntervalSince1970: 1_700_000_000)
        XCTAssertTrue(
            GeofenceFamilyBridge.shouldSoftNotify(
                regionId: region,
                isArrival: true,
                now: t0,
                defaults: defaults
            )
        )
        XCTAssertFalse(
            GeofenceFamilyBridge.shouldSoftNotify(
                regionId: region,
                isArrival: true,
                now: t0.addingTimeInterval(60),
                defaults: defaults
            )
        )
        // Opposite direction is independent.
        XCTAssertTrue(
            GeofenceFamilyBridge.shouldSoftNotify(
                regionId: region,
                isArrival: false,
                now: t0.addingTimeInterval(60),
                defaults: defaults
            )
        )
        // After throttle window — allow again.
        XCTAssertTrue(
            GeofenceFamilyBridge.shouldSoftNotify(
                regionId: region,
                isArrival: true,
                now: t0.addingTimeInterval(31 * 60),
                defaults: defaults
            )
        )
    }

    func testPlacesTerminology_isFamilyPlacesNotCheckpoints() {
        let loc = LocalizationManager.shared
        let title = loc.localized("geofences_title").lowercased()
        XCTAssertFalse(title.contains("контрол"))
        XCTAssertFalse(title.contains("checkpoint"))
        XCTAssertTrue(
            title.contains("мест") || title.contains("place"),
            "Expected places terminology, got: \(title)"
        )
    }
}
