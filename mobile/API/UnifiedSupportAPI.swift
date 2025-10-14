//
//  UnifiedSupportAPI.swift
//  ALADDIN Mobile
//
//  Unified Support API - Единый API для всех типов поддержки
//  Объединяет: Super AI Support Assistant + Psychological Support + Technical Support
//
//  Created by ALADDIN Security Team
//  Version: 2.1
//  Date: 2025-01-27
//

import Foundation
import Combine

// MARK: - Data Models
public struct SupportRequest: Codable {
    public let message: String
    public let category: SupportCategory
    public let priority: SupportPriority
    public let context: SupportContext
    
    public init(message: String, category: SupportCategory, priority: SupportPriority, context: SupportContext) {
        self.message = message
        self.category = category
        self.priority = priority
        self.context = context
    }
}

public struct SupportResponse: Codable {
    public let message: String
    public let category: SupportCategory
    public let priority: SupportPriority
    public let suggestions: [String]
    public let timestamp: Date
    public let responseTime: TimeInterval
    public let isResolved: Bool
    public let nextSteps: [String]?
    
    public init(message: String, category: SupportCategory, priority: SupportPriority, suggestions: [String], timestamp: Date, responseTime: TimeInterval, isResolved: Bool = false, nextSteps: [String]? = nil) {
        self.message = message
        self.category = category
        self.priority = priority
        self.suggestions = suggestions
        self.timestamp = timestamp
        self.responseTime = responseTime
        self.isResolved = isResolved
        self.nextSteps = nextSteps
    }
}

public struct SupportContext: Codable {
    public let userID: String
    public let deviceInfo: String
    public let appVersion: String
    public let language: String
    public let timezone: String
    public let location: String?
    public let previousTickets: [String]?
    
    public init(userID: String, deviceInfo: String, appVersion: String, language: String = "ru", timezone: String = "Europe/Moscow", location: String? = nil, previousTickets: [String]? = nil) {
        self.userID = userID
        self.deviceInfo = deviceInfo
        self.appVersion = appVersion
        self.language = language
        self.timezone = timezone
        self.location = location
        self.previousTickets = previousTickets
    }
}

public struct SupportTicket: Codable, Identifiable {
    public let id: String
    public let title: String
    public let status: TicketStatus
    public let category: SupportCategory
    public let priority: SupportPriority
    public let createdAt: Date
    public let lastMessage: String
    public let assignedAgent: String?
    public let resolutionTime: TimeInterval?
    
    public init(id: String, title: String, status: TicketStatus, category: SupportCategory, priority: SupportPriority, createdAt: Date, lastMessage: String, assignedAgent: String? = nil, resolutionTime: TimeInterval? = nil) {
        self.id = id
        self.title = title
        self.status = status
        self.category = category
        self.priority = priority
        self.createdAt = createdAt
        self.lastMessage = lastMessage
        self.assignedAgent = assignedAgent
        self.resolutionTime = resolutionTime
    }
}

public struct SupportMessage: Codable, Identifiable {
    public let id: String
    public let text: String
    public let isFromUser: Bool
    public let timestamp: Date
    public let category: SupportCategory
    public let attachments: [String]?
    
    public init(id: String, text: String, isFromUser: Bool, timestamp: Date, category: SupportCategory, attachments: [String]? = nil) {
        self.id = id
        self.text = text
        self.isFromUser = isFromUser
        self.timestamp = timestamp
        self.category = category
        self.attachments = attachments
    }
}

// MARK: - Status Enums
public enum TicketStatus: String, CaseIterable, Codable {
    case open = "open"
    case inProgress = "in_progress"
    case resolved = "resolved"
    case closed = "closed"
    case escalated = "escalated"
    
    public var displayName: String {
        switch self {
        case .open:
            return "Открыт"
        case .inProgress:
            return "В работе"
        case .resolved:
            return "Решен"
        case .closed:
            return "Закрыт"
        case .escalated:
            return "Эскалирован"
        }
    }
}

public enum SupportStatus: String, CaseIterable, Codable {
    case online = "online"
    case busy = "busy"
    case offline = "offline"
    case maintenance = "maintenance"
    
    public var displayName: String {
        switch self {
        case .online:
            return "Онлайн"
        case .busy:
            return "Занят"
        case .offline:
            return "Офлайн"
        case .maintenance:
            return "Техническое обслуживание"
        }
    }
}

// MARK: - API Client
public class UnifiedSupportAPIManager: ObservableObject {
    private let baseURL: String
    private let session: URLSession
    private var cancellables = Set<AnyCancellable>()
    
