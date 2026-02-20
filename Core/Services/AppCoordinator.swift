import SwiftUI
import Combine

/**
 * 🎯 APP COORDINATOR - Dependency Injection Container
 * Создает и предоставляет ViewModel'ы с реальными сервисами
 * Реализует паттерн Service Locator для MVVM архитектуры
 */
class AppCoordinator: ObservableObject {

    // MARK: - Singleton
    static let shared = AppCoordinator()

    // MARK: - Service Instances
    private let navigationManager = NavigationManager.shared
    private let localizationManager = LocalizationManager.shared
    private let notificationManager = NotificationManager.shared
    private let securityManager = SecurityManager.shared
    private let tariffManager = TariffManager.shared
    private let apiService = APIService.shared
    private let featuresManager = ProtectionFeaturesManager.shared
    private let toastManager = ToastManager.shared
    private let historyManager = ProtectionLevelHistoryManager.shared

    // MARK: - Service Adapters (Protocol Implementation)

    private lazy var navigationService: NavigationService = {
        NavigationServiceAdapter(navigationManager: navigationManager)
    }()

    private lazy var localizationService: LocalizationService = {
        LocalizationServiceAdapter(localizationManager: localizationManager)
    }()

    private lazy var notificationService: NotificationService = {
        NotificationServiceAdapter(notificationManager: notificationManager)
    }()

    private lazy var securityService: SecurityService = {
        SecurityServiceAdapter(securityManager: securityManager)
    }()

    private lazy var tariffService: TariffService = {
        TariffServiceAdapter(tariffManager: tariffManager)
    }()

    private lazy var apiServiceAdapter: APIService = {
        APIServiceAdapter(apiService: apiService)
    }()

    private lazy var positioningService: PositioningService = {
        PositioningServiceAdapter()
    }()

    private lazy var featuresService: ProtectionFeaturesService = {
        ProtectionFeaturesServiceAdapter(featuresManager: featuresManager)
    }()

    private lazy var toastService: ToastService = {
        ToastServiceAdapter(toastManager: toastManager)
    }()

    private lazy var historyService: ProtectionHistoryService = {
        ProtectionHistoryServiceAdapter(historyManager: historyManager)
    }()

    // MARK: - ViewModel Factories

    func makeSettingsViewModel() -> SettingsViewModel {
        return SettingsViewModel(
            navigationService: navigationService,
            localizationService: localizationService,
            notificationService: notificationService,
            securityService: securityService,
            tariffService: tariffService,
            apiService: apiServiceAdapter,
            positioningService: positioningService,
            featuresService: featuresService,
            toastService: toastService,
            historyService: historyService
        )
    }

    // MARK: - Screen Factories

    func makeSettingsScreen() -> SettingsScreen {
        let viewModel = makeSettingsViewModel()
        return SettingsScreen(viewModel: viewModel)
    }
}

// MARK: - Service Adapters

/**
 * 🔄 NAVIGATION SERVICE ADAPTER
 * Адаптер для NavigationManager -> NavigationService protocol
 */
class NavigationServiceAdapter: NavigationService {
    private let navigationManager: NavigationManager

    init(navigationManager: NavigationManager) {
        self.navigationManager = navigationManager
    }

    func navigateTo(_ screen: ALADDINScreen) {
        // Convert protocol enum to concrete enum if needed
        // For now, assume they are compatible
        navigationManager.navigateTo(screen as! ALADDINScreen)
    }

    func navigateToRoot(_ screen: ALADDINScreen) {
        navigationManager.navigateToRoot(screen as! ALADDINScreen)
    }

    func navigateToDevice(_ deviceId: String) {
        navigationManager.navigateToDevice(deviceId)
    }

    func navigateToProfile(_ userId: String) {
        navigationManager.navigateToProfile(userId)
    }

    func navigateToNotificationSettings() {
        navigationManager.navigateToNotificationSettings()
    }

    func navigateToLanguageSettings() {
        navigationManager.navigateToLanguageSettings()
    }
}

/**
 * 🌍 LOCALIZATION SERVICE ADAPTER
 * Адаптер для LocalizationManager -> LocalizationService protocol
 */
class LocalizationServiceAdapter: LocalizationService {
    private let localizationManager: LocalizationManager

    init(localizationManager: LocalizationManager) {
        self.localizationManager = localizationManager
    }

    var currentLanguage: Language {
        return localizationManager.currentLanguage
    }

    var languageChanged: AnyPublisher<Language, Never> {
        return localizationManager.languageChanged
    }

    func localized(_ key: String) -> String {
        return localizationManager.localized(key)
    }

    func localized(_ key: String, _ arguments: CVarArg...) -> String {
        return localizationManager.localized(key, arguments)
    }
}

/**
 * 🔔 NOTIFICATION SERVICE ADAPTER
 * Адаптер для NotificationManager -> NotificationService protocol
 */
class NotificationServiceAdapter: NotificationService {
    private let notificationManager: NotificationManager

    init(notificationManager: NotificationManager) {
        self.notificationManager = notificationManager
    }

    var notificationSettings: NotificationSettings {
        get { notificationManager.notificationSettings }
        set { notificationManager.notificationSettings = newValue }
    }

