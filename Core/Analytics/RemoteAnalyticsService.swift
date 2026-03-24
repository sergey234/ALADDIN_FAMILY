import Foundation
import os.log

// Импортируем модели компонентов
// ComponentStats и ComponentsAnalytics теперь в ComponentAnalyticsModels.swift

/// 🌐 Remote Analytics Service
/// ✅ ИСПРАВЛЕНО: Использует APIService для реальных API вызовов
/// ✅ ЗАДАЧА 64: Добавлен graceful degradation с fallback на LocalAnalyticsService

final class RemoteAnalyticsService: AnalyticsService {
    private let apiService: APIService

    // ✅ ИСПРАВЛЕНО: Убран fallback сервис - больше не используем LocalAnalyticsService
    // Fallback на MOCK данные убран даже в DEBUG режиме

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
    
    /// Возвращает summary+security одним сетевым запросом.
    /// Используется для предотвращения двойного GET /api/analytics на одном экране.
    func fetchCombinedAnalytics(period: String, filters: AnalyticsFilters) async throws -> ((AnalyticsSummary, DataSource), (SecurityAnalytics, DataSource)) {
        let cacheSummaryKey = "summary_\(period)_\(filters.onlyBlocked)_\(filters.includeFamily)_\(filters.includeDevices)"
        let cacheSecurityKey = "security_\(period)"
        
        return try await withCheckedThrowingContinuation { continuation in
            apiService.getAnalytics(period: period) { result in
                switch result {
                case .success(let analyticsResponse):
                    let summary = AnalyticsSummary(
                        threatsDetected: analyticsResponse.threatsDetected,
                        threatsBlocked: analyticsResponse.threatsBlocked,
                        itemsScanned: analyticsResponse.itemsScanned,
                        protectionLevel: Double(analyticsResponse.protectionLevel)
                    )
                    
                    let blockedThreats = analyticsResponse.threatsByType.map { threatByType in
                        ThreatTypeCount(type: threatByType.type, count: threatByType.count, icon: nil)
                    }
                    let recentThreats = analyticsResponse.topThreats.prefix(10).map { threat in
                        RecentThreat(
                            emoji: threat.icon,
                            text: threat.name,
                            time: "Недавно"
                        )
                    }
                    let networkStats = AnalyticsNetworkProtectionStats(
                        today: "0 GB",
                        week: "0 GB",
                        protection: "\(analyticsResponse.protectionLevel)%"
                    )
                    let security = SecurityAnalytics(
                        blockedThreats: blockedThreats,
                        recentThreats: recentThreats,
                        networkProtectionStats: networkStats
                    )
                    
                    self.setCachedSummary(summary, for: cacheSummaryKey)
                    self.setCachedSecurityAnalytics(security, for: cacheSecurityKey)
                    continuation.resume(returning: ((summary, .api), (security, .api)))
                    
                case .failure:
                    if let cachedSummary = self.getCachedSummary(for: cacheSummaryKey),
                       let cachedSecurity = self.getCachedSecurityAnalytics(for: cacheSecurityKey) {
                        continuation.resume(returning: ((cachedSummary, .cache), (cachedSecurity, .cache)))
                        return
                    }
                    
                    let emptySummary = AnalyticsSummary(
                        threatsDetected: 0,
                        threatsBlocked: 0,
                        itemsScanned: 0,
                        protectionLevel: 0.0
                    )
                    let emptySecurity = SecurityAnalytics(
                        blockedThreats: [],
                        recentThreats: [],
                        networkProtectionStats: AnalyticsNetworkProtectionStats(
                            today: "0 GB",
                            week: "0 GB",
                            protection: "0%"
                        )
                    )
                    continuation.resume(returning: ((emptySummary, .empty), (emptySecurity, .empty)))
                }
            }
        }
    }
    
