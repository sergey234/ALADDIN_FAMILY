import Foundation

// Импортируем DataSource из AnalyticsService
// DataSource определен в Core/Analytics/AnalyticsService.swift

// MARK: - Component Analytics Models

/// Статистика одного компонента защиты
struct ComponentStats: Codable {
    let componentId: String
    let metrics: [String: String] // Гибкая структура для разных компонентов
    let dataSource: DataSource
    
    // Вспомогательные методы для получения метрик
    func getMetric(key: String) -> String {
        return metrics[key] ?? "0"
    }
    
    func getIntMetric(key: String) -> Int {
        return Int(metrics[key] ?? "0") ?? 0
    }
    
    func getDoubleMetric(key: String) -> Double {
        return Double(metrics[key] ?? "0") ?? 0.0
    }
}

/// Аналитика всех компонентов защиты
struct ComponentsAnalytics: Codable {
    let drivingReports: ComponentStats?
    let darkWeb: ComponentStats?
    let identityTheft: ComponentStats?
    let locationBubble: ComponentStats?
    let dataCleanup: ComponentStats?
    let antiTracker: ComponentStats?
    let aiCategories: ComponentStats?
    
    /// Получить статистику компонента по ID
    func getStats(for componentId: String) -> ComponentStats? {
        switch componentId {
        case "driving_reports_agent", "driving":
            return drivingReports
        case "dark_web_monitoring_agent", "darkweb":
            return darkWeb
        case "russian_identity_theft_protection_agent", "identity":
            return identityTheft
        case "location_bubble_agent", "location":
            return locationBubble
        case "personal_data_cleanup_agent", "cleanup":
            return dataCleanup
        case "anti_tracker_agent", "tracker":
            return antiTracker
        case "ai_categories_agent", "ai":
            return aiCategories
        default:
            return nil
        }
    }
}

// MARK: - Component Response Models (для парсинга API ответов)

/// Ответ API для статистики вождения
struct DrivingStatsResponse: Codable {
    let trips: Int?
    let safety_score: Double?
    let new_events: Int?
}

/// Ответ API для статистики Dark Web
struct DarkWebStatsResponse: Codable {
    let leaks_found: Int?
    let new_leaks: Int?
    let new_events: Int?
}

/// Ответ API для статистики Identity Theft
struct IdentityTheftStatsResponse: Codable {
    let attempts: Int?
    let blocked: Int?
}

/// Ответ API для статистики Location Bubble
struct LocationStatsResponse: Codable {
    let blocked: Int?
    let accuracy: String?
}

/// Ответ API для статистики Data Cleanup
struct DataCleanupStatsResponse: Codable {
    let freed_space_gb: Double?
    let last_cleanup_hours_ago: Int?
}

/// Ответ API для статистики Anti Tracker
struct AntiTrackerStatsResponse: Codable {
    let blocked_total: Int?
    let blocked_this_week: Int?
}

/// Ответ API для статистики AI Categories
struct AICategoriesStatsResponse: Codable {
    let categorized: Int?
    let blocked: Int?
}
