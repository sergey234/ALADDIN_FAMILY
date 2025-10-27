import Foundation
import SwiftUI

/// Менеджер локального хранилища для ALADDIN
class StorageManager: ObservableObject {
    static let shared = StorageManager()
    
    private let userDefaults = UserDefaults.standard
    // private let keychain = KeychainManager.shared // Временно отключено
    
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

