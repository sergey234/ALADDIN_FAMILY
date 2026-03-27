import Foundation

// MARK: - Types from ProductionMonitoringService

enum AlertType: String {
    case performance = "performance"
    case error = "error"
    case security = "security"
}

enum AlertSeverity: String {
    case info = "info"
    case warning = "warning"
    case critical = "critical"
}

struct Alert {
    let id: String
    let type: AlertType
    let message: String
    let severity: AlertSeverity
    let timestamp: Date
}

struct HealthStatus {
    enum Status: String {
        case healthy = "healthy"
        case warning = "warning"
        case critical = "critical"
    }

    let status: Status
    let uptime: Double
    let lastCheck: Date
    let activeComponents: Int
    let totalComponents: Int
    let issues: [String] = []
}

// MARK: - Data Source Enum

/// Источник данных для аналитики
enum DataSource: String, Codable {
    case api          // Реальные данные из API
    case cache        // Кэшированные данные
    case empty        // Нет данных (показываем 0)
    case error        // Ошибка API
}

// MARK: - Data Models

/// Фильтры для аналитики
struct AnalyticsFilters: Equatable {
    let onlyBlocked: Bool
    let includeFamily: Bool
    let includeDevices: Bool
}

/// Сводная статистика аналитики
struct AnalyticsSummary: Codable, Equatable {
    let threatsDetected: Int
    let threatsBlocked: Int
    let itemsScanned: Int
    let protectionLevel: Double
}

// MARK: - Detailed Analytics Models

/// Детальная статистика безопасности
struct SecurityAnalytics: Codable {
    let blockedThreats: [ThreatTypeCount]
    let recentThreats: [RecentThreat]
    let networkProtectionStats: AnalyticsNetworkProtectionStats
}

/// Статистика по семье
struct FamilyAnalytics: Codable {
    let membersActivity: [FamilyMemberActivity]
    let threatsByMember: [MemberThreats]
    let recentActivity: [FamilyActivity]
}

/// Статистика использования
struct UsageAnalytics: Codable {
    let activityByTime: [TimePeriodActivity]
    let topApps: [AppUsage]
    let topSites: [SiteUsage]
    let totalTraffic: String // "2.3 GB"
}

/// Статистика по устройствам
struct DevicesAnalytics: Codable {
    let deviceActivity: [DeviceActivity]
    let threatsByDevice: [DeviceThreats]
    let status: AnalyticsDeviceStatus
}

// MARK: - Supporting Models

struct ThreatTypeCount: Codable, Identifiable, Equatable {
    let id: UUID
    let type: String // код категории (web, file, network, app)
    let count: Int
    let icon: String?
    
    init(id: UUID = UUID(), type: String, count: Int, icon: String? = nil) {
        self.id = id
        self.type = type
        self.count = count
        self.icon = icon
    }
    
    private enum CodingKeys: String, CodingKey {
        case type
        case count
        case icon
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = UUID()
        self.type = try container.decode(String.self, forKey: .type)
        self.count = try container.decode(Int.self, forKey: .count)
        self.icon = try container.decodeIfPresent(String.self, forKey: .icon)
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(type, forKey: .type)
        try container.encode(count, forKey: .count)
        try container.encodeIfPresent(icon, forKey: .icon)
    }
}

struct RecentThreat: Codable, Identifiable {
    let id: UUID
    let emoji: String
    let text: String
    let time: String // "2 мин назад"
    
    init(id: UUID = UUID(), emoji: String, text: String, time: String) {
        self.id = id
        self.emoji = emoji
        self.text = text
        self.time = time
    }
}

struct AnalyticsNetworkProtectionStats: Codable {
    let today: String // "2.3 GB"
    let week: String // "15.8 GB"
    let protection: String // "100%"
}

struct FamilyMemberActivity: Codable, Identifiable {
    let id: UUID
    let emoji: String
    let name: String
    let time: String // "4ч 15м"
    let percent: Int
    
    init(id: UUID = UUID(), emoji: String, name: String, time: String, percent: Int) {
        self.id = id
        self.emoji = emoji
        self.name = name
        self.time = time
        self.percent = percent
    }
}

