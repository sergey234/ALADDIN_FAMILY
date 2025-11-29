import Foundation

/// 🌐 Remote Analytics Service
/// Подключение к реальному API аналитики
/// 
/// ⚠️ Сейчас используется fallback на LocalAnalyticsService (API еще не готов)
/// Когда API будет готов - замените fallback на реальные запросы

enum AnalyticsAPIError: Error {
    case invalidURL
    case badStatus(Int)
    case decoding(Error)
    case transport(Error)
}

final class RemoteAnalyticsService: AnalyticsService {
    private let baseURL: URL
    private let authTokenProvider: () -> String?
    private let urlSession: URLSession
    private let fallbackService: LocalAnalyticsService
    
    init(baseURL: URL = URL(string: "https://api.aladdin.family")!,
         authTokenProvider: @escaping () -> String? = { nil },
         urlSession: URLSession = .shared) {
        self.baseURL = baseURL
        self.authTokenProvider = authTokenProvider
        self.urlSession = urlSession
        self.fallbackService = LocalAnalyticsService()
    }
    
    // MARK: - AnalyticsService Protocol
    
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary {
        // ✅ TODO: Когда API будет готов - заменить на реальный запрос
        // Пример:
        // let url = baseURL.appendingPathComponent("/v1/analytics/summary")
        // var request = URLRequest(url: url)
        // request.addValue("Bearer \(authTokenProvider() ?? "")", forHTTPHeaderField: "Authorization")
        // let (data, _) = try await urlSession.data(for: request)
        // return try JSONDecoder().decode(AnalyticsSummary.self, from: data)
        
        // Сейчас используем fallback на LocalAnalyticsService
        return try await fallbackService.fetchSummary(period: period, filters: filters)
    }
    
    func fetchSecurityAnalytics(period: String) async throws -> SecurityAnalytics {
        // ✅ TODO: Когда API будет готов - заменить на реальный запрос
        return try await fallbackService.fetchSecurityAnalytics(period: period)
    }
    
    func fetchFamilyAnalytics(period: String) async throws -> FamilyAnalytics {
        // ✅ TODO: Когда API будет готов - заменить на реальный запрос
        return try await fallbackService.fetchFamilyAnalytics(period: period)
    }
    
    func fetchUsageAnalytics(period: String) async throws -> UsageAnalytics {
        // ✅ TODO: Когда API будет готов - заменить на реальный запрос
        return try await fallbackService.fetchUsageAnalytics(period: period)
    }
    
    func fetchDevicesAnalytics(period: String) async throws -> DevicesAnalytics {
        // ✅ TODO: Когда API будет готов - заменить на реальный запрос
        return try await fallbackService.fetchDevicesAnalytics(period: period)
    }
}
