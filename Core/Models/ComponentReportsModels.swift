import Foundation
import SwiftUI

/**
 * 📊 Component Reports Models
 * Модели данных для отчетов компонентов защиты
 * Все модели Codable для работы с API
 */

// MARK: - Driving Reports Models

struct DrivingReport: Identifiable, Codable {
    let id: String
    let userId: String
    let userName: String
    let startTime: Date
    let endTime: Date
    let startLocation: String
    let endLocation: String
    let distance: Double // км
    let duration: TimeInterval // секунды
    let averageSpeed: Double // км/ч
    let maxSpeed: Double // км/ч
    let safetyScore: Double // 0-10
    let events: [DrivingEvent]
    let violations: [DrivingViolation]
    let positioningSystem: String? // GPS, GLONASS, Galileo, BeiDou
    
    var durationMinutes: Int {
        Int(duration / 60)
    }
    
    var formattedDistance: String {
        String(format: "%.1f км", distance)
    }
    
    var formattedAverageSpeed: String {
        String(format: "%.0f км/ч", averageSpeed)
    }
    
    var formattedMaxSpeed: String {
        String(format: "%.0f км/ч", maxSpeed)
    }
    
    var formattedSafetyScore: String {
        String(format: "%.1f/10", safetyScore)
    }
}

struct DrivingEvent: Codable {
    let type: DrivingEventType
    let timestamp: Date
    let severity: Double // 0-1 (0 = мягкое, 1 = резкое)
    let location: String?
    
    var severityLevel: String {
        if severity >= 0.8 {
            return "Резкое"
        } else if severity >= 0.5 {
            return "Среднее"
        } else {
            return "Мягкое"
        }
    }
}

enum DrivingEventType: String, Codable {
    case braking = "braking"
    case acceleration = "acceleration"
    case turn = "turn"
    
    var displayName: String {
        switch self {
        case .braking: return "Торможение"
        case .acceleration: return "Ускорение"
        case .turn: return "Поворот"
        }
    }
    
    var icon: String {
        switch self {
        case .braking: return "⏹️"
        case .acceleration: return "⚡"
        case .turn: return "🔄"
        }
    }
}

struct DrivingViolation: Codable {
    let type: ViolationType
    let timestamp: Date
    let description: String
    let severity: ViolationSeverity
    
    var displayName: String {
        switch type {
        case .speedExceeded: return "Превышение скорости"
        case .harshBraking: return "Резкое торможение"
        case .harshAcceleration: return "Резкое ускорение"
        case .sharpTurn: return "Резкий поворот"
        }
    }
}

enum ViolationType: String, Codable {
    case speedExceeded = "speed_exceeded"
    case harshBraking = "harsh_braking"
    case harshAcceleration = "harsh_acceleration"
    case sharpTurn = "sharp_turn"
}

enum ViolationSeverity: String, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    
    var displayName: String {
        switch self {
        case .low: return "Низкая"
        case .medium: return "Средняя"
        case .high: return "Высокая"
        }
    }
    
    var color: String {
        switch self {
        case .low: return "warningOrange"
        case .medium: return "warningOrange"
        case .high: return "dangerRed"
        }
    }
}

struct DrivingStats: Codable {
    let totalTrips: Int
    let totalDistance: Double // км
    let totalDuration: TimeInterval // секунды
    let averageSafetyScore: Double // 0-10
    let violationsCount: Int
    let period: String // "week", "month", "year"
    let positioningSystem: String? // GPS, GLONASS, Galileo, BeiDou
    
    var formattedTotalDistance: String {
        String(format: "%.1f км", totalDistance)
    }
    
    var formattedTotalDuration: String {
        let hours = Int(totalDuration / 3600)
        let minutes = Int((totalDuration.truncatingRemainder(dividingBy: 3600)) / 60)
        if hours > 0 {
            return "\(hours)ч \(minutes)мин"
        } else {
            return "\(minutes)мин"
        }
    }
    
    var formattedAverageSafetyScore: String {
        String(format: "%.1f/10", averageSafetyScore)
    }
}

// MARK: - Dark Web Monitoring Models

struct DarkWebLeak: Identifiable, Codable {
    let id: String
    let dataType: LeakDataType
    let value: String // замаскированное значение (user@***.com)
    let fullValue: String? // полное значение (только для отображения)
    let leakDate: Date
    let discoveryDate: Date
    let source: String // название базы данных
    let severity: LeakSeverity
    let status: LeakStatus
    let recommendations: [String]
    
