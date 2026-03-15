//
//  SubscriptionModels.swift
//  ALADDIN
//
//  Created by ALADDIN Team
//  Copyright © 2025 ALADDIN. All rights reserved.
//
//  🔐 CRITICAL SECURITY COMPONENT - JWT Subscription Management
//  Handles subscription state, JWT tokens, and feature access control
//  Core security layer protecting millions of families from cyber threats
//

import Foundation
import SwiftUI

// MARK: - Core Subscription Models

/// 🔑 JWT Token Structure for Subscription Management
struct JWTToken: Codable, Equatable {
    /// Raw JWT token string
    let token: String

    /// Device identifier
    let deviceId: String

    /// Subscription level embedded in token
    let subscriptionLevel: SubscriptionLevel

    /// Trial information (if active)
    let trialInfo: TrialInfo?

    /// Token expiration date
    let expiresAt: Date

    /// Token issued date
    let issuedAt: Date

    /// Token issuer
    let issuer: String

    /// Available feature limits
    let limits: SubscriptionLimits

    /// Available components
    let components: [String]

    enum CodingKeys: String, CodingKey {
        case token
        case deviceId = "device_id"
        case subscriptionLevel = "subscription_level"
        case trialInfo = "trial_info"
        case expiresAt = "exp"
        case issuedAt = "iat"
        case issuer = "iss"
        case limits
        case components
    }
    
    /// ✅ ИСПРАВЛЕНО: Явный инициализатор для предотвращения ошибок компиляции
    /// Также требуется для Codable, чтобы автоматический инициализатор работал правильно
    init(
        token: String,
        deviceId: String,
        subscriptionLevel: SubscriptionLevel,
        trialInfo: TrialInfo?,
        expiresAt: Date,
        issuedAt: Date,
        issuer: String,
        limits: SubscriptionLimits,
        components: [String]
    ) {
        self.token = token
        self.deviceId = deviceId
        self.subscriptionLevel = subscriptionLevel
        self.trialInfo = trialInfo
        self.expiresAt = expiresAt
        self.issuedAt = issuedAt
        self.issuer = issuer
        self.limits = limits
        self.components = components
    }
    
    /// ✅ ИСПРАВЛЕНО: Явный инициализатор из Decoder для Codable
    /// Обрабатывает Date как TimeInterval (Unix timestamp) из JSON
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        token = try container.decode(String.self, forKey: .token)
        deviceId = try container.decode(String.self, forKey: .deviceId)
        subscriptionLevel = try container.decode(SubscriptionLevel.self, forKey: .subscriptionLevel)
        trialInfo = try container.decodeIfPresent(TrialInfo.self, forKey: .trialInfo)
        
        // ✅ ИСПРАВЛЕНО: Date декодируется как TimeInterval (Unix timestamp)
        let expiresAtInterval = try container.decode(TimeInterval.self, forKey: .expiresAt)
        expiresAt = Date(timeIntervalSince1970: expiresAtInterval)
        
        let issuedAtInterval = try container.decode(TimeInterval.self, forKey: .issuedAt)
        issuedAt = Date(timeIntervalSince1970: issuedAtInterval)
        
        issuer = try container.decode(String.self, forKey: .issuer)
        limits = try container.decode(SubscriptionLimits.self, forKey: .limits)
        components = try container.decode([String].self, forKey: .components)
    }
    
    /// ✅ ИСПРАВЛЕНО: Явный метод encode для Codable
    /// Кодирует Date как TimeInterval (Unix timestamp) в JSON
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(token, forKey: .token)
        try container.encode(deviceId, forKey: .deviceId)
        try container.encode(subscriptionLevel, forKey: .subscriptionLevel)
        try container.encodeIfPresent(trialInfo, forKey: .trialInfo)
        
        // ✅ ИСПРАВЛЕНО: Date кодируется как TimeInterval (Unix timestamp)
        try container.encode(expiresAt.timeIntervalSince1970, forKey: .expiresAt)
        try container.encode(issuedAt.timeIntervalSince1970, forKey: .issuedAt)
        
        try container.encode(issuer, forKey: .issuer)
        try container.encode(limits, forKey: .limits)
        try container.encode(components, forKey: .components)
    }
}

/// 🎯 Subscription Level Hierarchy (5 levels as per specification)
enum SubscriptionLevel: String, Codable, CaseIterable {
    case trial = "trial"      // 14 days, 80% functions
    case free = "free"        // 26/142 functions (18%)
    case personal = "personal" // 69/142 functions (49%)
    case family = "family"    // 128/142 functions (90%)
    case premium = "premium"  // 142/142 functions (100%) + 42 components

    /// Numeric level for comparison (higher = more features)
    var numericLevel: Int {
        switch self {
        case .trial: return 0
        case .free: return 1
        case .personal: return 2
        case .family: return 3
        case .premium: return 4
        }
    }

    /// Display name for UI
    var displayName: String {
        switch self {
        case .trial: return "TRIAL"
        case .free: return "FREE"
        case .personal: return "PERSONAL"
        case .family: return "FAMILY"
        case .premium: return "PREMIUM"
        }
    }

    /// Maximum number of functions available
    var maxFunctions: Int {
        switch self {
        case .trial: return 114    // 80% of 142
        case .free: return 26      // 18% of 142
        case .personal: return 69  // 49% of 142
        case .family: return 128   // 90% of 142
        case .premium: return 142  // 100% of 142
        }
    }

    /// Maximum number of components available
    var maxComponents: Int {
        switch self {
        case .trial: return 0      // No components in trial
        case .free: return 8       // 8 components
        case .personal: return 20  // 20 components
        case .family: return 35    // 35 components
        case .premium: return 42   // All 42 components
        }
    }

    /// Price in RUB (monthly)
    var monthlyPrice: Int {
        switch self {
        case .trial: return 0
        case .free: return 0
        case .personal: return 100
        case .family: return 290
        case .premium: return 490
        }
    }
}

/// 🎁 Trial Information Structure
struct TrialInfo: Codable, Equatable {
    /// Trial start date
    let startDate: Date

    /// Trial end date
    let endDate: Date

    /// Trial duration in days
    let durationDays: Int

    /// Days remaining in trial
    var daysRemaining: Int {
        let calendar = Calendar.current
        let now = Date()
        let components = calendar.dateComponents([.day], from: now, to: endDate)
        return max(0, components.day ?? 0)
    }

    /// Is trial still active
    var isActive: Bool {
        Date() < endDate
    }

    /// Trial progress (0.0 to 1.0)
    var progress: Double {
        let total = Double(durationDays)
        let remaining = Double(daysRemaining)
        return (total - remaining) / total
    }
}

/// 📊 Subscription Limits Structure
struct SubscriptionLimits: Codable, Equatable {
    /// Maximum devices per subscription
    let maxDevices: Int

    /// Maximum AI chat messages per month
    let maxAIMessages: Int

    /// Maximum scans per month
    let maxScans: Int

    /// Maximum reports per month
    let maxReports: Int

    /// Current usage counters
    var currentUsage: UsageCounters

    /// Check if limit exceeded for specific resource
    func isLimitExceeded(for resource: SubscriptionResource) -> Bool {
        switch resource {
        case .aiMessages:
            return currentUsage.aiMessages >= maxAIMessages
        case .scans:
            return currentUsage.scans >= maxScans
        case .reports:
            return currentUsage.reports >= maxReports
        case .devices:
            return currentUsage.devices >= maxDevices
        }
    }

