import CoreLocation
import Foundation

/// Тихая зона («шапка-невидимка»): в радиусе у сохранённых мест точку семье не отправляем.
enum FamilyMapQuietZoneStore {
    private static let metersKey = "where_phone_quiet_zone_meters_v1"
    private static let enabledKey = "where_phone_quiet_zone_enabled_v1"

    /// Master switch — user can turn quiet zone off entirely.
    static var isEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: enabledKey) == nil { return true }
            return UserDefaults.standard.bool(forKey: enabledKey)
        }
        set { UserDefaults.standard.set(newValue, forKey: enabledKey) }
    }

    static var meters: Double {
        get {
            let v = UserDefaults.standard.double(forKey: metersKey)
            return v > 0 ? v : 150
        }
        set { UserDefaults.standard.set(newValue, forKey: metersKey) }
    }

    /// True when GPS is within quiet radius of any saved place center.
    @MainActor
    static func contains(_ location: CLLocation) -> Bool {
        guard isEnabled else { return false }
        let radius = meters
        let centers = GeofenceGeocodingService.shared.loadStoredCoordinates().values
        for center in centers {
            let place = CLLocation(latitude: center.latitude, longitude: center.longitude)
            if location.distance(from: place) <= radius {
                return true
            }
        }
        return false
    }

    /// False = do not send / save this point for the family map.
    @MainActor
    static func allowsFamilyShare(_ location: CLLocation) -> Bool {
        !contains(location)
    }
}
