# 🌐 ALADDIN Mobile App - API Integration Guide

**Эксперт:** Backend Developer + Mobile Developer  
**Дата:** 2025-01-27  
**Цель:** Настройка API интеграции с сервером ALADDIN для мобильных приложений

---

## 🎯 **ОБЩАЯ АРХИТЕКТУРА API**

### 📡 **СЕРВЕРНАЯ ЧАСТЬ ALADDIN:**
- **Base URL:** `https://api.aladdin-security.com/v1`
- **Протокол:** HTTPS с TLS 1.3
- **Аутентификация:** JWT + Biometric
- **Шифрование:** AES-256 для данных, RSA-4096 для ключей

### 📱 **МОБИЛЬНЫЕ КЛИЕНТЫ:**
- **iOS:** Swift + URLSession + Combine
- **Android:** Kotlin + Retrofit + Coroutines
- **Общий формат:** JSON с единой структурой

---

## 🍎 **iOS API ИНТЕГРАЦИЯ**

### 📋 **1. APIClient.swift:**
```swift
import Foundation
import Combine

// MARK: - API Client
class APIClient {
    static let shared = APIClient()
    
    private let baseURL = "https://api.aladdin-security.com/v1"
    private let session: URLSession
    private let jsonDecoder: JSONDecoder
    
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
        
        self.jsonDecoder = JSONDecoder()
        self.jsonDecoder.dateDecodingStrategy = .iso8601
    }
    
    // MARK: - Generic Request Method
    func request<T: Codable>(
        endpoint: APIEndpoint,
        responseType: T.Type
    ) -> AnyPublisher<T, APIError> {
        guard let url = buildURL(for: endpoint) else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        
        if let body = endpoint.body {
            request.httpBody = try? JSONEncoder().encode(body)
        }
        
        return session.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: T.self, decoder: jsonDecoder)
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError(error)
                } else {
                    return APIError.networkError(error)
                }
            }
            .eraseToAnyPublisher()
    }
    
    private func buildURL(for endpoint: APIEndpoint) -> URL? {
        var components = URLComponents(string: baseURL)
        components?.path = endpoint.path
        components?.queryItems = endpoint.queryItems
        return components?.url
    }
    
    private func getAuthToken() -> String {
        // Get JWT token from Keychain
        return KeychainManager.shared.getToken() ?? ""
    }
}

// MARK: - API Endpoints
enum APIEndpoint {
    case securityStatus
    case familyMembers
    case vpnStatus
    case aiAssistant(message: String)
    case threats
    case analytics
    case settings
    case profile
    
    var path: String {
        switch self {
        case .securityStatus:
            return "/security/status"
        case .familyMembers:
            return "/family/members"
        case .vpnStatus:
            return "/vpn/status"
        case .aiAssistant:
            return "/ai/assistant"
        case .threats:
            return "/security/threats"
        case .analytics:
            return "/analytics"
        case .settings:
            return "/settings"
        case .profile:
            return "/profile"
        }
    }
    
    var method: HTTPMethod {
        switch self {
        case .securityStatus, .familyMembers, .vpnStatus, .threats, .analytics, .settings, .profile:
            return .GET
        case .aiAssistant:
            return .POST
        }
    }
    
    var body: Codable? {
        switch self {
        case .aiAssistant(let message):
            return AIRequest(message: message)
        default:
            return nil
        }
    }
    
    var queryItems: [URLQueryItem]? {
        switch self {
        case .threats:
            return [URLQueryItem(name: "active", value: "true")]
        default:
            return nil
        }
    }
}

enum HTTPMethod: String {
    case GET = "GET"
    case POST = "POST"
    case PUT = "PUT"
    case DELETE = "DELETE"
}

// MARK: - API Error
enum APIError: Error, LocalizedError {
    case invalidURL
    case networkError(Error)
    case decodingError(Error)
    case authenticationFailed
    case serverError(Int)
    case noData
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Неверный URL"
        case .networkError(let error):
            return "Ошибка сети: \(error.localizedDescription)"
        case .decodingError(let error):
            return "Ошибка декодирования: \(error.localizedDescription)"
        case .authenticationFailed:
            return "Ошибка аутентификации"
        case .serverError(let code):
            return "Ошибка сервера: \(code)"
        case .noData:
            return "Нет данных"
        }
    }
}
```

