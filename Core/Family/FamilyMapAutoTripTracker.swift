import CoreLocation
import Foundation

/// Auto trip segment from real movement (no mandatory Start button).
/// Starts when speed stays high; ends when speed stays low. Not an all-day trail at rest.
@MainActor
enum FamilyMapAutoTripTracker {
    private static let movingSpeedKmh: Double = 18
    private static let stopSpeedKmh: Double = 6
    private static let movingHitsToStart = 2
    private static let stopHitsToEnd = 4
    private static let minSampleGapMeters: CLLocationDistance = 40
    /// P0.4 RCA: SLC/cell fixes are often ±100–500 m; still reject ±kilometre coarse.
    private static let maxSampleAccuracyMeters: CLLocationAccuracy = 150
    /// iOS pauses updates on parking → no «slow» fixes ever arrive; close the trip at its last real fix.
    static let staleTripGapSeconds: TimeInterval = 10 * 60

    private static var movingHits = 0
    private static var stopHits = 0
    private static var lastSample: CLLocation?

    static func note(location: CLLocation) {
        let auth = LocationManager.shared.authorizationStatus
        closeStaleTripIfNeeded(now: location.timestamp)
        if location.horizontalAccuracy < 0 || location.horizontalAccuracy > maxSampleAccuracyMeters {
            print(
                "TRIP_AUTO drop accuracy=±\(Int(location.horizontalAccuracy))m " +
                "auth=\(auth.rawValue) active=\(DrivingTripTrackStore.activeTripId ?? "nil")"
            )
            return
        }
        guard FamilyMapQuietZoneStore.allowsFamilyShare(location) else {
            // In quiet zone: no samples. Parked inside (home) → end the trip at its last point outside.
            if DrivingTripTrackStore.activeTripId == nil,
               location.speed >= 0, location.speed * 3.6 <= stopSpeedKmh {
                LocationManager.shared.armTripDepartureIfNeeded(at: location)
            }
            if let tripId = DrivingTripTrackStore.activeTripId,
               location.speed >= 0, location.speed * 3.6 <= stopSpeedKmh {
                stopHits += 1
                movingHits = 0
                if stopHits >= 2 {
                    print("TRIP_AUTO finalize id=\(tripId) reason=quiet_zone_parked")
                    finalize(tripId: tripId)
                }
            }
            print("TRIP_AUTO quiet-zone pause active=\(DrivingTripTrackStore.activeTripId ?? "nil")")
            return
        }

        // GPS often reports speed=0/-1 while moving (SLC / cell). Prefer instrumented speed when
        // valid; otherwise derive from displacement. Cap teleports (SLC jumps) so they never
        // open a fake trip.
        let speedKmh: Double
        if location.speed >= 0, location.speed * 3.6 >= 1 {
            speedKmh = location.speed * 3.6
        } else if let last = lastSample {
            let dt = location.timestamp.timeIntervalSince(last.timestamp)
            guard dt > 0.8 else { return }
            let derived = (location.distance(from: last) / dt) * 3.6
            if derived > 160 {
                print("TRIP_AUTO drop teleport speed=\(Int(derived)) dt=\(Int(dt))s")
                lastSample = location
                return
            }
            speedKmh = derived
        } else {
            lastSample = location
            return
        }

        if speedKmh >= movingSpeedKmh {
            movingHits += 1
            stopHits = 0
            if DrivingTripTrackStore.activeTripId == nil, movingHits >= movingHitsToStart {
                let tripId = "auto_\(Int(Date().timeIntervalSince1970))"
                let member = FamilyDrivingTripLedger.currentDeviceMember()
                DrivingTripTrackStore.begin(tripId: tripId, location: location)
                FamilyDrivingTripLedger.beginMeta(
                    tripId: tripId,
                    memberId: member.id,
                    memberName: member.name
                )
                LocationManager.shared.boostAccuracyForActiveTrip()
                print(
                    "TRIP_AUTO start id=\(tripId) member=\(member.id)/\(member.name) " +
                    "speed=\(Int(speedKmh)) auth=\(auth.rawValue)"
                )
            } else if let tripId = DrivingTripTrackStore.activeTripId {
                // App relaunched mid-trip (region/SLC wake) → GPS mode is not on yet.
                LocationManager.shared.ensureTripTracking()
                maybeAppend(tripId: tripId, location: location)
            }
        } else if speedKmh <= stopSpeedKmh {
            stopHits += 1
            movingHits = 0
            if DrivingTripTrackStore.activeTripId == nil {
                LocationManager.shared.armTripDepartureIfNeeded(at: location)
            }
            if let tripId = DrivingTripTrackStore.activeTripId, stopHits >= stopHitsToEnd {
                print("TRIP_AUTO finalize id=\(tripId) speed=\(Int(speedKmh)) hits=\(stopHits)")
                DrivingTripTrackStore.append(tripId: tripId, location: location)
                finalize(tripId: tripId)
            }
        } else {
            movingHits = 0
            stopHits = 0
            if let tripId = DrivingTripTrackStore.activeTripId {
                maybeAppend(tripId: tripId, location: location)
            }
        }

        lastSample = location
    }

    private static func finalize(tripId: String) {
        let parked = DrivingTripTrackStore.load(tripId: tripId).last.map {
            CLLocation(latitude: $0.latitude, longitude: $0.longitude)
        }
        _ = FamilyDrivingTripLedger.finalizeActiveTrip(tripId: tripId, end: nil)
        LocationManager.shared.endTripTracking(parkedAt: parked)
        movingHits = 0
        stopHits = 0
    }

    private static func closeStaleTripIfNeeded(now: Date) {
        guard let tripId = DrivingTripTrackStore.activeTripId,
              let lastFix = DrivingTripTrackStore.load(tripId: tripId).last?.t,
              now.timeIntervalSince(lastFix) > staleTripGapSeconds else { return }
        print("TRIP_AUTO finalize id=\(tripId) reason=stale gap=\(Int(now.timeIntervalSince(lastFix)))s")
        finalize(tripId: tripId)
        lastSample = nil
    }

    private static func maybeAppend(tripId: String, location: CLLocation) {
        if let last = lastSample, location.distance(from: last) < minSampleGapMeters {
            return
        }
        DrivingTripTrackStore.append(tripId: tripId, location: location)
        let n = DrivingTripTrackStore.load(tripId: tripId).count
        if n == 2 || n % 10 == 0 {
            print("TRIP_AUTO append id=\(tripId) points=\(n)")
        }
    }
}
