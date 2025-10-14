//
//  SupportAPI.swift
//  ALADDIN Mobile Security
//
//  Support API Integration for iOS
//  API client for Super AI Support Assistant and Psychological Support Agent
//
//  Created by ALADDIN Security Team
//  Date: 2025-01-27
//  Version: 1.0
//

import Foundation
import Combine

// MARK: - Support API Models
struct SupportRequest: Codable {
    let question: String
    let userId: String
    let context: SupportContext
    let category: SupportCategory?
    let language: String
    let timestamp: Date
    
    init(question: String, userId: String, context: SupportContext, category: SupportCategory? = nil, language: String = "ru") {
        self.question = question
        self.userId = userId
        self.context = context
        self.category = category
        self.language = language
        self.timestamp = Date()
    }
}

struct SupportContext: Codable {
    let currentScreen: String?
    let userAgeGroup: String?
    let emotionalState: String?
    let deviceInfo: DeviceInfo
    let sessionId: String
    
    init(currentScreen: String? = nil, userAgeGroup: String? = nil, emotionalState: String? = nil, deviceInfo: DeviceInfo, sessionId: String) {
        self.currentScreen = currentScreen
        self.userAgeGroup = userAgeGroup
        self.emotionalState = emotionalState
        self.deviceInfo = deviceInfo
        self.sessionId = sessionId
    }
}

struct DeviceInfo: Codable {
    let platform: String
    let version: String
    let model: String
    let screenSize: String
    let orientation: String
    
    init(platform: String = "iOS", version: String, model: String, screenSize: String, orientation: String = "portrait") {
        self.platform = platform
        self.version = version
        self.model = model
        self.screenSize = screenSize
        self.orientation = orientation
    }
}

struct SupportResponse: Codable {
    let answer: String
    let category: String
    let suggestedActions: [String]
    let relatedTopics: [String]
    let confidence: Double
    let responseTime: TimeInterval
    let timestamp: Date
    let sessionId: String
    let followUpQuestions: [String]?
    let emotionalAnalysis: EmotionalAnalysis?
    let priority: SupportPriority
}

struct EmotionalAnalysis: Codable {
    let emotion: String
    let confidence: Double
    let sentiment: String
    let recommendations: [String]
}

enum SupportCategory: String, CaseIterable, Codable {
    case cybersecurity = "cybersecurity"
    case familySupport = "family_support"
    case medicalSupport = "medical_support"
    case education = "education"
    case finance = "finance"
    case household = "household"
    case psychology = "psychology"
    case technology = "technology"
    case legal = "legal"
    case travel = "travel"
    case entertainment = "entertainment"
    case health = "health"
    case fitness = "fitness"
    case relationships = "relationships"
    case career = "career"
    case business = "business"
    case shopping = "shopping"
    case cooking = "cooking"
    case gardening = "gardening"
    case repair = "repair"
}

enum SupportPriority: String, CaseIterable, Codable {
    case low = "low"
    case medium = "medium"
    case high = "high"
    case urgent = "urgent"
}

// MARK: - Support API Client
class SupportAPIClient: ObservableObject {
    
    // MARK: - Properties
    private let baseURL: String
    private let session: URLSession
    private let apiKey: String
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    init(baseURL: String = "https://api.aladdin-security.com", apiKey: String) {
        self.baseURL = baseURL
        self.apiKey = apiKey
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        self.session = URLSession(configuration: config)
    }
    
    // MARK: - Public Methods
    
    /// Ask a question to the Super AI Support Assistant
    func askQuestion(_ request: SupportRequest) -> AnyPublisher<SupportResponse, Error> {
        let endpoint = "/api/v1/support/ask"
        return performRequest(endpoint: endpoint, method: "POST", body: request)
    }
    
    /// Get psychological support
    func getPsychologicalSupport(_ request: SupportRequest) -> AnyPublisher<SupportResponse, Error> {
        let endpoint = "/api/v1/support/psychological"
        return performRequest(endpoint: endpoint, method: "POST", body: request)
    }
    
    /// Get navigation help
    func getNavigationHelp(_ request: SupportRequest) -> AnyPublisher<SupportResponse, Error> {
        let endpoint = "/api/v1/support/navigation"
        return performRequest(endpoint: endpoint, method: "POST", body: request)
    }
    
    /// Get FAQ
    func getFAQ(category: SupportCategory? = nil) -> AnyPublisher<[FAQItem], Error> {
        var endpoint = "/api/v1/support/faq"
        if let category = category {
            endpoint += "?category=\(category.rawValue)"
        }
        return performRequest(endpoint: endpoint, method: "GET", body: nil as String?)
    }
    