    @Published public var isConnected = false
    @Published public var currentStatus: SupportStatus = .offline
    @Published public var recentTickets: [SupportTicket] = []
    
    public init(baseURL: String = "https://api.aladdin-security.com") {
        self.baseURL = baseURL
        self.session = URLSession.shared
    }
    
    // MARK: - API Methods
    public func sendSupportRequest(_ request: SupportRequest) -> AnyPublisher<SupportResponse, Error> {
        let url = URL(string: "\(baseURL)/api/v2/support/request")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: error).eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: SupportResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    public func getRecentTickets() -> AnyPublisher<[SupportTicket], Error> {
        let url = URL(string: "\(baseURL)/api/v2/support/tickets")!
        var urlRequest = URLRequest(url: url)
        urlRequest.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: [SupportTicket].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    public func getSupportStatus() -> AnyPublisher<SupportStatus, Error> {
        let url = URL(string: "\(baseURL)/api/v2/support/status")!
        var urlRequest = URLRequest(url: url)
        urlRequest.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: SupportStatus.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    public func sendCrisisRequest(_ crisisType: CrisisType, message: String, userID: String) -> AnyPublisher<SupportResponse, Error> {
        let request = SupportRequest(
            message: message,
            category: .crisis,
            priority: .critical,
            context: SupportContext(userID: userID, deviceInfo: "iOS Crisis", appVersion: "1.0.0")
        )
        
        return sendSupportRequest(request)
    }
    
    public func sendTechnicalTicket(_ issueType: String, description: String, userID: String, deviceInfo: String) -> AnyPublisher<SupportTicket, Error> {
        let url = URL(string: "\(baseURL)/api/v2/support/technical")!
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        
        let ticketData = [
            "issue_type": issueType,
            "description": description,
            "user_id": userID,
            "device_info": deviceInfo
        ]
        
        do {
            urlRequest.httpBody = try JSONSerialization.data(withJSONObject: ticketData)
        } catch {
            return Fail(error: error).eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: SupportTicket.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    public func getFAQ(category: SupportCategory) -> AnyPublisher<[String], Error> {
        let url = URL(string: "\(baseURL)/api/v2/support/faq/\(category.rawValue)")!
        var urlRequest = URLRequest(url: url)
        urlRequest.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: [String].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    public func getSupportMetrics() -> AnyPublisher<[String: Any], Error> {
        let url = URL(string: "\(baseURL)/api/v2/support/metrics")!
        var urlRequest = URLRequest(url: url)
        urlRequest.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .tryMap { data in
                guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                    throw URLError(.badServerResponse)
                }
                return json
            }
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - Helper Methods
    private func getAuthToken() -> String {
        // В реальном приложении здесь будет получение токена из Keychain
        return "mock_auth_token"
    }
    
    public func connect() {
        // Проверка подключения к API
        getSupportStatus()
            .sink(
                receiveCompletion: { completion in
                    if case .failure = completion {
                        self.isConnected = false
                        self.currentStatus = .offline
                    }
                },
                receiveValue: { status in
                    self.isConnected = true
                    self.currentStatus = status
                }
            )
            .store(in: &cancellables)
    }
    
    public func disconnect() {
        cancellables.removeAll()
        isConnected = false
        currentStatus = .offline
    }
}

// MARK: - Error Handling
public enum SupportAPIError: Error, LocalizedError {
    case networkError(Error)
    case decodingError(Error)
    case serverError(Int, String)
    case authenticationError
    case rateLimitExceeded
    case invalidRequest
    
    public var errorDescription: String? {
        switch self {
        case .networkError(let error):
            return "Ошибка сети: \(error.localizedDescription)"
        case .decodingError(let error):
            return "Ошибка декодирования: \(error.localizedDescription)"
        case .serverError(let code, let message):
            return "Ошибка сервера \(code): \(message)"
        case .authenticationError:
            return "Ошибка аутентификации"
        case .rateLimitExceeded:
            return "Превышен лимит запросов"
        case .invalidRequest:
            return "Неверный запрос"
        }
    }
}

// MARK: - Extensions
extension UnifiedSupportAPIManager {
    public func loadRecentTickets() {
        getRecentTickets()
            .sink(
                receiveCompletion: { _ in },
                receiveValue: { tickets in
                    self.recentTickets = tickets
                }
            )
            .store(in: &cancellables)
    }
    
    public func refreshStatus() {
        connect()
    }
}