    var maskedValue: String {
        // Маскируем значение для безопасности
        if let full = fullValue {
            if dataType == .email {
                let components = full.split(separator: "@")
                if components.count == 2 {
                    let username = String(components[0])
                    let domain = String(components[1])
                    if username.count > 2 {
                        return "\(username.prefix(2))***@\(domain)"
                    }
                    return "***@\(domain)"
                }
            } else if dataType == .phone {
                if full.count > 4 {
                    return "***\(full.suffix(4))"
                }
            }
            return "***"
        }
        return value
    }
}

enum LeakDataType: String, Codable {
    case email = "email"
    case password = "password"
    case phone = "phone"
    case bank = "bank"
    case passport = "passport"
    case snils = "snils"
    
    var displayName: String {
        switch self {
        case .email: return "Email"
        case .password: return "Пароль"
        case .phone: return "Номер телефона"
        case .bank: return "Банковские данные"
        case .passport: return "Паспорт"
        case .snils: return "СНИЛС"
        }
    }
    
    var icon: String {
        switch self {
        case .email: return "✉️"
        case .password: return "🔑"
        case .phone: return "📱"
        case .bank: return "💳"
        case .passport: return "🆔"
        case .snils: return "📄"
        }
    }
}

enum LeakSeverity: String, Codable {
    case critical = "critical"
    case high = "high"
    case medium = "medium"
    case low = "low"
    
    var displayName: String {
        switch self {
        case .critical: return "Критично"
        case .high: return "Высокая"
        case .medium: return "Средняя"
        case .low: return "Низкая"
        }
    }
    
    var color: String {
        switch self {
        case .critical: return "dangerRed"
        case .high: return "dangerRed"
        case .medium: return "warningOrange"
        case .low: return "warningOrange"
        }
    }
}

enum LeakStatus: String, Codable {
    case new = "new"
    case inProgress = "in_progress"
    case resolved = "resolved"
    case ignored = "ignored"
    
    var displayName: String {
        switch self {
        case .new: return "Новая"
        case .inProgress: return "В процессе"
        case .resolved: return "Решено"
        case .ignored: return "Игнорируется"
        }
    }
}

struct DarkWebScan: Identifiable, Codable {
    let id: String
    let scanDate: Date
    let databasesScanned: Int
    let newLeaksFound: Int
    let status: ScanStatus
    
    var formattedScanDate: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: scanDate)
    }
}

enum ScanStatus: String, Codable {
    case completed = "completed"
    case inProgress = "in_progress"
    case failed = "failed"
    
    var displayName: String {
        switch self {
        case .completed: return "Завершено"
        case .inProgress: return "В процессе"
        case .failed: return "Ошибка"
        }
    }
}

struct DarkWebStats: Codable {
    let totalLeaks: Int
    let newLeaks: Int
    let resolvedLeaks: Int
    let criticalLeaks: Int
    let lastScanDate: Date?
    
    var formattedLastScanDate: String? {
        guard let date = lastScanDate else { return nil }
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

// MARK: - Identity Theft Protection Models

struct IdentityTheftAttempt: Identifiable, Codable {
    let id: String
    let dataType: IdentityDataType
    let requestSource: String // сайт/приложение
    let timestamp: Date
    let action: AttemptAction
    let severity: AttemptSeverity
    let details: String?
    
    var formattedTimestamp: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: timestamp)
    }
}

enum IdentityDataType: String, Codable {
    case passport = "passport"
    case snils = "snils"
    case bank = "bank"
    case other = "other"
    
    var displayName: String {
        switch self {
        case .passport: return "Паспорт"
        case .snils: return "СНИЛС"
        case .bank: return "Банковские данные"
        case .other: return "Другое"
        }
    }
    
    var icon: String {
        switch self {
        case .passport: return "🆔"
        case .snils: return "📄"
        case .bank: return "💳"
        case .other: return "📋"
        }
    }
}

enum AttemptAction: String, Codable {
    case blocked = "blocked"
    case allowed = "allowed"
    case suspicious = "suspicious"
    case requiresReview = "requires_review"
    
    var displayName: String {
        switch self {
        case .blocked: return "Заблокировано"
        case .allowed: return "Разрешено"
        case .suspicious: return "Подозрительно"
        case .requiresReview: return "Требуется проверка"
        }
    }
    
    var icon: String {
        switch self {
        case .blocked: return "🚫"
        case .allowed: return "✅"
        case .suspicious: return "⚠️"
        case .requiresReview: return "🔍"
        }
    }
}

enum AttemptSeverity: String, Codable {
    case critical = "critical"
    case high = "high"
    case medium = "medium"
    case low = "low"
    