    /// Get remaining count for specific resource
    func remainingCount(for resource: SubscriptionResource) -> Int {
        switch resource {
        case .aiMessages:
            return max(0, maxAIMessages - currentUsage.aiMessages)
        case .scans:
            return max(0, maxScans - currentUsage.scans)
        case .reports:
            return max(0, maxReports - currentUsage.reports)
        case .devices:
            return max(0, maxDevices - currentUsage.devices)
        }
    }
}

/// 📈 Usage Counters Structure
struct UsageCounters: Codable, Equatable {
    /// Current AI messages used this month
    var aiMessages: Int

    /// Current scans used this month
    var scans: Int

    /// Current reports used this month
    var reports: Int

    /// Current devices connected
    var devices: Int

    /// Reset counters for new month
    mutating func resetMonthlyCounters() {
        aiMessages = 0
        scans = 0
        reports = 0
        // devices counter stays (persistent)
    }

    /// Increment counter for specific resource
    mutating func increment(_ resource: SubscriptionResource, by amount: Int = 1) {
        switch resource {
        case .aiMessages:
            aiMessages += amount
        case .scans:
            scans += amount
        case .reports:
            reports += amount
        case .devices:
            devices += amount
        }
    }
}

/// 🎯 Subscription Resource Types
enum SubscriptionResource: String, Codable {
    case aiMessages = "ai_messages"
    case scans = "scans"
    case reports = "reports"
    case devices = "devices"
}

/// 🔐 Subscription Status Structure
struct SubscriptionStatus: Codable, Equatable {
    /// Current subscription level
    let level: SubscriptionLevel

    /// Is subscription active
    let isActive: Bool

    /// Subscription expiration date (for paid levels)
    let expiresAt: Date?

    /// Trial information (if applicable)
    let trialInfo: TrialInfo?

    /// Current limits
    var limits: SubscriptionLimits

    /// Available components
    let components: [String]

    /// Last updated timestamp
    let lastUpdated: Date

    /// Is subscription expired
    var isExpired: Bool {
        if let expiresAt = self.expiresAt {
            return Date() > expiresAt
        }
        return false
    }

    /// Days until expiration (nil if no expiration)
    var daysUntilExpiration: Int? {
        guard let expiresAt = self.expiresAt else { return nil }
        let calendar = Calendar.current
        let components = calendar.dateComponents([.day], from: Date(), to: expiresAt)
        return components.day
    }
}

// 🔧 TEMPORARY: Alternative type to bypass caching issues
struct AppSubscriptionStatus: Codable, Equatable {
    let level: SubscriptionLevel
    let isActive: Bool
    let expiresAt: Date?
    let trialInfo: TrialInfo?
    var limits: SubscriptionLimits
    let components: [String]
    let lastUpdated: Date
}

// 📱 Device Registration Subscription - базовая информация при регистрации
/// ✅ SOLUTION: Separate model for API responses vs internal models
/// Используется только при регистрации устройства, содержит минимальный набор полей
struct DeviceRegistrationSubscription: Codable {
    /// Subscription level as string from API
    let level: String

    /// Is subscription active
    let isActive: Bool

    /// Subscription expiration date as ISO 8601 string from API
    let expiresAt: String?

    /// Trial information (if applicable)
    let trialInfo: TrialInfo?
}

// 🔄 Conversion Extension
extension DeviceRegistrationSubscription {
    /// Convert API model to internal SubscriptionStatus
    /// ✅ SOLUTION: Clean separation between API and internal models
    func toSubscriptionStatus() -> SubscriptionStatus {
        return SubscriptionStatus(
            level: SubscriptionLevel(rawValue: level) ?? .free,  // Convert string to enum
            isActive: isActive,
            expiresAt: parseISODate(expiresAt),                  // Convert string to Date
            trialInfo: trialInfo,
            limits: SubscriptionLimits.freeLimits,               // Default for new user
            components: [],                                       // Default for new user
            lastUpdated: Date()
        )
    }

    /// Parse ISO 8601 date string to Date (helper function)
    private func parseISODate(_ dateString: String?) -> Date? {
        guard let dateString = dateString else { return nil }
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime] // Поддержка формата 2026-03-05T10:19:39.616795Z
        return formatter.date(from: dateString)
    }
}

extension SubscriptionStatusSummaryResponse {
    /// Convert API model to internal SubscriptionStatus
    /// ✅ SOLUTION: Clean separation between API and internal models
    func toSubscriptionStatus(currentSubscription: SubscriptionStatus?) -> SubscriptionStatus {
        return SubscriptionStatus(
            level: currentSubscription?.level ?? .free,              // Use current subscription level
            isActive: isActive,
            expiresAt: currentSubscription?.expiresAt,               // Use current expiration date
            trialInfo: currentSubscription?.trialInfo,               // Use current trial info
            limits: currentSubscription?.limits ?? SubscriptionLimits.freeLimits, // Use current limits
            components: currentSubscription?.components ?? [],       // Use current components
            lastUpdated: parseISODate(lastModified) ?? Date()        // Parse lastModified as lastUpdated
        )
    }

    /// Parse ISO 8601 date string to Date (helper function)
    private func parseISODate(_ dateString: String?) -> Date? {
        guard let dateString = dateString else { return nil }
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime] // Поддержка формата 2026-03-06T15:43:24.486626
        return formatter.date(from: dateString)
    }
}

/// ⚠️ Subscription Error Types
enum SubscriptionError: LocalizedError {
    case tokenExpired
    case invalidToken
    case networkError
    case serverError(String)
    case limitExceeded(SubscriptionResource)
    case trialExpired
    case subscriptionExpired
    case unauthorized

    var errorDescription: String? {
        switch self {
        case .tokenExpired:
            return "Subscription token has expired"
        case .invalidToken:
            return "Invalid subscription token"
        case .networkError:
            return "Network connection error"
        case .serverError(let message):
            return "Server error: \(message)"
        case .limitExceeded(let resource):
            return "\(resource.rawValue.capitalized) limit exceeded"
        case .trialExpired:
            return "Trial period has ended"
        case .subscriptionExpired:
            return "Subscription has expired"
        case .unauthorized:
            return "Unauthorized access"
        }
    }
}

// MARK: - Feature Access Control

/// 🔒 Feature Access Level Requirements
enum FeatureAccessLevel: String, Codable {
    case free = "free"        // Available in free tier
    case trial = "trial"      // Available in trial
    case personal = "personal" // Requires personal+
    case family = "family"    // Requires family+
    case premium = "premium"  // Requires premium only
}

/// 🔑 Feature Access Configuration
struct FeatureAccessConfig {
    let featureId: String
    let requiredLevel: FeatureAccessLevel
    let resourceType: SubscriptionResource?
    let componentId: String?

    /// Check if user level can access this feature
    func canAccess(with level: SubscriptionLevel) -> Bool {
        switch requiredLevel {
        case .free:
            return true
        case .trial:
            return level.numericLevel >= SubscriptionLevel.trial.numericLevel
        case .personal:
            return level.numericLevel >= SubscriptionLevel.personal.numericLevel
        case .family:
            return level.numericLevel >= SubscriptionLevel.family.numericLevel
        case .premium:
            return level.numericLevel >= SubscriptionLevel.premium.numericLevel
        }
    }
}

// MARK: - API Response Models

