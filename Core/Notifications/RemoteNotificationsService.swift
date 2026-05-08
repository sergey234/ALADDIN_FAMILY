import Foundation

/// Ошибки удалённого сервиса уведомлений
enum NotificationsAPIError: Error {
    case invalidURL
    case invalidResponse
    case badStatus(Int)
    case decoding(Error)
    case encoding(Error)
    case transport(URLError)
    case contractViolation(String)
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
    private struct MarkReadResponse: Decodable {
        let success: Bool
        let unreadCount: Int
    }

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

        let envelope: NotificationsEnvelope = try await performGET(
            path: AppConfig.Endpoint.notifications,
            queryItems: query
        )
        try validateNotificationsEnvelope(envelope)
        return envelope
    }

    func markNotificationAsRead(_ notificationId: String) async throws -> Int {
        struct Payload: Encodable {
            let notificationId: String
        }

        let response: MarkReadResponse = try await performPOST(
            path: AppConfig.Endpoint.markRead,
            body: Payload(notificationId: notificationId)
        )
        try validateMarkReadResponse(response, notificationId: notificationId)

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

    // MARK: - Contract validation

    private func validateNotificationsEnvelope(_ envelope: NotificationsEnvelope) throws {
        guard envelope.unreadCount >= 0 else {
            reportContractViolation("unreadCount must be >= 0")
            throw NotificationsAPIError.contractViolation("unreadCount must be >= 0")
        }

        let securityTypes: Set<String> = [
            "threat",
            "security_alert",
            "threat_detected",
            "phishing_blocked",
            "bypass",
            "bypass_attempt",
            "attempt_bypass"
        ]

        var unreadFromPayload = 0
        for notification in envelope.notifications {
            let trimmedId = notification.id.trimmingCharacters(in: .whitespacesAndNewlines)
            let trimmedTitle = notification.title.trimmingCharacters(in: .whitespacesAndNewlines)
            let trimmedMessage = notification.message.trimmingCharacters(in: .whitespacesAndNewlines)
            let trimmedType = notification.type.trimmingCharacters(in: .whitespacesAndNewlines)
            let loweredType = trimmedType.lowercased()

            guard !trimmedId.isEmpty else {
                reportContractViolation("notification.id is empty")
                throw NotificationsAPIError.contractViolation("notification.id is empty")
            }
            guard !trimmedTitle.isEmpty else {
                reportContractViolation("notification.title is empty for id=\(trimmedId)")
                throw NotificationsAPIError.contractViolation("notification.title is empty for id=\(trimmedId)")
            }
            guard !trimmedMessage.isEmpty else {
                reportContractViolation("notification.message is empty for id=\(trimmedId)")
                throw NotificationsAPIError.contractViolation("notification.message is empty for id=\(trimmedId)")
            }
            guard !trimmedType.isEmpty else {
                reportContractViolation("notification.type is empty for id=\(trimmedId)")
                throw NotificationsAPIError.contractViolation("notification.type is empty for id=\(trimmedId)")
            }
            if isExplicitMockSource(notification) {
                reportContractViolation("security notifications cannot come from mock/fallback source")
                throw NotificationsAPIError.contractViolation("security notifications cannot come from mock/fallback source")
            }

            if securityTypes.contains(loweredType) {
                let correlation = notification.resolvedCorrelationId.trimmingCharacters(in: .whitespacesAndNewlines)
                guard !correlation.isEmpty else {
                    reportContractViolation("security notification missing correlation_id for id=\(trimmedId)")
                    throw NotificationsAPIError.contractViolation("security notification missing correlation_id for id=\(trimmedId)")
                }
            }

            if !notification.isRead {
                unreadFromPayload += 1
            }
        }

        if unreadFromPayload > envelope.unreadCount {
            reportContractViolation("unreadCount mismatch: payload has \(unreadFromPayload), server returned \(envelope.unreadCount)")
            throw NotificationsAPIError.contractViolation(
                "unreadCount mismatch: payload has \(unreadFromPayload), server returned \(envelope.unreadCount)"
            )
        }
    }

    private func isExplicitMockSource(_ notification: NotificationResponse) -> Bool {
        let source = notification.metadata?["source"]?.lowercased()
        let eventSource = notification.metadata?["event_source"]?.lowercased()
        let value = source ?? eventSource ?? ""
        guard !value.isEmpty else { return false }
        return value.contains("mock") || value.contains("fallback") || value.contains("sfm_")
    }

    private func validateMarkReadResponse(
        _ response: MarkReadResponse,
        notificationId: String
    ) throws {
        // This endpoint must explicitly confirm success.
        // unreadCount may be zero, but never negative.
        guard response.success else {
            reportContractViolation("markRead returned success=false for notificationId=\(notificationId)")
            throw NotificationsAPIError.contractViolation("markRead returned success=false for notificationId=\(notificationId)")
        }
        guard response.unreadCount >= 0 else {
            reportContractViolation("markRead returned negative unreadCount")
            throw NotificationsAPIError.contractViolation("markRead returned negative unreadCount")
        }
    }

    private func reportContractViolation(_ message: String) {
        Task { @MainActor in
            MetricsService.shared.trackUserAction(
                action: "security_notifications_anomaly",
                parameters: [
                    "anomaly_code": "notifications_contract_violation",
                    "message": message,
                    "severity": "critical"
                ]
            )
        }
    }
}

