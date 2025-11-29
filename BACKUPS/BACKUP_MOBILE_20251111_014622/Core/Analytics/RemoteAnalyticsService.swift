import Foundation

/// 🌐 Remote Analytics Service
/// Подключение к реальному API аналитики
/// 
/// ⚠️ Сейчас используется fallback на LocalAnalyticsService (API еще не готов)
/// Когда API будет готов - замените fallback на реальные запросы

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
    
    init(baseURL: URL = URL(string: "https://api.aladdin.family")!,
         authTokenProvider: @escaping () -> String? = { nil },
         urlSession: URLSession = .shared) {
        self.baseURL = baseURL
        self.authTokenProvider = authTokenProvider
        self.urlSession = urlSession
        self.fallbackService = LocalAnalyticsService()
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        self.decoder = decoder
    }
    
    // MARK: - AnalyticsService Protocol
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary {
        do {
            let queryItems = [
                URLQueryItem(name: "period", value: period),
                URLQueryItem(name: "only_blocked", value: filters.onlyBlocked ? "true" : "false"),
                URLQueryItem(name: "include_family", value: filters.includeFamily ? "true" : "false"),
                URLQueryItem(name: "include_devices", value: filters.includeDevices ? "true" : "false")
            ]
            return try await performGET(path: "/v1/analytics/summary", queryItems: queryItems)
        } catch {
            print("[RemoteAnalyticsService] summary request failed: \(error)")
            return try await fallbackService.fetchSummary(period: period, filters: filters)
        }
    }
    
    func fetchSecurityAnalytics(period: String) async throws -> SecurityAnalytics {
        do {
            let queryItems = [URLQueryItem(name: "period", value: period)]
            return try await performGET(path: "/v1/analytics/security", queryItems: queryItems)
        } catch {
            print("[RemoteAnalyticsService] security analytics request failed: \(error)")
            return try await fallbackService.fetchSecurityAnalytics(period: period)
        }
    }
    
    func fetchFamilyAnalytics(period: String) async throws -> FamilyAnalytics {
        do {
            let queryItems = [URLQueryItem(name: "period", value: period)]
            return try await performGET(path: "/v1/analytics/family", queryItems: queryItems)
        } catch {
            print("[RemoteAnalyticsService] family analytics request failed: \(error)")
            return try await fallbackService.fetchFamilyAnalytics(period: period)
        }
    }
    
    func fetchUsageAnalytics(period: String) async throws -> UsageAnalytics {
        do {
            let queryItems = [URLQueryItem(name: "period", value: period)]
            return try await performGET(path: "/v1/analytics/usage", queryItems: queryItems)
        } catch {
            print("[RemoteAnalyticsService] usage analytics request failed: \(error)")
            return try await fallbackService.fetchUsageAnalytics(period: period)
        }
    }
    
    func fetchDevicesAnalytics(period: String) async throws -> DevicesAnalytics {
        do {
            let queryItems = [URLQueryItem(name: "period", value: period)]
            return try await performGET(path: "/v1/analytics/devices", queryItems: queryItems)
        } catch {
            print("[RemoteAnalyticsService] devices analytics request failed: \(error)")
            return try await fallbackService.fetchDevicesAnalytics(period: period)
        }
    }
    
    // MARK: - Networking helper
    private func performGET<T: Decodable>(path: String, queryItems: [URLQueryItem]) async throws -> T {
        guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else {
            throw AnalyticsAPIError.invalidURL
        }
        components.path = path
        components.queryItems = queryItems.isEmpty ? nil : queryItems
        guard let url = components.url else {
            throw AnalyticsAPIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
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
}
