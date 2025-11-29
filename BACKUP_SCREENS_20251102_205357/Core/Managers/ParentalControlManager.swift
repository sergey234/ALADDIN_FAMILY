import Foundation
import Combine

/**
 * 👨‍👩‍👧‍👦 Parental Control Manager
 * Управление родительским контролем
 * Централизованная логика для всех функций родительского контроля
 */

class ParentalControlManager: ObservableObject {
    
    // MARK: - Dependencies
    
    private let apiService: APIService
    private let networkManager: NetworkManager
    
    // MARK: - Published Properties
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Singleton
    
    static let shared = ParentalControlManager()
    
    // MARK: - Initialization
    
    init(
        apiService: APIService? = nil,
        networkManager: NetworkManager? = nil
    ) {
        // Инициализируем NetworkManager
        if let networkManager = networkManager {
            self.networkManager = networkManager
        } else {
            self.networkManager = NetworkManager()
        }
        
        // Инициализируем APIService с NetworkManager
        if let apiService = apiService {
            self.apiService = apiService
        } else {
            self.apiService = APIService(networkManager: self.networkManager)
        }
    }
    
    // MARK: - Content Blocking
    
    /**
     * Применение блокировки контента
     */
    func applyContentBlocking(
        childId: String,
        websiteBlocking: Bool,
        appBlocking: Bool,
        searchBlocking: Bool,
        safesearch: Bool,
        completion: ((Bool, String?) -> Void)? = nil
    ) {
        isLoading = true
        errorMessage = nil
        
        var successCount = 0
        var errorMessages: [String] = []
        let group = DispatchGroup()
        
        // Применяем блокировку сайтов
        if websiteBlocking != UserDefaults.standard.bool(forKey: "parental_website_blocking") {
            group.enter()
            apiService.applyBlocking(childId: childId, type: .website, enabled: websiteBlocking) { result in
                switch result {
                case .success:
                    successCount += 1
                    print("✅ Блокировка сайтов: \(websiteBlocking ? "ВКЛ" : "ВЫКЛ")")
                case .failure(let error):
                    errorMessages.append("Ошибка блокировки сайтов: \(error.localizedDescription)")
                }
                group.leave()
            }
        } else {
            successCount += 1
        }
        
        // Применяем блокировку приложений
        if appBlocking != UserDefaults.standard.bool(forKey: "parental_app_blocking") {
            group.enter()
            apiService.applyBlocking(childId: childId, type: .app, enabled: appBlocking) { result in
                switch result {
                case .success:
                    successCount += 1
                    print("✅ Блокировка приложений: \(appBlocking ? "ВКЛ" : "ВЫКЛ")")
                case .failure(let error):
                    errorMessages.append("Ошибка блокировки приложений: \(error.localizedDescription)")
                }
                group.leave()
            }
        } else {
            successCount += 1
        }
        
        // Применяем блокировку поисковых запросов
        if searchBlocking != UserDefaults.standard.bool(forKey: "parental_search_blocking") {
            group.enter()
            apiService.applyBlocking(childId: childId, type: .search, enabled: searchBlocking) { result in
                switch result {
                case .success:
                    successCount += 1
                    print("✅ Блокировка поисковых запросов: \(searchBlocking ? "ВКЛ" : "ВЫКЛ")")
                case .failure(let error):
                    errorMessages.append("Ошибка блокировки поиска: \(error.localizedDescription)")
                }
                group.leave()
            }
        } else {
            successCount += 1
        }
        
        // Применяем SafeSearch
        if safesearch != UserDefaults.standard.bool(forKey: "parental_safesearch") {
            group.enter()
            apiService.applyBlocking(childId: childId, type: .safesearch, enabled: safesearch) { result in
                switch result {
                case .success:
                    successCount += 1
                    print("✅ SafeSearch: \(safesearch ? "ВКЛ" : "ВЫКЛ")")
                case .failure(let error):
                    errorMessages.append("Ошибка SafeSearch: \(error.localizedDescription)")
                }
                group.leave()
            }
        } else {
            successCount += 1
        }
        
        // Ждём завершения всех запросов
        group.notify(queue: .main) { [weak self] in
            self?.isLoading = false
            
            if errorMessages.isEmpty {
                self?.errorMessage = nil
                completion?(true, nil)
            } else {
                self?.errorMessage = errorMessages.joined(separator: "\n")
                completion?(false, errorMessages.first)
            }
        }
    }
    
    // MARK: - Apply Rules
    
