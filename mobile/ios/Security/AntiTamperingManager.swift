import Foundation
import Security
import CommonCrypto

class AntiTamperingManager {
    static let shared = AntiTamperingManager()
    
    private let expectedChecksums: [String: String]
    private let criticalFunctions: [String]
    private var validationResults: [String: Bool] = [:]
    
    private init() {
        self.expectedChecksums = AntiTamperingManager.loadExpectedChecksums()
        self.criticalFunctions = [
            "performSecurityChecks",
            "validateUserInput",
            "encryptSensitiveData",
            "decryptSensitiveData",
            "validateCertificate",
            "authenticateUser"
        ]
    }
    
    // MARK: - Main Validation Methods
    
    /// Проверка целостности приложения
    func validateAppIntegrity() -> TamperingDetectionResult {
        var detectionMethods: [TamperingCheck: Bool] = [:]
        var riskLevel: TamperingRiskLevel = .low
        
        // 1. Проверка подписи приложения
        detectionMethods[.appSignature] = validateAppSignature()
        
        // 2. Проверка целостности критических функций
        detectionMethods[.criticalFunctions] = validateCriticalFunctions()
        
        // 3. Проверка целостности ресурсов
        detectionMethods[.resources] = validateResources()
        
        // 4. Проверка целостности бинарного файла
        detectionMethods[.binaryIntegrity] = validateBinaryIntegrity()
        
        // 5. Проверка контрольных сумм
        detectionMethods[.checksums] = validateChecksums()
        
        // 6. Проверка динамической библиотеки
        detectionMethods[.dynamicLibraries] = validateDynamicLibraries()
        
        // 7. Проверка конфигурации
        detectionMethods[.configuration] = validateConfiguration()
        
        // Определяем уровень риска
        let violations = detectionMethods.values.filter { !$0 }.count
        riskLevel = determineTamperingRiskLevel(violations: violations)
        
        let isTampered = violations > 0
        
        return TamperingDetectionResult(
            isTampered: isTampered,
            riskLevel: riskLevel,
            detectionMethods: detectionMethods,
            timestamp: Date()
        )
    }
    
    // MARK: - Validation Methods
    
    // 1. Проверка подписи приложения
    private func validateAppSignature() -> Bool {
        guard let bundlePath = Bundle.main.bundlePath.cString(using: .utf8) else {
            print("❌ Anti-Tampering: Failed to get bundle path")
            return false
        }
        
        var staticCode: SecStaticCode?
        let status = SecStaticCodeCreateWithPath(
            URL(fileURLWithPath: Bundle.main.bundlePath) as CFURL,
            [],
            &staticCode
        )
        
        guard status == errSecSuccess, let code = staticCode else {
            print("❌ Anti-Tampering: Failed to create static code")
            return false
        }
        
        let validationResult = SecStaticCodeCheckValidity(code, [], nil)
        let isValid = validationResult == errSecSuccess
        
        if !isValid {
            print("🚨 Anti-Tampering: App signature validation failed")
        } else {
            print("✅ Anti-Tampering: App signature valid")
        }
        
        return isValid
    }
    
    // 2. Проверка целостности критических функций
    private func validateCriticalFunctions() -> Bool {
        var allValid = true
        
        for functionName in criticalFunctions {
            if let symbol = dlsym(dlopen(nil, RTLD_NOW), functionName) {
                // Проверяем, что функция не была изменена
                let checksum = calculateChecksum(for: symbol)
                
                if let expectedChecksum = expectedChecksums[functionName] {
                    if checksum != expectedChecksum {
                        print("🚨 Anti-Tampering: Function \(functionName) modified")
                        allValid = false
                    } else {
                        print("✅ Anti-Tampering: Function \(functionName) intact")
                    }
                }
            } else {
                print("⚠️ Anti-Tampering: Function \(functionName) not found")
            }
        }
        
        return allValid
    }
    
    // 3. Проверка целостности ресурсов
    private func validateResources() -> Bool {
        let criticalResources = [
            "Info.plist",
            "Base.lproj",
            "Assets.car"
        ]
        
        var allValid = true
        
        for resource in criticalResources {
            if let resourcePath = Bundle.main.path(forResource: resource, ofType: nil) {
                let checksum = calculateFileChecksum(path: resourcePath)
                
                if let expectedChecksum = expectedChecksums[resource] {
                    if checksum != expectedChecksum {
                        print("🚨 Anti-Tampering: Resource \(resource) modified")
                        allValid = false
                    } else {
                        print("✅ Anti-Tampering: Resource \(resource) intact")
                    }
                }
            } else {
                print("⚠️ Anti-Tampering: Resource \(resource) not found")
            }
        }
        
        return allValid
    }
    
    // 4. Проверка целостности бинарного файла
    private func validateBinaryIntegrity() -> Bool {
        guard let executablePath = Bundle.main.executablePath else {
            print("❌ Anti-Tampering: Failed to get executable path")
            return false
        }
        
        let checksum = calculateFileChecksum(path: executablePath)
        
        if let expectedChecksum = expectedChecksums["executable"] {
            let isValid = checksum == expectedChecksum
            
            if !isValid {
                print("🚨 Anti-Tampering: Executable modified")
            } else {
                print("✅ Anti-Tampering: Executable intact")
            }
            
            return isValid
        }
        
        return true
    }
    