struct MemberThreats: Codable, Identifiable {
    let id: UUID
    let emoji: String
    let name: String
    let count: Int
    let warning: String? // "⚠️" или nil
    
    init(id: UUID = UUID(), emoji: String, name: String, count: Int, warning: String? = nil) {
        self.id = id
        self.emoji = emoji
        self.name = name
        self.count = count
        self.warning = warning
    }
}

struct FamilyActivity: Codable, Identifiable {
    let id: UUID
    let emoji: String
    let member: String
    let activity: String
    let time: String
    
    init(id: UUID = UUID(), emoji: String, member: String, activity: String, time: String) {
        self.id = id
        self.emoji = emoji
        self.member = member
        self.activity = activity
        self.time = time
    }
}

struct TimePeriodActivity: Codable, Identifiable {
    let id: UUID
    let emoji: String
    let period: String // "Утро (6-12)"
    let time: String // "2ч 15м"
    let percent: Int
    
    init(id: UUID = UUID(), emoji: String, period: String, time: String, percent: Int) {
        self.id = id
        self.emoji = emoji
        self.period = period
        self.time = time
        self.percent = percent
    }
}

struct AppUsage: Codable, Identifiable {
    let id: UUID
    let rank: Int
    let name: String
    let time: String // "2ч 15м"
    
    init(id: UUID = UUID(), rank: Int, name: String, time: String) {
        self.id = id
        self.rank = rank
        self.name = name
        self.time = time
    }
}

struct SiteUsage: Codable, Identifiable {
    let id: UUID
    let rank: Int
    let url: String
    let visits: String // "142 визита"
    
    init(id: UUID = UUID(), rank: Int, url: String, visits: String) {
        self.id = id
        self.rank = rank
        self.url = url
        self.visits = visits
    }
}

struct DeviceActivity: Codable, Identifiable {
    let id: UUID
    let emoji: String
    let name: String
    let time: String // "4ч 15м"
    let percent: Int
    
    init(id: UUID = UUID(), emoji: String, name: String, time: String, percent: Int) {
        self.id = id
        self.emoji = emoji
        self.name = name
        self.time = time
        self.percent = percent
    }
}

struct DeviceThreats: Codable, Identifiable {
    let id: UUID
    let emoji: String
    let name: String
    let count: Int
    
    init(id: UUID = UUID(), emoji: String, name: String, count: Int) {
        self.id = id
        self.emoji = emoji
        self.name = name
        self.count = count
    }
}

struct AnalyticsDeviceStatus: Codable {
    let online: Int
    let offline: Int
    let protection: String // "100%"
}

// MARK: - Service Protocol

/// Протокол для получения аналитики
protocol AnalyticsService {
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> (AnalyticsSummary, DataSource)
    func fetchSecurityAnalytics(period: String) async throws -> (SecurityAnalytics, DataSource)
    func fetchFamilyAnalytics(period: String) async throws -> FamilyAnalytics
    func fetchUsageAnalytics(period: String) async throws -> (UsageAnalytics, DataSource)
    func fetchDevicesAnalytics(period: String) async throws -> DevicesAnalytics

    // Production monitoring methods
    func trackAPIRequest(endpoint: String, method: String, responseTime: TimeInterval, statusCode: Int, success: Bool)
    func trackUserAction(action: String, parameters: [String: Any]?)
    func trackError(error: Error, context: String?)
    func trackAlert(alert: Alert)
    func trackHealthReport(healthStatus: HealthStatus)
}

// MARK: - Local Implementation

/// Локальный сервис аналитики с мок-данными
final class LocalAnalyticsService: AnalyticsService {
    
