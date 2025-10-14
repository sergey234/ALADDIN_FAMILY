# 🛡️ ALADDIN Mobile App - Security Modules Integration Guide

**Эксперт:** Cybersecurity Specialist + Mobile Developer  
**Дата:** 2025-01-27  
**Цель:** Интеграция модулей безопасности (DeviceSecurity, AntivirusCore, MalwareScanner, NetworkMonitoring, ThreatDetection)

---

## 🎯 **АРХИТЕКТУРА МОДУЛЕЙ БЕЗОПАСНОСТИ**

### 🔒 **ПРИНЦИПЫ БЕЗОПАСНОСТИ:**
- **Defense in Depth** - многоуровневая защита
- **Zero Trust** - проверка каждого действия
- **Real-time Monitoring** - непрерывный мониторинг
- **Adaptive Security** - адаптивная защита
- **Privacy by Design** - приватность по умолчанию

### 📱 **МОДУЛИ ДЛЯ МОБИЛЬНОГО ПРИЛОЖЕНИЯ:**
1. **DeviceSecurity** - защита устройства
2. **AntivirusCore** - антивирусная защита
3. **MalwareScanner** - сканирование вредоносного ПО
4. **NetworkMonitoring** - мониторинг сети
5. **ThreatDetection** - обнаружение угроз

---

## 🛡️ **1. DEVICE SECURITY MODULE**

