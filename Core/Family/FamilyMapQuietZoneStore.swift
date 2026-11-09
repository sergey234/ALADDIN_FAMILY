import CoreLocation
import Foundation

/// Тихая зона: в радиусе у сохранённых мест точку семье не отправляем.
enum FamilyMapQuietZoneStore {
    private static let key = "where_phone_quiet_zone_meters_v1"

    static var meters: Double {
        get {
            let v = UserDefaults.standard.double(forKey: key)
            return v > 0 ? v : 150
        }
        set { UserDefaults.standard.set(newValue, forKey: key) }
    }

    /// True when GPS is within quiet radius of any saved place center.
    @MainActor
    static func contains(_ location: CLLocation) -> Bool {
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
