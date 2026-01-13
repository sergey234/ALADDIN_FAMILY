import Foundation
import SwiftUI

/**
 * 📦 API Models
 * Модели данных для API запросов и ответов
 * Соответствуют структуре вашего Python backend
 */

// MARK: - Network Protection Models

struct NetworkProtectionStatusResponse: Codable {
    let isConnected: Bool
    let serverLocation: String
    let ipAddress: String
    let ping: Int
    let downloadSpeed: String
    let uploadSpeed: String
    let sessionTime: String
    let threatsBlocked: Int
}

struct NetworkProtectionServer: Codable, Identifiable {
    let id: String
    let country: String
    let city: String
    let flag: String
    let ping: Int
    let load: Int // 0-100%
    let status: ServerStatus
    
    func localizedName(_ localizationManager: LocalizationManager) -> String {
        // Локализуем название страны
        let key = "network_protection_server_\(country.lowercased())"
        let localized = localizationManager.localized(key)
        // Если локализация не найдена, возвращаем оригинальное название
        return localized != key ? localized : country
    }
    
    var name: String {
        country // Только страна (для обратной совместимости)
    }
    
    var location: String {
        "\(city)" // Только город
    }
}

enum ServerStatus: String, Codable, CaseIterable {
    case optimal = "optimal"
    case loaded = "loaded"
}

// MARK: - Network Protection Stats Models

struct NetworkProtectionStats: Codable {
    let bytesIn: Int64
    let bytesOut: Int64
    let packetsIn: Int64
    let packetsOut: Int64
    let today: Int64
    let thisMonth: Int64
    let sessionTime: TimeInterval
    let threatsBlocked: Int
}

struct NetworkProtectionConfigResponse: Codable {
    let encryption: EncryptionConfig
    let servers: [NetworkProtectionServer]
    let features: NetworkProtectionFeatures
    let settings: NetworkProtectionSettings
}

struct EncryptionConfig: Codable {
    let algorithm: String // "AES-128" or "AES-256-GCM"
    let keySize: Int
    let recommendedLevel: String // "light", "normal", "maximum"
}

struct NetworkProtectionFeatures: Codable {
    let killSwitch: Bool
    let autoConnect: Bool
    let dnsLeakProtection: Bool
    let splitTunneling: Bool
}

struct NetworkProtectionSettings: Codable {
    let autoDisconnectEnabled: Bool
    let autoDisconnectTimeout: TimeInterval
    let batteryOptimizationEnabled: Bool
}

// MARK: - Family Models

struct CreateFamilyResponse: Codable {
    let success: Bool
    let family_id: String
    let recovery_code: String
    let members: [FamilyMemberResponse]
    let your_member_id: String
}

struct JoinFamilyResponse: Codable {
    let success: Bool
    let family_id: String
    let members: [FamilyMemberResponse]
    let your_member_id: String
}

struct FamilyMemberResponse: Codable, Identifiable {
    let id: String
    let name: String
    let role: String // "parent", "child", "teenager", "elderly"
    let avatar: String
    let status: String // "protected", "warning", "danger", "offline"
    let threatsBlocked: Int
    let lastActive: String
    let devices: Int
}

struct FamilyStatsResponse: Codable {
    let totalMembers: Int
    let totalDevices: Int
    let totalThreats: Int
    let protectionLevel: Int
    let familyStatus: String?
    let familyStatusMessage: String?
}

// MARK: - Analytics Models

struct AnalyticsResponse: Codable {
    let period: String // "day", "week", "month"
    let threatsDetected: Int
    let threatsBlocked: Int
    let itemsScanned: Int
    let protectionLevel: Int
    let topThreats: [ThreatItem]
    let threatsByType: [ThreatByType]
}

struct ThreatItem: Codable, Identifiable {
    let id: String
    let name: String
    let count: Int
    let icon: String
    let severity: String // "low", "medium", "high", "critical"
}

struct ThreatByType: Codable {
    let type: String // "web", "app", "network", "file"
    let count: Int
    let percentage: Double
}

// MARK: - AI Assistant Models

