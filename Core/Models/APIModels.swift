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

// ✅ ДОБАВЛЕНО: Network Protection Settings Response (для синхронизации между устройствами)
struct NetworkProtectionSettingsResponse: Codable {
    let autoSelectServer: Bool
    let autoConnectWiFi: Bool
    let autoConnectMobile: Bool
    let killSwitch: Bool
    let dnsLeakProtection: Bool
    let batteryOptimizationEnabled: Bool
    let antivirusEnabled: Bool
    let lastUpdated: Date?
}

// ✅ План 2026: DNS Configuration
struct DNSConfigResponse: Codable {
    let dohUrl: String
    let serverName: String
    let blockingEnabled: Bool
    let categories: [String]
    
    enum CodingKeys: String, CodingKey {
        case dohUrl = "doh_url"
        case serverName = "server_name"
        case blockingEnabled = "blocking_enabled"
        case categories
    }
}

// ✅ План 2026: Parental Reports
struct ParentalReportItem: Codable, Identifiable {
    let id: Int
    let userId: Int
    let type: String
    let content: [String: AnyCodable]
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case type
        case content
        case createdAt = "created_at"
    }
}

// MARK: - Family Models

struct FamilyMemberData: Identifiable, Codable {
    var id = UUID()
    var name: String
    var role: FamilyMemberCard.FamilyRole
    var avatar: String
    var status: FamilyMemberCard.ProtectionStatus
    var threatsBlocked: Int
    var lastActive: String
}

struct AppLimitItemCodable: Codable {
    let app: String
    var limit: Double
    let colorHex: String
}

struct AppLimitItem: Identifiable {
    let id = UUID()
    var app: String
    var limit: Double
    let color: Color
}

struct LocationEvent: Identifiable {
    let id = UUID()
    let time: String
    let action: String
    let status: LocationStatus
    
    enum LocationStatus {
        case arrival
        case departure
        
        var icon: String {
            switch self {
            case .arrival: return "✅"
            case .departure: return "🚶"
            }
        }
    }
}

struct ReportWarning: Identifiable {
    let id = UUID()
    let title: String
    let time: String
    let severity: Severity
    
    enum Severity {
        case low, medium, high
        
        var color: Color {
            switch self {
            case .low: return .blue
            case .medium: return .orange
            case .high: return .red
            }
        }
    }
    
    // For backward compatibility with Build 122 design
    init(title: String, time: String, severity: Severity) {
        self.title = title
        self.time = time
        self.severity = severity
    }
    
    init(text: String, color: Color) {
        self.title = text
        self.time = ""
        self.severity = color == .red || color == .dangerRed ? .high : .medium
    }
    
    var text: String { title }
    var color: Color { severity.color }
}

struct CreateFamilyResponse: Codable {
    // ✅ ИСПРАВЛЕНО: Модель соответствует реальному ответу сервера
    let family_id: String
    let short_code: String          // Сервер возвращает short_code вместо recovery_code
    let creator_member_id: String  // Сервер возвращает creator_member_id вместо your_member_id
    let qr_code_data: String
    let expires_at: String
    
    // ✅ Опциональные поля для обратной совместимости (если сервер их вернет)
    let success: Bool?
    let members: [FamilyMemberResponse]?
    let access_token: String?
    let refresh_token: String?
    
    // ✅ CodingKeys для правильного маппинга
    enum CodingKeys: String, CodingKey {
        case family_id
        case short_code
        case creator_member_id
        case qr_code_data
        case expires_at
        case success
        case members
        case access_token
        case refresh_token
    }
    
    // ✅ Вычисляемые свойства для обратной совместимости
    var recovery_code: String {
        // Преобразуем family_id в формат recovery code: FAM_ABC123 → FAM-ABC1-23
        return formatRecoveryCode(from: family_id)
    }
    
    var your_member_id: String {
        return creator_member_id
    }
    
    // ✅ Приватный метод для форматирования recovery code
    private func formatRecoveryCode(from familyId: String) -> String {
        // FAM_03F8BB425B7C → FAM-03F8-BB42-5B7C
        let cleaned = familyId.replacingOccurrences(of: "FAM_", with: "")
        guard cleaned.count >= 12 else {
            // Если формат неожиданный, используем short_code
            return "FAM-\(short_code)"
        }
        
        // Разбиваем на группы по 4 символа
        let part1 = String(cleaned.prefix(4))
        let part2 = String(cleaned.dropFirst(4).prefix(4))
        let part3 = String(cleaned.dropFirst(8).prefix(4))
        
        return "FAM-\(part1)-\(part2)-\(part3)"
    }
}

// MARK: - Recovery Code Login Models

struct RecoveryCodeLoginRequest: Codable {
    let family_id: String
    let recovery_code: String
}

struct RecoveryCodeLoginResponse: Codable {
    let access_token: String
    let refresh_token: String?
    let expires_in: TimeInterval?
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
    let context: String?
    let userId: String?
    let timestamp: Date?

    init(message: String, context: String? = nil, userId: String? = nil, timestamp: Date? = nil) {
        self.message = message
        self.context = context
        self.userId = userId
        self.timestamp = timestamp ?? Date()
    }
}

struct ChatMessageResponse: Codable {
    let response: String
    let confidence: Double?
    let suggestions: [String]?
    let followUpQuestions: [String]?
    let timestamp: String?  // ✅ ИСПРАВЛЕНО: Изменено с Date? на String? для совместимости с сервером

    enum CodingKeys: String, CodingKey {
        case response, confidence, suggestions
        case followUpQuestions = "follow_up_questions"
        case timestamp
    }

    // ✅ ИСПРАВЛЕНИЕ BUILD 90: Статический форматтер для предотвращения рекурсии
    private static let timestampFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime] // Поддержка формата 2026-03-03T00:37:41.912231
        return formatter
    }()

    // ✅ ДОБАВЛЕНО: Вычисляемое свойство для конвертации timestamp в Date (для UI)
    var timestampDate: Date? {
        guard let timestamp = timestamp else { return nil }
        // ✅ Используем статический formatter вместо создания нового каждый раз
        return Self.timestampFormatter.date(from: timestamp)
    }
}

// История чата
struct AIChatHistoryResponse: Codable {
    let conversations: [AIConversation]

    struct AIConversation: Codable {
        let date: String
        let messages: Int
        let topics: [String]
    }
}

// Обратная связь
struct AIFeedbackRequest: Codable {
    let rating: Int
    let comment: String?
    let messageId: String?
}

struct AIFeedbackResponse: Codable {
    let feedbackRecorded: Bool
    let averageRating: Double
    let totalFeedbacks: Int

    enum CodingKeys: String, CodingKey {
        case feedbackRecorded = "feedback_recorded"
        case averageRating = "average_rating"
        case totalFeedbacks = "total_feedbacks"
    }
}

// Возможности AI
struct AICapabilitiesResponse: Codable {
    let features: [String]
    let languages: [String]
    let responseTime: String
    let accuracy: String

    enum CodingKeys: String, CodingKey {
        case features, languages
        case responseTime = "response_time"
        case accuracy
    }
}

// Анализ угрозы
struct AIAnalyzeThreatRequest: Codable {
    let threat: String
    let type: String?
    let context: String?
}

struct AIAnalyzeThreatResponse: Codable {
    let threatLevel: String
    let analysis: String
    let actionsTaken: [String]
    let preventionTips: [String]

    enum CodingKeys: String, CodingKey {
        case threatLevel = "threat_level"
        case analysis
        case actionsTaken = "actions_taken"
        case preventionTips = "prevention_tips"
    }
}

// Персональные рекомендации
struct AIRecommendationsResponse: Codable {
    let personalRecommendations: [String]
    let securityScore: Int
    let improvementAreas: [String]

