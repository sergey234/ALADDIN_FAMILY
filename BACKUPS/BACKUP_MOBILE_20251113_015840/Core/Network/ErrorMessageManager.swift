import Foundation
import SwiftUI

/**
 * Менеджер пользовательских сообщений об ошибках
 * Обеспечивает дружелюбные и понятные сообщения для пользователей
 */
class ErrorMessageManager: ObservableObject {
    
    // MARK: - Published Properties
    
    /// Текущее сообщение об ошибке
    @Published var currentError: ErrorMessage?
    
    /// Показывать ли сообщение об ошибке
    @Published var showError: Bool = false
    
    /// История ошибок для аналитики
    @Published private var errorHistory: [ErrorMessage] = []
    
    // MARK: - Configuration
    
    /// Максимальное количество ошибок в истории
    private let maxHistorySize = 100
    
    /// Время показа сообщения об ошибке (в секундах)
    private let errorDisplayDuration: TimeInterval = 5.0
    
    // MARK: - Singleton
    
    static let shared = ErrorMessageManager()
    
    private init() {}
    
    // MARK: - Public Methods
    
    /**
     * Показывает сообщение об ошибке пользователю
     * - Parameter error: Ошибка для отображения
     * - Parameter context: Дополнительный контекст ошибки
     */
    func showError(_ error: NetworkError, context: String? = nil) {
        let errorMessage = createErrorMessage(from: error, context: context)
        displayError(errorMessage)
    }
    
    /**
     * Показывает сообщение об ошибке с кастомным текстом
     * - Parameter title: Заголовок ошибки
     * - Parameter message: Сообщение об ошибке
     * - Parameter type: Тип ошибки
     * - Parameter action: Действие для исправления
     */
    func showCustomError(
        title: String,
        message: String,
        type: ErrorType = .warning,
        action: ErrorAction? = nil
    ) {
        let errorMessage = ErrorMessage(
            id: UUID(),
            title: title,
            message: message,
            type: type,
            action: action,
            timestamp: Date(),
            context: nil
        )
        displayError(errorMessage)
    }
    
    /**
     * Скрывает текущее сообщение об ошибке
     */
    func hideError() {
        DispatchQueue.main.async {
            self.showError = false
            self.currentError = nil
        }
    }
    
    /**
     * Очищает историю ошибок
     */
    func clearHistory() {
        errorHistory.removeAll()
    }
    
    // MARK: - Private Methods
    
    /**
     * Создает ErrorMessage из NetworkError
     */
    private func createErrorMessage(from error: NetworkError, context: String?) -> ErrorMessage {
        let (title, message, type, action) = getErrorDetails(for: error)
        
        return ErrorMessage(
            id: UUID(),
            title: title,
            message: message,
            type: type,
            action: action,
            timestamp: Date(),
            context: context
        )
    }
    
    /**
     * Отображает сообщение об ошибке
     */
    private func displayError(_ errorMessage: ErrorMessage) {
        DispatchQueue.main.async {
            // Добавляем в историю
            self.addToHistory(errorMessage)
            
            // Показываем пользователю
            self.currentError = errorMessage
            self.showError = true
            
            // Автоматически скрываем через заданное время
            if errorMessage.type != .critical {
                DispatchQueue.main.asyncAfter(deadline: .now() + self.errorDisplayDuration) {
                    if self.currentError?.id == errorMessage.id {
                        self.hideError()
                    }
                }
            }
        }
    }
    
    /**
     * Добавляет ошибку в историю
     */
    private func addToHistory(_ errorMessage: ErrorMessage) {
        errorHistory.append(errorMessage)
        
        // Ограничиваем размер истории
        if errorHistory.count > maxHistorySize {
            errorHistory.removeFirst(errorHistory.count - maxHistorySize)
        }
    }
    
