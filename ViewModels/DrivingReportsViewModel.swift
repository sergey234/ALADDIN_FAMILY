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
        
        // ✅ ИСПРАВЛЕНО: Умная проверка токена через TokenManager (как в AnalyticsViewModel)
        // Проверяет SubscriptionManager.currentToken первым делом!
        let tokenAvailability = TokenManager.shared.checkTokenAvailability()
        
        // Если токен загружается - ждем немного
        if tokenAvailability.isAvailable {
            // Токен доступен - продолжаем загрузку
            #if DEBUG
            VisualLogger.shared.log("✅ DrivingReportsViewModel: Токен доступен, начинаем загрузку отчетов", level: .success, category: "DRIVING_REPORTS")
            print("✅ DrivingReportsViewModel: Токен доступен, начинаем загрузку отчетов")
            #endif
        } else {
            // Токен не найден - проверяем, загружается ли он
            if TokenManager.shared.isTokenLoading() {
                // Токен загружается - ждем до 500ms
                #if DEBUG
                VisualLogger.shared.log("⏳ DrivingReportsViewModel: Токен загружается, ждем...", level: .info, category: "DRIVING_REPORTS")
                print("⏳ DrivingReportsViewModel: Токен загружается, ждем...")
                #endif
                if let token = await TokenManager.shared.waitForTokenLoad(maxWaitTime: 0.5) {
                    // Токен загрузился - продолжаем
                    #if DEBUG
                    VisualLogger.shared.log("✅ DrivingReportsViewModel: Токен загрузился, продолжаем загрузку отчетов", level: .success, category: "DRIVING_REPORTS")
                    print("✅ DrivingReportsViewModel: Токен загрузился, продолжаем загрузку отчетов")
                    #endif
                } else {
                    // Токен не загрузился - показываем ошибку (БЕЗ SessionExpired)
                    #if DEBUG
                    VisualLogger.shared.log("⚠️ DrivingReportsViewModel: Токен не загрузился, показываем ошибку", level: .warning, category: "DRIVING_REPORTS")
                    print("⚠️ DrivingReportsViewModel: Токен не загрузился, показываем ошибку")
                    #endif
                    errorMessage = "Не удалось загрузить отчеты. Проверьте подключение к интернету."
                    self.stats = nil
                    self.reports = []
                    return
                }
            } else {
                // Токена нет нигде - показываем ошибку (БЕЗ SessionExpired)
                // SessionExpired отправляется только при реальных 401 ошибках от API
                #if DEBUG
                VisualLogger.shared.log("⚠️ DrivingReportsViewModel: Токен отсутствует, показываем ошибку", level: .warning, category: "DRIVING_REPORTS")
                print("⚠️ DrivingReportsViewModel: Токен отсутствует, показываем ошибку")
                #endif
                errorMessage = "Не удалось загрузить отчеты. Проверьте подключение к интернету."
                self.stats = nil
                self.reports = []
                return
            }
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
            
            // ✅ ИСПРАВЛЕНО: Обработка unauthorized - SessionExpired отправляется только при реальных 401 ошибках
            if case .unauthorized(let message) = networkError {
                // Реальная ошибка авторизации от API (401) - отправляем SessionExpired
                let errorMessage = message ?? "Сессия истекла. Пожалуйста, войдите снова."
                self.errorMessage = errorMessage
                self.stats = nil
                self.reports = []
                // ✅ Отправляем SessionExpired только при реальных 401 ошибках от API
                // ✅ BUILD 121: Логирование отправки SessionExpired
                #if DEBUG
                let stackTrace = Thread.callStackSymbols.prefix(5).joined(separator: "\n")
                print("📤 DrivingReportsViewModel: Отправка SessionExpired notification")
                print("   - Call stack:")
                print(stackTrace)
                VisualLogger.shared.log("📤 DrivingReportsViewModel: Отправка SessionExpired", level: .warning, category: "SESSION")
                MasterLogger.shared.log(.warn, category: .business, message: "📤 DrivingReportsViewModel: Sending SessionExpired notification")
                #endif
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