    // 5. Проверка контрольных сумм
    private func validateChecksums() -> Bool {
        var allValid = true
        
        for (file, expectedChecksum) in expectedChecksums {
            if let filePath = Bundle.main.path(forResource: file, ofType: nil) {
                let actualChecksum = calculateFileChecksum(path: filePath)
                
                if actualChecksum != expectedChecksum {
                    print("🚨 Anti-Tampering: Checksum mismatch for \(file)")
                    allValid = false
                } else {
                    print("✅ Anti-Tampering: Checksum valid for \(file)")
                }
            }
        }
        
        return allValid
    }
    
    // 6. Проверка динамических библиотек
    private func validateDynamicLibraries() -> Bool {
        let suspiciousLibraries = [
            "MobileSubstrate",
            "libsubstrate",
            "libhooker",
            "libsubstitute"
        ]
        
        for library in suspiciousLibraries {
            if dlopen(library, RTLD_NOW) != nil {
                print("🚨 Anti-Tampering: Suspicious library detected: \(library)")
                return false
            }
        }
        
        print("✅ Anti-Tampering: No suspicious libraries")
        return true
    }
    
    // 7. Проверка конфигурации
    private func validateConfiguration() -> Bool {
        guard let infoDictionary = Bundle.main.infoDictionary else {
            print("❌ Anti-Tampering: Failed to get info dictionary")
            return false
        }
        
        // Проверяем критические ключи конфигурации
        let criticalKeys = [
            "CFBundleIdentifier",
            "CFBundleVersion",
            "CFBundleShortVersionString"
        ]
        
        for key in criticalKeys {
            if infoDictionary[key] == nil {
                print("🚨 Anti-Tampering: Missing configuration key: \(key)")
                return false
            }
        }
        
        print("✅ Anti-Tampering: Configuration valid")
        return true
    }
    
    // MARK: - Helper Methods
    
    private static func loadExpectedChecksums() -> [String: String] {
        // В реальном приложении эти значения были бы зашифрованы и обфусцированы
        return [
            "executable": "abc123def456",
            "Info.plist": "def456ghi789",
            "Base.lproj": "ghi789jkl012",
            "performSecurityChecks": "jkl012mno345",
            "validateUserInput": "mno345pqr678"
        ]
    }
    
    private func calculateChecksum(for symbol: UnsafeRawPointer) -> String {
        // Упрощенная версия - в реальном приложении здесь был бы SHA-256
        let address = Int(bitPattern: symbol)
        return String(format: "%016x", address)
    }
    
    private func calculateFileChecksum(path: String) -> String {
        guard let data = FileManager.default.contents(atPath: path) else {
            return ""
        }
        
        var hash = [UInt8](repeating: 0, count: Int(CC_SHA256_DIGEST_LENGTH))
        data.withUnsafeBytes {
            _ = CC_SHA256($0.baseAddress, CC_LONG(data.count), &hash)
        }
        
        return hash.map { String(format: "%02x", $0) }.joined()
    }
    
    private func determineTamperingRiskLevel(violations: Int) -> TamperingRiskLevel {
        switch violations {
        case 0:
            return .low
        case 1...2:
            return .medium
        case 3...4:
            return .high
        default:
            return .critical
        }
    }
    
    // MARK: - Public Methods
    
    /// Получить детальный отчет
    func getDetailedReport() -> String {
        let result = validateAppIntegrity()
        
        var report = "🔒 Anti-Tampering Report\n"
        report += "========================\n"
        report += "Status: \(result.isTampered ? "🚨 TAMPERED" : "✅ INTACT")\n"
        report += "Risk Level: \(result.riskLevel.rawValue)\n"
        report += "Timestamp: \(result.timestamp)\n\n"
        
        report += "Validation Checks:\n"
        for (check, isValid) in result.detectionMethods {
            report += "- \(check.rawValue): \(isValid ? "✅ VALID" : "🚨 INVALID")\n"
        }
        
        return report
    }
    
    /// Быстрая проверка целостности
    func quickIntegrityCheck() -> Bool {
        let result = validateAppIntegrity()
        return !result.isTampered
    }
}

// MARK: - Data Models

struct TamperingDetectionResult {
    let isTampered: Bool
    let riskLevel: TamperingRiskLevel
    let detectionMethods: [TamperingCheck: Bool]
    let timestamp: Date
}

enum TamperingRiskLevel: String, CaseIterable {
    case low = "Low"
    case medium = "Medium"
    case high = "High"
    case critical = "Critical"
}

enum TamperingCheck: String, CaseIterable {
    case appSignature = "App Signature"
    case criticalFunctions = "Critical Functions"
    case resources = "Resources"
    case binaryIntegrity = "Binary Integrity"
    case checksums = "Checksums"
    case dynamicLibraries = "Dynamic Libraries"
    case configuration = "Configuration"
}

