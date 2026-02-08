import Foundation

/**
 * ⚠️ Component Error Model
 * Модель для обработки ошибок компонентов
 * Локализованные сообщения об ошибках
 */

enum ComponentError: LocalizedError, Equatable {
    case componentNotFound(String)
    case apiError(String)
    case networkError(String)
    case configurationError(String)
    case permissionDenied
    case rateLimitExceeded
    case invalidConfiguration
    case updateFailed(String)
    case cacheError
    case notImplemented
    case unknown(Error)
    
    // MARK: - Equatable
    
    static func == (lhs: ComponentError, rhs: ComponentError) -> Bool {
        switch (lhs, rhs) {
        case (.componentNotFound(let lhsId), .componentNotFound(let rhsId)):
            return lhsId == rhsId
        case (.apiError(let lhsMsg), .apiError(let rhsMsg)):
            return lhsMsg == rhsMsg
        case (.networkError(let lhsMsg), .networkError(let rhsMsg)):
            return lhsMsg == rhsMsg
        case (.configurationError(let lhsMsg), .configurationError(let rhsMsg)):
            return lhsMsg == rhsMsg
        case (.permissionDenied, .permissionDenied):
            return true
        case (.rateLimitExceeded, .rateLimitExceeded):
            return true
        case (.invalidConfiguration, .invalidConfiguration):
            return true
        case (.updateFailed(let lhsMsg), .updateFailed(let rhsMsg)):
            return lhsMsg == rhsMsg
        case (.cacheError, .cacheError):
            return true
        case (.notImplemented, .notImplemented):
            return true
        case (.unknown(let lhsError), .unknown(let rhsError)):
            // Сравниваем по описанию ошибки, так как Error не Equatable
            return lhsError.localizedDescription == rhsError.localizedDescription
        default:
            return false
        }
    }
    
    var errorDescription: String? {
        switch self {
        case .componentNotFound(let id):
            return "Компонент не найден: \(id)"
        case .apiError(let message):
            return "Ошибка API: \(message)"
        case .networkError(let message):
            return "Ошибка сети: \(message)"
        case .configurationError(let message):
            return "Ошибка конфигурации: \(message)"
        case .permissionDenied:
            return "Доступ запрещен. Проверьте права доступа."
        case .rateLimitExceeded:
            return "Превышен лимит запросов. Попробуйте позже."
        case .invalidConfiguration:
            return "Некорректная конфигурация компонента."
        case .updateFailed(let message):
            return "Не удалось обновить: \(message)"
        case .cacheError:
            return "Ошибка кэширования данных."
        case .notImplemented:
            return "Функция не реализована."
        case .unknown(let error):
            return "Неизвестная ошибка: \(error.localizedDescription)"
        }
    }
    
    var recoverySuggestion: String? {
        switch self {
        case .componentNotFound:
            return "Проверьте правильность идентификатора компонента."
        case .apiError:
            return "Попробуйте обновить данные позже."
        case .networkError:
            return "Проверьте подключение к интернету и попробуйте снова."
        case .configurationError:
            return "Проверьте настройки компонента."
        case .permissionDenied:
            return "Обратитесь к администратору для получения доступа."
        case .rateLimitExceeded:
            return "Подождите несколько минут и попробуйте снова."
        case .invalidConfiguration:
            return "Сбросьте настройки компонента до значений по умолчанию."
        case .updateFailed:
            return "Попробуйте обновить компонент позже."
        case .cacheError:
            return "Очистите кэш и попробуйте снова."
        case .notImplemented:
            return "Эта функция будет доступна в будущих версиях."
        case .unknown:
            return "Перезапустите приложение. Если проблема сохраняется, обратитесь в поддержку."
        }
    }
    
    /// Получить локализованное сообщение через LocalizationManager
    func localizedMessage() -> String {
        // Будет использоваться LocalizationManager для локализации
        // Пока возвращаем errorDescription
        return errorDescription ?? "Неизвестная ошибка"
    }
}

// MARK: - NetworkError Conversion

extension ComponentError {
    /// Конвертировать ComponentError в NetworkError
    func toNetworkError() -> NetworkError {
        switch self {
        case .networkError(_):
            return .noConnection
        case .apiError(let message):
            return .badRequest(message)
        case .componentNotFound(let id):
            return .notFound("Component \(id) not found")
        case .configurationError(let message):
            return .badRequest("Configuration error: \(message)")
        case .permissionDenied:
            return .unauthorized("Permission denied")
        case .rateLimitExceeded:
            return .tooManyRequests("Rate limit exceeded")
        case .invalidConfiguration:
            return .badRequest("Invalid configuration")
        case .updateFailed(let message):
            return .badRequest("Update failed: \(message)")
        case .cacheError:
            return .unknown(self)
        case .notImplemented:
            return .badRequest("Not implemented")
        case .unknown(let error):
            if let networkError = error as? NetworkError {
                return networkError
            }
            return .unknown(error)
        }
    }
}

