import Foundation
import Combine

/**
 * 🚗 Driving Reports ViewModel
 * Управление данными для DrivingReportsModal
 */

@MainActor
class DrivingReportsViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var stats: DrivingStats?
    @Published var reports: [DrivingReport] = []
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
    
    func loadReports(userId: String?, period: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // Загружаем статистику и отчеты параллельно
            async let statsTask: DrivingStats = withCheckedThrowingContinuation { continuation in
                apiService.getDrivingStats(userId: userId, period: period) { result in
                    continuation.resume(with: result)
                }
            }
            
            async let reportsTask: [DrivingReport] = withCheckedThrowingContinuation { continuation in
                apiService.getDrivingReports(userId: userId, period: period) { result in
                    continuation.resume(with: result)
                }
            }
            
            let (stats, reports) = try await (statsTask, reportsTask)
            self.stats = stats
            self.reports = reports
        } catch {
            errorMessage = "Не удалось загрузить отчеты о вождении: \(error.localizedDescription)"
            // В случае ошибки используем пустые данные
            self.stats = nil
            self.reports = []
        }
    }
    
    func exportReport(reportId: String, format: String) async throws -> Data {
        return try await withCheckedThrowingContinuation { continuation in
            apiService.exportDrivingReport(reportId: reportId, format: format) { result in
                continuation.resume(with: result)
            }
        }
    }
}

