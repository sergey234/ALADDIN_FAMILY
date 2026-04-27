import Foundation
import SwiftUI

/// Менеджер локального хранилища для ALADDIN
class StorageManager: ObservableObject {
    static let shared = StorageManager()
    
    private let userDefaults = UserDefaults.standard
    private let keychain = KeychainManager.shared
    
    // MARK: - User Defaults Keys
    private enum Keys {
        static let isFirstLaunch = "isFirstLaunch"
        static let userPreferences = "userPreferences"
        static let appSettings = "appSettings"
        static let lastSyncDate = "lastSyncDate"
    }
    
    private init() {}
    
    // MARK: - First Launch
    var isFirstLaunch: Bool {
        get { userDefaults.bool(forKey: Keys.isFirstLaunch) }
        set { userDefaults.set(newValue, forKey: Keys.isFirstLaunch) }
    }
    
    // MARK: - User Preferences
    func saveUserPreferences(_ preferences: [String: Any]) {
        userDefaults.set(preferences, forKey: Keys.userPreferences)
    }
    
    func getUserPreferences() -> [String: Any] {
        return userDefaults.dictionary(forKey: Keys.userPreferences) ?? [:]
    }
    
    // MARK: - App Settings
    func saveAppSettings(_ settings: [String: Any]) {
        userDefaults.set(settings, forKey: Keys.appSettings)
    }
    
    func getAppSettings() -> [String: Any] {
        return userDefaults.dictionary(forKey: Keys.appSettings) ?? [:]
    }
    
    // MARK: - Secure Storage (Keychain)
    func saveSecureData(_ data: Data, forKey key: KeychainManager.Key) {
        keychain.save(data, forKey: key)
    }
    
    func getSecureData(forKey key: KeychainManager.Key) -> Data? {
        return keychain.loadData(forKey: key)
    }
    
    func deleteSecureData(forKey key: KeychainManager.Key) {
        keychain.delete(forKey: key)
    }
    
    func saveSecureString(_ string: String, forKey key: KeychainManager.Key) {
        keychain.save(string, forKey: key)
    }
    
    func getSecureString(forKey key: KeychainManager.Key) -> String? {
        return keychain.loadString(forKey: key)
    }
    
    // MARK: - Cleanup
    func clearAllData() {
        let domain = Bundle.main.bundleIdentifier!
        userDefaults.removePersistentDomain(forName: domain)
        keychain.clearAll()
    }
}

enum UnicornRewardsStore {
    private static let legacyBalanceKey = "child_unicorn_balance"
    private static let legacyWeeklyEarnedKey = "child_weekly_earned"
    private static let legacyWeeklyPunishedKey = "child_weekly_punished"
    private static let defaultBalance = 100

    static func resolveActiveChildId(from defaults: UserDefaults = .standard) -> String? {
        let candidates = [
            defaults.string(forKey: "parental_selected_child_id"),
            defaults.string(forKey: "active_child_profile_server_id"),
            defaults.string(forKey: "your_member_id"),
            defaults.string(forKey: "user_id")
        ]
        for candidate in candidates {
            let trimmed = candidate?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            if !trimmed.isEmpty { return trimmed }
        }
        return nil
    }

    static func readBalance(for childId: String?, defaults: UserDefaults = .standard) -> Int {
        guard let childId = sanitized(childId) else { return defaults.integer(forKey: legacyBalanceKey) }
        let key = scopedKey(base: legacyBalanceKey, childId: childId)
        if defaults.object(forKey: key) != nil {
            return max(defaults.integer(forKey: key), 0)
        }
        return defaultBalance
    }

    static func writeBalance(_ value: Int, for childId: String?, defaults: UserDefaults = .standard) {
        let safeValue = max(value, 0)
        if let childId = sanitized(childId) {
            defaults.set(safeValue, forKey: scopedKey(base: legacyBalanceKey, childId: childId))
        }
        defaults.set(safeValue, forKey: legacyBalanceKey)
    }

    static func readWeeklyEarned(for childId: String?, defaults: UserDefaults = .standard) -> Int {
        readScopedInt(base: legacyWeeklyEarnedKey, childId: childId, defaults: defaults)
    }

    static func writeWeeklyEarned(_ value: Int, for childId: String?, defaults: UserDefaults = .standard) {
        writeScopedInt(base: legacyWeeklyEarnedKey, value: value, childId: childId, defaults: defaults)
    }

    static func readWeeklyPunished(for childId: String?, defaults: UserDefaults = .standard) -> Int {
        readScopedInt(base: legacyWeeklyPunishedKey, childId: childId, defaults: defaults)
    }

    static func writeWeeklyPunished(_ value: Int, for childId: String?, defaults: UserDefaults = .standard) {
        writeScopedInt(base: legacyWeeklyPunishedKey, value: value, childId: childId, defaults: defaults)
    }

    private static func readScopedInt(base: String, childId: String?, defaults: UserDefaults) -> Int {
        guard let childId = sanitized(childId) else { return defaults.integer(forKey: base) }
        let key = scopedKey(base: base, childId: childId)
        if defaults.object(forKey: key) != nil {
            return max(defaults.integer(forKey: key), 0)
        }
        return 0
    }

    private static func writeScopedInt(base: String, value: Int, childId: String?, defaults: UserDefaults) {
        let safeValue = max(value, 0)
        if let childId = sanitized(childId) {
            defaults.set(safeValue, forKey: scopedKey(base: base, childId: childId))
        }
        defaults.set(safeValue, forKey: base)
    }

    private static func scopedKey(base: String, childId: String) -> String {
        "\(base)_\(childId)"
    }

    private static func sanitized(_ value: String?) -> String? {
        let trimmed = value?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return trimmed.isEmpty ? nil : trimmed
    }
}
