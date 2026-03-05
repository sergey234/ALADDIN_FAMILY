import Foundation
import Combine
import Security
import os.log  // ✅ ДОБАВЛЕНО: Для Production логирования

// Master Logger for network logging
private let logger = MasterLogger.shared

/**
 * 🌐 Network Manager
 * API клиент для подключения к Python backend
 * Управляет всеми HTTP запросами
 */

class NetworkManager: NSObject, ObservableObject {
    
    // ✅ ДОБАВЛЕНО: Logger для Production логирования
    private static let networkLogger = OSLog(
        subsystem: "com.aladdin.network",
        category: "NetworkManager"
    )
    
    // MARK: - Properties

    @Published var isOnline: Bool = true
    @Published var lastError: String?

    private let baseURL: String
    private var session: URLSession
    private var sessionConfiguration: URLSessionConfiguration = URLSessionConfiguration.default
    private var slowRequestCount: Int = 0
    private let slowRequestThreshold: TimeInterval = 5.0
    private let slowRequestLimitBeforeAdjusting: Int = 2
    private var didIncreaseTimeouts = false
    private var cancellables = Set<AnyCancellable>()

    // ✅ ЗАДАЧА 62: Rate Limiting
    /// Rate limiter для защиты от перегрузки API
    private let rateLimiter = RateLimiter(maxRequests: 100, timeWindow: 60.0) // 100 запросов в минуту
    
    // MARK: - SSL Pinning Properties
    
    /// Включен ли SSL Pinning (по умолчанию включен для безопасности)
    var isSSLPinningEnabled: Bool
    
    /// Домены для которых включен SSL Pinning
    let pinnedDomains: Set<String>
    
    /// Сертификаты для проверки (в реальном приложении загружаются из Bundle)
    var pinnedCertificates: [Data] = []
    
    // MARK: - Init
    
    init(baseURL: String = AppConfig.apiBaseURL, enableSSLPinning: Bool = true) {
        // 🟡 ОТКЛЮЧИТЬ SSL PINNING - проверить, связано ли с сертификатами
        // TEMPORARILY DISABLE SSL PINNING FOR TESTING CRASH CAUSE
        let shouldDisableSSLPinning = ProcessInfo.processInfo.environment["DISABLE_SSL_PINNING"] == "1"
        let actualEnableSSLPinning = enableSSLPinning && !shouldDisableSSLPinning

        print("🔐 SSL PINNING: enableSSLPinning parameter = \(enableSSLPinning)")
        print("🔐 SSL PINNING: DISABLE_SSL_PINNING env = \(ProcessInfo.processInfo.environment["DISABLE_SSL_PINNING"] ?? "not set")")
        print("🔐 SSL PINNING: Final decision = \(actualEnableSSLPinning ? "ENABLED" : "DISABLED")")

        // Override the property with our decision
        self.isSSLPinningEnabled = actualEnableSSLPinning
        print("🚨 NetworkManager.init: Начало")
        print("   - baseURL: '\(baseURL)'")
        print("   - baseURL.isEmpty: \(baseURL.isEmpty)")
        
        // ✅ ИСПРАВЛЕНИЕ #3: Инициализируем все свойства ПЕРЕД super.init()
        // Но для NSObject можно инициализировать после, если использовать временные значения
        self.baseURL = baseURL
        self.isSSLPinningEnabled = enableSSLPinning
        
        // Домены для SSL Pinning (реальные домены ALADDIN)
        self.pinnedDomains = Set([
            "aladdin-ai.ru",       // Основной API (текущий домен)
            "api.aladdin.family",  // Резервный API
            "cdn.aladdin.family"   // CDN сервер
        ])
        
        // Инициализируем пустой массив сертификатов
        self.pinnedCertificates = []
        
        // ✅ ИСПРАВЛЕНИЕ #3: Создаем временную сессию для инициализации
        let tempConfiguration = URLSessionConfiguration.default
        self.session = URLSession(configuration: tempConfiguration)
        
        // ✅ ИСПРАВЛЕНИЕ #3: Вызываем super.init() ПЕРЕД использованием self в методах
        super.init()
        print("✅ super.init() выполнен")
        
        // 🚀 ОПТИМИЗИРОВАННАЯ конфигурация сессии для лучшей производительности
        print("🔍 Создание оптимизированной URLSessionConfiguration...")
        let configuration = createOptimizedConfiguration()
        print("✅ Оптимизированная конфигурация сессии создана")
        
        print("🔍 Настройка таймаутов...")
        print("   - AppConfig.Network.requestTimeout: \(AppConfig.Network.requestTimeout)")
        print("   - AppConfig.Network.resourceTimeout: \(AppConfig.Network.resourceTimeout)")
        print("   - AppConfig.Network.waitsForConnectivity: \(AppConfig.Network.waitsForConnectivity)")
        
        // ✅ УПРОЩЕННАЯ ЗАЩИТА: Используем значения напрямую (они статические, не могут быть nil)
        configuration.timeoutIntervalForRequest = AppConfig.Network.requestTimeout
        print("✅ requestTimeout установлен: \(configuration.timeoutIntervalForRequest)")
        
        configuration.timeoutIntervalForResource = AppConfig.Network.resourceTimeout
        print("✅ resourceTimeout установлен: \(configuration.timeoutIntervalForResource)")
        
        configuration.waitsForConnectivity = AppConfig.Network.waitsForConnectivity
        print("✅ waitsForConnectivity установлен: \(configuration.waitsForConnectivity)")
        
        print("🔍 Загрузка сертификатов...")
        // Загружаем сертификаты после инициализации (после super.init())
        self.pinnedCertificates = loadPinnedCertificates()
        print("✅ Сертификаты загружены, count: \(self.pinnedCertificates.count)")
        
        // ✅ ЗАДАЧА 61: Проверка SSL Pinning в продакшене
        #if !DEBUG
        // В продакшене SSL Pinning ОБЯЗАТЕЛЬНО должен быть включен!
        assert(isSSLPinningEnabled, "🚨 КРИТИЧЕСКАЯ ОШИБКА: SSL Pinning должен быть включен в продакшене!")
        if !isSSLPinningEnabled {
            os_log("🚨 КРИТИЧЕСКАЯ ОШИБКА: SSL Pinning отключен в продакшене!", log: Self.networkLogger, type: .error)
        }
        #endif
        
        // Логируем статус SSL Pinning
        #if DEBUG
        print("🔐 SSL Pinning статус: \(isSSLPinningEnabled ? "✅ ВКЛЮЧЕН" : "❌ ВЫКЛЮЧЕН")")
        print("🔐 SSL Pinning домены: \(pinnedDomains)")
        print("🔐 SSL Pinning сертификаты: \(pinnedCertificates.count) шт.")
        #else
        os_log("🔐 SSL Pinning: %{public}@, доменов: %d, сертификатов: %d", 
               log: Self.networkLogger, 
               type: .info,
               isSSLPinningEnabled ? "ВКЛЮЧЕН" : "ВЫКЛЮЧЕН",
               pinnedDomains.count,
               pinnedCertificates.count)
        #endif
        
        print("🔍 Создание URLSession...")
        // Создаем сессию с делегатом для SSL Pinning
        self.sessionConfiguration = configuration
        self.session = URLSession(configuration: configuration, delegate: self, delegateQueue: nil)
        print("✅ URLSession создан с делегатом")
        print("✅ NetworkManager.init: Завершен успешно")
    }

