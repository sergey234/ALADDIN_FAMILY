import Foundation
import Combine
import CryptoKit

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
    @Published var isScanning: Bool = false
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
    
    func loadData(status: String? = nil, severity: String? = nil) async {
        // ✅ ИСПРАВЛЕНИЕ: Проверяем токен перед загрузкой
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("dark_web_error_unauthorized")
            return
        }
        
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
            // Очищаем ошибку при успешной загрузке
            errorMessage = nil
        } catch {
            // Проверяем тип ошибки - показываем только реальные проблемы
            let networkError = NetworkError.from(error)
            
            // ✅ ИСПРАВЛЕНИЕ: Обрабатываем ошибку авторизации отдельно
            if case .unauthorized = networkError {
                errorMessage = localizationManager.localized("dark_web_error_unauthorized")
                self.stats = nil
                self.leaks = []
                self.scans = []
                return
            }
            
            // Не показываем ошибку для 404 (нет данных - это нормально)
            if case .notFound = networkError {
                // Просто используем пустые данные, не показываем ошибку
                self.stats = nil
                self.leaks = []
                self.scans = []
                errorMessage = nil
                return
            }
            
            // Показываем понятные сообщения об ошибках
            if networkError.isCritical {
                let errorKey = "dark_web_error_critical"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else if case .notFound = networkError {
                // Для 404 показываем специальное сообщение
                errorMessage = localizationManager.localized("dark_web_error_service_unavailable")
            } else if !networkError.isRetryable {
                let errorKey = "dark_web_error_temporary"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для других ошибок показываем обобщенное сообщение
                errorMessage = localizationManager.localized("dark_web_error_try_later")
            }
            
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
    
    func startScan() async {
        // ✅ ИСПРАВЛЕНИЕ: Проверяем токен перед запуском сканирования
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("dark_web_error_unauthorized")
            return
        }
        
        isScanning = true
        errorMessage = nil
        defer { isScanning = false }
        
        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.startDarkWebScan { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            // Обновить данные после успешного запуска сканирования
            await loadData()
        } catch {
            let networkError = NetworkError.from(error)
            
            // ✅ ИСПРАВЛЕНИЕ: Обрабатываем ошибку авторизации отдельно
            if case .unauthorized = networkError {
                errorMessage = localizationManager.localized("dark_web_error_unauthorized")
                return
            }
            
            // ✅ ИСПРАВЛЕНИЕ: Правильная обработка ошибки "Ресурс не найден"
            if case .notFound = networkError {
                errorMessage = localizationManager.localized("dark_web_error_resource_not_found")
            } else if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "dark_web_error_scan_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для других ошибок показываем временную ошибку
                let errorKey = "dark_web_error_temporary"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    // MARK: - Hybrid Scan Methods
    
    func scanSecure(email: String?, password: String?) async {
        isScanning = true
        errorMessage = nil
        defer { isScanning = false }
        
        do {
            // Хешируем данные на клиенте
            var emailHash: String? = nil
            var passwordHash: String? = nil
            
            if let email = email, !email.isEmpty {
                let hash = SHA256.hash(data: email.data(using: .utf8)!)
                emailHash = hash.compactMap { String(format: "%02x", $0) }.joined()
            }
            
            if let password = password, !password.isEmpty {
                let hash = SHA256.hash(data: password.data(using: .utf8)!)
                passwordHash = hash.compactMap { String(format: "%02x", $0) }.joined()
            }
            
            guard emailHash != nil || passwordHash != nil else {
                errorMessage = localizationManager.localized("dark_web_scan_error_no_data")
                return
            }
            
            let response: APIResponse<[DarkWebScanResult]> = try await withCheckedThrowingContinuation { continuation in
                apiService.scanDarkWebSecure(
                    emailHash: emailHash,
                    passwordHash: passwordHash
                ) { result in
                    continuation.resume(with: result)
                }
            }
            
            // Преобразуем результаты в утечки
            let newLeaks = (response.data ?? []).compactMap { result -> DarkWebLeak? in
                guard result.found,
                      let leakDate = result.leakDate,
                      let dataType = LeakDataType(rawValue: result.dataType),
                      let severity = result.severity.flatMap({ LeakSeverity(rawValue: $0) }) else {
                    return nil
                }
                
                return DarkWebLeak(
                    id: result.id,
                    dataType: dataType,
                    value: "***", // Маскируем для безопасного сканирования
                    fullValue: nil,
                    leakDate: leakDate,
                    discoveryDate: Date(),
                    source: result.source ?? "Unknown",
                    severity: severity,
                    status: .new,
                    recommendations: result.recommendations ?? []
                )
            }
            
            // Добавляем новые утечки в начало списка
            self.leaks = newLeaks + self.leaks
            
            print("✅ DarkWebMonitoringViewModel.scanSecure: Найдено \(newLeaks.count) утечек")
            MasterLogger.shared.log(.info, category: .business, message: "✅ DarkWebMonitoringViewModel.scanSecure: Найдено \(newLeaks.count) утечек")
            
            // ✅ ИСПРАВЛЕНИЕ: Обновляем данные после успешного сканирования
            await loadData()
        } catch {
            let networkError = NetworkError.from(error)
            
            print("❌ DarkWebMonitoringViewModel.scanSecure: Ошибка сканирования: \(networkError.localizedDescription)")
            MasterLogger.shared.log(.error, category: .business, message: "❌ DarkWebMonitoringViewModel.scanSecure: Ошибка сканирования: \(networkError.localizedDescription)")
            
            // ✅ ИСПРАВЛЕНИЕ: Обрабатываем ошибку авторизации отдельно
            if case .unauthorized = networkError {
                errorMessage = localizationManager.localized("dark_web_error_unauthorized")
                return
            }
            
            // ✅ ИСПРАВЛЕНИЕ: Правильная обработка ошибки "Ресурс не найден"
            if case .notFound = networkError {
                errorMessage = localizationManager.localized("dark_web_error_resource_not_found")
            } else if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "dark_web_scan_error_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для других ошибок показываем временную ошибку
                let errorKey = "dark_web_error_temporary"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
    
    func scanFast(email: String?, phone: String?, passport: String?, snils: String?) async {
        print("⚡ DarkWebMonitoringViewModel.scanFast: Начало быстрого сканирования")
        MasterLogger.shared.log(.info, category: .business, message: "⚡ DarkWebMonitoringViewModel.scanFast: Начало быстрого сканирования")
        
        isScanning = true
        errorMessage = nil
        defer { 
            isScanning = false
            print("⚡ DarkWebMonitoringViewModel.scanFast: Сканирование завершено")
        }
        
        do {
            let response: APIResponse<[DarkWebScanResult]> = try await withCheckedThrowingContinuation { continuation in
                apiService.scanDarkWebFast(
                    email: email,
                    phone: phone,
                    passport: passport,
                    snils: snils
                ) { result in
                    continuation.resume(with: result)
                }
            }
            
            // Преобразуем результаты в утечки
            let newLeaks = (response.data ?? []).compactMap { result -> DarkWebLeak? in
                guard result.found,
                      let leakDate = result.leakDate,
                      let dataType = LeakDataType(rawValue: result.dataType),
                      let severity = result.severity.flatMap({ LeakSeverity(rawValue: $0) }) else {
                    return nil
                }
                
                return DarkWebLeak(
                    id: result.id,
                    dataType: dataType,
                    value: "***",
                    fullValue: email ?? phone ?? passport ?? snils,
                    leakDate: leakDate,
                    discoveryDate: Date(),
                    source: result.source ?? "Unknown",
                    severity: severity,
                    status: .new,
                    recommendations: result.recommendations ?? []
                )
            }
            
            // Добавляем новые утечки в начало списка
            self.leaks = newLeaks + self.leaks
            
            print("✅ DarkWebMonitoringViewModel.scanFast: Найдено \(newLeaks.count) утечек")
            MasterLogger.shared.log(.info, category: .business, message: "✅ DarkWebMonitoringViewModel.scanFast: Найдено \(newLeaks.count) утечек")
            
            // ✅ ИСПРАВЛЕНИЕ: Обновляем данные после успешного сканирования
            await loadData()
        } catch {
            let networkError = NetworkError.from(error)
            
            // ✅ ИСПРАВЛЕНИЕ: Обрабатываем ошибку авторизации отдельно
            if case .unauthorized = networkError {
                errorMessage = localizationManager.localized("dark_web_error_unauthorized")
                return
            }
            
            // ✅ ИСПРАВЛЕНИЕ: Правильная обработка ошибки "Ресурс не найден"
            if case .notFound = networkError {
                errorMessage = localizationManager.localized("dark_web_error_resource_not_found")
            } else if networkError.isCritical || !networkError.isRetryable {
                let errorKey = "dark_web_scan_error_failed"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            } else {
                // Для других ошибок показываем временную ошибку
                let errorKey = "dark_web_error_temporary"
                let errorFormat = localizationManager.localized(errorKey)
                errorMessage = String(format: errorFormat, networkError.localizedDescription)
            }
        }
    }
}

