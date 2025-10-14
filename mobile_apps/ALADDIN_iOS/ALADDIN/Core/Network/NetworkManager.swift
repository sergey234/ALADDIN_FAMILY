import Foundation
import Combine

/**
 * 🌐 Network Manager
 * API клиент для подключения к Python backend
 * Управляет всеми HTTP запросами
 */

class NetworkManager: ObservableObject {
    
    // MARK: - Properties
    
    @Published var isOnline: Bool = true
    @Published var lastError: String?
    
    private let baseURL: String
    private let session: URLSession
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Init
    
    init(baseURL: String = AppConfig.apiBaseURL) {
        self.baseURL = baseURL
        
        // Конфигурация сессии
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 60
        configuration.waitsForConnectivity = true
        
        self.session = URLSession(configuration: configuration)
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

// MARK: - Network Error

enum NetworkError: LocalizedError {
    case invalidURL
    case invalidResponse
    case noData
    case httpError(Int)
    
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
        }
    }
}