struct ChatMessageRequest: Codable {
    let message: String
    let userId: String
    let timestamp: Date
}

struct ChatMessageResponse: Codable {
    let message: String
    let timestamp: Date
    let suggestions: [String]?
}

// MARK: - User Models

// MARK: - Token Refresh Models

struct RefreshTokenResponse: Codable {
    let access_token: String
    let refresh_token: String?
    let expires_in: TimeInterval?
    let token_type: String?
}

struct UserProfile: Codable {
    let id: String
    let name: String
    let email: String
    let phone: String?
    let registrationDate: String
    let subscriptionType: String
    let subscriptionEndDate: String?
    let threatsBlocked: Int
    let familyMembers: Int
    let devices: Int
}

struct UpdateProfileRequest: Codable {
    let name: String?
    let email: String?
    let phone: String?
}

// MARK: - Parental Control Models

struct ParentalControlSettings: Codable {
    let childId: String
    let isContentFilterEnabled: Bool
    let isAppBlockingEnabled: Bool
    let screenTimeLimitHours: Int
    let allowedApps: [String]
    let blockedWebsites: [String]
    let bedtime: String? // "22:00"
}

struct ChildStatsResponse: Codable {
    let screenTimeToday: String
    let blockedSitesToday: Int
    let allowedAppsCount: Int
    let timeRemaining: String
}

// MARK: - Bypass Protection Models

enum BypassType: String {
    case incognito = "incognito"  // Внутренний код
    case tor = "tor"
    case proxy = "proxy"
    
    var displayName: String {  // НОВОЕ свойство для UI
        switch self {
        case .incognito: return "Скрытый режим"  // Простое название
        case .tor: return "Tor"
        case .proxy: return "Proxy"
        }
    }
    
    var icon: String {
        switch self {
        case .incognito: return "🕶️"
        case .tor: return "🧅"
        case .proxy: return "🔀"
        }
    }
}

struct BypassStatsResponse: Codable {
    let success: Bool
    let today: Int
    let week: Int
    let blocked: Int
    let incognito: Int
    let tor: Int
    let proxy: Int
    let message: String?
}

// MARK: - Notifications Models

struct NotificationResponse: Codable, Identifiable {
    let id: String
    let icon: String
    let title: String
    let message: String
    let timestamp: Date
    let isRead: Bool
    let type: String // "threat", "success", "info", "warning"
    let priority: String? // "high", "medium", "low" (optional для обратной совместимости)
    let actionRequired: Bool?
    let actionUrl: String?
    let metadata: [String: String]?
    
    // Приоритет по умолчанию на основе типа
    var defaultPriority: NotificationPriority {
        if let priority = priority {
            return NotificationPriority(from: priority)
        }
        // Приоритет по умолчанию на основе типа
        switch type.lowercased() {
        case "threat", "security_alert", "threat_detected", "emergency":
            return .high
        case "warning", "subscription_expiring", "subscription_expired":
            return .medium
        case "success", "payment_success", "subscription_activated", "referral_reward":
            return .low
        default:
            return .low
        }
    }
}

enum NotificationPriority: String, Codable {
    case high = "high"
    case medium = "medium"
    case low = "low"
    
    init(from string: String) {
        switch string.lowercased() {
        case "high": self = .high
        case "medium": self = .medium
        default: self = .low
        }
    }
}

// MARK: - Subscription Models

struct TariffResponse: Codable, Identifiable {
    let id: String
    let name: String
    let price: Int
    let period: String
    let features: [String]
    let isRecommended: Bool
}

struct SubscriptionStatus: Codable {
    let isActive: Bool
    let tariffId: String
    let startDate: Date
    let endDate: Date
    let autoRenew: Bool
}

struct ActivationCodeRequest: Codable {
    let code: String
}

struct ActivationCodeResponse: Codable {
    let status: String
    let message: String?
    let planName: String?
    let expiresAt: String?
    let familyId: String?
}

// MARK: - Activation Code Models (новые для payment_service)

// Запрос на проверку кода
struct ActivationVerifyRequest: Codable {
    let code: String
    let familyId: String
    let deviceId: String
}

