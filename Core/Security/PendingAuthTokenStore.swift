import Foundation

/// P0: одноразовые токены deep link (device bind / magic auth) — только Keychain, не UserDefaults.
enum PendingAuthTokenStore {
    private static let keychain = KeychainManager.shared

    static func saveDeviceBindToken(_ token: String) {
        let trimmed = token.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            clearDeviceBindToken()
            return
        }
        keychain.save(trimmed, forKey: .pendingDeviceBindToken)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.pendingDeviceBindToken)
    }

    static func loadDeviceBindToken() -> String? {
        if let value = keychain.loadString(forKey: .pendingDeviceBindToken) {
            return value
        }
        if let legacy = UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.pendingDeviceBindToken)?
            .trimmingCharacters(in: .whitespacesAndNewlines), !legacy.isEmpty {
            saveDeviceBindToken(legacy)
            return legacy
        }
        return nil
    }

    static func clearDeviceBindToken() {
        keychain.delete(forKey: .pendingDeviceBindToken)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.pendingDeviceBindToken)
    }

    static func saveMagicAuthToken(_ token: String) {
        let trimmed = token.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            clearMagicAuthToken()
            return
        }
        keychain.save(trimmed, forKey: .pendingMagicAuthToken)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.pendingMagicAuthToken)
    }

    static func loadMagicAuthToken() -> String? {
        if let value = keychain.loadString(forKey: .pendingMagicAuthToken) {
            return value
        }
        if let legacy = UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.pendingMagicAuthToken)?
            .trimmingCharacters(in: .whitespacesAndNewlines), !legacy.isEmpty {
            saveMagicAuthToken(legacy)
            return legacy
        }
        return nil
    }

    static func clearMagicAuthToken() {
        keychain.delete(forKey: .pendingMagicAuthToken)
        UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.pendingMagicAuthToken)
    }
}