    enum CodingKeys: String, CodingKey {
        case personalRecommendations = "personal_recommendations"
        case securityScore = "security_score"
        case improvementAreas = "improvement_areas"
    }
}

// Сообщение об инциденте
struct AIReportIncidentRequest: Codable {
    let type: String
    let description: String
    let severity: String?
}

struct AIReportIncidentResponse: Codable {
    let incidentId: String
    let status: String
    let estimatedResolution: String
    let assignedSpecialist: String
    let followUpActions: [String]

    enum CodingKeys: String, CodingKey {
        case incidentId = "incident_id"
        case status
        case estimatedResolution = "estimated_resolution"
        case assignedSpecialist = "assigned_specialist"
        case followUpActions = "follow_up_actions"
    }
}

// Советы по безопасности
struct AISecurityTipsResponse: Codable {
    let dailyTips: [String]
    let weeklyFocus: String
    let monthlyGoal: String

    enum CodingKeys: String, CodingKey {
        case dailyTips = "daily_tips"
        case weeklyFocus = "weekly_focus"
        case monthlyGoal = "monthly_goal"
    }
}

// MARK: - User Models

// MARK: - Token Refresh Models

struct RefreshTokenResponse: Codable {
    let access_token: String
    let refresh_token: String?
    let expires_in: TimeInterval?
    let token_type: String?
}

// MARK: - JWT Payload Models (для декодирования JWT)

/// Структура для декодирования JWT payload
/// JWT Payload structure for token decoding (used in TokenHealthMonitor)
/// Note: This is different from private JWTPayload in SubscriptionManager.swift
struct JWTPayload: Codable {
    let sub: String?  // User ID
    let device_id: String?
    let exp: TimeInterval?  // Expiration time (Unix timestamp)
    let iat: TimeInterval?  // Issued at (Unix timestamp)
    let iss: String?  // Issuer
    let subscription: JWTSubscriptionPayload?
}

/// Структура subscription в JWT payload
struct JWTSubscriptionPayload: Codable {
    let level: String  // subscription level (trial, free, personal, family, premium)
    let is_active: Bool?
    let expires_at: String?  // ISO 8601 date string
    let trial_info: TrialInfo?
    let limits: JWTSubscriptionLimits?
    let components: [String]?
}

/// Структура limits в JWT payload
struct JWTSubscriptionLimits: Codable {
    let max_devices: Int?
    let max_ai_messages: Int?
    let max_scans: Int?
    let max_reports: Int?
    
    /// Конвертировать в SubscriptionLimits
    func toSubscriptionLimits() -> SubscriptionLimits {
        return SubscriptionLimits(
            maxDevices: max_devices ?? 1,
            maxAIMessages: max_ai_messages ?? 10,
            maxScans: max_scans ?? 5,
            maxReports: max_reports ?? 3,
            currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
        )
    }
}

struct UserProfile: Codable {
    let id: String
    let name: String
    let isGuest: Bool?
    let email: String?
    let phone: String?
    let registrationDate: String?
    let subscriptionType: String?
    let subscriptionEndDate: String?
    let threatsBlocked: Int?
    let familyMembers: Int?
    let devices: Int?
    
    // ✅ КОМПЬЮТЕД ПРОПЕРТИ: Безопасные значения по умолчанию для опциональных полей
    var safeEmail: String {
        return email ?? ""
    }

    var safeIsGuest: Bool {
        return isGuest ?? false
    }

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case isGuest = "is_guest"
        case email
        case phone
        case registrationDate
        case subscriptionType
        case subscriptionEndDate
        case threatsBlocked
        case familyMembers
        case devices
    }
    
    var safeRegistrationDate: String {
        return registrationDate ?? ""
    }
    
    var safeSubscriptionType: String {
        return subscriptionType ?? "free"
    }
    
    var safeThreatsBlocked: Int {
        return threatsBlocked ?? 0
    }
    
    var safeFamilyMembers: Int {
        return familyMembers ?? 0
    }
    
    var safeDevices: Int {
        return devices ?? 0
    }
}

struct UpdateProfileRequest: Codable {
    let name: String?
    let email: String?
    let phone: String?
}

// ✅ ДОБАВЛЕНО: 2FA Status Response (для синхронизации между устройствами)
struct TwoFactorAuthStatusResponse: Codable {
    let enabled: Bool
    let lastUpdated: Date?
    let method: String? // "sms", "email", "app"
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

// MARK: - Receipt Validation Models

/// Запрос валидации receipt
struct ReceiptValidationRequest: Codable {
    let receiptData: String
    let productId: String
    let subscriptionLevel: String

    enum CodingKeys: String, CodingKey {
        case receiptData = "receipt_data"
        case productId = "product_id"
        case subscriptionLevel = "subscription_level"
    }
}

/// Ответ валидации receipt
struct ReceiptValidationResponse: Codable {
    let isValid: Bool
    let subscriptionLevel: String?
    let transactionId: String?
    let errorMessage: String?

    enum CodingKeys: String, CodingKey {
        case isValid = "is_valid"
        case subscriptionLevel = "subscription_level"
        case transactionId = "transaction_id"
        case errorMessage = "error_message"
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
    
    func localizedName() -> String {
        return self.rawValue
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
    let location: ParentalControlLocationStats
    let monitoring: MonitoringStats
    
    // ✅ ИСПРАВЛЕНО: CodingKeys для маппинга snake_case → camelCase
    enum CodingKeys: String, CodingKey {
        case contentBlocked = "content_blocked"
        case screenTime = "screen_time"
        case location
        case monitoring
    }
}

struct ContentBlockedStats: Codable {
    let websitesBlocked: Int
    let appsBlocked: Int
    let searchQueriesBlocked: Int
    let activeFilters: Int
    
    // ✅ ИСПРАВЛЕНО: CodingKeys для маппинга snake_case → camelCase
    enum CodingKeys: String, CodingKey {
        case websitesBlocked = "websites_blocked"
        case appsBlocked = "apps_blocked"
        case searchQueriesBlocked = "search_queries_blocked"
        case activeFilters = "active_filters"
    }
}

struct ScreenTimeStats: Codable {
    let todayUsage: String // "1ч 24мин"
    let todayLimit: String // "2ч"
    let remaining: String // "36мин"
    let schedulesCount: Int
    
    // ✅ ИСПРАВЛЕНО: CodingKeys для маппинга snake_case → camelCase
    enum CodingKeys: String, CodingKey {
        case todayUsage = "today_usage"
        case todayLimit = "today_limit"
        case remaining
        case schedulesCount = "schedules_count"
    }
}

struct ParentalControlLocationStats: Codable {
    let currentLocation: String?
    let lastUpdate: String?
    let geofencesCount: Int
    let eventsToday: Int
    
    // ✅ ИСПРАВЛЕНО: CodingKeys для маппинга snake_case → camelCase
    enum CodingKeys: String, CodingKey {
        case currentLocation = "current_location"
        case lastUpdate = "last_update"
        case geofencesCount = "geofences_count"
        case eventsToday = "events_today"
    }
}

struct MonitoringStats: Codable {
    let sitesTracked: Int
    let appsTracked: Int
    let contactsTracked: Int
    let messagesMonitored: Bool
    let screenshotsEnabled: Bool?  // ✅ ИСПРАВЛЕНО: Опциональное поле (сервер может не возвращать)
    
