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
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(apiService: APIService = APIService.shared) {
        self.apiService = apiService
    }
    
    // MARK: - Public Methods
    
    func loadData(action: String? = nil, severity: String? = nil) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // Загружаем статистику и попытки параллельно
            async let statsTask: IdentityTheftStats = withCheckedThrowingContinuation { continuation in
                apiService.getIdentityTheftStats { result in
                    continuation.resume(with: result)
                }
            }
            
            async let attemptsTask: [IdentityTheftAttempt] = withCheckedThrowingContinuation { continuation in
                apiService.getIdentityTheftAttempts(action: action, severity: severity) { result in
                    continuation.resume(with: result)
                }
            }
            
            let (stats, attempts) = try await (statsTask, attemptsTask)
            self.stats = stats
            self.attempts = attempts
        } catch {
            errorMessage = "Не удалось загрузить данные: \(error.localizedDescription)"
            // В случае ошибки используем пустые данные
            self.stats = nil
            self.attempts = []
        }
    }
}