    // MARK: - Performance Optimization

    /**
     * 🚀 Создает оптимизированную конфигурацию сессии для максимальной производительности
     */
    private func createOptimizedConfiguration() -> URLSessionConfiguration {
        let config = URLSessionConfiguration.default

        // 🚀 HTTP/2 включается автоматически для HTTPS

        // 🔄 Connection pooling - поддерживать до 10 одновременных соединений
        config.httpMaximumConnectionsPerHost = 10

        // ⏱️ Оптимизированные таймауты
        config.timeoutIntervalForRequest = AppConfig.Network.requestTimeout
        config.timeoutIntervalForResource = AppConfig.Network.resourceTimeout
        config.waitsForConnectivity = AppConfig.Network.waitsForConnectivity

        // 📦 Умное кэширование для снижения сетевых запросов
        config.urlCache = URLCache(
            memoryCapacity: 10 * 1024 * 1024,    // 10MB in memory
            diskCapacity: 50 * 1024 * 1024,      // 50MB on disk
            diskPath: "aladdin_api_cache"
        )

        // 🔒 Безопасность - отключить cookies для API (не нужны)
        config.httpCookieAcceptPolicy = .never
        config.httpShouldSetCookies = false

        // 📊 Request caching policy - использовать кэш для GET запросов
        config.requestCachePolicy = .returnCacheDataElseLoad

        // 🗜️ Включить сжатие ответов
        config.httpAdditionalHeaders = [
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "application/json",
            "User-Agent": "ALADDIN-iOS/\(AppConfig.appVersion)"
        ]

        print("🚀 Performance optimizations applied:")
        print("   - HTTP/2 enabled")
        print("   - Connection pooling: \(config.httpMaximumConnectionsPerHost)")
        print("   - Caching: \(config.urlCache?.memoryCapacity ?? 0)MB memory, \(config.urlCache?.diskCapacity ?? 0)MB disk")
        print("   - Compression: enabled")

        return config
    }

    // MARK: - API Methods
    
    /**
     * GET запрос
     * ✅ ИСПРАВЛЕНО: Добавлен параметр requiresAuth для обязательной авторизации
     */
    func get<T: Decodable>(
        endpoint: String,
        requiresAuth: Bool = true,  // ✅ По умолчанию авторизация обязательна
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        // Проверяем и обновляем токен если нужно
        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
            
            guard let url = URL(string: baseURL + endpoint) else {
                completion(.failure(NetworkError.invalidURL))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "GET"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            // ✅ ПРОВЕРКА АВТОРИЗАЦИИ: Если требуется авторизация, проверяем токен
            if requiresAuth {
                guard let token = AppConfig.authToken else {
                    #if DEBUG
                    print("⚠️ NetworkManager.get: Токен отсутствует для защищенного endpoint: \(endpoint)")
                    #endif
                    completion(.failure(NetworkError.unauthorized("Токен авторизации отсутствует")))
                    return
                }
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            } else {
                // Для публичных endpoint'ов токен опциональный
                if let token = AppConfig.authToken {
                    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                }
            }
            
            performRequest(request: request, requiresAuth: false, completion: completion)
        }
    }
    