    // MARK: - Summary
    
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> (AnalyticsSummary, DataSource) {
        // Небольшая задержка для имитации загрузки
        try? await Task.sleep(nanoseconds: 100_000_000) // 0.1 секунды
        
        let summary: AnalyticsSummary
        switch period {
        case "day":
            summary = AnalyticsSummary(
                threatsDetected: 12,
                threatsBlocked: 12,
                itemsScanned: 847,
                protectionLevel: 96.0
            )
        case "week":
            summary = AnalyticsSummary(
                threatsDetected: 47,
                threatsBlocked: 45,
                itemsScanned: 5234,
                protectionLevel: 96.0
            )
        case "month":
            summary = AnalyticsSummary(
                threatsDetected: 189,
                threatsBlocked: 185,
                itemsScanned: 21890,
                protectionLevel: 98.0
            )
        default:
            summary = AnalyticsSummary(
                threatsDetected: 0,
                threatsBlocked: 0,
                itemsScanned: 0,
                protectionLevel: 0
            )
        }
        return (summary, .api) // LocalAnalyticsService всегда возвращает .api
    }
    
    // MARK: - Security Analytics
    
    func fetchSecurityAnalytics(period: String) async throws -> (SecurityAnalytics, DataSource) {
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        let security = SecurityAnalytics(
            blockedThreats: [
                ThreatTypeCount(type: "web", count: 542, icon: "globe"),
                ThreatTypeCount(type: "file", count: 318, icon: "doc"),
                ThreatTypeCount(type: "app", count: 187, icon: "iphone"),
                ThreatTypeCount(type: "network", count: 200, icon: "shield")
            ],
            recentThreats: [
                RecentThreat(emoji: "✅", text: "Фишинговый сайт", time: "2 мин назад"),
                RecentThreat(emoji: "⚠️", text: "Подозрительное приложение", time: "15 мин"),
                RecentThreat(emoji: "🚫", text: "Вредоносный файл", time: "1 час назад")
            ],
            networkProtectionStats: AnalyticsNetworkProtectionStats(
                today: "2.3 GB",
                week: "15.8 GB",
                protection: "100%"
            )
        )
        return (security, .api) // LocalAnalyticsService всегда возвращает .api
    }
    
    // MARK: - Family Analytics
    
    func fetchFamilyAnalytics(period: String) async throws -> FamilyAnalytics {
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        return FamilyAnalytics(
            membersActivity: [
                FamilyMemberActivity(emoji: "👨", name: "Александр", time: "4ч 15м", percent: 35),
                FamilyMemberActivity(emoji: "👩", name: "Елена", time: "3ч 42м", percent: 31),
                FamilyMemberActivity(emoji: "👦", name: "Алексей", time: "2ч 27м", percent: 20),
                FamilyMemberActivity(emoji: "👵", name: "Бабушка", time: "1ч 40м", percent: 14)
            ],
            threatsByMember: [
                MemberThreats(emoji: "👨", name: "Александр", count: 245, warning: nil),
                MemberThreats(emoji: "👩", name: "Елена", count: 189, warning: nil),
                MemberThreats(emoji: "👦", name: "Алексей", count: 342, warning: "⚠️"),
                MemberThreats(emoji: "👵", name: "Бабушка", count: 80, warning: nil)
            ],
            recentActivity: [
                FamilyActivity(emoji: "👦", member: "Алексей", activity: "безопасная игра", time: "5 мин"),
                FamilyActivity(emoji: "👧", member: "Мария", activity: "урок безопасности", time: "30 мин"),
                FamilyActivity(emoji: "👩", member: "Мама", activity: "родительский контроль", time: "2ч")
            ]
        )
    }
    
    // MARK: - Usage Analytics
    
