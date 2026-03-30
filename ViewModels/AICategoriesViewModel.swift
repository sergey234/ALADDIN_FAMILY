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
    
    /// Применить данные из объединённой аналитики компонентов (без прямых сетевых запросов)
    func applyFrom(components: ComponentsAnalytics?, childId: String?) {
        guard let components = components else {
            self.stats = nil
            self.reports = []
            return
        }
        // Достаём агрегированные метрики по компоненту AI
        if let ai = components.getStats(for: "ai_categories_agent") {
            let totalCategorized = ai.getIntMetric(key: "categorized")
            let totalBlocked = ai.getIntMetric(key: "blocked")
            let accuracy = ai.getDoubleMetric(key: "accuracy")
            
            // Карты категорий могут отсутствовать в метриках агрегатора — используем пустые
            let byCategory: [String: Int] = [:]
            let blockedByCategory: [String: Int] = [:]
            
            self.stats = AICategoriesStats(
                totalCategorized: totalCategorized,
                totalBlocked: totalBlocked,
                accuracy: accuracy,
                byCategory: byCategory,
                blockedByCategory: blockedByCategory
            )
            // Агрегатор компонентов не отдаёт подробные отчёты — показываем пустой список (UI отрисует «Нет данных»)
            self.reports = []
            self.errorMessage = nil
        } else {
            self.stats = nil
            self.reports = []
        }
    }
    
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
                        avatar: member.avatar ?? ""
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
        // Переведено на единый источник данных: AnalyticsViewModel.componentsAnalytics
        // Эта функция теперь становится no-op и сохраняется для обратной совместимости вызовов из UI.
        // Фактическое наполнение выполняется через applyFrom(components:childId:), вызываемую из модального окна.
        return
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