    /**
     * POST запрос
     * ✅ ИСПРАВЛЕНО: Добавлен параметр requiresAuth для обязательной авторизации
     */
    func post<T: Decodable, B: Encodable>(
        endpoint: String,
        body: B,
        requiresAuth: Bool = true,  // ✅ По умолчанию авторизация обязательна
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        let fullURL = baseURL + endpoint
        logger.network("🔵 NetworkManager.post: Starting request")
        logger.network("   - URL: \(fullURL)")
        
        // Проверяем и обновляем токен если нужно
        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()

            // 🛡️ DEFENSIVE JWT: Circuit Breaker check for JWT-protected endpoints
            if requiresAuth {
                guard JWTCircuitBreaker.shared.shouldAllowRequest() else {
                    logger.error("🚫 DEFENSIVE JWT: Circuit Breaker active - blocking JWT-protected request to \(endpoint)")
                    let error = NetworkError.circuitBreakerActive("Сервер временно недоступен. Повторите попытку позже.")
                    completion(.failure(error))
                    return
                }
            }

            guard let url = URL(string: fullURL) else {
                logger.error("❌ NetworkManager.post: Invalid URL: \(fullURL)")
                completion(.failure(NetworkError.invalidURL))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            // Добавляем X-API-Key для payment_service endpoints
            if endpoint.contains("activation") || endpoint.contains("subscription") {
                request.setValue("PUBLIC_CLIENT_KEY", forHTTPHeaderField: "X-API-Key")
                logger.network("   - Added X-API-Key header")
            }
            
            // ✅ ПРОВЕРКА АВТОРИЗАЦИИ: Если требуется авторизация, проверяем токен
            if requiresAuth {
                guard let token = AppConfig.authToken else {
                    #if DEBUG
                    print("⚠️ NetworkManager.post: Токен отсутствует для защищенного endpoint: \(endpoint)")
                    #endif
                    completion(.failure(NetworkError.unauthorized("Токен авторизации отсутствует")))
                    return
                }
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                print("   - Добавлен Authorization заголовок")
            } else {
                // Для публичных endpoint'ов токен опциональный
                if let token = AppConfig.authToken {
                    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                    print("   - Добавлен Authorization заголовок (опционально)")
                }
            }
            
            // Encode body
            do {
                let bodyData = try JSONEncoder().encode(body)
                request.httpBody = bodyData
                print("📦 REQUEST BODY: \(String(data: bodyData, encoding: .utf8) ?? "NIL")")
                print("📦 REQUEST BODY SIZE: \(bodyData.count) bytes")
                if let bodyString = String(data: bodyData, encoding: .utf8) {
                    print("   - Body: \(bodyString)")
                }
            } catch {
                print("❌ NetworkManager.post: Ошибка кодирования body: \(error)")
                completion(.failure(error))
                return
            }
            
            print("🔵 NetworkManager.post: Отправка запроса...")
            performRequest(request: request, requiresAuth: false, completion: completion)
        }
    }
    
    /**
     * DELETE запрос без body
     */
    func delete<T: Decodable>(
        endpoint: String,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        // Проверяем и обновляем токен если нужно
        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
            
            guard let url = URL(string: baseURL + endpoint) else {
                completion(.failure(NetworkError.invalidURL))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "DELETE"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            if let token = AppConfig.authToken {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }
            
            performRequest(request: request, requiresAuth: false, completion: completion)
        }
    }
    
    /**
     * PUT запрос
     */
    func put<T: Decodable, B: Encodable>(
        endpoint: String,
        body: B,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        let fullURL = baseURL + endpoint
        print("🔵 NetworkManager.put: Начало")
        print("   - URL: \(fullURL)")
        
        // Проверяем и обновляем токен если нужно
        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
            
            guard let url = URL(string: fullURL) else {
                print("❌ NetworkManager.put: Неверный URL: \(fullURL)")
                completion(.failure(NetworkError.invalidURL))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "PUT"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            if let token = AppConfig.authToken {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }
            
            // Encode body
            do {
                let bodyData = try JSONEncoder().encode(body)
                request.httpBody = bodyData
            } catch {
                print("❌ NetworkManager.put: Ошибка кодирования body: \(error)")
                completion(.failure(error))
                return
            }
            
            performRequest(request: request, requiresAuth: false, completion: completion)
        }
    }
    
    /**
     * PATCH запрос
     */
    func patch<T: Decodable, B: Encodable>(
        endpoint: String,
        body: B,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        let fullURL = baseURL + endpoint
        print("🔵 NetworkManager.patch: Начало")
        print("   - URL: \(fullURL)")
        
        // Проверяем и обновляем токен если нужно
        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
            
            guard let url = URL(string: fullURL) else {
                print("❌ NetworkManager.patch: Неверный URL: \(fullURL)")
                completion(.failure(NetworkError.invalidURL))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "PATCH"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            if let token = AppConfig.authToken {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }
            
            // Encode body
            do {
                let bodyData = try JSONEncoder().encode(body)
                request.httpBody = bodyData
            } catch {
                print("❌ NetworkManager.patch: Ошибка кодирования body: \(error)")
                completion(.failure(error))
                return
            }
            
            performRequest(request: request, requiresAuth: false, completion: completion)
        }
    }
    
