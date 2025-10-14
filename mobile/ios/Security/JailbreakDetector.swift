import Foundation
import UIKit
import Security

class JailbreakDetector {
    static let shared = JailbreakDetector()
    
    private init() {}
    
    // MARK: - Main Detection Method
    
    /// Проверка на jailbreak
    static func isJailbroken() -> Bool {
        return checkJailbreakSigns()
    }
    
    /// Детальная проверка с результатами
    func detectJailbreak() -> JailbreakDetectionResult {
        var detectionMethods: [JailbreakMethod: Bool] = [:]
        var riskLevel: RiskLevel = .low
        
        // 1. Проверка файлов Cydia
        detectionMethods[.cydiaFiles] = checkCydiaFiles()
        
        // 2. Проверка sandbox
        detectionMethods[.sandbox] = checkSandboxViolation()
        
        // 3. Проверка URL schemes
        detectionMethods[.urlSchemes] = checkCydiaURLSchemes()
        
        // 4. Проверка системных вызовов
        detectionMethods[.systemCalls] = checkSystemCalls()
        
        // 5. Проверка приложений
        detectionMethods[.jailbreakApps] = checkJailbreakApps()
        
        // 6. Проверка библиотек
        detectionMethods[.suspiciousLibraries] = checkSuspiciousLibraries()
        
        // 7. Проверка файловой системы
        detectionMethods[.fileSystem] = checkFileSystemAnomalies()
        
        // Определяем уровень риска
        let positiveDetections = detectionMethods.values.filter { $0 }.count
        riskLevel = determineRiskLevel(positiveDetections: positiveDetections)
        
        return JailbreakDetectionResult(
            isJailbroken: positiveDetections > 0,
            riskLevel: riskLevel,
            detectionMethods: detectionMethods,
            timestamp: Date()
        )
    }
    
    // MARK: - Detection Methods
    
    private static func checkJailbreakSigns() -> Bool {
        let detector = JailbreakDetector.shared
        let result = detector.detectJailbreak()
        return result.isJailbroken
    }
    
    // 1. Проверка файлов Cydia
    private func checkCydiaFiles() -> Bool {
        let cydiaPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/var/cache/apt",
            "/var/lib/apt",
            "/var/lib/cydia",
            "/usr/libexec/sftp-server",
            "/usr/bin/ssh",
            "/usr/sbin/sshd",
            "/System/Library/LaunchDaemons/com.ikey.bbot.plist",
            "/Library/MobileSubstrate/DynamicLibraries/Veency.plist",
            "/Library/MobileSubstrate/DynamicLibraries/LiveClock.plist",
            "/private/var/lib/apt/",
            "/private/var/Users/",
            "/var/log/syslog",
            "/usr/libexec/ssh-keysign",
            "/Applications/RockApp.app",
            "/Applications/Icy.app",
            "/usr/bin/cycript",
            "/usr/local/bin/cycript",
            "/usr/lib/libcycript.dylib",
            "/System/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist",
            "/System/Library/LaunchDaemons/com.ikey.bbot.plist",
            "/bin/sh",
            "/etc/ssh/sshd_config",
            "/private/var/tmp/cydia.log",
            "/private/var/lib/dpkg/info/cydia.list"
        ]
        
        for path in cydiaPaths {
            if FileManager.default.fileExists(atPath: path) {
                print("🚨 Jailbreak detected: Found \(path)")
                return true
            }
        }
        