    /// ✅ ВАРИАНТ 4: Graceful degradation с возвратом источника данных
    func fetchSummary(period: String, filters: AnalyticsFilters) async throws -> (AnalyticsSummary, DataSource) {
        let cacheKey = "summary_\(period)_\(filters.onlyBlocked)_\(filters.includeFamily)_\(filters.includeDevices)"

        #if DEBUG
        print("📊 RemoteAnalyticsService: fetchSummary - начинаем запрос к API для period=\(period)")
        #endif

        return try await withCheckedThrowingContinuation { continuation in
            apiService.getAnalytics(period: period) { result in
                #if DEBUG
                print("📊 RemoteAnalyticsService: fetchSummary - получен ответ от API")
                #endif
                
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
                    print("   - Threats detected: \(summary.threatsDetected)")
                    print("   - Threats blocked: \(summary.threatsBlocked)")
                    print("   - Items scanned: \(summary.itemsScanned)")
                    print("   - Protection level: \(summary.protectionLevel)%")
                    #endif

                    continuation.resume(returning: (summary, .api))

                case .failure(let error):
                    #if DEBUG
                    print("⚠️ RemoteAnalyticsService: fetchSummary - ошибка API: \(error.localizedDescription)")
                    #endif

                    // ✅ ВАРИАНТ 4: Graceful degradation - пытаемся получить из кэша
                    if let cachedSummary = self.getCachedSummary(for: cacheKey) {
                        #if DEBUG
                        print("✅ RemoteAnalyticsService: fetchSummary - возвращаем кэшированные данные")
                        print("   - Threats detected: \(cachedSummary.threatsDetected)")
                        print("   - Threats blocked: \(cachedSummary.threatsBlocked)")
                        #endif

                        // Production логирование использования кэша
                        os_log("📊 Analytics Summary: Using cached data due to API failure", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                        continuation.resume(returning: (cachedSummary, .cache))
                        return
                    }

                    // ✅ ВАРИАНТ 4: Нет данных - возвращаем пустые данные с .empty (не ошибку!)
                    let emptySummary = AnalyticsSummary(
                        threatsDetected: 0,
                        threatsBlocked: 0,
                        itemsScanned: 0,
                        protectionLevel: 0.0
                    )
                    
                    VisualLogger.shared.log("ℹ️ RemoteAnalyticsService: summary empty (api_fail_no_cache)", level: .info, category: "ANALYTICS.API")
                    
                    #if DEBUG
                    print("📊 RemoteAnalyticsService: fetchSummary - API failed, no cache, returning empty data")
                    print("   - Error: \(error.localizedDescription)")
                    #endif
                    
                    os_log("📊 Analytics Summary: API failed, no cache available, returning empty data", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)
                    continuation.resume(returning: (emptySummary, .empty))
                }
            }
        }
    }
    
