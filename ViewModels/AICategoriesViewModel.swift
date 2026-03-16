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
            
            print("✅ AICategoriesViewModel: Загружено \(familyMembers.count) членов семьи из API")
            
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
            
            print("✅ AICategoriesViewModel: Отфильтровано \(self.children.count) детей (включая подростков)")
            
            // ✅ ИСПРАВЛЕНИЕ: Если список пуст, пробуем загрузить из UserDefaults
            if self.children.isEmpty {
                print("⚠️ AICategoriesViewModel: Список детей пуст, пробуем загрузить из UserDefaults...")
                await loadChildrenFromUserDefaults()
            } else {
                // ✅ ИСПРАВЛЕНИЕ: Всегда синхронизируем с UserDefaults для полноты данных
                await loadChildrenFromUserDefaults()
            }
        } catch {
            print("❌ AICategoriesViewModel: Ошибка загрузки детей из API: \(error.localizedDescription)")
            // Пробуем загрузить из UserDefaults как fallback
            await loadChildrenFromUserDefaults()
            
            // Показываем ошибку только если и из UserDefaults ничего не загрузилось
            if self.children.isEmpty {
                let errorKey = "ai_categories_error_load_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, error.localizedDescription)
            }
        }
    }
    
    /// Загрузка детей из UserDefaults как fallback
    private func loadChildrenFromUserDefaults() async {
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Синхронизируем UserDefaults перед чтением
        UserDefaults.standard.synchronize()
        
        let familyMembersKey = "family_members_list"
        if let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            
            print("✅ AICategoriesViewModel: Загружено \(decoded.count) членов семьи из UserDefaults")
            
            let userDefaultsChildren: [UserSelectorView.UserOption] = decoded
                .filter { $0.role == .child || $0.role == .teenager }
                .map { member -> UserSelectorView.UserOption in
                    let roleString: String
                    switch member.role {
                    case .child: roleString = "child"
                    case .teenager: roleString = "teenager"
                    default: roleString = "child"
                    }
                    
                    return UserSelectorView.UserOption(
                        id: member.id.uuidString,
                        name: member.name,
                        role: roleString,
                        avatar: member.avatar
                    )
                }
            
            // Объединяем с существующими, избегая дубликатов по id
            var existingIds = Set(self.children.map { $0.id })
            let newChildren = userDefaultsChildren.filter { !existingIds.contains($0.id) }
            self.children.append(contentsOf: newChildren)
            
            print("✅ AICategoriesViewModel: Добавлено \(newChildren.count) детей из UserDefaults. Всего: \(self.children.count)")
        } else {
            print("⚠️ AICategoriesViewModel: Нет данных в UserDefaults")
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