// Ответ на проверку кода
struct ActivationVerifyResponse: Codable {
    let tariffId: String
    let status: String  // "pending", "active", "redeemed", "expired"
    let expiresAt: String  // ISO 8601 format
}

// Запрос на активацию кода
struct ActivationActivateRequest: Codable {
    let code: String
    let familyId: String
    let deviceId: String
}

// Ответ на активацию кода
struct ActivationActivateResponse: Codable {
    let success: Bool
    let tariffId: String
    let expiresAt: String  // ISO 8601 format
}

// MARK: - Auth Models

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct LoginResponse: Codable {
    let token: String
    let userId: String
    let expiresAt: Date
}

struct RegisterRequest: Codable {
    let name: String
    let email: String
    let password: String
    let phone: String?
}

// MARK: - Payment Models

struct CreateQRPaymentRequest: Codable {
    let amount: Double
    let currency: String
    let description: String
    let tariffId: String?
    let periodMonths: Int?  // Период подписки: 1, 3, 6, 12 месяцев
}

struct CreateQRPaymentResponse: Codable {
    let paymentId: String
    let qrCode: String
    let amount: Double
    let currency: String
    let expiresAt: Date
    let status: String
}

struct CheckQRPaymentStatusResponse: Codable {
    let paymentId: String
    let status: String // "pending", "completed", "failed", "expired"
    let amount: Double
    let currency: String
    let completedAt: Date?
}

// MARK: - Generic Response

struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let message: String?
    let error: String?
}

// MARK: - Notification UI Models

struct NotificationItem: Identifiable {
    let id: String
    let icon: String
    let title: String
    let message: String
    let time: String
    var isRead: Bool
    let type: NotificationType
    let timestamp: Date
    let actionRequired: Bool
    let actionURL: String?
    
    init(id: String,
         icon: String,
         title: String,
         message: String,
         time: String,
         isRead: Bool,
         type: NotificationType,
         timestamp: Date,
         actionRequired: Bool = false,
         actionURL: String? = nil) {
        self.id = id
        self.icon = icon
        self.title = title
        self.message = message
        self.time = time
        self.isRead = isRead
        self.type = type
        self.timestamp = timestamp
        self.actionRequired = actionRequired
        self.actionURL = actionURL
    }
}

enum NotificationType: String, CaseIterable {
    case threat = "Угроза"
    case success = "Успех"
    case info = "Информация"
    case warning = "Предупреждение"
    case bypassAttempt = "Обход"
    
    var color: Color {
        switch self {
        case .threat: return .red
        case .success: return .green
        case .info: return .blue
        case .warning: return .orange
        case .bypassAttempt: return .warningOrange
        }
    }
}

// MARK: - Parental Control API Models

// Блокировка контента
struct ApplyBlockingRequest: Codable {
    let childId: String
    let type: BlockingType
    let enabled: Bool
}

enum BlockingType: String, Codable {
    case website
    case app
    case search
    case safesearch
}

// Применение правил блокировки
struct ApplyParentalControlRulesRequest: Codable {
    let childId: String
    let ageGroup: String // "1-6", "7-13", "14-17", "18+"
    let rules: ParentalControlRules
}

struct ParentalControlRules: Codable {
    let websiteBlocking: Bool
    let appBlocking: Bool
    let searchBlocking: Bool
    let safesearch: Bool
    let screenTimeLimit: Int? // минуты
    let bedtimeStart: String? // "HH:mm"
    let bedtimeEnd: String? // "HH:mm"
    let appLimits: [AppLimit]?
    let geofences: [GeofenceAPI]?
}

struct AppLimit: Codable {
    let app: String
    let limit: Double // минуты в день
}

struct GeofenceAPI: Codable {
    let name: String
    let address: String
    let latitude: Double
    let longitude: Double
    let radius: Double // метры
}

// Запросы доступа
struct AccessRequestResponse: Codable, Identifiable {
    let id: String
    let childId: String
    let app: String
    let time: String
    let reason: String
    let limit: String
    let status: AccessRequestStatus
}