### 📋 **2. Models.swift:**
```swift
import Foundation

// MARK: - Security Models
struct SecurityStatus: Codable {
    let isSecure: Bool
    let responseTime: String
    let activeModules: Int
    let lastScan: Date
    let threatsBlocked: Int
    let uptime: String
    let systemHealth: SystemHealth
}

struct SystemHealth: Codable {
    let cpu: Double
    let memory: Double
    let disk: Double
    let network: Double
}

struct Threat: Codable, Identifiable {
    let id: String
    let type: ThreatType
    let severity: ThreatSeverity
    let description: String
    let timestamp: Date
    let source: String
    let status: ThreatStatus
}

enum ThreatType: String, Codable {
    case malware = "malware"
    case phishing = "phishing"
    case suspiciousCall = "suspicious_call"
    case dataLeak = "data_leak"
    case deepfake = "deepfake"
    case ransomware = "ransomware"
    case botnet = "botnet"
    case ddos = "ddos"
}

enum ThreatSeverity: String, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
}

enum ThreatStatus: String, Codable {
    case active = "active"
    case blocked = "blocked"
    case resolved = "resolved"
    case investigating = "investigating"
}

// MARK: - Family Models
struct FamilyMember: Codable, Identifiable {
    let id: String
    let name: String
    let age: Int
    let role: FamilyRole
    let isOnline: Bool
    let lastSeen: Date
    let deviceInfo: DeviceInfo
    let securityStatus: MemberSecurityStatus
}

enum FamilyRole: String, Codable {
    case child = "child"
    case teenager = "teenager"
    case parent = "parent"
    case elderly = "elderly"
    case guardian = "guardian"
    case admin = "admin"
}

struct DeviceInfo: Codable {
    let platform: String
    let model: String
    let osVersion: String
    let appVersion: String
    let batteryLevel: Int?
    let isCharging: Bool?
}

struct MemberSecurityStatus: Codable {
    let isProtected: Bool
    let activeThreats: Int
    let lastScan: Date
    let timeOnline: String
    let blockedSites: Int
    let blockedApps: Int
}

// MARK: - VPN Models
struct VPNStatus: Codable {
    let isConnected: Bool
    let server: VPNServer
    let connectionTime: Date?
    let dataTransferred: DataUsage
    let speed: NetworkSpeed
    let encryption: EncryptionInfo
}

struct VPNServer: Codable {
    let id: String
    let name: String
    let country: String
    let city: String
    let ip: String
    let load: Double
    let ping: Int
}

struct DataUsage: Codable {
    let downloaded: Int64
    let uploaded: Int64
    let total: Int64
    let sessionDownloaded: Int64
    let sessionUploaded: Int64
}

struct NetworkSpeed: Codable {
    let download: Double
    let upload: Double
    let ping: Int
    let jitter: Int
}

struct EncryptionInfo: Codable {
    let protocol: String
    let cipher: String
    let keySize: Int
    let handshake: String
}

// MARK: - AI Assistant Models
struct AIRequest: Codable {
    let message: String
    let context: AIContext?
    let language: String
    let timestamp: Date
}

struct AIResponse: Codable {
    let message: String
    let suggestions: [String]
    let actions: [AIAction]
    let confidence: Double
    let timestamp: Date
}

struct AIContext: Codable {
    let userRole: FamilyRole
    let currentScreen: String
    let previousMessages: [String]
    let systemStatus: String
}

struct AIAction: Codable {
    let type: AIActionType
    let title: String
    let description: String
    let parameters: [String: String]
}

enum AIActionType: String, Codable {
    case navigate = "navigate"
    case showInfo = "show_info"
    case openSettings = "open_settings"
    case blockThreat = "block_threat"
    case sendNotification = "send_notification"
}

// MARK: - Analytics Models
struct AnalyticsData: Codable {
    let threatsBlocked: Int
    let timeOnline: String
    let efficiency: Double
    let familyActivity: FamilyActivity
    let deviceStats: DeviceStats
    let securityTrends: SecurityTrends
}

struct FamilyActivity: Codable {
    let totalTime: String
    let mostActiveMember: String
    let averageSession: String
    let peakHours: [String]
}

struct DeviceStats: Codable {
    let totalDevices: Int
    let onlineDevices: Int
    let protectedDevices: Int
    let averageUptime: String
}

struct SecurityTrends: Codable {
    let threatsPerDay: [Int]
    let blockedSites: [Int]
    let blockedApps: [Int]
    let efficiencyTrend: [Double]
}

// MARK: - Settings Models
struct UserSettings: Codable {
    let notifications: NotificationSettings
    let security: SecuritySettings
    let privacy: PrivacySettings
    let display: DisplaySettings
}

struct NotificationSettings: Codable {
    let enabled: Bool
    let types: [NotificationType]
    let frequency: NotificationFrequency
    let quietHours: QuietHours?
}

enum NotificationType: String, Codable {
    case threats = "threats"
    case family = "family"
    case system = "system"
    case updates = "updates"
}

enum NotificationFrequency: String, Codable {
    case immediate = "immediate"
    case hourly = "hourly"
    case daily = "daily"
    case weekly = "weekly"
}

struct QuietHours: Codable {
    let start: String
    let end: String
    let timezone: String
}

struct SecuritySettings: Codable {
    let biometricAuth: Bool
    let twoFactorAuth: Bool
    let autoScan: Bool
    let scanFrequency: ScanFrequency
    let threatSensitivity: ThreatSensitivity
}

enum ScanFrequency: String, Codable {
    case realTime = "real_time"
    case every5Minutes = "5_minutes"
    case every15Minutes = "15_minutes"
    case everyHour = "hourly"
}

enum ThreatSensitivity: String, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case maximum = "maximum"
}

struct PrivacySettings: Codable {
    let dataCollection: Bool
    let analytics: Bool
    let crashReporting: Bool
    let personalization: Bool
}

struct DisplaySettings: Codable {
    let theme: AppTheme
    let fontSize: FontSize
    let language: String
    let interfaceMode: InterfaceMode
}

enum AppTheme: String, Codable {
    case stormSky = "storm_sky"
    case dark = "dark"
    case light = "light"
    case auto = "auto"
}

enum FontSize: String, Codable {
    case small = "small"
    case medium = "medium"
    case large = "large"
    case extraLarge = "extra_large"
}

enum InterfaceMode: String, Codable {
    case standard = "standard"
    case child = "child"
    case elderly = "elderly"
    case accessibility = "accessibility"
}
```

