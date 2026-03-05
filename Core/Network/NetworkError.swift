import Foundation

/**
 * Типизированные ошибки сети для ALADDIN
 * Обеспечивает детальную обработку различных типов ошибок
 */
enum NetworkError: Error, LocalizedError {
    
    // MARK: - Connection Errors
    
    /// Нет подключения к интернету
    case noConnection
    
    /// Нет данных в ответе
    case noData
    
    /// Неверный URL
    case invalidURL
    
    /// Неверный ответ сервера
    case invalidResponse
    
    /// HTTP ошибка с кодом
    case httpError(Int)
    
    /// Таймаут запроса
    case timeout
    
    /// Сервер недоступен
    case serverUnavailable
    
    /// DNS не может разрешить домен
    case dnsResolutionFailed
    
    // MARK: - SSL/Security Errors
    
    /// Ошибка SSL Pinning
    case sslPinningFailed
    
    /// Недействительный сертификат
    case invalidCertificate
    
    /// Ошибка шифрования
    case encryptionError
    
    // MARK: - HTTP Errors
    
    /// Неверный HTTP статус код
    case invalidStatusCode(Int)
    
    /// Ошибка 400 - Неверный запрос
    case badRequest(String?)
    
    /// Ошибка 401 - Не авторизован
    case unauthorized(String?)
    
    /// Ошибка 403 - Доступ запрещен
    case forbidden(String?)
    
    /// Ошибка 404 - Не найдено
    case notFound(String?)
    
    /// Ошибка 429 - Слишком много запросов
    case tooManyRequests(String?)
    
    /// Ошибка 500 - Внутренняя ошибка сервера
    case internalServerError(String?)
    
    /// Ошибка 502 - Плохой шлюз
    case badGateway(String?)
    
    /// Ошибка 503 - Сервис недоступен
    case serviceUnavailable(String?)
    
    // MARK: - Data Errors
    
    /// Неверный формат данных
    case invalidData
    
    /// Ошибка декодирования JSON
    case decodingError(Error)
    
    /// Ошибка кодирования JSON
    case encodingError(Error)
    
    /// Пустой ответ от сервера
    case emptyResponse
    
    // MARK: - Authentication Errors
    
    /// Токен истек
    case tokenExpired
    
    /// Неверный токен
    case invalidToken
    
    /// Требуется повторная авторизация
    case reauthenticationRequired
    
    // MARK: - API Errors
    
    /// Ошибка API (кастомная)
    case apiError(String, Int?)
    
    /// Ошибка валидации данных
    case validationError([String: String])
    
    /// Ошибка бизнес-логики
    case businessLogicError(String)
    
    // MARK: - System Errors
    
    /// Недостаточно памяти
    case outOfMemory
    
    /// Ошибка файловой системы
    case fileSystemError(Error)
    
    /// Circuit breaker protection active
    case circuitBreakerActive(String?)

    /// Неизвестная ошибка
    case unknown(Error?)
    
    // MARK: - LocalizedError Implementation
    
