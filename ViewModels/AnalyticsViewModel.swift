import SwiftUI

// Master Logger for analytics logging
private let logger = MasterLogger.shared

/// 📊 Analytics View Model
/// Упрощённый state для экрана аналитики
class AnalyticsViewModel: ObservableObject {
    @Published private(set) var threatsDetected: Int = 0
    @Published private(set) var threatsBlocked: Int = 0
    @Published private(set) var itemsScanned: Int = 0
    @Published private(set) var protectionLevel: Double = 0
    @Published private(set) var threatCategories: [ThreatTypeCount] = []
    @Published private(set) var isLoading: Bool = false
    @Published private(set) var errorMessage: String?

    // ✅ ЗАДАЧА 64: Индикатор офлайн режима для graceful degradation
    @Published private(set) var isOfflineMode: Bool = false
    
    // ✅ ВАРИАНТ 4: Индикатор источника данных
    @Published private(set) var dataSource: DataSource = .empty
    
    // ✅ ВАРИАНТ 4: Данные компонентов
    @Published private(set) var componentsAnalytics: ComponentsAnalytics?
    @Published private(set) var componentsDataSource: DataSource = .empty

    /// Состояние пустой детализации угроз (текст и цвет задаются в UI по `DataSource` и ошибке).
    enum ThreatBreakdownEmptyKind: Equatable {
        case successEmpty
        case cacheEmpty
        case noDatasourceEmpty
        case loadFailed
    }

    /// Процент защиты показываем только после реального ответа API или кэша (не «ложный 0%» при старте).
    var canDisplayProtectionLevel: Bool {
        dataSource == .api || dataSource == .cache
    }
    
    /// `nil`, если есть строки категорий или идёт загрузка.
    var threatBreakdownEmptyKind: ThreatBreakdownEmptyKind? {
        guard threatCategories.isEmpty, !isLoading else { return nil }
        if errorMessage != nil { return .loadFailed }
        switch dataSource {
        case .api: return .successEmpty
        case .cache: return .cacheEmpty
        case .empty: return .noDatasourceEmpty
        case .error: return .loadFailed
        }
    }
    
    private let service: AnalyticsService
    private var watchdogTask: Task<Void, Never>?
    private var lastLoadStartAt: Date?
    private var currentLoadId: String?
    private var loadTask: Task<Void, Never>?
    private var componentsTask: Task<Void, Never>?
    private var lastSessionExpiredAt: Date?
    
    // Ключи для UserDefaults
    private let periodKey = "analytics_last_period"
    private let filtersOnlyBlockedKey = "analytics_last_filters_only_blocked"
    private let filtersIncludeFamilyKey = "analytics_last_filters_include_family"
    private let filtersIncludeDevicesKey = "analytics_last_filters_include_devices"
    
    // ✅ ИСПРАВЛЕНО: @State вместо computed properties (защита от рекурсии)
    @Published private(set) var cachedPeriod: String = "day"
    @Published private(set) var cachedFilters: AnalyticsFilters = AnalyticsFilters(
        onlyBlocked: false,
        includeFamily: true,
        includeDevices: true
    )
    
    init(service: AnalyticsService) {
        // ✅ BUILD 104: Silent Startup - убрали logger.business из init()
        self.service = service
        
        // ✅ ИСПРАВЛЕНО: Загружаем из UserDefaults один раз при инициализации (асинхронно)
        Task { @MainActor in
            cachedPeriod = UserDefaults.standard.string(forKey: periodKey) ?? "day"
            cachedFilters = AnalyticsFilters(
                onlyBlocked: UserDefaults.standard.bool(forKey: filtersOnlyBlockedKey),
                includeFamily: UserDefaults.standard.object(forKey: filtersIncludeFamilyKey) as? Bool ?? true,
                includeDevices: UserDefaults.standard.object(forKey: filtersIncludeDevicesKey) as? Bool ?? true
            )
        }
    }
    
