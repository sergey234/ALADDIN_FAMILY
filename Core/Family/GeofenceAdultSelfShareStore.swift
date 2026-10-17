import Foundation

/// WAVE3 L16-adult (A3) — opt-in «Мои места для семьи» on this device.
/// Missing key = enabled (backward compatible / child phones after P1).
enum GeofenceAdultSelfShareStore {
    private static let key = "aladdin_geofence_adult_self_share_v1"

    static var isEnabled: Bool {
        if UserDefaults.standard.object(forKey: key) == nil { return true }
        return UserDefaults.standard.bool(forKey: key)
    }

    static func setEnabled(_ on: Bool) {
        UserDefaults.standard.set(on, forKey: key)
    }
}