enum AccessRequestStatus: String, Codable {
    case pending
    case accepted
    case rejected
    case expired
}

struct HandleAccessRequestRequest: Codable {
    let requestId: String
    let action: String // "accept" или "reject"
    let reason: String? // опциональная причина отклонения
}

// Статистика родительского контроля
struct ParentalControlStatsResponse: Codable {
    let contentBlocked: ContentBlockedStats
    let screenTime: ScreenTimeStats
    let location: LocationStats
    let monitoring: MonitoringStats
}

struct ContentBlockedStats: Codable {
    let websitesBlocked: Int
    let appsBlocked: Int
    let searchQueriesBlocked: Int
    let activeFilters: Int
}

struct ScreenTimeStats: Codable {
    let todayUsage: String // "1ч 24мин"
    let todayLimit: String // "2ч"
    let remaining: String // "36мин"
    let schedulesCount: Int
}

struct LocationStats: Codable {
    let currentLocation: String?
    let lastUpdate: String?
    let geofencesCount: Int
    let eventsToday: Int
}

struct MonitoringStats: Codable {
    let sitesTracked: Int
    let appsTracked: Int
    let contactsTracked: Int
    let messagesMonitored: Bool
    let screenshotsEnabled: Bool
}

// История браузера/приложений
struct BrowserHistoryItemResponse: Codable, Identifiable {
    let id: String
    let url: String
    let title: String
    let timestamp: Date
    let category: String?
    let isBlocked: Bool
}

struct AppHistoryItemResponse: Codable, Identifiable {
    let id: String
    let app: String
    let usage: String // "15 мин"
    let timestamp: Date
    let limit: String?
    let exceeded: Bool
}

// Отчёты
struct WeeklyReportResponse: Codable {
    let weekStart: Date
    let weekEnd: Date
    let totalScreenTime: String
    let appsUsed: [AppUsageReport]
    let sitesVisited: [SiteVisitReport]
    let threatsDetected: Int
    let rulesTriggered: Int
}

struct AppUsageReport: Codable {
    let app: String
    let totalTime: String
    let sessions: Int
    let limit: String?
    let exceeded: Bool
}

struct SiteVisitReport: Codable {
    let site: String
    let visits: Int
    let category: String?
    let isBlocked: Bool
}

// MARK: - Device Models

struct DeviceResponse: Codable, Identifiable {
    let id: String
    let name: String
    let owner: String
    let type: String // "iphone", "mac", "ipad", "android"
    let status: String // "protected", "warning", "danger", "inactive"
    let lastActive: String
}

struct DeviceDetailResponse: Codable {
    let id: String
    let name: String
    let owner: String
    let type: String
    let status: String
    let lastActive: String
    let ipAddress: String?
    let osVersion: String?
    let appVersion: String?
    let threatsBlocked: Int
    let dataUsage: Int64 // bytes
    let batteryLevel: Int? // 0-100%
    let isProtected: Bool
}

// MARK: - Family Chat Models

struct FamilyChatMessageResponse: Codable, Identifiable {
    let id: String
    let sender: String
    let text: String?
    let timestamp: String
    let isCurrentUser: Bool
    let messageType: String? // "text", "voice", "image", "video"
    let voiceUrl: String? // URL голосового сообщения
    let voiceDuration: Double? // Длительность в секундах
    let mediaUrl: String? // URL медиа файла
    let mediaType: String? // Тип медиа
    let replyToMessageId: String? // ID сообщения, на которое отвечают
    let reactions: [MessageReaction]? // Реакции
    let readStatus: String? // "sent", "delivered", "read"
    let readAt: String? // Время прочтения
    let editedAt: String? // Время редактирования
}

struct MessageReaction: Codable {
    let emoji: String
    let userId: String
    let userName: String
}

struct SendFamilyChatMessageRequest: Codable {
    let message: String?
    let familyId: String?
    let messageType: String? // "text", "voice", "image", "video"
    let voiceUrl: String? // URL голосового сообщения
    let voiceDuration: Double? // Длительность в секундах
    let mediaUrl: String? // URL медиа файла
    let mediaType: String? // Тип медиа
    let replyToMessageId: String? // ID сообщения, на которое отвечают
}

