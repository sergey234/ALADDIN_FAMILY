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
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(apiService: APIService = APIService.shared) {
        self.apiService = apiService
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
            errorMessage = "Не удалось загрузить список детей: \(error.localizedDescription)"
            // В случае ошибки используем пустой список
            self.children = []
        }
    }
    
    func loadReports(childId: String?) async {
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
        } catch {
            errorMessage = "Не удалось загрузить отчеты: \(error.localizedDescription)"
            // В случае ошибки используем пустые данные
            self.stats = nil
            self.reports = []
        }
    }
}