### 📋 **3. Services.swift:**
```swift
import Foundation
import Combine

// MARK: - Security Service
class SecurityService: ObservableObject {
    private let apiClient = APIClient.shared
    
    func getSecurityStatus() -> AnyPublisher<SecurityStatus, APIError> {
        return apiClient.request(endpoint: .securityStatus, responseType: SecurityStatus.self)
    }
    
    func getActiveThreats() -> AnyPublisher<[Threat], APIError> {
        return apiClient.request(endpoint: .threats, responseType: [Threat].self)
    }
    
    func blockThreat(_ threatId: String) -> AnyPublisher<Bool, APIError> {
        // Implementation for blocking specific threat
        return Just(true)
            .setFailureType(to: APIError.self)
            .eraseToAnyPublisher()
    }
}

// MARK: - Family Service
class FamilyService: ObservableObject {
    private let apiClient = APIClient.shared
    
    func getFamilyMembers() -> AnyPublisher<[FamilyMember], APIError> {
        return apiClient.request(endpoint: .familyMembers, responseType: [FamilyMember].self)
    }
    
    func updateMemberSettings(_ memberId: String, settings: [String: Any]) -> AnyPublisher<Bool, APIError> {
        // Implementation for updating member settings
        return Just(true)
            .setFailureType(to: APIError.self)
            .eraseToAnyPublisher()
    }
}

// MARK: - VPN Service
class VPNService: ObservableObject {
    private let apiClient = APIClient.shared
    
    func getVPNStatus() -> AnyPublisher<VPNStatus, APIError> {
        return apiClient.request(endpoint: .vpnStatus, responseType: VPNStatus.self)
    }
    
    func connectVPN(serverId: String) -> AnyPublisher<Bool, APIError> {
        // Implementation for connecting to VPN
        return Just(true)
            .setFailureType(to: APIError.self)
            .eraseToAnyPublisher()
    }
    
    func disconnectVPN() -> AnyPublisher<Bool, APIError> {
        // Implementation for disconnecting VPN
        return Just(true)
            .setFailureType(to: APIError.self)
            .eraseToAnyPublisher()
    }
}

// MARK: - AI Assistant Service
class AIAssistantService: ObservableObject {
    private let apiClient = APIClient.shared
    
    func sendMessage(_ message: String, context: AIContext? = nil) -> AnyPublisher<AIResponse, APIError> {
        let request = AIRequest(
            message: message,
            context: context,
            language: "ru",
            timestamp: Date()
        )
        
        return apiClient.request(endpoint: .aiAssistant(message: message), responseType: AIResponse.self)
    }
}

// MARK: - Analytics Service
class AnalyticsService: ObservableObject {
    private let apiClient = APIClient.shared
    
    func getAnalytics() -> AnyPublisher<AnalyticsData, APIError> {
        return apiClient.request(endpoint: .analytics, responseType: AnalyticsData.self)
    }
}

// MARK: - Settings Service
class SettingsService: ObservableObject {
    private let apiClient = APIClient.shared
    
    func getSettings() -> AnyPublisher<UserSettings, APIError> {
        return apiClient.request(endpoint: .settings, responseType: UserSettings.self)
    }
    
    func updateSettings(_ settings: UserSettings) -> AnyPublisher<Bool, APIError> {
        // Implementation for updating settings
        return Just(true)
            .setFailureType(to: APIError.self)
            .eraseToAnyPublisher()
    }
}
```

