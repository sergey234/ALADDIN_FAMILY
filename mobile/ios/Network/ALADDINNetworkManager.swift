import Foundation
import Alamofire
import Network

class ALADDINNetworkManager {
    static let shared = ALADDINNetworkManager()
    
    private let session: Session
    private let certificatePinningManager = CertificatePinningManager.shared
    
    private init() {
        // Настройка Trust Evaluators для каждого хоста
        let evaluators: [String: ServerTrustEvaluating] = [
            "api.aladdin.security": certificatePinningManager.createTrustEvaluator(),
            "ai.aladdin.security": certificatePinningManager.createTrustEvaluator(),
            "vpn.aladdin.security": certificatePinningManager.createTrustEvaluator(),
            "auth.aladdin.security": certificatePinningManager.createTrustEvaluator()
        ]
        
        let serverTrustManager = ServerTrustManager(evaluators: evaluators)
        
        // Настройка сессии с pinning
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 60
        
        self.session = Session(
            configuration: configuration,
            serverTrustManager: serverTrustManager
        )
    }
    
    // MARK: - API Methods
    
    // Безопасный запрос с pinning
    func secureRequest<T: Codable>(
        _ endpoint: String,
        method: HTTPMethod = .get,
        parameters: Parameters? = nil,
        headers: HTTPHeaders? = nil,
        responseType: T.Type,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        let url = buildURL(for: endpoint)
        
        session.request(
            url,
            method: method,
            parameters: parameters,
            headers: headers
        )
        .validate()
        .responseData { response in
            switch response.result {
            case .success(let data):
                do {
                    let decodedResponse = try JSONDecoder().decode(T.self, from: data)
                    completion(.success(decodedResponse))
                } catch {
                    completion(.failure(ALADDINError.networkError(.invalidResponse)))
                }
            case .failure(let error):
                completion(.failure(ALADDINError.networkError(.serverError(response.response?.statusCode ?? 500))))
            }
        }
    }
    
    // Загрузка данных с проверкой сертификата
    func downloadData(from url: String, completion: @escaping (Result<Data, Error>) -> Void) {
        guard let requestURL = URL(string: url) else {
            completion(.failure(ALADDINError.networkError(.invalidResponse)))
            return
        }
        
        session.request(requestURL)
            .validate()
            .responseData { response in
                switch response.result {
                case .success(let data):
                    completion(.success(data))
                case .failure(let error):
                    completion(.failure(ALADDINError.networkError(.serverError(response.response?.statusCode ?? 500))))
                }
            }
    }
    
    // MARK: - Security Methods
    
    // Проверка статуса pinning
    func getPinningStatus() -> [String: Bool] {
        return certificatePinningManager.getPinningStatus()
    }
    
    // Обновление сертификатов
    func updateCertificates() {
        certificatePinningManager.updateCertificates()
    }
    
    // MARK: - Private Methods
    
    private func buildURL(for endpoint: String) -> String {
        let baseURL = "https://api.aladdin.security"
        return "\(baseURL)/\(endpoint)"
    }
}

// MARK: - Network Monitoring
extension ALADDINNetworkManager {
    
    // Мониторинг сетевого соединения
    func startNetworkMonitoring() {
        let monitor = NWPathMonitor()
        let queue = DispatchQueue(label: "NetworkMonitor")
        
        monitor.pathUpdateHandler = { path in
            if path.status == .satisfied {
                print("✅ Network connection available")
            } else {
                print("❌ Network connection lost")
            }
        }
        
        monitor.start(queue: queue)
    }
}

// MARK: - Error Types
enum ALADDINError: Error, LocalizedError {
    case networkError(NetworkError)
    case securityError(SecurityError)
    
    var errorDescription: String? {
        switch self {
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .securityError(let error):
            return "Security error: \(error.localizedDescription)"
        }
    }
}

enum NetworkError: Error {
    case noConnection
    case timeout
    case serverError(Int)
    case invalidResponse
    case rateLimited
    
    var localizedDescription: String {
        switch self {
        case .noConnection:
            return "No internet connection"
        case .timeout:
            return "Request timeout"
        case .serverError(let code):
            return "Server error: \(code)"
        case .invalidResponse:
            return "Invalid response format"
        case .rateLimited:
            return "Rate limit exceeded"
        }
    }
}

enum SecurityError: Error {
    case certificatePinningFailed
    case invalidCertificate
    case hostNotTrusted
    
    var localizedDescription: String {
        switch self {
        case .certificatePinningFailed:
            return "Certificate pinning failed"
        case .invalidCertificate:
            return "Invalid certificate"
        case .hostNotTrusted:
            return "Host not trusted"
        }
    }
}