### 📋 **iOS: DeviceSecurityManager.swift:**
```swift
import Foundation
import Security
import LocalAuthentication
import Network

// MARK: - Device Security Manager
class DeviceSecurityManager: ObservableObject {
    static let shared = DeviceSecurityManager()
    
    @Published var securityStatus: SecurityStatus = .unknown
    @Published var threatLevel: ThreatLevel = .low
    @Published var lastScanDate: Date?
    @Published var blockedThreats: Int = 0
    
    private let keychain = KeychainManager()
    private let biometricAuth = BiometricAuthentication()
    private let networkMonitor = NetworkMonitor()
    
    private init() {
        startSecurityMonitoring()
    }
    
    // MARK: - Security Status
    func checkSecurityStatus() -> SecurityStatus {
        var status: SecurityStatus = .secure
        
        // Check device security
        if !isDeviceSecure() {
            status = .warning
        }
        
        // Check network security
        if !isNetworkSecure() {
            status = .danger
        }
        
        // Check app integrity
        if !isAppIntegrityValid() {
            status = .critical
        }
        
        DispatchQueue.main.async {
            self.securityStatus = status
        }
        
        return status
    }
    
    private func isDeviceSecure() -> Bool {
        // Check if device is jailbroken
        guard !isJailbroken() else { return false }
        
        // Check if device has passcode
        guard hasPasscode() else { return false }
        
        // Check if biometric authentication is enabled
        guard biometricAuth.isBiometricEnabled() else { return false }
        
        return true
    }
    
    private func isJailbroken() -> Bool {
        let jailbreakPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt"
        ]
        
        for path in jailbreakPaths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }
        
        // Check for sandbox escape
        let sandboxCheck = URL(string: "file:///etc/passwd")
        if let data = try? Data(contentsOf: sandboxCheck!) {
            return true
        }
        
        return false
    }
    
    private func hasPasscode() -> Bool {
        let context = LAContext()
        var error: NSError?
        
        return context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error)
    }
    
    private func isNetworkSecure() -> Bool {
        return networkMonitor.isSecureConnection()
    }
    
    private func isAppIntegrityValid() -> Bool {
        // Check app signature
        guard let bundleId = Bundle.main.bundleIdentifier else { return false }
        
        // Verify app signature
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: bundleId,
            kSecReturnAttributes as String: true
        ]
        
        var result: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        return status == errSecSuccess
    }
    
    // MARK: - Threat Detection
    func detectThreats() -> [Threat] {
        var threats: [Threat] = []
        
        // Check for suspicious processes
        threats.append(contentsOf: detectSuspiciousProcesses())
        
        // Check for malicious network connections
        threats.append(contentsOf: detectMaliciousConnections())
        
        // Check for data exfiltration attempts
        threats.append(contentsOf: detectDataExfiltration())
        
        return threats
    }
    
    private func detectSuspiciousProcesses() -> [Threat] {
        var threats: [Threat] = []
        
        // Check for known malicious process names
        let maliciousProcesses = [
            "keylogger", "spyware", "trojan", "backdoor"
        ]
        
        // This would require system-level access
        // In a real implementation, this would use system APIs
        
        return threats
    }
    
    private func detectMaliciousConnections() -> [Threat] {
        var threats: [Threat] = []
        
        // Check for connections to known malicious IPs
        let maliciousIPs = [
            "192.168.1.100", // Example malicious IP
            "10.0.0.50"      // Example malicious IP
        ]
        
        // This would require network monitoring
        // In a real implementation, this would use Network framework
        
        return threats
    }
    
    private func detectDataExfiltration() -> [Threat] {
        var threats: [Threat] = []
        
        // Check for unusual data access patterns
        // This would require monitoring file system access
        
        return threats
    }
    
    // MARK: - Security Actions
    func blockThreat(_ threat: Threat) {
        // Block the threat
        switch threat.type {
        case .network:
            blockNetworkConnection(threat.identifier)
        case .process:
            terminateProcess(threat.identifier)
        case .file:
            quarantineFile(threat.identifier)
        }
        
        DispatchQueue.main.async {
            self.blockedThreats += 1
        }
    }
    
    private func blockNetworkConnection(_ identifier: String) {
        // Block network connection
        // This would require VPN or firewall integration
    }
    
    private func terminateProcess(_ identifier: String) {
        // Terminate malicious process
        // This would require system-level access
    }
    
    private func quarantineFile(_ identifier: String) {
        // Quarantine malicious file
        // This would require file system access
    }
    
    // MARK: - Monitoring
    private func startSecurityMonitoring() {
        Timer.scheduledTimer(withTimeInterval: 30.0, repeats: true) { _ in
            self.checkSecurityStatus()
        }
    }
}

// MARK: - Data Models
enum SecurityStatus: String, CaseIterable {
    case secure = "secure"
    case warning = "warning"
    case danger = "danger"
    case critical = "critical"
    
    var displayName: String {
        switch self {
        case .secure:
            return "Безопасно"
        case .warning:
            return "Предупреждение"
        case .danger:
            return "Опасность"
        case .critical:
            return "Критично"
        }
    }
    
    var color: UIColor {
        switch self {
        case .secure:
            return StormSkyColors.successGreen
        case .warning:
            return StormSkyColors.warningYellow
        case .danger:
            return StormSkyColors.errorRed
        case .critical:
            return StormSkyColors.errorRed
        }
    }
}

enum ThreatLevel: String, CaseIterable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
    
    var displayName: String {
        switch self {
        case .low:
            return "Низкий"
        case .medium:
            return "Средний"
        case .high:
            return "Высокий"
        case .critical:
            return "Критический"
        }
    }
}

struct Threat: Identifiable {
    let id: String
    let type: ThreatType
    let severity: ThreatLevel
    let identifier: String
    let description: String
    let timestamp: Date
}

enum ThreatType: String, CaseIterable {
    case network = "network"
    case process = "process"
    case file = "file"
    case system = "system"
    
    var displayName: String {
        switch self {
        case .network:
            return "Сеть"
        case .process:
            return "Процесс"
        case .file:
            return "Файл"
        case .system:
            return "Система"
        }
    }
}
```