### 📋 **4. KeychainManager.swift:**
```swift
import Foundation
import Security

class KeychainManager {
    static let shared = KeychainManager()
    
    private let service = "com.aladdin.security"
    
    private init() {}
    
    func saveToken(_ token: String) {
        let data = token.data(using: .utf8)!
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token",
            kSecValueData as String: data
        ]
        
        // Delete existing item
        SecItemDelete(query as CFDictionary)
        
        // Add new item
        SecItemAdd(query as CFDictionary, nil)
    }
    
    func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token",
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var dataTypeRef: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &dataTypeRef)
        
        guard status == errSecSuccess,
              let data = dataTypeRef as? Data,
              let token = String(data: data, encoding: .utf8) else {
            return nil
        }
        
        return token
    }
    
    func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token"
        ]
        
        SecItemDelete(query as CFDictionary)
    }
}
```

---

## 🤖 **ANDROID API ИНТЕГРАЦИЯ**

### 📋 **1. ApiClient.kt:**
```kotlin
package com.aladdin.network

import com.aladdin.models.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

class ApiClient {
    companion object {
        private const val BASE_URL = "https://api.aladdin-security.com/v1"
        
        private val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        
        val apiService: ApiService = retrofit.create(ApiService::class.java)
    }
}

interface ApiService {
    @GET("/security/status")
    suspend fun getSecurityStatus(): SecurityStatus
    
    @GET("/family/members")
    suspend fun getFamilyMembers(): List<FamilyMember>
    
    @GET("/vpn/status")
    suspend fun getVPNStatus(): VPNStatus
    
    @POST("/ai/assistant")
    suspend fun sendAIMessage(@Body request: AIRequest): AIResponse
    
    @GET("/security/threats")
    suspend fun getActiveThreats(@Query("active") active: Boolean = true): List<Threat>
    
    @GET("/analytics")
    suspend fun getAnalytics(): AnalyticsData
    
    @GET("/settings")
    suspend fun getSettings(): UserSettings
    
    @PUT("/settings")
    suspend fun updateSettings(@Body settings: UserSettings): Boolean
    
    @GET("/profile")
    suspend fun getProfile(): UserProfile
}

// MARK: - Data Classes
data class SecurityStatus(
    val isSecure: Boolean,
    val responseTime: String,
    val activeModules: Int,
    val lastScan: String,
    val threatsBlocked: Int,
    val uptime: String,
    val systemHealth: SystemHealth
)

data class SystemHealth(
    val cpu: Double,
    val memory: Double,
    val disk: Double,
    val network: Double
)

data class Threat(
    val id: String,
    val type: String,
    val severity: String,
    val description: String,
    val timestamp: String,
    val source: String,
    val status: String
)

data class FamilyMember(
    val id: String,
    val name: String,
    val age: Int,
    val role: String,
    val isOnline: Boolean,
    val lastSeen: String,
    val deviceInfo: DeviceInfo,
    val securityStatus: MemberSecurityStatus
)

data class DeviceInfo(
    val platform: String,
    val model: String,
    val osVersion: String,
    val appVersion: String,
    val batteryLevel: Int?,
    val isCharging: Boolean?
)

data class MemberSecurityStatus(
    val isProtected: Boolean,
    val activeThreats: Int,
    val lastScan: String,
    val timeOnline: String,
    val blockedSites: Int,
    val blockedApps: Int
)

data class VPNStatus(
    val isConnected: Boolean,
    val server: VPNServer,
    val connectionTime: String?,
    val dataTransferred: DataUsage,
    val speed: NetworkSpeed,
    val encryption: EncryptionInfo
)

data class VPNServer(
    val id: String,
    val name: String,
    val country: String,
    val city: String,
    val ip: String,
    val load: Double,
    val ping: Int
)

data class DataUsage(
    val downloaded: Long,
    val uploaded: Long,
    val total: Long,
    val sessionDownloaded: Long,
    val sessionUploaded: Long
)

data class NetworkSpeed(
    val download: Double,
    val upload: Double,
    val ping: Int,
    val jitter: Int
)

data class EncryptionInfo(
    val protocol: String,
    val cipher: String,
    val keySize: Int,
    val handshake: String
)

data class AIRequest(
    val message: String,
    val context: AIContext?,
    val language: String,
    val timestamp: String
)

data class AIResponse(
    val message: String,
    val suggestions: List<String>,
    val actions: List<AIAction>,
    val confidence: Double,
    val timestamp: String
)

data class AIContext(
    val userRole: String,
    val currentScreen: String,
    val previousMessages: List<String>,
    val systemStatus: String
)

data class AIAction(
    val type: String,
    val title: String,
    val description: String,
    val parameters: Map<String, String>
)

data class AnalyticsData(
    val threatsBlocked: Int,
    val timeOnline: String,
    val efficiency: Double,
    val familyActivity: FamilyActivity,
    val deviceStats: DeviceStats,
    val securityTrends: SecurityTrends
)

data class FamilyActivity(
    val totalTime: String,
    val mostActiveMember: String,
    val averageSession: String,
    val peakHours: List<String>
)

data class DeviceStats(
    val totalDevices: Int,
    val onlineDevices: Int,
    val protectedDevices: Int,
    val averageUptime: String
)

data class SecurityTrends(
    val threatsPerDay: List<Int>,
    val blockedSites: List<Int>,
    val blockedApps: List<Int>,
    val efficiencyTrend: List<Double>
)

data class UserSettings(
    val notifications: NotificationSettings,
    val security: SecuritySettings,
    val privacy: PrivacySettings,
    val display: DisplaySettings
)

data class NotificationSettings(
    val enabled: Boolean,
    val types: List<String>,
    val frequency: String,
    val quietHours: QuietHours?
)

data class QuietHours(
    val start: String,
    val end: String,
    val timezone: String
)

data class SecuritySettings(
    val biometricAuth: Boolean,
    val twoFactorAuth: Boolean,
    val autoScan: Boolean,
    val scanFrequency: String,
    val threatSensitivity: String
)

data class PrivacySettings(
    val dataCollection: Boolean,
    val analytics: Boolean,
    val crashReporting: Boolean,
    val personalization: Boolean
)

data class DisplaySettings(
    val theme: String,
    val fontSize: String,
    val language: String,
    val interfaceMode: String
)

data class UserProfile(
    val id: String,
    val name: String,
    val email: String,
    val role: String,
    val avatar: String?,
    val preferences: Map<String, Any>
)
```

