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
        // ✅ ЭТАП 2: Проверка токена перед загрузкой данных
        guard AppConfig.authToken != nil else {
            print("⚠️ AnalyticsViewModel: Токен отсутствует, пропускаем загрузку аналитики")
            errorMessage = "Требуется авторизация для просмотра аналитики."
            isLoading = false
            isOfflineMode = false
            dataSource = .error
            // Отправляем уведомление о необходимости логина
            NotificationCenter.default.post(
                name: NSNotification.Name("SessionExpired"),
                object: nil,
                userInfo: ["message": "Требуется авторизация. Войдите в аккаунт для просмотра аналитики."]
            )
            return
        }
        
        isLoading = true
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
            async let summaryTask = service.fetchSummary(period: cachedPeriod, filters: cachedFilters)
            async let securityTask = service.fetchSecurityAnalytics(period: cachedPeriod)

            let (summaryResult, securityResult) = try await (summaryTask, securityTask)
            
            // Извлекаем данные и источник
            let (summary, summarySource) = summaryResult
            let (security, securitySource) = securityResult
            
            // Определяем общий источник данных
            dataSource = summarySource == .api && securitySource == .api ? .api :
                         summarySource == .cache || securitySource == .cache ? .cache : .empty

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
            isOfflineMode = (summarySource == .cache || securitySource == .cache)

            apply(summary: summary)
            apply(securityAnalytics: security)
            
            // ✅ ВАРИАНТ 4: Загружаем данные компонентов (если сервис поддерживает)
            if let remoteService = service as? RemoteAnalyticsService {
                do {
                    #if DEBUG
                    print("📊 AnalyticsViewModel: Начинаем загрузку компонентов...")
                    #endif
                    let components = try await remoteService.fetchAllComponentsStats()
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
            
            // ✅ ВАРИАНТ 4: Убеждаемся, что isLoading установлен в false
            isLoading = false

        } catch {
            // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности даже при ошибке
            PerformanceMonitor.shared.endScreenLoad("AnalyticsScreen")
            
            // ✅ ВАРИАНТ 4: Если ошибка - устанавливаем dataSource = .error
            dataSource = .error
            
            // ✅ ЭТАП 3: Обработка unauthorized
            let networkError = NetworkError.from(error)
            if case .unauthorized(let message) = networkError {
                let errorMessage = message ?? "Сессия истекла. Пожалуйста, войдите снова."
                self.errorMessage = errorMessage
                resetState()
                isOfflineMode = false
                // Отправляем уведомление о необходимости логина
                NotificationCenter.default.post(
                    name: NSNotification.Name("SessionExpired"),
                    object: nil,
                    userInfo: ["message": errorMessage]
                )
                #if DEBUG
                print("⚠️ AnalyticsViewModel: Ошибка авторизации при загрузке аналитики")
                #endif
            } else {
                // Полная ошибка - не удалось получить данные даже через fallback
                let errorMsg = getErrorMessage(from: error)
                errorMessage = errorMsg
                resetState()
                isOfflineMode = false

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

        isLoading = false
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
        threatsDetected = summary.threatsDetected
        threatsBlocked = summary.threatsBlocked
        itemsScanned = summary.itemsScanned
        protectionLevel = summary.protectionLevel
    }
    
    private func apply(securityAnalytics: SecurityAnalytics) {
        logger.business("Applying security analytics data")
        threatCategories = securityAnalytics.blockedThreats
    }
    
    @MainActor
    private func resetState() {
        threatsDetected = 0
        threatsBlocked = 0
        itemsScanned = 0
        protectionLevel = 0
        threatCategories = []
    }
}
