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
    
    private let service: AnalyticsService
    private let defaultPeriod = "day"
    private let defaultFilters = AnalyticsFilters(onlyBlocked: false, includeFamily: true, includeDevices: true)
    
    init(service: AnalyticsService) {
        self.service = service
    }
    
    @MainActor
    func load() async {
        isLoading = true
        errorMessage = nil
        
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
            
            apply(summary: summary)
            apply(securityAnalytics: security)
        } catch {
            // ✅ УЛУЧШЕНИЕ: Улучшенная обработка ошибок
            let errorMsg = getErrorMessage(from: error)
            errorMessage = errorMsg
            resetState()
            
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
        
        // Для других типов ошибок (например, AnalyticsAPIError)
        if let apiError = error as? AnalyticsAPIError {
            switch apiError {
            case .invalidURL:
                return "Некорректный URL запроса."
            case .invalidResponse:
                return "Некорректный ответ от сервера."
            case .badStatus(let code):
                return "Ошибка сервера (код \(code)). Попробуйте позже."
            case .decoding(let error):
                return "Ошибка обработки данных: \(error.localizedDescription)"
            case .transport(let error):
                if let urlError = error as? URLError {
                    switch urlError.code {
                    case .notConnectedToInternet:
                        return "Нет подключения к интернету. Проверьте соединение."
                    case .timedOut:
                        return "Превышено время ожидания. Попробуйте позже."
                    default:
                        return "Ошибка сети: \(urlError.localizedDescription)"
                    }
                }
                return "Ошибка сети: \(error.localizedDescription)"
            }
        }
        
        // Для других типов ошибок
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