    @MainActor
    func startLoad() {
        loadTask?.cancel()
        loadTask = Task { @MainActor [weak self] in
            await self?.load()
        }
    }

    @MainActor
    private func load() async {
        let loadId = UUID().uuidString.prefix(8)
        currentLoadId = String(loadId)
        VisualLogger.shared.log("🚀 analytics_load_start id=\(loadId)", level: .info, category: "ANALYTICS.API")

        // Guard against rapid re-entry bursts from multiple UI triggers.
        if let lastLoadStartAt = self.lastLoadStartAt, Date().timeIntervalSince(lastLoadStartAt) < 0.8 {
            VisualLogger.shared.log("⏭️ analytics_load_skip_throttled id=\(loadId) (<0.8s)", level: .info, category: "ANALYTICS.API")
            return
        }
        if isLoading {
            VisualLogger.shared.log("⏭️ analytics_load_skip_already_loading id=\(loadId)", level: .info, category: "ANALYTICS.API")
            return
        }
        self.lastLoadStartAt = Date()
        
        // ✅ ДИАГНОСТИКА: Проверка токена во всех хранилищах
        #if DEBUG
        let appConfigToken = AppConfig.authToken != nil
        let keychainToken = KeychainManager.shared.loadString(forKey: .authToken) != nil
        let subscriptionToken = SubscriptionManager.shared.currentToken != nil
        let tokenMessage = """
        🔍 AnalyticsViewModel: Диагностика токена
           - AppConfig.authToken: \(appConfigToken ? "✅ есть" : "❌ нет")
           - Keychain token: \(keychainToken ? "✅ есть" : "❌ нет")
           - SubscriptionManager token: \(subscriptionToken ? "✅ есть" : "❌ нет")
        """
        VisualLogger.shared.log(tokenMessage, level: .info, category: "ANALYTICS")
        print(tokenMessage)
        #endif
        
        // ✅ ИСПРАВЛЕНО: Умная проверка токена (TokenManager)
        // Теперь проверяет SubscriptionManager.currentToken первым делом!
        let tokenAvailability = TokenManager.shared.checkTokenAvailability()
        
        // Если токен загружается - ждем немного
        if tokenAvailability.isAvailable {
            // Токен доступен - продолжаем загрузку
            #if DEBUG
            VisualLogger.shared.log("✅ AnalyticsViewModel: Токен доступен, начинаем загрузку", level: .success, category: "ANALYTICS")
            print("✅ AnalyticsViewModel: Токен доступен, начинаем загрузку")
            #endif
        } else {
            // Токен не найден - проверяем, загружается ли он
            if TokenManager.shared.isTokenLoading() {
                // Токен загружается - ждем до 500ms
                #if DEBUG
                VisualLogger.shared.log("⏳ AnalyticsViewModel: Токен загружается, ждем...", level: .info, category: "ANALYTICS")
                print("⏳ AnalyticsViewModel: Токен загружается, ждем...")
                #endif
                if let token = await TokenManager.shared.waitForTokenLoad(maxWaitTime: 1.0) {
                    // Токен загрузился - продолжаем
                    #if DEBUG
                    VisualLogger.shared.log("✅ AnalyticsViewModel: Токен загрузился, продолжаем", level: .success, category: "ANALYTICS")
                    print("✅ AnalyticsViewModel: Токен загрузился, продолжаем")
                    #endif
                } else {
                    // Токен не загрузился - показываем ошибку (БЕЗ кнопки "Войти")
                    #if DEBUG
                    VisualLogger.shared.log("⚠️ AnalyticsViewModel: Токен не загрузился, показываем ошибку", level: .warning, category: "ANALYTICS")
                    print("⚠️ AnalyticsViewModel: Токен не загрузился, показываем ошибку")
                    #endif
                    errorMessage = LocalizationManager.shared.localized("analytics_err_load_token")
                    VisualLogger.shared.log("❌ analytics_load_fail id=\(loadId) reason=token_wait_timeout", level: .error, category: "ANALYTICS.API")
                    isLoading = false
                    isOfflineMode = false
                    dataSource = .empty
                    // ✅ Пробуем загрузить кэшированные данные
                    await loadCachedDataIfAvailable()
                    return
                }
            } else {
                // Токена нет нигде - показываем ошибку (БЕЗ кнопки "Войти")
                #if DEBUG
                VisualLogger.shared.log("⚠️ AnalyticsViewModel: Токен отсутствует, показываем ошибку", level: .warning, category: "ANALYTICS")
                print("⚠️ AnalyticsViewModel: Токен отсутствует, показываем ошибку")
                #endif
                errorMessage = LocalizationManager.shared.localized("analytics_err_load_token")
                VisualLogger.shared.log("❌ analytics_load_fail id=\(loadId) reason=token_absent", level: .error, category: "ANALYTICS.API")
                isLoading = false
                isOfflineMode = false
                dataSource = .empty
                // ✅ Пробуем загрузить кэшированные данные
                await loadCachedDataIfAvailable()
                return
            }
        }
        
        isLoading = true
        watchdogTask?.cancel()
        watchdogTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: 15_000_000_000)
            await self?.applyWatchdogTimeoutIfNeeded()
        }
        defer {
            isLoading = false
            watchdogTask?.cancel()
            watchdogTask = nil
        }
        errorMessage = nil
        isOfflineMode = false // ✅ ЗАДАЧА 64: Сбрасываем индикатор офлайн режима

        // ✅ ЗАДАЧА 66: Начинаем отслеживание производительности загрузки
        PerformanceMonitor.shared.startScreenLoad("AnalyticsScreen")

        #if DEBUG
        print("📊 AnalyticsViewModel: Загрузка аналитики...")
        print("   - Period: \(cachedPeriod)")
        print("   - Filters: onlyBlocked=\(cachedFilters.onlyBlocked), includeFamily=\(cachedFilters.includeFamily), includeDevices=\(cachedFilters.includeDevices)")
        #endif

        do {
            let summaryResult: (AnalyticsSummary, DataSource)
            let securityResult: (SecurityAnalytics, DataSource)
            
            if let remoteService = service as? RemoteAnalyticsService {
                let combined = try await remoteService.fetchCombinedAnalytics(period: cachedPeriod, filters: cachedFilters)
                summaryResult = combined.0
                securityResult = combined.1
            } else {
                async let summaryTask = service.fetchSummary(period: cachedPeriod, filters: cachedFilters)
                async let securityTask = service.fetchSecurityAnalytics(period: cachedPeriod)
                (summaryResult, securityResult) = try await (summaryTask, securityTask)
            }
            
            // Извлекаем данные и источник
            let (summary, summarySource) = summaryResult
            let (security, securitySource) = securityResult
            
            // Определяем общий источник данных
            let resolvedDataSource: DataSource =
                summarySource == .api && securitySource == .api ? .api :
                summarySource == .cache || securitySource == .cache ? .cache : .empty
            if dataSource != resolvedDataSource {
                dataSource = resolvedDataSource
            }
            VisualLogger.shared.log("✅ analytics_load_base_ok id=\(loadId) source=\(resolvedDataSource)", level: .success, category: "ANALYTICS.API")

            #if DEBUG
            print("✅ AnalyticsViewModel: Данные загружены:")
            print("   - Threats detected: \(summary.threatsDetected)")
            print("   - Threats blocked: \(summary.threatsBlocked)")
            print("   - Items scanned: \(summary.itemsScanned)")
            print("   - Protection level: \(summary.protectionLevel)%")
            print("   - Threat categories: \(security.blockedThreats.count)")
            print("   - Data Source: Summary=\(summarySource), Security=\(securitySource), Final=\(dataSource)")
            #endif
            
            logger.business("Analytics data loaded: threats=\(summary.threatsDetected), source=\(dataSource)")

            // ✅ ЗАДАЧА 64: Проверяем, используется ли офлайн режим
            // Если данные из кэша - включаем индикатор офлайн режима
            let resolvedOfflineMode = (summarySource == .cache || securitySource == .cache)
            if isOfflineMode != resolvedOfflineMode {
                isOfflineMode = resolvedOfflineMode
            }

            apply(summary: summary)
            apply(securityAnalytics: security)
            
            // ✅ ВАРИАНТ 4: Загружаем данные компонентов (если сервис поддерживает)
            // Ограничиваем время ожидания, чтобы не оставлять экран в вечном loading.
            startComponentsLoad(loadId: String(loadId))

            // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности загрузки
            PerformanceMonitor.shared.endScreenLoad("AnalyticsScreen")
            
        } catch {
            // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности даже при ошибке
            PerformanceMonitor.shared.endScreenLoad("AnalyticsScreen")
            
            // ✅ ВАРИАНТ 4: Если ошибка - устанавливаем dataSource = .error
            if dataSource != .error {
                dataSource = .error
            }
            
            // ✅ ЭТАП 3: Обработка unauthorized
            let networkError = NetworkError.from(error)
            if case .unauthorized(let message) = networkError {
                let errorMessage: String
                if let message = message, !message.isEmpty {
                    errorMessage = LocalizationManager.shared.localized("analytics_err_unauthorized_detail", message)
                } else {
                    errorMessage = LocalizationManager.shared.localized("analytics_err_session_expired")
                }
                self.errorMessage = errorMessage
                resetState()
                if isOfflineMode {
                    isOfflineMode = false
                }
                // Debounce SessionExpired to avoid global notification cascades.
                let shouldPostSessionExpired: Bool
                if let last = lastSessionExpiredAt {
                    shouldPostSessionExpired = Date().timeIntervalSince(last) > 5
                } else {
                    shouldPostSessionExpired = true
                }
                if shouldPostSessionExpired {
                    lastSessionExpiredAt = Date()
                    NotificationCenter.default.post(
                        name: NSNotification.Name("SessionExpired"),
                        object: nil,
                        userInfo: ["message": errorMessage]
                    )
                } else {
                    VisualLogger.shared.log("⏭️ analytics_session_expired_debounced id=\(loadId)", level: .info, category: "ANALYTICS.API")
                }
                VisualLogger.shared.log("❌ analytics_load_fail id=\(loadId) reason=unauthorized", level: .error, category: "ANALYTICS.API")
                #if DEBUG
                print("⚠️ AnalyticsViewModel: Ошибка авторизации при загрузке аналитики")
                #endif
            } else {
                // Полная ошибка - не удалось получить данные даже через fallback
                let errorMsg = getErrorMessage(from: error)
                errorMessage = errorMsg
                resetState()
                if isOfflineMode {
                    isOfflineMode = false
                }
                VisualLogger.shared.log("❌ analytics_load_fail id=\(loadId) reason=api_fail msg=\(errorMsg)", level: .error, category: "ANALYTICS.API")

                #if DEBUG
                print("❌ AnalyticsViewModel: Ошибка загрузки:")
                print("   - Ошибка: \(error)")
                if let networkError = error as? NetworkError {
                    print("   - Тип: \(networkError)")
                    print("   - Описание: \(networkError.localizedDescription)")
                }
                print("   - Сообщение пользователю: \(errorMsg)")
                #endif
            }
        }
        VisualLogger.shared.log("🏁 analytics_load_finish id=\(loadId) loading=\(isLoading)", level: .info, category: "ANALYTICS.API")
    }

    @MainActor
    private func applyWatchdogTimeoutIfNeeded() {
        guard isLoading else { return }
        let loadId = currentLoadId ?? "unknown"
        isLoading = false
        errorMessage = LocalizationManager.shared.localized("analytics_err_watchdog")
        if dataSource == .empty {
            dataSource = .error
        }
        VisualLogger.shared.log("⏱️ analytics_watchdog_timeout id=\(loadId) -> controlled_stop", level: .warning, category: "ANALYTICS.API")
    }

    @MainActor
    func cancelAll(reason: String) {
        loadTask?.cancel()
        loadTask = nil
        componentsTask?.cancel()
        componentsTask = nil
        watchdogTask?.cancel()
        watchdogTask = nil
        if isLoading {
            isLoading = false
        }
        let loadId = currentLoadId ?? "none"
        VisualLogger.shared.log("🛑 analytics_cancel_all id=\(loadId) reason=\(reason)", level: .warning, category: "ANALYTICS.API")
    }

    @MainActor
    private func startComponentsLoad(loadId: String) {
        componentsTask?.cancel()
        componentsTask = Task { [weak self] in
            guard let self = self else { return }
            guard let remoteService = self.service as? RemoteAnalyticsService else { return }

            await MainActor.run {
                VisualLogger.shared.log("📦 analytics_components_start id=\(loadId) count=7", level: .info, category: "ANALYTICS.API")
            }

            do {
                let components = try await self.withTimeout(seconds: 6) {
                    try await remoteService.fetchAllComponentsStats()
                }
                await MainActor.run {
                    self.componentsAnalytics = components
                    self.componentsDataSource = .api
                    VisualLogger.shared.log("✅ analytics_components_ok id=\(loadId)", level: .success, category: "ANALYTICS.API")
                }
            } catch {
                if Task.isCancelled { return }
                await MainActor.run {
                    self.componentsDataSource = .error
                    VisualLogger.shared.log("⚠️ analytics_components_fail id=\(loadId) reason=\(error.localizedDescription)", level: .warning, category: "ANALYTICS.API")
                }
            }
        }
    }

    private func withTimeout<T>(seconds: Double, operation: @escaping () async throws -> T) async throws -> T {
        try await withThrowingTaskGroup(of: T.self) { group in
            group.addTask { try await operation() }
            group.addTask {
                try await Task.sleep(nanoseconds: UInt64(seconds * 1_000_000_000))
                throw NetworkError.timeout
            }
            let result = try await group.next()!
            group.cancelAll()
            return result
        }
    }
    
    // ✅ УЛУЧШЕНИЕ: Функция для получения понятного сообщения об ошибке
    private func getErrorMessage(from error: Error) -> String {
        let loc = LocalizationManager.shared
        if let networkError = error as? NetworkError {
            switch networkError {
            case .noConnection:
                return loc.localized("analytics_err_no_connection")
            case .timeout:
                return loc.localized("analytics_err_timeout")
            case .serverUnavailable:
                return loc.localized("analytics_err_server_unavailable")
            case .badRequest(let message):
                if let msg = message {
                    return loc.localized("analytics_err_bad_request_detail", msg)
                }
                return loc.localized("analytics_err_bad_request")
            case .unauthorized(let message):
                if let msg = message {
                    return loc.localized("analytics_err_unauthorized_detail", msg)
                }
                return loc.localized("analytics_err_auth_required")
            case .forbidden:
                return loc.localized("analytics_err_forbidden")
            case .notFound:
                return loc.localized("analytics_err_not_found")
            case .internalServerError(let message):
                if let msg = message {
                    return loc.localized("analytics_err_server_detail", msg)
                }
                return loc.localized("analytics_err_server_generic")
            case .invalidResponse:
                return loc.localized("analytics_err_invalid_response")
            case .decodingError(let error):
                return loc.localized("analytics_err_decoding", error.localizedDescription)
            default:
                return loc.localized("analytics_err_generic")
            }
        }
        
        if error.localizedDescription.contains("URL") {
            return loc.localized("analytics_err_invalid_url")
        } else if error.localizedDescription.contains("response") {
            return loc.localized("analytics_err_bad_response_generic")
        } else if error.localizedDescription.contains("status") {
            return loc.localized("analytics_err_server_generic")
        } else if error.localizedDescription.contains("decoding") {
            return loc.localized("analytics_err_decoding", error.localizedDescription)
        } else if let urlError = error as? URLError {
            switch urlError.code {
            case .notConnectedToInternet:
                return loc.localized("analytics_err_no_connection")
            case .timedOut:
                return loc.localized("analytics_err_timeout")
            default:
                return loc.localized("analytics_err_network_detail", urlError.localizedDescription)
            }
        }
        
        return error.localizedDescription.isEmpty ? loc.localized("analytics_err_generic") : error.localizedDescription
    }
    
    // MARK: - Private helpers
    private func apply(summary: AnalyticsSummary) {
        logger.business("Applying analytics summary: \(summary.threatsDetected) threats detected")
        if threatsDetected != summary.threatsDetected { threatsDetected = summary.threatsDetected }
        if threatsBlocked != summary.threatsBlocked { threatsBlocked = summary.threatsBlocked }
        if itemsScanned != summary.itemsScanned { itemsScanned = summary.itemsScanned }
        if protectionLevel != summary.protectionLevel { protectionLevel = summary.protectionLevel }
    }
    
    private func apply(securityAnalytics: SecurityAnalytics) {
        logger.business("Applying security analytics data")
        if threatCategories != securityAnalytics.blockedThreats {
            threatCategories = securityAnalytics.blockedThreats
        }
    }
    
    @MainActor
    private func resetState() {
        if threatsDetected != 0 { threatsDetected = 0 }
        if threatsBlocked != 0 { threatsBlocked = 0 }
        if itemsScanned != 0 { itemsScanned = 0 }
        if protectionLevel != 0 { protectionLevel = 0 }
        if !threatCategories.isEmpty { threatCategories = [] }
    }
    
    // ✅ ВАРИАНТ 9: Загрузка кэшированных данных в офлайн режиме
    @MainActor
    private func loadCachedDataIfAvailable() async {
        // Пробуем загрузить кэшированные данные из сервиса
        if let remoteService = service as? RemoteAnalyticsService {
            do {
                // Пробуем загрузить summary из кэша
                let summaryResult = try await remoteService.fetchSummary(
                    period: cachedPeriod,
                    filters: cachedFilters
                )
                let (summary, summarySource) = summaryResult
                
                // Если данные из кэша - применяем их
                if summarySource == .cache {
                    #if DEBUG
                    print("✅ AnalyticsViewModel: Загружены кэшированные данные summary")
                    #endif
                    apply(summary: summary)
                    isOfflineMode = true
                    dataSource = .cache
                }
                
                // Пробуем загрузить security из кэша
                let securityResult = try await remoteService.fetchSecurityAnalytics(
                    period: cachedPeriod
                )
                let (security, securitySource) = securityResult
                
                // Если данные из кэша - применяем их
                if securitySource == .cache {
                    #if DEBUG
                    print("✅ AnalyticsViewModel: Загружены кэшированные данные security")
                    #endif
                    apply(securityAnalytics: security)
                    isOfflineMode = true
                    if dataSource == .empty {
                        dataSource = .cache
                    }
                }
                
                // Если загрузили хотя бы что-то из кэша - показываем офлайн режим
                if summarySource == .cache || securitySource == .cache {
                    isOfflineMode = true
                    #if DEBUG
                    print("✅ AnalyticsViewModel: Офлайн режим активирован с кэшированными данными")
                    #endif
                }
            } catch {
                #if DEBUG
                print("⚠️ AnalyticsViewModel: Не удалось загрузить кэшированные данные: \(error)")
                #endif
                // Если не удалось загрузить кэш - ничего не делаем
                // Пользователь увидит ошибку и кнопку "Войти"
            }
        }
    }
}