struct SendFamilyChatMessageResponse: Codable {
    let success: Bool
    let messageId: String
}

// MARK: - Referral Models

struct ReferralOverviewResponse: Codable {
    let referralCode: String
    let referralURL: String?
    let qrCode: String?
    let invitationsCount: Int
    let earnedBonus: Double
    let invitedFriends: [ReferralFriendResponse]
    
    enum CodingKeys: String, CodingKey {
        case referralCode = "referral_code"
        case referralURL = "referral_url"
        case qrCode = "qr_code"
        case invitationsCount = "invitations_count"
        case earnedBonus = "earned_bonus"
        case invitedFriends = "invited_friends"
    }
}

struct ReferralFriendResponse: Codable, Identifiable {
    let friendId: String
    let status: String
    let createdAt: String
    let convertedAt: String?
    let rewardAmount: Double?
    
    var id: String { friendId }
    
    enum CodingKeys: String, CodingKey {
        case friendId = "friend_id"
        case status
        case createdAt = "created_at"
        case convertedAt = "converted_at"
        case rewardAmount = "reward_amount"
    }
}

struct ReferralStatsResponse: Codable {
    let totalReferrals: Int
    let convertedReferrals: Int
    let pendingReferrals: Int
    let totalRewards: Double
    let conversionRate: Double
    let referralTier: String
    let activeLinks: Int
    
    enum CodingKeys: String, CodingKey {
        case totalReferrals = "total_referrals"
        case convertedReferrals = "converted_referrals"
        case pendingReferrals = "pending_referrals"
        case totalRewards = "total_rewards"
        case conversionRate = "conversion_rate"
        case referralTier = "referral_tier"
        case activeLinks = "active_links"
    }
}

struct ReferralRewardsResponse: Codable {
    let totalConverted: Int
    let rewards: [ReferralRewardItem]
    
    enum CodingKeys: String, CodingKey {
        case totalConverted = "total_converted"
        case rewards
    }
}

struct ReferralRewardItem: Codable, Identifiable {
    let rewardId: String
    let titleKey: String
    let subtitleKey: String
    let amountKey: String
    let rewardValue: String
    let icon: String
    let requiredConverted: Int
    let status: String
    let remaining: Int
    let unlockedAt: String?
    
    var id: String { rewardId }
    
    enum CodingKeys: String, CodingKey {
        case rewardId = "reward_id"
        case titleKey = "title_key"
        case subtitleKey = "subtitle_key"
        case amountKey = "amount_key"
        case rewardValue = "reward_value"
        case icon
        case requiredConverted = "required_converted"
        case status
        case remaining
        case unlockedAt = "unlocked_at"
    }
}

// MARK: - IoT Models

struct IoTDevice: Codable, Identifiable {
    let id: String
    let name: String
    let type: IoTDeviceType
    let ip: String?
    let mac: String?
    let vendor: String?
    let model: String?
    let status: IoTDeviceStatus
    let lastSeen: String?
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case type
        case ip
        case mac
        case vendor
        case model
        case status
        case lastSeen = "last_seen"
    }
}

enum IoTDeviceType: String, Codable {
    case camera = "camera"
    case speaker = "speaker"
    case sensor = "sensor"
    case thermostat = "thermostat"
    case light = "light"
    case door = "door"
    case other = "other"
    
    // Расширенные типы устройств
    case smartLight = "smart_light"
    case smartOutlet = "smart_outlet"
    case smartCamera = "smart_camera"
    case smartLock = "smart_lock"
    case smartThermostat = "smart_thermostat"
    case smartTV = "smart_tv"
    case smartSpeaker = "smart_speaker"
    case unknown = "unknown"
    