    // ✅ ИСПРАВЛЕНО: CodingKeys для маппинга snake_case → camelCase
    enum CodingKeys: String, CodingKey {
        case sitesTracked = "sites_tracked"
        case appsTracked = "apps_tracked"
        case contactsTracked = "contacts_tracked"
        case messagesMonitored = "messages_monitored"
        case screenshotsEnabled = "screenshots_enabled"
    }
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

// ✅ ДОБАВЛЕНО: Device Settings Response (для синхронизации между устройствами)
struct DeviceSettingsResponse: Codable {
    let isProtectionOn: Bool
    let isScanningEnabled: Bool
    let lastUpdated: Date?
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

// ✅ ИСПРАВЛЕНО: Обновлена структура для соответствия API
struct ProtectionStatsResponse: Codable {
    let isActive: Bool
    let functionsActive: Int
    let threatsBlocked: Int
    let lastScan: String
    let securityScore: Int
    let protectionLevel: String
    let activeComponents: [String]
    let recommendations: [String]?
    
    enum CodingKeys: String, CodingKey {
        case isActive
        case functionsActive
        case threatsBlocked
        case lastScan
        case securityScore
        case protectionLevel
        case activeComponents
        case recommendations
    }
}

// MARK: - Protection Threats & Quarantine Models (Antivirus)

struct ThreatResponse: Codable, Identifiable {
    let id: String
    let name: String
    let type: String
    let severity: String
    let confidence: Double
    let filePath: String?
    let fileSize: Int64?
    let detectedAt: String  // ISO 8601 date string
    let status: String  // "active", "quarantined", "resolved"
    let quarantinePath: String?
    let quarantinedAt: String?  // ISO 8601 date string
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case type
        case severity
        case confidence
        case filePath
        case fileSize
        case detectedAt
        case status
        case quarantinePath
        case quarantinedAt
    }
}

struct ThreatsListResponse: Codable {
    let threats: [ThreatResponse]
    let total: Int
    let active: Int
    let quarantined: Int
    let resolved: Int
}

struct QuarantineActionRequest: Codable {
    let threatId: String
    let action: String  // "quarantine", "restore", "remove"
    let filePath: String?
}

struct QuarantineActionResponse: Codable {
    let success: Bool
    let message: String?
    let threat: ThreatResponse?
}

// MARK: - Component Models

struct ComponentStatusResponse: Codable {
    // OLD CONTRACT (flat)
    let flatStatus: String?           // "enabled" или "disabled"
    let uptime: Double?              // Процент uptime
    let last_check: String?         // ISO дата последней проверки
    let version: String?            // Версия компонента
    let source: String?             // Источник данных
    let function: String?          // Название функции (используется для derivation componentId)
    let timestamp: String?         // Время ответа

    // NEW CONTRACT (envelope)
    let componentId: String?
    let isEnabled: Bool?
    let envelopeStatus: String?
    let lastUpdated: String?
    let error: String?

    private enum CodingKeys: String, CodingKey {
        case status
        case uptime
        case last_check
        case version
        case source
        case function
        case timestamp
        // envelope fields live inside `status`, but we reuse names for readability
        case componentId
        case isEnabled
        case lastUpdated
        case error
    }

    private struct EnvelopeStatus: Codable {
        let componentId: String
        let isEnabled: Bool
        let status: String
        let lastUpdated: String
        let error: String?
    }

    init(
        flatStatus: String?,
        uptime: Double?,
        last_check: String?,
        version: String?,
        source: String?,
        function: String?,
        timestamp: String?,
        componentId: String?,
        isEnabled: Bool?,
        envelopeStatus: String?,
        lastUpdated: String?,
        error: String?
    ) {
        self.flatStatus = flatStatus
        self.uptime = uptime
        self.last_check = last_check
        self.version = version
        self.source = source
        self.function = function
        self.timestamp = timestamp

        self.componentId = componentId
        self.isEnabled = isEnabled
        self.envelopeStatus = envelopeStatus
        self.lastUpdated = lastUpdated
        self.error = error
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        // Try new envelope first: {"status":{componentId,isEnabled,status,lastUpdated,...}}
        if let env = try? container.decode(EnvelopeStatus.self, forKey: .status) {
            self.flatStatus = nil
            self.uptime = nil
            self.last_check = nil
            self.version = nil
            self.source = nil
            self.function = nil
            self.timestamp = nil

            self.componentId = env.componentId
            self.isEnabled = env.isEnabled
            self.envelopeStatus = env.status
            self.lastUpdated = env.lastUpdated
            self.error = env.error
            return
        }

        // Fallback to old flat contract
        self.flatStatus = try? container.decode(String.self, forKey: .status)
        self.uptime = try? container.decode(Double.self, forKey: .uptime)
        self.last_check = try? container.decode(String.self, forKey: .last_check)
        self.version = try? container.decode(String.self, forKey: .version)
        self.source = try? container.decode(String.self, forKey: .source)
        self.function = try? container.decode(String.self, forKey: .function)
        self.timestamp = try? container.decode(String.self, forKey: .timestamp)

        self.componentId = nil
        self.isEnabled = nil
        self.envelopeStatus = nil
        self.lastUpdated = nil
        self.error = nil
    }

    // Энкодинг почти нигде не используется (мы только декодируем ответ сервера),
    // но тип должен соответствовать `Codable` из-за `APIResponse<T: Codable>`.
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)

        // Если есть данные нового envelope-формата — попробуем закодировать как объект под ключом `status`.
        if let componentId = componentId,
           let isEnabled = isEnabled,
           let envelopeStatus = envelopeStatus,
           let lastUpdated = lastUpdated {
            let env = EnvelopeStatus(
                componentId: componentId,
                isEnabled: isEnabled,
                status: envelopeStatus,
                lastUpdated: lastUpdated,
                error: error
            )
            try container.encode(env, forKey: .status)
        } else {
            // Иначе: закодируем old flat-структуру (минимально).
            try container.encodeIfPresent(flatStatus, forKey: .status)
            try container.encodeIfPresent(uptime, forKey: .uptime)
            try container.encodeIfPresent(last_check, forKey: .last_check)
            try container.encodeIfPresent(version, forKey: .version)
            try container.encodeIfPresent(source, forKey: .source)
            try container.encodeIfPresent(function, forKey: .function)
            try container.encodeIfPresent(timestamp, forKey: .timestamp)
        }
    }

    // Вычисляемое свойство для конвертации в ComponentStatus
    var componentStatus: ComponentStatus {
        let derivedComponentId: String = {
            if let componentId = componentId, !componentId.isEmpty {
                return componentId
            }
            return function?
                .replacingOccurrences(of: "get_component_status", with: "")
                .trimmingCharacters(in: CharacterSet(charactersIn: "/")) ?? "unknown"
        }()

        let derivedIsEnabled: Bool = {
            if let isEnabled = isEnabled {
                return isEnabled
            }
            let statusText = (flatStatus ?? envelopeStatus)?.lowercased() ?? "disabled"
            return statusText == "enabled"
        }()

        let lastUpdate = parseFlexibleDate(lastUpdated) ?? parseFlexibleDate(last_check)

        return ComponentStatus(
            componentId: derivedComponentId,
            isEnabled: derivedIsEnabled,
            lastUpdate: lastUpdate,
            configuration: nil
        )
    }

    // Парсим разные форматы, которые реально прилетают на проде:
    // - ISO8601
    // - "2026-03-18 19:58:49"
    private func parseFlexibleDate(_ input: String?) -> Date? {
        guard let inputValue = input, !inputValue.isEmpty else { return nil }

        // 1) ISO8601 (на случай если сервер даст строго ISO)
        let iso = ISO8601DateFormatter()
        if let d = iso.date(from: inputValue) { return d }

        // 2) "yyyy-MM-dd HH:mm:ss" (как в логах: lastUpdated: "2026-03-18 19:58:49")
        let df = DateFormatter()
        df.locale = Locale(identifier: "en_US_POSIX")
        df.timeZone = TimeZone(secondsFromGMT: 0)
        df.dateFormat = "yyyy-MM-dd HH:mm:ss"
        return df.date(from: inputValue)
    }
}

struct ComponentConfigurationResponse: Codable {
    let component_id: String
    let config: ComponentConfigData
    let version: String?
    let last_updated: String?
    