/// 📡 JWT Registration Response
/// ✅ FIXED: Server returns dates as ISO 8601 strings, not Date objects
struct JWTDeviceRegisterResponse: Codable {
    let token: String
    let deviceId: String
    let expiresAt: String  // ISO 8601 date string from server
    let registeredAt: String  // ISO 8601 date string from server
    let subscription: DeviceRegistrationSubscription  // ✅ FIXED: Use separate model for API responses

    /// Convert expiresAt string to Date
    var expiresAtDate: Date? {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime] // Поддержка формата 2026-03-05T10:19:39.616795Z
        return formatter.date(from: expiresAt)
    }

    /// Convert registeredAt string to Date
    var registeredAtDate: Date? {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        return formatter.date(from: registeredAt)
    }
}

/// 📡 Subscription Status Summary Response (for /api/subscription/status)
struct SubscriptionStatusSummaryResponse: Codable {
    let userId: String
    let isActive: Bool
    let daysRemaining: Int?
    let canRenew: Bool
    let lastModified: String // ISO 8601 date string
}

/// 📡 Subscription Status Response
struct SubscriptionStatusResponse: Codable {
    let status: SubscriptionStatus
    let serverTime: Date
}

/// 📡 Trial Activation Response
struct TrialActivationResponse: Codable {
    let trialActivated: Bool
    let trialInfo: TrialInfo
    let newToken: String
}

// MARK: - Equatable Conformances

extension JWTToken {
    static func == (lhs: JWTToken, rhs: JWTToken) -> Bool {
        lhs.token == rhs.token &&
        lhs.deviceId == rhs.deviceId &&
        lhs.subscriptionLevel == rhs.subscriptionLevel
    }
}

extension TrialInfo {
    static func == (lhs: TrialInfo, rhs: TrialInfo) -> Bool {
        lhs.startDate == rhs.startDate &&
        lhs.endDate == rhs.endDate &&
        lhs.durationDays == rhs.durationDays
    }
}

extension SubscriptionLimits {
    static func == (lhs: SubscriptionLimits, rhs: SubscriptionLimits) -> Bool {
        lhs.maxDevices == rhs.maxDevices &&
        lhs.maxAIMessages == rhs.maxAIMessages &&
        lhs.maxScans == rhs.maxScans &&
        lhs.maxReports == rhs.maxReports &&
        lhs.currentUsage == rhs.currentUsage
    }
    
    /// Free tier limits
    static var freeLimits: SubscriptionLimits {
        SubscriptionLimits(
            maxDevices: 1,
            maxAIMessages: 10,
            maxScans: 5,
            maxReports: 3,
            currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
        )
    }
    
    /// Trial tier limits
    static var trialLimits: SubscriptionLimits {
        SubscriptionLimits(
            maxDevices: 3,
            maxAIMessages: 50,
            maxScans: 100,
            maxReports: 10,
            currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
        )
    }
    
    /// Personal tier limits
    static var personalLimits: SubscriptionLimits {
        SubscriptionLimits(
            maxDevices: 2,
            maxAIMessages: 100,
            maxScans: 50,
            maxReports: 20,
            currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
        )
    }
    
    /// Family tier limits
    static var familyLimits: SubscriptionLimits {
        SubscriptionLimits(
            maxDevices: 6,
            maxAIMessages: 1000,
            maxScans: 200,
            maxReports: 100,
            currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
        )
    }
    
    /// Premium tier limits
    static var premiumLimits: SubscriptionLimits {
        SubscriptionLimits(
            maxDevices: 10,
            maxAIMessages: 10000,
            maxScans: 1000,
            maxReports: 500,
            currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
        )
    }
}

extension UsageCounters {
    static func == (lhs: UsageCounters, rhs: UsageCounters) -> Bool {
        lhs.aiMessages == rhs.aiMessages &&
        lhs.scans == rhs.scans &&
        lhs.reports == rhs.reports &&
        lhs.devices == rhs.devices
    }
}

extension SubscriptionStatus {
    static func == (lhs: SubscriptionStatus, rhs: SubscriptionStatus) -> Bool {
        lhs.level == rhs.level &&
        lhs.isActive == rhs.isActive &&
        lhs.expiresAt == rhs.expiresAt &&
        lhs.trialInfo == rhs.trialInfo &&
        lhs.limits == rhs.limits &&
        lhs.components == rhs.components
    }
}

// MARK: - Detailed Feature Distribution (142 Functions)

// 🎯 GRANULAR FEATURE CONTROL - Enterprise Level
// Critical for precise subscription management and analytics

/// Individual app feature with granular access control
struct AppFeature: Identifiable, Codable {
    let id: String
    let name: String
    let description: String
    let requiredLevel: SubscriptionLevel
    let category: FeatureCategory
    let module: FeatureModule
    let isEnabled: Bool

    var displayName: String { name }
    var fullDescription: String { "\(category.emoji) \(name): \(description)" }
}

enum FeatureCategory: String, Codable, CaseIterable {
    case threatProtection = "threat_protection"
    case parentalControl = "parental_control"
    case additionalFeatures = "additional_features"
    case premiumComponents = "premium_components" // 🏆 42 расширенных компонента только для PREMIUM

    var emoji: String {
        switch self {
        case .threatProtection: return "🛡️"
        case .parentalControl: return "👨‍👩‍👧"
        case .additionalFeatures: return "⭐"
        case .premiumComponents: return "🏆"
        }
    }

    var displayName: String {
        switch self {
        case .threatProtection: return "Защита от угроз"
        case .parentalControl: return "Родительский контроль"
        case .additionalFeatures: return "Дополнительные функции"
        case .premiumComponents: return "Расширенные компоненты"
        }
    }
}

enum FeatureModule: String, Codable {
    // Threat Protection
    case cyberThreats = "cyber_threats"
    case fraud = "fraud"
    case dataLeaks = "data_leaks"
    case deepfakes = "deepfakes"
    case internetThreats = "internet_threats"
    case mobileThreats = "mobile_threats"
    case iotThreats = "iot_threats"
    case childThreats = "child_threats"
    case familyThreats = "family_threats"

    // Parental Control
    case contentFiltering = "content_filtering"
    case timeManagement = "time_management"
    case activityMonitoring = "activity_monitoring"
    case locationTracking = "location_tracking"
    case communicationControl = "communication_control"
    case educationalTools = "educational_tools"
    case emergencyFeatures = "emergency_features"
    case familySharing = "family_sharing"

    // Additional Features
    case aiAssistant = "ai_assistant"
    case analytics = "analytics"
    case backup = "backup"
    case customization = "customization"

    // Premium Components (42 components - PREMIUM only)
    case emergencyAssistance = "emergency_assistance"      // 10 components
    case advancedThreatProtection = "advanced_threat_protection" // 6 components
    case privacyMonitoring = "privacy_monitoring"         // 8 components
    case messagingApps = "messaging_apps"                  // 10 components
    case coreManagers = "core_managers"                    // 8 components
}

/// 🎯 MASTER REGISTRY: 142 Functions Distributed by 5 Levels
/// TRIAL: 114 functions (80%), FREE: 26 functions (18%), PERSONAL: 69 functions (49%), FAMILY: 128 functions (90%), PREMIUM: 142 functions (100%)
struct FeatureRegistry {

