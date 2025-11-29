import Foundation
// import Firebase // Uncomment when Firebase SDK added

/**
 * 📊 Analytics Manager
 * Управление аналитикой пользователей
 * Firebase Analytics интеграция
 */

class AnalyticsManager {
    
    // MARK: - Singleton
    
    static let shared = AnalyticsManager()
    
    private init() {
        // Firebase будет инициализирован в AppDelegate
    }
    
    // MARK: - Screen Tracking
    
    /**
     * Отслеживать просмотр экрана
     */
    func trackScreen(_ screenName: String, screenClass: String? = nil) {
        #if DEBUG
        print("📊 Screen: \(screenName)")
        #endif
        
        // В production:
        // Analytics.logEvent(AnalyticsEventScreenView, parameters: [
        //     AnalyticsParameterScreenName: screenName,
        //     AnalyticsParameterScreenClass: screenClass ?? screenName
        // ])
    }
    
    // MARK: - Event Tracking
    
    /**
     * Отслеживать событие
     */
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        #if DEBUG
        print("📊 Event: \(eventName), params: \(parameters ?? [:])")
        #endif
        
        // В production:
        // Analytics.logEvent(eventName, parameters: parameters)
    }
    
    // MARK: - User Properties
    
    /**
     * Установить свойство пользователя
     */
    func setUserProperty(_ value: String?, forName name: String) {
        #if DEBUG
        print("📊 User Property: \(name) = \(value ?? "nil")")
        #endif
        
        // В production:
        // Analytics.setUserProperty(value, forName: name)
    }
    
    /**
     * Установить User ID
     */
    func setUserID(_ userID: String?) {
        #if DEBUG
        print("📊 User ID: \(userID ?? "nil")")
        #endif
        
        // В production:
        // Analytics.setUserID(userID)
    }
    
    // MARK: - Predefined Events
    
    /**
     * Отследить вход пользователя
     */
    func trackLogin(method: String) {
        trackEvent("login", parameters: ["method": method])
    }
    
    /**
     * Отследить регистрацию
     */
    func trackSignUp(method: String) {
        trackEvent("sign_up", parameters: ["method": method])
    }
    
    /**
     * Отследить подписку
     */
    func trackPurchase(subscriptionID: String, price: Double, currency: String = "RUB") {
        trackEvent("purchase", parameters: [
            "subscription_id": subscriptionID,
            "value": price,
            "currency": currency
        ])
    }
    
    /**
     * Отследить VPN подключение
     */
    func trackVPNConnect(server: String) {
        trackEvent("vpn_connect", parameters: ["server": server])
    }
    
    /**
     * Отследить VPN отключение
     */
    func trackVPNDisconnect() {
        trackEvent("vpn_disconnect")
    }
    
    /**
     * Отследить добавление члена семьи
     */
    func trackAddFamilyMember(role: String) {
        trackEvent("add_family_member", parameters: ["role": role])
    }
    
    /**
     * Отследить блокировку угрозы
     */
    func trackThreatBlocked(type: String) {
        trackEvent("threat_blocked", parameters: ["threat_type": type])
    }
    
    /**
     * Отследить использование AI помощника
     */
    func trackAIAssistantMessage() {
        trackEvent("ai_assistant_message")
    }
    
    /**
     * Отследить использование родительского контроля
     */
    func trackParentalControlUsed(action: String) {
        trackEvent("parental_control", parameters: ["action": action])
    }
    
    /**
     * Отследить добавление устройства
     */
    func trackAddDevice(deviceType: String) {
        trackEvent("add_device", parameters: ["device_type": deviceType])
    }
    
    /**
     * Отследить реферальное приглашение
     */
    func trackReferralShare(method: String) {
        trackEvent("referral_share", parameters: ["method": method])
    }
    
    /**
     * Отследить сообщение в семейном чате
     */
    func trackFamilyChatMessage() {
        trackEvent("family_chat_message")
    }
    
    // MARK: - Conversion Tracking
    
    /**
     * Отследить начало бесплатного триала
     */
    func trackTrialStarted(subscriptionID: String) {
        trackEvent("trial_started", parameters: ["subscription_id": subscriptionID])
    }
    
    /**
     * Отследить конверсию из триала в подписку
     */
    func trackTrialConverted(subscriptionID: String) {
        trackEvent("trial_converted", parameters: ["subscription_id": subscriptionID])
    }
    
    /**
     * Отследить отмену подписки
     */
    func trackSubscriptionCancelled(subscriptionID: String, reason: String?) {
        var params: [String: Any] = ["subscription_id": subscriptionID]
        if let reason = reason {
            params["cancellation_reason"] = reason
        }
        trackEvent("subscription_cancelled", parameters: params)
    }
}