    /// Get support categories
    func getSupportCategories() -> AnyPublisher<[SupportCategory], Error> {
        let endpoint = "/api/v1/support/categories"
        return performRequest(endpoint: endpoint, method: "GET", body: nil as String?)
    }
    
    /// Submit feedback
    func submitFeedback(_ feedback: SupportFeedback) -> AnyPublisher<SupportResponse, Error> {
        let endpoint = "/api/v1/support/feedback"
        return performRequest(endpoint: endpoint, method: "POST", body: feedback)
    }
    
    /// Get support history
    func getSupportHistory(userId: String, limit: Int = 50) -> AnyPublisher<[SupportHistoryItem], Error> {
        let endpoint = "/api/v1/support/history?userId=\(userId)&limit=\(limit)"
        return performRequest(endpoint: endpoint, method: "GET", body: nil as String?)
    }
    
    // MARK: - Private Methods
    
    private func performRequest<T: Codable, U: Codable>(
        endpoint: String,
        method: String,
        body: T?
    ) -> AnyPublisher<U, Error> {
        guard let url = URL(string: baseURL + endpoint) else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("iOS", forHTTPHeaderField: "X-Platform")
        request.setValue(Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0", forHTTPHeaderField: "X-App-Version")
        
        if let body = body {
            do {
                request.httpBody = try JSONEncoder().encode(body)
            } catch {
                return Fail(error: APIError.encodingError(error))
                    .eraseToAnyPublisher()
            }
        }
        
        return session.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: U.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

// MARK: - Additional Models
struct FAQItem: Codable {
    let id: String
    let question: String
    let answer: String
    let category: String
    let tags: [String]
    let helpful: Int
    let notHelpful: Int
    let lastUpdated: Date
}

struct SupportFeedback: Codable {
    let sessionId: String
    let rating: Int
    let comment: String?
    let helpful: Bool
    let category: String
    let timestamp: Date
}

struct SupportHistoryItem: Codable {
    let id: String
    let question: String
    let answer: String
    let category: String
    let timestamp: Date
    let rating: Int?
    let helpful: Bool?
}

// MARK: - API Errors
enum APIError: Error, LocalizedError {
    case invalidURL
    case noData
    case decodingError(Error)
    case encodingError(Error)
    case networkError(Error)
    case serverError(Int, String)
    case unauthorized
    case forbidden
    case notFound
    case rateLimited
    case timeout
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .noData:
            return "No data received"
        case .decodingError(let error):
            return "Decoding error: \(error.localizedDescription)"
        case .encodingError(let error):
            return "Encoding error: \(error.localizedDescription)"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .serverError(let code, let message):
            return "Server error \(code): \(message)"
        case .unauthorized:
            return "Unauthorized access"
        case .forbidden:
            return "Access forbidden"
        case .notFound:
            return "Resource not found"
        case .rateLimited:
            return "Rate limit exceeded"
        case .timeout:
            return "Request timeout"
        }
    }
}

// MARK: - Support API Manager
class SupportAPIManager: ObservableObject {
    
    // MARK: - Properties
    private let apiClient: SupportAPIClient
    private let userId: String
    private let sessionId: String
    private var cancellables = Set<AnyCancellable>()
    
    @Published var isLoading = false
    @Published var lastError: APIError?
    @Published var supportHistory: [SupportHistoryItem] = []
    @Published var faqItems: [FAQItem] = []
    
    // MARK: - Initialization
    init(apiClient: SupportAPIClient, userId: String, sessionId: String = UUID().uuidString) {
        self.apiClient = apiClient
        self.userId = userId
        self.sessionId = sessionId
    }
    
    // MARK: - Public Methods
    
