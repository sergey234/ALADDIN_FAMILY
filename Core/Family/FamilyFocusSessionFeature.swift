import Foundation

/// p2-8 / fsl-09 — Focus sessions. Default ON so teen can start 25 min without hunting a flag.
enum FamilyFocusSessionFeature {
    static let flagKey = "feature_focus_session"

    static var isEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: flagKey) == nil {
                return true
            }
            return UserDefaults.standard.bool(forKey: flagKey)
        }
        set { UserDefaults.standard.set(newValue, forKey: flagKey) }
    }
}