    // MARK: - FREE Level (26 functions - 18%)
    static let freeFeatures: [AppFeature] = [
        // Cyber Threats - Basic (10)
        AppFeature(id: "virus_protection", name: "Защита от вирусов", description: "Блокировка компьютерных вирусов", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "trojan_protection", name: "Защита от троянов", description: "Обнаружение троянских программ", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "worm_protection", name: "Защита от червей", description: "Предотвращение распространения червей", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "rootkit_protection", name: "Защита от руткитов", description: "Обнаружение скрытого вредоносного ПО", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "spyware_protection", name: "Защита от шпионского ПО", description: "Блокировка программ слежки", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "adware_protection", name: "Защита от adware", description: "Удаление навязчивой рекламы", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "ransomware_protection", name: "Защита от ransomware", description: "Предотвращение шифрования файлов", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "keylogger_protection", name: "Защита от keyloggers", description: "Блокировка перехвата клавиатуры", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "browser_hijacker_protection", name: "Защита от browser hijackers", description: "Предотвращение изменения настроек браузера", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),
        AppFeature(id: "exploit_protection", name: "Защита от эксплойтов", description: "Блокировка уязвимостей в ПО", requiredLevel: .free, category: .threatProtection, module: .cyberThreats, isEnabled: true),

        // Internet Threats - Basic (6)
        AppFeature(id: "phishing_protection", name: "Защита от фишинга", description: "Блокировка фишинговых сайтов", requiredLevel: .free, category: .threatProtection, module: .internetThreats, isEnabled: true),
        AppFeature(id: "malicious_sites_blocking", name: "Блокировка вредоносных сайтов", description: "Предотвращение посещения опасных ресурсов", requiredLevel: .free, category: .threatProtection, module: .internetThreats, isEnabled: true),
        AppFeature(id: "drive_by_download_protection", name: "Защита от drive-by downloads", description: "Блокировка автоматической загрузки malware", requiredLevel: .free, category: .threatProtection, module: .internetThreats, isEnabled: true),
        AppFeature(id: "malicious_redirects_blocking", name: "Блокировка вредоносных редиректов", description: "Предотвращение перенаправления на опасные сайты", requiredLevel: .free, category: .threatProtection, module: .internetThreats, isEnabled: true),
        AppFeature(id: "fake_websites_detection", name: "Обнаружение поддельных сайтов", description: "Идентификация фальшивых веб-ресурсов", requiredLevel: .free, category: .threatProtection, module: .internetThreats, isEnabled: true),
        AppFeature(id: "suspicious_links_scanning", name: "Сканирование подозрительных ссылок", description: "Проверка URL на безопасность", requiredLevel: .free, category: .threatProtection, module: .internetThreats, isEnabled: true),

        // Mobile & Basic Features (10)
        AppFeature(id: "android_malware_protection", name: "Защита Android malware", description: "Блокировка вредоносного ПО для Android", requiredLevel: .free, category: .threatProtection, module: .mobileThreats, isEnabled: true),
        AppFeature(id: "ios_threats_detection", name: "Обнаружение iOS угроз", description: "Мониторинг безопасности iOS устройств", requiredLevel: .free, category: .threatProtection, module: .mobileThreats, isEnabled: true),
        AppFeature(id: "app_store_scanning", name: "Сканирование App Store", description: "Проверка приложений на безопасность", requiredLevel: .free, category: .threatProtection, module: .mobileThreats, isEnabled: true),
        AppFeature(id: "device_encryption_check", name: "Проверка шифрования устройства", description: "Контроль шифрования данных на устройстве", requiredLevel: .free, category: .threatProtection, module: .mobileThreats, isEnabled: true),
        AppFeature(id: "basic_scan_results", name: "Результаты базового сканирования", description: "Отчеты о найденных угрозах", requiredLevel: .free, category: .additionalFeatures, module: .analytics, isEnabled: true),
        AppFeature(id: "threat_history", name: "История угроз", description: "Журнал обнаруженных угроз", requiredLevel: .free, category: .additionalFeatures, module: .analytics, isEnabled: true),
        AppFeature(id: "basic_ai_queries", name: "Базовые AI запросы", description: "Простые вопросы безопасности", requiredLevel: .free, category: .additionalFeatures, module: .aiAssistant, isEnabled: true),
        AppFeature(id: "security_tips", name: "Советы по безопасности", description: "Рекомендации по защите", requiredLevel: .free, category: .additionalFeatures, module: .aiAssistant, isEnabled: true),
        AppFeature(id: "basic_device_monitoring", name: "Базовый мониторинг устройства", description: "Основной контроль безопасности", requiredLevel: .free, category: .additionalFeatures, module: .analytics, isEnabled: true),
        AppFeature(id: "security_alerts", name: "Предупреждения безопасности", description: "Базовые оповещения об угрозах", requiredLevel: .free, category: .additionalFeatures, module: .analytics, isEnabled: true)
    ]

