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

    /// Prod hang build 35 (iOS 16.7): SimpleHome body → todayEvents → unconditional
    /// UserDefaults write → @AppStorage re-render loop → 0x8BADF00D.
    func testGeofenceReads_doNotWriteUserDefaultsWhenNothingToPurge() throws {
        let key = "aladdin_geofence_day_events_v1"
        let defaults = UserDefaults.standard
        let previous = defaults.data(forKey: key)
        defer {
            if let previous { defaults.set(previous, forKey: key) } else { defaults.removeObject(forKey: key) }
        }
        let fresh = GeofenceDayEvent(
            id: "e1",
            time: "10:00",
            action: "arrived",
            isArrival: true,
            regionName: "Home",
            createdAt: Date()
        )
        defaults.set(try JSONEncoder().encode([fresh]), forKey: key)

        var writes = 0
        let token = NotificationCenter.default.addObserver(
            forName: UserDefaults.didChangeNotification,
            object: nil,
            queue: nil
        ) { _ in writes += 1 }
        defer { NotificationCenter.default.removeObserver(token) }

        XCTAssertEqual(GeofenceEventStore.todayEvents().count, 1)
        _ = GeofenceEventStore.events(lastDays: 7)
        _ = WherePhoneTravel.minutesInTransitToday()
        XCTAssertEqual(writes, 0, "Read path must not write UserDefaults (iOS 16 @AppStorage loop)")
    }

    func testGeofencePurge_stillDropsEventsOlderThanRetention() throws {
        let key = "aladdin_geofence_day_events_v1"
        let defaults = UserDefaults.standard
        let previous = defaults.data(forKey: key)
        defer {
            if let previous { defaults.set(previous, forKey: key) } else { defaults.removeObject(forKey: key) }
        }
        let old = GeofenceDayEvent(
            id: "old",
            time: "09:00",
            action: "left",
            isArrival: false,
            regionName: "School",
            createdAt: Date().addingTimeInterval(-10 * 24 * 60 * 60)
        )
        defaults.set(try JSONEncoder().encode([old]), forKey: key)

        XCTAssertTrue(GeofenceEventStore.events(lastDays: 7).isEmpty)
        let stored = try XCTUnwrap(defaults.data(forKey: key))
        XCTAssertTrue(try JSONDecoder().decode([GeofenceDayEvent].self, from: stored).isEmpty)
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