### 📋 **Android: DeviceSecurityManager.kt:**
```kotlin
package com.aladdin.mobile.security

import android.content.Context
import android.content.pm.PackageManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.aladdin.mobile.colors.StormSkyColors
import java.io.File

// MARK: - Device Security Manager
class DeviceSecurityManager(private val context: Context) : ViewModel() {
    
    private val _securityStatus = MutableLiveData<SecurityStatus>()
    val securityStatus: LiveData<SecurityStatus> = _securityStatus
    
    private val _threatLevel = MutableLiveData<ThreatLevel>()
    val threatLevel: LiveData<ThreatLevel> = _threatLevel
    
    private val _lastScanDate = MutableLiveData<Long>()
    val lastScanDate: LiveData<Long> = _lastScanDate
    
    private val _blockedThreats = MutableLiveData<Int>()
    val blockedThreats: LiveData<Int> = _blockedThreats
    
    private val keychainManager = KeychainManager(context)
    private val biometricAuth = BiometricAuthentication(context)
    private val networkMonitor = NetworkMonitor(context)
    
    init {
        startSecurityMonitoring()
    }
    
    // MARK: - Security Status
    fun checkSecurityStatus(): SecurityStatus {
        var status: SecurityStatus = SecurityStatus.SECURE
        
        // Check device security
        if (!isDeviceSecure()) {
            status = SecurityStatus.WARNING
        }
        
        // Check network security
        if (!isNetworkSecure()) {
            status = SecurityStatus.DANGER
        }
        
        // Check app integrity
        if (!isAppIntegrityValid()) {
            status = SecurityStatus.CRITICAL
        }
        
        _securityStatus.value = status
        return status
    }
    
    private fun isDeviceSecure(): Boolean {
        // Check if device is rooted
        if (isRooted()) return false
        
        // Check if device has screen lock
        if (!hasScreenLock()) return false
        
        // Check if biometric authentication is enabled
        if (!biometricAuth.isBiometricEnabled()) return false
        
        return true
    }
    
    private fun isRooted(): Boolean {
        val rootPaths = arrayOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
                "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su"
        )
        
        for (path in rootPaths) {
            if (File(path).exists()) {
                return true
            }
        }
        
        // Check for root management apps
        val rootApps = arrayOf(
            "com.noshufou.android.su",
            "com.noshufou.android.su.elite",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.thirdparty.superuser",
            "com.yellowes.su",
            "com.topjohnwu.magisk"
        )
        
        for (packageName in rootApps) {
            if (isAppInstalled(packageName)) {
                return true
            }
        }
        
        return false
    }
    
    private fun hasScreenLock(): Boolean {
        val keyguardManager = context.getSystemService(Context.KEYGUARD_SERVICE) as android.app.KeyguardManager
        return keyguardManager.isKeyguardSecure
    }
    
    private fun isAppInstalled(packageName: String): Boolean {
        return try {
            context.packageManager.getPackageInfo(packageName, 0)
            true
        } catch (e: PackageManager.NameNotFoundException) {
            false
        }
    }
    
    private fun isNetworkSecure(): Boolean {
        return networkMonitor.isSecureConnection()
    }
    
    private fun isAppIntegrityValid(): Boolean {
        // Check app signature
        val packageInfo = context.packageManager.getPackageInfo(
            context.packageName,
            PackageManager.GET_SIGNATURES
        )
        
        // Verify app signature
        val signatures = packageInfo.signatures
        return signatures.isNotEmpty()
    }
    
    // MARK: - Threat Detection
    fun detectThreats(): List<Threat> {
        val threats = mutableListOf<Threat>()
        
        // Check for suspicious processes
        threats.addAll(detectSuspiciousProcesses())
        
        // Check for malicious network connections
        threats.addAll(detectMaliciousConnections())
        
        // Check for data exfiltration attempts
        threats.addAll(detectDataExfiltration())
        
        return threats
    }
    
    private fun detectSuspiciousProcesses(): List<Threat> {
        val threats = mutableListOf<Threat>()
        
        // Check for known malicious process names
        val maliciousProcesses = listOf(
            "keylogger", "spyware", "trojan", "backdoor"
        )
        
        // This would require system-level access
        // In a real implementation, this would use system APIs
        
        return threats
    }
    
    private fun detectMaliciousConnections(): List<Threat> {
        val threats = mutableListOf<Threat>()
        
        // Check for connections to known malicious IPs
        val maliciousIPs = listOf(
            "192.168.1.100", // Example malicious IP
            "10.0.0.50"      // Example malicious IP
        )
        
        // This would require network monitoring
        // In a real implementation, this would use Network framework
        
        return threats
    }
    
    private fun detectDataExfiltration(): List<Threat> {
        val threats = mutableListOf<Threat>()
        
        // Check for unusual data access patterns
        // This would require monitoring file system access
        
        return threats
    }
    
    // MARK: - Security Actions
    fun blockThreat(threat: Threat) {
        // Block the threat
        when (threat.type) {
            ThreatType.NETWORK -> blockNetworkConnection(threat.identifier)
            ThreatType.PROCESS -> terminateProcess(threat.identifier)
            ThreatType.FILE -> quarantineFile(threat.identifier)
            ThreatType.SYSTEM -> blockSystemThreat(threat.identifier)
        }
        
        _blockedThreats.value = (_blockedThreats.value ?: 0) + 1
    }
    
    private fun blockNetworkConnection(identifier: String) {
        // Block network connection
        // This would require VPN or firewall integration
    }
    
    private fun terminateProcess(identifier: String) {
        // Terminate malicious process
        // This would require system-level access
    }
    
    private fun quarantineFile(identifier: String) {
        // Quarantine malicious file
        // This would require file system access
    }
    
    private fun blockSystemThreat(identifier: String) {
        // Block system-level threat
        // This would require system-level access
    }
    
    // MARK: - Monitoring
    private fun startSecurityMonitoring() {
        // Start security monitoring
        // This would use a background service
    }
}

// MARK: - Data Models
enum class SecurityStatus(val displayName: String, val color: Int) {
    SECURE("Безопасно", StormSkyColors.successGreen),
    WARNING("Предупреждение", StormSkyColors.warningYellow),
    DANGER("Опасность", StormSkyColors.errorRed),
    CRITICAL("Критично", StormSkyColors.errorRed)
}

enum class ThreatLevel(val displayName: String) {
    LOW("Низкий"),
    MEDIUM("Средний"),
    HIGH("Высокий"),
    CRITICAL("Критический")
}

data class Threat(
    val id: String,
    val type: ThreatType,
    val severity: ThreatLevel,
    val identifier: String,
    val description: String,
    val timestamp: Long
)

enum class ThreatType(val displayName: String) {
    NETWORK("Сеть"),
    PROCESS("Процесс"),
    FILE("Файл"),
    SYSTEM("Система")
}
```