    // MARK: - PERSONAL Level (69 functions - 49%)
    static let personalFeatures: [AppFeature] = freeFeatures + [
        // Fraud Protection (12)
        AppFeature(id: "banking_fraud_detection", name: "Обнаружение банковского мошенничества", description: "Мониторинг подозрительных банковских операций", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "credit_card_fraud_protection", name: "Защита кредитных карт", description: "Предотвращение несанкционированного использования карт", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "identity_theft_prevention", name: "Предотвращение кражи личности", description: "Защита персональных данных", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "online_shopping_protection", name: "Защита онлайн-покупок", description: "Безопасность интернет-платежей", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "fake_website_alerts", name: "Предупреждения о фальшивых сайтах", description: "Оповещения о подозрительных ресурсах", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "transaction_monitoring", name: "Мониторинг транзакций", description: "Отслеживание финансовых операций", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "password_theft_detection", name: "Обнаружение кражи паролей", description: "Предупреждение о компрометации учетных данных", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "social_engineering_protection", name: "Защита от social engineering", description: "Предотвращение манипуляций", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "phishing_email_detection", name: "Обнаружение фишинговых email", description: "Фильтрация подозрительных писем", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "suspicious_calls_blocking", name: "Блокировка подозрительных звонков", description: "Фильтрация спам-звонков", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "investment_fraud_protection", name: "Защита от инвестиционного мошенничества", description: "Мониторинг финансовых вложений", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),
        AppFeature(id: "crypto_scams_detection", name: "Обнаружение крипто-мошенничества", description: "Защита от криптовалютных scam", requiredLevel: .personal, category: .threatProtection, module: .fraud, isEnabled: true),

        // Data Leaks Protection (12)
        AppFeature(id: "personal_data_monitoring", name: "Мониторинг персональных данных", description: "Отслеживание утечек личной информации", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "password_breach_alerts", name: "Предупреждения о breach паролей", description: "Оповещения о компрометации паролей", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "email_address_leaks", name: "Утечки email адресов", description: "Мониторинг компрометации email", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "phone_number_exposure", name: "Разглашение номеров телефона", description: "Защита телефонных номеров", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "social_security_monitoring", name: "Мониторинг соцсетей", description: "Защита аккаунтов в соцсетях", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "database_breach_scanning", name: "Сканирование breach баз", description: "Проверка утечек в базах данных", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "dark_web_monitoring", name: "Мониторинг dark web", description: "Поиск данных в даркнете", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "data_broker_protection", name: "Защита от data brokers", description: "Предотвращение продажи данных", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "identity_theft_alerts", name: "Предупреждения о краже личности", description: "Оповещения о подозрительной активности", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "credit_report_monitoring", name: "Мониторинг кредитных отчетов", description: "Защита кредитной истории", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "address_exposure_protection", name: "Защита адреса проживания", description: "Предотвращение разглашения адреса", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),
        AppFeature(id: "birth_date_protection", name: "Защита даты рождения", description: "Контроль разглашения персональных дат", requiredLevel: .personal, category: .threatProtection, module: .dataLeaks, isEnabled: true),

        // Advanced Features (7)
        AppFeature(id: "detailed_threat_reports", name: "Детальные отчеты об угрозах", description: "Расширенная аналитика угроз", requiredLevel: .personal, category: .additionalFeatures, module: .analytics, isEnabled: true),
        AppFeature(id: "security_score_tracking", name: "Отслеживание security score", description: "Рейтинг безопасности устройства", requiredLevel: .personal, category: .additionalFeatures, module: .analytics, isEnabled: true),
        AppFeature(id: "advanced_ai_queries", name: "Расширенные AI запросы", description: "Комплексные вопросы безопасности", requiredLevel: .personal, category: .additionalFeatures, module: .aiAssistant, isEnabled: true),
        AppFeature(id: "threat_analysis_ai", name: "AI анализ угроз", description: "ИИ-powered анализ угроз", requiredLevel: .personal, category: .additionalFeatures, module: .aiAssistant, isEnabled: true),
        AppFeature(id: "security_recommendations", name: "Рекомендации по безопасности", description: "Персонализированные советы", requiredLevel: .personal, category: .additionalFeatures, module: .aiAssistant, isEnabled: true),
        AppFeature(id: "advanced_device_monitoring", name: "Расширенный мониторинг устройства", description: "Детальный контроль безопасности", requiredLevel: .personal, category: .additionalFeatures, module: .analytics, isEnabled: true),
        AppFeature(id: "custom_security_alerts", name: "Пользовательские оповещения", description: "Настраиваемые уведомления безопасности", requiredLevel: .personal, category: .additionalFeatures, module: .analytics, isEnabled: true),

        // Additional PERSONAL functions (to reach 43 total additional)
        AppFeature(id: "personal_device_backup", name: "Резервное копирование", description: "Автоматическое резервное копирование данных", requiredLevel: .personal, category: .additionalFeatures, module: .backup, isEnabled: true),
        AppFeature(id: "personal_data_sync", name: "Синхронизация данных", description: "Синхронизация настроек между устройствами", requiredLevel: .personal, category: .additionalFeatures, module: .backup, isEnabled: true),
        AppFeature(id: "personal_security_audit", name: "Аудит безопасности", description: "Регулярная проверка безопасности аккаунта", requiredLevel: .personal, category: .additionalFeatures, module: .analytics, isEnabled: true),
        AppFeature(id: "personal_privacy_dashboard", name: "Приватность dashboard", description: "Обзор приватности и настроек", requiredLevel: .personal, category: .additionalFeatures, module: .analytics, isEnabled: true),
        AppFeature(id: "personal_customization", name: "Персонализация", description: "Настройка интерфейса под пользователя", requiredLevel: .personal, category: .additionalFeatures, module: .customization, isEnabled: true),
        AppFeature(id: "personal_quick_actions", name: "Быстрые действия", description: "Кастомные быстрые действия", requiredLevel: .personal, category: .additionalFeatures, module: .customization, isEnabled: true),
        AppFeature(id: "personal_automation", name: "Автоматизация", description: "Автоматические действия по расписанию", requiredLevel: .personal, category: .additionalFeatures, module: .customization, isEnabled: true),
        AppFeature(id: "personal_shortcuts", name: "Ярлыки", description: "Персональные ярлыки для часто используемых функций", requiredLevel: .personal, category: .additionalFeatures, module: .customization, isEnabled: true),
        AppFeature(id: "personal_themes", name: "Темы", description: "Выбор тем оформления", requiredLevel: .personal, category: .additionalFeatures, module: .customization, isEnabled: true),
        AppFeature(id: "personal_language_settings", name: "Языковые настройки", description: "Выбор языка интерфейса", requiredLevel: .personal, category: .additionalFeatures, module: .customization, isEnabled: true),
        AppFeature(id: "personal_notification_settings", name: "Настройки уведомлений", description: "Контроль уведомлений", requiredLevel: .personal, category: .additionalFeatures, module: .customization, isEnabled: true),
        AppFeature(id: "personal_accessibility", name: "Специальные возможности", description: "Настройки доступности", requiredLevel: .personal, category: .additionalFeatures, module: .customization, isEnabled: true)
    ]

