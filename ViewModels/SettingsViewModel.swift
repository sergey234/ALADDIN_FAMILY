import SwiftUI
import Combine

// Temporary protocols and implementations for compilation
protocol ProtectionFeaturesService {
    var features: [String] { get set }
    func loadFeatures()
    func toggleFeature(_ featureId: String, enabled: Bool)
    func getFeaturesForLevel(_ level: Int) -> [String]
}

protocol ToastService {
    func showToast(message: String, type: String, duration: TimeInterval)
    func hideToast()
}

protocol ProtectionHistoryService {
    var history: [String] { get }
    func addRecord(level: Int, reason: String, timestamp: Date)
    func getRecentRecords(limit: Int) -> [String]
    func clearHistory()
}

// Temporary implementations for compilation
class MockProtectionFeaturesService: ProtectionFeaturesService {
    var features: [String] = []
    func loadFeatures() {}
    func toggleFeature(_ featureId: String, enabled: Bool) {}
    func getFeaturesForLevel(_ level: Int) -> [String] { [] }
}

class MockToastService: ToastService {
    func showToast(message: String, type: String, duration: TimeInterval) {}
    func hideToast() {}
}

class MockProtectionHistoryService: ProtectionHistoryService {
    var history: [String] = []
    func addRecord(level: Int, reason: String, timestamp: Date) {}
    func getRecentRecords(limit: Int) -> [String] { [] }
    func clearHistory() {}
}

// Local TariffType enum for compilation
// Import TariffType from TariffsScreen for compatibility
// We'll use TariffType instead of creating duplicate enum

protocol NavigationService {
    func navigateTo(_ screen: ALADDINScreen)
}

protocol LocalizationService {
    var currentLanguage: Language { get }
    func localized(_ key: String) -> String
}

protocol NotificationService {
    var notificationSettings: NotificationSettings { get set }
    func saveSettings()
    func requestAuthorization() async -> Bool
    func sendLocalNotification(title: String, body: String, userInfo: [AnyHashable: Any]?)
    func updateNotificationSettings(_ settings: NotificationSettings)
}

protocol SecurityService {
    var biometricAuthAvailable: Bool { get }
    func authenticateWithBiometrics() async -> Bool
}

protocol TariffService {
    var currentTariff: TariffType { get }
}

protocol SettingsAPIService {
    func getComponentsList(completion: @escaping (Result<[ComponentStatus], Error>) -> Void)
    func enableComponent(componentId: String) async throws -> ComponentStatus
    func disableComponent(componentId: String) async throws -> ComponentStatus
}

protocol PositioningService {
    var currentSystem: PositioningSystem { get }
    var selectedSystem: PositioningSystem { get set }
    func saveSelectedSystem(_ system: PositioningSystem)
}

// MARK: - Temporary LocalizedStrings for compilation
struct LocalizedStrings {
    // Navigation & Common
    let settingsTitle: String = "Настройки"
    let settingsSubtitle: String = "Управление приложением"
    let settingsAccessibilityBackground: String = "Фон настроек"
    let settingsAccessibilityList: String = "Список настроек"
    let settingsAccessibilityNavbar: String = "Панель навигации настроек"

    // Profile Section
    let profileSection: String = "Профиль"
    let profileNamePlaceholder: String = "Имя"
    let profileEmailPlaceholder: String = "Email"
    let profileStatus: String = "Активен"
    let profileAvatarAccessibility: String = "Аватар профиля"
    let profileNameAccessibilityFormat: String = "Имя: %@"
    let profileEmailAccessibilityFormat: String = "Email: %@"
    let profileStatusAccessibilityFormat: String = "Статус: %@"
    let settingsProfileEditAccessibility: String = "Редактировать профиль"

    // Security Section
    let securitySection: String = "Безопасность"
    let networkProtectionProtection: String = "Защита сети"
    let networkProtectionProtectionSubtitle: String = "Защита от сетевых угроз"
    let biometricAuth: String = "Биометрия"
    let biometricAuthSubtitle: String = "Отпечаток пальца / Face ID"
    let protectionLevel: String = "Уровень защиты"
    let settingsProtectionLevelValueFormat: String = "Уровень: %d%%"
    let settingsProtectionLevel: String = "Защита"
    let settingsProtectionHistory: String = "История"
    let settingsAdvancedSettings: String = "Расширенные настройки"
    let settingsImproveProtection: String = "Улучшить защиту"
    let settingsProtectionLevelAccessibility: String = "Уровень защиты"