    // Вычисляемое свойство для совместимости
    var configuration: ComponentConfiguration {
        // Преобразуем config в ComponentConfiguration
        var additionalSettings: [String: AnyCodable] = [:]
        
        // Преобразуем дополнительные настройки из config
        if let autoStart = self.config.auto_start {
            additionalSettings["auto_start"] = AnyCodable(autoStart)
        }
        if let logLevel = self.config.log_level {
            additionalSettings["log_level"] = AnyCodable(logLevel)
        }
        
        return ComponentConfiguration(
            isEnabled: self.config.enabled,
            priority: .normal,
            additionalSettings: additionalSettings.isEmpty ? nil : additionalSettings
        )
    }
    
    struct ComponentConfigData: Codable {
        let enabled: Bool
        let auto_start: Bool?
        let log_level: String?
    }
}

// ✅ ЗАДАЧА 22: Модель для общего здоровья компонентов
struct ComponentsHealthResponse: Codable {
    let overallHealth: String  // "healthy", "degraded", "critical"
    let totalComponents: Int
    let enabledComponents: Int
    let disabledComponents: Int
    let healthyComponents: Int
    let degradedComponents: Int
    let criticalComponents: Int
    let lastCheck: String?  // ISO дата
}

// ✅ ЗАДАЧА 24-25: Roadside Assistance Models
struct RoadsideRequest: Codable, Identifiable {
    let id: String
    let status: String  // "waiting", "en_route", "arrived", "completed", "cancelled"
    let eta: String?  // Estimated time of arrival
    let provider: String?  // Название службы помощи
    let latitude: Double
    let longitude: Double
    let vehicleInfo: String?
    let createdAt: String?  // ISO дата
    let updatedAt: String?  // ISO дата
}

struct RoadsideStatus: Codable {
    let requestId: String
    let status: String  // "waiting", "en_route", "arrived", "completed", "cancelled"
    let eta: String?  // Estimated time of arrival
    let provider: String?  // Название службы помощи
    let location: RoadsideLocation?
    let updatedAt: String?  // ISO дата
}

struct RoadsideLocation: Codable {
    let latitude: Double
    let longitude: Double
    let address: String?
}

// MARK: - ✅ ГЕЙМИФИКАЦИЯ: Gamification Models

// Баланс единорогов
struct GamificationBalanceResponse: Codable {
    let balance: Int
    let userId: String
    let lastModified: String  // ISO дата
    let deviceId: String?
    let version: Int
}

struct AddBalanceRequest: Codable {
    let userId: String
    let amount: Int
    let reason: String?
    let deviceId: String?
}

struct SubtractBalanceRequest: Codable {
    let userId: String
    let amount: Int
    let reason: String?
    let deviceId: String?
}

struct BalanceHistoryEntry: Codable, Identifiable {
    let id: String  // operationId
    let userId: String
    let amount: Int
    let balanceAfter: Int
    let reason: String?
    let timestamp: String  // ISO дата
    let deviceId: String?
}

struct BalanceHistoryResponse: Codable {
    let history: [BalanceHistoryEntry]
    let total: Int
    let currentBalance: Int
}

// Награды
struct RewardResponse: Codable, Identifiable {
    let id: String  // rewardId
    let name: String
    let description: String?
    let price: Int
    let category: String?
    let available: Bool
    
    // ✅ ИСПРАВЛЕНО: Маппинг rewardId → id
    enum CodingKeys: String, CodingKey {
        case id = "rewardId"  // Сервер возвращает rewardId, маппим в id
        case name
        case description
        case price
        case category
        case available
    }
    
    var rewardId: String { id }
}

struct RewardsListResponse: Codable {
    let rewards: [RewardResponse]
    let total: Int

    init(rewards: [RewardResponse], total: Int) {
        self.rewards = rewards
        self.total = total
    }

    init(from decoder: Decoder) throws {
        // Tolerant decoding: backend may return [] instead of {"rewards":[...],"total":N}
        if var unkeyed = try? decoder.unkeyedContainer() {
            var decodedRewards: [RewardResponse] = []
            while !unkeyed.isAtEnd {
                if let reward = try? unkeyed.decode(RewardResponse.self) {
                    decodedRewards.append(reward)
                } else {
                    _ = try? unkeyed.decode(String.self)
                }
            }
            self.rewards = decodedRewards
            self.total = decodedRewards.count
            return
        }

        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.rewards = (try? container.decode([RewardResponse].self, forKey: .rewards)) ?? []
        self.total = (try? container.decode(Int.self, forKey: .total)) ?? rewards.count
    }
}

struct ClaimRewardRequest: Codable {
    let userId: String
    let rewardId: String
    let deviceId: String?
}

struct ClaimRewardResponse: Codable {
    let success: Bool
    let newBalance: Int
    let reward: RewardResponse?
    let message: String?
}

// Достижения
struct AchievementResponse: Codable, Identifiable {
    let id: String  // achievementId
    let name: String
    let description: String?
    let icon: String?
    let reward: Int
    let unlocked: Bool
    let unlockedAt: String?  // ISO дата
    let progress: Double  // 0-1
    
    var achievementId: String { id }
}

struct AchievementsListResponse: Codable {
    let achievements: [AchievementResponse]
    let total: Int
    let unlockedCount: Int
}

struct UnlockAchievementRequest: Codable {
    let userId: String
    let achievementId: String
    let deviceId: String?
}

struct AchievementProgressResponse: Codable {
    let achievements: [AchievementResponse]
    let totalProgress: Double  // 0-1
}

// Турниры
struct TournamentResponse: Codable, Identifiable {
    let id: String  // tournamentId
    let name: String
    let description: String?
    let startDate: String  // ISO дата
    let endDate: String  // ISO дата
    let status: String  // "upcoming", "active", "finished"
    let participants: Int
    let maxParticipants: Int?
    let prize: Int
    
    // ✅ ИСПРАВЛЕНО: Маппинг tournamentId → id
    enum CodingKeys: String, CodingKey {
        case id = "tournamentId"  // Сервер возвращает tournamentId, маппим в id
        case name
        case description
        case startDate
        case endDate
        case status
        case participants
        case maxParticipants
        case prize
    }
    
    var tournamentId: String { id }
}

struct TournamentsListResponse: Codable {
    let tournaments: [TournamentResponse]
    let total: Int
}

struct JoinTournamentRequest: Codable {
    let userId: String
    let tournamentId: String
    let deviceId: String?
}

struct LeaderboardEntry: Codable, Identifiable {
    let id: String  // userId
    let username: String?
    let score: Int
    let rank: Int
    let avatar: String?
    