    // MARK: - FAMILY Level (128 базовые + 21 компонент = 149 функций - 74.5%)
    static let familyFeatures: [AppFeature] = personalFeatures + familyComponents + [
        // Child Threats Protection (17)
        AppFeature(id: "inappropriate_content_filtering", name: "Фильтрация неприемлемого контента", description: "Блокировка вредного контента для детей", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "bullying_detection", name: "Обнаружение буллинга", description: "Мониторинг травли в сети", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "predator_detection", name: "Обнаружение хищников", description: "Защита от опасных контактов", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "grooming_prevention", name: "Предотвращение grooming", description: "Защита от онлайн-груминга", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "sexting_detection", name: "Обнаружение sexting", description: "Мониторинг опасных сообщений", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "cyberbullying_alerts", name: "Предупреждения о кибербуллинге", description: "Оповещения о травле", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "inappropriate_apps_blocking", name: "Блокировка неподходящих приложений", description: "Контроль установленных приложений", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "gambling_sites_blocking", name: "Блокировка сайтов азартных игр", description: "Защита от игровых сайтов", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "adult_content_filtering", name: "Фильтрация взрослого контента", description: "Блокировка 18+ материалов", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "violence_content_blocking", name: "Блокировка контента с насилием", description: "Защита от агрессивного контента", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "hate_speech_detection", name: "Обнаружение hate speech", description: "Фильтрация разжигающего ненависть контента", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "self_harm_content_filtering", name: "Фильтрация контента о self-harm", description: "Защита от опасного контента", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "suicide_prevention_alerts", name: "Предупреждения о суициде", description: "Мониторинг опасных тем", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "eating_disorders_monitoring", name: "Мониторинг расстройств пищевого поведения", description: "Защита от опасного контента", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "drug_abuse_detection", name: "Обнаружение drug abuse", description: "Мониторинг наркотической тематики", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "alcohol_abuse_monitoring", name: "Мониторинг alcohol abuse", description: "Защита от алкогольной тематики", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),
        AppFeature(id: "pornography_blocking", name: "Блокировка порнографии", description: "Полная защита от adult контента", requiredLevel: .family, category: .threatProtection, module: .childThreats, isEnabled: true),

        // Parental Control - Basic (20)
        AppFeature(id: "basic_content_filtering", name: "Базовая фильтрация контента", description: "Основная защита от вредного контента", requiredLevel: .family, category: .parentalControl, module: .contentFiltering, isEnabled: true),
        AppFeature(id: "time_limits_setup", name: "Установка лимитов времени", description: "Контроль времени использования устройств", requiredLevel: .family, category: .parentalControl, module: .timeManagement, isEnabled: true),
        AppFeature(id: "screen_time_monitoring", name: "Мониторинг screen time", description: "Отслеживание времени за экраном", requiredLevel: .family, category: .parentalControl, module: .timeManagement, isEnabled: true),
        AppFeature(id: "app_usage_tracking", name: "Отслеживание использования приложений", description: "Мониторинг активности в приложениях", requiredLevel: .family, category: .parentalControl, module: .activityMonitoring, isEnabled: true),
        AppFeature(id: "website_visits_logging", name: "Логирование посещений сайтов", description: "Журнал посещенных веб-ресурсов", requiredLevel: .family, category: .parentalControl, module: .activityMonitoring, isEnabled: true),
        AppFeature(id: "location_tracking", name: "Отслеживание местоположения", description: "Мониторинг геолокации устройств", requiredLevel: .family, category: .parentalControl, module: .locationTracking, isEnabled: true),
        AppFeature(id: "geofence_setup", name: "Настройка геозон", description: "Создание безопасных географических зон", requiredLevel: .family, category: .parentalControl, module: .locationTracking, isEnabled: true),
        AppFeature(id: "communication_monitoring", name: "Мониторинг коммуникаций", description: "Контроль сообщений и звонков", requiredLevel: .family, category: .parentalControl, module: .communicationControl, isEnabled: true),
        AppFeature(id: "contacts_whitelist", name: "Белый список контактов", description: "Разрешенные контакты для общения", requiredLevel: .family, category: .parentalControl, module: .communicationControl, isEnabled: true),
        AppFeature(id: "educational_apps_recommendations", name: "Рекомендации образовательных приложений", description: "Предложения полезных приложений", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "learning_progress_tracking", name: "Отслеживание прогресса обучения", description: "Мониторинг образовательной активности", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "emergency_contacts_setup", name: "Настройка экстренных контактов", description: "Контакты для чрезвычайных ситуаций", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "panic_button", name: "Кнопка паники", description: "Экстренный сигнал помощи", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_location_sharing", name: "Совместное использование местоположения", description: "Обмен геолокацией в семье", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_chat", name: "Семейный чат", description: "Безопасный чат для семьи", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "shared_family_calendar", name: "Общий семейный календарь", description: "Семейное расписание и события", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_media_sharing", name: "Совместное использование медиа", description: "Обмен фото и видео в семье", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_goals_tracking", name: "Отслеживание семейных целей", description: "Совместные достижения и цели", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_rewards_system", name: "Система семейных наград", description: "Мотивация для всей семьи", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_activity_reports", name: "Отчеты о семейной активности", description: "Сводки по активности семьи", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),

        // Additional FAMILY functions (to reach 59 total additional)
        AppFeature(id: "family_device_limits", name: "Лимиты устройств", description: "Ограничение количества устройств в семье", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_bandwidth_control", name: "Контроль трафика", description: "Управление использованием интернет-трафика", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_content_scheduling", name: "Расписание контента", description: "График доступа к контенту", requiredLevel: .family, category: .parentalControl, module: .contentFiltering, isEnabled: true),
        AppFeature(id: "family_educational_goals", name: "Образовательные цели", description: "Установка учебных целей для детей", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "family_progress_tracking", name: "Отслеживание прогресса", description: "Мониторинг достижения целей", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "family_achievement_rewards", name: "Награды за достижения", description: "Система поощрений", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "family_learning_analytics", name: "Аналитика обучения", description: "Статистика образовательной активности", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "family_skill_assessment", name: "Оценка навыков", description: "Тестирование знаний и навыков", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "family_custom_lessons", name: "Индивидуальные уроки", description: "Персонализированные обучающие материалы", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "family_educational_reports", name: "Образовательные отчеты", description: "Подробные отчеты об обучении", requiredLevel: .family, category: .parentalControl, module: .educationalTools, isEnabled: true),
        AppFeature(id: "family_emergency_protocols", name: "Протоколы ЧС", description: "Планы действий при чрезвычайных ситуациях", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_safety_drills", name: "Тренировки безопасности", description: "Регулярные учения по безопасности", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_emergency_alerts", name: "Экстренные оповещения", description: "Срочные уведомления для семьи", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_medical_alerts", name: "Медицинские оповещения", description: "Здравоохранные предупреждения", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_weather_alerts", name: "Погодные предупреждения", description: "Оповещения о неблагоприятных погодных условиях", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_community_alerts", name: "Общественные предупреждения", description: "Информация о местных событиях", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_backup_communication", name: "Резервная связь", description: "Альтернативные способы коммуникации", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_emergency_kit_tracking", name: "Отслеживание аварийного набора", description: "Контроль наличия необходимых вещей", requiredLevel: .family, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "family_meeting_scheduler", name: "Планировщик встреч", description: "Организация семейных собраний", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_event_planner", name: "Планировщик событий", description: "Организация семейных мероприятий", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_memory_book", name: "Семейная книга воспоминаний", description: "Сбор и хранение семейных историй", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "family_tradition_tracker", name: "Отслеживание традиций", description: "Напоминания о семейных традициях", requiredLevel: .family, category: .parentalControl, module: .familySharing, isEnabled: true)
    ]

    // MARK: - FAMILY COMPONENTS (21 компонент - FAMILY + PREMIUM)
    static let familyComponents: [AppFeature] = [
        // Сетевая защита (4 компонента)
        AppFeature(id: "phishing_protection_agent", name: "Защита от фишинга", description: "Специализированная защита от фишинговых атак", requiredLevel: .family, category: .premiumComponents, module: .advancedThreatProtection, isEnabled: true),
        AppFeature(id: "malware_detection_agent", name: "Обнаружение malware", description: "Продвинутый детектор вредоносного ПО", requiredLevel: .family, category: .premiumComponents, module: .advancedThreatProtection, isEnabled: true),
        AppFeature(id: "mobile_security_agent", name: "Мобильная безопасность", description: "Комплексная защита мобильных устройств", requiredLevel: .family, category: .premiumComponents, module: .advancedThreatProtection, isEnabled: true),
        AppFeature(id: "network_security_agent", name: "Сетевая безопасность", description: "Защита сетевых соединений и трафика", requiredLevel: .family, category: .premiumComponents, module: .advancedThreatProtection, isEnabled: true),

        // Родительский контроль (5 компонентов)
        AppFeature(id: "self_harm_detection_agent", name: "Self-harm Detection", description: "Обнаруживает контент о самоповреждении", requiredLevel: .family, category: .premiumComponents, module: .coreManagers, isEnabled: true),
        AppFeature(id: "grooming_detection_agent", name: "Grooming Detection", description: "Предотвращает онлайн-груминг", requiredLevel: .family, category: .premiumComponents, module: .coreManagers, isEnabled: true),
        AppFeature(id: "online_predators_agent", name: "Online Predators Protection", description: "Защищает от хищников в сети", requiredLevel: .family, category: .premiumComponents, module: .coreManagers, isEnabled: true),
        AppFeature(id: "psychological_support_agent", name: "Psychological Support", description: "Предоставляет психологическую помощь", requiredLevel: .family, category: .premiumComponents, module: .coreManagers, isEnabled: true),
        AppFeature(id: "parental_control_bot", name: "Parental Control Bot", description: "Основной бот родительского контроля", requiredLevel: .family, category: .premiumComponents, module: .coreManagers, isEnabled: true),

        // Мессенджеры (6 компонентов)
        AppFeature(id: "telegram_security_bot", name: "Telegram Security Bot", description: "Защищает от угроз в Telegram", requiredLevel: .family, category: .premiumComponents, module: .messagingApps, isEnabled: true),
        AppFeature(id: "whatsapp_security_bot", name: "WhatsApp Security Bot", description: "Обеспечивает безопасность WhatsApp", requiredLevel: .family, category: .premiumComponents, module: .messagingApps, isEnabled: true),
        AppFeature(id: "instagram_security_bot", name: "Instagram Security Bot", description: "Фильтрует угрозы в Instagram", requiredLevel: .family, category: .premiumComponents, module: .messagingApps, isEnabled: true),
        AppFeature(id: "max_messenger_security_bot", name: "Max Messenger Security", description: "Защищает Max Messenger", requiredLevel: .family, category: .premiumComponents, module: .messagingApps, isEnabled: true),
        AppFeature(id: "gaming_security_bot", name: "Gaming Security Bot", description: "Предотвращает угрозы в онлайн-играх", requiredLevel: .family, category: .premiumComponents, module: .messagingApps, isEnabled: true),
        AppFeature(id: "browser_security_bot", name: "Browser Security Bot", description: "Защищает веб-браузер", requiredLevel: .family, category: .premiumComponents, module: .messagingApps, isEnabled: true),

        // Приватность (1 компонент)
        AppFeature(id: "location_bubble_agent", name: "Location Bubble", description: "Скрывает точное местоположение пользователя", requiredLevel: .family, category: .premiumComponents, module: .advancedThreatProtection, isEnabled: true),

        // Регуляторные (2 компонента)
        AppFeature(id: "russian_child_protection_manager", name: "Защита детей РФ", description: "Соответствие закону о защите детей", requiredLevel: .family, category: .premiumComponents, module: .messagingApps, isEnabled: true),
        AppFeature(id: "russian_data_protection_manager", name: "Защита данных РФ", description: "Соблюдение законов о данных", requiredLevel: .family, category: .premiumComponents, module: .messagingApps, isEnabled: true),

        // Интерфейсы (3 компонента)
        AppFeature(id: "family_notification_manager", name: "Семейные уведомления", description: "Управляет семейными уведомлениями", requiredLevel: .family, category: .premiumComponents, module: .privacyMonitoring, isEnabled: true),
        AppFeature(id: "child_interface_manager", name: "Детский интерфейс", description: "Адаптирует интерфейс для детей", requiredLevel: .family, category: .premiumComponents, module: .privacyMonitoring, isEnabled: true),
        AppFeature(id: "elderly_interface_manager", name: "Интерфейс для пожилых", description: "Оптимизирует интерфейс для пожилых", requiredLevel: .family, category: .premiumComponents, module: .privacyMonitoring, isEnabled: true)
    ]

    // MARK: - PREMIUM COMPONENTS (21 компонент - PREMIUM ONLY)
    static let premiumOnlyComponents: [AppFeature] = [
        // Экстренная помощь (10 компонентов) - ТОЛЬКО PREMIUM
        AppFeature(id: "crash_detection_agent", name: "Обнаружение аварий", description: "Автоматически обнаруживает аварии по датчикам и вызывает помощь", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "roadside_assistance_agent", name: "Дорожная помощь", description: "Организует эвакуацию и помощь при поломке автомобиля", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "emergency_response_bot", name: "Экстренный бот", description: "Координирует действия в чрезвычайных ситуациях", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "emergency_event_manager", name: "Менеджер экстренных событий", description: "Управляет всеми экстренными событиями и инцидентами", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "incident_response_agent", name: "Агент реагирования на инциденты", description: "Автоматически реагирует на обнаруженные угрозы безопасности", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "password_security_agent", name: "Агент безопасности паролей", description: "Генерирует и проверяет надежность паролей", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "emergency_contact_manager", name: "Менеджер экстренных контактов", description: "Управляет базой экстренных контактов", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "emergency_notification_manager", name: "Менеджер экстренных уведомлений", description: "Настраивает шаблоны экстренных уведомлений", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "voice_control_manager", name: "Голосовое управление", description: "Предоставляет голосовое управление устройством", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),
        AppFeature(id: "smart_notification_manager", name: "Умные уведомления", description: "Интеллектуально управляет уведомлениями", requiredLevel: .premium, category: .premiumComponents, module: .emergencyAssistance, isEnabled: true),

        // Расширенная приватность (8 компонентов) - ТОЛЬКО PREMIUM
        AppFeature(id: "personal_data_cleanup_agent", name: "Очистка персональных данных", description: "Автоматически очищает персональные данные из сети", requiredLevel: .premium, category: .premiumComponents, module: .privacyMonitoring, isEnabled: true),
        AppFeature(id: "dark_web_monitoring_agent", name: "Мониторинг Dark Web", description: "Мониторит упоминания данных в даркнете", requiredLevel: .premium, category: .premiumComponents, module: .privacyMonitoring, isEnabled: true),
        AppFeature(id: "russian_identity_theft_protection_agent", name: "Защита от кражи личности РФ", description: "Защищает от кражи документов в РФ", requiredLevel: .premium, category: .premiumComponents, module: .privacyMonitoring, isEnabled: true),
        AppFeature(id: "ai_categories_agent", name: "AI категоризация", description: "ИИ анализирует и категоризирует угрозы", requiredLevel: .premium, category: .premiumComponents, module: .privacyMonitoring, isEnabled: true),
        AppFeature(id: "driving_reports_agent", name: "Отчеты о вождении", description: "Анализирует стиль вождения и предоставляет отчеты", requiredLevel: .premium, category: .premiumComponents, module: .privacyMonitoring, isEnabled: true),
        AppFeature(id: "anti_tracker_agent", name: "Анти-трекер", description: "Блокирует трекеры и сбор персональных данных", requiredLevel: .premium, category: .premiumComponents, module: .advancedThreatProtection, isEnabled: true),

        // Расширенная аналитика (3 компонента) - ТОЛЬКО PREMIUM
        AppFeature(id: "analytics_manager", name: "Analytics Manager", description: "Анализирует использование и безопасность", requiredLevel: .premium, category: .premiumComponents, module: .messagingApps, isEnabled: true),
        AppFeature(id: "report_manager", name: "Report Manager", description: "Генерирует детальные отчеты о безопасности", requiredLevel: .premium, category: .premiumComponents, module: .messagingApps, isEnabled: true)
    ]

    // MARK: - PREMIUM Level (128 базовые + 42 компонента + 30 расширенных = 200 функций - 100%)
    static let premiumFeatures: [AppFeature] = familyFeatures + premiumOnlyComponents + [
        // Deepfakes Protection (8) - базовые
        AppFeature(id: "deepfake_video_detection", name: "Обнаружение deepfake видео", description: "Идентификация поддельных видео", requiredLevel: .premium, category: .threatProtection, module: .deepfakes, isEnabled: true),
        AppFeature(id: "deepfake_audio_analysis", name: "Анализ deepfake аудио", description: "Проверка подлинности аудио", requiredLevel: .premium, category: .threatProtection, module: .deepfakes, isEnabled: true),
        AppFeature(id: "ai_generated_content_detection", name: "Обнаружение AI-generated контента", description: "Идентификация ИИ-сгенерированного контента", requiredLevel: .premium, category: .threatProtection, module: .deepfakes, isEnabled: true),
        AppFeature(id: "face_manipulation_detection", name: "Обнаружение манипуляций с лицом", description: "Защита от face swap", requiredLevel: .premium, category: .threatProtection, module: .deepfakes, isEnabled: true),
        AppFeature(id: "voice_cloning_protection", name: "Защита от voice cloning", description: "Предотвращение клонирования голоса", requiredLevel: .premium, category: .threatProtection, module: .deepfakes, isEnabled: true),
        AppFeature(id: "deepfake_social_media_monitoring", name: "Мониторинг deepfake в соцсетях", description: "Поиск подделок в социальных сетях", requiredLevel: .premium, category: .threatProtection, module: .deepfakes, isEnabled: true),
        AppFeature(id: "political_deepfake_detection", name: "Обнаружение политических deepfake", description: "Защита от дезинформации", requiredLevel: .premium, category: .threatProtection, module: .deepfakes, isEnabled: true),
        AppFeature(id: "celebrity_deepfake_protection", name: "Защита от celebrity deepfake", description: "Защита знаменитостей от подделок", requiredLevel: .premium, category: .threatProtection, module: .deepfakes, isEnabled: true),

        // IoT Threats Protection (10) - базовые
        AppFeature(id: "smart_home_device_security", name: "Безопасность умного дома", description: "Защита IoT устройств", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_firmware_updates", name: "Обновления firmware IoT", description: "Автоматические обновления безопасности", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_device_authentication", name: "Аутентификация IoT устройств", description: "Проверка подлинности устройств", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_network_segmentation", name: "Сегментация IoT сети", description: "Изоляция IoT устройств", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_vulnerability_scanning", name: "Сканирование уязвимостей IoT", description: "Проверка безопасности устройств", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_encryption_monitoring", name: "Мониторинг шифрования IoT", description: "Контроль шифрования данных", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_remote_access_control", name: "Контроль удаленного доступа IoT", description: "Управление доступом к устройствам", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_threat_intelligence", name: "IoT threat intelligence", description: "Аналитика угроз для IoT", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_behavioral_analysis", name: "Поведенческий анализ IoT", description: "Мониторинг аномального поведения", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),
        AppFeature(id: "iot_emergency_response", name: "Аварийный отклик IoT", description: "Экстренные меры безопасности", requiredLevel: .premium, category: .threatProtection, module: .iotThreats, isEnabled: true),

        // Premium Parental Control (4) - базовые
        AppFeature(id: "advanced_content_filtering", name: "Расширенная фильтрация контента", description: "ИИ-powered фильтрация с машинным обучением", requiredLevel: .premium, category: .parentalControl, module: .contentFiltering, isEnabled: true),
        AppFeature(id: "real_time_content_monitoring", name: "Мониторинг контента в реальном времени", description: "Непрерывный анализ контента", requiredLevel: .premium, category: .parentalControl, module: .contentFiltering, isEnabled: true),
        AppFeature(id: "ai_content_classification", name: "AI классификация контента", description: "Автоматическая категоризация", requiredLevel: .premium, category: .parentalControl, module: .contentFiltering, isEnabled: true),
        AppFeature(id: "premium_family_analytics", name: "Премиум семейная аналитика", description: "Расширенные отчеты по семье", requiredLevel: .premium, category: .additionalFeatures, module: .analytics, isEnabled: true)
    ]

    // MARK: - TRIAL Level (114 functions - 80% of premium)
    static let trialFeatures: [AppFeature] = freeFeatures + personalFeatures + [
        // Trial gets most FAMILY features for demo (80% coverage)
        AppFeature(id: "trial_family_monitoring", name: "Семейный мониторинг (trial)", description: "Базовый семейный контроль в trial периоде", requiredLevel: .trial, category: .threatProtection, module: .familyThreats, isEnabled: true),
        AppFeature(id: "trial_content_filtering", name: "Фильтрация контента (trial)", description: "Базовая защита контента в trial", requiredLevel: .trial, category: .parentalControl, module: .contentFiltering, isEnabled: true),
        AppFeature(id: "trial_time_management", name: "Управление временем (trial)", description: "Базовое управление временем в trial", requiredLevel: .trial, category: .parentalControl, module: .timeManagement, isEnabled: true),
        AppFeature(id: "trial_location_tracking", name: "Отслеживание местоположения (trial)", description: "Базовое отслеживание геолокации", requiredLevel: .trial, category: .parentalControl, module: .locationTracking, isEnabled: true),
        AppFeature(id: "trial_communication_control", name: "Контроль коммуникаций (trial)", description: "Базовый контроль общения", requiredLevel: .trial, category: .parentalControl, module: .communicationControl, isEnabled: true),
        AppFeature(id: "trial_family_sharing", name: "Семейное взаимодействие (trial)", description: "Базовые семейные функции", requiredLevel: .trial, category: .parentalControl, module: .familySharing, isEnabled: true),
        AppFeature(id: "trial_emergency_features", name: "Экстренные функции (trial)", description: "Базовые функции безопасности", requiredLevel: .trial, category: .parentalControl, module: .emergencyFeatures, isEnabled: true),
        AppFeature(id: "trial_educational_tools", name: "Образовательные инструменты (trial)", description: "Базовые образовательные функции", requiredLevel: .trial, category: .parentalControl, module: .educationalTools, isEnabled: true)
    ]

    // MARK: - Access Methods

    /// Get all features for subscription level
    static func features(for level: SubscriptionLevel) -> [AppFeature] {
        switch level {
        case .trial: return trialFeatures
        case .free: return freeFeatures
        case .personal: return personalFeatures
        case .family: return familyFeatures
        case .premium: return premiumFeatures
        }
    }

    /// Check if feature is available for level
    static func isFeatureAvailable(_ featureId: String, for level: SubscriptionLevel) -> Bool {
        let levelFeatures = features(for: level)
        return levelFeatures.contains { $0.id == featureId }
    }

    /// Get feature by ID
    static func feature(byId id: String) -> AppFeature? {
        // Search through all levels
        let allFeatures = trialFeatures + freeFeatures + personalFeatures + familyFeatures + premiumFeatures
        return allFeatures.first { $0.id == id }
    }

    /// Count features by level
    static func featureCount(for level: SubscriptionLevel) -> Int {
        return features(for: level).count
    }

    /// Get features by category and level
    static func features(for level: SubscriptionLevel, in category: FeatureCategory) -> [AppFeature] {
        return features(for: level).filter { $0.category == category }
    }

    // MARK: - Statistics & Validation

    /// Validate total function count (should be 184)
    static func validateTotalFunctionCount() -> Bool {
        let totalPremium = premiumFeatures.count
        return totalPremium == 184 // 142 базовые + 42 компонента
    }

    /// Get detailed breakdown by level and category
    static func getDetailedBreakdown() -> [String: [String: Int]] {
        var breakdown: [String: [String: Int]] = [:]

        for level in SubscriptionLevel.allCases {
            var levelStats: [String: Int] = [:]
            let levelFeatures = features(for: level)

            // By category
            for category in FeatureCategory.allCases {
                let count = levelFeatures.filter { $0.category == category }.count
                levelStats[category.rawValue] = count
            }

            // Total
            levelStats["total"] = levelFeatures.count

            breakdown[level.rawValue] = levelStats
        }

        return breakdown
    }

    /// Verify distribution matches specification
    static func verifyDistribution() -> [String: Bool] {
        var results: [String: Bool] = [:]

        // Check total counts
        results["trial_total"] = trialFeatures.count >= 114 // 80% minimum
        results["free_total"] = freeFeatures.count == 26     // Exactly 26
        results["personal_total"] = personalFeatures.count == 69 // Exactly 69
        results["family_total"] = familyFeatures.count >= 128  // 90% minimum
        results["premium_total"] = premiumFeatures.count == 184 // Exactly 184

        // Check component distribution
        let premiumComponentsCount = premiumOnlyComponents.count
        results["premium_components"] = premiumComponentsCount == 42

        // Check progressive access (higher levels include lower levels)
        results["progressive_free_to_personal"] = personalFeatures.count >= freeFeatures.count
        results["progressive_personal_to_family"] = familyFeatures.count >= personalFeatures.count
        results["progressive_family_to_premium"] = premiumFeatures.count >= familyFeatures.count

        return results
    }
}