    // Protection level texts
    let protectionLevelLow: String = "Низкий"
    let protectionLevelMedium: String = "Средний"
    let protectionLevelHigh: String = "Высокий"
    let protectionLevelMaximum: String = "Максимальный"

    // Notifications Section
    let notificationsSection: String = "Уведомления"
    let pushNotifications: String = "Push уведомления"
    let pushNotificationsSubtitle: String = "Важные оповещения"
    let soundNotifications: String = "Звуковые уведомления"
    let soundNotificationsSubtitle: String = "Звук уведомлений"

    // App Section
    let appSection: String = "Приложение"
    let language: String = "Язык"
    let languageSubtitle: String = "Выберите язык"
    let darkTheme: String = "Тема"
    let updates: String = "Обновления"
    let updatesSubtitle: String = "Проверить обновления"

    // System Components
    let systemComponentsTitle: String = "Системные компоненты"
    let retry: String = "Повторить"
    let systemComponentsEmpty: String = "Компоненты не найдены"
    let systemComponentsLastUpdate: String = "Последнее обновление"

    // Additional Section
    let additionalSection: String = "Дополнительно"
    let helpSupport: String = "Помощь и поддержка"
    let helpSupportSubtitle: String = "Связаться с поддержкой"
    let privacyPolicy: String = "Политика конфиденциальности"
    let privacyPolicySubtitle: String = "Узнать о приватности"
    let termsOfService: String = "Условия использования"
    let termsOfServiceSubtitle: String = "Правила использования"
    let shareApp: String = "Поделиться приложением"
    let shareAppSubtitle: String = "Рекомендовать друзьям"
    let settingsShareMessage: String = "Попробуйте ALADDIN - лучшее приложение для защиты!"

    // Biometric notifications
    let biometricEnabled: String = "Биометрия включена"
    let biometricDisabled: String = "Биометрия отключена"
    let biometricEnableFailed: String = "Не удалось включить биометрию"
    let biometricUnavailable: String = "Биометрия недоступна"

}

class SettingsViewModel: ObservableObject {

    // MARK: - Published Properties (23 @State variables migrated from View)

    // Network & Security
    @Published var isNetworkProtectionEnabled: Bool = true
    @Published var isBiometricEnabled: Bool = false

    // Profile Data
    @Published var displayName: String = ""
    @Published var displayAlias: String = ""

    // Notifications
    @Published var isNotificationsEnabled: Bool = true
    @Published var securityEnabled: Bool = false
    @Published var soundEnabled: Bool = false

    // UI State - Modals
    @Published var showProfileEdit: Bool = false
    @Published var showLanguageSettings: Bool = false
    @Published var showSupportScreen: Bool = false
    @Published var showPrivacyPolicy: Bool = false
    @Published var showTermsOfService: Bool = false
    @Published var showShareSheet: Bool = false
    @Published var showProtectionExplanation: Bool = false
    @Published var showAdvancedProtection: Bool = false
    @Published var showProtectionHistory: Bool = false
    @Published var showEmergencyContacts: Bool = false
    @Published var showEmergencyNotifications: Bool = false
    @Published var showVoiceControl: Bool = false
    @Published var showChildProtectionCompliance: Bool = false
    @Published var showDataProtectionCompliance: Bool = false
    @Published var showPositioningSystemPicker: Bool = false

    // App Settings
    @Published var selectedTheme: ThemeMode = .system

    // Protection Level (computed from tariff)
    @Published var cachedProtectionLevel: Double = 25.0
    @Published var cachedProtectionLevelText: String = "Низкий"
    @Published var cachedProtectionColor: Color = .red

    // Personal Data Consent
    @Published var consentAccepted: Bool = false

    // System Components
    @Published var components: [SettingsComponentStatus] = []
    @Published var isLoadingComponents: Bool = false
    @Published var componentsError: String? = nil