    /**
     * Получает детали ошибки для отображения
     */
    private func getErrorDetails(for error: NetworkError) -> (String, String, ErrorType, ErrorAction?) {
        switch error {
        // Connection Errors
        case .noConnection:
            return (
                "Нет подключения",
                "Проверьте подключение к интернету и попробуйте снова",
                .error,
                .retry
            )
        case .timeout:
            return (
                "Превышено время ожидания",
                "Сервер не отвечает. Попробуйте еще раз",
                .warning,
                .retry
            )
        case .serverUnavailable:
            return (
                "Сервер недоступен",
                "Сервер временно не работает. Попробуйте позже",
                .warning,
                .retry
            )
        case .dnsResolutionFailed:
            return (
                "Не удалось найти сервер",
                "Проверьте подключение к интернету",
                .error,
                .retry
            )
            
        // SSL/Security Errors
        case .sslPinningFailed:
            return (
                "Ошибка безопасности",
                "Проблема с безопасностью соединения. Обновите приложение",
                .critical,
                .update
            )
        case .invalidCertificate:
            return (
                "Недействительный сертификат",
                "Проблема с сертификатом сервера. Обратитесь в поддержку",
                .critical,
                .contactSupport
            )
        case .encryptionError:
            return (
                "Ошибка шифрования",
                "Не удалось зашифровать данные. Попробуйте снова",
                .critical,
                .retry
            )
            
        // HTTP Errors
        case .badRequest(let message):
            return (
                "Неверный запрос",
                message ?? "Проверьте введенные данные",
                .error,
                .checkInput
            )
        case .unauthorized(let message):
            return (
                "Не авторизован",
                message ?? "Войдите в систему заново",
                .warning,
                .login
            )
        case .forbidden(let message):
            return (
                "Доступ запрещен",
                message ?? "У вас нет прав для этого действия",
                .error,
                .contactSupport
            )
        case .notFound(let message):
            return (
                "Не найдено",
                message ?? "Запрашиваемый ресурс не найден",
                .warning,
                .retry
            )
        case .tooManyRequests(let message):
            return (
                "Слишком много запросов",
                message ?? "Подождите несколько минут и попробуйте снова",
                .warning,
                .wait
            )
        case .internalServerError(let message):
            return (
                "Ошибка сервера",
                message ?? "Временная проблема на сервере. Попробуйте позже",
                .error,
                .retry
            )
        case .badGateway(let message):
            return (
                "Ошибка шлюза",
                message ?? "Сервер временно недоступен",
                .warning,
                .retry
            )
        case .serviceUnavailable(let message):
            return (
                "Сервис недоступен",
                message ?? "Сервис временно не работает",
                .warning,
                .retry
            )
            
        // Data Errors
        case .invalidData:
            return (
                "Неверные данные",
                "Получены некорректные данные от сервера",
                .error,
                .retry
            )
        case .decodingError(let error):
            return (
                "Ошибка обработки данных",
                "Не удалось обработать данные: \(error.localizedDescription)",
                .error,
                .retry
            )
        case .emptyResponse:
            return (
                "Пустой ответ",
                "Сервер вернул пустой ответ",
                .warning,
                .retry
            )
            
        // Authentication Errors
        case .tokenExpired:
            return (
                "Сессия истекла",
                "Войдите в систему заново",
                .warning,
                .login
            )
        case .invalidToken:
            return (
                "Неверный токен",
                "Проблема с авторизацией. Войдите заново",
                .warning,
                .login
            )
        case .reauthenticationRequired:
            return (
                "Требуется повторная авторизация",
                "Войдите в систему заново для продолжения",
                .warning,
                .login
            )
            
        // API Errors
        case .apiError(let message, let code):
            return (
                "Ошибка API",
                "\(message)\(code != nil ? " (код: \(code!))" : "")",
                .error,
                .retry
            )
        case .validationError(let errors):
            let errorMessages = errors.values.joined(separator: ", ")
            return (
                "Ошибка валидации",
                errorMessages,
                .error,
                .checkInput
            )
        case .businessLogicError(let message):
            return (
                "Ошибка логики",
                message,
                .error,
                .contactSupport
            )
            
        // System Errors
        case .outOfMemory:
            return (
                "Недостаточно памяти",
                "Закройте другие приложения и попробуйте снова",
                .critical,
                .closeApps
            )
        case .fileSystemError(let error):
            return (
                "Ошибка файловой системы",
                "Проблема с сохранением данных: \(error.localizedDescription)",
                .error,
                .retry
            )
        case .unknown(let error):
            return (
                "Неизвестная ошибка",
                error?.localizedDescription ?? "Произошла неожиданная ошибка",
                .error,
                .retry
            )
        case .invalidStatusCode(let code):
            return (
                "Неверный статус код",
                "Сервер вернул неожиданный ответ: \(code)",
                .error,
                .retry
            )
        default:
            return (
                "Неизвестная ошибка",
                "Произошла непредвиденная ошибка",
                .error,
                .retry
            )
        }
    }
    
