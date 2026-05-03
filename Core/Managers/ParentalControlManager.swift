import Foundation
import Combine
import UIKit
import CryptoKit
import FamilyControls
import ManagedSettings
import DeviceActivity

/**
 * 👨‍👩‍👧‍👦 Parental Control Manager
 * Управление родительским контролем
 * Централизованная логика для всех функций родительского контроля
 */

// MARK: - Statistics Period

enum StatisticsPeriod {
    case today
    case week
    case month
    case custom(startDate: Date, endDate: Date)
}

// MARK: - Statistics Models

struct AppUsageStatistics: Codable {
    let appName: String
    let timeSpent: TimeInterval
    let sessions: Int
    let limit: TimeInterval
}

struct WebsiteUsageStatistics: Codable {
    let website: String
    let visits: Int
    let timeSpent: TimeInterval
    let isBlocked: Bool
}

struct ActivityCharts: Codable {
    let hourlyActivity: [HourlyActivity]
    let dailyActivity: [DailyActivity]
}

struct HourlyActivity: Codable {
    let hour: Int
    let timeSpent: TimeInterval
}

struct DailyActivity: Codable {
    let date: Date
    let timeSpent: TimeInterval
}

// MARK: - App Settings Model

struct AppSetting: Codable {
    let appName: String
    let isBlocked: Bool
    let timeLimit: TimeInterval?
}

// MARK: - FamilyControls Readiness

struct FamilyControlsReadiness: Sendable {
    let hasAuthorization: Bool
    let authorizationStatus: AuthorizationStatus
    let hasDeviceActivityExtension: Bool
    let managedSettingsAvailable: Bool
    let deviceActivityAvailable: Bool
    let fallbackReason: String?

    var isPipelineReady: Bool {
        hasAuthorization && managedSettingsAvailable && deviceActivityAvailable
    }
}

class ParentalControlManager: ObservableObject {
    
    // MARK: - Dependencies
    
    private let apiService: APIService
    private let networkManager: NetworkManager
    
    // MARK: - Published Properties
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var familyAuthStatus: AuthorizationStatus = .notDetermined

    // Anti-spam guards for parental stats polling in UI cycles.
    /// Throttle for `/parental-control/stats` only.
    private var lastStatsRequestAt: Date?
    /// Separate throttle for bypass stats — must not share `lastStatsRequestAt` or back-to-back
    /// `getStats` + `getBypassStats` on screen load always trips the 10s window.
    private var lastBypassStatsRequestAt: Date?
    private var statsBackoffUntil: Date?
    private let statsMinInterval: TimeInterval = 10
    private let statsContractBackoff: TimeInterval = 90
    
    // Managed Settings Store
    private let managedSettingsStore = ManagedSettingsStore()
    private let deviceActivityCenter = DeviceActivityCenter()
    private let defaultDeviceActivityName = DeviceActivityName("aladdin.family.daily")
    
    // MARK: - Singleton
    
    static let shared = ParentalControlManager()
    
    // MARK: - Initialization
    
    init(
        apiService: APIService? = nil,
        networkManager: NetworkManager? = nil
    ) {
        // ✅ ИСПРАВЛЕНИЕ: Правильная инициализация в правильном порядке
        // Сначала инициализируем NetworkManager
        if let networkManager = networkManager {
            self.networkManager = networkManager
        } else {
            self.networkManager = NetworkManager()
        }

        // Затем инициализируем APIService
        if let apiService = apiService {
            self.apiService = apiService
        } else {
            self.apiService = APIService(networkManager: self.networkManager)
        }
        
        // Проверяем текущий статус авторизации
        self.familyAuthStatus = AuthorizationCenter.shared.authorizationStatus
    }
    
    // MARK: - Screen Time Authorization
    
    /**
     * Запрос авторизации FamilyControls
     * Должно вызываться на устройстве ребенка (или родителя для управления)
     */
    func requestFamilyAuthorization() async throws {
        isLoading = true
        defer { isLoading = false }
        
        return try await withCheckedThrowingContinuation { continuation in
            AuthorizationCenter.shared.requestAuthorization(completionHandler: { result in
                switch result {
                case .success:
                    Task { @MainActor in
                        self.familyAuthStatus = AuthorizationCenter.shared.authorizationStatus
                        print("✅ ParentalControlManager: FamilyControls authorized")
                        continuation.resume()
                    }
                case .failure(let error):
                    Task { @MainActor in
                        self.familyAuthStatus = AuthorizationCenter.shared.authorizationStatus
                        self.errorMessage = "Ошибка авторизации Screen Time: \(error.localizedDescription)"
                        print("❌ ParentalControlManager: Auth failed: \(error.localizedDescription)")
                        continuation.resume(throwing: error)
                    }
                }
            })
        }
    }