    var userId: String { id }
}

struct LeaderboardResponse: Codable {
    let leaderboard: [LeaderboardEntry]
    let total: Int
    let tournamentId: String
}

// Настройки игр
struct GameSettingsResponse: Codable {
    let userId: String
    let soundEnabled: Bool
    let musicEnabled: Bool
    let notificationsEnabled: Bool
    let difficulty: String  // "easy", "medium", "hard"
    let language: String
    let lastModified: String  // ISO дата
    let version: Int
}

struct UpdateGameSettingsRequest: Codable {
    let userId: String
    let soundEnabled: Bool?
    let musicEnabled: Bool?
    let notificationsEnabled: Bool?
    let difficulty: String?
    let language: String?
    let deviceId: String?
    let version: Int?
}

struct NotificationSettingsResponse: Codable {
    let userId: String
    let achievementUnlocked: Bool
    let tournamentStarted: Bool
    let rewardAvailable: Bool
    let levelUp: Bool
    let lastModified: String  // ISO дата
}

struct UpdateNotificationSettingsRequest: Codable {
    let userId: String
    let achievementUnlocked: Bool?
    let tournamentStarted: Bool?
    let rewardAvailable: Bool?
    let levelUp: Bool?
    let deviceId: String?
}

// MARK: - ✅ РОДИТЕЛЬСКИЙ КОНТРОЛЬ: Parental Control Sync Models

// Настройки родительского контроля
struct ParentalControlSettingsResponse: Codable {
    let familyId: String
    let childId: String?
    let isContentFilterEnabled: Bool
    let isAppBlockingEnabled: Bool
    let screenTimeLimitHours: Int
    let allowedApps: [String]
    let blockedWebsites: [String]
    let bedtime: String?
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int

    enum CodingKeys: String, CodingKey {
        case familyId
        case childId
        case isContentFilterEnabled
        case isAppBlockingEnabled
        case screenTimeLimitHours
        case allowedApps
        case blockedWebsites
        case bedtime
        case lastModified
        case deviceId
        case version
        // legacy flat keys from /api/parental-control/settings
        case success
        case safeSearch
        case youtubeRestrictedMode
        case appInstallBlocked
        // optional snake_case compatibility keys (backend variants)
        case is_content_filter_enabled
        case is_app_blocking_enabled
        case screen_time_limit_hours
        case allowed_apps
        case blocked_websites
        case last_modified
        case device_id
    }

