import Foundation

/// 🌐 Remote Analytics Service
/// Работает с backend FastAPI (unified security analytics)

enum AnalyticsAPIError: Error {
    case invalidURL
    case invalidResponse
    case badStatus(Int)
    case decoding(Error)
    case transport(Error)
}

final class RemoteAnalyticsService: AnalyticsService {
    private let baseURL: URL
    private let authTokenProvider: () -> String?
    private let urlSession: URLSession
    private let fallbackService: LocalAnalyticsService
    private let decoder: JSONDecoder
    
    init(baseURL: URL? = nil,
         authTokenProvider: @escaping () -> String? = { nil },
         urlSession: URLSession = .shared) {
        self.baseURL = baseURL ?? RemoteAnalyticsService.defaultBaseURL
        self.authTokenProvider = authTokenProvider
        self.urlSession = urlSession
        self.fallbackService = LocalAnalyticsService()
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        self.decoder = decoder
    }
    
    private static var defaultBaseURL: URL {
        if let url = URL(string: AppConfig.baseURL) {
            return url
        }
        return URL(string: "https://api.aladdin.family/api")!
    }
    
    // MARK: - AnalyticsService Protocol
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary {
        do {
            let response: DashboardResponse = try await performGET(path: "/security/unified-dashboard")
            return AnalyticsSummary(
                threatsDetected: response.totalThreatsBlocked,
                threatsBlocked: response.vpnThreats,
                itemsScanned: response.avThreats,
                protectionLevel: max(0, min(response.securityScore, 100))
            )
        } catch {
            print("[RemoteAnalyticsService] summary request failed: \(error)")
            return try await fallbackService.fetchSummary(period: period, filters: filters)
        }
    }
    
    func fetchSecurityAnalytics(period: String) async throws -> SecurityAnalytics {
        do {
            let fallback = try? await fallbackService.fetchSecurityAnalytics(period: period)
            let response: UnifiedStatsResponse = try await performGET(path: "/security/unified-stats")
            let categories = convertCategories(from: response)
            return SecurityAnalytics(
                blockedThreats: categories,
                recentThreats: fallback?.recentThreats ?? [],
                vpnStats: fallback?.vpnStats ?? AnalyticsVPNStats(today: "—", week: "—", protection: "—")
            )
        } catch {
            print("[RemoteAnalyticsService] security analytics request failed: \(error)")
            return try await fallbackService.fetchSecurityAnalytics(period: period)
        }
    }
    
    func fetchFamilyAnalytics(period: String) async throws -> FamilyAnalytics {
        return try await fallbackService.fetchFamilyAnalytics(period: period)
    }
    
    func fetchUsageAnalytics(period: String) async throws -> UsageAnalytics {
        return try await fallbackService.fetchUsageAnalytics(period: period)
    }
    
    func fetchDevicesAnalytics(period: String) async throws -> DevicesAnalytics {
        return try await fallbackService.fetchDevicesAnalytics(period: period)
    }
    
    // MARK: - Networking helper
    private func performGET<T: Decodable>(path: String, queryItems: [URLQueryItem] = []) async throws -> T {
        guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else {
            throw AnalyticsAPIError.invalidURL
        }
        
        let normalizedPath = path.hasPrefix("/") ? path : "/" + path
        let basePath = components.path == "/" ? "" : components.path
        components.path = basePath + normalizedPath
        components.queryItems = queryItems.isEmpty ? nil : queryItems
        guard let url = components.url else {
            throw AnalyticsAPIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if let rawToken = authTokenProvider()?.trimmingCharacters(in: .whitespacesAndNewlines), !rawToken.isEmpty {
            request.addValue("Bearer \(rawToken)", forHTTPHeaderField: "Authorization")
        }
        
        do {
            let (data, response) = try await urlSession.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw AnalyticsAPIError.invalidResponse
            }
            guard (200..<300).contains(httpResponse.statusCode) else {
                throw AnalyticsAPIError.badStatus(httpResponse.statusCode)
            }
            do {
                return try decoder.decode(T.self, from: data)
            } catch {
                throw AnalyticsAPIError.decoding(error)
            }
        } catch let error as URLError {
            throw AnalyticsAPIError.transport(error)
        } catch {
            throw error
        }
    }
    
    // MARK: - Mapping helpers
    private func convertCategories(from response: UnifiedStatsResponse) -> [ThreatTypeCount] {
        var combined: [String: Int] = [:]
        if let vpnCategories = response.vpnStats?.threatsByCategory {
            for (key, value) in vpnCategories {
                let normalized = normalizeCategoryKey(key)
                combined[normalized, default: 0] += value
            }
        }
        if let avCategories = response.avStats?.threatsByCategory {
            for (key, value) in avCategories {
                let normalized = normalizeCategoryKey(key)
                combined[normalized, default: 0] += value
            }
        }
        let sorted = combined.sorted { $0.value > $1.value }
        return sorted.map { ThreatTypeCount(type: $0.key, count: $0.value, icon: iconName(for: $0.key)) }
    }
    
    private func normalizeCategoryKey(_ key: String) -> String {
        switch key.lowercased() {
        case "vpn_blocked", "network_attack", "data_exfiltration":
            return "network"
        case "malware_detected", "virus_detected", "suspicious_file":
            return "file"
        case "phishing":
            return "web"
        case "app_misuse", "unauthorized_app":
            return "app"
        default:
            return key.lowercased()
        }
    }
    
    private func iconName(for key: String) -> String {
        switch key.lowercased() {
        case "network": return "shield"
        case "file": return "doc"
        case "web": return "globe"
        case "app": return "iphone"
        default: return "shield"
        }
    }
}

// MARK: - DTOs

private struct DashboardResponse: Decodable {
    let totalThreatsBlocked: Int
    let vpnThreats: Int
    let avThreats: Int
    let securityScore: Double
}

private struct UnifiedStatsResponse: Decodable {
    struct StatsBlock: Decodable {
        let threatsByCategory: [String: Int]?
    }
    
    let vpnThreatsBlocked: Int
    let avThreatsDetected: Int
    let totalThreats: Int
    let vpnStats: StatsBlock?
    let avStats: StatsBlock?
    let securityLevel: String
    let recommendations: [String]?
}