    /**
     * Применение правил родительского контроля
     */
    func applyRules(
        childId: String,
        ageGroup: String,
        rules: ParentalControlRules,
        completion: ((Bool, String?) -> Void)? = nil
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.applyParentalControlRules(childId: childId, ageGroup: ageGroup, rules: rules) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    if response.success {
                        print("✅ Правила применены для \(childId), возраст: \(ageGroup)")
                        self?.errorMessage = nil
                        completion?(true, nil)
                    } else {
                        let errorMsg = response.message ?? "Ошибка применения правил"
                        self?.errorMessage = errorMsg
                        completion?(false, errorMsg)
                    }
                case .failure(let error):
                    let errorMsg = error.localizedDescription
                    self?.errorMessage = errorMsg
                    completion?(false, errorMsg)
                }
            }
        }
    }
    
    // MARK: - Access Requests
    
    /**
     * Получение запросов доступа
     */
    func getAccessRequests(
        childId: String? = nil,
        completion: @escaping (Result<[AccessRequestResponse], Error>) -> Void
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.getAccessRequests(childId: childId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let requests):
                    self?.errorMessage = nil
                    completion(.success(requests))
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    completion(.failure(error))
                }
            }
        }
    }
    
    /**
     * Обработка запроса доступа (принять/отклонить)
     */
    func handleAccessRequest(
        requestId: String,
        action: String, // "accept" или "reject"
        reason: String? = nil,
        completion: ((Bool, String?) -> Void)? = nil
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.handleAccessRequest(requestId: requestId, action: action, reason: reason) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    if response.success {
                        print("✅ Запрос \(requestId) \(action == "accept" ? "принят" : "отклонён")")
                        self?.errorMessage = nil
                        completion?(true, nil)
                    } else {
                        let errorMsg = response.message ?? "Ошибка обработки запроса"
                        self?.errorMessage = errorMsg
                        completion?(false, errorMsg)
                    }
                case .failure(let error):
                    let errorMsg = error.localizedDescription
                    self?.errorMessage = errorMsg
                    completion?(false, errorMsg)
                }
            }
        }
    }
    
    // MARK: - Statistics
    
    /**
     * Получение статистики родительского контроля
     */
    func getStats(
        childId: String? = nil,
        completion: @escaping (Result<ParentalControlStatsResponse, Error>) -> Void
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.getParentalControlStats(childId: childId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let stats):
                    self?.errorMessage = nil
                    completion(.success(stats))
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    completion(.failure(error))
                }
            }
        }
    }
    
    // MARK: - Bypass Protection
    
    /**
     * Получение статистики защиты от обхода
     */
    func getBypassStats(
        childId: String? = nil,
        completion: @escaping (Result<BypassStatsResponse, Error>) -> Void
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.getBypassStats(childId: childId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let stats):
                    self?.errorMessage = nil
                    completion(.success(stats))
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    completion(.failure(error))
                }
            }
        }
    }
    
    /**
     * Применение защиты от обхода
     */
    func applyBypassProtection(
        childId: String,
        incognito: Bool,
        tor: Bool,
        proxy: Bool,
        completion: ((Bool, String?) -> Void)? = nil
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.applyBypassProtection(childId: childId, incognito: incognito, tor: tor, proxy: proxy) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    if response.success {
                        print("✅ Защита от обхода применена для \(childId)")
                        self?.errorMessage = nil
                        completion?(true, nil)
                    } else {
                        let errorMsg = response.message ?? "Ошибка применения защиты от обхода"
                        self?.errorMessage = errorMsg
                        completion?(false, errorMsg)
                    }
                case .failure(let error):
                    let errorMsg = error.localizedDescription
                    self?.errorMessage = errorMsg
                    completion?(false, errorMsg)
                }
            }
        }
    }
    
    /**
     * Обнаружение попытки обхода
     */
    func detectBypassAttempt(
        type: BypassType,
        childId: String,
        completion: ((Bool) -> Void)? = nil
    ) {
        // Сохраняем попытку обхода
        let attempt = BypassAttempt(
            id: UUID().uuidString,
            type: type,
            timestamp: Date(),
            blocked: true,
            deviceName: "Устройство \(childId)"
        )
        
        saveBypassAttempt(attempt)
        
        // Проверяем настройки уведомлений
        let notificationManager = NotificationManager.shared
        let _ = notificationManager.notificationSettings
        
        // Создаем уведомление для экрана уведомлений (через NotificationManager)
        NotificationManager.shared.sendLocalNotification(
            title: "🚨 Попытка обхода",
            body: "\(type.displayName) заблокирован",
            category: .security,
            userInfo: [
                "type": "bypass",
                "bypass_type": type.rawValue,
                "child_id": childId
            ]
        )
        
        // Push-уведомление отправляется ТОЛЬКО если включено в настройках
        // Проверка выполняется в NotificationManager.sendLocalNotification()
        
        completion?(true)
    }
    
    /**
     * Сохранение попытки обхода
     */
    private func saveBypassAttempt(_ attempt: BypassAttempt) {
        // Сохраняем в UserDefaults или отправляем на сервер
        let _ = "bypass_attempts_\(attempt.childId ?? "all")"
        // TODO: Реализовать сохранение в UserDefaults или API
        print("💾 Сохранена попытка обхода: \(attempt.type.displayName) для \(attempt.childId ?? "всех")")
    }
    
    /**
     * Форматирование времени
     */
    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }
}

// MARK: - Bypass Attempt Model

struct BypassAttempt {
    let id: String
    let type: BypassType
    let timestamp: Date
    let blocked: Bool
    let deviceName: String
    let childId: String?
    
    init(id: String, type: BypassType, timestamp: Date, blocked: Bool, deviceName: String, childId: String? = nil) {
        self.id = id
        self.type = type
        self.timestamp = timestamp
        self.blocked = blocked
        self.deviceName = deviceName
        self.childId = childId
    }
}

// MARK: - Bypass Stats Response
// BypassStatsResponse теперь находится в Core/Models/APIModels.swift

