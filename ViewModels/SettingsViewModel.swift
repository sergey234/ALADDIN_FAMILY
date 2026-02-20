import SwiftUI
import Combine

// TariffType defined locally for compilation
enum SettingsTariffType: String {
    case free = "free"
    case personal = "personal"
    case family = "family"
    case premium = "premium"
    case ultimate = "ultimate"
}

// Type aliases are defined in AppCoordinator

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
    var currentTariff: SettingsTariffType { get }
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

    // Constructor for dependency injection
    init(from localizationService: LocalizationService) {
        // Initialize with real localization service
        self.settingsTitle = localizationService.localized("settings_title")
        self.settingsSubtitle = localizationService.localized("settings_subtitle")
        self.settingsAccessibilityBackground = localizationService.localized("settings_accessibility_background")
        self.settingsAccessibilityList = localizationService.localized("settings_accessibility_list")
        self.settingsAccessibilityNavbar = localizationService.localized("settings_accessibility_navbar")

        // Profile Section
        self.profileSection = localizationService.localized("profile_section")
        self.profileNamePlaceholder = localizationService.localized("profile_name_placeholder")
        self.profileEmailPlaceholder = localizationService.localized("profile_email_placeholder")
        self.profileStatus = localizationService.localized("settings_profile_status")
        self.profileAvatarAccessibility = localizationService.localized("settings_profile_avatar_accessibility")
        self.profileNameAccessibilityFormat = localizationService.localized("settings_profile_name_accessibility")
        self.profileEmailAccessibilityFormat = localizationService.localized("settings_profile_email_accessibility")
        self.profileStatusAccessibilityFormat = localizationService.localized("settings_profile_status_accessibility")
        self.settingsProfileEditAccessibility = localizationService.localized("settings_profile_edit_accessibility")

        // Security Section
        self.securitySection = localizationService.localized("security_section")
        self.networkProtectionProtection = localizationService.localized("network_protection_protection")
        self.networkProtectionProtectionSubtitle = localizationService.localized("network_protection_protection_subtitle")
        self.biometricAuth = localizationService.localized("biometric_auth")
        self.biometricAuthSubtitle = localizationService.localized("biometric_auth_subtitle")
        self.protectionLevel = localizationService.localized("protection_level")
        self.settingsProtectionLevelValueFormat = localizationService.localized("settings_protection_level_value")
        self.settingsProtectionLevel = localizationService.localized("settings_protection_level")
        self.settingsProtectionHistory = localizationService.localized("settings_protection_history")
        self.settingsAdvancedSettings = localizationService.localized("settings_advanced_settings")
        self.settingsImproveProtection = localizationService.localized("settings_improve_protection")
        self.settingsProtectionLevelAccessibility = localizationService.localized("settings_protection_level_accessibility")

        // Notifications Section
        self.notificationsSection = localizationService.localized("notifications_section")
        self.pushNotifications = localizationService.localized("push_notifications")
        self.pushNotificationsSubtitle = localizationService.localized("push_notifications_subtitle")
        self.soundNotifications = localizationService.localized("sound_notifications")
        self.soundNotificationsSubtitle = localizationService.localized("sound_notifications_subtitle")

        // App Section
        self.appSection = localizationService.localized("app_section")
        self.language = localizationService.localized("language")
        self.languageSubtitle = localizationService.localized("language_subtitle")
        self.darkTheme = localizationService.localized("dark_theme")
        self.updates = localizationService.localized("updates")
        self.updatesSubtitle = localizationService.localized("updates_subtitle")

        // System Components
        self.systemComponentsTitle = localizationService.localized("system_components_title")
        self.retry = localizationService.localized("retry")
        self.systemComponentsEmpty = localizationService.localized("system_components_empty")
        self.systemComponentsLastUpdate = localizationService.localized("system_components_last_update")

        // Additional Section
        self.additionalSection = localizationService.localized("additional_section")
        self.helpSupport = localizationService.localized("help_support")
        self.helpSupportSubtitle = localizationService.localized("help_support_subtitle")
        self.privacyPolicy = localizationService.localized("privacy_policy")
        self.privacyPolicySubtitle = localizationService.localized("privacy_policy_subtitle")
        self.termsOfService = localizationService.localized("terms_of_service")
        self.termsOfServiceSubtitle = localizationService.localized("terms_of_service_subtitle")
        self.shareApp = localizationService.localized("share_app")
        self.shareAppSubtitle = localizationService.localized("share_app_subtitle")
        self.settingsShareMessage = localizationService.localized("settings_share_message")

        // Biometric notifications
        self.biometricEnabled = localizationService.localized("biometric_enabled")
        self.biometricDisabled = localizationService.localized("biometric_disabled")
        self.biometricEnableFailed = localizationService.localized("biometric_enable_failed")
        self.biometricUnavailable = localizationService.localized("biometric_unavailable")
    }
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

    // Initialization flag
    @Published var isInitializing: Bool = false

    // MARK: - Computed Properties

    var isAdmin: Bool {
        let userRole = UserDefaults.standard.string(forKey: "user_role") ?? "user"
        return userRole == "admin" || userRole == "administrator"
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

    // MARK: - Initialization

    init() {
        // Default constructor with mock services for preview/testing
        localizedStrings = LocalizedStrings()
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
        positioningService: PositioningService
    ) {
        self.navigationService = navigationService
        self.localizationService = localizationService
        self.notificationService = notificationService
        self.securityService = securityService
        self.tariffService = tariffService
        self.apiService = apiService
        self.positioningService = positioningService

        // Initialize localized strings with real localization service
        localizedStrings = LocalizedStrings(from: localizationService)
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

    func cycleTheme() {
        let allThemes = ThemeMode.allCases
        if let currentIndex = allThemes.firstIndex(of: selectedTheme) {
            let nextIndex = (currentIndex + 1) % allThemes.count
            selectedTheme = allThemes[nextIndex]
            UserDefaults.standard.set(selectedTheme.rawValue, forKey: "selected_theme")
            applyTheme(selectedTheme)
        }
    }

    private func applyTheme(_ theme: ThemeMode) {
        print("🎨 Applied theme: \(theme.rawValue)")
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
            case .premium:
                cachedProtectionLevel = 50.0
                cachedProtectionLevelText = localizedStrings.protectionLevelMedium
                cachedProtectionColor = .orange
            case .premium:
                cachedProtectionLevel = 75.0
                cachedProtectionLevelText = "Высокий"
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
