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
    
    init(apiService: APIService = APIService.shared, localizationManager: LocalizationManager = LocalizationManager()) {
        self.apiService = apiService
        self.localizationManager = localizationManager
    }
    
    // MARK: - Public Methods
    
    func loadReports(userId: String?, period: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        
        // ✅ ЭТАП 2: Проверка токена перед загрузкой
        guard AppConfig.authToken != nil else {
            errorMessage = "Требуется авторизация. Войдите в аккаунт для просмотра отчетов."
            self.stats = nil
            self.reports = []
            // Отправляем уведомление о необходимости логина
            NotificationCenter.default.post(
                name: NSNotification.Name("SessionExpired"),
                object: nil,
                userInfo: ["message": "Требуется авторизация. Войдите в аккаунт."]
            )
            return
        }
        
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
            // Очищаем ошибку при успешной загрузке
            errorMessage = nil
        } catch {
            // Проверяем тип ошибки - показываем только реальные проблемы
            let networkError = NetworkError.from(error)
            
            // ✅ ЭТАП 3: Обработка unauthorized
            if case .unauthorized(let message) = networkError {
                // Ошибка авторизации - показываем понятное сообщение
                let errorMessage = message ?? "Сессия истекла. Пожалуйста, войдите снова."
                self.errorMessage = errorMessage
                self.stats = nil
                self.reports = []
                // Отправляем уведомление о необходимости логина
                NotificationCenter.default.post(
                    name: NSNotification.Name("SessionExpired"),
                    object: nil,
                    userInfo: ["message": errorMessage]
                )
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
            
            // Показываем ошибку только для реальных проблем (кроме unauthorized)
            if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "driving_reports_error_load_failed"
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