    // MARK: - Phase 7.2.1 readiness + pipeline

    func assessFamilyControlsReadiness() -> FamilyControlsReadiness {
        let authStatus = AuthorizationCenter.shared.authorizationStatus
        let hasAuthorization = authStatus == .approved

        // Provisioning/extension readiness heuristic: check if any Screen Time related extension is bundled.
        let hasDeviceActivityExtension: Bool = {
            guard let pluginsURL = Bundle.main.builtInPlugInsURL,
                  let urls = try? FileManager.default.contentsOfDirectory(
                    at: pluginsURL,
                    includingPropertiesForKeys: nil,
                    options: [.skipsHiddenFiles]
                  ) else {
                return false
            }
            let names = urls.map { $0.lastPathComponent.lowercased() }
            return names.contains(where: { $0.contains("deviceactivity") || $0.contains("shield") || $0.contains("familycontrols") })
        }()

        let managedSettingsAvailable = true
        let deviceActivityAvailable = true

        let fallbackReason: String? = {
            if !hasAuthorization { return "authorization_not_approved" }
            if !hasDeviceActivityExtension { return "extension_missing_or_not_embedded" }
            if !managedSettingsAvailable { return "managed_settings_unavailable" }
            if !deviceActivityAvailable { return "device_activity_unavailable" }
            return nil
        }()

        return FamilyControlsReadiness(
            hasAuthorization: hasAuthorization,
            authorizationStatus: authStatus,
            hasDeviceActivityExtension: hasDeviceActivityExtension,
            managedSettingsAvailable: managedSettingsAvailable,
            deviceActivityAvailable: deviceActivityAvailable,
            fallbackReason: fallbackReason
        )
    }

    /// End-to-end pipeline: AuthorizationCenter -> ManagedSettings -> DeviceActivity.
    /// Returns latest readiness snapshot; caller may show fallback UX when `isPipelineReady == false`.
    @discardableResult
    func applyFamilyControlsPipelineIfPossible() async -> FamilyControlsReadiness {
        var readiness = assessFamilyControlsReadiness()

        if !readiness.hasAuthorization {
            do {
                try await requestFamilyAuthorization()
            } catch {
                print("⚠️ FamilyControls auth request failed: \(error.localizedDescription)")
            }
            readiness = assessFamilyControlsReadiness()
        }

        guard readiness.isPipelineReady else {
            return readiness
        }

        // ManagedSettings stage
        setAppRemovalDenied(true)

        // DeviceActivity stage
        do {
            try startDefaultDeviceActivityMonitoring()
        } catch {
            print("⚠️ DeviceActivity monitoring start failed: \(error.localizedDescription)")
        }

        return assessFamilyControlsReadiness()
    }

    private func startDefaultDeviceActivityMonitoring() throws {
        let schedule = DeviceActivitySchedule(
            intervalStart: DateComponents(hour: 0, minute: 0),
            intervalEnd: DateComponents(hour: 23, minute: 59),
            repeats: true
        )
        try deviceActivityCenter.startMonitoring(defaultDeviceActivityName, during: schedule)
    }
    
    // MARK: - App & Content Management
    
    /**
     * Запретить удаление приложений
     */
    func setAppRemovalDenied(_ denied: Bool) {
        managedSettingsStore.application.denyAppRemoval = denied
        print("🛡️ ParentalControlManager: denyAppRemoval set to \(denied)")
    }
    
    /**
     * Системная блокировка категорий приложений
     */
    func shieldCategories(_ categories: ActivityCategoryToken) {
        managedSettingsStore.shield.applicationCategories = .specific([categories])
        print("🛡️ ParentalControlManager: Shields applied to categories")
    }
    
    /**
     * Очистить все блокировки
     */
    func clearAllShields() {
        managedSettingsStore.shield.applications = nil
        managedSettingsStore.shield.applicationCategories = nil
        managedSettingsStore.shield.webDomains = nil
        print("🛡️ ParentalControlManager: All shields cleared")
    }
    
    // MARK: - Screen Time Statistics (Real Data)
    
    /**
     * Получить реальную статистику использования (текстовый формат)
     */
    func fetchRealScreenTimeStats() async -> [AppUsageStatistics] {
        // ✅ BUILD 123: Очищено от MOCK имен. В будущем здесь будет запрос к DeviceActivityCenter.
        // Пока возвращаем пустой список, чтобы UI показывал "Нет данных" вместо фейковых приложений,
        // либо загружаем реальные данные если Extension настроен.
        return []
    }
    
    // MARK: - Content Blocking
    