    var errorDescription: String? {
        switch self {
        // Connection Errors
        case .noConnection:
            return "Нет подключения к интернету"
        case .noData:
            return "Нет данных в ответе сервера"
        case .invalidURL:
            return "Неверный URL-адрес"
        case .invalidResponse:
            return "Неверный ответ сервера"
        case .httpError(let code):
            return "HTTP ошибка: \(code)"
        case .timeout:
            return "Превышено время ожидания запроса"
        case .serverUnavailable:
            return "Сервер временно недоступен"
        case .dnsResolutionFailed:
            return "Не удалось найти сервер"
            
        // SSL/Security Errors
        case .sslPinningFailed:
            return "Ошибка проверки SSL сертификата"
        case .invalidCertificate:
            return "Недействительный сертификат сервера"
        case .encryptionError:
            return "Ошибка шифрования данных"
            
        // HTTP Errors
        case .invalidStatusCode(let code):
            return "Неверный статус код: \(code)"
        case .badRequest(let message):
            return "Неверный запрос: \(message ?? "Неизвестная ошибка")"
        case .unauthorized(let message):
            return "Не авторизован: \(message ?? "Проверьте учетные данные")"
        case .forbidden(let message):
            return "Доступ запрещен: \(message ?? "Недостаточно прав")"
        case .notFound(let message):
            return "Ресурс не найден: \(message ?? "Проверьте URL")"
        case .tooManyRequests(let message):
            return "Слишком много запросов: \(message ?? "Попробуйте позже")"
        case .internalServerError(let message):
            return "Ошибка сервера: \(message ?? "Попробуйте позже")"
        case .badGateway(let message):
            return "Ошибка шлюза: \(message ?? "Сервер временно недоступен")"
        case .serviceUnavailable(let message):
            return "Сервис недоступен: \(message ?? "Попробуйте позже")"
            
        // Data Errors
        case .invalidData:
            return "Неверный формат данных"
        case .decodingError(let error):
            return "Ошибка обработки данных: \(error.localizedDescription)"
        case .encodingError(let error):
            return "Ошибка подготовки данных: \(error.localizedDescription)"
        case .emptyResponse:
            return "Пустой ответ от сервера"
            
        // Authentication Errors
        case .tokenExpired:
            return "Сессия истекла. Войдите заново"
        case .invalidToken:
            return "Неверный токен авторизации"
        case .reauthenticationRequired:
            return "Требуется повторная авторизация"
            
        // API Errors
        case .apiError(let message, let code):
            return "Ошибка API: \(message)\(code != nil ? " (код: \(code!))" : "")"
        case .validationError(let errors):
            let errorMessages = errors.values.joined(separator: ", ")
            return "Ошибка валидации: \(errorMessages)"
        case .businessLogicError(let message):
            return "Ошибка логики: \(message)"
            
        // System Errors
        case .outOfMemory:
            return "Недостаточно памяти"
        case .fileSystemError(let error):
            return "Ошибка файловой системы: \(error.localizedDescription)"
        case .circuitBreakerActive(let message):
            return message ?? "Сервер временно недоступен. Повторите попытку позже."

        case .unknown(let error):
            return "Неизвестная ошибка: \(error?.localizedDescription ?? "Попробуйте позже")"
        }
    }
    
    var failureReason: String? {
        switch self {
        case .noConnection:
            return "Проверьте подключение к интернету"
        case .timeout:
            return "Попробуйте повторить запрос"
        case .sslPinningFailed:
            return "Проблема с безопасностью соединения"
        case .tokenExpired:
            return "Необходимо войти в систему заново"
        case .tooManyRequests:
            return "Подождите несколько минут"
        default:
            return "Обратитесь в поддержку"
        }
    }
    
    var recoverySuggestion: String? {
        switch self {
        case .noConnection:
            return "Проверьте Wi-Fi или мобильный интернет"
        case .timeout:
            return "Попробуйте еще раз через несколько секунд"
        case .serverUnavailable:
            return "Попробуйте позже"
        case .sslPinningFailed:
            return "Обновите приложение"
        case .tokenExpired:
            return "Войдите в систему заново"
        case .tooManyRequests:
            return "Подождите 5-10 минут"
        default:
            return "Перезапустите приложение"
        }
    }
    
    // MARK: - Helper Methods
    
    /// Проверяет, является ли ошибка критической
    var isCritical: Bool {
        switch self {
        case .sslPinningFailed, .encryptionError, .invalidCertificate:
            return true
        case .outOfMemory, .fileSystemError:
            return true
        default:
            return false
        }
    }
    
    /// Проверяет, можно ли повторить запрос
    var isRetryable: Bool {
        switch self {
        case .timeout, .serverUnavailable, .dnsResolutionFailed:
            return true
        case .badGateway, .serviceUnavailable:
            return true
        case .tooManyRequests:
            return true
        default:
            return false
        }
    }
    
    /// Возвращает рекомендуемую задержку для повтора
    var retryDelay: TimeInterval {
        switch self {
        case .timeout:
            return 2.0
        case .serverUnavailable:
            return 5.0
        case .tooManyRequests:
            return 60.0
        case .badGateway, .serviceUnavailable:
            return 10.0
        default:
            return 1.0
        }
    }
    
