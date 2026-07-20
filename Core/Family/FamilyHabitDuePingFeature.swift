import Foundation

/// p1-7b / inf-flags — Due-ping until Done. Default OFF (risk: notification fatigue).
enum FamilyHabitDuePingFeature {
    static let flagKey = "feature_due_ping"

    /// Client mirror of FEATURE_DUE_PING (default OFF until parent/product enables).
    static var isEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: flagKey) == nil {
                return false
            }
            return UserDefaults.standard.bool(forKey: flagKey)
        }
        set {
            UserDefaults.standard.set(newValue, forKey: flagKey)
        }
    }
}
