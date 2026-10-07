import Foundation

/// geo-04 — явное согласие: уведомления о местах, не слежка по карте.
enum GeofencePlacesConsentStore {
    private static let key = "aladdin_geofence_places_consent_v1"

    static var hasAccepted: Bool {
        UserDefaults.standard.bool(forKey: key)
    }

    static func accept() {
        UserDefaults.standard.set(true, forKey: key)
    }

    static func revokeForTesting() {
        UserDefaults.standard.removeObject(forKey: key)
    }
}
