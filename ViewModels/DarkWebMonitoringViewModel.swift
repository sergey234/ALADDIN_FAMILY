import Foundation
import Combine

/**
 * 🌑 Dark Web Monitoring ViewModel
 * Управление данными для DarkWebMonitoringModal
 */

@MainActor
class DarkWebMonitoringViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var stats: DarkWebStats?
    @Published var leaks: [DarkWebLeak] = []
    @Published var scans: [DarkWebScan] = []
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
    
    func loadData(status: String? = nil, severity: String? = nil) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // Загружаем статистику, утечки и сканирования параллельно
            async let statsTask: DarkWebStats = withCheckedThrowingContinuation { continuation in
                apiService.getDarkWebStats { result in
                    continuation.resume(with: result)
                }
            }
            
            async let leaksTask: [DarkWebLeak] = withCheckedThrowingContinuation { continuation in
                apiService.getDarkWebLeaks(status: status, severity: severity) { result in
                    continuation.resume(with: result)
                }
            }
            
            async let scansTask: [DarkWebScan] = withCheckedThrowingContinuation { continuation in
                apiService.getDarkWebScans(limit: 20) { result in
                    continuation.resume(with: result)
                }
            }
            
            let (stats, leaks, scans) = try await (statsTask, leaksTask, scansTask)
            self.stats = stats
            self.leaks = leaks
            self.scans = scans
        } catch {
            errorMessage = "Не удалось загрузить данные: \(error.localizedDescription)"
            // В случае ошибки используем пустые данные
            self.stats = nil
            self.leaks = []
            self.scans = []
        }
    }
    
    func resolveLeak(leakId: String) async throws {
        try await withCheckedThrowingContinuation { continuation in
            apiService.resolveDarkWebLeak(leakId: leakId) { result in
                continuation.resume(with: result.map { _ in () })
            }
        }
        // Обновить локальные данные после успешного решения
        await loadData()
    }
}