    var displayName: String {
        switch self {
        case .critical: return "Критично"
        case .high: return "Высокая"
        case .medium: return "Средняя"
        case .low: return "Низкая"
        }
    }
}

struct IdentityTheftStats: Codable {
    let totalAttempts: Int
    let blockedAttempts: Int
    let suspiciousActivities: Int
    let byDataType: [String: Int] // "passport": 12, "snils": 8
}

// MARK: - Privacy Reports Models

// Location Bubble
struct LocationRequest: Identifiable, Codable {
    let id: String
    let appName: String
    let timestamp: Date
    let action: LocationRequestAction
    let accuracy: LocationAccuracy?
    
    var formattedTimestamp: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: timestamp)
    }
}

enum LocationRequestAction: String, Codable {
    case blocked = "blocked"
    case allowed = "allowed"
    case modified = "modified" // Показано приблизительное
    
    var displayName: String {
        switch self {
        case .blocked: return "Заблокировано"
        case .allowed: return "Разрешено"
        case .modified: return "Показано приблизительное"
        }
    }
    
    var icon: String {
        switch self {
        case .blocked: return "🚫"
        case .allowed: return "✅"
        case .modified: return "📍"
        }
    }
}

enum LocationAccuracy: String, Codable {
    case high = "high" // 100м
    case medium = "medium" // 300м
    case low = "low" // 500м
    
    var displayName: String {
        switch self {
        case .high: return "Высокая (100м)"
        case .medium: return "Средняя (300м)"
        case .low: return "Низкая (500м)"
        }
    }
    
    var meters: Int {
        switch self {
        case .high: return 100
        case .medium: return 300
        case .low: return 500
        }
    }
}

struct LocationStats: Codable {
    let blockedRequests: Int
    let allowedRequests: Int
    let modifiedRequests: Int
    let currentAccuracy: LocationAccuracy
}

// Data Cleanup
struct DataCleanupRecord: Identifiable, Codable {
    let id: String
    let cleanupDate: Date
    let freedSpace: Int64 // байты
    let categories: [CleanupCategory]
    
    var formattedFreedSpace: String {
        formatBytes(freedSpace)
    }
    
    var formattedDate: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: cleanupDate)
    }
    
    private func formatBytes(_ bytes: Int64) -> String {
        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useMB, .useGB]
        formatter.countStyle = .file
        return formatter.string(fromByteCount: bytes)
    }
}

struct CleanupCategory: Codable {
    let name: String
    let size: Int64 // байты
    
    var formattedSize: String {
        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useMB, .useGB]
        formatter.countStyle = .file
        return formatter.string(fromByteCount: size)
    }
}

struct DataCleanupStats: Codable {
    let totalFreed: Int64 // байты
    let lastCleanupDate: Date?
    let cleanupsCount: Int
    let byCategory: [String: Int64] // "cache": 1200000000
    
    var formattedTotalFreed: String {
        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useMB, .useGB]
        formatter.countStyle = .file
        return formatter.string(fromByteCount: totalFreed)
    }
}

// Anti Tracker
struct TrackerBlock: Identifiable, Codable {
    let id: String
    let trackerName: String
    let blockedCount: Int
    let lastBlocked: Date?
    
    var formattedLastBlocked: String? {
        guard let date = lastBlocked else { return nil }
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

struct AntiTrackerStats: Codable {
    let totalBlocked: Int
    let blockedThisWeek: Int
    let effectiveness: Double // 0-100%
    let topTrackers: [TrackerBlock]
    
    var formattedEffectiveness: String {
        String(format: "%.0f%%", effectiveness)
    }
}

// MARK: - AI Categories Models

struct AICategoryReport: Identifiable, Codable {
    let id: String
    let childId: String?
    let childName: String?
    let category: ContentCategory
    let sitesCount: Int
    let blockedCount: Int
    
    var blockedPercentage: Double {
        guard sitesCount > 0 else { return 0 }
        return Double(blockedCount) / Double(sitesCount) * 100
    }
}

enum ContentCategory: String, Codable, CaseIterable {
    case education = "education"
    case games = "games"
    case entertainment = "entertainment"
    case adult = "adult"
    case violence = "violence"
    case other = "other"
    
    var displayName: String {
        switch self {
        case .education: return "Образование"
        case .games: return "Игры"
        case .entertainment: return "Развлечения"
        case .adult: return "Взрослый контент"
        case .violence: return "Насилие"
        case .other: return "Другое"
        }
    }
    
    var icon: String {
        switch self {
        case .education: return "📚"
        case .games: return "🎮"
        case .entertainment: return "🎬"
        case .adult: return "🔞"
        case .violence: return "⚠️"
        case .other: return "📋"
        }
    }
}

struct AICategoriesStats: Codable {
    let totalCategorized: Int
    let totalBlocked: Int
    let accuracy: Double // 0-100%
    let byCategory: [String: Int] // "education": 145
    let blockedByCategory: [String: Int] // "adult": 12
    
    var formattedAccuracy: String {
        String(format: "%.0f%%", accuracy)
    }
}

// MARK: - Helper Extensions

extension DateFormatter {
    static let iso8601: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        return formatter
    }()
}

extension JSONDecoder {
    static let componentReportsDecoder: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)
            