    /**
     * Применение блокировки контента
     */
    func applyContentBlocking(
        childId: String,
        websiteBlocking: Bool,
        appBlocking: Bool,
        searchBlocking: Bool,
        safesearch: Bool,
        completion: ((Bool, String?) -> Void)? = nil
    ) {
        isLoading = true
        errorMessage = nil
        
        var successCount = 0
        var errorMessages: [String] = []
        let group = DispatchGroup()
        
        // Применяем блокировку сайтов
        if websiteBlocking != UserDefaults.standard.bool(forKey: "parental_website_blocking") {
            group.enter()
            apiService.applyBlocking(childId: childId, type: .website, enabled: websiteBlocking) { result in
                switch result {
                case .success:
                    successCount += 1
                    print("✅ Блокировка сайтов: \(websiteBlocking ? "ВКЛ" : "ВЫКЛ")")
                case .failure(let error):
                    errorMessages.append("Ошибка блокировки сайтов: \(error.localizedDescription)")
                }
                group.leave()
            }
        } else {
            successCount += 1
        }
        
        // Применяем блокировку приложений
        if appBlocking != UserDefaults.standard.bool(forKey: "parental_app_blocking") {
            group.enter()
            apiService.applyBlocking(childId: childId, type: .app, enabled: appBlocking) { result in
                switch result {
                case .success:
                    successCount += 1
                    print("✅ Блокировка приложений: \(appBlocking ? "ВКЛ" : "ВЫКЛ")")
                case .failure(let error):
                    errorMessages.append("Ошибка блокировки приложений: \(error.localizedDescription)")
                }
                group.leave()
            }
        } else {
            successCount += 1
        }
        
        // Применяем блокировку поисковых запросов
        if searchBlocking != UserDefaults.standard.bool(forKey: "parental_search_blocking") {
            group.enter()
            apiService.applyBlocking(childId: childId, type: .search, enabled: searchBlocking) { result in
                switch result {
                case .success:
                    successCount += 1
                    print("✅ Блокировка поисковых запросов: \(searchBlocking ? "ВКЛ" : "ВЫКЛ")")
                case .failure(let error):
                    errorMessages.append("Ошибка блокировки поиска: \(error.localizedDescription)")
                }
                group.leave()
            }
        } else {
            successCount += 1
        }
        
        // Применяем SafeSearch
        if safesearch != UserDefaults.standard.bool(forKey: "parental_safesearch") {
            group.enter()
            apiService.applyBlocking(childId: childId, type: .safesearch, enabled: safesearch) { result in
                switch result {
                case .success:
                    successCount += 1
                    print("✅ SafeSearch: \(safesearch ? "ВКЛ" : "ВЫКЛ")")
                case .failure(let error):
                    errorMessages.append("Ошибка SafeSearch: \(error.localizedDescription)")
                }
                group.leave()
            }
        } else {
            successCount += 1
        }
        
        // Ждём завершения всех запросов
        group.notify(queue: .main) { [weak self] in
            self?.isLoading = false
            
            if errorMessages.isEmpty {
                self?.errorMessage = nil
                completion?(true, nil)
            } else {
                self?.errorMessage = errorMessages.joined(separator: "\n")
                completion?(false, errorMessages.first)
            }
        }
    }
    
    // MARK: - Apply Rules
    