    var displayName: String {
        switch self {
        case .camera: return "Камера"
        case .speaker: return "Колонка"
        case .sensor: return "Датчик"
        case .thermostat: return "Термостат"
        case .light: return "Лампа"
        case .door: return "Замок"
        case .other: return "Другое"
        case .smartLight: return "Умная лампа"
        case .smartOutlet: return "Умная розетка"
        case .smartCamera: return "Умная камера"
        case .smartLock: return "Умный замок"
        case .smartThermostat: return "Умный термостат"
        case .smartTV: return "Умный телевизор"
        case .smartSpeaker: return "Умная колонка"
        case .unknown: return "Неизвестно"
        }
    }
}

enum IoTDeviceStatus: String, Codable {
    case online = "online"
    case offline = "offline"
    case compromised = "compromised"
    case safe = "safe"
}

struct IoTThreat: Codable, Identifiable {
    let id: String
    let threatType: IoTThreatType
    let severity: ThreatSeverity
    let description: String
    let timestamp: String
    let deviceId: String?
    let recommendations: [String]?
    
    enum CodingKeys: String, CodingKey {
        case id
        case threatType = "threat_type"
        case severity
        case description
        case timestamp
        case deviceId = "device_id"
        case recommendations
    }
}

enum IoTThreatType: String, Codable {
    case cameraIntrusion = "camera_intrusion"
    case speakerEavesdropping = "speaker_eavesdropping"
    case weakPassword = "weak_password"
    case defaultCredentials = "default_credentials"
    case physicalTampering = "physical_tampering"
    case dataLeak = "data_leak"
    case unauthorizedAccess = "unauthorized_access"
    case camera
    case unknown = "unknown"
}

enum ThreatSeverity: String, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case critical = "critical"
}

struct IoTStatusResponse: Codable {
    let homeId: String
    let devices: [IoTDevice]?
    let threats: [IoTThreat]?
    let recommendations: [String]?
    let protectionLevel: Int?
    let lastScan: String?
    
    enum CodingKeys: String, CodingKey {
        case homeId = "home_id"
        case devices
        case threats
        case recommendations
        case protectionLevel = "protection_level"
        case lastScan = "last_scan"
    }
}

struct IoTDevicesResponse: Codable {
    let devices: [IoTDevice]
    let threats: [IoTThreat]?
    let total: Int?
    let compromised: Int?
    let safe: Int?
}

struct IoTThreatsResponse: Codable {
    let threats: [IoTThreat]
    let total: Int?
    let high: Int?
    let medium: Int?
    let low: Int?
}

struct ReferralHistoryItem: Codable, Identifiable {
    let referralId: String
    let friendId: String
    let status: String
    let createdAt: String
    let convertedAt: String?
    let referralCode: String?
    let discountApplied: Double?
    let rewardAmount: Double?
    
    var id: String { referralId }
    
    enum CodingKeys: String, CodingKey {
        case referralId = "referral_id"
        case friendId = "friend_id"
        case status
        case createdAt = "created_at"
        case convertedAt = "converted_at"
        case referralCode = "referral_code"
        case discountApplied = "discount_applied"
        case rewardAmount = "reward_amount"
    }
}

// MARK: - Protection (Threat Protection) Models

// Note: ProtectionSettings is defined in Shared/Models/ProtectionSettings.swift

struct ProtectionSettingsResponse: Codable {
    let settings: ProtectionSettings
    let lastUpdated: Date
    let version: String
}

struct ProtectionStatusResponse: Codable {
    let isActive: Bool
    let activeCategories: [String]
    let threatsBlockedToday: Int
    let threatsBlockedWeek: Int
    let lastThreat: Date?
}

struct ThreatScenarioResponse: Codable, Identifiable {
    let id: String
    let title: String
    let description: String
    let icon: String
    let requiredTariff: String
    let protectionSteps: [String]
    let category: String
}

struct ProtectionStatsResponse: Codable {
    let totalThreatsBlocked: Int
    let threatsByCategory: [String: Int]
    let lastUpdate: Date
    let protectionLevel: Int
}

// MARK: - Component Models

struct ComponentStatusResponse: Codable {
    let status: ComponentStatus
    let message: String?
}

struct ComponentConfigurationResponse: Codable {
    let configuration: ComponentConfiguration
    let message: String?
}


