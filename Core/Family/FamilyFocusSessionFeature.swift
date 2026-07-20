import Foundation

/// p2-8 / inf-flags — Focus sessions. Default OFF (notification/focus fatigue risk).
enum FamilyFocusSessionFeature {
    static let flagKey = "feature_focus_session"

    static var isEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: flagKey) == nil {
                return false
            }
            return UserDefaults.standard.bool(forKey: flagKey)
        }
        set { UserDefaults.standard.set(newValue, forKey: flagKey) }
    }
}
