import Foundation
import Combine

/**
 * 🤖 AI Categories ViewModel
 * Управление данными для AICategoriesModal
 */

@MainActor
class AICategoriesViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var stats: AICategoriesStats?
    @Published var reports: [AICategoryReport] = []
    @Published var children: [UserSelectorView.UserOption] = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(apiService: APIService = APIService.shared, localizationManager: LocalizationManager = LocalizationManager()) {
        self.apiService = apiService
        self.localizationManager = localizationManager
    }
    
    // MARK: - Public Methods
    
    func loadChildren() async {
        do {
            // Загружаем список членов семьи и фильтруем детей
            let familyMembers: [FamilyMemberResponse] = try await withCheckedThrowingContinuation { continuation in
                apiService.getFamilyMembers { result in
                    continuation.resume(with: result)
                }
            }
            
            self.children = familyMembers
                .filter { $0.role == "child" || $0.role == "teenager" }
                .map { member in
                    UserSelectorView.UserOption(
                        id: member.id,
                        name: member.name,
                        role: member.role,
                        avatar: member.avatar
                    )
                }
        } catch {
            let errorKey = "ai_categories_error_load_failed"
            let errorFormat = localizationManager.localized(errorKey)
            errorMessage = String(format: errorFormat, error.localizedDescription)
            // В случае ошибки используем пустой список
            self.children = []
        }
    }
    
    func loadReports(childId: String?) async {
        // ✅ ИСПРАВЛЕНИЕ: Проверяем токен перед загрузкой
        guard AppConfig.authToken != nil else {
            errorMessage = "Требуется авторизация. Войдите в аккаунт для просмотра данных."
            return
        }
        
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // Загружаем статистику и отчеты параллельно
            async let statsTask: AICategoriesStats = withCheckedThrowingContinuation { continuation in
                apiService.getAICategoriesStats(childId: childId) { result in
                    continuation.resume(with: result)
                }
            }
            
            async let reportsTask: [AICategoryReport] = withCheckedThrowingContinuation { continuation in
                apiService.getAICategoryReports(childId: childId) { result in
                    continuation.resume(with: result)
                }
            }
            
            let (stats, reports) = try await (statsTask, reportsTask)
            self.stats = stats
            self.reports = reports
            // Очищаем ошибку при успешной загрузке
            errorMessage = nil
        } catch {
            // Проверяем тип ошибки - показываем только реальные проблемы
            let networkError = NetworkError.from(error)
            
            // ✅ ИСПРАВЛЕНИЕ: Обрабатываем ошибку авторизации отдельно
            if case .unauthorized = networkError {
                errorMessage = "Требуется авторизация. Войдите в аккаунт для просмотра данных."
                self.stats = nil
                self.reports = []
                return
            }
            
            // Не показываем ошибку для 404 (нет данных - это нормально)
            if case .notFound = networkError {
                // Просто используем пустые данные, не показываем ошибку
                self.stats = nil
                self.reports = []
                errorMessage = nil
                return
            }
            
            // Показываем ошибку только для реальных проблем
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "ai_categories_error_load_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для временных ошибок тоже не показываем, просто используем пустые данные
                errorMessage = nil
            }
            
            // В случае ошибки используем пустые данные
            self.stats = nil
            self.reports = []
        }
    }
    
    // MARK: - Actions
    
    func allowContent(contentId: String, childId: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.allowAIContent(contentId: contentId, childId: childId) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadReports(childId: childId.isEmpty ? nil : childId)
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "ai_categories_error_action_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    func blockContent(contentId: String, childId: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.blockAIContent(contentId: contentId, childId: childId) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadReports(childId: childId.isEmpty ? nil : childId)
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "ai_categories_error_action_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
}

