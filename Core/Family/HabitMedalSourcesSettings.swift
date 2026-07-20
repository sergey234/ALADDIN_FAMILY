import Foundation

/// p2-9f — which sources feed streak medals (default water + medicine ON).
enum HabitMedalSourcesSettings {
    private static let masterKey = "habit_medals_master_enabled"
    private static let prefix = "habit_medal_source_"

    static let builtInSources = [
        "water", "medicine", "phone_down", "wind_down", "breath", "checkin", "focus",
    ]

    static var masterEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: masterKey) == nil { return true }
            return UserDefaults.standard.bool(forKey: masterKey)
        }
        set { UserDefaults.standard.set(newValue, forKey: masterKey) }
    }

    static func isSourceEnabled(_ sourceId: String) -> Bool {
        guard masterEnabled else { return false }
        let key = prefix + sourceId
        if UserDefaults.standard.object(forKey: key) == nil {
            // Custom FamilyChallenge sources default ON once created.
            if sourceId.hasPrefix("challenge:") { return true }
            return sourceId == "water" || sourceId == "medicine"
        }
        return UserDefaults.standard.bool(forKey: key)
    }

    static func challengeSourceId(_ challengeId: String) -> String {
        "challenge:\(challengeId)"
    }

    static func setSourceEnabled(_ sourceId: String, _ on: Bool) {
        UserDefaults.standard.set(on, forKey: prefix + sourceId)
    }
}
