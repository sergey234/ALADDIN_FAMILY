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
    private let localizationManager: LocalizationManager
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(apiService: APIService = APIService.shared, localizationManager: LocalizationManager = LocalizationManager()) {
        self.apiService = apiService
        self.localizationManager = localizationManager
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
            // Очищаем ошибку при успешной загрузке
            errorMessage = nil
        } catch {
            // Проверяем тип ошибки - показываем только реальные проблемы
            let networkError = NetworkError.from(error)
            
            // Не показываем ошибку для 404 (нет данных - это нормально)
            if case .notFound = networkError {
                // Просто используем пустые данные, не показываем ошибку
                self.locationStats = nil
                self.locationRequests = []
                errorMessage = nil
                return
            }
            
            // Показываем ошибку только для реальных проблем
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "privacy_error_load_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для временных ошибок тоже не показываем, просто используем пустые данные
                errorMessage = nil
            }
            
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
            // Очищаем ошибку при успешной загрузке
            errorMessage = nil
        } catch {
            // Проверяем тип ошибки - показываем только реальные проблемы
            let networkError = NetworkError.from(error)
            
            // Не показываем ошибку для 404 (нет данных - это нормально)
            if case .notFound = networkError {
                // Просто используем пустые данные, не показываем ошибку
                self.cleanupStats = nil
                self.cleanupRecords = []
                errorMessage = nil
                return
            }
            
            // Показываем ошибку только для реальных проблем
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "privacy_error_load_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для временных ошибок тоже не показываем, просто используем пустые данные
                errorMessage = nil
            }
            
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
            // Очищаем ошибку при успешной загрузке
            errorMessage = nil
        } catch {
            // Проверяем тип ошибки - показываем только реальные проблемы
            let networkError = NetworkError.from(error)
            
            // Не показываем ошибку для 404 (нет данных - это нормально)
            if case .notFound = networkError {
                // Просто используем пустые данные, не показываем ошибку
                self.trackerStats = nil
                self.topTrackers = []
                errorMessage = nil
                return
            }
            
            // Показываем ошибку только для реальных проблем
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "privacy_error_load_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для временных ошибок тоже не показываем, просто используем пустые данные
                errorMessage = nil
            }
            
            // В случае ошибки используем пустые данные
            self.trackerStats = nil
            self.topTrackers = []
        }
    }
    
    // MARK: - Location Actions
    
    func allowLocationRequest(requestId: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.allowLocationRequest(requestId: requestId) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadLocationData()
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "privacy_location_error_action_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    func blockLocationRequest(requestId: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.blockLocationRequest(requestId: requestId) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadLocationData()
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "privacy_location_error_action_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    func updateLocationAccuracy(requestId: String, accuracy: LocationAccuracy) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.updateLocationAccuracy(requestId: requestId, accuracy: accuracy) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadLocationData()
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "privacy_location_error_accuracy_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    // MARK: - Cleanup Actions
    
    func startCleanup(categories: [String]) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.startDataCleanup(categories: categories) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadCleanupData()
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "privacy_cleanup_error_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    // MARK: - Tracker Actions
    
    func addTrackerToWhitelist(trackerName: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.addTrackerToWhitelist(trackerName: trackerName) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadTrackerData()
        } catch {
            let networkError = NetworkError.from(error)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "privacy_tracker_error_whitelist_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
}