    // Positioning System
    @Published var selectedPositioningSystem: PositioningSystem = .gps
    var currentPositioningSystem: PositioningSystem { .gps }
    var currentRegionName: String { "Russia" }

    // Initialization flag
    @Published var isInitializing: Bool = false

    // MARK: - Computed Properties

    var isAdmin: Bool {
        let userRole = UserDefaults.standard.string(forKey: "user_role") ?? "user"
        return userRole == "admin" || userRole == "administrator"
    }

    var currentTariff: TariffType {
        return tariffService?.currentTariff ?? .free
    }

    // MARK: - Dependencies

    var localizedStrings: LocalizedStrings

    // Service dependencies (initialized in DI constructor)
    private var navigationService: NavigationService!
    private var localizationService: LocalizationService!
    private var notificationService: NotificationService!
    private var securityService: SecurityService!
    private var tariffService: TariffService!
    private var apiService: SettingsAPIService!
    private var positioningService: PositioningService!
    private var featuresService: ProtectionFeaturesService!
    private var toastService: ToastService!
    private var historyService: ProtectionHistoryService!

    // MARK: - Initialization

    init() {
        // Default constructor with default localized strings for preview/testing
        localizedStrings = LocalizedStrings()
        // Use mock services for default initialization
        navigationService = nil
        localizationService = nil
        notificationService = nil
        securityService = nil
        tariffService = nil
        apiService = nil
        positioningService = nil
        featuresService = MockProtectionFeaturesService()
        toastService = MockToastService()
        historyService = MockProtectionHistoryService()
        loadInitialState()
    }

    // Constructor with dependency injection
    init(
        navigationService: NavigationService,
        localizationService: LocalizationService,
        notificationService: NotificationService,
        securityService: SecurityService,
        tariffService: TariffService,
        apiService: SettingsAPIService,
        positioningService: PositioningService,
        featuresService: ProtectionFeaturesService,
        toastService: ToastService,
        historyService: ProtectionHistoryService
    ) {
        self.navigationService = navigationService
        self.localizationService = localizationService
        self.notificationService = notificationService
        self.securityService = securityService
        self.tariffService = tariffService
        self.apiService = apiService
        self.positioningService = positioningService
        self.featuresService = featuresService
        self.toastService = toastService
        self.historyService = historyService

        // Initialize localized strings with defaults (TODO: use real localization)
        localizedStrings = LocalizedStrings()
        loadInitialState()
        setupBindings()
    }

    // MARK: - Reactive Bindings

    private func setupBindings() {
        guard notificationService != nil else { return }

        // Sync notification settings
        $isNotificationsEnabled
            .dropFirst()
            .sink { [weak self] enabled in
                var settings = self?.notificationService.notificationSettings
                settings?.familyEnabled = enabled
                settings?.networkProtectionEnabled = enabled
                settings?.aiEnabled = enabled
                settings?.bypassEnabled = enabled
                if let settings = settings {
                    self?.notificationService.updateNotificationSettings(settings)
                    self?.notificationService.saveSettings()
                }
            }
            .store(in: &cancellables)

        $securityEnabled
            .dropFirst()
            .sink { [weak self] enabled in
                var settings = self?.notificationService.notificationSettings
                settings?.securityEnabled = enabled
                if let settings = settings {
                    self?.notificationService.updateNotificationSettings(settings)
                    self?.notificationService.saveSettings()
                }
            }
            .store(in: &cancellables)

        $soundEnabled
            .dropFirst()
            .sink { [weak self] enabled in
                var settings = self?.notificationService.notificationSettings
                settings?.soundEnabled = enabled
                if let settings = settings {
                    self?.notificationService.updateNotificationSettings(settings)
                    self?.notificationService.saveSettings()
                }
            }
            .store(in: &cancellables)

        // Sync consent
        $consentAccepted
            .dropFirst()
            .sink { accepted in
                UserDefaults.standard.set(accepted, forKey: "personal_data_consent_accepted")
            }
            .store(in: &cancellables)

        // Sync biometric enabled state
        $isBiometricEnabled
            .dropFirst()
            .sink { enabled in
                UserDefaults.standard.set(enabled, forKey: "biometricEnabled")
            }
            .store(in: &cancellables)

        // Sync theme selection and apply theme
        $selectedTheme
            .dropFirst()
            .sink { [weak self] theme in
                UserDefaults.standard.set(theme.rawValue, forKey: "selected_theme")
                self?.applyTheme(theme)
            }
            .store(in: &cancellables)
    }

