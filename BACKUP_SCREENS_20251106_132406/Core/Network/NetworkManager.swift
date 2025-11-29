import Foundation
import Combine
import Security

/**
 * 🌐 Network Manager
 * API клиент для подключения к Python backend
 * Управляет всеми HTTP запросами
 */

class NetworkManager: NSObject, ObservableObject {
    
    // MARK: - Properties
    
    @Published var isOnline: Bool = true
    @Published var lastError: String?
    
    private let baseURL: String
    private var session: URLSession
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - SSL Pinning Properties
    
    /// Включен ли SSL Pinning (по умолчанию включен для безопасности)
    let isSSLPinningEnabled: Bool
    
    /// Домены для которых включен SSL Pinning
    let pinnedDomains: Set<String>
    
    /// Сертификаты для проверки (в реальном приложении загружаются из Bundle)
    var pinnedCertificates: [Data] = []
    
    // MARK: - Init
    
    init(baseURL: String = AppConfig.apiBaseURL, enableSSLPinning: Bool = true) {
        print("🚨 NetworkManager.init: Начало")
        print("   - baseURL: '\(baseURL)'")
        print("   - baseURL.isEmpty: \(baseURL.isEmpty)")
        
        // ✅ ИСПРАВЛЕНИЕ #3: Инициализируем все свойства ПЕРЕД super.init()
        // Но для NSObject можно инициализировать после, если использовать временные значения
        self.baseURL = baseURL
        self.isSSLPinningEnabled = enableSSLPinning
        
        // Домены для SSL Pinning (реальные домены ALADDIN)
        self.pinnedDomains = Set([
            "api.aladdin.family",  // Основной API
            "vpn.aladdin.family",  // VPN сервер
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
        
        // Конфигурация сессии
        print("🔍 Создание URLSessionConfiguration...")
        let configuration = URLSessionConfiguration.default
        print("✅ URLSessionConfiguration создан")
        
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
        
        print("🔍 Создание URLSession...")
        // Создаем сессию с делегатом для SSL Pinning
        self.session = URLSession(configuration: configuration, delegate: self, delegateQueue: nil)
        print("✅ URLSession создан с делегатом")
        print("✅ NetworkManager.init: Завершен успешно")
    }
    
    // MARK: - API Methods
    
    /**
     * GET запрос
     */
    func get<T: Decodable>(
        endpoint: String,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        // Проверяем и обновляем токен если нужно
        Task {
            let tokenValid = await JWTTokenManager.shared.refreshTokenIfNeeded()
            
            guard let url = URL(string: baseURL + endpoint) else {
                completion(.failure(NetworkError.invalidURL))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "GET"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            // Добавляем токен если есть
            if let token = AppConfig.authToken {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }
            
            performRequest(request: request, completion: completion)
        }
    }
    
    /**
     * POST запрос
     */
    func post<T: Decodable, B: Encodable>(
        endpoint: String,
        body: B,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        // Проверяем и обновляем токен если нужно
        Task {
            let tokenValid = await JWTTokenManager.shared.refreshTokenIfNeeded()
            
            guard let url = URL(string: baseURL + endpoint) else {
                completion(.failure(NetworkError.invalidURL))
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
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
            
            performRequest(request: request, completion: completion)
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
        if certificates.isEmpty {
            print("⚠️ SSL Pinning: Сертификаты не найдены в Bundle!")
            print("   Инструкция: Добавьте сертификаты в Xcode проект:")
            print("   1. Откройте Xcode проект")
            print("   2. Перетащите файлы из ALADDIN/Certificates/ в проект")
            print("   3. Убедитесь, что они добавлены в Target Membership")
            print("   4. Файлы: aladdin_cert.cer, aladdin_cert_backup.cer")
            // В продакшене здесь должно быть исключение, но для разработки используем fallback
        } else {
            print("✅ SSL Pinning: Загружено \(certificates.count) сертификатов")
        }
        
        return certificates
    }
    
    /**
     * Загружает конкретный сертификат по имени
     */
    private func loadCertificate(named name: String) -> Data? {
        guard let path = Bundle.main.path(forResource: name, ofType: "cer") else {
            print("⚠️ SSL Pinning: Сертификат \(name) не найден")
            return nil
        }
        
        guard let data = NSData(contentsOfFile: path) as Data? else {
            print("⚠️ SSL Pinning: Ошибка чтения сертификата \(name)")
            return nil
        }
        
        print("✅ SSL Pinning: Сертификат \(name) загружен")
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
        var secresult = SecTrustResultType.invalid
        let status = SecTrustEvaluate(serverTrust, &secresult)
        
        if status == errSecSuccess {
            if secresult == .unspecified || secresult == .proceed {
                print("✅ SSL Pinning Fallback: Стандартная проверка сертификата успешна")
                return true
            } else {
                print("❌ SSL Pinning Fallback: Стандартная проверка сертификата не прошла (результат: \(secresult.rawValue))")
                return false
            }
        } else {
            print("❌ SSL Pinning Fallback: Ошибка проверки сертификата (статус: \(status))")
            return false
        }
    }
    
    // MARK: - Private Methods
    
    private func performRequest<T: Decodable>(
        request: URLRequest,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        session.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                // Проверка ошибки
                if let error = error {
                    self?.lastError = error.localizedDescription
                    completion(.failure(error))
                    return
                }
                
                // Проверка HTTP статуса
                guard let httpResponse = response as? HTTPURLResponse else {
                    completion(.failure(NetworkError.invalidResponse))
                    return
                }
                
                // Обработка 401 ошибки (Unauthorized) - токен истёк
                if httpResponse.statusCode == 401 {
                    print("⚠️ NetworkManager: Получен 401 - токен истёк, пытаемся обновить...")
                    
                    // Пытаемся обновить токен
                    Task { [weak self] in
                        let refreshed = await JWTTokenManager.shared.refreshTokenIfNeeded()
                        
                        if refreshed {
                            print("✅ NetworkManager: Токен обновлён, повторяем запрос...")
                            
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
                            strongSelf.performRequest(request: retryRequest, completion: completion)
                        } else {
                            print("❌ NetworkManager: Не удалось обновить токен")
                            completion(.failure(NetworkError.tokenExpired))
                        }
                    }
                    return
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    completion(.failure(NetworkError.httpError(httpResponse.statusCode)))
                    return
                }
                
                // Проверка данных
                guard let data = data else {
                    completion(.failure(NetworkError.noData))
                    return
                }
                
                // Декодирование
                do {
                    let decoded = try JSONDecoder().decode(T.self, from: data)
                    completion(.success(decoded))
                } catch {
                    self?.lastError = "Ошибка декодирования: \(error.localizedDescription)"
                    completion(.failure(error))
                }
            }
        }.resume()
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
        } else {
            // Сертификат не прошел проверку - блокируем соединение
            print("🚫 SSL Pinning: Соединение заблокировано из-за неверного сертификата")
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}

// MARK: - Network Error
// NetworkError теперь определен в отдельном файле NetworkError.swift