        return false
    }
    
    // 2. Проверка sandbox
    private func checkSandboxViolation() -> Bool {
        // Попытка записи в системные директории
        let restrictedPaths = [
            "/",
            "/root/",
            "/private/",
            "/Applications/"
        ]
        
        for path in restrictedPaths {
            let testFile = "\(path)jailbreak_test_\(UUID().uuidString)"
            do {
                try "test".write(toFile: testFile, atomically: true, encoding: .utf8)
                try FileManager.default.removeItem(atPath: testFile)
                print("🚨 Jailbreak detected: Can write to \(path)")
                return true
            } catch {
                // Ожидаемое поведение - не можем писать в системные директории
                continue
            }
        }
        
        return false
    }
    
    // 3. Проверка URL schemes
    private func checkCydiaURLSchemes() -> Bool {
        let suspiciousSchemes = [
            "cydia://",
            "undecimus://",
            "sileo://",
            "zbra://",
            "filza://",
            "activator://"
        ]
        
        for scheme in suspiciousSchemes {
            if let url = URL(string: scheme) {
                if UIApplication.shared.canOpenURL(url) {
                    print("🚨 Jailbreak detected: Can open \(scheme)")
                    return true
                }
            }
        }
        
        return false
    }
    
    // 4. Проверка системных вызовов
    private func checkSystemCalls() -> Bool {
        // Проверка fork() - в jailbroken устройствах может работать
        let forkResult = fork()
        if forkResult >= 0 {
            if forkResult == 0 {
                // Дочерний процесс
                exit(0)
            } else {
                // Родительский процесс
                print("🚨 Jailbreak detected: fork() succeeded")
                return true
            }
        }
        
        return false
    }
    
    // 5. Проверка приложений
    private func checkJailbreakApps() -> Bool {
        let suspiciousApps = [
            "Cydia",
            "Sileo", 
            "Zebra",
            "Filza",
            "iFile",
            "Activator",
            "WinterBoard",
            "OpenSSH",
            "SSH Toggle",
            "Terminal",
            "MobileTerminal"
        ]
        
        for app in suspiciousApps {
            if canOpenApp(appName: app) {
                print("🚨 Jailbreak detected: Found app \(app)")
                return true
            }
        }
        
        return false
    }
    
    // 6. Проверка библиотек
    private func checkSuspiciousLibraries() -> Bool {
        let suspiciousLibraries = [
            "MobileSubstrate",
            "libsubstrate",
            "libhooker",
            "libsubstitute"
        ]
        
        for library in suspiciousLibraries {
            if dlopen(library, RTLD_NOW) != nil {
                print("🚨 Jailbreak detected: Found library \(library)")
                return true
            }
        }
        
        return false
    }
    
    // 7. Проверка файловой системы
    private func checkFileSystemAnomalies() -> Bool {
        // Проверка на симлинки в неожиданных местах
        let suspiciousPaths = [
            "/etc/fstab",
            "/etc/hosts"
        ]
        
        for path in suspiciousPaths {
            do {
                let attributes = try FileManager.default.attributesOfItem(atPath: path)
                if let type = attributes[.type] as? FileAttributeType,
                   type == .typeSymbolicLink {
                    print("🚨 Jailbreak detected: Symlink at \(path)")
                    return true
                }
            } catch {
                continue
            }
        }
        
        return false
    }
    
    // MARK: - Helper Methods
    
    private func canOpenApp(appName: String) -> Bool {
        let schemes = [
            "cydia://",
            "sileo://",
            "zbra://",
            "filza://",
            "activator://"
        ]
        
        for scheme in schemes {
            if let url = URL(string: scheme) {
                if UIApplication.shared.canOpenURL(url) {
                    return true
                }
            }
        }
        
        return false
    }
    
    private func determineRiskLevel(positiveDetections: Int) -> RiskLevel {
        switch positiveDetections {
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
    
    /// Получить детальный отчет о проверке
    func getDetailedReport() -> String {
        let result = detectJailbreak()
        
        var report = "🔍 Jailbreak Detection Report\n"
        report += "========================\n"
        report += "Status: \(result.isJailbroken ? "🚨 JAILBROKEN" : "✅ CLEAN")\n"
        report += "Risk Level: \(result.riskLevel.rawValue)\n"
        report += "Timestamp: \(result.timestamp)\n\n"
        
        report += "Detection Methods:\n"
        for (method, detected) in result.detectionMethods {
            report += "- \(method.rawValue): \(detected ? "🚨 DETECTED" : "✅ CLEAN")\n"
        }
        
        return report
    }
}

// MARK: - Data Models

struct JailbreakDetectionResult {
    let isJailbroken: Bool
    let riskLevel: RiskLevel
    let detectionMethods: [JailbreakMethod: Bool]
    let timestamp: Date
}

enum RiskLevel: String, CaseIterable {
    case low = "Low"
    case medium = "Medium"
    case high = "High"
    case critical = "Critical"
}

enum JailbreakMethod: String, CaseIterable {
    case cydiaFiles = "Cydia Files"
    case sandbox = "Sandbox Violation"
    case urlSchemes = "URL Schemes"
    case systemCalls = "System Calls"
    case jailbreakApps = "Jailbreak Apps"
    case suspiciousLibraries = "Suspicious Libraries"
    case fileSystem = "File System Anomalies"
}