    // MARK: - Analytics
    
    /**
     * Возвращает статистику ошибок
     */
    func getErrorStatistics() -> ErrorStatistics {
        let totalErrors = errorHistory.count
        let criticalErrors = errorHistory.filter { $0.type == .critical }.count
        let recentErrors = errorHistory.filter { 
            Date().timeIntervalSince($0.timestamp) < 3600 // Последний час
        }.count
        
        return ErrorStatistics(
            totalErrors: totalErrors,
            criticalErrors: criticalErrors,
            recentErrors: recentErrors,
            mostCommonError: getMostCommonError()
        )
    }
    
    /**
     * Получает наиболее частую ошибку
     */
    private func getMostCommonError() -> String? {
        let errorCounts = Dictionary(grouping: errorHistory, by: { $0.title })
            .mapValues { $0.count }
        
        return errorCounts.max { $0.value < $1.value }?.key
    }
}

// MARK: - ErrorMessage

/**
 * Структура сообщения об ошибке
 */
struct ErrorMessage: Identifiable {
    let id: UUID
    let title: String
    let message: String
    let type: ErrorType
    let action: ErrorAction?
    let timestamp: Date
    let context: String?
}

// MARK: - ErrorType

/**
 * Типы ошибок для визуального отображения
 */
enum ErrorType {
    case info
    case warning
    case error
    case critical
    
    var color: Color {
        switch self {
        case .info:
            return .blue
        case .warning:
            return .orange
        case .error:
            return .red
        case .critical:
            return .purple
        }
    }
    
    var icon: String {
        switch self {
        case .info:
            return "info.circle"
        case .warning:
            return "exclamationmark.triangle"
        case .error:
            return "xmark.circle"
        case .critical:
            return "exclamationmark.octagon"
        }
    }
}

// MARK: - ErrorAction

/**
 * Действия для исправления ошибок
 */
enum ErrorAction {
    case retry
    case login
    case update
    case contactSupport
    case checkInput
    case wait
    case closeApps
    
    var title: String {
        switch self {
        case .retry:
            return "Повторить"
        case .login:
            return "Войти"
        case .update:
            return "Обновить"
        case .contactSupport:
            return "Поддержка"
        case .checkInput:
            return "Проверить"
        case .wait:
            return "Подождать"
        case .closeApps:
            return "Закрыть приложения"
        }
    }
    
    var icon: String {
        switch self {
        case .retry:
            return "arrow.clockwise"
        case .login:
            return "person.circle"
        case .update:
            return "arrow.down.circle"
        case .contactSupport:
            return "questionmark.circle"
        case .checkInput:
            return "checkmark.circle"
        case .wait:
            return "clock"
        case .closeApps:
            return "xmark.circle"
        }
    }
}

// MARK: - ErrorStatistics

/**
 * Статистика ошибок
 */
struct ErrorStatistics {
    let totalErrors: Int
    let criticalErrors: Int
    let recentErrors: Int
    let mostCommonError: String?
    
    var criticalErrorRate: Double {
        return totalErrors > 0 ? Double(criticalErrors) / Double(totalErrors) : 0
    }
    
    var recentErrorRate: Double {
        return totalErrors > 0 ? Double(recentErrors) / Double(totalErrors) : 0
    }
}
