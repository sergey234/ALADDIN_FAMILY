import Foundation
import Security
import LocalAuthentication
import CryptoKit

/// 🔒 SecurityManager - Менеджер безопасности ALADDIN
/// Обеспечивает защиту данных, аутентификацию и шифрование
@MainActor
class SecurityManager: ObservableObject {
    
    // MARK: - Singleton
    static let shared = SecurityManager()
    
    // MARK: - Published Properties
    @Published var isSecurityEnabled: Bool = false
    @Published var biometricAuthAvailable: Bool = false
    @Published var securityLevel: SecurityLevel = .standard
    
    // MARK: - Private Properties
    private let keychain = Keychain(service: "com.aladdin.security")
    private let biometricContext = LAContext()
    
    // MARK: - Security Levels
    enum SecurityLevel: String, CaseIterable {
        case basic = "basic"
        case standard = "standard"
        case high = "high"
        case maximum = "maximum"
        
        var description: String {
            switch self {
            case .basic: return "Базовая защита"
            case .standard: return "Стандартная защита"
            case .high: return "Высокая защита"
            case .maximum: return "Максимальная защита"
            }
        }
    }
    
    // MARK: - Initialization
    private init() {
        setupSecurity()
    }
    
    // MARK: - Setup
    private func setupSecurity() {
        checkBiometricAvailability()
        loadSecuritySettings()
    }
    
    // MARK: - Biometric Authentication
    private func checkBiometricAvailability() {
        var error: NSError?
        biometricAuthAvailable = biometricContext.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }
    
    func authenticateWithBiometrics() async -> Bool {
        guard biometricAuthAvailable else { return false }
        
        do {
            let result = try await biometricContext.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: "Подтвердите личность для доступа к ALADDIN"
            )
            return result
        } catch {
            print("❌ Biometric authentication failed: \(error.localizedDescription)")
            return false
        }
    }
    
    // MARK: - Data Encryption
    func encryptData(_ data: Data) -> Data? {
        guard let key = getEncryptionKey() else { return nil }
        
        do {
            let sealedBox = try AES.GCM.seal(data, using: key)
            return sealedBox.combined
        } catch {
            print("❌ Encryption failed: \(error.localizedDescription)")
            return nil
        }
    }
    
    func decryptData(_ encryptedData: Data) -> Data? {
        guard let key = getEncryptionKey() else { return nil }
        
        do {
            let sealedBox = try AES.GCM.SealedBox(combined: encryptedData)
            let decryptedData = try AES.GCM.open(sealedBox, using: key)
            return decryptedData
        } catch {
            print("❌ Decryption failed: \(error.localizedDescription)")
            return nil
        }
    }
    
    // MARK: - Key Management
    private func getEncryptionKey() -> SymmetricKey? {
        if let keyData = keychain["encryption_key"] {
            return SymmetricKey(data: keyData)
        } else {
            let newKey = SymmetricKey(size: .bits256)
            keychain["encryption_key"] = newKey.withUnsafeBytes { Data($0) }
            return newKey
        }
    }
    
    // MARK: - Secure Storage
    func storeSecureData(_ data: Data, forKey key: String) -> Bool {
        guard let encryptedData = encryptData(data) else { return false }
        keychain[key] = encryptedData
        return true
    }
    
    func retrieveSecureData(forKey key: String) -> Data? {
        guard let encryptedData = keychain[key] else { return nil }
        return decryptData(encryptedData)
    }
    
    func deleteSecureData(forKey key: String) {
        keychain[key] = nil
    }
    
    // MARK: - Security Settings
    private func loadSecuritySettings() {
        // Загружаем настройки безопасности из UserDefaults
        isSecurityEnabled = UserDefaults.standard.bool(forKey: "security_enabled")
        
        if let levelString = UserDefaults.standard.string(forKey: "security_level"),
           let level = SecurityLevel(rawValue: levelString) {
            securityLevel = level
        }
    }
    
    func updateSecurityLevel(_ level: SecurityLevel) {
        securityLevel = level
        UserDefaults.standard.set(level.rawValue, forKey: "security_level")
    }
    
    func enableSecurity() {
        isSecurityEnabled = true
        UserDefaults.standard.set(true, forKey: "security_enabled")
    }
    
    func disableSecurity() {
        isSecurityEnabled = false
        UserDefaults.standard.set(false, forKey: "security_enabled")
    }
    
    // MARK: - Security Validation
    func validateSecurityRequirements() -> SecurityValidationResult {
        var issues: [String] = []
        
        if !isSecurityEnabled {
            issues.append("Безопасность отключена")
        }
        
        if !biometricAuthAvailable {
            issues.append("Биометрическая аутентификация недоступна")
        }
        
        if securityLevel == .basic {
            issues.append("Используется базовая защита")
        }
        
        return SecurityValidationResult(
            isValid: issues.isEmpty,
            issues: issues,
            securityScore: calculateSecurityScore()
        )
    }
    
    private func calculateSecurityScore() -> Int {
        var score = 0
        
        if isSecurityEnabled { score += 25 }
        if biometricAuthAvailable { score += 25 }
        if securityLevel != .basic { score += 25 }
        if securityLevel == .maximum { score += 25 }
        
        return score
    }
    
    // MARK: - Security Monitoring
    func startSecurityMonitoring() {
        // Запуск мониторинга безопасности
        print("🔒 Security monitoring started")
    }
    
    func stopSecurityMonitoring() {
        // Остановка мониторинга безопасности
        print("🔒 Security monitoring stopped")
    }
}

// MARK: - Security Validation Result
struct SecurityValidationResult {
    let isValid: Bool
    let issues: [String]
    let securityScore: Int
    
    var description: String {
        if isValid {
            return "✅ Безопасность настроена корректно (Оценка: \(securityScore)/100)"
        } else {
            return "❌ Обнаружены проблемы безопасности: \(issues.joined(separator: ", "))"
        }
    }
}

// MARK: - Keychain Helper
private class Keychain {
    private let service: String
    
    init(service: String) {
        self.service = service
    }
    
    subscript(key: String) -> Data? {
        get {
            let query: [String: Any] = [
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrService as String: service,
                kSecAttrAccount as String: key,
                kSecReturnData as String: true
            ]
            
            var result: AnyObject?
            let status = SecItemCopyMatching(query as CFDictionary, &result)
            
            return status == errSecSuccess ? result as? Data : nil
        }
        set {
            if let data = newValue {
                // Добавляем или обновляем
                let query: [String: Any] = [
                    kSecClass as String: kSecClassGenericPassword,
                    kSecAttrService as String: service,
                    kSecAttrAccount as String: key
                ]
                
                let attributes: [String: Any] = [
                    kSecValueData as String: data
                ]
                
                SecItemDelete(query as CFDictionary)
                SecItemAdd(attributes as CFDictionary, nil)
            } else {
                // Удаляем
                let query: [String: Any] = [
                    kSecClass as String: kSecClassGenericPassword,
                    kSecAttrService as String: service,
                    kSecAttrAccount as String: key
                ]
                
                SecItemDelete(query as CFDictionary)
            }
        }
    }
}




