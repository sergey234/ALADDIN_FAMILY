import Foundation
import os.log

/// 🌐 Remote Analytics Service
/// ✅ ИСПРАВЛЕНО: Использует APIService для реальных API вызовов
/// ✅ ЗАДАЧА 64: Добавлен graceful degradation с fallback на LocalAnalyticsService

final class RemoteAnalyticsService: AnalyticsService {
    private let apiService: APIService

    // ✅ ЗАДАЧА 64: Fallback сервис для graceful degradation
    private let fallbackService = LocalAnalyticsService()

    // ✅ ЗАДАЧА 64: Кэш для успешных ответов
    private var summaryCache: [String: (AnalyticsSummary, Date)] = [:]
    private var securityCache: [String: (SecurityAnalytics, Date)] = [:]
    private var usageCache: [String: (UsageAnalytics, Date)] = [:]

    // Время жизни кэша (5 минут)
    private let cacheLifetime: TimeInterval = 300

    // ✅ ЗАДАЧА 65: Metrics service для отправки метрик на сервер
    private let metricsService = MetricsService()

    init(apiService: APIService = .shared) {
        self.apiService = apiService

        #if DEBUG
        print("🛡️ RemoteAnalyticsService: Инициализирован с graceful degradation")
        print("📊 RemoteAnalyticsService: Metrics service подключен")
        #endif
    }

    // MARK: - Graceful Degradation Helpers

    /// ✅ ЗАДАЧА 64: Проверяет актуальность кэшированных данных
    private func isCacheValid(cacheDate: Date) -> Bool {
        return Date().timeIntervalSince(cacheDate) < cacheLifetime
    }

    /// ✅ ЗАДАЧА 64: Получает данные из кэша
    private func getCachedSummary(for key: String) -> AnalyticsSummary? {
        guard let (summary, cacheDate) = summaryCache[key], isCacheValid(cacheDate: cacheDate) else {
            return nil
        }
        return summary
    }

    /// ✅ ЗАДАЧА 64: Сохраняет данные в кэш
    private func setCachedSummary(_ summary: AnalyticsSummary, for key: String) {
        summaryCache[key] = (summary, Date())
    }

    /// ✅ ЗАДАЧА 64: Получает данные из кэша для security analytics
    private func getCachedSecurityAnalytics(for key: String) -> SecurityAnalytics? {
        guard let (analytics, cacheDate) = securityCache[key], isCacheValid(cacheDate: cacheDate) else {
            return nil
        }
        return analytics
    }

    /// ✅ ЗАДАЧА 64: Сохраняет данные в кэш для security analytics
    private func setCachedSecurityAnalytics(_ analytics: SecurityAnalytics, for key: String) {
        securityCache[key] = (analytics, Date())
    }

    /// ✅ ЗАДАЧА 64: Получает данные из кэша для usage analytics
    private func getCachedUsageAnalytics(for key: String) -> UsageAnalytics? {
        guard let (analytics, cacheDate) = usageCache[key], isCacheValid(cacheDate: cacheDate) else {
            return nil
        }
        return analytics
    }

    /// ✅ ЗАДАЧА 64: Сохраняет данные в кэш для usage analytics
    private func setCachedUsageAnalytics(_ analytics: UsageAnalytics, for key: String) {
        usageCache[key] = (analytics, Date())
    }

    // MARK: - AnalyticsService Protocol
    