### 📋 **2. Services.kt:**
```kotlin
package com.aladdin.services

import com.aladdin.network.ApiClient
import com.aladdin.models.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SecurityService {
    private val apiService = ApiClient.apiService
    
    suspend fun getSecurityStatus(): SecurityStatus = withContext(Dispatchers.IO) {
        apiService.getSecurityStatus()
    }
    
    suspend fun getActiveThreats(): List<Threat> = withContext(Dispatchers.IO) {
        apiService.getActiveThreats()
    }
    
    suspend fun blockThreat(threatId: String): Boolean = withContext(Dispatchers.IO) {
        // Implementation for blocking specific threat
        true
    }
}

class FamilyService {
    private val apiService = ApiClient.apiService
    
    suspend fun getFamilyMembers(): List<FamilyMember> = withContext(Dispatchers.IO) {
        apiService.getFamilyMembers()
    }
    
    suspend fun updateMemberSettings(memberId: String, settings: Map<String, Any>): Boolean = withContext(Dispatchers.IO) {
        // Implementation for updating member settings
        true
    }
}

class VPNService {
    private val apiService = ApiClient.apiService
    
    suspend fun getVPNStatus(): VPNStatus = withContext(Dispatchers.IO) {
        apiService.getVPNStatus()
    }
    
    suspend fun connectVPN(serverId: String): Boolean = withContext(Dispatchers.IO) {
        // Implementation for connecting to VPN
        true
    }
    
    suspend fun disconnectVPN(): Boolean = withContext(Dispatchers.IO) {
        // Implementation for disconnecting VPN
        true
    }
}

class AIAssistantService {
    private val apiService = ApiClient.apiService
    
    suspend fun sendMessage(message: String, context: AIContext? = null): AIResponse = withContext(Dispatchers.IO) {
        val request = AIRequest(
            message = message,
            context = context,
            language = "ru",
            timestamp = System.currentTimeMillis().toString()
        )
        apiService.sendAIMessage(request)
    }
}

class AnalyticsService {
    private val apiService = ApiClient.apiService
    
    suspend fun getAnalytics(): AnalyticsData = withContext(Dispatchers.IO) {
        apiService.getAnalytics()
    }
}

class SettingsService {
    private val apiService = ApiClient.apiService
    
    suspend fun getSettings(): UserSettings = withContext(Dispatchers.IO) {
        apiService.getSettings()
    }
    
    suspend fun updateSettings(settings: UserSettings): Boolean = withContext(Dispatchers.IO) {
        apiService.updateSettings(settings)
    }
}
```

