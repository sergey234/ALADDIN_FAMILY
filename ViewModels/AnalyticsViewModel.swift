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
    
    private let service: AnalyticsService
    private var watchdogTask: Task<Void, Never>?
    private var lastLoadStartAt: Date?
    
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
    func load() async {
        // Guard against rapid re-entry bursts from multiple UI triggers.
        if let lastLoadStartAt = self.lastLoadStartAt, Date().timeIntervalSince(lastLoadStartAt) < 0.8 {
            VisualLogger.shared.log("⏭️ Analytics load throttled (<0.8s)", level: .info, category: "ANALYTICS.API")
            return
        }
        if isLoading {
            VisualLogger.shared.log("⏭️ Analytics load skipped: already loading", level: .info, category: "ANALYTICS.API")
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
                    errorMessage = "Не удалось загрузить данные аналитики. Проверьте подключение к интернету."
                    VisualLogger.shared.log("❌ AnalyticsViewModel: token_wait_timeout -> empty", level: .error, category: "ANALYTICS.API")
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
                errorMessage = "Не удалось загрузить данные аналитики. Проверьте подключение к интернету."
                VisualLogger.shared.log("❌ AnalyticsViewModel: token_absent -> empty", level: .error, category: "ANALYTICS.API")
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
            if let remoteService = service as? RemoteAnalyticsService {
                do {
                    #if DEBUG
                    print("📊 AnalyticsViewModel: Начинаем загрузку компонентов...")
                    #endif
                    let components = try await withTimeout(seconds: 6) {
                        try await remoteService.fetchAllComponentsStats()
                    }
                    componentsAnalytics = components
                    componentsDataSource = .api // Если загрузилось успешно - данные из API
                    #if DEBUG
                    print("✅ AnalyticsViewModel: Компоненты загружены успешно")
                    #endif
                } catch {
                    #if DEBUG
                    print("⚠️ AnalyticsViewModel: Ошибка загрузки компонентов: \(error)")
                    #endif
                    // При ошибке компоненты остаются nil - UI покажет пустые данные
                    componentsDataSource = .error
                }
            }

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
                let errorMessage = message ?? "Сессия истекла. Пожалуйста, войдите снова."
                self.errorMessage = errorMessage
                resetState()
                if isOfflineMode {
                    isOfflineMode = false
                }
                // Отправляем уведомление о необходимости логина
                NotificationCenter.default.post(
                    name: NSNotification.Name("SessionExpired"),
                    object: nil,
                    userInfo: ["message": errorMessage]
                )
                VisualLogger.shared.log("❌ AnalyticsViewModel: unauthorized -> empty", level: .error, category: "ANALYTICS.API")
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
                VisualLogger.shared.log("❌ AnalyticsViewModel: api_fail -> empty (\(errorMsg))", level: .error, category: "ANALYTICS.API")

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

    }

    @MainActor
    private func applyWatchdogTimeoutIfNeeded() {
        guard isLoading else { return }
        isLoading = false
        errorMessage = "Загрузка аналитики заняла слишком много времени. Попробуйте снова."
        if dataSource == .empty {
            dataSource = .error
        }
        VisualLogger.shared.log("⏱️ Analytics watchdog timeout -> controlled stop", level: .warning, category: "ANALYTICS.API")
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
        if let networkError = error as? NetworkError {
            switch networkError {
            case .noConnection:
                return "Нет подключения к интернету. Проверьте соединение и попробуйте снова."
            case .timeout:
                return "Превышено время ожидания. Проверьте соединение и попробуйте снова."
            case .serverUnavailable:
                return "Сервер временно недоступен. Попробуйте позже."
            case .badRequest(let message):
                if let msg = message {
                    return "Ошибка в данных: \(msg)"
                }
                return "Проверьте правильность запроса."
            case .unauthorized(let message):
                if let msg = message {
                    return "Ошибка авторизации: \(msg)"
                }
                return "Требуется авторизация. Войдите в аккаунт."
            case .forbidden:
                return "Недостаточно прав для просмотра аналитики."
            case .notFound:
                return "Ресурс не найден. Возможно, endpoint не существует."
            case .internalServerError(let message):
                if let msg = message {
                    return "Ошибка сервера: \(msg)"
                }
                return "Ошибка сервера. Попробуйте позже."
            case .invalidResponse:
                return "Некорректный ответ от сервера."
            case .decodingError(let error):
                return "Ошибка обработки данных: \(error.localizedDescription)"
            default:
                return "Не удалось загрузить аналитику. Попробуйте позже."
            }
        }
        
        // Общая обработка ошибок
        if error.localizedDescription.contains("URL") {
            return "Некорректный URL запроса."
        } else if error.localizedDescription.contains("response") {
            return "Некорректный ответ от сервера."
        } else if error.localizedDescription.contains("status") {
            return "Ошибка сервера. Попробуйте позже."
        } else if error.localizedDescription.contains("decoding") {
            return "Ошибка обработки данных: \(error.localizedDescription)"
        } else if let urlError = error as? URLError {
            switch urlError.code {
            case .notConnectedToInternet:
                return "Нет подключения к интернету. Проверьте соединение."
            case .timedOut:
                return "Превышено время ожидания. Попробуйте позже."
            default:
                return "Ошибка сети: \(urlError.localizedDescription)"
            }
        }
        
        return error.localizedDescription.isEmpty ? "Не удалось загрузить аналитику. Попробуйте позже." : error.localizedDescription
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
