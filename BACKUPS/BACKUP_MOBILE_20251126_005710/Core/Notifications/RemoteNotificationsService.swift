import Foundation

/// Ошибки удалённого сервиса уведомлений
enum NotificationsAPIError: Error {
    case invalidURL
    case invalidResponse
    case badStatus(Int)
    case decoding(Error)
    case encoding(Error)
    case transport(URLError)
}

/// DTO ответа `/notifications`
struct NotificationsEnvelope: Decodable {
    let notifications: [NotificationResponse]
    let unreadCount: Int
}

protocol NotificationsService {
    func fetchNotifications(includeRead: Bool, limit: Int) async throws -> NotificationsEnvelope
    func markNotificationAsRead(_ notificationId: String) async throws -> Int
}

/// Реальный сервис уведомлений, обращающийся к Python backend
final class RemoteNotificationsService: NotificationsService {
    private let baseURL: URL
    private let authTokenProvider: () -> String?
    private let urlSession: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    init(
        baseURL: URL? = nil,
        authTokenProvider: @escaping () -> String? = { nil },
        urlSession: URLSession = .shared
    ) {
        self.baseURL = baseURL ?? RemoteNotificationsService.defaultBaseURL
        self.authTokenProvider = authTokenProvider
        self.urlSession = urlSession

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        self.decoder = decoder

        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        encoder.dateEncodingStrategy = .iso8601
        self.encoder = encoder
    }

    private static var defaultBaseURL: URL {
        guard let url = URL(string: AppConfig.baseURL) else {
            return URL(string: "https://api.aladdin.family/api")!
        }
        return url
    }

    func fetchNotifications(includeRead: Bool, limit: Int) async throws -> NotificationsEnvelope {
        let query: [URLQueryItem] = [
            URLQueryItem(name: "includeRead", value: includeRead ? "true" : "false"),
            URLQueryItem(name: "limit", value: "\(max(1, min(limit, 100)))")
        ]

        return try await performGET(
            path: AppConfig.Endpoint.notifications,
            queryItems: query
        )
    }

    func markNotificationAsRead(_ notificationId: String) async throws -> Int {
        struct Payload: Encodable {
            let notificationId: String
        }

        struct Response: Decodable {
            let success: Bool
            let unreadCount: Int
        }

        let response: Response = try await performPOST(
            path: AppConfig.Endpoint.markRead,
            body: Payload(notificationId: notificationId)
        )

        return response.unreadCount
    }

    // MARK: - Networking helpers

    private func performGET<T: Decodable>(
        path: String,
        queryItems: [URLQueryItem] = []
    ) async throws -> T {
        guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else {
            throw NotificationsAPIError.invalidURL
        }

        let normalizedPath = path.hasPrefix("/") ? path : "/" + path
        let basePath = components.path == "/" ? "" : components.path
        components.path = basePath + normalizedPath
        components.queryItems = queryItems.isEmpty ? nil : queryItems

        guard let url = components.url else {
            throw NotificationsAPIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        attachAuthIfNeeded(to: &request)

        return try await execute(request: request)
    }

    private func performPOST<T: Decodable, Body: Encodable>(
        path: String,
        body: Body
    ) async throws -> T {
        guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else {
            throw NotificationsAPIError.invalidURL
        }

        let normalizedPath = path.hasPrefix("/") ? path : "/" + path
        let basePath = components.path == "/" ? "" : components.path
        components.path = basePath + normalizedPath

        guard let url = components.url else {
            throw NotificationsAPIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        attachAuthIfNeeded(to: &request)

        do {
            request.httpBody = try encoder.encode(body)
        } catch {
            throw NotificationsAPIError.encoding(error)
        }

        return try await execute(request: request)
    }

    private func attachAuthIfNeeded(to request: inout URLRequest) {
        guard let token = authTokenProvider()?.trimmingCharacters(in: .whitespacesAndNewlines),
              !token.isEmpty else { return }
        request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    }

    private func execute<T: Decodable>(request: URLRequest) async throws -> T {
        do {
            let (data, response) = try await urlSession.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw NotificationsAPIError.invalidResponse
            }

            guard (200..<300).contains(httpResponse.statusCode) else {
                throw NotificationsAPIError.badStatus(httpResponse.statusCode)
            }

            do {
                return try decoder.decode(T.self, from: data)
            } catch {
                throw NotificationsAPIError.decoding(error)
            }
        } catch let error as URLError {
            throw NotificationsAPIError.transport(error)
        } catch {
            throw error
        }
    }
}

