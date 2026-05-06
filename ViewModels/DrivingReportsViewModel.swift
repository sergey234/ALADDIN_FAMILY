import Foundation
import Combine
import CoreLocation

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
    private let localizationManager: LocalizationManager
    private let locationManager = LocationManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(apiService: APIService? = nil, localizationManager: LocalizationManager = LocalizationManager()) {
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
    }
    
    // MARK: - Public Methods
    
    /// Применить данные из объединённой аналитики компонентов (без прямых сетевых запросов)
    func applyFrom(components: ComponentsAnalytics?, period: String) {
        // Достаём агрегированные метрики по компоненту Driving
        guard let stats = components?.getStats(for: "driving_reports_agent") else {
            self.stats = nil
            self.reports = []
            self.errorMessage = nil
            return
        }
        // Преобразуем агрегированные метрики к нашим UI-моделям
        let totalTrips = stats.getIntMetric(key: "trips_total")
        let totalDistanceKm = stats.getDoubleMetric(key: "distance_km_total")
        let totalDurationSec = stats.getDoubleMetric(key: "duration_sec_total")
        let avgSafety = stats.getDoubleMetric(key: "avg_safety_score")
        let violations = stats.getIntMetric(key: "violations_total")
        let positioning = stats.getMetric(key: "positioning") // может быть пустым
        
        self.stats = DrivingStats(
            totalTrips: totalTrips,
            totalDistance: totalDistanceKm,
            totalDuration: totalDurationSec,
            averageSafetyScore: avgSafety,
            violationsCount: violations,
            period: period,
            positioningSystem: positioning.isEmpty ? nil : positioning
        )
        // Агрегатор компонентов не отдаёт детальные поездки — показываем пустой список (UI отрисует «Нет данных»)
        self.reports = []
        self.errorMessage = nil
    }
    
    func loadReports(userId: String?, period: String) async {
        // Переведено на единый источник данных: AnalyticsViewModel.componentsAnalytics
        // Сетевая загрузка здесь больше не выполняется.
        return
    }
    
    func exportReport(reportId: String, format: String) async throws -> Data {
        return try await withCheckedThrowingContinuation { continuation in
            apiService.exportDrivingReport(reportId: reportId, format: format) { result in
                continuation.resume(with: result)
            }
        }
    }
    
    // ✅ ИНТЕГРАЦИЯ: Начать поездку с получением координат
    func startTrip(userId: String?) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // ✅ ИНТЕГРАЦИЯ: Получаем текущее местоположение при начале поездки
            let startLocation = try await locationManager.getCurrentLocation()
            print("📍 DrivingReportsViewModel: Начало поездки для пользователя \(userId ?? "current"): \(startLocation.coordinate.latitude), \(startLocation.coordinate.longitude)")
            
            // ✅ ИНТЕГРАЦИЯ: Отправляем координаты начала поездки на сервер
            try await withCheckedThrowingContinuation { continuation in
                apiService.startDrivingTrip(userId: userId, startLatitude: startLocation.coordinate.latitude, startLongitude: startLocation.coordinate.longitude) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            
            // Обновляем отчеты
            await loadReports(userId: userId, period: "week")
        } catch {
            // Если ошибка получения местоположения - все равно начинаем поездку
            if error is LocationManagerError {
                print("⚠️ DrivingReportsViewModel: Ошибка получения местоположения, но начинаем поездку: \(error.localizedDescription)")
                // Продолжаем без координат
                await loadReports(userId: userId, period: "week")
            } else {
                let networkError = NetworkError.from(error)
                // ✅ ИСПРАВЛЕНИЕ 1: Обрабатываем ошибку авторизации отдельно
                if case .unauthorized = networkError {
                    errorMessage = "Требуется авторизация. Войдите в аккаунт для начала поездки."
                } else if networkError.isCritical || !networkError.isRetryable {
                    let errorKey = "driving_reports_error_start_failed"
                    let errorFormat = localizationManager.localized(errorKey)
                    errorMessage = String(format: errorFormat, networkError.localizedDescription)
                }
            }
        }
    }
    
    // ✅ ИНТЕГРАЦИЯ: Завершить поездку с получением координат
    func endTrip(userId: String?, tripId: String?) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        do {
            // ✅ ИНТЕГРАЦИЯ: Получаем текущее местоположение при завершении поездки
            let endLocation = try await locationManager.getCurrentLocation()
            print("📍 DrivingReportsViewModel: Завершение поездки \(tripId ?? "current"): \(endLocation.coordinate.latitude), \(endLocation.coordinate.longitude)")
            
            // ✅ ИНТЕГРАЦИЯ: Отправляем координаты конца поездки на сервер
            try await withCheckedThrowingContinuation { continuation in
                apiService.endDrivingTrip(tripId: tripId ?? "current", endLatitude: endLocation.coordinate.latitude, endLongitude: endLocation.coordinate.longitude) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            
            // Обновляем отчеты
            await loadReports(userId: userId, period: "week")
        } catch {
            // Если ошибка получения местоположения - все равно завершаем поездку
            if error is LocationManagerError {
                print("⚠️ DrivingReportsViewModel: Ошибка получения местоположения, но завершаем поездку: \(error.localizedDescription)")
                // Продолжаем без координат
                await loadReports(userId: userId, period: "week")
            } else {
                let networkError = NetworkError.from(error)
                // ✅ ИСПРАВЛЕНИЕ 1: Обрабатываем ошибку авторизации отдельно
                if case .unauthorized = networkError {
                    errorMessage = "Требуется авторизация. Войдите в аккаунт для завершения поездки."
                } else if networkError.isCritical || !networkError.isRetryable {
                    let errorKey = "driving_reports_error_end_failed"
                    let errorFormat = localizationManager.localized(errorKey)
                    errorMessage = String(format: errorFormat, networkError.localizedDescription)
                }
            }
        }
    }
}