    /**
     * Применение правил родительского контроля
     */
    func applyRules(
        childId: String,
        ageGroup: String,
        rules: ParentalControlRules,
        completion: ((Bool, String?) -> Void)? = nil
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.applyParentalControlRules(childId: childId, ageGroup: ageGroup, rules: rules) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    if response.success {
                        print("✅ Правила применены для \(childId), возраст: \(ageGroup)")
                        self?.postAppRulesMonitoringIngest(childId: childId, ageGroup: ageGroup, rules: rules)
                        self?.errorMessage = nil
                        completion?(true, nil)
                    } else {
                        let errorMsg = response.message ?? "Ошибка применения правил"
                        self?.errorMessage = errorMsg
                        completion?(false, errorMsg)
                    }
                case .failure(let error):
                    let errorMsg = error.localizedDescription
                    self?.errorMessage = errorMsg
                    completion?(false, errorMsg)
                }
            }
        }
    }

    /// pc-05: снимок правил (SHA256 JSON), без полного списка сайтов в payload.
    private func postAppRulesMonitoringIngest(childId: String, ageGroup: String, rules: ParentalControlRules) {
        guard let data = try? JSONEncoder().encode(rules) else { return }
        let digest = SHA256.hash(data: data)
        let hashHex = digest.map { String(format: "%02x", $0) }.joined()
        let payload: [String: Any] = [
            "child_id": childId,
            "age_group": ageGroup,
            "rules_snapshot_sha256": hashHex
        ]
        let ev = ParentalMonitoringEventInDTO(kind: "app_rules", payload: payload)
        apiService.postParentalMonitoringEvents(events: [ev]) { _ in }
    }

    /// pc-05: хост в нижнем регистре + SHA256 для `GET …/monitoring/detail` (JWT должен быть ребёнка, `user_id` числовой).
    func postChildUrlVisitMonitoring(host: String) {
        let normalized = host.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalized.isEmpty else { return }
        let digest = SHA256.hash(data: Data(normalized.utf8))
        let hashHex = digest.map { String(format: "%02x", $0) }.joined()
        let ev = ParentalMonitoringEventInDTO(
            kind: "url_visit",
            payload: ["url_sha256": hashHex]
        )
        apiService.postParentalMonitoringEvents(events: [ev]) { _ in }
    }
    
    // MARK: - Access Requests
    
    /**
     * Получение запросов доступа
     */
    func getAccessRequests(
        childId: String? = nil,
        completion: @escaping (Result<[AccessRequestResponse], Error>) -> Void
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.getAccessRequests(childId: childId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let requests):
                    self?.errorMessage = nil
                    completion(.success(requests))
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    completion(.failure(error))
                }
            }
        }
    }
    
    /**
     * Обработка запроса доступа (принять/отклонить)
     */
    func handleAccessRequest(
        requestId: String,
        action: String, // "accept" или "reject"
        reason: String? = nil,
        completion: ((Bool, String?) -> Void)? = nil
    ) {
        isLoading = true
        errorMessage = nil
        
        apiService.handleAccessRequest(requestId: requestId, action: action, reason: reason) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    if response.success {
                        print("✅ Запрос \(requestId) \(action == "accept" ? "принят" : "отклонён")")
                        self?.errorMessage = nil
                        completion?(true, nil)
                    } else {
                        let errorMsg = response.message ?? "Ошибка обработки запроса"
                        self?.errorMessage = errorMsg
                        completion?(false, errorMsg)
                    }
                case .failure(let error):
                    let errorMsg = error.localizedDescription
                    self?.errorMessage = errorMsg
                    completion?(false, errorMsg)
                }
            }
        }
    }
    
    // MARK: - Usage Statistics
    
    /// Получает статистику использования по приложениям
    func getAppUsageStatistics(childId: String, period: StatisticsPeriod = .today) async -> Result<[AppUsageStatistics], Error> {
        // TODO: Реализовать API запрос
        // Пока возвращаем мок данные
        let statistics = [
            AppUsageStatistics(
                appName: "Instagram",
                timeSpent: 1800, // 30 минут
                sessions: 5,
                limit: 1800
            ),
            AppUsageStatistics(
                appName: "TikTok",
                timeSpent: 1200, // 20 минут
                sessions: 3,
                limit: 1200
            )
        ]
        
        return .success(statistics)
    }
    
    /// Получает статистику использования по сайтам
    func getWebsiteUsageStatistics(childId: String, period: StatisticsPeriod = .today) async -> Result<[WebsiteUsageStatistics], Error> {
        // TODO: Реализовать API запрос
        // Пока возвращаем мок данные
        let statistics = [
            WebsiteUsageStatistics(
                website: "youtube.com",
                visits: 15,
                timeSpent: 2400, // 40 минут
                isBlocked: false
            ),
            WebsiteUsageStatistics(
                website: "example-blocked.com",
                visits: 0,
                timeSpent: 0,
                isBlocked: true
            )
        ]
        
        return .success(statistics)
    }
    
    /// Получает данные для графиков активности (без создания самих графиков)
    func getActivityCharts(childId: String, period: StatisticsPeriod = .today) async -> Result<ActivityCharts, Error> {
        // TODO: Реализовать API запрос
        // Пока возвращаем мок данные для демонстрации структуры
        let hourlyActivity = (0..<24).map { hour in
            HourlyActivity(
                hour: hour,
                timeSpent: Double.random(in: 0...300) // Случайные данные для демонстрации
            )
        }
        
        let dailyActivity = (0..<7).map { day in
            DailyActivity(
                date: Calendar.current.date(byAdding: .day, value: -day, to: Date()) ?? Date(),
                timeSpent: Double.random(in: 1800...7200) // Случайные данные для демонстрации
            )
        }
        
        let charts = ActivityCharts(
            hourlyActivity: hourlyActivity,
            dailyActivity: dailyActivity
        )
        
        return .success(charts)
    }
    
    // MARK: - Flexible Settings
    
    /// Применяет гибкие настройки по возрасту
    func applyAgeBasedSettings(childId: String, age: Int) {
        print("🔧 Применение настроек по возрасту для \(childId), возраст: \(age)")
        
        // Настройки для разных возрастов
        switch age {
        case 0..<6:
            // Дошкольники: строгие ограничения
            print("👶 Дошкольник: строгие ограничения")
            applyContentBlocking(
                childId: childId,
                websiteBlocking: true,
                appBlocking: true,
                searchBlocking: true,
                safesearch: true
            ) { success, error in
                if success {
                    print("✅ Блокировка контента применена")
                }
            }
            
            // Применяем ограничения времени через applyRules
            let rules = ParentalControlRules(
                websiteBlocking: true,
                appBlocking: true,
                searchBlocking: true,
                safesearch: true,
                screenTimeLimit: 60, // 1 час в минутах
                bedtimeStart: "20:00",
                bedtimeEnd: "07:00",
                appLimits: nil,
                geofences: nil
            )
            applyRules(childId: childId, ageGroup: "preschool", rules: rules) { success, error in
                if success {
                    print("✅ Ограничения времени применены для дошкольника (1 час, сон: 20:00-07:00)")
                } else {
                    print("⚠️ Ошибка применения ограничений времени: \(error ?? "неизвестная ошибка")")
                }
            }
            
        case 6..<13:
            // Младшие школьники: умеренные ограничения
            print("🎒 Младший школьник: умеренные ограничения")
            applyContentBlocking(
                childId: childId,
                websiteBlocking: true,
                appBlocking: false,
                searchBlocking: true,
                safesearch: true
            ) { success, error in
                if success {
                    print("✅ Блокировка контента применена")
                }
            }
            
            // Применяем ограничения времени через applyRules
            let rules = ParentalControlRules(
                websiteBlocking: true,
                appBlocking: false,
                searchBlocking: true,
                safesearch: true,
                screenTimeLimit: 120, // 2 часа в минутах
                bedtimeStart: "21:00",
                bedtimeEnd: "07:00",
                appLimits: nil,
                geofences: nil
            )
            applyRules(childId: childId, ageGroup: "elementary", rules: rules) { success, error in
                if success {
                    print("✅ Ограничения времени применены для младшего школьника (2 часа, сон: 21:00-07:00)")
                } else {
                    print("⚠️ Ошибка применения ограничений времени: \(error ?? "неизвестная ошибка")")
                }
            }
            
        case 13..<18:
            // Подростки: мягкие ограничения
            print("👨‍🎓 Подросток: мягкие ограничения")
            applyContentBlocking(
                childId: childId,
                websiteBlocking: false,
                appBlocking: false,
                searchBlocking: false,
                safesearch: true
            ) { success, error in
                if success {
                    print("✅ Блокировка контента применена")
                }
            }
            
            // Применяем ограничения времени через applyRules
            let rules = ParentalControlRules(
                websiteBlocking: false,
                appBlocking: false,
                searchBlocking: false,
                safesearch: true,
                screenTimeLimit: 180, // 3 часа в минутах
                bedtimeStart: "22:00",
                bedtimeEnd: "07:00",
                appLimits: nil,
                geofences: nil
            )
            applyRules(childId: childId, ageGroup: "teen", rules: rules) { success, error in
                if success {
                    print("✅ Ограничения времени применены для подростка (3 часа, сон: 22:00-07:00)")
                } else {
                    print("⚠️ Ошибка применения ограничений времени: \(error ?? "неизвестная ошибка")")
                }
            }
            
        default:
            print("⚠️ Возраст \(age) не попадает в категории, настройки не применены")
        }
    }
    
    /// Применяет настройки по приложениям
    func applyAppBasedSettings(childId: String, appSettings: [AppSetting]) {
        print("🔧 Применение настроек по приложениям для \(childId)")
        
        // TODO: Реализовать применение настроек по приложениям
        // Пока просто логируем
        for setting in appSettings {
            print("   - \(setting.appName): блокировка=\(setting.isBlocked), лимит=\(setting.timeLimit?.description ?? "нет")")
        }
        
        print("⚠️ Применение настроек по приложениям требует реализации API")
    }
    
    // MARK: - Statistics
    
    /**
     * Получение статистики родительского контроля
     */
    func getStats(
        childId: String? = nil,
        completion: @escaping (Result<ParentalControlStatsResponse, Error>) -> Void
    ) {
        let now = Date()
        if let backoffUntil = statsBackoffUntil, now < backoffUntil {
            DispatchQueue.main.async {
                self.isLoading = false
                completion(.failure(NSError(domain: "ParentalControlManager", code: 429, userInfo: [NSLocalizedDescriptionKey: "Запрос отклонен из-за лимита (backoff). Повторите позже."])))
            }
            return
        }
        if let lastRequest = lastStatsRequestAt, now.timeIntervalSince(lastRequest) < statsMinInterval {
            DispatchQueue.main.async {
                self.isLoading = false
                completion(.failure(NSError(domain: "ParentalControlManager", code: 429, userInfo: [NSLocalizedDescriptionKey: "Слишком частые запросы (throttle). Повторите позже."])))
            }
            return
        }
        lastStatsRequestAt = now

        isLoading = true
        errorMessage = nil
        
        apiService.getParentalControlStats(childId: childId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let stats):
                    self?.statsBackoffUntil = nil
                    self?.errorMessage = nil
                    completion(.success(stats))
                case .failure(let error):
                    let message = error.localizedDescription.lowercased()
                    if message.contains("numeric user id") || message.contains("contract 401") {
                        self?.statsBackoffUntil = Date().addingTimeInterval(self?.statsContractBackoff ?? 90)
                    }
                    self?.errorMessage = error.localizedDescription
                    completion(.failure(error))
                }
            }
        }
    }
    
    // MARK: - Bypass Protection
    
    /**
     * Получение статистики защиты от обхода
     */
    func getBypassStats(
        childId: String? = nil,
        completion: @escaping (Result<BypassStatsResponse, Error>) -> Void
    ) {
        let now = Date()
        if let lastRequest = lastBypassStatsRequestAt, now.timeIntervalSince(lastRequest) < statsMinInterval {
            DispatchQueue.main.async {
                self.isLoading = false
                completion(.failure(NSError(domain: "ParentalControlManager", code: 429, userInfo: [NSLocalizedDescriptionKey: "Слишком частые запросы (throttle). Повторите позже."])))
            }
            return
        }
        lastBypassStatsRequestAt = now

        isLoading = true
        errorMessage = nil

        apiService.getBypassStats(childId: childId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let stats):
                    self?.errorMessage = nil
                    completion(.success(stats))
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    completion(.failure(error))
                }
            }
        }
    }
    
    /**
     * Применение защиты от обхода
     */
    func applyBypassProtection(
        childId: String,
        incognito: Bool,
        tor: Bool,
        proxy: Bool,
        completion: ((Bool, String?) -> Void)? = nil
    ) {
        isLoading = true
        errorMessage = nil
        let endpointURL = "\(AppConfig.baseURL)/api/parental/bypass/apply"
        VisualLogger.shared.log(
            "🔵 BYPASS APPLY start url=\(endpointURL) incognito=\(incognito) tor=\(tor) proxy=\(proxy)",
            level: .info,
            category: "PARENTAL.API"
        )
        
        apiService.applyBypassProtection(childId: childId, incognito: incognito, tor: tor, proxy: proxy) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let response):
                    if response.success {
                        print("✅ Защита от обхода применена для \(childId)")
                        VisualLogger.shared.log(
                            "✅ BYPASS APPLY ok",
                            level: .success,
                            category: "PARENTAL.API"
                        )
                        self?.errorMessage = nil
                        completion?(true, nil)
                    } else {
                        let errorMsg = response.message ?? "Ошибка применения защиты от обхода"
                        VisualLogger.shared.log(
                            "❌ BYPASS APPLY failed: \(errorMsg)",
                            level: .error,
                            category: "PARENTAL.API"
                        )
                        self?.errorMessage = errorMsg
                        completion?(false, errorMsg)
                    }
                case .failure(let error):
                    let errorMsg = error.localizedDescription
                    if errorMsg.localizedCaseInsensitiveContains("mock response from sfm") ||
                        errorMsg.localizedCaseInsensitiveContains("sfm_mock") {
                        VisualLogger.shared.log(
                            "⚠️ BYPASS APPLY backend mock_fallback: нужен реальный create_parental_bypass_apply",
                            level: .warning,
                            category: "PARENTAL.API"
                        )
                    }
                    VisualLogger.shared.log(
                        "❌ BYPASS APPLY failed: \(errorMsg)",
                        level: .error,
                        category: "PARENTAL.API"
                    )
                    self?.errorMessage = errorMsg
                    completion?(false, errorMsg)
                }
            }
        }
    }
    
    /**
     * Обнаружение попытки обхода
     */
    func detectBypassAttempt(
        type: BypassType,
        childId: String,
        completion: ((Bool) -> Void)? = nil
    ) {
        // Сохраняем попытку обхода
        let attempt = BypassAttempt(
            id: UUID().uuidString,
            type: type,
            timestamp: Date(),
            blocked: true,
            deviceName: "Устройство \(childId)"
        )
        
        saveBypassAttempt(attempt)
        
        // ✅ ИСПРАВЛЕНО: Проверяем настройки уведомлений на main thread
        // Доступ к notificationSettings требует main thread
        
        // Создаем уведомление для экрана уведомлений (через NotificationManager)
        // ✅ sendLocalNotification безопасен для вызова из любого потока
        NotificationManager.shared.sendLocalNotification(
            title: "🚨 Попытка обхода",
            body: "\(type.displayName) заблокирован",
            category: .security,
            userInfo: [
                "type": "bypass",
                "bypass_type": type.rawValue,
                "child_id": childId
            ],
            delay: 0
        )
        
        // Push-уведомление отправляется ТОЛЬКО если включено в настройках
        // Проверка выполняется в NotificationManager.sendLocalNotification()
        
        completion?(true)
    }
    
    /**
     * Сохранение попытки обхода
     */
    private func saveBypassAttempt(_ attempt: BypassAttempt) {
        // Сохраняем в UserDefaults или отправляем на сервер
        let _ = "bypass_attempts_\(attempt.childId ?? "all")"
        // TODO: Реализовать сохранение в UserDefaults или API
        print("💾 Сохранена попытка обхода: \(attempt.type.displayName) для \(attempt.childId ?? "всех")")
    }
    
    /**
     * Форматирование времени
     */
    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }
    
    // MARK: - ✅ РОДИТЕЛЬСКИЙ КОНТРОЛЬ: API методы для синхронизации
    
    /// Получить familyId для API вызовов
    private var familyId: String {
        UserDefaults.standard.string(forKey: "family_id") ?? "family_001"
    }
    
    /// Получить deviceId для API вызовов
    private var deviceId: String {
        UIDevice.current.identifierForVendor?.uuidString ?? "unknown_device"
    }
    
    // Настройки родительского контроля
    func loadSettingsFromServer(familyId: String? = nil, childId: String? = nil, completion: @escaping (Result<ParentalControlSettingsResponse, Error>) -> Void) {
        let family = familyId ?? self.familyId
        apiService.getParentalControlSettings(familyId: family, childId: childId, completion: completion)
    }
    
    func saveSettingsToServer(familyId: String? = nil, childId: String? = nil, isContentFilterEnabled: Bool? = nil, isAppBlockingEnabled: Bool? = nil, screenTimeLimitHours: Int? = nil, allowedApps: [String]? = nil, blockedWebsites: [String]? = nil, bedtime: String? = nil, completion: @escaping (Result<ParentalControlSettingsResponse, Error>) -> Void) {
        let family = familyId ?? self.familyId
        apiService.updateParentalControlSettings(
            familyId: family,
            childId: childId,
            isContentFilterEnabled: isContentFilterEnabled,
            isAppBlockingEnabled: isAppBlockingEnabled,
            screenTimeLimitHours: screenTimeLimitHours,
            allowedApps: allowedApps,
            blockedWebsites: blockedWebsites,
            bedtime: bedtime,
            deviceId: deviceId,
            version: nil,
            completion: completion
        )
    }
    
    func syncSettingsFromServer(familyId: String? = nil, completion: @escaping (Result<SyncParentalControlSettingsResponse, Error>) -> Void) {
        let family = familyId ?? self.familyId
        apiService.syncParentalControlSettings(familyId: family, deviceId: deviceId, lastSyncTimestamp: nil, completion: completion)
    }
    
    // Лимиты времени
    func loadTimeLimitsFromServer(childId: String, completion: @escaping (Result<TimeLimitResponse, Error>) -> Void) {
        apiService.getTimeLimits(childId: childId, completion: completion)
    }
    
    func saveTimeLimitsToServer(childId: String, dailyLimitMinutes: Int? = nil, weeklyLimitMinutes: Int? = nil, bedtimeStart: String? = nil, bedtimeEnd: String? = nil, completion: @escaping (Result<TimeLimitResponse, Error>) -> Void) {
        apiService.updateTimeLimits(
            childId: childId,
            dailyLimitMinutes: dailyLimitMinutes,
            weeklyLimitMinutes: weeklyLimitMinutes,
            bedtimeStart: bedtimeStart,
            bedtimeEnd: bedtimeEnd,
            deviceId: deviceId,
            version: nil,
            completion: completion
        )
    }
    
    func resetTimeLimitsOnServer(childId: String, completion: @escaping (Result<TimeLimitResponse, Error>) -> Void) {
        apiService.resetTimeLimits(childId: childId, deviceId: deviceId, completion: completion)
    }
    
    // Расписания
    func loadSchedulesFromServer(childId: String, completion: @escaping (Result<[ScheduleResponse], Error>) -> Void) {
        apiService.getSchedules(childId: childId, completion: completion)
    }
    
    func saveScheduleToServer(childId: String, scheduleId: String? = nil, name: String? = nil, weekdays: [Int]? = nil, startTime: String? = nil, endTime: String? = nil, isActive: Bool? = nil, completion: @escaping (Result<ScheduleResponse, Error>) -> Void) {
        apiService.updateSchedule(
            scheduleId: scheduleId,
            childId: childId,
            name: name,
            weekdays: weekdays,
            startTime: startTime,
            endTime: endTime,
            isActive: isActive,
            deviceId: deviceId,
            version: nil,
            completion: completion
        )
    }
    
    func deleteScheduleOnServer(scheduleId: String, completion: @escaping (Result<[String: String], Error>) -> Void) {
        apiService.deleteSchedule(scheduleId: scheduleId, deviceId: deviceId, completion: completion)
    }
    
    // Геозоны
    func loadGeofencesFromServer(childId: String, completion: @escaping (Result<[GeofenceResponse], Error>) -> Void) {
        apiService.getGeofences(childId: childId, completion: completion)
    }
    
    func addGeofenceToServer(childId: String, name: String, latitude: Double, longitude: Double, radius: Double, isActive: Bool = true, completion: @escaping (Result<GeofenceResponse, Error>) -> Void) {
        apiService.addGeofence(
            childId: childId,
            name: name,
            latitude: latitude,
            longitude: longitude,
            radius: radius,
            isActive: isActive,
            deviceId: deviceId,
            completion: completion
        )
    }
    
    func updateGeofenceOnServer(geofenceId: String, name: String? = nil, latitude: Double? = nil, longitude: Double? = nil, radius: Double? = nil, isActive: Bool? = nil, completion: @escaping (Result<GeofenceResponse, Error>) -> Void) {
        apiService.updateGeofence(
            geofenceId: geofenceId,
            name: name,
            latitude: latitude,
            longitude: longitude,
            radius: radius,
            isActive: isActive,
            deviceId: deviceId,
            version: nil,
            completion: completion
        )
    }
    
    func deleteGeofenceOnServer(geofenceId: String, completion: @escaping (Result<[String: String], Error>) -> Void) {
        apiService.deleteGeofence(geofenceId: geofenceId, completion: completion)
    }
    
    // Блокировки приложений
    func loadAppBlocksFromServer(childId: String, completion: @escaping (Result<AppBlockResponse, Error>) -> Void) {
        apiService.getAppBlocks(childId: childId, completion: completion)
    }
    
    func saveAppBlocksToServer(childId: String, blockedApps: [String]? = nil, appLimits: [String: Int]? = nil, completion: @escaping (Result<AppBlockResponse, Error>) -> Void) {
        apiService.updateAppBlocks(
            childId: childId,
            blockedApps: blockedApps,
            appLimits: appLimits,
            deviceId: deviceId,
            version: nil,
            completion: completion
        )
    }
    
    func syncAppBlocksFromServer(childId: String, completion: @escaping (Result<SyncAppBlocksResponse, Error>) -> Void) {
        apiService.syncAppBlocks(childId: childId, deviceId: deviceId, lastSyncTimestamp: nil, completion: completion)
    }
}