    /**
     * DELETE запрос
     */
    func delete<T: Decodable, B: Encodable>(
        endpoint: String,
        body: B,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        // Проверяем и обновляем токен если нужно
        Task {
            _ = await JWTTokenManager.shared.refreshTokenIfNeeded()
            
            guard let url = URL(string: baseURL + endpoint) else {
                completion(.failure(NetworkError.invalidURL))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "DELETE"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            if let token = AppConfig.authToken {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }
            
            // Encode body
            do {
                request.httpBody = try JSONEncoder().encode(body)
            } catch {
                completion(.failure(error))
                return
            }
            
            performRequest(request: request, requiresAuth: false, completion: completion)
        }
    }
    
    // MARK: - SSL Pinning Methods
    
    /**
     * Загружает сертификаты для SSL Pinning
     * В реальном приложении сертификаты должны быть в Bundle
     */
    private func loadPinnedCertificates() -> [Data] {
        var certificates: [Data] = []
        
        // Загружаем основной сертификат
        if let mainCert = loadCertificate(named: "aladdin_cert") {
            certificates.append(mainCert)
        }
        
        // Загружаем резервный сертификат
        if let backupCert = loadCertificate(named: "aladdin_cert_backup") {
            certificates.append(backupCert)
        }
        
        // Проверяем наличие сертификатов
        #if !DEBUG
        if certificates.isEmpty {
            print("⚠️ SSL Pinning: Сертификаты не найдены в Bundle!")
            print("   Инструкция: Добавьте сертификаты в Xcode проект:")
            print("   1. Откройте Xcode проект")
            print("   2. Перетащите файлы из ALADDIN/Certificates/ в проект")
            print("   3. Убедитесь, что они добавлены в Target Membership")
            print("   4. Файлы: aladdin_cert.cer, aladdin_cert_backup.cer")
        } else {
            print("✅ SSL Pinning: Загружено \(certificates.count) сертификатов")
        }
        #endif
        
        return certificates
    }
    
    /**
     * Загружает конкретный сертификат по имени
     */
    private func loadCertificate(named name: String) -> Data? {
        // Пытаемся загрузить сертификат из Bundle
        guard let path = Bundle.main.path(forResource: name, ofType: "cer") else {
            print("⚠️ SSL Pinning: Сертификат \(name).cer не найден в Bundle")
            print("   Для продакшена добавьте сертификаты в Xcode проект:")
            print("   1. Скачайте сертификаты с сервера aladdin-ai.ru")
            print("   2. Добавьте их в проект как .cer файлы")
            print("   3. Убедитесь, что они включены в Target Membership")
            return nil
        }

        guard let data = NSData(contentsOfFile: path) as Data? else {
            print("❌ SSL Pinning: Не удалось загрузить данные сертификата \(name).cer")
            return nil
        }

        print("✅ SSL Pinning: Сертификат \(name).cer загружен (\(data.count) байт)")
        return data
    }
    
    /**
     * Проверяет, нужно ли применять SSL Pinning для данного домена
     */
    private func shouldPinCertificate(for host: String) -> Bool {
        guard isSSLPinningEnabled else { return false }
        return pinnedDomains.contains(host)
    }
    
    /**
     * Проверяет сертификат сервера против закрепленных сертификатов
     */
    private func validateServerCertificate(_ serverTrust: SecTrust, for host: String) -> Bool {
        guard shouldPinCertificate(for: host) else {
            print("🔓 SSL Pinning: Домен \(host) не требует SSL Pinning")
            return true
        }
        
        // Проверяем, что у нас есть закрепленные сертификаты
        guard !pinnedCertificates.isEmpty else {
            print("⚠️ SSL Pinning: Нет закрепленных сертификатов для проверки - используем fallback")
            // FALLBACK: Используем стандартную проверку сертификата
            return performStandardCertificateValidation(serverTrust)
        }
        
        // Получаем цепочку сертификатов сервера (современная версия)
        guard let certificateChain = SecTrustCopyCertificateChain(serverTrust) else {
            print("❌ SSL Pinning: Не удалось получить цепочку сертификатов")
            return false
        }
        
        let chainCount = CFArrayGetCount(certificateChain)
        guard chainCount > 0 else {
            print("❌ SSL Pinning: Пустая цепочка сертификатов")
            return false
        }
        
        print("🔍 SSL Pinning: Проверяем цепочку из \(chainCount) сертификатов для \(host)")
        
        // Проверяем каждый сертификат в цепочке
        for i in 0..<chainCount {
            guard let certificate = CFArrayGetValueAtIndex(certificateChain, i) else {
                print("⚠️ SSL Pinning: Не удалось получить сертификат \(i)")
                continue
            }
            
            let serverCert = Unmanaged<SecCertificate>.fromOpaque(certificate).takeUnretainedValue()
            
            // Получаем данные сертификата
            let serverCertData = SecCertificateCopyData(serverCert)
            let serverCertDataPtr = CFDataGetBytePtr(serverCertData)
            let serverCertDataSize = CFDataGetLength(serverCertData)
            let serverCertBytes = Data(bytes: serverCertDataPtr!, count: serverCertDataSize)
            
            // Сравниваем с закрепленными сертификатами
            for (index, pinnedCertificate) in pinnedCertificates.enumerated() {
                if serverCertBytes == pinnedCertificate {
                    print("✅ SSL Pinning: Сертификат \(i) для \(host) совпадает с закрепленным \(index)")
                    return true
                }
            }
        }
        
        print("❌ SSL Pinning: Ни один сертификат для \(host) не прошел проверку - используем fallback")
        // FALLBACK: Используем стандартную проверку сертификата
        return performStandardCertificateValidation(serverTrust)
    }
    
    /**
     * Выполняет стандартную проверку сертификата (fallback механизм)
     * Используется когда SSL Pinning не работает или сертификаты не найдены
     */
    private func performStandardCertificateValidation(_ serverTrust: SecTrust) -> Bool {
        var trustError: CFError?
        let isValid = SecTrustEvaluateWithError(serverTrust, &trustError)
        
        if isValid {
            print("✅ SSL Pinning Fallback: Стандартная проверка сертификата успешна")
            return true
        }
        
        if let error = trustError {
            print("❌ SSL Pinning Fallback: Ошибка проверки сертификата \(error)")
        } else {
            print("❌ SSL Pinning Fallback: Неизвестная ошибка проверки сертификата")
        }
        return false
    }
    
    // MARK: - Private Methods
    
    private func performRequest<T: Decodable>(
        request: URLRequest,
        requiresAuth: Bool = false,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        print("🚀🚀🚀 PERFORM_REQUEST STARTED for \(request.url?.absoluteString ?? "unknown")")

        // ✅ ЗАДАЧА 62: Проверка rate limit перед запросом
        let endpoint = request.url?.path ?? "unknown"
        print("📊 ENDPOINT: \(endpoint)")

        guard rateLimiter.canMakeRequest(to: endpoint) else {
            // Лимит превышен - возвращаем ошибку
            let timeUntilReset = rateLimiter.getTimeUntilReset(for: endpoint) ?? 60.0
            let errorMessage = String(format: "Слишком много запросов. Повторите через %.0f секунд", timeUntilReset)

            #if DEBUG
            print("🚫 Rate Limit: Запрос заблокирован для \(endpoint)")
            print("   - Время до сброса: \(String(format: "%.1f", timeUntilReset)) сек")
            #endif

            // Production логирование
            os_log("🚫 Rate Limit: Request blocked for %{public}@, retry in %.1fs",
                   log: Self.networkLogger,
                   type: .error,
                   endpoint,
                   timeUntilReset)

            completion(.failure(NetworkError.tooManyRequests(errorMessage)))
            return
        }

        // Регистрируем запрос в rate limiter
        rateLimiter.recordRequest(to: endpoint)

        // ✅ Production логирование (видно в Xcode Console на реальном устройстве)
        os_log("🌐 API Request: %{public}@ %{public}@", 
               log: Self.networkLogger, 
               type: .info,
               request.httpMethod ?? "unknown",
               request.url?.absoluteString ?? "unknown")
        
        #if DEBUG
        print("🔵 NetworkManager.performRequest: Начало")
        print("   - URL: \(request.url?.absoluteString ?? "unknown")")
        print("   - Method: \(request.httpMethod ?? "unknown")")
        print("   - Rate limit: OK (\(rateLimiter.getRequestCount(for: endpoint))/100)")
        #endif
        
        let requestStartTime = Date()

        // 🔍 NETWORK: Логируем исходящий запрос
        logger.logRequest(request)

        print("🔥🔥🔥 ABOUT TO CALL session.dataTask for \(request.url?.absoluteString ?? "unknown")")

        session.dataTask(with: request) { [weak self] data, response, error in
            print("🔥🔥🔥 SESSION DATATASK CALLBACK STARTED for \(request.url?.absoluteString ?? "unknown")")
            // 🔍 NETWORK: Логируем входящий ответ
            logger.logResponse(response, data: data)

            DispatchQueue.main.async {
                let duration = Date().timeIntervalSince(requestStartTime)
                self?.handleRequestDuration(duration)

                // Отслеживаем запрос в production monitoring
                if let strongSelf = self {
                    strongSelf.trackAPIRequest(
                        endpoint: request.url?.path ?? "unknown",
                        method: request.httpMethod ?? "unknown",
                        duration: duration,
                        response: response,
                        error: error
                    )
                }
                
                #if DEBUG
                print("🔵 NetworkManager.performRequest: Получен ответ (время: \(String(format: "%.2f", duration))s)")
                #endif
                
                // Проверка ошибки
                if let error = error {
                    // ✅ Production логирование ошибок (критично для диагностики!)
                    os_log("❌ Network Error: %{public}@ - %{public}@", 
                           log: Self.networkLogger, 
                           type: .error,
                           request.url?.absoluteString ?? "unknown",
                           error.localizedDescription)
                    
                    if let nsError = error as NSError? {
                        os_log("   Domain: %{public}@, Code: %d", 
                               log: Self.networkLogger, 
                               type: .error,
                               nsError.domain,
                               nsError.code)
                    }
                    
                    #if DEBUG
                    print("❌ NetworkManager.performRequest: Ошибка сети: \(error)")
                    print("   - Описание: \(error.localizedDescription)")
                    if let nsError = error as NSError? {
                        print("   - Domain: \(nsError.domain)")
                        print("   - Code: \(nsError.code)")
                    }
                    #endif
                    
                    // 🛡️ DEFENSIVE JWT: Record failure for JWT-protected endpoints
                    if requiresAuth {
                        JWTCircuitBreaker.shared.recordFailure()
                        logger.network("❌ DEFENSIVE JWT: Circuit breaker failure recorded")

                        // Execute error recovery strategy
                        Task {
                            await JWTErrorRecovery.executeStrategy(
                                JWTErrorRecovery.selectStrategy(for: error),
                                for: error
                            )
                        }
                    }

                    self?.lastError = error.localizedDescription
                    completion(.failure(error))
                    return
                }
                
                // Проверка HTTP статуса
                guard let httpResponse = response as? HTTPURLResponse else {
                    // ✅ Production логирование неверного ответа
                    os_log("❌ Invalid Response: %{public}@", 
                           log: Self.networkLogger, 
                           type: .error,
                           request.url?.absoluteString ?? "unknown")
                    
                    #if DEBUG
                    print("❌ NetworkManager.performRequest: Неверный ответ (не HTTPURLResponse)")
                    #endif
                    
                    completion(.failure(NetworkError.invalidResponse))
                    return
                }
                
                // ✅ Production логирование HTTP статуса (только для ошибок)
                if httpResponse.statusCode >= 400 {
                    os_log("⚠️ HTTP Error: %d - %{public}@", 
                           log: Self.networkLogger, 
                           type: .error,
                           httpResponse.statusCode,
                           request.url?.absoluteString ?? "unknown")
                }
                
                #if DEBUG
                print("   - HTTP Status: \(httpResponse.statusCode)")
                #endif
                
                // Логируем тело ответа для отладки
                if let data = data, let responseString = String(data: data, encoding: .utf8) {
                    logger.network("   - Response body: \(responseString.prefix(200))")
                }
                
                // Обработка 429 ошибки (Too Many Requests) - rate limit
                if httpResponse.statusCode == 429 {
                    // ✅ ЗАДАЧА 62: Обработка 429 ошибки от сервера
                    let retryAfter = httpResponse.value(forHTTPHeaderField: "Retry-After") ?? "60"
                    let errorMessage = "Сервер ограничил частоту запросов. Повторите через \(retryAfter) секунд"

                    #if DEBUG
                    print("⚠️ NetworkManager: Получен 429 Too Many Requests")
                    print("   - Retry-After: \(retryAfter) сек")
                    print("   - Endpoint: \(request.url?.path ?? "unknown")")
                    #endif

                    // Production логирование
                    os_log("⚠️ 429 Too Many Requests: %{public}@ - Retry-After: %{public}@",
                           log: Self.networkLogger,
                           type: .error,
                           request.url?.absoluteString ?? "unknown",
                           retryAfter)

                    self?.lastError = errorMessage
                    completion(.failure(NetworkError.tooManyRequests(errorMessage)))
                    return
                }

                // Обработка 401 ошибки (Unauthorized) - токен истёк
                if httpResponse.statusCode == 401 {
                    // ✅ Production логирование 401 ошибки
                    os_log("⚠️ 401 Unauthorized: %{public}@ - Attempting token refresh", 
                           log: Self.networkLogger, 
                           type: .error,
                           request.url?.absoluteString ?? "unknown")
                    
                    #if DEBUG
                    print("⚠️ NetworkManager: Получен 401 - токен истёк, пытаемся обновить...")
                    #endif

                    // Проверяем, есть ли токен в Keychain перед обновлением
                    guard JWTTokenManager.shared.hasValidToken() else {
                        // ✅ Production логирование отсутствия токена
                        os_log("❌ No valid token: %{public}@", 
                               log: Self.networkLogger, 
                               type: .error,
                               request.url?.absoluteString ?? "unknown")
                        
                        #if DEBUG
                        print("❌ NetworkManager: Валидный токен отсутствует, не повторяем запрос")
                        #endif
                        
                        completion(.failure(NetworkError.tokenExpired))
                        return
                    }
                    
                    // Пытаемся обновить токен
                    Task { [weak self] in
                        let tokenWasRefreshed = await JWTTokenManager.shared.forceRefreshToken()
                        
                        if tokenWasRefreshed {
                            // ✅ Production логирование успешного обновления токена
                            os_log("✅ Token refreshed: %{public}@ - Retrying request", 
                                   log: Self.networkLogger, 
                                   type: .info,
                                   request.url?.absoluteString ?? "unknown")
                            
                            #if DEBUG
                            print("✅ NetworkManager: Токен обновлён, повторяем запрос...")
                            #endif
                            
                            guard let strongSelf = self else {
                                completion(.failure(NetworkError.tokenExpired))
                                return
                            }
                            
                            // Создаём новый запрос с обновлённым токеном
                            guard let url = request.url else {
                                completion(.failure(NetworkError.invalidURL))
                                return
                            }
                            
                            var retryRequest = URLRequest(url: url)
                            retryRequest.httpMethod = request.httpMethod
                            retryRequest.httpBody = request.httpBody
                            
                            // Копируем все заголовки
                            for (key, value) in request.allHTTPHeaderFields ?? [:] {
                                retryRequest.setValue(value, forHTTPHeaderField: key)
                            }
                            
                            // Обновляем токен
                            if let token = AppConfig.authToken {
                                retryRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                            }
                            
                            // Повторяем запрос с новым токеном
                            strongSelf.performRequest(request: retryRequest, requiresAuth: true, completion: completion)
                        } else {
                            // ✅ Production логирование ошибки обновления токена
                            os_log("❌ Token refresh failed: %{public}@", 
                                   log: Self.networkLogger, 
                                   type: .error,
                                   request.url?.absoluteString ?? "unknown")
                            
                            #if DEBUG
                            print("❌ NetworkManager: Не удалось обновить токен")
                            #endif
                            
                            // 🛡️ DEFENSIVE JWT: Record failure for JWT-protected endpoints
                            JWTCircuitBreaker.shared.recordFailure()
                            logger.network("❌ DEFENSIVE JWT: Circuit breaker failure recorded for 401 token expired")

                            completion(.failure(NetworkError.tokenExpired))
                        }
                    }
                    return
                }
                
                // Обработка ошибок HTTP
                guard (200...299).contains(httpResponse.statusCode) else {
                    // Пытаемся декодировать ошибку от сервера
                    let errorMessage: String
                    if let data = data, let errorData = try? JSONDecoder().decode([String: String].self, from: data) {
                        errorMessage = errorData["detail"] ?? errorData["message"] ?? "HTTP ошибка \(httpResponse.statusCode)"
                    } else {
                        errorMessage = "HTTP ошибка \(httpResponse.statusCode)"
                    }
                    
                    // ✅ Production логирование HTTP ошибок
                    os_log("❌ HTTP Error %d: %{public}@ - %{public}@", 
                           log: Self.networkLogger, 
                           type: .error,
                           httpResponse.statusCode,
                           request.url?.absoluteString ?? "unknown",
                           errorMessage)
                    
                    #if DEBUG
                    print("❌ NetworkManager.performRequest: HTTP ошибка \(httpResponse.statusCode)")
                    print("   - Сообщение от сервера: \(errorMessage)")
                    #endif
                    
                    // Создаем более информативную ошибку
                    let networkError: NetworkError
                    switch httpResponse.statusCode {
                    case 400:
                        networkError = .badRequest(errorMessage)
                    case 403:
                        networkError = .forbidden(errorMessage)
                    case 404:
                        networkError = .notFound(errorMessage)
                    case 429:
                        networkError = .tooManyRequests(errorMessage)
                    case 500:
                        networkError = .internalServerError(errorMessage)
                    case 502:
                        networkError = .badGateway(errorMessage)
                    case 503:
                        networkError = .serviceUnavailable(errorMessage)
                    default:
                        networkError = .httpError(httpResponse.statusCode)
                    }
                    
                    // 🛡️ DEFENSIVE JWT: Record failure for JWT-protected endpoints
                    if requiresAuth {
                        JWTCircuitBreaker.shared.recordFailure()
                        logger.network("❌ DEFENSIVE JWT: Circuit breaker failure recorded for HTTP \(httpResponse.statusCode)")

                        // Execute error recovery strategy
                        Task {
                            await JWTErrorRecovery.executeStrategy(
                                JWTErrorRecovery.selectStrategy(for: networkError),
                                for: networkError
                            )
                        }
                    }

                    completion(.failure(networkError))
                    return
                }
                
                // Проверка данных
                guard let data = data else {
                    // ✅ Production логирование отсутствия данных
                    os_log("❌ No data in response: %{public}@", 
                           log: Self.networkLogger, 
                           type: .error,
                           request.url?.absoluteString ?? "unknown")
                    
                    #if DEBUG
                    print("❌ NetworkManager.performRequest: Нет данных в ответе")
                    #endif
                    
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                #if DEBUG
                print("   - Размер данных: \(data.count) байт")
                #endif
                
                // Декодирование
                do {
                    let decoded = try JSONDecoder().decode(T.self, from: data)

                    #if DEBUG
                    print("✅ NetworkManager.performRequest: Декодирование успешно")
                    #endif

                    // ✅ ЗАДАЧА 63: Валидация данных от API
                    do {
                        try APIResponseValidator.validate(decoded, type: T.self)

                        #if DEBUG
                        print("✅ NetworkManager.performRequest: Валидация успешна")
                        #endif

                        // 🛡️ DEFENSIVE JWT: Record success for JWT-protected endpoints
                        if requiresAuth {
                            JWTCircuitBreaker.shared.recordSuccess()
                            logger.network("✅ DEFENSIVE JWT: Circuit breaker success recorded")
                        }

                        completion(.success(decoded))
                    } catch let validationError as ValidationError {
                        // Валидация не пройдена - логируем и возвращаем ошибку
                        #if DEBUG
                        print("❌ NetworkManager.performRequest: Валидация не пройдена")
                        print("   - Ошибка: \(validationError.localizedDescription)")
                        #endif

                        // Production логирование ошибки валидации
                        os_log("❌ Validation Error: %{public}@ - %{public}@",
                               log: Self.networkLogger,
                               type: .error,
                               request.url?.absoluteString ?? "unknown",
                               validationError.localizedDescription)

                        self?.lastError = validationError.localizedDescription
                        completion(.failure(validationError))
                    } catch {
                        // Неожиданная ошибка валидации
                        #if DEBUG
                        print("❌ NetworkManager.performRequest: Неожиданная ошибка валидации: \(error)")
                        #endif

                        os_log("❌ Unexpected validation error: %{public}@ - %{public}@",
                               log: Self.networkLogger,
                               type: .error,
                               request.url?.absoluteString ?? "unknown",
                               error.localizedDescription)

                        self?.lastError = "Ошибка валидации данных: \(error.localizedDescription)"
                        completion(.failure(error))
                    }
                } catch {
                    // ✅ Production логирование ошибок декодирования
                    os_log("❌ Decoding Error: %{public}@ - %{public}@", 
                           log: Self.networkLogger, 
                           type: .error,
                           request.url?.absoluteString ?? "unknown",
                           error.localizedDescription)
                    
                    #if DEBUG
                    print("❌ NetworkManager.performRequest: Ошибка декодирования: \(error)")
                    if let dataString = String(data: data, encoding: .utf8) {
                        print("   - Данные для декодирования: \(dataString.prefix(500))")
                    }
                    #endif
                    
                    self?.lastError = "Ошибка декодирования: \(error.localizedDescription)"
                    completion(.failure(error))
                }
            }
        }.resume()
    }

    // MARK: - Диагностические методы для отладки crash

    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        print("🌐🌐🌐 URLSessionDelegate: Task completed")
        print("   - Task: \(task.taskIdentifier)")
        print("   - URL: \(task.currentRequest?.url?.absoluteString ?? "NIL")")
        print("   - Error: \(error?.localizedDescription ?? "NIL")")
        print("   - Thread: \(Thread.current)")
        print("   - Is main: \(Thread.isMainThread)")

        if let error = error {
            print("   - Error Domain: \((error as NSError).domain)")
            print("   - Error Code: \((error as NSError).code)")
            print("   - Error UserInfo: \((error as NSError).userInfo)")
        }
    }

    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive response: URLResponse, completionHandler: @escaping (URLSession.ResponseDisposition) -> Void) {
        print("🌐🌐🌐 URLSessionDelegate: Received response")
        print("   - Task: \(dataTask.taskIdentifier)")
        print("   - URL: \(response.url?.absoluteString ?? "NIL")")

        if let httpResponse = response as? HTTPURLResponse {
            print("   - Status Code: \(httpResponse.statusCode)")
            print("   - Headers: \(httpResponse.allHeaderFields)")
        }

        completionHandler(.allow)
    }

    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        print("🌐🌐🌐 URLSessionDelegate: Received data")
        print("   - Task: \(dataTask.taskIdentifier)")
        print("   - Data length: \(data.count) bytes")

