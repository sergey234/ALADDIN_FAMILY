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
    
    /// Ошибка 409 — конфликт (например, `familyId` не совпадает с семьёй по токену)
    case conflict(String?)
    
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

    /// Шлюз/прод: маршрут отключён до «живого» бэкенда (см. `detail` на API).
    case endpointFeatureUnavailable

    /// Шлюз вернул SFM/mock envelope вместо контракта `/api/content/*` — клиент использует кэш.
    case contentSyncGatewayEnvelope

    /// Неизвестная ошибка
    case unknown(Error?)
    
    // MARK: - LocalizedError Implementation
    
    var errorDescription: String? {
        let L = LocalizationManager.shared
        switch self {
        // Connection Errors — always via LocalizationManager (respects RU/EN app language).
        case .noConnection:
            return L.localized("network_error_no_connection")
        case .noData:
            return L.localized("network_error_no_data")
        case .invalidURL:
            return L.localized("network_error_invalid_url")
        case .invalidResponse:
            return L.localized("network_error_invalid_response")
        case .httpError(let code):
            if code == 504 {
                return L.localized("network_error_http_504")
            }
            return String(format: L.localized("network_error_http"), code)
        case .timeout:
            return L.localized("network_error_timeout")
        case .serverUnavailable:
            return L.localized("network_error_server_unavailable")
        case .dnsResolutionFailed:
            return L.localized("network_error_dns")
            
        // SSL/Security Errors
        case .sslPinningFailed:
            return L.localized("network_error_ssl_pinning")
        case .invalidCertificate:
            return L.localized("network_error_invalid_certificate")
        case .encryptionError:
            return L.localized("network_error_encryption")
            
        // HTTP Errors
        case .invalidStatusCode(let code):
            return String(format: L.localized("network_error_invalid_status"), code)
        case .badRequest(let message):
            return String(format: L.localized("network_error_bad_request"), message ?? L.localized("network_error_generic_unknown"))
        case .unauthorized(let message):
            return String(format: L.localized("network_error_unauthorized"), message ?? L.localized("network_error_check_credentials"))
        case .forbidden(let message):
            return String(format: L.localized("network_error_forbidden"), message ?? L.localized("network_error_insufficient_rights"))
        case .notFound(let message):
            return String(format: L.localized("network_error_not_found"), message ?? L.localized("network_error_check_url"))
        case .conflict(let message):
            return message ?? L.localized("network_error_conflict_default")
        case .tooManyRequests(let message):
            return message ?? L.localized("network_error_too_many")
        case .internalServerError(let message):
            return message ?? L.localized("network_error_internal")
        case .badGateway(let message):
            return message ?? L.localized("network_error_bad_gateway")
        case .serviceUnavailable(let message):
            return message ?? L.localized("network_error_service_unavailable")
            
        // Data Errors
        case .invalidData:
            return L.localized("network_error_invalid_data")
        case .decodingError(let error):
            // Use app language — do not append system DecodingError text (often device-locale RU).
            _ = error
            return LocalizationManager.shared.localized("network_error_decoding")
        case .encodingError(let error):
            return String(format: L.localized("network_error_encoding"), error.localizedDescription)
        case .emptyResponse:
            return L.localized("network_error_empty_response")
            
        // Authentication Errors
        case .tokenExpired:
            return L.localized("network_error_token_expired")
        case .invalidToken:
            return L.localized("network_error_invalid_token")
        case .reauthenticationRequired:
            return L.localized("network_error_reauth")
            
        // API Errors
        case .apiError(let message, let code):
            _ = code
            return String(format: L.localized("network_error_api"), message)
        case .validationError(let errors):
            let errorMessages = errors.values.joined(separator: ", ")
            return String(format: L.localized("network_error_validation"), errorMessages)
        case .businessLogicError(let message):
            return String(format: L.localized("network_error_business"), message)
            
        // System Errors
        case .outOfMemory:
            return L.localized("network_error_oom")
        case .fileSystemError(let error):
            return String(format: L.localized("network_error_filesystem"), error.localizedDescription)
        case .circuitBreakerActive(let message):
            return message ?? L.localized("network_error_circuit")
        case .endpointFeatureUnavailable:
            return LocalizationManager.shared.localized("api_error_endpoint_feature_unavailable")

        case .contentSyncGatewayEnvelope:
            return L.localized("network_error_content_sync")

        case .unknown(let error):
            return String(format: L.localized("network_error_unknown"), error?.localizedDescription ?? L.localized("network_error_try_later"))
        }
    }
    
    var failureReason: String? {
        let L = LocalizationManager.shared
        switch self {
        case .noConnection:
            return L.localized("network_error_failure_no_connection")
        case .timeout:
            return L.localized("network_error_failure_timeout")
        case .sslPinningFailed:
            return L.localized("network_error_failure_ssl")
        case .tokenExpired:
            return L.localized("network_error_failure_reauth")
        case .tooManyRequests:
            return L.localized("network_error_failure_rate_limit")
        case .endpointFeatureUnavailable:
            return L.localized("api_error_endpoint_feature_unavailable_reason")
        case .contentSyncGatewayEnvelope:
            return L.localized("network_error_failure_content_sync")
        default:
            return L.localized("network_error_failure_support")
        }
    }
    
    var recoverySuggestion: String? {
        let L = LocalizationManager.shared
        switch self {
        case .noConnection:
            return L.localized("network_error_recovery_no_connection")
        case .timeout:
            return L.localized("network_error_recovery_timeout")
        case .serverUnavailable:
            return L.localized("network_error_recovery_later")
        case .sslPinningFailed:
            return L.localized("network_error_recovery_update_app")
        case .tokenExpired:
            return L.localized("network_error_recovery_sign_in")
        case .tooManyRequests:
            return L.localized("network_error_recovery_rate_limit")
        case .endpointFeatureUnavailable:
            return L.localized("api_error_endpoint_feature_unavailable_recovery")
        case .contentSyncGatewayEnvelope:
            return L.localized("network_error_recovery_content_sync")
        default:
            return L.localized("network_error_recovery_restart")
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
        case 409:
            return .conflict(message)
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

    /// Конфликт контекста семьи при `GET /api/family/members` (HTTP 409).
    var isFamilyMembersContextConflict: Bool {
        switch self {
        case .conflict:
            return true
        case .httpError(let code) where code == 409:
            return true
        default:
            return false
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
             (.outOfMemory, .outOfMemory),
             (.endpointFeatureUnavailable, .endpointFeatureUnavailable),
             (.contentSyncGatewayEnvelope, .contentSyncGatewayEnvelope):
            return true
        case (.invalidStatusCode(let lhsCode), .invalidStatusCode(let rhsCode)):
            return lhsCode == rhsCode
        case (.badRequest(let lhsMsg), .badRequest(let rhsMsg)),
             (.unauthorized(let lhsMsg), .unauthorized(let rhsMsg)),
             (.forbidden(let lhsMsg), .forbidden(let rhsMsg)),
             (.notFound(let lhsMsg), .notFound(let rhsMsg)),
             (.conflict(let lhsMsg), .conflict(let rhsMsg)),
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
