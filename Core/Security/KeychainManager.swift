import Foundation
import Security

/// 🔐 Keychain Manager
/// Безопасное хранение данных в Keychain
/// Используется для токенов, паролей, чувствительных данных
class KeychainManager {
    static let shared = KeychainManager()
    
    private let service = Bundle.main.bundleIdentifier ?? "family.aladdin.ios"
    
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
        // ✅ НОВЫЕ КЛЮЧИ ДЛЯ RECOVERY CODE
        case recoveryCode = "recovery_code"
        case familyId = "family_id"
        case pendingDeviceBindToken = "pending_device_bind_token"
        case pendingMagicAuthToken = "pending_magic_auth_token"
        // E1.4 Family Chat E2EE
        case e2eeDeviceId = "e2ee_device_id"
        case e2eeRegistrationId = "e2ee_registration_id"
        case e2eeIdentityPrivate = "e2ee_identity_private"
    }

    /// Семейный симметричный ключ E2EE (per `family_id`).
    static func e2eeFamilySymmetricKey(familyId: String) -> String {
        "e2ee_family_symmetric_\(familyId)"
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
            // Автоочищаем повреждённые значения, чтобы приложение могло заново авторизоваться
            delete(forKey: key)
            if key == .authToken {
                AppConfig.authToken = nil
                #if DEBUG
                print("⚠️ KeychainManager: Повреждённый auth_token удалён из Keychain и AppConfig")
                #endif
            }
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
        // ✅ BUILD 121: Детальное логирование всех удалений из Keychain
        #if DEBUG
        let stackTrace = Thread.callStackSymbols.prefix(5).joined(separator: "\n")
        let logMessage = """
        🗑️ KeychainManager.delete(forKey: \(key.rawValue))
           - Time: \(Date())
           - Call stack:
        \(stackTrace)
        """
        VisualLogger.shared.log(logMessage, level: .warning, category: "KEYCHAIN")
        MasterLogger.shared.log(.warn, category: .security, message: "🗑️ KeychainManager.delete(forKey: \(key.rawValue))")
        print(logMessage)
        #endif
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key.rawValue
        ]
        
        let status = SecItemDelete(query as CFDictionary)
        
        if status != errSecSuccess && status != errSecItemNotFound {
            let errorMessage = "❌ KeychainManager: Failed to delete data for key \(key.rawValue). Status: \(status)"
            print(errorMessage)
            #if DEBUG
            VisualLogger.shared.log(errorMessage, level: .error, category: "KEYCHAIN")
            MasterLogger.shared.log(.error, category: .security, message: errorMessage)
            #endif
        } else {
            #if DEBUG
            let successMessage = "✅ KeychainManager: Successfully deleted data for key \(key.rawValue)"
            VisualLogger.shared.log(successMessage, level: .success, category: "KEYCHAIN")
            MasterLogger.shared.log(.info, category: .security, message: successMessage)
            #endif
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

    // MARK: - Scoped keys (dynamic account names: per-family E2EE, cipher cache, …)

    func save(_ data: Data, scopedKey: String) {
        saveScoped(data, account: scopedKey)
    }

    func loadData(scopedKey: String) -> Data? {
        loadScopedData(account: scopedKey)
    }

    func delete(scopedKey: String) {
        deleteScoped(account: scopedKey)
    }

    private func saveScoped(_ data: Data, account: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data
        ]
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        if status != errSecSuccess {
            print("❌ KeychainManager: Failed to save scoped key \(account). Status: \(status)")
        }
    }

    private func loadScopedData(account: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        guard status == errSecSuccess, let data = item as? Data else { return nil }
        return data
    }

    private func deleteScoped(account: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        SecItemDelete(query as CFDictionary)
    }
}

#if DEBUG
/// 🛠️ Сервис для автоматического восстановления токенов в Keychain.
/// ВАЖНО: НИКОГДА не должен удалять валидные токены.
enum KeychainAutoRecoveryService {
    
    /// ✅ BUILD 121: Исправлено — аккуратно проверяет токены и удаляет ИСКЛЮЧИТЕЛЬНО повреждённые данные.
    ///
    /// Форматы хранения:
    /// - authToken: raw JWT String (`save(_ string:forKey:)`)
    /// - refreshToken: raw String
    ///
    /// Логика:
    /// 1. Для authToken:
    ///    - пробуем прочитать как raw String через `String(data:encoding:)`
    ///    - (опционально) пробуем декодировать как JWTToken, если когда‑то менялся формат
    ///    - удаляем ТОЛЬКО если не удаётся прочитать ни как строку, ни как JWTToken
    /// 2. Для refreshToken:
    ///    - пробуем прочитать как raw String
    ///    - удаляем ТОЛЬКО если строку прочитать нельзя
    static func repairTokensIfNeeded() {
        let keychain = KeychainManager.shared
        
        // ✅ BUILD 121: Проверяем auth_token (основной JWT)
        if let data = keychain.loadData(forKey: .authToken) {
            // Попытка прочитать как raw String (фактический формат хранения сейчас)
            let rawString = String(data: data, encoding: .utf8)
            
            // Дополнительная защита: если когда‑то authToken сохранялся как JSON JWTToken
            var canDecodeAsJWTToken = false
            if rawString == nil {
                // Если как строку прочитать нельзя — пробуем как JWTToken
                if let jwt = try? JSONDecoder().decode(JWTToken.self, from: data) {
                    canDecodeAsJWTToken = true
                    #if DEBUG
                    print("✅ KeychainAutoRecoveryService: auth_token успешно декодирован как JWTToken (fallback)")
                    print("   - deviceId: \(jwt.deviceId)")
                    print("   - subscriptionLevel: \(jwt.subscriptionLevel)")
                    #endif
                }
            }
            
            let isValidRawString = (rawString != nil)
            let isValidJWTToken  = canDecodeAsJWTToken
            
            if !isValidRawString && !isValidJWTToken {
                // ❌ Данные действительно повреждены — удалить безопасно
                print("⚠️ KeychainAutoRecoveryService: удалён повреждённый auth_token (нельзя прочитать ни как String, ни как JWTToken)")
                keychain.delete(forKey: .authToken)
                // AppConfig.authToken читает из Keychain, поэтому достаточно удалить запись;
                // но для надёжности очищаем и кэш в UserDefaults.
                AppConfig.authToken = nil
            } else {
                #if DEBUG
                let format = isValidRawString ? "raw String" : "JWTToken"
                print("✅ KeychainAutoRecoveryService: auth_token валиден (формат: \(format)) — НЕ удаляем")
                #endif
            }
        }
        
        // ✅ BUILD 121: Проверяем refresh_token (всегда raw String)
        if let data = keychain.loadData(forKey: .refreshToken) {
            let rawString = String(data: data, encoding: .utf8)
            
            if rawString == nil {
                print("⚠️ KeychainAutoRecoveryService: удалён повреждённый refresh_token (нельзя прочитать как String)")
                keychain.delete(forKey: .refreshToken)
            } else {
                #if DEBUG
                print("✅ KeychainAutoRecoveryService: refresh_token валиден — НЕ удаляем")
                #endif
            }
        }
    }
}
#endif