    // MARK: - Private Properties

    private var cancellables = Set<AnyCancellable>()

    // MARK: - Initial State Loading

    private func loadInitialState() {
        displayName = UserDefaults.standard.string(forKey: "profile_name") ?? ""
        displayAlias = UserDefaults.standard.string(forKey: "profile_alias") ?? ""
        consentAccepted = UserDefaults.standard.bool(forKey: "personal_data_consent_accepted")
        isBiometricEnabled = UserDefaults.standard.bool(forKey: "biometricEnabled")

        if let savedTheme = UserDefaults.standard.string(forKey: "selected_theme"),
           let theme = ThemeMode(rawValue: savedTheme) {
            selectedTheme = theme
        }
    }

    // MARK: - Public Methods

    func initializeView() {
        guard !isInitializing else { return }
        isInitializing = true

        print("✅ SettingsViewModel: MVVM initialization successful")

        // Initialize notifications
        initializeNotifications()

        // Load components if admin
        if isAdmin {
            loadComponents()
        }

        initializeProtectionLevel()
        isInitializing = false
    }

    func toggleBiometric() {
        Task {
            if securityService != nil {
                let success = await securityService.authenticateWithBiometrics()
                if success {
                    isBiometricEnabled.toggle()
                    UserDefaults.standard.set(isBiometricEnabled, forKey: "biometricEnabled")

                    if isBiometricEnabled {
                        notificationService?.sendLocalNotification(
                            title: localizedStrings.biometricEnabled,
                            body: "",
                            userInfo: nil
                        )
                        print("✅ Biometric enabled")
                    } else {
                        notificationService?.sendLocalNotification(
                            title: localizedStrings.biometricDisabled,
                            body: "",
                            userInfo: nil
                        )
                        print("❌ Biometric disabled")
                    }
                } else {
                    notificationService?.sendLocalNotification(
                        title: localizedStrings.biometricEnableFailed,
                        body: "",
                        userInfo: nil
                    )
                }
            } else {
                // Fallback for mock services
                isBiometricEnabled.toggle()
                UserDefaults.standard.set(isBiometricEnabled, forKey: "biometricEnabled")
            }
        }
    }


    func initializeProtectionLevel() {
        if tariffService != nil {
            // Use real tariff service
            let tariff = tariffService.currentTariff
            // Calculate protection level based on tariff
            switch tariff {
            case .free:
                cachedProtectionLevel = 25.0
                cachedProtectionLevelText = localizedStrings.protectionLevelLow
                cachedProtectionColor = .red
            case .personal:
                cachedProtectionLevel = 50.0
                cachedProtectionLevelText = localizedStrings.protectionLevelMedium
                cachedProtectionColor = .orange
            case .family:
                cachedProtectionLevel = 65.0
                cachedProtectionLevelText = localizedStrings.protectionLevelHigh
                cachedProtectionColor = .yellow
            case .premium:
                cachedProtectionLevel = 75.0
                cachedProtectionLevelText = localizedStrings.protectionLevelHigh
                cachedProtectionColor = .yellow
            case .ultimate:
                cachedProtectionLevel = 100.0
                cachedProtectionLevelText = localizedStrings.protectionLevelMaximum
                cachedProtectionColor = .green
            }
        } else {
            // Mock implementation for testing
            cachedProtectionLevel = 75.0
            cachedProtectionLevelText = "Высокий"
            cachedProtectionColor = .yellow
        }
    }

