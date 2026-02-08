import XCTest
@testable import ALADDIN
import CryptoKit

/**
 * 🔒 SecurityManager Integration Tests
 * 
 * Тесты для проверки безопасности:
 * - Шифрование/расшифровка данных
 * - Биометрическая аутентификация
 * - Безопасное хранение данных
 * - Управление ключами
 * 
 * ⚠️ ВАЖНО: Эти тесты работают с реальными системными API (Keychain, LocalAuthentication)
 * ✅ НЕ требуют сервер (локальные тесты)
 */

@MainActor
class SecurityManagerIntegrationTests: XCTestCase {
    
    // MARK: - Properties
    
    var securityManager: SecurityManager!
    
    // MARK: - Test Setup
    
    override func setUp() {
        super.setUp()
        
        // ✅ Используем реальный SecurityManager (не Mock!)
        securityManager = SecurityManager.shared
        
        print("✅ SecurityManagerIntegrationTests: Setup completed")
    }
    
    override func tearDown() {
        // Очищаем тестовые данные
        securityManager.deleteSecureData(forKey: "test_secure_data")
        securityManager.deleteSecureData(forKey: "test_encryption_key")
        
        securityManager = nil
        
        super.tearDown()
        
        print("✅ SecurityManagerIntegrationTests: Teardown completed")
    }
    
    // MARK: - Initialization Tests
    
    /// Тест: Инициализация SecurityManager
    func testInitialization() {
        XCTAssertNotNil(securityManager, "SecurityManager should be initialized")
        XCTAssertNotNil(securityManager.isSecurityEnabled, "isSecurityEnabled should have a value")
        XCTAssertNotNil(securityManager.biometricAuthAvailable, "biometricAuthAvailable should have a value")
        XCTAssertNotNil(securityManager.securityLevel, "securityLevel should have a value")
        
        print("✅ SecurityManager initialized successfully")
    }
    
    // MARK: - Encryption/Decryption Tests
    
    /// Тест: Полный цикл шифрование-расшифровка
    func testEncryptDecrypt_RoundTrip() {
        // Подготовка тестовых данных
        let originalData = "Sensitive test data for encryption".data(using: .utf8)!
        
        // Шаг 1: Шифрование
        guard let encryptedData = securityManager.encryptData(originalData) else {
            XCTFail("Encryption should succeed")
            return
        }
        
        XCTAssertNotNil(encryptedData, "Encrypted data should not be nil")
        XCTAssertNotEqual(originalData, encryptedData, "Encrypted data should be different from original")
        XCTAssertGreaterThan(encryptedData.count, originalData.count, "Encrypted data should be larger (includes nonce and tag)")
        
        print("✅ Encryption successful")
        print("   - Original size: \(originalData.count) bytes")
        print("   - Encrypted size: \(encryptedData.count) bytes")
        
        // Шаг 2: Расшифровка
        guard let decryptedData = securityManager.decryptData(encryptedData) else {
            XCTFail("Decryption should succeed")
            return
        }
        
        XCTAssertNotNil(decryptedData, "Decrypted data should not be nil")
        XCTAssertEqual(originalData, decryptedData, "Decrypted data should match original")
        
        print("✅ Decryption successful")
        print("   - Decrypted size: \(decryptedData.count) bytes")
        print("   - Data matches: \(originalData == decryptedData)")
    }
    
    /// Тест: Шифрование больших данных
    func testEncryptDecrypt_LargeData() {
        // Создаем большие тестовые данные (1 MB)
        let largeData = Data(repeating: 0x42, count: 1_000_000)
        
        guard let encryptedData = securityManager.encryptData(largeData) else {
            XCTFail("Encryption of large data should succeed")
            return
        }
        
        guard let decryptedData = securityManager.decryptData(encryptedData) else {
            XCTFail("Decryption of large data should succeed")
            return
        }
        
        XCTAssertEqual(largeData, decryptedData, "Large data should be encrypted and decrypted correctly")
        
        print("✅ Large data encryption/decryption successful")
        print("   - Original size: \(largeData.count) bytes")
        print("   - Encrypted size: \(encryptedData.count) bytes")
    }
    