            if let date = DateFormatter.iso8601.date(from: dateString) {
                return date
            }
            
            // Fallback на другие форматы
            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ssZ"
            if let date = formatter.date(from: dateString) {
                return date
            }
            
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Cannot decode date string \(dateString)"
            )
        }
        return decoder
    }()
}

extension JSONEncoder {
    static let componentReportsEncoder: JSONEncoder = {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .custom { date, encoder in
            var container = encoder.singleValueContainer()
            let dateString = DateFormatter.iso8601.string(from: date)
            try container.encode(dateString)
        }
        return encoder
    }()
}

// MARK: - Localization Extensions

extension DrivingReport {
    func localizedFormattedDistance(_ localizationManager: LocalizationManager) -> String {
        String(format: "%.1f %@", distance, localizationManager.localized("driving_reports_unit_km"))
    }
    
    func localizedFormattedAverageSpeed(_ localizationManager: LocalizationManager) -> String {
        String(format: "%.0f %@", averageSpeed, localizationManager.localized("driving_reports_unit_km"))
    }
}

extension DrivingEvent {
    func localizedSeverityLevel(_ localizationManager: LocalizationManager) -> String {
        if severity >= 0.8 {
            return localizationManager.localized("driving_event_severity_sharp")
        } else if severity >= 0.5 {
            return localizationManager.localized("driving_event_severity_medium")
        } else {
            return localizationManager.localized("driving_event_severity_soft")
        }
    }
}

extension DrivingEventType {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .braking: return localizationManager.localized("driving_event_type_braking")
        case .acceleration: return localizationManager.localized("driving_event_type_acceleration")
        case .turn: return localizationManager.localized("driving_event_type_turn")
        }
    }
}

extension DrivingViolation {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch type {
        case .speedExceeded: return localizationManager.localized("driving_violation_speed_exceeded")
        case .harshBraking: return localizationManager.localized("driving_violation_harsh_braking")
        case .harshAcceleration: return localizationManager.localized("driving_violation_harsh_acceleration")
        case .sharpTurn: return localizationManager.localized("driving_violation_sharp_turn")
        }
    }
}

extension ViolationSeverity {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .low: return localizationManager.localized("violation_severity_low")
        case .medium: return localizationManager.localized("violation_severity_medium")
        case .high: return localizationManager.localized("violation_severity_high")
        }
    }
}

extension DrivingStats {
    func localizedFormattedTotalDistance(_ localizationManager: LocalizationManager) -> String {
        String(format: "%.1f %@", totalDistance, localizationManager.localized("driving_reports_unit_km"))
    }
    
    func localizedFormattedTotalDuration(_ localizationManager: LocalizationManager) -> String {
        let hours = Int(totalDuration / 3600)
        let minutes = Int((totalDuration.truncatingRemainder(dividingBy: 3600)) / 60)
        if hours > 0 {
            return "\(hours)\(localizationManager.localized("driving_reports_unit_hour")) \(minutes)\(localizationManager.localized("driving_reports_unit_min"))"
        } else {
            return "\(minutes)\(localizationManager.localized("driving_reports_unit_min"))"
        }
    }
}

extension LeakStatus {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .new: return localizationManager.localized("dark_web_leak_status_new")
        case .inProgress: return localizationManager.localized("dark_web_scan_status_in_progress")
        case .resolved: return localizationManager.localized("dark_web_leak_status_resolved")
        case .ignored: return localizationManager.localized("dark_web_leak_status_resolved") // Используем тот же ключ
        }
    }
}

extension LeakSeverity {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .critical: return localizationManager.localized("dark_web_severity_critical")
        case .high: return localizationManager.localized("dark_web_severity_high")
        case .medium: return localizationManager.localized("dark_web_severity_high") // Используем тот же ключ
        case .low: return localizationManager.localized("dark_web_severity_high") // Используем тот же ключ
        }
    }
}

