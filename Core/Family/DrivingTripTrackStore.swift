import CoreLocation
import Foundation

/// GPS track for a trip segment (auto from movement or optional record).
/// Samples are real CLLocations — never invent mid-points. Not an all-day trail at rest.
enum DrivingTripTrackStore {
    private static let activeKey = "driving_trip_track_active_id_v1"
    private static let pointsPrefix = "driving_trip_track_points_v1_"
    private static let maxPoints = 400

    static var activeTripId: String? {
        get {
            let v = UserDefaults.standard.string(forKey: activeKey)?
                .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            return v.isEmpty ? nil : v
        }
        set {
            if let newValue, !newValue.isEmpty {
                UserDefaults.standard.set(newValue, forKey: activeKey)
            } else {
                UserDefaults.standard.removeObject(forKey: activeKey)
            }
        }
    }

    static func begin(tripId: String, start: CLLocationCoordinate2D) {
        activeTripId = tripId
        replace(tripId: tripId, points: [
            DrivingRoutePoint(latitude: start.latitude, longitude: start.longitude)
        ])
    }

    static func append(tripId: String, coordinate: CLLocationCoordinate2D) {
        guard CLLocationCoordinate2DIsValid(coordinate) else { return }
        var pts = load(tripId: tripId)
        if let last = pts.last {
            let d = CLLocation(latitude: last.latitude, longitude: last.longitude)
                .distance(from: CLLocation(latitude: coordinate.latitude, longitude: coordinate.longitude))
            if d < 25 { return }
        }
        pts.append(DrivingRoutePoint(latitude: coordinate.latitude, longitude: coordinate.longitude))
        if pts.count > maxPoints {
            pts = Array(pts.suffix(maxPoints))
        }
        replace(tripId: tripId, points: pts)
    }

    static func finish(tripId: String, end: CLLocationCoordinate2D?) {
        if let end, CLLocationCoordinate2DIsValid(end) {
            append(tripId: tripId, coordinate: end)
        }
        if activeTripId == tripId {
            activeTripId = nil
        }
    }

    static func load(tripId: String) -> [DrivingRoutePoint] {
        guard let data = UserDefaults.standard.data(forKey: pointsPrefix + tripId),
              let pts = try? JSONDecoder().decode([DrivingRoutePoint].self, from: data) else {
            return []
        }
        return pts.filter(\.isValid)
    }

    static func mergeInto(_ report: DrivingReport) -> DrivingReport {
        if report.hasGPSTrack { return report }
        let local = load(tripId: report.id)
        guard local.count >= 2 else { return report }
        return report.withRoutePoints(local)
    }

    private static func replace(tripId: String, points: [DrivingRoutePoint]) {
        if let data = try? JSONEncoder().encode(points) {
            UserDefaults.standard.set(data, forKey: pointsPrefix + tripId)
        }
    }
}