    /// Тест: Шифрование пустых данных
    func testEncryptDecrypt_EmptyData() {
        let emptyData = Data()
        
        guard let encryptedData = securityManager.encryptData(emptyData) else {
            XCTFail("Encryption of empty data should succeed")
            return
        }
        
        guard let decryptedData = securityManager.decryptData(encryptedData) else {
            XCTFail("Decryption of empty data should succeed")
            return
        }
        
        XCTAssertEqual(emptyData, decryptedData, "Empty data should be encrypted and decrypted correctly")
        
        print("✅ Empty data encryption/decryption successful")
    }
    
    /// Тест: Множественное шифрование (разные ключи)
    func testEncryptDecrypt_MultipleEncryptions() {
        let testData = "Test data for multiple encryptions".data(using: .utf8)!
        
        // Первое шифрование
        guard let encrypted1 = securityManager.encryptData(testData) else {
            XCTFail("First encryption should succeed")
            return
        }
        
        // Второе шифрование (должно быть другим из-за nonce)
        guard let encrypted2 = securityManager.encryptData(testData) else {
            XCTFail("Second encryption should succeed")
            return
        }
        
        // Зашифрованные данные должны быть разными (из-за случайного nonce)
        XCTAssertNotEqual(encrypted1, encrypted2, "Multiple encryptions should produce different results")
        
        // Но расшифровка должна давать одинаковый результат
        guard let decrypted1 = securityManager.decryptData(encrypted1),
              let decrypted2 = securityManager.decryptData(encrypted2) else {
            XCTFail("Decryption should succeed")
            return
        }
        
        XCTAssertEqual(decrypted1, testData, "First decryption should match original")
        XCTAssertEqual(decrypted2, testData, "Second decryption should match original")
        
        print("✅ Multiple encryptions successful")
    }
    
    // MARK: - Secure Storage Tests
    
    /// Тест: Сохранение и получение безопасных данных
    func testStoreRetrieveSecureData() {
        let testKey = "test_secure_data"
        let testData = "Sensitive data to store securely".data(using: .utf8)!
        
        // Сохранение
        let storeSuccess = securityManager.storeSecureData(testData, forKey: testKey)
        XCTAssertTrue(storeSuccess, "Storing secure data should succeed")
        
        print("✅ Secure data stored successfully")
        
        // Получение
        guard let retrievedData = securityManager.retrieveSecureData(forKey: testKey) else {
            XCTFail("Retrieving secure data should succeed")
            return
        }
        
        XCTAssertEqual(testData, retrievedData, "Retrieved data should match original")
        
        print("✅ Secure data retrieved successfully")
    }
    
    /// Тест: Удаление безопасных данных
    func testDeleteSecureData() {
        let testKey = "test_secure_data"
        let testData = "Data to be deleted".data(using: .utf8)!
        
        // Сохраняем данные
        let storeSuccess = securityManager.storeSecureData(testData, forKey: testKey)
        XCTAssertTrue(storeSuccess, "Storing should succeed")
        
        // Проверяем, что данные есть
        let retrievedBefore = securityManager.retrieveSecureData(forKey: testKey)
        XCTAssertNotNil(retrievedBefore, "Data should exist before deletion")
        
        // Удаляем данные
        securityManager.deleteSecureData(forKey: testKey)
        
        // Проверяем, что данные удалены
        let retrievedAfter = securityManager.retrieveSecureData(forKey: testKey)
        XCTAssertNil(retrievedAfter, "Data should be nil after deletion")
        
        print("✅ Secure data deleted successfully")
    }
    