    /// Создает NetworkError из URLSessionError
    static func from(urlError: URLError) -> NetworkError {
        switch urlError.code {
        case .notConnectedToInternet:
            return .noConnection
        case .timedOut:
            return .timeout
        case .cannotFindHost, .cannotConnectToHost:
            return .serverUnavailable
        case .dnsLookupFailed:
            return .dnsResolutionFailed
        case .serverCertificateUntrusted, .secureConnectionFailed:
            return .sslPinningFailed
        case .cannotDecodeContentData:
            return .invalidData
        case .dataNotAllowed:
            return .forbidden(nil)
        default:
            return .unknown(urlError)
        }
    }
    
    /// Создает NetworkError из HTTP статус кода
    static func from(httpStatusCode: Int, message: String? = nil) -> NetworkError {
        switch httpStatusCode {
        case 400:
            return .badRequest(message)
        case 401:
            return .unauthorized(message)
        case 403:
            return .forbidden(message)
        case 404:
            return .notFound(message)
        case 429:
            return .tooManyRequests(message)
        case 500:
            return .internalServerError(message)
        case 502:
            return .badGateway(message)
        case 503:
            return .serviceUnavailable(message)
        default:
            return .invalidStatusCode(httpStatusCode)
        }
    }
    
    /// Создает NetworkError из Error
    static func from(_ error: Error) -> NetworkError {
        if let urlError = error as? URLError {
            return from(urlError: urlError)
        } else if let networkError = error as? NetworkError {
            return networkError
        } else {
            return .unknown(error)
        }
    }
}

// MARK: - Equatable

extension NetworkError: Equatable {
    static func == (lhs: NetworkError, rhs: NetworkError) -> Bool {
        switch (lhs, rhs) {
        case (.noConnection, .noConnection),
             (.timeout, .timeout),
             (.serverUnavailable, .serverUnavailable),
             (.dnsResolutionFailed, .dnsResolutionFailed),
             (.sslPinningFailed, .sslPinningFailed),
             (.invalidCertificate, .invalidCertificate),
             (.encryptionError, .encryptionError),
             (.invalidData, .invalidData),
             (.emptyResponse, .emptyResponse),
             (.tokenExpired, .tokenExpired),
             (.invalidToken, .invalidToken),
             (.reauthenticationRequired, .reauthenticationRequired),
             (.outOfMemory, .outOfMemory):
            return true
        case (.invalidStatusCode(let lhsCode), .invalidStatusCode(let rhsCode)):
            return lhsCode == rhsCode
        case (.badRequest(let lhsMsg), .badRequest(let rhsMsg)),
             (.unauthorized(let lhsMsg), .unauthorized(let rhsMsg)),
             (.forbidden(let lhsMsg), .forbidden(let rhsMsg)),
             (.notFound(let lhsMsg), .notFound(let rhsMsg)),
             (.tooManyRequests(let lhsMsg), .tooManyRequests(let rhsMsg)),
             (.internalServerError(let lhsMsg), .internalServerError(let rhsMsg)),
             (.badGateway(let lhsMsg), .badGateway(let rhsMsg)),
             (.serviceUnavailable(let lhsMsg), .serviceUnavailable(let rhsMsg)):
            return lhsMsg == rhsMsg
        case (.apiError(let lhsMsg, let lhsCode), .apiError(let rhsMsg, let rhsCode)):
            return lhsMsg == rhsMsg && lhsCode == rhsCode
        case (.validationError(let lhsErrors), .validationError(let rhsErrors)):
            return lhsErrors == rhsErrors
        case (.businessLogicError(let lhsMsg), .businessLogicError(let rhsMsg)):
            return lhsMsg == rhsMsg
        case (.decodingError(let lhsError), .decodingError(let rhsError)),
             (.encodingError(let lhsError), .encodingError(let rhsError)),
             (.fileSystemError(let lhsError), .fileSystemError(let rhsError)):
            return lhsError.localizedDescription == rhsError.localizedDescription
        case (.unknown(let lhsError), .unknown(let rhsError)):
            return lhsError?.localizedDescription == rhsError?.localizedDescription
        default:
            return false
        }
    }
}