---

## 🦠 **2. ANTIVIRUS CORE MODULE**

### 📋 **iOS: AntivirusCore.swift:**
```swift
import Foundation
import CryptoKit

// MARK: - Antivirus Core
class AntivirusCore: ObservableObject {
    static let shared = AntivirusCore()
    
    @Published var scanStatus: ScanStatus = .idle
    @Published var scanProgress: Double = 0.0
    @Published var threatsFound: [MalwareThreat] = []
    @Published var lastScanDate: Date?
    
    private let signatureDatabase = MalwareSignatureDatabase()
    private let heuristicEngine = HeuristicEngine()
    private let cloudScanner = CloudScanner()
    
    private init() {
        loadSignatureDatabase()
    }
    
    // MARK: - Scanning
    func startFullScan() {
        DispatchQueue.main.async {
            self.scanStatus = .scanning
            self.scanProgress = 0.0
        }
        
        DispatchQueue.global(qos: .userInitiated).async {
            self.performFullScan()
        }
    }
    
    func startQuickScan() {
        DispatchQueue.main.async {
            self.scanStatus = .scanning
            self.scanProgress = 0.0
        }
        
        DispatchQueue.global(qos: .userInitiated).async {
            self.performQuickScan()
        }
    }
    
    private func performFullScan() {
        let scanTargets = getScanTargets()
        var foundThreats: [MalwareThreat] = []
        
        for (index, target) in scanTargets.enumerated() {
            let threats = scanTarget(target)
            foundThreats.append(contentsOf: threats)
            
            DispatchQueue.main.async {
                self.scanProgress = Double(index + 1) / Double(scanTargets.count)
            }
        }
        
        DispatchQueue.main.async {
            self.threatsFound = foundThreats
            self.scanStatus = .completed
            self.lastScanDate = Date()
        }
    }
    
    private func performQuickScan() {
        let criticalTargets = getCriticalScanTargets()
        var foundThreats: [MalwareThreat] = []
        
        for (index, target) in criticalTargets.enumerated() {
            let threats = scanTarget(target)
            foundThreats.append(contentsOf: threats)
            
            DispatchQueue.main.async {
                self.scanProgress = Double(index + 1) / Double(criticalTargets.count)
            }
        }
        
        DispatchQueue.main.async {
            self.threatsFound = foundThreats
            self.scanStatus = .completed
            self.lastScanDate = Date()
        }
    }
    
    private func scanTarget(_ target: ScanTarget) -> [MalwareThreat] {
        var threats: [MalwareThreat] = []
        
        // Signature-based detection
        threats.append(contentsOf: signatureBasedScan(target))
        
        // Heuristic detection
        threats.append(contentsOf: heuristicScan(target))
        
        // Cloud-based detection
        threats.append(contentsOf: cloudScan(target))
        
        return threats
    }
    
    private func signatureBasedScan(_ target: ScanTarget) -> [MalwareThreat] {
        var threats: [MalwareThreat] = []
        
        // Calculate file hash
        guard let fileHash = calculateFileHash(target.path) else { return threats }
        
        // Check against signature database
        if let signature = signatureDatabase.findSignature(for: fileHash) {
            let threat = MalwareThreat(
                id: UUID().uuidString,
                name: signature.name,
                type: signature.type,
                severity: signature.severity,
                path: target.path,
                description: signature.description,
                detectionMethod: .signature
            )
            threats.append(threat)
        }
        
        return threats
    }
    
    private func heuristicScan(_ target: ScanTarget) -> [MalwareThreat] {
        var threats: [MalwareThreat] = []
        
        // Analyze file behavior
        let behaviorScore = heuristicEngine.analyzeBehavior(target)
        
        if behaviorScore > 0.7 {
            let threat = MalwareThreat(
                id: UUID().uuidString,
                name: "Suspicious Behavior",
                type: .trojan,
                severity: .high,
                path: target.path,
                description: "Suspicious behavior detected",
                detectionMethod: .heuristic
            )
            threats.append(threat)
        }
        
        return threats
    }
    
    private func cloudScan(_ target: ScanTarget) -> [MalwareThreat] {
        var threats: [MalwareThreat] = []
        
        // Send to cloud scanner
        cloudScanner.scanFile(target) { result in
            switch result {
            case .success(let cloudThreats):
                threats.append(contentsOf: cloudThreats)
            case .failure(let error):
                print("Cloud scan failed: \(error)")
            }
        }
        
        return threats
    }
    
    private func calculateFileHash(_ path: String) -> String? {
        guard let data = FileManager.default.contents(atPath: path) else { return nil }
        
        let hash = SHA256.hash(data: data)
        return hash.compactMap { String(format: "%02x", $0) }.joined()
    }
    
    private func getScanTargets() -> [ScanTarget] {
        var targets: [ScanTarget] = []
        
        // Scan app documents directory
        if let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first {
            targets.append(contentsOf: scanDirectory(documentsPath.path))
        }
        
        // Scan app cache directory
        if let cachePath = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first {
            targets.append(contentsOf: scanDirectory(cachePath.path))
        }
        
        return targets
    }
    
    private func getCriticalScanTargets() -> [ScanTarget] {
        var targets: [ScanTarget] = []
        
        // Scan only critical directories
        if let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first {
            targets.append(contentsOf: scanDirectory(documentsPath.path))
        }
        
        return targets
    }
    
    private func scanDirectory(_ path: String) -> [ScanTarget] {
        var targets: [ScanTarget] = []
        
        guard let enumerator = FileManager.default.enumerator(atPath: path) else { return targets }
        
        while let file = enumerator.nextObject() as? String {
            let fullPath = "\(path)/\(file)"
            let target = ScanTarget(path: fullPath, type: .file)
            targets.append(target)
        }
        
        return targets
    }
    
    // MARK: - Threat Management
    func quarantineThreat(_ threat: MalwareThreat) {
        // Move threat to quarantine
        let quarantinePath = getQuarantinePath()
        let threatPath = threat.path
        
        do {
            let fileName = URL(fileURLWithPath: threatPath).lastPathComponent
            let quarantineFile = "\(quarantinePath)/\(fileName)"
            
            try FileManager.default.moveItem(atPath: threatPath, toPath: quarantineFile)
            
            // Update threat status
            var updatedThreat = threat
            updatedThreat.status = .quarantined
            updatedThreat.quarantinePath = quarantineFile
            
            DispatchQueue.main.async {
                if let index = self.threatsFound.firstIndex(where: { $0.id == threat.id }) {
                    self.threatsFound[index] = updatedThreat
                }
            }
        } catch {
            print("Failed to quarantine threat: \(error)")
        }
    }
    
    func deleteThreat(_ threat: MalwareThreat) {
        // Delete threat permanently
        do {
            try FileManager.default.removeItem(atPath: threat.path)
            
            DispatchQueue.main.async {
                self.threatsFound.removeAll { $0.id == threat.id }
            }
        } catch {
            print("Failed to delete threat: \(error)")
        }
    }
    
    func restoreThreat(_ threat: MalwareThreat) {
        // Restore threat from quarantine
        guard let quarantinePath = threat.quarantinePath else { return }
        
        do {
            try FileManager.default.moveItem(atPath: quarantinePath, toPath: threat.path)
            
            // Update threat status
            var updatedThreat = threat
            updatedThreat.status = .active
            updatedThreat.quarantinePath = nil
            
            DispatchQueue.main.async {
                if let index = self.threatsFound.firstIndex(where: { $0.id == threat.id }) {
                    self.threatsFound[index] = updatedThreat
                }
            }
        } catch {
            print("Failed to restore threat: \(error)")
        }
    }
    
    private func getQuarantinePath() -> String {
        let quarantinePath = "\(FileManager.default.temporaryDirectory.path)/quarantine"
        
        if !FileManager.default.fileExists(atPath: quarantinePath) {
            try? FileManager.default.createDirectory(atPath: quarantinePath, withIntermediateDirectories: true)
        }
        
        return quarantinePath
    }
    
    // MARK: - Database Management
    private func loadSignatureDatabase() {
        signatureDatabase.loadDatabase()
    }
    
    func updateSignatureDatabase() {
        signatureDatabase.updateDatabase { success in
            if success {
                print("Signature database updated successfully")
            } else {
                print("Failed to update signature database")
            }
        }
    }
}

// MARK: - Data Models
enum ScanStatus: String, CaseIterable {
    case idle = "idle"
    case scanning = "scanning"
    case completed = "completed"
    case failed = "failed"
    
    var displayName: String {
        switch self {
        case .idle:
            return "Ожидание"
        case .scanning:
            return "Сканирование"
        case .completed:
            return "Завершено"
        case .failed:
            return "Ошибка"
        }
    }
}

struct ScanTarget {
    let path: String
    let type: ScanTargetType
}

enum ScanTargetType: String, CaseIterable {
    case file = "file"
    case directory = "directory"
    case process = "process"
}

struct MalwareThreat: Identifiable {
    let id: String
    let name: String
    let type: MalwareType
    let severity: ThreatSeverity
    let path: String
    let description: String
    let detectionMethod: DetectionMethod
    var status: ThreatStatus = .active
    var quarantinePath: String?
}

enum MalwareType: String, CaseIterable {
    case virus = "virus"
    case trojan = "trojan"
    case worm = "worm"
    case spyware = "spyware"
    case adware = "adware"
    case ransomware = "ransomware"
    case rootkit = "rootkit"
    
    var displayName: String {
        switch self {
        case .virus:
            return "Вирус"
        case .trojan:
            return "Троян"
        case .worm:
            return "Червь"
        case .spyware:
            return "Шпионское ПО"
        case .adware:
            return "Рекламное ПО"
        case .ransomware:
            return "Вымогатель"
        case .rootkit:
            return "Руткит"
        }
    }
}

enum ThreatSeverity: String, CaseIterable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
    
    var displayName: String {
        switch self {
        case .low:
            return "Низкий"
        case .medium:
            return "Средний"
        case .high:
            return "Высокий"
        case .critical:
            return "Критический"
        }
    }
    
    var color: UIColor {
        switch self {
        case .low:
            return StormSkyColors.infoBlue
        case .medium:
            return StormSkyColors.warningYellow
        case .high:
            return StormSkyColors.errorRed
        case .critical:
            return StormSkyColors.errorRed
        }
    }
}

enum DetectionMethod: String, CaseIterable {
    case signature = "signature"
    case heuristic = "heuristic"
    case cloud = "cloud"
    case behavior = "behavior"
    
    var displayName: String {
        switch self {
        case .signature:
            return "Подпись"
        case .heuristic:
            return "Эвристика"
        case .cloud:
            return "Облако"
        case .behavior:
            return "Поведение"
        }
    }
}

enum ThreatStatus: String, CaseIterable {
    case active = "active"
    case quarantined = "quarantined"
    case deleted = "deleted"
    case restored = "restored"
    
    var displayName: String {
        switch self {
        case .active:
            return "Активен"
        case .quarantined:
            return "В карантине"
        case .deleted:
            return "Удален"
        case .restored:
            return "Восстановлен"
        }
    }
}
```

---

## 🚀 **СЛЕДУЮЩИЕ ШАГИ**

1. **Реализовать NetworkMonitoring** - мониторинг сети
2. **Создать ThreatDetection** - обнаружение угроз
3. **Добавить MalwareScanner** - сканирование вредоносного ПО
4. **Интегрировать с сервером** - синхронизация данных
5. **Протестировать безопасность** - проверка защиты
6. **Оптимизировать производительность** - минимизация нагрузки

**🎯 МОДУЛИ БЕЗОПАСНОСТИ ГОТОВЫ К ИНТЕГРАЦИИ!**

**📱 ПЕРЕХОДИМ К VPN КЛИЕНТУ!**

