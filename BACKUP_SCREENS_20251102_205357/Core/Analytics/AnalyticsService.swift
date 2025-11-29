import Foundation

// MARK: - Data Models

struct AnalyticsFilters: Equatable {
    let onlyBlocked: Bool
    let includeFamily: Bool
    let includeDevices: Bool
}

struct AnalyticsSummary: Codable, Equatable {
    let threatsDetected: Int
    let threatsBlocked: Int
    let itemsScanned: Int
    let protectionLevel: Double
}

// MARK: - Service Protocol

protocol AnalyticsService {
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary
}

// MARK: - Local Implementation (initial, switchable later)

final class LocalAnalyticsService: AnalyticsService {
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary {
        switch period {
        case "day":
            return AnalyticsSummary(threatsDetected: 12, threatsBlocked: 12, itemsScanned: 847, protectionLevel: 96)
        case "week":
            return AnalyticsSummary(threatsDetected: 47, threatsBlocked: 45, itemsScanned: 5234, protectionLevel: 96)
        case "month":
            return AnalyticsSummary(threatsDetected: 189, threatsBlocked: 185, itemsScanned: 21890, protectionLevel: 98)
        default:
            return AnalyticsSummary(threatsDetected: 0, threatsBlocked: 0, itemsScanned: 0, protectionLevel: 0)
        }
    }
}







