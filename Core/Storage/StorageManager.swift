import Foundation
import SwiftUI

/// Менеджер локального хранилища для ALADDIN
class StorageManager: ObservableObject {
    static let shared = StorageManager()
    
    private let userDefaults = UserDefaults.standard
    private let keychain = KeychainManager()
    
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
    func saveSecureData(_ data: Data, forKey key: String) {
        keychain.save(data, forKey: key)
    }
    
    func getSecureData(forKey key: String) -> Data? {
        return keychain.load(forKey: key)
    }
    
    func deleteSecureData(forKey key: String) {
        keychain.delete(forKey: key)
    }
    
    // MARK: - Cleanup
    func clearAllData() {
        let domain = Bundle.main.bundleIdentifier!
        userDefaults.removePersistentDomain(forName: domain)
        keychain.clearAll()
    }
}

// MARK: - Keychain Manager
private class KeychainManager {
    func save(_ data: Data, forKey key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }
    
    func load(forKey key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        return status == errSecSuccess ? result as? Data : nil
    }
    
    func delete(forKey key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        
        SecItemDelete(query as CFDictionary)
    }
    
    func clearAll() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}