    init(
        familyId: String,
        childId: String?,
        isContentFilterEnabled: Bool,
        isAppBlockingEnabled: Bool,
        screenTimeLimitHours: Int,
        allowedApps: [String],
        blockedWebsites: [String],
        bedtime: String?,
        lastModified: String,
        deviceId: String?,
        version: Int
    ) {
        self.familyId = familyId
        self.childId = childId
        self.isContentFilterEnabled = isContentFilterEnabled
        self.isAppBlockingEnabled = isAppBlockingEnabled
        self.screenTimeLimitHours = screenTimeLimitHours
        self.allowedApps = allowedApps
        self.blockedWebsites = blockedWebsites
        self.bedtime = bedtime
        self.lastModified = lastModified
        self.deviceId = deviceId
        self.version = version
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.familyId = (try? container.decode(String.self, forKey: .familyId)) ?? "family_default"
        self.childId = try? container.decodeIfPresent(String.self, forKey: .childId)
        self.isContentFilterEnabled =
            (try? container.decode(Bool.self, forKey: .isContentFilterEnabled))
            ?? (try? container.decode(Bool.self, forKey: .is_content_filter_enabled))
            ?? (try? container.decode(Bool.self, forKey: .safeSearch))
            ?? false
        self.isAppBlockingEnabled =
            (try? container.decode(Bool.self, forKey: .isAppBlockingEnabled))
            ?? (try? container.decode(Bool.self, forKey: .is_app_blocking_enabled))
            ?? (try? container.decode(Bool.self, forKey: .appInstallBlocked))
            ?? false
        self.screenTimeLimitHours =
            (try? container.decode(Int.self, forKey: .screenTimeLimitHours))
            ?? (try? container.decode(Int.self, forKey: .screen_time_limit_hours))
            ?? 0
        self.allowedApps =
            (try? container.decode([String].self, forKey: .allowedApps))
            ?? (try? container.decode([String].self, forKey: .allowed_apps))
            ?? []
        self.blockedWebsites =
            (try? container.decode([String].self, forKey: .blockedWebsites))
            ?? (try? container.decode([String].self, forKey: .blocked_websites))
            ?? []
        self.bedtime = try? container.decodeIfPresent(String.self, forKey: .bedtime)
        self.lastModified =
            (try? container.decode(String.self, forKey: .lastModified))
            ?? (try? container.decode(String.self, forKey: .last_modified))
            ?? ""
        self.deviceId =
            (try? container.decodeIfPresent(String.self, forKey: .deviceId))
            ?? (try? container.decodeIfPresent(String.self, forKey: .device_id))
        self.version = (try? container.decode(Int.self, forKey: .version)) ?? 1
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(familyId, forKey: .familyId)
        try container.encodeIfPresent(childId, forKey: .childId)
        try container.encode(isContentFilterEnabled, forKey: .isContentFilterEnabled)
        try container.encode(isAppBlockingEnabled, forKey: .isAppBlockingEnabled)
        try container.encode(screenTimeLimitHours, forKey: .screenTimeLimitHours)
        try container.encode(allowedApps, forKey: .allowedApps)
        try container.encode(blockedWebsites, forKey: .blockedWebsites)
        try container.encodeIfPresent(bedtime, forKey: .bedtime)
        try container.encode(lastModified, forKey: .lastModified)
        try container.encodeIfPresent(deviceId, forKey: .deviceId)
        try container.encode(version, forKey: .version)
    }
}

struct UpdateParentalControlSettingsRequest: Codable {
    let familyId: String
    let childId: String?
    let isContentFilterEnabled: Bool?
    let isAppBlockingEnabled: Bool?
    let screenTimeLimitHours: Int?
    let allowedApps: [String]?
    let blockedWebsites: [String]?
    let bedtime: String?
    let deviceId: String?
    let version: Int?
}

struct SettingsHistoryEntry: Codable {
    let historyId: String
    let familyId: String
    let childId: String?
    let changedBy: String
    let changes: [String: String] // JSON как словарь
    let timestamp: String // ISO дата
    let deviceId: String?
}

struct SettingsHistoryResponse: Codable {
    let history: [SettingsHistoryEntry]
    let total: Int
}

struct SyncParentalControlSettingsRequest: Codable {
    let familyId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncParentalControlSettingsResponse: Codable {
    let familyId: String
    let settings: [ParentalControlSettingsResponse]
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct SettingsConflictResponse: Codable {
    let conflictId: String
    let familyId: String
    let childId: String?
    let field: String
    let localValue: String // JSON строка
    let serverValue: String // JSON строка
    let localTimestamp: String // ISO дата
    let serverTimestamp: String // ISO дата
    let localDeviceId: String
    let serverDeviceId: String
}

struct SettingsConflictsResponse: Codable {
    let conflicts: [SettingsConflictResponse]
    let total: Int
}

// Лимиты времени
struct TimeLimitResponse: Codable {
    let childId: String
    let dailyLimitMinutes: Int
    let weeklyLimitMinutes: Int
    let bedtimeStart: String?
    let bedtimeEnd: String?
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int

    enum CodingKeys: String, CodingKey {
        case childId
        case dailyLimitMinutes
        case weeklyLimitMinutes
        case bedtimeStart
        case bedtimeEnd
        case lastModified
        case deviceId
        case version
    }

    init(from decoder: Decoder) throws {
        // Tolerant decoding: backend may return []
        if let unkeyed = try? decoder.unkeyedContainer(), unkeyed.count == 0 {
            self.childId = ""
            self.dailyLimitMinutes = 0
            self.weeklyLimitMinutes = 0
            self.bedtimeStart = nil
            self.bedtimeEnd = nil
            self.lastModified = ""
            self.deviceId = nil
            self.version = 1
            return
        }

        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.childId = (try? container.decode(String.self, forKey: .childId)) ?? ""
        self.dailyLimitMinutes = (try? container.decode(Int.self, forKey: .dailyLimitMinutes)) ?? 0
        self.weeklyLimitMinutes = (try? container.decode(Int.self, forKey: .weeklyLimitMinutes)) ?? 0
        self.bedtimeStart = try? container.decodeIfPresent(String.self, forKey: .bedtimeStart)
        self.bedtimeEnd = try? container.decodeIfPresent(String.self, forKey: .bedtimeEnd)
        self.lastModified = (try? container.decode(String.self, forKey: .lastModified)) ?? ""
        self.deviceId = try? container.decodeIfPresent(String.self, forKey: .deviceId)
        self.version = (try? container.decode(Int.self, forKey: .version)) ?? 1
    }
}

struct UpdateTimeLimitRequest: Codable {
    let childId: String
    let dailyLimitMinutes: Int?
    let weeklyLimitMinutes: Int?
    let bedtimeStart: String?
    let bedtimeEnd: String?
    let deviceId: String?
    let version: Int?
}

struct TimeLimitHistoryEntry: Codable {
    let historyId: String
    let childId: String
    let changedBy: String
    let changes: [String: String] // JSON как словарь
    let timestamp: String // ISO дата
    let deviceId: String?
}

struct TimeLimitHistoryResponse: Codable {
    let history: [TimeLimitHistoryEntry]
    let total: Int
}

struct ResetTimeLimitRequest: Codable {
    let childId: String
    let deviceId: String?
}

// Расписания
struct ScheduleResponse: Codable {
    let scheduleId: String
    let childId: String
    let name: String
    let weekdays: [Int] // 0=понедельник, 6=воскресенье
    let startTime: String // HH:mm
    let endTime: String // HH:mm
    let isActive: Bool
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdateScheduleRequest: Codable {
    let scheduleId: String?
    let childId: String
    let name: String?
    let weekdays: [Int]?
    let startTime: String?
    let endTime: String?
    let isActive: Bool?
    let deviceId: String?
    let version: Int?
}

struct ScheduleHistoryEntry: Codable {
    let historyId: String
    let scheduleId: String
    let childId: String
    let changedBy: String
    let action: String // "created", "updated", "deleted"
    let changes: [String: String]? // JSON как словарь
    let timestamp: String // ISO дата
    let deviceId: String?
}

struct ScheduleHistoryResponse: Codable {
    let history: [ScheduleHistoryEntry]
    let total: Int
}

struct DeleteScheduleRequest: Codable {
    let scheduleId: String
    let deviceId: String?
}

// Геозоны
struct GeofenceResponse: Codable {
    let geofenceId: String
    let childId: String
    let name: String
    let latitude: Double
    let longitude: Double
    let radius: Double // в метрах
    let isActive: Bool
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct AddGeofenceRequest: Codable {
    let childId: String
    let name: String
    let latitude: Double
    let longitude: Double
    let radius: Double
    let isActive: Bool
    let deviceId: String?
}

struct UpdateGeofenceRequest: Codable {
    let geofenceId: String
    let name: String?
    let latitude: Double?
    let longitude: Double?
    let radius: Double?
    let isActive: Bool?
    let deviceId: String?
    let version: Int?
}

// Блокировки приложений
struct AppBlockResponse: Codable {
    let childId: String
    let blockedApps: [String]
    let appLimits: [String: Int] // appName -> minutes
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int

    enum CodingKeys: String, CodingKey {
        case childId
        case blockedApps
        case appLimits
        case lastModified
        case deviceId
        case version
    }

    init(from decoder: Decoder) throws {
        // Tolerant decoding: backend may return []
        if let unkeyed = try? decoder.unkeyedContainer(), unkeyed.count == 0 {
            self.childId = ""
            self.blockedApps = []
            self.appLimits = [:]
            self.lastModified = ""
            self.deviceId = nil
            self.version = 1
            return
        }

        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.childId = (try? container.decode(String.self, forKey: .childId)) ?? ""
        self.blockedApps = (try? container.decode([String].self, forKey: .blockedApps)) ?? []
        self.appLimits = (try? container.decode([String: Int].self, forKey: .appLimits)) ?? [:]
        self.lastModified = (try? container.decode(String.self, forKey: .lastModified)) ?? ""
        self.deviceId = try? container.decodeIfPresent(String.self, forKey: .deviceId)
        self.version = (try? container.decode(Int.self, forKey: .version)) ?? 1
    }
}

struct UpdateAppBlocksRequest: Codable {
    let childId: String
    let blockedApps: [String]?
    let appLimits: [String: Int]?
    let deviceId: String?
    let version: Int?
}

struct SyncAppBlocksRequest: Codable {
    let childId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncAppBlocksResponse: Codable {
    let childId: String
    let appBlocks: AppBlockResponse
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

// MARK: - ✅ ЭТАП 2: User Profile Sync Models

struct UserProfileSyncResponse: Codable {
    let userId: String
    let name: String
    let email: String?
    let phone: String?
    let avatar: String?
    let registrationDate: String // ISO дата
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdateUserProfileSyncRequest: Codable {
    let userId: String
    let name: String?
    let email: String?
    let phone: String?
    let avatar: String?
    let deviceId: String?
    let version: Int?
}

struct SyncUserProfileRequest: Codable {
    let userId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncUserProfileResponse: Codable {
    let userId: String
    let profile: UserProfileSyncResponse
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct ProfileHistoryEntry: Codable {
    let historyId: String
    let userId: String
    let changedBy: String
    let changes: [String: String] // JSON как словарь
    let timestamp: String // ISO дата
    let deviceId: String?
}

struct ProfileHistoryResponse: Codable {
    let history: [ProfileHistoryEntry]
    let total: Int
}

struct PrivacySettingsResponse: Codable {
    let userId: String
    let profileVisibility: String // "public", "private", "friends"
    let showEmail: Bool
    let showPhone: Bool
    let showLocation: Bool
    let allowDataSharing: Bool
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdatePrivacySettingsRequest: Codable {
    let userId: String
    let profileVisibility: String?
    let showEmail: Bool?
    let showPhone: Bool?
    let showLocation: Bool?
    let allowDataSharing: Bool?
    let deviceId: String?
    let version: Int?
}

// MARK: - ✅ ЭТАП 2: Subscription Sync Models

struct SubscriptionResponse: Codable {
    let userId: String
    let subscriptionType: String // "free", "basic", "family", "premium"
    let status: String // "active", "expired", "cancelled", "pending"
    let startDate: String // ISO дата
    let endDate: String? // ISO дата
    let autoRenewal: Bool
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct SyncSubscriptionRequest: Codable {
    let userId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncSubscriptionResponse: Codable {
    let userId: String
    let subscription: SubscriptionResponse
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct UpdateSubscriptionRequest: Codable {
    let userId: String
    let subscriptionType: String?
    let status: String?
    let endDate: String? // ISO дата
    let deviceId: String?
    let version: Int?
}

struct PurchaseHistoryEntry: Codable {
    let purchaseId: String
    let userId: String
    let subscriptionType: String
    let amount: Double
    let currency: String
    let purchaseDate: String // ISO дата
    let transactionId: String?
    let status: String // "success", "failed", "pending", "refunded"
}

struct PurchaseHistoryResponse: Codable {
    let history: [PurchaseHistoryEntry]
    let total: Int
}


struct UpdateSubscriptionStatusRequest: Codable {
    let userId: String
    let status: String
    let deviceId: String?
    let version: Int?
}

struct AutoRenewalResponse: Codable {
    let userId: String
    let enabled: Bool
    let nextRenewalDate: String? // ISO дата
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdateAutoRenewalRequest: Codable {
    let userId: String
    let enabled: Bool
    let deviceId: String?
    let version: Int?
}

struct CancelSubscriptionRequest: Codable {
    let userId: String
    let reason: String?
    let deviceId: String?
}

// MARK: - ✅ ЭТАП 2: App Settings Sync Models

struct AppSettingsResponse: Codable {
    let userId: String
    let theme: String // "light", "dark", "system"
    let language: String // "ru", "en"
    let notificationsEnabled: Bool
    let biometryEnabled: Bool
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct SyncAppSettingsRequest: Codable {
    let userId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncAppSettingsResponse: Codable {
    let userId: String
    let settings: AppSettingsResponse
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct UpdateAppSettingsRequest: Codable {
    let userId: String
    let theme: String?
    let language: String?
    let notificationsEnabled: Bool?
    let biometryEnabled: Bool?
    let deviceId: String?
    let version: Int?
}

struct ThemeSettingsResponse: Codable {
    let userId: String
    let theme: String
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdateThemeSettingsRequest: Codable {
    let userId: String
    let theme: String
    let deviceId: String?
    let version: Int?
}

struct LanguageSettingsResponse: Codable {
    let userId: String
    let language: String
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdateLanguageSettingsRequest: Codable {
    let userId: String
    let language: String
    let deviceId: String?
    let version: Int?
}

struct NotificationSettingsAppResponse: Codable {
    let userId: String
    let enabled: Bool
    let pushEnabled: Bool
    let emailEnabled: Bool
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdateNotificationSettingsAppRequest: Codable {
    let userId: String
    let enabled: Bool?
    let pushEnabled: Bool?
    let emailEnabled: Bool?
    let deviceId: String?
    let version: Int?
}

struct BiometrySettingsResponse: Codable {
    let userId: String
    let enabled: Bool
    let type: String? // "face", "touch", "none"
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdateBiometrySettingsRequest: Codable {
    let userId: String
    let enabled: Bool
    let type: String?
    let deviceId: String?
    let version: Int?
}

// MARK: - ✅ ЭТАП 2: Location & Chat Sync Models

// Геолокация и геозоны
struct LocationGeofenceResponse: Codable {
    let geofenceId: String
    let userId: String
    let name: String
    let latitude: Double
    let longitude: Double
    let radius: Double // в метрах
    let isActive: Bool
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct SyncLocationGeofencesRequest: Codable {
    let userId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncLocationGeofencesResponse: Codable {
    let userId: String
    let geofences: [LocationGeofenceResponse]
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct UpdateLocationGeofenceRequest: Codable {
    let geofenceId: String?
    let userId: String
    let name: String?
    let latitude: Double?
    let longitude: Double?
    let radius: Double?
    let isActive: Bool?
    let deviceId: String?
    let version: Int?
}

struct MovementHistoryEntry: Codable {
    let entryId: String
    let userId: String
    let latitude: Double
    let longitude: Double
    let timestamp: String // ISO дата
    let speed: Double?
    let accuracy: Double?
    let deviceId: String?
}

struct MovementHistoryResponse: Codable {
    let history: [MovementHistoryEntry]
    let total: Int
}

struct UpdateMovementHistoryRequest: Codable {
    let userId: String
    let entries: [MovementHistoryEntry]
    let deviceId: String?
}

struct LocationStatusResponse: Codable {
    let userId: String
    let enabled: Bool
    let lastKnownLocation: [String: Double]? // {latitude, longitude}
    let lastUpdate: String? // ISO дата
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct UpdateLocationStatusRequest: Codable {
    let userId: String
    let enabled: Bool
    let deviceId: String?
    let version: Int?
}

// Семейный чат (офлайн)
struct OfflineMessageResponse: Codable {
    let messageId: String
    let userId: String
    let recipientId: String
    let familyId: String
    let content: String
    let timestamp: String // ISO дата
    let isRead: Bool
    let deviceId: String?
    let version: Int
}

struct SyncOfflineMessagesRequest: Codable {
    let userId: String
    let familyId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncOfflineMessagesResponse: Codable {
    let userId: String
    let familyId: String
    let messages: [OfflineMessageResponse]
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct SendOfflineMessageRequest: Codable {
    let userId: String
    let recipientId: String
    let familyId: String
    let content: String
    let deviceId: String?
    let timestamp: String? // ISO дата
}

struct ResolveMessageConflictsRequest: Codable {
    let userId: String
    let familyId: String
    let conflicts: [[String: String]] // Массив конфликтов
    let deviceId: String?
}

// MARK: - ✅ ЭТАП 3: Offline Storage Sync Models

struct OfflineDataResponse: Codable {
    let dataId: String
    let userId: String
    let dataType: String // "settings", "cache", "temp", etc.
    let data: [String: AnyCodable] // JSON данные
    let size: Int // Размер в байтах
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct SyncOfflineStorageRequest: Codable {
    let userId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
    let dataTypes: [String]? // Типы данных для синхронизации
}

struct SyncOfflineStorageResponse: Codable {
    let userId: String
    let data: [OfflineDataResponse]
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
    let totalSize: Int // Общий размер в байтах
}

struct UpdateOfflineDataRequest: Codable {
    let userId: String
    let dataId: String?
    let dataType: String
    let data: [String: AnyCodable] // JSON данные
    let deviceId: String?
    let version: Int?
}

struct ResolveOfflineStorageConflictsRequest: Codable {
    let userId: String
    let conflicts: [[String: String]] // Массив конфликтов
    let resolutionStrategy: String // "last-write-wins", "merge", "manual"
    let deviceId: String?
}

// AnyCodable определен в ComponentConfiguration.swift

// MARK: - ✅ ЭТАП 3: Crash Detection Sync Models

struct CrashReportResponse: Codable {
    let reportId: String
    let userId: String
    let deviceId: String
    let crashType: String // "accident", "fall", "emergency", etc.
    let severity: String // "low", "medium", "high", "critical"
    let location: [String: Double]? // {latitude, longitude}
    let timestamp: String // ISO дата
    let details: [String: AnyCodable]? // Дополнительные детали
    let isResolved: Bool
    let lastModified: String // ISO дата
    let version: Int
}

struct SyncCrashDetectionRequest: Codable {
    let userId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncCrashDetectionResponse: Codable {
    let userId: String
    let reports: [CrashReportResponse]
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct ReportCrashRequest: Codable {
    let userId: String
    let deviceId: String
    let crashType: String
    let severity: String
    let location: [String: Double]?
    let timestamp: String? // ISO дата
    let details: [String: AnyCodable]?
}

struct CrashNotificationResponse: Codable {
    let notificationId: String
    let userId: String
    let reportId: String
    let recipientId: String?
    let message: String
    let timestamp: String // ISO дата
    let isRead: Bool
}

struct SendCrashNotificationRequest: Codable {
    let userId: String
    let reportId: String
    let recipientId: String?
    let message: String?
    let deviceId: String?
}

// MARK: - ✅ ЭТАП 3: Elderly Interface Sync Models

struct MedicationResponse: Codable {
    let medicationId: String
    let userId: String
    let name: String
    let dosage: String
    let frequency: String // "daily", "weekly", "as_needed", etc.
    let timeOfDay: String? // "HH:MM"
    let startDate: String // ISO дата
    let endDate: String? // ISO дата
    let notes: String?
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct SyncMedicationsRequest: Codable {
    let userId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncMedicationsResponse: Codable {
    let userId: String
    let medications: [MedicationResponse]
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct UpdateMedicationRequest: Codable {
    let medicationId: String?
    let userId: String
    let name: String?
    let dosage: String?
    let frequency: String?
    let timeOfDay: String?
    let startDate: String? // ISO дата
    let endDate: String? // ISO дата
    let notes: String?
    let deviceId: String?
    let version: Int?
}

struct AppointmentResponse: Codable {
    let appointmentId: String
    let userId: String
    let title: String
    let description: String?
    let dateTime: String // ISO дата
    let location: String?
    let contactName: String?
    let contactPhone: String?
    let reminderMinutes: Int?
    let isCompleted: Bool
    let lastModified: String // ISO дата
    let deviceId: String?
    let version: Int
}

struct SyncAppointmentsRequest: Codable {
    let userId: String
    let deviceId: String
    let lastSyncTimestamp: String? // ISO дата
}

struct SyncAppointmentsResponse: Codable {
    let userId: String
    let appointments: [AppointmentResponse]
    let conflicts: [[String: String]] // Массив конфликтов
    let lastSyncTimestamp: String // ISO дата
}

struct UpdateAppointmentRequest: Codable {
    let appointmentId: String?
    let userId: String
    let title: String?
    let description: String?
    let dateTime: String? // ISO дата
    let location: String?
    let contactName: String?
    let contactPhone: String?
    let reminderMinutes: Int?
    let isCompleted: Bool?
    let deviceId: String?
    let version: Int?
}

// Прогресс игр
struct GameProgressResponse: Codable, Identifiable {
    let id: String  // gameId
    let gameName: String
    let level: Int
    let experience: Int
    let experienceToNextLevel: Int
    let totalScore: Int
    let lastPlayed: String?  // ISO дата
    
    var gameId: String { id }
}

struct GameProgressListResponse: Codable {
    let progress: [GameProgressResponse]
    let total: Int
}

struct UpdateProgressRequest: Codable {
    let userId: String
    let gameId: String
    let experience: Int?
    let score: Int?
    let deviceId: String?
}

struct ProgressStatsResponse: Codable {
    let totalGames: Int
    let totalLevel: Int
    let totalExperience: Int
    let totalScore: Int
    let gamesPlayed: Int
}

struct LevelResponse: Codable {
    let userId: String
    let currentLevel: Int
    let experience: Int
    let experienceToNextLevel: Int
    let progress: Double  // 0-1
}

struct ResetProgressRequest: Codable {
    let userId: String
    let gameId: String?
    let parentId: String
}

// MARK: - ✅ NEW: Crash Detection Extended Models

struct UpdateCrashSettingsRequest: Codable {
    let userId: String
    let sensitivity: Double
    let geofenceRadius: Double
}

struct CrashHistoryResponse: Codable {
    let crashes: [CrashEvent]
    let total: Int
    let hasMore: Bool
}

struct CrashEvent: Codable {
    let id: String
    let timestamp: String
    let location: LocationData?
    let severity: String
    let description: String
}

struct LocationData: Codable {
    let latitude: Double
    let longitude: Double
    let address: String?
}

// MARK: - ✅ NEW: System Management Models

struct SystemHealthResponse: Codable {
    let status: String  // "healthy", "warning", "critical"
    let components: [ComponentHealth]
    let overall: HealthMetrics
    let timestamp: String
}

struct ComponentHealth: Codable {
    let name: String
    let status: String
    let responseTime: Double?
    let errorRate: Double?
    let lastCheck: String?
}

struct HealthMetrics: Codable {
    let uptime: Double  // секунды
    let cpuUsage: Double  // 0-100%
    let memoryUsage: Double  // 0-100%
    let diskUsage: Double  // 0-100%
    let activeConnections: Int
}

struct SystemInfoResponse: Codable {
    let version: String
    let build: String
    let environment: String
    let activeUsers: Int
    let totalUsers: Int
    let uptime: Double
    let serverTime: String
}

struct SystemMetricsResponse: Codable {
    let timestamp: String
    let requestsPerSecond: Double
    let averageResponseTime: Double
    let errorRate: Double
    let activeConnections: Int
    let queueLength: Int
    let memoryUsage: Double
    let cpuUsage: Double
}

struct SystemStatusResponse: Codable {
    let status: String  // "operational", "degraded", "maintenance"
    let message: String
    let lastUpdated: String
    let estimatedRecoveryTime: String?
}

struct BackupResponse: Codable {
    let backupId: String
    let status: String  // "scheduled", "running", "completed", "failed"
    let estimatedTime: Double?
    let size: Int64?
    let startedAt: String
}

struct BackupStatusResponse: Codable {
    let backupId: String
    let status: String
    let progress: Double  // 0.0 to 1.0
    let size: Int64?
    let startedAt: String
    let completedAt: String?
    let error: String?
    let downloadUrl: String?
}

// MARK: - ✅ NEW: Notifications Extended Models

struct NotificationCategoriesResponse: Codable {
    let categories: [APINotificationCategory]
}

struct APINotificationCategory: Codable {
    let id: String
    let name: String
    let description: String
    let icon: String
    let enabled: Bool
    let priority: String  // "low", "medium", "high"
    let defaultEnabled: Bool
}

struct BulkMarkReadRequest: Codable {
    let notificationIds: [String]
}

struct NotificationStatsResponse: Codable {
    let total: Int
    let unread: Int
    let archived: Int
    let byCategory: [String: Int]
    let byPriority: [String: Int]
    let lastWeek: Int
    let lastMonth: Int
    let averagePerDay: Double
}

// MARK: - Device Registration Models

/// 📱 Device Registration Request
struct DeviceRegisterRequest: Codable {
    let deviceId: String
    let deviceType: String
    
    // ✅ ИСПРАВЛЕНИЕ BUILD 121: Конвертация camelCase в snake_case для сервера
    enum CodingKeys: String, CodingKey {
        case deviceId = "device_id"
        case deviceType = "device_type"
    }
}

/// 📱 Device Registration Response
/// ✅ FIXED: Proper date format handling (ISO 8601)
struct DeviceRegisterResponse: Codable {
    let deviceId: String
    let token: String
    let subscription: DeviceSubscription
    let registeredAt: String  // ISO 8601 date string
    let expiresAt: String?    // ISO 8601 date string (nullable)

    /// 🔧 Subscription info within device registration
    struct DeviceSubscription: Codable {
        let level: String      // "free", "trial", "personal", etc.
        let isActive: Bool
        let expiresAt: String? // ISO 8601 date string (nullable)
        let trialInfo: TrialInfo?

        /// ✅ STORED: Default limits for FREE level during registration
        /// 🔧 FIXED: Stored properties work with Codable, computed don't
        let limits: SubscriptionLimits
        let components: [String]

        /// ✅ CUSTOM DECODER: Handle missing fields with defaults
        init(from decoder: Decoder) throws {
            let container = try decoder.container(keyedBy: CodingKeys.self)

            // Decode required fields
            level = try container.decode(String.self, forKey: .level)
            isActive = try container.decode(Bool.self, forKey: .isActive)
            expiresAt = try container.decodeIfPresent(String.self, forKey: .expiresAt)
            trialInfo = try container.decodeIfPresent(TrialInfo.self, forKey: .trialInfo)

            // ✅ Handle missing limits/components with FREE defaults
            limits = try container.decodeIfPresent(SubscriptionLimits.self, forKey: .limits) ?? SubscriptionLimits(
                maxDevices: 1,
                maxAIMessages: 10,
                maxScans: 5,
                maxReports: 3,
                currentUsage: UsageCounters(aiMessages: 0, scans: 0, reports: 0, devices: 0)
            )

            components = try container.decodeIfPresent([String].self, forKey: .components) ?? []
        }

        /// ✅ CODING KEYS: Include limits and components
        enum CodingKeys: String, CodingKey {
            case level, isActive, expiresAt, trialInfo
            case limits, components  // ✅ Now included in Codable
        }
    }
}

/// 📱 Trial Device Registration Request
struct TrialDeviceRegisterRequest: Codable {
    let deviceId: String
    let deviceType: String
    let trialInfo: TrialInfo

    enum CodingKeys: String, CodingKey {
        case deviceId = "device_id"
        case deviceType = "device_type"
        case trialInfo = "trial_info"
    }
}



