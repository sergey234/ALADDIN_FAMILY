import Foundation
import Security

/// 🔐 Keychain Manager
/// Безопасное хранение данных в Keychain
/// Используется для токенов, паролей, чувствительных данных
class KeychainManager {
    static let shared = KeychainManager()
    
    private let service = Bundle.main.bundleIdentifier ?? "com.aladdin.ios"
    
    private init() {}
    
    // MARK: - Key Types
    
    enum Key: String, CaseIterable {
        case authToken = "auth_token"
        case refreshToken = "refresh_token"
        case userPassword = "user_password"
        case biometricData = "biometric_data"
        case encryptionKey = "encryption_key"
        case deviceId = "device_id"
        case userPreferences = "user_preferences"
    }
    
    // MARK: - Generic Save/Load
    
    func save<T: Codable>(_ object: T, forKey key: Key) {
        do {
            let data = try JSONEncoder().encode(object)
            save(data, forKey: key)
        } catch {
            print("❌ KeychainManager: Failed to encode object for key \(key.rawValue): \(error)")
        }
    }
    
    func load<T: Codable>(_ type: T.Type, forKey key: Key) -> T? {
        guard let data = loadData(forKey: key) else { return nil }
        
        do {
            return try JSONDecoder().decode(type, from: data)
        } catch {
            print("❌ KeychainManager: Failed to decode object for key \(key.rawValue): \(error)")
            return nil
        }
    }
    
    // MARK: - Data Operations
    
    func save(_ data: Data, forKey key: Key) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key.rawValue,
            kSecValueData as String: data
        ]
        
        // Удаляем существующую запись
        SecItemDelete(query as CFDictionary)
        
        // Добавляем новую запись
        let status = SecItemAdd(query as CFDictionary, nil)
        
        if status != errSecSuccess {
            print("❌ KeychainManager: Failed to save data for key \(key.rawValue). Status: \(status)")
        }
    }
    
    func loadData(forKey key: Key) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key.rawValue,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        if status == errSecSuccess {
            return result as? Data
        } else {
            print("❌ KeychainManager: Failed to load data for key \(key.rawValue). Status: \(status)")
            return nil
        }
    }
    
    func delete(forKey key: Key) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key.rawValue
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        
        if status != errSecSuccess && status != errSecItemNotFound {
            print("❌ KeychainManager: Failed to delete data for key \(key.rawValue). Status: \(status)")
        }
    }
    
    // MARK: - String Operations
    
    func save(_ string: String, forKey key: Key) {
        guard let data = string.data(using: .utf8) else {
            print("❌ KeychainManager: Failed to convert string to data for key \(key.rawValue)")
            return
        }
        save(data, forKey: key)
    }
    
    func loadString(forKey key: Key) -> String? {
        guard let data = loadData(forKey: key) else { return nil }
        return String(data: data, encoding: .utf8)
    }
    
    // MARK: - Cleanup
    
    func clearAll() {
        for key in Key.allCases {
            delete(forKey: key)
        }
    }
    
    func clearUserData() {
        let userKeys: [Key] = [.authToken, .refreshToken, .userPassword, .userPreferences]
        for key in userKeys {
            delete(forKey: key)
        }
    }
    
    // MARK: - Security
    
    func isDataAvailable(forKey key: Key) -> Bool {
        return loadData(forKey: key) != nil
    }
    
    func getDataSize(forKey key: Key) -> Int {
        return loadData(forKey: key)?.count ?? 0
    }
}