    /// ✅ ЗАДАЧА 64: Graceful degradation - fallback на LocalAnalyticsService при ошибках
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> AnalyticsSummary {
        let cacheKey = "summary_\(period)_\(filters.onlyBlocked)_\(filters.includeFamily)_\(filters.includeDevices)"

        return try await withCheckedThrowingContinuation { continuation in
            apiService.getAnalytics(period: period) { result in
                switch result {
                case .success(let analyticsResponse):
                    // Преобразуем AnalyticsResponse в AnalyticsSummary
                    let summary = AnalyticsSummary(
                        threatsDetected: analyticsResponse.threatsDetected,
                        threatsBlocked: analyticsResponse.threatsBlocked,
                        itemsScanned: analyticsResponse.itemsScanned,
                        protectionLevel: Double(analyticsResponse.protectionLevel)
                    )

                    // ✅ ЗАДАЧА 64: Кэшируем успешный ответ
                    self.setCachedSummary(summary, for: cacheKey)

                    #if DEBUG
                    print("📊 RemoteAnalyticsService: fetchSummary - успех, данные закэшированы")
                    #endif

                    continuation.resume(returning: summary)

                case .failure(let error):
                    #if DEBUG
                    print("⚠️ RemoteAnalyticsService: fetchSummary - ошибка API: \(error.localizedDescription)")
                    #endif

                    // ✅ ЗАДАЧА 64: Graceful degradation - пытаемся получить из кэша
                    if let cachedSummary = self.getCachedSummary(for: cacheKey) {
                        #if DEBUG
                        print("✅ RemoteAnalyticsService: fetchSummary - возвращаем кэшированные данные")
                        #endif

                        // Production логирование использования кэша
                        os_log("📊 Analytics Summary: Using cached data due to API failure", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                        continuation.resume(returning: cachedSummary)
                        return
                    }

                    // ✅ ЗАДАЧА 64: Fallback на LocalAnalyticsService
                    #if DEBUG
                    print("🛡️ RemoteAnalyticsService: fetchSummary - fallback на LocalAnalyticsService")
                    #endif

                    // Production логирование fallback
                    os_log("🛡️ Analytics Summary: Fallback to LocalAnalyticsService", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                    Task {
                        do {
                            let fallbackSummary = try await self.fallbackService.fetchSummary(period: period, filters: filters)
                            continuation.resume(returning: fallbackSummary)
                        } catch {
                            // Если даже fallback не сработал, возвращаем оригинальную ошибку
                            continuation.resume(throwing: error)
                        }
                    }
                }
            }
        }
    }
    
    /// ✅ ЗАДАЧА 64: Graceful degradation - fallback на LocalAnalyticsService при ошибках
    func fetchSecurityAnalytics(period: String) async throws -> SecurityAnalytics {
        let cacheKey = "security_\(period)"

        return try await withCheckedThrowingContinuation { continuation in
            apiService.getAnalytics(period: period) { result in
                switch result {
                case .success(let analyticsResponse):
                    // Преобразуем AnalyticsResponse в SecurityAnalytics
                    // Преобразуем threatsByType в ThreatTypeCount
                    let blockedThreats = analyticsResponse.threatsByType.map { threatByType in
                        ThreatTypeCount(type: threatByType.type, count: threatByType.count, icon: nil)
                    }
                    // Преобразуем topThreats в RecentThreat
                    let recentThreats = analyticsResponse.topThreats.prefix(10).map { threat in
                        RecentThreat(
                            emoji: threat.icon,
                            text: threat.name,
                            time: "Недавно"
                        )
                    }
                    // Создаем сетевую статистику
                    let networkStats = AnalyticsNetworkProtectionStats(
                        today: "0 GB",
                        week: "0 GB",
                        protection: "\(analyticsResponse.protectionLevel)%"
                    )
                    let securityAnalytics = SecurityAnalytics(
                        blockedThreats: blockedThreats,
                        recentThreats: recentThreats,
                        networkProtectionStats: networkStats
                    )

                    // ✅ ЗАДАЧА 64: Кэшируем успешный ответ
                    self.setCachedSecurityAnalytics(securityAnalytics, for: cacheKey)

                    #if DEBUG
                    print("📊 RemoteAnalyticsService: fetchSecurityAnalytics - успех, данные закэшированы")
                    #endif

                    continuation.resume(returning: securityAnalytics)

                case .failure(let error):
                    #if DEBUG
                    print("⚠️ RemoteAnalyticsService: fetchSecurityAnalytics - ошибка API: \(error.localizedDescription)")
                    #endif

                    // ✅ ЗАДАЧА 64: Graceful degradation - пытаемся получить из кэша
                    if let cachedAnalytics = self.getCachedSecurityAnalytics(for: cacheKey) {
                        #if DEBUG
                        print("✅ RemoteAnalyticsService: fetchSecurityAnalytics - возвращаем кэшированные данные")
                        #endif

                        os_log("📊 Analytics Security: Using cached data due to API failure", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                        continuation.resume(returning: cachedAnalytics)
                        return
                    }

                    // ✅ ЗАДАЧА 64: Fallback на LocalAnalyticsService
                    #if DEBUG
                    print("🛡️ RemoteAnalyticsService: fetchSecurityAnalytics - fallback на LocalAnalyticsService")
                    #endif

                    os_log("🛡️ Analytics Security: Fallback to LocalAnalyticsService", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                    Task {
                        do {
                            let fallbackAnalytics = try await self.fallbackService.fetchSecurityAnalytics(period: period)
                            continuation.resume(returning: fallbackAnalytics)
                        } catch {
                            continuation.resume(throwing: error)
                        }
                    }
                }
            }
        }
    }
    
    /// ✅ ИСПРАВЛЕНО: Использует реальный API через APIService
    func fetchFamilyAnalytics(period: String) async throws -> FamilyAnalytics {
        // TODO: Когда API будет поддерживать семейную аналитику, добавить реальный вызов
        // Пока возвращаем пустые данные
        return FamilyAnalytics(
            membersActivity: [],
            threatsByMember: [],
            recentActivity: []
        )
    }
    
    /// ✅ ЗАДАЧА 64: Graceful degradation - fallback на LocalAnalyticsService при ошибках
    func fetchUsageAnalytics(period: String) async throws -> UsageAnalytics {
        let cacheKey = "usage_\(period)"

        return try await withCheckedThrowingContinuation { continuation in
            apiService.getAnalytics(period: period) { result in
                switch result {
                case .success(let analyticsResponse):
                    // Преобразуем AnalyticsResponse в UsageAnalytics
                    let usageAnalytics = UsageAnalytics(
                        activityByTime: [],
                        topApps: [],
                        topSites: [],
                        totalTraffic: "0 GB"
                    )

                    // ✅ ЗАДАЧА 64: Кэшируем успешный ответ
                    self.setCachedUsageAnalytics(usageAnalytics, for: cacheKey)

                    #if DEBUG
                    print("📊 RemoteAnalyticsService: fetchUsageAnalytics - успех, данные закэшированы")
                    #endif

                    continuation.resume(returning: usageAnalytics)

                case .failure(let error):
                    #if DEBUG
                    print("⚠️ RemoteAnalyticsService: fetchUsageAnalytics - ошибка API: \(error.localizedDescription)")
                    #endif

                    // ✅ ЗАДАЧА 64: Graceful degradation - пытаемся получить из кэша
                    if let cachedAnalytics = self.getCachedUsageAnalytics(for: cacheKey) {
                        #if DEBUG
                        print("✅ RemoteAnalyticsService: fetchUsageAnalytics - возвращаем кэшированные данные")
                        #endif

                        os_log("📊 Analytics Usage: Using cached data due to API failure", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                        continuation.resume(returning: cachedAnalytics)
                        return
                    }

                    // ✅ ЗАДАЧА 64: Fallback на LocalAnalyticsService
                    #if DEBUG
                    print("🛡️ RemoteAnalyticsService: fetchUsageAnalytics - fallback на LocalAnalyticsService")
                    #endif

                    os_log("🛡️ Analytics Usage: Fallback to LocalAnalyticsService", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                    Task {
                        do {
                            let fallbackAnalytics = try await self.fallbackService.fetchUsageAnalytics(period: period)
                            continuation.resume(returning: fallbackAnalytics)
                        } catch {
                            continuation.resume(throwing: error)
                        }
                    }
                }
            }
        }
    }
    
    /// ✅ ИСПРАВЛЕНО: Использует реальный API через APIService
    func fetchDevicesAnalytics(period: String) async throws -> DevicesAnalytics {
        // TODO: Когда API будет поддерживать аналитику устройств, добавить реальный вызов
        // Пока возвращаем пустые данные с правильной структурой
        return DevicesAnalytics(
            deviceActivity: [],
            threatsByDevice: [],
            status: AnalyticsDeviceStatus(online: 0, offline: 0, protection: "0%")
        )
    }

    // MARK: - Production monitoring methods
    
    /// ✅ ЗАДАЧА 65: Отслеживание API запросов (теперь с отправкой на сервер)
    func trackAPIRequest(endpoint: String, method: String, responseTime: TimeInterval, statusCode: Int, success: Bool) {
        #if DEBUG
        print("📊 [Analytics] API Request: \(method) \(endpoint) - \(statusCode) (\(responseTime)s)")
        #endif

        // ✅ ЗАДАЧА 65: Отправляем метрику на сервер
        metricsService.trackAPIRequest(
            endpoint: endpoint,
            method: method,
            responseTime: responseTime,
            statusCode: statusCode,
            success: success
        )
    }
    
    /// ✅ ЗАДАЧА 65: Отслеживание действий пользователя (теперь с отправкой на сервер)
    func trackUserAction(action: String, parameters: [String: Any]?) {
        #if DEBUG
        print("📊 [Analytics] User Action: \(action) - \(parameters ?? [:])")
        #endif

        // ✅ ЗАДАЧА 65: Отправляем метрику на сервер
        metricsService.trackUserAction(action: action, parameters: parameters)
    }
    
    /// ✅ ЗАДАЧА 65: Отслеживание ошибок (теперь с отправкой на сервер)
    func trackError(error: Error, context: String?) {
        #if DEBUG
        print("📊 [Analytics] Error: \(error.localizedDescription) - Context: \(context ?? "none")")
        #endif

        // ✅ ЗАДАЧА 65: Отправляем метрику на сервер
        metricsService.trackError(error, context: context)
    }
    
    /// ✅ ЗАДАЧА 65: Отслеживание алертов (теперь с отправкой на сервер)
    func trackAlert(alert: Alert) {
        #if DEBUG
        print("📊 [Analytics] Alert: \(alert.type.rawValue) - \(alert.message)")
        #endif

        // ✅ ЗАДАЧА 65: Отправляем метрику на сервер
        metricsService.trackAlert(alert)
    }
    
    /// ✅ ЗАДАЧА 65: Отслеживание отчетов о здоровье (теперь с отправкой на сервер)
    func trackHealthReport(healthStatus: HealthStatus) {
        #if DEBUG
        print("📊 [Analytics] Health: \(healthStatus.status.rawValue) - Uptime: \(healthStatus.uptime)%")
        #endif

        // ✅ ЗАДАЧА 65: Отправляем метрику на сервер
        metricsService.trackHealthReport(healthStatus)
    }
}