    /// Тест: Перезапись безопасных данных
    func testOverwriteSecureData() {
        let testKey = "test_secure_data"
        let originalData = "Original data".data(using: .utf8)!
        let newData = "New data".data(using: .utf8)!
        
        // Сохраняем оригинальные данные
        let store1 = securityManager.storeSecureData(originalData, forKey: testKey)
        XCTAssertTrue(store1, "First store should succeed")
        
        // Перезаписываем новыми данными
        let store2 = securityManager.storeSecureData(newData, forKey: testKey)
        XCTAssertTrue(store2, "Second store should succeed")
        
        // Проверяем, что сохранены новые данные
        guard let retrieved = securityManager.retrieveSecureData(forKey: testKey) else {
            XCTFail("Retrieval should succeed")
            return
        }
        
        XCTAssertEqual(newData, retrieved, "Retrieved data should be new data")
        XCTAssertNotEqual(originalData, retrieved, "Retrieved data should not be original data")
        
        print("✅ Secure data overwritten successfully")
    }
    
    // MARK: - Security Level Tests
    
    /// Тест: Изменение уровня безопасности
    func testUpdateSecurityLevel() {
        let initialLevel = securityManager.securityLevel
        
        // Изменяем уровень безопасности
        securityManager.updateSecurityLevel(.high)
        XCTAssertEqual(securityManager.securityLevel, .high, "Security level should be updated to high")
        
        // Возвращаем исходный уровень
        securityManager.updateSecurityLevel(initialLevel)
        XCTAssertEqual(securityManager.securityLevel, initialLevel, "Security level should be restored")
        
        print("✅ Security level updated successfully")
    }
    
    /// Тест: Включение/выключение безопасности
    func testEnableDisableSecurity() {
        let initialState = securityManager.isSecurityEnabled
        
        // Включаем безопасность
        securityManager.enableSecurity()
        XCTAssertTrue(securityManager.isSecurityEnabled, "Security should be enabled")
        
        // Выключаем безопасность
        securityManager.disableSecurity()
        XCTAssertFalse(securityManager.isSecurityEnabled, "Security should be disabled")
        
        // Восстанавливаем исходное состояние
        if initialState {
            securityManager.enableSecurity()
        } else {
            securityManager.disableSecurity()
        }
        
        print("✅ Security enable/disable successful")
    }
    
    // MARK: - Security Validation Tests
    
    /// Тест: Валидация требований безопасности
    func testValidateSecurityRequirements() {
        let result = securityManager.validateSecurityRequirements()
        
        XCTAssertNotNil(result, "Validation result should not be nil")
        XCTAssertNotNil(result.isValid, "isValid should have a value")
        XCTAssertNotNil(result.issues, "issues should have a value")
        
        print("✅ Security validation completed")
        print("   - Is valid: \(result.isValid)")
        print("   - Issues count: \(result.issues.count)")
        if !result.issues.isEmpty {
            print("   - Issues: \(result.issues.joined(separator: ", "))")
        }
    }
    
    // MARK: - Biometric Authentication Tests
    
    /// Тест: Проверка доступности биометрии
    func testBiometricAvailability() {
        let isAvailable = securityManager.biometricAuthAvailable
        
        XCTAssertNotNil(isAvailable, "Biometric availability should be checked")
        
        print("✅ Biometric availability checked")
        print("   - Available: \(isAvailable)")
        
        // Примечание: Фактическая аутентификация требует интерактивного взаимодействия,
        // поэтому мы не тестируем authenticateWithBiometrics() автоматически
        // Это должно быть протестировано вручную или через UI тесты
    }
    
    // MARK: - Performance Tests
    
    /// Тест: Производительность шифрования
    func testEncryptionPerformance() {
        let testData = Data(repeating: 0x42, count: 100_000) // 100 KB
        
        measure {
            guard let encrypted = securityManager.encryptData(testData) else {
                XCTFail("Encryption should succeed")
                return
            }
            
            guard let _ = securityManager.decryptData(encrypted) else {
                XCTFail("Decryption should succeed")
                return
            }
        }
        
        print("✅ Encryption/decryption performance measured")
    }
}
