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
    private let isSSLPinningEnabled: Bool
    
    /// Домены для которых включен SSL Pinning
    private let pinnedDomains: Set<String>
    
    /// Сертификаты для проверки (в реальном приложении загружаются из Bundle)
    private var pinnedCertificates: [Data] = []
    
    // MARK: - Init
    
    init(baseURL: String = AppConfig.apiBaseURL, enableSSLPinning: Bool = true) {
        self.baseURL = baseURL
        self.isSSLPinningEnabled = enableSSLPinning
        
        // Домены для SSL Pinning (в реальном приложении из конфигурации)
        self.pinnedDomains = Set([
            "api.aladdin.com",
            "api.example.com",
            "localhost"
        ])
        
        // Инициализируем пустой массив сертификатов
        self.pinnedCertificates = []
        
        // Конфигурация сессии
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = AppConfig.Network.requestTimeout
        configuration.timeoutIntervalForResource = AppConfig.Network.resourceTimeout
        configuration.waitsForConnectivity = AppConfig.Network.waitsForConnectivity
        
        // Создаем временную сессию без делегата
        self.session = URLSession(configuration: configuration)
        
        super.init()
        
        // Загружаем сертификаты после инициализации
        self.pinnedCertificates = loadPinnedCertificates()
        
        // Создаем новую сессию с делегатом для SSL Pinning
        self.session = URLSession(configuration: configuration, delegate: self, delegateQueue: nil)
    }
    
    // MARK: - API Methods
    
    /**
     * GET запрос
     */
    func get<T: Decodable>(
        endpoint: String,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
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
    
    /**
     * POST запрос
     */
    func post<T: Decodable, B: Encodable>(
        endpoint: String,
        body: B,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
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
    
    // MARK: - SSL Pinning Methods
    
    /**
     * Загружает сертификаты для SSL Pinning
     * В реальном приложении сертификаты должны быть в Bundle
     */
    private func loadPinnedCertificates() -> [Data] {
        var certificates: [Data] = []
        
        // В реальном приложении загружаем сертификаты из Bundle
        // Пока создаем тестовые сертификаты для демонстрации
        if let certificatePath = Bundle.main.path(forResource: "aladdin_cert", ofType: "cer") {
            if let certificateData = NSData(contentsOfFile: certificatePath) as Data? {
                certificates.append(certificateData)
            }
        }
        
        // Fallback: создаем тестовый сертификат для разработки
        if certificates.isEmpty {
            print("⚠️ SSL Pinning: Сертификаты не найдены, используем тестовый режим")
            // В реальном приложении здесь должно быть исключение или отключение SSL Pinning
        }
        
        return certificates
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
        
        // Получаем сертификат сервера
        guard let serverCertificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            print("❌ SSL Pinning: Не удалось получить сертификат сервера")
            return false
        }
        
        // Получаем данные сертификата сервера
        let serverCertificateDataRef = SecCertificateCopyData(serverCertificate)
        let serverCertificateDataBytes = CFDataGetBytePtr(serverCertificateDataRef)
        let serverCertificateDataSize = CFDataGetLength(serverCertificateDataRef)
        
        let serverCertificateData = Data(bytes: serverCertificateDataBytes!, count: serverCertificateDataSize)
        
        // Сравниваем с закрепленными сертификатами
        for pinnedCertificate in pinnedCertificates {
            if serverCertificateData == pinnedCertificate {
                print("✅ SSL Pinning: Сертификат для \(host) прошел проверку")
                return true
            }
        }
        
        print("❌ SSL Pinning: Сертификат для \(host) не прошел проверку")
        return false
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

enum NetworkError: LocalizedError {
    case invalidURL
    case invalidResponse
    case noData
    case httpError(Int)
    case sslPinningFailed
    case certificateValidationFailed
    case untrustedCertificate
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Неверный URL"
        case .invalidResponse:
            return "Неверный ответ сервера"
        case .noData:
            return "Нет данных от сервера"
        case .httpError(let code):
            return "HTTP ошибка: \(code)"
        case .sslPinningFailed:
            return "SSL Pinning не удался - возможна атака Man-in-the-Middle"
        case .certificateValidationFailed:
            return "Проверка сертификата не удалась"
        case .untrustedCertificate:
            return "Недоверенный сертификат сервера"
        }
    }
}



