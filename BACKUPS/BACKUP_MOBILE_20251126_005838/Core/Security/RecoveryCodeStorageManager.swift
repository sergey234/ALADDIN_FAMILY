import Foundation

/// 🔐 Recovery Code Storage Manager
/// Управление сохранением и восстановлением Recovery Code
class RecoveryCodeStorageManager {
    static let shared = RecoveryCodeStorageManager()
    
    private let keychain = KeychainManager.shared
    
    private init() {}
    
    // MARK: - Save Recovery Code
    
    /// Сохранить Recovery Code и Family ID в Keychain
    /// - Parameters:
    ///   - code: Recovery Code (формат: FAM-A1B2-C3D4-E5F6)
    ///   - familyID: Family ID (формат: FAM_123456)
    /// - Returns: true если сохранение успешно, false если ошибка
    func saveRecoveryCode(_ code: String, familyID: String) -> Bool {
        guard !code.isEmpty, !familyID.isEmpty else {
            print("❌ RecoveryCodeStorageManager: Пустой код или familyID")
            return false
        }
        
        // Сохраняем Recovery Code
        keychain.save(code, forKey: .recoveryCode)
        
        // Сохраняем Family ID
        keychain.save(familyID, forKey: .familyId)
        
        print("✅ RecoveryCodeStorageManager: Код сохранен: \(code)")
        return true
    }
    
    // MARK: - Get Recovery Code
    
    /// Получить сохраненный Recovery Code
    /// - Returns: Recovery Code или nil если не найден
    func getRecoveryCode() -> String? {
        return keychain.loadString(forKey: .recoveryCode)
    }
    
    /// Получить сохраненный Family ID
    /// - Returns: Family ID или nil если не найден
    func getFamilyID() -> String? {
        return keychain.loadString(forKey: .familyId)
    }
    
    // MARK: - Check Availability
    
    /// Проверить, есть ли сохраненный Recovery Code
    /// - Returns: true если код есть, false если нет
    func hasRecoveryCode() -> Bool {
        return getRecoveryCode() != nil && getFamilyID() != nil
    }
    
    // MARK: - Delete Recovery Code
    
    /// Удалить сохраненный Recovery Code и Family ID
    /// - Returns: true если удаление успешно, false если ошибка
    func deleteRecoveryCode() -> Bool {
        keychain.delete(forKey: .recoveryCode)
        keychain.delete(forKey: .familyId)
        
        print("✅ RecoveryCodeStorageManager: Код удален")
        return true
    }
}