    func fetchUsageAnalytics(period: String) async throws -> (UsageAnalytics, DataSource) {
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        let usage = UsageAnalytics(
            activityByTime: [
                TimePeriodActivity(emoji: "🌅", period: "Утро (6-12)", time: "2ч 15м", percent: 27),
                TimePeriodActivity(emoji: "☀️", period: "День (12-18)", time: "3ч 42м", percent: 44),
                TimePeriodActivity(emoji: "🌙", period: "Вечер (18-24)", time: "2ч 27м", percent: 29)
            ],
            topApps: [
                AppUsage(rank: 1, name: "Instagram", time: "2ч 15м"),
                AppUsage(rank: 2, name: "YouTube", time: "1ч 48м"),
                AppUsage(rank: 3, name: "WhatsApp", time: "1ч 12м"),
                AppUsage(rank: 4, name: "Safari", time: "58мин"),
                AppUsage(rank: 5, name: "TikTok", time: "45мин")
            ],
            topSites: [
                SiteUsage(rank: 1, url: "youtube.com", visits: "142 визита"),
                SiteUsage(rank: 2, url: "vk.com", visits: "89 визитов"),
                SiteUsage(rank: 3, url: "google.com", visits: "67 визитов"),
                SiteUsage(rank: 4, url: "yandex.ru", visits: "54 визита"),
                SiteUsage(rank: 5, url: "mail.ru", visits: "42 визита")
            ],
            totalTraffic: "2.3 GB"
        )
        return (usage, .api) // LocalAnalyticsService всегда возвращает .api
    }
    
    // MARK: - Devices Analytics
    
    func fetchDevicesAnalytics(period: String) async throws -> DevicesAnalytics {
        try? await Task.sleep(nanoseconds: 100_000_000)
        
        return DevicesAnalytics(
            deviceActivity: [
                DeviceActivity(emoji: "📱", name: "iPhone 13 Pro", time: "4ч 15м", percent: 35),
                DeviceActivity(emoji: "💻", name: "MacBook Pro", time: "3ч 42м", percent: 31),
                DeviceActivity(emoji: "📱", name: "iPhone 12", time: "2ч 27м", percent: 20),
                DeviceActivity(emoji: "🖥️", name: "iMac 27\"", time: "1ч 40м", percent: 14),
                DeviceActivity(emoji: "📲", name: "iPad Air", time: "45мин", percent: 6),
                DeviceActivity(emoji: "⌚", name: "Apple Watch", time: "15мин", percent: 2)
            ],
            threatsByDevice: [
                DeviceThreats(emoji: "📱", name: "iPhone 13 Pro", count: 245),
                DeviceThreats(emoji: "💻", name: "MacBook Pro", count: 189),
                DeviceThreats(emoji: "📱", name: "iPhone 12", count: 142),
                DeviceThreats(emoji: "🖥️", name: "iMac 27\"", count: 198),
                DeviceThreats(emoji: "📲", name: "iPad Air", count: 82),
                DeviceThreats(emoji: "⌚", name: "Apple Watch", count: 5)
            ],
            status: AnalyticsDeviceStatus(
                online: 4,
                offline: 2,
                protection: "100%"
            )
        )
    }

    // MARK: - Production Monitoring Implementation

    func trackAPIRequest(endpoint: String, method: String, responseTime: TimeInterval, statusCode: Int, success: Bool) {
        #if DEBUG
        print("📊 API Request: \(method) \(endpoint) - \(String(format: "%.3f", responseTime))s - Status: \(statusCode) - Success: \(success)")
        #endif

        // В локальном сервисе просто логируем
        // В продакшене можно отправлять на сервер аналитики
    }

    func trackUserAction(action: String, parameters: [String: Any]?) {
        #if DEBUG
        print("👤 User Action: \(action) - Parameters: \(parameters ?? [:])")
        #endif
    }

    func trackError(error: Error, context: String?) {
        #if DEBUG
        print("❌ Error: \(error.localizedDescription) - Context: \(context ?? "unknown")")
        #endif
    }

    func trackAlert(alert: Alert) {
        #if DEBUG
        print("🚨 Alert [\(alert.severity.rawValue)]: \(alert.message)")
        #else
        // В продакшене отправляем алерты разработчикам
        print("🚨 PRODUCTION ALERT: [\(alert.severity.rawValue.uppercased())] \(alert.message)")
        #endif
    }

    func trackHealthReport(healthStatus: HealthStatus) {
        #if DEBUG
        print("💚 Health Report: \(healthStatus.status.rawValue) - Issues: \(healthStatus.issues.count)")
        for issue in healthStatus.issues {
            print("   - \(issue)")
        }
        #endif
    }
}
