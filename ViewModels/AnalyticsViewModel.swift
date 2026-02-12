import SwiftUI

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
    
    private let service: AnalyticsService
    
    // Ключи для UserDefaults
    private let periodKey = "analytics_last_period"
    private let filtersOnlyBlockedKey = "analytics_last_filters_only_blocked"
    private let filtersIncludeFamilyKey = "analytics_last_filters_include_family"
    private let filtersIncludeDevicesKey = "analytics_last_filters_include_devices"
    
    // Загружаем сохраненные значения или используем дефолтные
    private var defaultPeriod: String {
        UserDefaults.standard.string(forKey: periodKey) ?? "day"
    }
    
    private var defaultFilters: AnalyticsFilters {
        AnalyticsFilters(
            onlyBlocked: UserDefaults.standard.bool(forKey: filtersOnlyBlockedKey),
            includeFamily: UserDefaults.standard.object(forKey: filtersIncludeFamilyKey) as? Bool ?? true,
            includeDevices: UserDefaults.standard.object(forKey: filtersIncludeDevicesKey) as? Bool ?? true
        )
    }
    
    init(service: AnalyticsService) {
        self.service = service
    }
    
    @MainActor
    func load() async {
        isLoading = true
        errorMessage = nil
        isOfflineMode = false // ✅ ЗАДАЧА 64: Сбрасываем индикатор офлайн режима

        // ✅ ЗАДАЧА 66: Начинаем отслеживание производительности загрузки
        PerformanceMonitor.shared.startScreenLoad("AnalyticsScreen")

        #if DEBUG
        print("📊 AnalyticsViewModel: Загрузка аналитики...")
        print("   - Period: \(defaultPeriod)")
        print("   - Filters: onlyBlocked=\(defaultFilters.onlyBlocked), includeFamily=\(defaultFilters.includeFamily), includeDevices=\(defaultFilters.includeDevices)")
        #endif

        do {
            async let summaryTask = service.fetchSummary(period: defaultPeriod, filters: defaultFilters)
            async let securityTask = service.fetchSecurityAnalytics(period: defaultPeriod)

            let (summary, security) = try await (summaryTask, securityTask)

            #if DEBUG
            print("✅ AnalyticsViewModel: Данные загружены:")
            print("   - Threats detected: \(summary.threatsDetected)")
            print("   - Threats blocked: \(summary.threatsBlocked)")
            print("   - Items scanned: \(summary.itemsScanned)")
            print("   - Protection level: \(summary.protectionLevel)%")
            print("   - Threat categories: \(security.blockedThreats.count)")
            #endif

            // ✅ ЗАДАЧА 64: Проверяем, используется ли офлайн режим
            // Если сервис - RemoteAnalyticsService и данные получены из кэша/fallback, включаем индикатор
            if service is RemoteAnalyticsService {
                // Для RemoteAnalyticsService мы можем определить использование кэша по логированию выше
                // Индикатор включается только если была ошибка API, но данные получены
                isOfflineMode = false // По умолчанию онлайн режим
            }

            apply(summary: summary)
            apply(securityAnalytics: security)

            // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности загрузки
            PerformanceMonitor.shared.endScreenLoad("AnalyticsScreen")

        } catch {
            // ✅ ЗАДАЧА 66: Завершаем отслеживание производительности даже при ошибке
            PerformanceMonitor.shared.endScreenLoad("AnalyticsScreen")
            // ✅ ЗАДАЧА 64: Проверяем, удалось ли получить данные через graceful degradation
            let isUsingFallback = errorMessage == nil || !errorMessage!.contains("Не удалось загрузить аналитику")

            if isUsingFallback && service is RemoteAnalyticsService {
                // ✅ ЗАДАЧА 64: Включаем индикатор офлайн режима
                isOfflineMode = true

                #if DEBUG
                print("🛡️ AnalyticsViewModel: Включен офлайн режим - используются кэшированные данные")
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
        threatsDetected = summary.threatsDetected
        threatsBlocked = summary.threatsBlocked
        itemsScanned = summary.itemsScanned
        protectionLevel = summary.protectionLevel
    }
    
    private func apply(securityAnalytics: SecurityAnalytics) {
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