    /// Ask a question with automatic error handling
    func askQuestion(
        _ question: String,
        category: SupportCategory? = nil,
        context: SupportContext? = nil
    ) -> AnyPublisher<SupportResponse, Never> {
        isLoading = true
        lastError = nil
        
        let defaultContext = context ?? createDefaultContext()
        let request = SupportRequest(
            question: question,
            userId: userId,
            context: defaultContext,
            category: category
        )
        
        return apiClient.askQuestion(request)
            .handleEvents(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.lastError = error as? APIError
                    }
                }
            )
            .catch { error in
                Just(SupportResponse(
                    answer: "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.",
                    category: "error",
                    suggestedActions: ["Попробовать еще раз", "Обратиться в поддержку"],
                    relatedTopics: [],
                    confidence: 0.0,
                    responseTime: 0.0,
                    timestamp: Date(),
                    sessionId: self.sessionId,
                    followUpQuestions: nil,
                    emotionalAnalysis: nil,
                    priority: .low
                ))
            }
            .eraseToAnyPublisher()
    }
    
    /// Get psychological support
    func getPsychologicalSupport(
        _ question: String,
        ageGroup: String? = nil,
        emotionalState: String? = nil
    ) -> AnyPublisher<SupportResponse, Never> {
        isLoading = true
        lastError = nil
        
        let context = SupportContext(
            currentScreen: nil,
            userAgeGroup: ageGroup,
            emotionalState: emotionalState,
            deviceInfo: createDeviceInfo(),
            sessionId: sessionId
        )
        
        let request = SupportRequest(
            question: question,
            userId: userId,
            context: context,
            category: .psychology
        )
        
        return apiClient.getPsychologicalSupport(request)
            .handleEvents(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.lastError = error as? APIError
                    }
                }
            )
            .catch { error in
                Just(SupportResponse(
                    answer: "Извините, психологическая поддержка временно недоступна. Пожалуйста, попробуйте позже.",
                    category: "psychology",
                    suggestedActions: ["Попробовать позже", "Обратиться к специалисту"],
                    relatedTopics: [],
                    confidence: 0.0,
                    responseTime: 0.0,
                    timestamp: Date(),
                    sessionId: self.sessionId,
                    followUpQuestions: nil,
                    emotionalAnalysis: nil,
                    priority: .medium
                ))
            }
            .eraseToAnyPublisher()
    }
    
    /// Load FAQ items
    func loadFAQ(category: SupportCategory? = nil) {
        apiClient.getFAQ(category: category)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure(let error) = completion {
                        self?.lastError = error as? APIError
                    }
                },
                receiveValue: { [weak self] items in
                    self?.faqItems = items
                }
            )
            .store(in: &cancellables)
    }
    
    /// Load support history
    func loadSupportHistory() {
        apiClient.getSupportHistory(userId: userId)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure(let error) = completion {
                        self?.lastError = error as? APIError
                    }
                },
                receiveValue: { [weak self] items in
                    self?.supportHistory = items
                }
            )
            .store(in: &cancellables)
    }
    
    /// Submit feedback
    func submitFeedback(
        sessionId: String,
        rating: Int,
        comment: String? = nil,
        helpful: Bool,
        category: String
    ) {
        let feedback = SupportFeedback(
            sessionId: sessionId,
            rating: rating,
            comment: comment,
            helpful: helpful,
            category: category,
            timestamp: Date()
        )
        
        apiClient.submitFeedback(feedback)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure(let error) = completion {
                        self?.lastError = error as? APIError
                    }
                },
                receiveValue: { _ in
                    // Feedback submitted successfully
                }
            )
            .store(in: &cancellables)
    }
    
    // MARK: - Private Methods
    
    private func createDefaultContext() -> SupportContext {
        return SupportContext(
            currentScreen: nil,
            userAgeGroup: nil,
            emotionalState: nil,
            deviceInfo: createDeviceInfo(),
            sessionId: sessionId
        )
    }
    
    private func createDeviceInfo() -> DeviceInfo {
        let screenSize = UIScreen.main.bounds.size
        let screenSizeString = "\(Int(screenSize.width))x\(Int(screenSize.height))"
        
        return DeviceInfo(
            platform: "iOS",
            version: UIDevice.current.systemVersion,
            model: UIDevice.current.model,
            screenSize: screenSizeString,
            orientation: UIDevice.current.orientation.isPortrait ? "portrait" : "landscape"
        )
    }
}

// MARK: - Support API Extensions
extension SupportAPIManager {
    
    /// Quick question method for simple queries
    func quickQuestion(_ question: String) -> AnyPublisher<SupportResponse, Never> {
        return askQuestion(question)
    }
    
    /// Get help for specific screen
    func getScreenHelp(screen: String) -> AnyPublisher<SupportResponse, Never> {
        let context = SupportContext(
            currentScreen: screen,
            userAgeGroup: nil,
            emotionalState: nil,
            deviceInfo: createDeviceInfo(),
            sessionId: sessionId
        )
        
        let request = SupportRequest(
            question: "Помощь по экрану \(screen)",
            userId: userId,
            context: context,
            category: .technology
        )
        
        return apiClient.getNavigationHelp(request)
            .catch { error in
                Just(SupportResponse(
                    answer: "Помощь по экрану \(screen) временно недоступна.",
                    category: "technology",
                    suggestedActions: ["Попробовать позже"],
                    relatedTopics: [],
                    confidence: 0.0,
                    responseTime: 0.0,
                    timestamp: Date(),
                    sessionId: self.sessionId,
                    followUpQuestions: nil,
                    emotionalAnalysis: nil,
                    priority: .low
                ))
            }
            .eraseToAnyPublisher()
    }
}