// MARK: - Analytics Events Constants

enum AnalyticsEvent {
    static let appLaunched = "app_launched"
    static let appBackgrounded = "app_backgrounded"
    static let appForegrounded = "app_foregrounded"
    static let screenView = "screen_view"
    static let buttonTapped = "button_tapped"
    static let errorOccurred = "error_occurred"
}

// MARK: - Analytics Parameters Constants

enum AnalyticsParameter {
    static let screenName = "screen_name"
    static let buttonName = "button_name"
    static let errorMessage = "error_message"
    static let userId = "user_id"
    static let subscriptionType = "subscription_type"
}

// MARK: - Analytics Data Layer (inlined to ensure target membership)

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

protocol AnalyticsService {
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary
}

final class LocalAnalyticsService: AnalyticsService {
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary {
        switch period {
        case "day":   return .init(threatsDetected: 12, threatsBlocked: 12, itemsScanned: 847,  protectionLevel: 96)
        case "week":  return .init(threatsDetected: 47, threatsBlocked: 45, itemsScanned: 5234, protectionLevel: 96)
        case "month": return .init(threatsDetected: 189, threatsBlocked: 185, itemsScanned: 21890, protectionLevel: 98)
        default:       return .init(threatsDetected: 0, threatsBlocked: 0, itemsScanned: 0, protectionLevel: 0)
        }
    }
}

enum EnvironmentConfig {
    static let baseURL: URL = URL(string: "https://api.aladdin.family")!
    static var useRemoteAnalytics: Bool { false }
    static func authToken() -> String? { nil }
}

enum NetworkLogger {
    static func logRequest(_ request: URLRequest) {
        #if DEBUG
        var headers = request.allHTTPHeaderFields ?? [:]
        if headers["Authorization"] != nil { headers["Authorization"] = "<redacted>" }
        print("➡️ Request: \(request.httpMethod ?? "GET") \(request.url?.absoluteString ?? "-") headers=\(headers)")
        #endif
    }
    static func logResponse(_ response: URLResponse?, data: Data?) {
        #if DEBUG
        if let http = response as? HTTPURLResponse {
            print("⬅️ Response: status=\(http.statusCode) url=\(http.url?.absoluteString ?? "-")")
        }
        #endif
    }
}

enum AnalyticsAPIError: Error { case invalidURL, badStatus(Int), decoding(Error), transport(Error) }

final class RemoteAnalyticsService: AnalyticsService {
    private let baseURL: URL
    private let authTokenProvider: () -> String?
    private let urlSession: URLSession
    private let cacheTTL: TimeInterval = 300
    private var cache: [String: (date: Date, summary: AnalyticsSummary)] = [:]
    
    init(baseURL: URL = EnvironmentConfig.baseURL,
         authTokenProvider: @escaping () -> String? = { EnvironmentConfig.authToken() },
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
        if let token = authTokenProvider() { request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization") }
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        NetworkLogger.logRequest(request)
        
        var lastError: Error?
        let maxAttempts = 3
        var delay: UInt64 = 200_000_000
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
                    } catch { lastError = AnalyticsAPIError.decoding(error) }
                }
            } catch { lastError = AnalyticsAPIError.transport(error) }
            if attempt < maxAttempts { try? await Task.sleep(nanoseconds: delay); delay *= 2 }
        }
        if let entry = cache[cacheKey] { return entry.summary }
        throw lastError ?? AnalyticsAPIError.invalidURL
    }
}