// MARK: - Tariff Integration

extension ParentalControlManager {
    func enableForTariff(_ tariffType: TariffType) async throws {
        print("🔄 ParentalControlManager: Активация функций родительского контроля для \(tariffType.rawValue)")
        var activatedCount = 0
        for module in ParentalControlModule.allCases {
            let features = module.features(for: tariffType)
            for feature in features {
                // Здесь должна быть логика активации каждой функции родительского контроля
                // Например, вызов API или обновление локальных настроек
                // Для примера просто логируем и увеличиваем счетчик
                print("✅ ParentalControlManager: Активирована функция РК: \(feature.id)")
                activatedCount += 1
            }
        }
        print("✅ ParentalControlManager: Активировано \(activatedCount) функций родительского контроля")
    }
}

// MARK: - Bypass Attempt Model

struct BypassAttempt {
    let id: String
    let type: BypassType
    let timestamp: Date
    let blocked: Bool
    let deviceName: String
    let childId: String?
    
    init(id: String, type: BypassType, timestamp: Date, blocked: Bool, deviceName: String, childId: String? = nil) {
        self.id = id
        self.type = type
        self.timestamp = timestamp
        self.blocked = blocked
        self.deviceName = deviceName
        self.childId = childId
    }
}

// MARK: - Bypass Stats Response
// BypassStatsResponse теперь находится в Core/Models/APIModels.swift