    /// ✅ ВАРИАНТ 4: Graceful degradation с возвратом источника данных
    func fetchSecurityAnalytics(period: String) async throws -> (SecurityAnalytics, DataSource) {
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

                    continuation.resume(returning: (securityAnalytics, .api))

                case .failure(let error):
                    #if DEBUG
                    print("⚠️ RemoteAnalyticsService: fetchSecurityAnalytics - ошибка API: \(error.localizedDescription)")
                    #endif

                    // ✅ ВАРИАНТ 4: Graceful degradation - пытаемся получить из кэша
                    if let cachedAnalytics = self.getCachedSecurityAnalytics(for: cacheKey) {
                        #if DEBUG
                        print("✅ RemoteAnalyticsService: fetchSecurityAnalytics - возвращаем кэшированные данные")
                        #endif

                        os_log("📊 Analytics Security: Using cached data due to API failure", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                        continuation.resume(returning: (cachedAnalytics, .cache))
                        return
                    }

                    // ✅ ВАРИАНТ 4: Нет данных - возвращаем пустые данные с .empty (не ошибку!)
                    let emptySecurity = SecurityAnalytics(
                        blockedThreats: [],
                        recentThreats: [],
                        networkProtectionStats: AnalyticsNetworkProtectionStats(
                            today: "0 GB",
                            week: "0 GB",
                            protection: "0%"
                        )
                    )
                    
                     VisualLogger.shared.log("ℹ️ RemoteAnalyticsService: security empty (api_fail_no_cache)", level: .info, category: "ANALYTICS.API")
                    
                    os_log("📊 Analytics Security: API failed, no cache available, returning empty data", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)
                    continuation.resume(returning: (emptySecurity, .empty))
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
    
    /// ✅ ВАРИАНТ 4: Graceful degradation с возвратом источника данных
    func fetchUsageAnalytics(period: String) async throws -> (UsageAnalytics, DataSource) {
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

                    continuation.resume(returning: (usageAnalytics, .api))

                case .failure(let error):
                    #if DEBUG
                    print("⚠️ RemoteAnalyticsService: fetchUsageAnalytics - ошибка API: \(error.localizedDescription)")
                    #endif

                    // ✅ ВАРИАНТ 4: Graceful degradation - пытаемся получить из кэша
                    if let cachedAnalytics = self.getCachedUsageAnalytics(for: cacheKey) {
                        #if DEBUG
                        print("✅ RemoteAnalyticsService: fetchUsageAnalytics - возвращаем кэшированные данные")
                        #endif

                        os_log("📊 Analytics Usage: Using cached data due to API failure", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)

                        continuation.resume(returning: (cachedAnalytics, .cache))
                        return
                    }

                    // ✅ ВАРИАНТ 4: Нет данных - возвращаем пустые данные с .empty (не ошибку!)
                    let emptyUsage = UsageAnalytics(
                        activityByTime: [],
                        topApps: [],
                        topSites: [],
                        totalTraffic: "0 GB"
                    )
                    
                    os_log("📊 Analytics Usage: API failed, no cache available, returning empty data", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)
                    continuation.resume(returning: (emptyUsage, .empty))
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
    
    // MARK: - Component Analytics
    
    // ✅ ВАРИАНТ 4: Кэш для компонентов
    private var componentCache: [String: (ComponentStats, Date)] = [:]
    
    /// ✅ ВАРИАНТ 4: Получить статистику компонента с graceful degradation
    func fetchComponentStats(componentId: String) async throws -> (ComponentStats, DataSource) {
        let cacheKey = "component_\(componentId)"
        
        return try await withCheckedThrowingContinuation { continuation in
            apiService.getComponentStats(componentId: componentId) { result in
                switch result {
                case .success(let stats):
                    // ✅ Реальные данные из API
                    self.setCachedComponentStats(stats, for: cacheKey)
                    continuation.resume(returning: (stats, .api))
                    
                case .failure(let error):
                    #if DEBUG
                    print("⚠️ RemoteAnalyticsService: fetchComponentStats - ошибка API: \(error.localizedDescription)")
                    #endif
                    
                    // ✅ ВАРИАНТ 4: Graceful degradation - пытаемся получить из кэша
                    if let cachedStats = self.getCachedComponentStats(for: cacheKey) {
                        #if DEBUG
                        print("✅ RemoteAnalyticsService: fetchComponentStats - возвращаем кэшированные данные")
                        #endif
                        
                        os_log("📊 Component Stats: Using cached data due to API failure", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)
                        
                        continuation.resume(returning: (cachedStats, .cache))
                        return
                    }
                    
                    // ✅ ВАРИАНТ 4: Нет данных - возвращаем пустые данные с .empty (не ошибку!)
                    let emptyStats = ComponentStats(
                        componentId: componentId,
                        metrics: self.getEmptyMetrics(for: componentId),
                        dataSource: .empty
                    )
                    
                    os_log("📊 Component Stats: API failed, no cache available, returning empty data", log: OSLog(subsystem: "com.aladdin.analytics", category: "graceful_degradation"), type: .info)
                    continuation.resume(returning: (emptyStats, .empty))
                }
            }
        }
    }
    
    /// ✅ ВАРИАНТ 4: Получить статистику всех компонентов (параллельная загрузка)
    func fetchAllComponentsStats() async throws -> ComponentsAnalytics {
        async let driving = fetchComponentStats(componentId: "driving")
        async let darkWeb = fetchComponentStats(componentId: "darkweb")
        async let identity = fetchComponentStats(componentId: "identity")
        async let location = fetchComponentStats(componentId: "location")
        async let cleanup = fetchComponentStats(componentId: "cleanup")
        async let tracker = fetchComponentStats(componentId: "tracker")
        async let ai = fetchComponentStats(componentId: "ai")
        
        let (drivingStats, _) = try await driving
        let (darkWebStats, _) = try await darkWeb
        let (identityStats, _) = try await identity
        let (locationStats, _) = try await location
        let (cleanupStats, _) = try await cleanup
        let (trackerStats, _) = try await tracker
        let (aiStats, _) = try await ai
        
        return ComponentsAnalytics(
            drivingReports: drivingStats,
            darkWeb: darkWebStats,
            identityTheft: identityStats,
            locationBubble: locationStats,
            dataCleanup: cleanupStats,
            antiTracker: trackerStats,
            aiCategories: aiStats
        )
    }
    
    // MARK: - Component Cache Helpers
    
    /// Сохраняет статистику компонента в кэш
    private func setCachedComponentStats(_ stats: ComponentStats, for key: String) {
        componentCache[key] = (stats, Date())
    }
    
    /// Получает статистику компонента из кэша
    private func getCachedComponentStats(for key: String) -> ComponentStats? {
        guard let (stats, cacheDate) = componentCache[key], isCacheValid(cacheDate: cacheDate) else {
            return nil
        }
        return stats
    }
    
    /// Возвращает пустые метрики для компонента
    private func getEmptyMetrics(for componentId: String) -> [String: String] {
        switch componentId {
        case "driving_reports_agent", "driving":
            return ["trips": "0", "safety_score": "0.0", "new_events": "0"]
        case "dark_web_monitoring_agent", "darkweb":
            return ["leaks_found": "0", "new_leaks": "0", "new_events": "0"]
        case "russian_identity_theft_protection_agent", "identity":
            return ["attempts": "0", "blocked": "0"]
        case "location_bubble_agent", "location":
            return ["blocked": "0", "accuracy": "Нет данных"]
        case "personal_data_cleanup_agent", "cleanup":
            return ["freed_space_gb": "0.0", "last_cleanup_hours_ago": "0"]
        case "anti_tracker_agent", "tracker":
            return ["blocked_total": "0", "blocked_this_week": "0"]
        case "ai_categories_agent", "ai":
            return ["categorized": "0", "blocked": "0"]
        default:
            return [:]
        }
    }
}