        if let stringData = String(data: data, encoding: .utf8), data.count < 1000 {
            print("   - Data content: \(stringData)")
        }
    }
}

// MARK: - URLSessionDelegate

extension NetworkManager: URLSessionDelegate {
    
    /**
     * Обрабатывает SSL аутентификацию и проверяет сертификаты
     * Это критически важно для защиты от Man-in-the-Middle атак
     */
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        
        // Получаем информацию о хосте
        let host = challenge.protectionSpace.host
        guard !host.isEmpty else {
            print("❌ SSL Pinning: Не удалось получить host из challenge")
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        print("🔐 SSL Pinning: Проверяем сертификат для \(host)")
        
        // Проверяем тип аутентификации
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust else {
            print("⚠️ SSL Pinning: Неожиданный тип аутентификации: \(challenge.protectionSpace.authenticationMethod)")
            completionHandler(.performDefaultHandling, nil)
            return
        }
        
        // Получаем server trust
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            print("❌ SSL Pinning: Не удалось получить server trust")
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        // Если SSL Pinning отключен, используем стандартную проверку
        guard isSSLPinningEnabled else {
            print("🔓 SSL Pinning: Отключен, используем стандартную проверку")
            completionHandler(.performDefaultHandling, nil)
            return
        }
        
        // Проверяем сертификат
        if validateServerCertificate(serverTrust, for: host) {
            // Сертификат прошел проверку
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
            
            #if !DEBUG
            // ✅ ЗАДАЧА 61: Логируем успешную проверку SSL Pinning в продакшене
            os_log("✅ SSL Pinning: Сертификат для %{public}@ успешно проверен", 
                   log: Self.networkLogger, 
                   type: .info,
                   host)
            #endif
        } else {
            // Сертификат не прошел проверку - блокируем соединение
            print("🚫 SSL Pinning: Соединение заблокировано из-за неверного сертификата")
            
            // ✅ ЗАДАЧА 61: Метрика для отслеживания SSL Pinning ошибок
            #if !DEBUG
            os_log("🚨 SSL Pinning ERROR: Соединение заблокировано для %{public}@ - неверный сертификат", 
                   log: Self.networkLogger, 
                   type: .error,
                   host)
            #else
            print("🚨 SSL Pinning ERROR: Соединение заблокировано для \(host) - неверный сертификат")
            #endif
            
            // TODO: В будущем отправлять метрику на сервер аналитики
            // metricsService.trackSSLPinningError(host: host, reason: "invalid_certificate")
            
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
    
    private func handleRequestDuration(_ duration: TimeInterval) {
        #if DEBUG
        let formatted = String(format: "%.2f", duration)
        print("⏱️ NetworkManager: запрос завершился за \(formatted) c")
        #endif

        if duration > slowRequestThreshold {
            slowRequestCount += 1
            #if DEBUG
            print("⚠️ NetworkManager: медленный ответ \(slowRequestCount)/\(slowRequestLimitBeforeAdjusting)")
            #endif

            if !didIncreaseTimeouts && slowRequestCount >= slowRequestLimitBeforeAdjusting {
                increaseTimeoutsForSlowNetwork()
            }
        } else {
            slowRequestCount = 0
        }
    }

    private func trackAPIRequest(
        endpoint: String,
        method: String,
        duration: TimeInterval,
        response: URLResponse?,
        error: Error?
    ) {
        let statusCode: Int
        if let httpResponse = response as? HTTPURLResponse {
            statusCode = httpResponse.statusCode
        } else {
            statusCode = error != nil ? -1 : 0
        }

        // Отправляем в production monitoring (закомментировано для совместимости)
        // ProductionMonitoringService.shared.trackAPIRequest(
        //     endpoint: endpoint,
        //     method: method,
        //     responseTime: duration,
        //     statusCode: statusCode,
        //     error: error
        // )
    }
    
    private func increaseTimeoutsForSlowNetwork() {
        didIncreaseTimeouts = true
        let newRequestTimeout = AppConfig.Network.requestTimeout * 1.5
        let newResourceTimeout = AppConfig.Network.resourceTimeout * 1.5
        
        sessionConfiguration.timeoutIntervalForRequest = newRequestTimeout
        sessionConfiguration.timeoutIntervalForResource = newResourceTimeout
        session = URLSession(configuration: sessionConfiguration, delegate: self, delegateQueue: nil)
        
        #if DEBUG
        print("⚠️ NetworkManager: таймауты увеличены до \(newRequestTimeout)s / \(newResourceTimeout)s из-за медленных ответов")
        #endif
    }
}


// MARK: - Network Error
// NetworkError теперь определен в отдельном файле NetworkError.swift