    func loadComponents() {
        guard isAdmin else { return }
        isLoadingComponents = true
        componentsError = nil

        if apiService != nil {
            // Use real API service
            apiService.getComponentsList { [weak self] result in
                DispatchQueue.main.async {
                    switch result {
                    case .success(let components):
                        self?.components = components.map {
                            SettingsComponentStatus(componentId: $0.componentId, isEnabled: $0.isEnabled)
                        }
                    case .failure(let error):
                        self?.componentsError = error.localizedDescription
                    }
                    self?.isLoadingComponents = false
                }
            }
        } else {
            // Mock implementation for testing
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                self.components = [
                    SettingsComponentStatus(componentId: "emergency", isEnabled: true),
                    SettingsComponentStatus(componentId: "notification", isEnabled: false),
                    SettingsComponentStatus(componentId: "voice", isEnabled: true)
                ]
                self.isLoadingComponents = false
            }
        }
    }

    func toggleComponent(_ component: SettingsComponentStatus) {
        guard isAdmin else { return }
        if let index = components.firstIndex(where: { $0.componentId == component.componentId }) {
            components[index].isEnabled.toggle()
        }
    }

    func updateProfile(name: String, alias: String) {
        displayName = name
        displayAlias = alias
        UserDefaults.standard.set(name, forKey: "profile_name")
        UserDefaults.standard.set(alias, forKey: "profile_alias")
    }

    func checkForUpdates() {
        // Mock implementation - would open App Store in real app
        print("✅ Checking for updates...")
    }

    func handleBiometricToggle(_ enabled: Bool) {
        print("🔐 Биометрический переключатель изменён: \(enabled)")

        // Проверяем доступность биометрии перед включением
        guard let securityService = securityService,
              securityService.biometricAuthAvailable || !enabled else {
            print("⚠️ Биометрия недоступна на этом устройстве")
            isBiometricEnabled = false // Reactive binding автоматически сохранит в UserDefaults

            // Show toast if available
            if let toastService = toastService {
                toastService.showToast(
                    message: localizedStrings.biometricUnavailable,
                    type: "error",
                    duration: 3.0
                )
            }
            return
        }

        // Устанавливаем состояние (reactive binding автоматически сохранит в UserDefaults)
        isBiometricEnabled = enabled

        // Показываем подтверждение
        if let toastService = toastService {
            let message = enabled ? localizedStrings.biometricEnabled : localizedStrings.biometricDisabled
            toastService.showToast(
                message: message,
                type: "success",
                duration: 2.0
            )
        }
    }
}

// MARK: - Supporting Types
struct SettingsComponentStatus {
    let componentId: String
    var isEnabled: Bool
}

enum ThemeMode: String, CaseIterable {
    case light = "light"
    case dark = "dark"
    case system = "system"

    var displayName: String {
        switch self {
        case .light: return "Светлая"
        case .dark: return "Темная"
        case .system: return "Системная"
        }
    }

    var icon: String {
        switch self {
        case .light: return "sun.max.fill"
        case .dark: return "moon.fill"
        case .system: return "gear"
        }
    }
}

// MARK: - Theme Management
extension SettingsViewModel {
    func cycleTheme() {
        let allThemes = ThemeMode.allCases
        if let currentIndex = allThemes.firstIndex(of: selectedTheme) {
            let nextIndex = (currentIndex + 1) % allThemes.count
            selectedTheme = allThemes[nextIndex]
            // applyTheme будет автоматически вызван через reactive binding
        }
    }

    private func applyTheme(_ theme: ThemeMode) {
        switch theme {
        case .light:
            // Применить светлую тему
            print("🌞 Применена светлая тема")
        case .dark:
            // Применить темную тему
            print("🌙 Применена темная тема")
        case .system:
            // Следовать системной теме
            print("⚙️ Следуем системной теме")
        }
    }
}

// MARK: - Notification Initialization
extension SettingsViewModel {
    func initializeNotifications() {
        // Инициализация системы уведомлений
        guard let notificationService = notificationService else {
            print("❌ NotificationService не доступен")
            return
        }

        Task {
            let granted = await notificationService.requestAuthorization()
            if granted {
                print("🔔 Разрешение на уведомления получено")
                // Можно добавить дополнительную логику при успешном разрешении
            } else {
                print("🔕 Разрешение на уведомления отклонено")
                // Можно добавить обработку отказа в разрешениях
            }
        }
    }
}

// Mock services are defined in SettingsScreen file
