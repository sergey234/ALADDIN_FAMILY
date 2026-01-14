import Foundation
import Combine

/**
 * 🔒 Privacy Reports ViewModel
 * Управление данными для PrivacyReportsModal
 * Включает Location Bubble, Data Cleanup, Anti Tracker
 */

@MainActor
class PrivacyReportsViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    // Location Bubble
    @Published var locationStats: LocationStats?
    @Published var locationRequests: [LocationRequest] = []
    
    // Data Cleanup
    @Published var cleanupStats: DataCleanupStats?
    @Published var cleanupRecords: [DataCleanupRecord] = []
    
    // Anti Tracker
    @Published var trackerStats: AntiTrackerStats?
    @Published var topTrackers: [TrackerBlock] = []
    
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
    
    func loadLocationData() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // Загружаем статистику и запросы параллельно
            async let statsTask: LocationStats = withCheckedThrowingContinuation { continuation in
                apiService.getLocationStats { result in
                    continuation.resume(with: result)
                }
            }
            
            async let requestsTask: [LocationRequest] = withCheckedThrowingContinuation { continuation in
                apiService.getLocationRequests(limit: 50) { result in
                    continuation.resume(with: result)
                }
            }
            
            let (stats, requests) = try await (statsTask, requestsTask)
            self.locationStats = stats
            self.locationRequests = requests
        } catch {
            errorMessage = "Не удалось загрузить данные местоположения: \(error.localizedDescription)"
            // В случае ошибки используем пустые данные
            self.locationStats = nil
            self.locationRequests = []
        }
    }
    
    func loadCleanupData() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // Загружаем статистику и записи параллельно
            async let statsTask: DataCleanupStats = withCheckedThrowingContinuation { continuation in
                apiService.getDataCleanupStats { result in
                    continuation.resume(with: result)
                }
            }
            
            async let recordsTask: [DataCleanupRecord] = withCheckedThrowingContinuation { continuation in
                apiService.getDataCleanupRecords(limit: 20) { result in
                    continuation.resume(with: result)
                }
            }
            
            let (stats, records) = try await (statsTask, recordsTask)
            self.cleanupStats = stats
            self.cleanupRecords = records
        } catch {
            errorMessage = "Не удалось загрузить данные очистки: \(error.localizedDescription)"
            // В случае ошибки используем пустые данные
            self.cleanupStats = nil
            self.cleanupRecords = []
        }
    }
    
    func loadTrackerData() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // Загружаем статистику и топ трекеров параллельно
            async let statsTask: AntiTrackerStats = withCheckedThrowingContinuation { continuation in
                apiService.getAntiTrackerStats { result in
                    continuation.resume(with: result)
                }
            }
            
            async let trackersTask: [TrackerBlock] = withCheckedThrowingContinuation { continuation in
                apiService.getTopTrackers(limit: 10) { result in
                    continuation.resume(with: result)
                }
            }
            
            let (stats, trackers) = try await (statsTask, trackersTask)
            self.trackerStats = stats
            self.topTrackers = trackers
        } catch {
            errorMessage = "Не удалось загрузить данные трекеров: \(error.localizedDescription)"
            // В случае ошибки используем пустые данные
            self.trackerStats = nil
            self.topTrackers = []
        }
    }
}