    func saveSettings() {
        notificationManager.saveSettings()
    }

    func requestAuthorization() async -> Bool {
        return await notificationManager.requestAuthorization()
    }

    func sendLocalNotification(title: String, body: String, userInfo: [AnyHashable : Any]?) {
        notificationManager.sendLocalNotification(title: title, body: body, userInfo: userInfo)
    }

    func updateNotificationSettings(_ settings: NotificationSettings) {
        notificationManager.updateNotificationSettings(settings)
    }
}

/**
 * 🔒 SECURITY SERVICE ADAPTER
 * Адаптер для SecurityManager -> SecurityService protocol
 */
class SecurityServiceAdapter: SecurityService {
    private let securityManager: SecurityManager

    init(securityManager: SecurityManager) {
        self.securityManager = securityManager
    }

    var biometricAuthAvailable: Bool {
        return securityManager.biometricAuthAvailable
    }

    func authenticateWithBiometrics() async -> Bool {
        return await securityManager.authenticateWithBiometrics()
    }
}

/**
 * 💰 TARIFF SERVICE ADAPTER
 * Адаптер для TariffManager -> TariffService protocol
 */
class TariffServiceAdapter: TariffService {
    private let tariffManager: TariffManager

    init(tariffManager: TariffManager) {
        self.tariffManager = tariffManager
    }

    var currentTariff: TariffType {
        return tariffManager.currentTariff
    }

    func createCard(localizationService: LocalizationService) -> TariffCard {
        // Create tariff card using real tariff data
        return TariffCard(type: currentTariff, localizationService: localizationService)
    }
}

/**
 * 🌐 API SERVICE ADAPTER
 * Адаптер для APIService -> APIService protocol
 */
class APIServiceAdapter: APIService {
    private let apiService: APIService

    init(apiService: APIService) {
        self.apiService = apiService
    }

    func getComponentsList(completion: @escaping (Result<[ComponentStatus], Error>) -> Void) {
        apiService.getComponentsList(completion: completion)
    }

    func enableComponent(componentId: String) async throws -> ComponentStatus {
        return try await apiService.enableComponent(componentId: componentId)
    }

    func disableComponent(componentId: String) async throws -> ComponentStatus {
        return try await apiService.disableComponent(componentId: componentId)
    }
}

/**
 * 📍 POSITIONING SERVICE ADAPTER
 * Простая реализация PositioningService
 */
class PositioningServiceAdapter: PositioningService {
    var currentSystem: PositioningSystem = .gps
    var selectedSystem: PositioningSystem = .gps
    var currentRegionName: String = "Russia"

    func saveSelectedSystem(_ system: PositioningSystem) {
        selectedSystem = system
        // Save to UserDefaults or other storage
        UserDefaults.standard.set(system.rawValue, forKey: "selected_positioning_system")
    }
}

/**
 * 🛡️ PROTECTION FEATURES SERVICE ADAPTER
 * Адаптер для ProtectionFeaturesManager
 */
class ProtectionFeaturesServiceAdapter: ProtectionFeaturesService {
    private let featuresManager: ProtectionFeaturesManager

    init(featuresManager: ProtectionFeaturesManager) {
        self.featuresManager = featuresManager
    }

    var features: [ProtectionFeature] {
        get { featuresManager.features }
        set { featuresManager.features = newValue }
    }

    func loadFeatures() {
        featuresManager.loadFeatures()
    }

    func toggleFeature(_ featureId: String, enabled: Bool) {
        featuresManager.toggleFeature(featureId, enabled: enabled)
    }

    func getFeaturesForLevel(_ level: Int) -> [ProtectionFeature] {
        return featuresManager.getFeaturesForLevel(level)
    }
}

/**
 * 🔔 TOAST SERVICE ADAPTER
 * Адаптер для ToastManager
 */
class ToastServiceAdapter: ToastService {
    private let toastManager: ToastManager

    init(toastManager: ToastManager) {
        self.toastManager = toastManager
    }

    func showToast(message: String, type: ToastType, duration: TimeInterval) {
        toastManager.showToast(message: message, type: type, duration: duration)
    }

    func hideToast() {
        toastManager.hideToast()
    }
}

/**
 * 📊 PROTECTION HISTORY SERVICE ADAPTER
 * Адаптер для ProtectionLevelHistoryManager
 */
class ProtectionHistoryServiceAdapter: ProtectionHistoryService {
    private let historyManager: ProtectionLevelHistoryManager

    init(historyManager: ProtectionLevelHistoryManager) {
        self.historyManager = historyManager
    }

    var history: [ProtectionLevelRecord] {
        return historyManager.history
    }

    func addRecord(level: Int, reason: String, timestamp: Date) {
        historyManager.addRecord(level: level, reason: reason, timestamp: timestamp)
    }

    func getRecentRecords(limit: Int) -> [ProtectionLevelRecord] {
        return historyManager.getRecentRecords(limit: limit)
    }

    func clearHistory() {
        historyManager.clearHistory()
    }
}

// MARK: - Type Aliases for Protocol Conformance
typealias ALADDINScreen = NavigationManager.ALADDINScreen
typealias Language = LocalizationManager.Language