extension ScanStatus {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .completed: return localizationManager.localized("dark_web_scan_status_completed")
        case .inProgress: return localizationManager.localized("dark_web_scan_status_in_progress")
        case .failed: return localizationManager.localized("dark_web_scan_status_failed")
        }
    }
}

extension AttemptAction {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .blocked: return localizationManager.localized("identity_theft_action_blocked")
        case .allowed: return localizationManager.localized("identity_theft_action_allowed")
        case .suspicious: return localizationManager.localized("identity_theft_action_suspicious")
        case .requiresReview: return localizationManager.localized("identity_theft_action_suspicious") // Используем тот же ключ
        }
    }
}

extension AttemptSeverity {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .critical: return localizationManager.localized("dark_web_severity_critical")
        case .high: return localizationManager.localized("dark_web_severity_high")
        case .medium: return localizationManager.localized("violation_severity_medium")
        case .low: return localizationManager.localized("violation_severity_low")
        }
    }
}

extension LeakDataType {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .email: return localizationManager.localized("identity_theft_data_type_email")
        case .password: return localizationManager.localized("identity_theft_data_type_password")
        case .phone: return localizationManager.localized("identity_theft_data_type_phone")
        case .bank: return localizationManager.localized("identity_theft_data_type_card")
        case .passport: return localizationManager.localized("identity_theft_data_type_passport")
        case .snils: return localizationManager.localized("identity_theft_data_type_passport") // Используем тот же ключ
        }
    }
}

extension IdentityDataType {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .passport: return localizationManager.localized("identity_theft_data_type_passport")
        case .snils: return localizationManager.localized("identity_theft_data_type_passport") // Используем тот же ключ
        case .bank: return localizationManager.localized("identity_theft_data_type_card")
        case .other: return localizationManager.localized("identity_theft_data_type_passport") // Используем тот же ключ
        }
    }
}

extension LocationRequestAction {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .blocked: return localizationManager.localized("privacy_location_action_blocked")
        case .allowed: return localizationManager.localized("privacy_location_action_allowed")
        case .modified: return localizationManager.localized("privacy_location_action_modified_approx")
        }
    }
}

extension LocationAccuracy {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .high: return localizationManager.localized("privacy_location_accuracy_high_with_meters")
        case .medium: return localizationManager.localized("privacy_location_accuracy_medium_with_meters")
        case .low: return localizationManager.localized("privacy_location_accuracy_low_with_meters")
        }
    }
}

extension ContentCategory {
    func localizedDisplayName(_ localizationManager: LocalizationManager) -> String {
        let key = "ai_categories_category_\(self.rawValue)"
        let localized = localizationManager.localized(key)
        // Если ключ не найден, используем дефолтное значение
        return localized != key ? localized : displayName
    }
}

// MARK: - Dark Web Hybrid Scan Models

/// Метод сканирования темной сети
enum DarkWebScanMethod: String, Codable, CaseIterable {
    case secure = "secure"  // Хеширование
    case fast = "fast"      // Без хеширования
    
    func displayName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .secure:
            return localizationManager.localized("dark_web_scan_method_secure")
        case .fast:
            return localizationManager.localized("dark_web_scan_method_fast")
        }
    }
    
    var icon: String {
        switch self {
        case .secure: return "lock.shield.fill"
        case .fast: return "bolt.fill"
        }
    }
}

/// Запрос на сканирование темной сети
struct DarkWebScanRequest: Codable {
    // Для безопасного сканирования (хеши)
    let emailHash: String?
    let passwordHash: String?
    
    // Для быстрого сканирования (plaintext)
    let email: String?
    let phone: String?
    let passport: String?
    let snils: String?
    
    let method: String  // "secure" или "fast"
}

/// Результат сканирования темной сети
struct DarkWebScanResult: Codable, Identifiable {
    let id: String
    let dataType: String  // "email", "password", "phone", "passport", "snils"
    let found: Bool
    let leakDate: Date?
    let source: String?
    let severity: String?
    let recommendations: [String]?
}

/// Хеш для безопасного сканирования
struct DarkWebHash: Codable {
    let type: String  // "email", "phone", "password", "snils", "passport"
    let hash: String
}

/// Результат сканирования (утечка)
struct DarkWebLeakResult: Identifiable, Codable {
    let id: String
    let dataType: LeakDataType
    let value: String? // Original value if plaintext scan, or masked if secure
    let leakDate: Date
    let discoveryDate: Date?
    let source: String
    let severity: LeakSeverity
    let status: LeakStatus
    let recommendations: [String]
}