### 📋 **3. SecureStorage.kt:**
```kotlin
package com.aladdin.security

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import java.security.KeyStore

class SecureStorage(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "aladdin_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    fun saveToken(token: String) {
        sharedPreferences.edit()
            .putString("auth_token", token)
            .apply()
    }
    
    fun getToken(): String? {
        return sharedPreferences.getString("auth_token", null)
    }
    
    fun deleteToken() {
        sharedPreferences.edit()
            .remove("auth_token")
            .apply()
    }
    
    fun saveUserSettings(settings: String) {
        sharedPreferences.edit()
            .putString("user_settings", settings)
            .apply()
    }
    
    fun getUserSettings(): String? {
        return sharedPreferences.getString("user_settings", null)
    }
}
```

---

## 🔐 **БЕЗОПАСНОСТЬ API**

### 🛡️ **МЕРЫ БЕЗОПАСНОСТИ:**
1. **TLS 1.3** для всех соединений
2. **JWT токены** с коротким временем жизни
3. **Biometric аутентификация** для критических операций
4. **Certificate Pinning** для предотвращения MITM атак
5. **Request signing** для предотвращения подделки запросов
6. **Rate limiting** для предотвращения DDoS атак

### 🔑 **АУТЕНТИФИКАЦИЯ:**
- **JWT токены** с refresh механизмом
- **Biometric аутентификация** для чувствительных операций
- **Two-factor authentication** для административных функций
- **Session management** с автоматическим logout

---

## 🚀 **СЛЕДУЮЩИЕ ШАГИ**

1. **Настроить серверную часть** ALADDIN API
2. **Реализовать аутентификацию** с JWT и биометрией
3. **Создать тестовые данные** для разработки
4. **Настроить мониторинг** и логирование
5. **Протестировать API** на всех платформах
6. **Оптимизировать производительность**

**🎯 API ИНТЕГРАЦИЯ ГОТОВА К РЕАЛИЗАЦИИ!**

**📱 ПЕРЕХОДИМ К СИСТЕМЕ АУТЕНТИФИКАЦИИ!**

