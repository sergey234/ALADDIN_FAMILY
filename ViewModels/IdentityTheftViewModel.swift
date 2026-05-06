import Foundation
import Combine

/**
 * 🛡️ Identity Theft Protection ViewModel
 * Управление данными для IdentityTheftModal
 */

@MainActor
class IdentityTheftViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var stats: IdentityTheftStats?
    @Published var attempts: [IdentityTheftAttempt] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(apiService: APIService? = nil, localizationManager: LocalizationManager = LocalizationManager()) {
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
    }
    
    // MARK: - Public Methods
    
    func loadData(action: String? = nil, severity: String? = nil) async {
        // ✅ ИСПРАВЛЕНИЕ: Проверяем токен перед загрузкой
        guard AppConfig.authToken != nil else {
            errorMessage = "Требуется авторизация. Войдите в аккаунт для просмотра данных."
            return
        }
        
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // Загружаем статистику и попытки параллельно
            async let statsTask: IdentityTheftStats = withCheckedThrowingContinuation { continuation in
                Task { @MainActor in
                    self.apiService.getIdentityTheftStats { result in
                        continuation.resume(with: result)
                    }
                }
            }
            
            async let attemptsTask: [IdentityTheftAttempt] = withCheckedThrowingContinuation { continuation in
                Task { @MainActor in
                    self.apiService.getIdentityTheftAttempts(action: action, severity: severity) { result in
                        continuation.resume(with: result)
                    }
                }
            }
            
            let (stats, attempts) = try await (statsTask, attemptsTask)
            self.stats = stats
            self.attempts = attempts
            // Очищаем ошибку при успешной загрузке
            errorMessage = nil
        } catch {
            // Проверяем тип ошибки - показываем только реальные проблемы
            let networkError = NetworkError.from(error)
            
            // ✅ ИСПРАВЛЕНИЕ: Обрабатываем ошибку авторизации отдельно
            if case .unauthorized = networkError {
                errorMessage = "Требуется авторизация. Войдите в аккаунт для просмотра данных."
                self.stats = nil
                self.attempts = []
                return
            }
            
            // Не показываем ошибку для 404 (нет данных - это нормально)
            if case .notFound = networkError {
                // Просто используем пустые данные, не показываем ошибку
                self.stats = nil
                self.attempts = []
                errorMessage = nil
                return
            }
            
            // Показываем ошибку только для реальных проблем
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "identity_theft_error_load_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для временных ошибок тоже не показываем, просто используем пустые данные
                errorMessage = nil
            }
            
            // В случае ошибки используем пустые данные
            self.stats = nil
            self.attempts = []
        }
    }
    
    // MARK: - Actions
    
    func allowAttempt(attemptId: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.allowIdentityTheftAttempt(attemptId: attemptId) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadData()
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "identity_theft_error_action_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    func blockAttempt(attemptId: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.blockIdentityTheftAttempt(attemptId: attemptId) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadData()
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "identity_theft_error_action_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    func addToWhitelist(source: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.addToWhitelist(source: source) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadData()
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "identity_theft_error_whitelist_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
}

