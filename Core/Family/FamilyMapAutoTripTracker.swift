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

    private static var movingHits = 0
    private static var stopHits = 0
    private static var lastSample: CLLocation?

    static func note(location: CLLocation) {
        guard location.horizontalAccuracy >= 0, location.horizontalAccuracy < 80 else { return }
        guard FamilyMapQuietZoneStore.allowsFamilyShare(location) else {
            // In quiet zone: pause sampling, keep trip open until leave + stop.
            return
        }

        let speedKmh: Double
        if location.speed >= 0 {
            speedKmh = location.speed * 3.6
        } else if let last = lastSample {
            let dt = location.timestamp.timeIntervalSince(last.timestamp)
            guard dt > 0.5 else { return }
            speedKmh = (location.distance(from: last) / dt) * 3.6
        } else {
            lastSample = location
            return
        }

        if speedKmh >= movingSpeedKmh {
            movingHits += 1
            stopHits = 0
            if DrivingTripTrackStore.activeTripId == nil, movingHits >= movingHitsToStart {
                let tripId = "auto_\(Int(Date().timeIntervalSince1970))"
                DrivingTripTrackStore.begin(tripId: tripId, start: location.coordinate)
            } else if let tripId = DrivingTripTrackStore.activeTripId {
                maybeAppend(tripId: tripId, location: location)
            }
        } else if speedKmh <= stopSpeedKmh {
            stopHits += 1
            movingHits = 0
            if let tripId = DrivingTripTrackStore.activeTripId, stopHits >= stopHitsToEnd {
                DrivingTripTrackStore.finish(tripId: tripId, end: location.coordinate)
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

    private static func maybeAppend(tripId: String, location: CLLocation) {
        if let last = lastSample, location.distance(from: last) < minSampleGapMeters {
            return
        }
        DrivingTripTrackStore.append(tripId: tripId, coordinate: location.coordinate)
    }
}
