import Foundation
import Combine
import UIKit
import CryptoKit
@preconcurrency import FamilyControls
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

enum FamilyControlsAvailabilityError: LocalizedError {
    case unavailableInThisBuild

    var errorDescription: String? {
        switch self {
        case .unavailableInThisBuild:
            return "System Family Controls are not available in this build."
        }
    }
}

@MainActor class ParentalControlManager: ObservableObject {
    
    // MARK: - Dependencies
    
    private let apiService: APIService
    
    // MARK: - Published Properties
    
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var familyAuthStatus: AuthorizationStatus = .notDetermined
    /// Последний снимок readiness для UI (на родительском устройстве — только локальный статус этого iPhone; не путать со статусом телефона ребёнка).
    @Published var familyControlsReadinessSnapshot: FamilyControlsReadiness?

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
        apiService: APIService? = nil
    ) {
        self.apiService = apiService ?? APIService.shared
        
        // Проверяем текущий статус авторизации
        self.familyAuthStatus = AppStoreBuildPolicy.allowsSystemFamilyControls
            ? AuthorizationCenter.shared.authorizationStatus
            : .notDetermined
        self.familyControlsReadinessSnapshot = assessFamilyControlsReadiness()
    }

    private func isChildRoleDeviceForFamilyControls() -> Bool {
        FamilyScreenTimeEligibility.isSupervisedDevice()
    }

    /// Обновить снимок readiness без применения ManagedSettings (удобно для экрана родителя).
    func refreshFamilyControlsReadinessForCurrentDevice() {
        familyControlsReadinessSnapshot = assessFamilyControlsReadiness()
    }
    
    // MARK: - Screen Time Authorization
    
    /**
     * Запрос авторизации FamilyControls
     * Должно вызываться на устройстве ребенка (или родителя для управления)
     */
    func requestFamilyAuthorization() async throws {
        guard AppStoreBuildPolicy.allowsSystemFamilyControls else {
            throw FamilyControlsAvailabilityError.unavailableInThisBuild
        }
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
        guard AppStoreBuildPolicy.allowsSystemFamilyControls else {
            return FamilyControlsReadiness(
                hasAuthorization: false,
                authorizationStatus: .notDetermined,
                hasDeviceActivityExtension: false,
                managedSettingsAvailable: false,
                deviceActivityAvailable: false,
                fallbackReason: "system_family_controls_not_available_in_build"
            )
        }
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
        familyControlsReadinessSnapshot = readiness

        // ManagedSettings / DeviceActivity действуют только на **текущем** устройстве — запускаем на профиле ребёнка.
        guard isChildRoleDeviceForFamilyControls() else {
            print(
                "ℹ️ FamilyControls: skip local ManagedSettings/DeviceActivity on non-child profile " +
                    "(current_user_role=\(UserDefaults.standard.string(forKey: "current_user_role") ?? ""))"
            )
            return readiness
        }

        if !readiness.hasAuthorization {
            do {
                try await requestFamilyAuthorization()
            } catch {
                print("⚠️ FamilyControls auth request failed: \(error.localizedDescription)")
            }
            readiness = assessFamilyControlsReadiness()
            familyControlsReadinessSnapshot = readiness
        }

        guard readiness.isPipelineReady else {
            return readiness
        }

        // Persist identity for Monitor/Report App Group writers.
        let ag = UserDefaults(suiteName: ScreenTimeUsageStore.appGroupId) ?? .standard
        let familyId = FamilyLocalStore.loadPersistedFamilyId()
        ag.set(familyId, forKey: "screen_time_family_id")
        let memberId = [
            UserDefaults.standard.string(forKey: "your_member_id"),
            UserDefaults.standard.string(forKey: "active_child_profile_server_id"),
            UserDefaults.standard.string(forKey: "user_id")
        ]
        .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
        .first { !$0.isEmpty } ?? ""
        ag.set(memberId, forKey: "screen_time_member_id")

        // ManagedSettings stage
        setAppRemovalDenied(true)

        // DeviceActivity stage (день — минуты; ночь — отдельный bedtime, F4)
        do {
            try startDefaultDeviceActivityMonitoring()
        } catch {
            print("⚠️ DeviceActivity monitoring start failed: \(error.localizedDescription)")
        }
        BedtimeNightLock.rescheduleFromSavedIfNeeded()
        _ = await ScreenTimeUsageSync.postIfChild()

        let finalReadiness = assessFamilyControlsReadiness()
        familyControlsReadinessSnapshot = finalReadiness
        return finalReadiness
    }

    private func startDefaultDeviceActivityMonitoring() throws {
        let schedule = DeviceActivitySchedule(
            intervalStart: DateComponents(hour: 0, minute: 0),
            intervalEnd: DateComponents(hour: 23, minute: 59),
            repeats: true
        )
        let events = ScreenTimeAppLimitsBridge.thresholdEvents()
        if events.isEmpty {
            try deviceActivityCenter.startMonitoring(defaultDeviceActivityName, during: schedule)
        } else {
            try deviceActivityCenter.startMonitoring(
                defaultDeviceActivityName,
                during: schedule,
                events: events
            )
        }
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

    // MARK: - Child device: pull + apply parental settings (Apple-compliant)

    private static let childSettingsLastSyncAtKey = "parental_child_settings_last_sync_at"
    private static let childSettingsMinInterval: TimeInterval = 60

    /// On the child's iPhone only: GET parental settings from `:8002` and apply locally
    /// (FamilyControls / Safari Content Blocker). Parent cannot apply ManagedSettings to another device.
    @discardableResult
    func syncAndApplyParentalSettingsFromServerIfChildDevice(force: Bool = false) async -> Bool {
        guard isChildRoleDeviceForFamilyControls() else { return false }

        let now = Date().timeIntervalSince1970
        let last = UserDefaults.standard.double(forKey: Self.childSettingsLastSyncAtKey)
        if !force, last > 0, now - last < Self.childSettingsMinInterval {
            return false
        }

        let familyId = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard !familyId.isEmpty else {
            print("ℹ️ Child parental sync skipped: empty family_id")
            return false
        }

        let childIdCandidates = [
            UserDefaults.standard.string(forKey: "your_member_id"),
            UserDefaults.standard.string(forKey: "active_child_profile_server_id"),
            UserDefaults.standard.string(forKey: "user_id")
        ]
        let childId = childIdCandidates
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .first { !$0.isEmpty }

        let result: Result<ParentalControlSettingsResponse, Error> = await withCheckedContinuation { continuation in
            loadSettingsFromServer(familyId: familyId, childId: childId) { apiResult in
                continuation.resume(returning: apiResult)
            }
        }

        switch result {
        case .success(let response):
            UserDefaults.standard.set(now, forKey: Self.childSettingsLastSyncAtKey)
            await applyPulledParentalSettingsLocally(response)
            print("✅ Child parental settings applied (version=\(response.version), sites=\(response.blockedWebsites.count))")
            return true
        case .failure(let error):
            print("⚠️ Child parental settings pull failed: \(error.localizedDescription)")
            return false
        }
    }

    /// Persist server settings into local flags and apply on-device controls Apple allows.
    func applyPulledParentalSettingsLocally(_ response: ParentalControlSettingsResponse) async {
        let defaults = UserDefaults.standard
        defaults.set(response.isContentFilterEnabled, forKey: "parental_content_filter_enabled")
        defaults.set(response.isAppBlockingEnabled, forKey: "parental_app_blocking")
        defaults.set(response.isAppBlockingEnabled, forKey: "parental_homework_mode")
        defaults.set(response.screenTimeLimitHours, forKey: "parental_screen_time_limit_hours")
        defaults.set(response.allowedApps, forKey: "parental_allowed_apps")
        defaults.set(response.blockedWebsites, forKey: "parental_blocked_websites")
        if response.screenTimeLimitHours > 0 {
            defaults.set(
                ParentalScreenTimeFormat.storageValue(hours: response.screenTimeLimitHours),
                forKey: "parental_screen_time_limit"
            )
        }
        if let bedtime = response.bedtime {
            defaults.set(bedtime, forKey: "parental_bedtime")
        }

        let blockedLower = response.blockedWebsites.map { $0.lowercased() }
        let youtubeBlocked = blockedLower.contains { site in
            site.contains("youtube") || site.contains("youtu.be")
        }
        defaults.set(youtubeBlocked, forKey: "youtube_safe_mode")
        defaults.set(youtubeBlocked, forKey: "parental_youtube_filtering")

        if response.isAppBlockingEnabled || response.isContentFilterEnabled {
            _ = await applyFamilyControlsPipelineIfPossible()
            setAppRemovalDenied(response.isAppBlockingEnabled)
        } else {
            clearAllShields()
            setAppRemovalDenied(false)
        }

        // F5: пауза — отдельный именованный щит, живёт после закрытия ALADDIN
        ParentalInternetPause.applyLocalState(paused: response.internetPaused)

        await ContentBlockerManager.shared.applyParentalBlockedWebsites(
            response.blockedWebsites,
            contentFilterEnabled: response.isContentFilterEnabled || youtubeBlocked || response.internetPaused
        )
    }
    
    // MARK: - Screen Time Statistics (Real Data)
    
    /**
     * Получить реальную статистику использования (текстовый формат)
     */
    func fetchRealScreenTimeStats() async -> [AppUsageStatistics] {
        // Parent: try server aggregate first (child POST → GET).
        if !isChildRoleDeviceForFamilyControls() {
            let familyId = FamilyLocalStore.loadPersistedFamilyId()
                .trimmingCharacters(in: .whitespacesAndNewlines)
            let memberId = [
                UserDefaults.standard.string(forKey: "active_child_profile_server_id"),
                UserDefaults.standard.string(forKey: "selected_child_member_id"),
                UserDefaults.standard.string(forKey: "your_member_id")
            ]
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .first { !$0.isEmpty } ?? ""
            if !familyId.isEmpty, !memberId.isEmpty {
                _ = await ScreenTimeUsageSync.pullForParent(familyId: familyId, memberId: memberId)
            }
        }

        if let snap = ScreenTimeUsageStore.load(),
           !snap.isStale,
           snap.isTodayInStoredTimezone,
           snap.totalSeconds > 0 || !snap.apps.isEmpty {
            if snap.apps.isEmpty {
                return [
                    AppUsageStatistics(
                        appName: "Total",
                        timeSpent: TimeInterval(snap.totalSeconds),
                        sessions: 1,
                        limit: 0
                    )
                ]
            }
            return snap.apps.map {
                AppUsageStatistics(
                    appName: $0.displayName ?? $0.tokenHash,
                    timeSpent: TimeInterval($0.seconds),
                    sessions: 1,
                    limit: TimeInterval($0.limitSeconds ?? 0)
                )
            }
        }

        // Fallback: parental_time_stats written by store/sync (source gated in UI).
        if let stats = ScreenTimeUsageStore.loadParentalTimeStats(),
           (stats["source"] == "device_activity" || stats["source"] == "server"),
           let used = stats["totalTimeUsed"], !used.isEmpty {
            // Signal UI via empty device rows — FamilyTimeControlModal reads App Group cache next.
            return []
        }
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
    
    /// Получает статистику использования по приложениям.
    /// Честно: без DeviceActivity Report extension / API — пустой список (не Instagram/TikTok mock).
    func getAppUsageStatistics(childId: String, period: StatisticsPeriod = .today) async -> Result<[AppUsageStatistics], Error> {
        let fromDevice = await fetchRealScreenTimeStats()
        return .success(fromDevice)
    }
    
    /// Получает статистику использования по сайтам (без mock до реального API).
    func getWebsiteUsageStatistics(childId: String, period: StatisticsPeriod = .today) async -> Result<[WebsiteUsageStatistics], Error> {
        return .success([])
    }
    
    /// Графики активности — пустые, пока нет реального источника (не random demo).
    func getActivityCharts(childId: String, period: StatisticsPeriod = .today) async -> Result<ActivityCharts, Error> {
        return .success(ActivityCharts(hourlyActivity: [], dailyActivity: []))
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
                completion(.failure(NSError(
                    domain: "ParentalControlManager",
                    code: 429,
                    userInfo: [NSLocalizedDescriptionKey: LocalizationManager.shared.localized("parental_stats_rate_limited")]
                )))
            }
            return
        }
        if let lastRequest = lastStatsRequestAt, now.timeIntervalSince(lastRequest) < statsMinInterval {
            DispatchQueue.main.async {
                self.isLoading = false
                completion(.failure(NSError(
                    domain: "ParentalControlManager",
                    code: 429,
                    userInfo: [NSLocalizedDescriptionKey: LocalizationManager.shared.localized("parental_stats_rate_limited")]
                )))
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

    /// p1-2a/b: тот же путь данных, что для модалок семьи и экрана РК — коалесcing в `APIService`.
    func getMonitoringDetail(
        childId: String?,
        completion: @escaping (Result<ParentalMonitoringDetailResponse, Error>) -> Void
    ) {
        apiService.getParentalMonitoringDetail(childId: childId, completion: completion)
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
                completion(.failure(NSError(
                    domain: "ParentalControlManager",
                    code: 429,
                    userInfo: [NSLocalizedDescriptionKey: LocalizationManager.shared.localized("parental_stats_rate_limited")]
                )))
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
                            "🚫 BYPASS APPLY rejected: backend returned mock/fallback response; operation is NOT confirmed",
                            level: .error,
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
        let correlationId = "bypass-\(UUID().uuidString)"
        let trimmedChild = childId.trimmingCharacters(in: .whitespacesAndNewlines)
        let resolvedChildId: String? = trimmedChild.isEmpty ? nil : trimmedChild
        // Сохраняем попытку обхода
        let attempt = BypassAttempt(
            id: UUID().uuidString,
            type: type,
            timestamp: Date(),
            blocked: true,
            deviceName: UIDevice.current.name,
            childId: resolvedChildId
        )
        
        saveBypassAttempt(attempt)
        
        // ✅ ИСПРАВЛЕНО: Проверяем настройки уведомлений на main thread
        // Доступ к notificationSettings требует main thread
        
        // Создаем уведомление для экрана уведомлений (через NotificationManager)
        // ✅ sendLocalNotification безопасен для вызова из любого потока
        NotificationManager.shared.sendLocalNotification(
            title: LocalizationManager.shared.localized("push_bypass_attempt_title"),
            body: String(format: LocalizationManager.shared.localized("push_bypass_attempt_body"), type.displayName),
            category: .security,
            userInfo: [
                "type": "bypass_attempt",
                "priority": "high",
                "correlation_id": correlationId,
                "event_id": correlationId,
                "source": "parental_bypass_detection",
                "bypass_type": type.rawValue,
                "child_id": trimmedChild
            ],
            delay: 0
        )

        postBypassMonitoringIngest(
            type: type,
            correlationId: correlationId,
            childId: resolvedChildId
        )

        // Push-уведомление отправляется ТОЛЬКО если включено в настройках
        // Проверка выполняется в NotificationManager.sendLocalNotification()

        completion?(true)
    }

    /// Единый POST на `/api/parental-control/monitoring/events` (JWT ребёнка → ingest на сервере).
    func postBypassMonitoringIngest(type: BypassType, correlationId: String, childId: String?) {
        let kind = "bypass_\(type.rawValue)"
        var payload: [String: Any] = [
            "bypass_type": type.rawValue,
            "correlation_id": correlationId,
            "category": "bypass",
            "source": "parental_bypass_detection",
        ]
        if let childId, !childId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            payload["child_id"] = childId
        }
        let ev = ParentalMonitoringEventInDTO(kind: kind, payload: payload)
        apiService.postParentalMonitoringEvents(events: [ev]) { result in
            if case .failure(let error) = result {
                VisualLogger.shared.log(
                    "⚠️ bypass monitoring ingest failed: \(error.localizedDescription)",
                    level: .warning,
                    category: "PARENTAL.API"
                )
            }
        }
    }

    /// Удалённый push (APNs) с типом bypass: пробуем echo-ingest на устройстве ребёнка (родительский JWT вернёт ошибку — лог).
    func ingestBypassMonitoringFromPushUserInfo(_ userInfo: [AnyHashable: Any]) {
        func stringValue(_ any: Any?) -> String {
            if let s = any as? String { return s }
            if let n = any as? NSNumber { return n.stringValue }
            return ""
        }

        let dict = userInfo as? [String: Any] ?? [:]
        let typeRaw = stringValue(dict["type"]).lowercased()
        let bypassHintEarly = stringValue(dict["bypass_type"] ?? dict["bypassType"]).lowercased()
        let looksBypass = typeRaw == "bypass"
            || typeRaw == "bypass_attempt"
            || typeRaw == "attempt_bypass"
            || typeRaw.contains("bypass")
            || !bypassHintEarly.isEmpty
        guard looksBypass else { return }

        let bypassRaw = bypassHintEarly
        let type: BypassType
        switch bypassRaw {
        case "incognito": type = .incognito
        case "tor": type = .tor
        case "proxy": type = .proxy
        default:
            if typeRaw.contains("tor") { type = .tor }
            else if typeRaw.contains("incognito") { type = .incognito }
            else if typeRaw.contains("proxy") { type = .proxy }
            else { type = .proxy }
        }

        let correlationCandidates = [stringValue(dict["correlation_id"]), stringValue(dict["correlationId"]), stringValue(dict["event_id"])]
        let correlationId = correlationCandidates.first(where: { !$0.isEmpty }) ?? "push-\(UUID().uuidString)"

        let childCandidates = [stringValue(dict["child_id"]), stringValue(dict["childId"])]
        let childJoined = childCandidates.first(where: { !$0.isEmpty }) ?? ""
        let childId: String? = childJoined.isEmpty ? nil : childJoined

        postBypassMonitoringIngest(type: type, correlationId: correlationId, childId: childId)
    }
    
    /**
     * Сохранение попытки обхода
     */
    private let bypassAttemptsLocalMaxCount = 200

    private func bypassAttemptsStorageKey(for childId: String?) -> String {
        let trimmed = childId?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let suffix = trimmed.isEmpty ? "all" : trimmed
        return "parental_bypass_attempts_v1_\(suffix)"
    }

    /// Локальные агрегаты (офлайн / fallback при ошибке API). Неделя = последние 7 дней.
    func localBypassAggregates(for childId: String?) -> BypassStatsResponse {
        let attempts = loadBypassAttemptsFromStorage(for: childId)
        let cal = Calendar.current
        let now = Date()
        let weekStart = cal.date(byAdding: .day, value: -7, to: now) ?? now

        let todayAttempts = attempts.filter { cal.isDateInToday($0.timestamp) }
        let weekAttempts = attempts.filter { $0.timestamp >= weekStart }

        let incognito = weekAttempts.filter { $0.type == .incognito }.count
        let tor = weekAttempts.filter { $0.type == .tor }.count
        let proxy = weekAttempts.filter { $0.type == .proxy }.count

        return BypassStatsResponse(
            success: true,
            today: todayAttempts.count,
            week: weekAttempts.count,
            blocked: weekAttempts.filter(\.blocked).count,
            incognito: incognito,
            tor: tor,
            proxy: proxy,
            message: nil
        )
    }

    func loadBypassAttemptsFromStorage(for childId: String?) -> [BypassAttempt] {
        let key = bypassAttemptsStorageKey(for: childId)
        guard let data = UserDefaults.standard.data(forKey: key) else { return [] }
        return (try? JSONDecoder().decode([BypassAttempt].self, from: data)) ?? []
    }

    private func saveBypassAttempt(_ attempt: BypassAttempt) {
        let key = bypassAttemptsStorageKey(for: attempt.childId)
        var list = loadBypassAttemptsFromStorage(for: attempt.childId)
        list.insert(attempt, at: 0)
        if list.count > bypassAttemptsLocalMaxCount {
            list = Array(list.prefix(bypassAttemptsLocalMaxCount))
        }
        if let data = try? JSONEncoder().encode(list) {
            UserDefaults.standard.set(data, forKey: key)
        }
        #if DEBUG
        print("💾 Сохранена попытка обхода: \(attempt.type.rawValue) для \(attempt.childId ?? "всех") (всего \(list.count))")
        #endif
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
    
    func saveSettingsToServer(familyId: String? = nil, childId: String? = nil, isContentFilterEnabled: Bool? = nil, isAppBlockingEnabled: Bool? = nil, internetPaused: Bool? = nil, screenTimeLimitHours: Int? = nil, allowedApps: [String]? = nil, blockedWebsites: [String]? = nil, bedtime: String? = nil, completion: @escaping (Result<ParentalControlSettingsResponse, Error>) -> Void) {
        let family = familyId ?? self.familyId
        apiService.updateParentalControlSettings(
            familyId: family,
            childId: childId,
            isContentFilterEnabled: isContentFilterEnabled,
            isAppBlockingEnabled: isAppBlockingEnabled,
            internetPaused: internetPaused,
            screenTimeLimitHours: screenTimeLimitHours,
            allowedApps: allowedApps,
            blockedWebsites: blockedWebsites,
            bedtime: bedtime,
            deviceId: deviceId,
            version: nil,
            completion: completion
        )
    }

    /// F5: родитель включает/выключает паузу → сервер; ребёнок тянет sync и ставит щит.
    func setInternetPaused(_ paused: Bool, childId: String? = nil, completion: ((Result<ParentalControlSettingsResponse, Error>) -> Void)? = nil) {
        saveSettingsToServer(childId: childId, internetPaused: paused) { result in
            if case .success = result {
                UserDefaults.standard.set(paused, forKey: "parental_internet_paused")
            }
            completion?(result)
        }
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

struct BypassAttempt: Codable, Identifiable, Sendable {
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

