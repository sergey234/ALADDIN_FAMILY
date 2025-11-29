import Foundation

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
    private let cacheTTL: TimeInterval = 300
    private var cache: [String: (date: Date, summary: AnalyticsSummary)] = [:]
    
    init(baseURL: URL = URL(string: "https://api.aladdin.family")!,
         authTokenProvider: @escaping () -> String? = { nil },
         urlSession: URLSession = .shared) {
        self.baseURL = baseURL
        self.authTokenProvider = authTokenProvider
        self.urlSession = urlSession
    }
    
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary {
        let cacheKey = "p=\(period)|b=\(filters.onlyBlocked)|f=\(filters.includeFamily)|d=\(filters.includeDevices)"
        if let entry = cache[cacheKey], Date().timeIntervalSince(entry.date) < cacheTTL {
            return entry.summary
        }
        var components = URLComponents(url: baseURL.appendingPathComponent("/v1/analytics/summary"), resolvingAgainstBaseURL: false)
        components?.queryItems = [
            URLQueryItem(name: "period", value: period),
            URLQueryItem(name: "onlyBlocked", value: filters.onlyBlocked ? "1" : "0"),
            URLQueryItem(name: "includeFamily", value: filters.includeFamily ? "1" : "0"),
            URLQueryItem(name: "includeDevices", value: filters.includeDevices ? "1" : "0")
        ]
        guard let url = components?.url else { throw AnalyticsAPIError.invalidURL }
        var request = URLRequest(url: url)
        request.timeoutInterval = 15
        request.cachePolicy = .reloadRevalidatingCacheData
        if let token = authTokenProvider() {
            request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        NetworkLogger.logRequest(request)
        
        var lastError: Error?
        let maxAttempts = 3
        var delay: UInt64 = 200_000_000 // 200ms
        let start = Date()
        for attempt in 1...maxAttempts {
            do {
                let (data, response) = try await urlSession.data(for: request)
                NetworkLogger.logResponse(response, data: data)
                if let http = response as? HTTPURLResponse, !(200...299).contains(http.statusCode) {
                    lastError = AnalyticsAPIError.badStatus(http.statusCode)
                } else {
                    do {
                        let decoder = JSONDecoder()
                        decoder.keyDecodingStrategy = .convertFromSnakeCase
                        let summary = try decoder.decode(AnalyticsSummary.self, from: data)
                        cache[cacheKey] = (date: Date(), summary: summary)
                        let elapsed = Date().timeIntervalSince(start)
                        print("AnalyticsAPI summary OK in \(String(format: "%.2f", elapsed))s (attempt \(attempt))")
                        return summary
                    } catch {
                        lastError = AnalyticsAPIError.decoding(error)
                    }
                }
            } catch {
                lastError = AnalyticsAPIError.transport(error)
            }
            if attempt < maxAttempts { try? await Task.sleep(nanoseconds: delay); delay *= 2 }
        }
        if let entry = cache[cacheKey] { return entry.summary }
        throw lastError ?? AnalyticsAPIError.invalidURL
    }
}


