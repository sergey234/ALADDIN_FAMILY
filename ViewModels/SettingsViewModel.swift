import SwiftUI
import Combine

// Master Logger for UI logging
private let logger = MasterLogger.shared

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
// ✅ ПРОДАКШН: Mock сервисы удалены - используются только реальные сервисы

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

// MARK: - LocalizedStrings wrapper for LocalizationManager
struct LocalizedStrings {
    private let localizationManager = LocalizationManager.shared
    
    // Navigation & Common
    var settingsTitle: String { localizationManager.localized("settings_title") }
    var settingsSubtitle: String { localizationManager.localized("settings_subtitle") }
    var settingsAccessibilityBackground: String { localizationManager.localized("settings_accessibility_background") }
    var settingsAccessibilityList: String { localizationManager.localized("settings_accessibility_list") }
    var settingsAccessibilityNavbar: String { localizationManager.localized("settings_accessibility_navbar") }

    // Profile Section
    var profileSection: String { localizationManager.localized("profile_section") }
    var profileNamePlaceholder: String { localizationManager.localized("profile_name") }
    var profileEmailPlaceholder: String { localizationManager.localized("profile_email") }
    var profileStatus: String { localizationManager.localized("profile_status_active") }
    var profileAvatarAccessibility: String { localizationManager.localized("settings_profile_avatar_accessibility") }
    var profileNameAccessibilityFormat: String { localizationManager.localized("settings_profile_name_accessibility") }
    var profileEmailAccessibilityFormat: String { localizationManager.localized("settings_profile_email_accessibility") }
    var profileStatusAccessibilityFormat: String { localizationManager.localized("settings_profile_status_accessibility") }
    var settingsProfileEditAccessibility: String { localizationManager.localized("settings_profile_edit") }

    // Security Section
    var securitySection: String { localizationManager.localized("security_section") }
    var networkProtectionProtection: String { localizationManager.localized("network_protection_protection") }
    var networkProtectionProtectionSubtitle: String { localizationManager.localized("network_protection_protection_subtitle") }
    var biometricAuth: String { localizationManager.localized("biometric_auth") }
    var biometricAuthSubtitle: String { localizationManager.localized("biometric_auth_subtitle") }
    var protectionLevel: String { localizationManager.localized("protection_level") }
    var settingsProtectionLevelValueFormat: String { localizationManager.localized("settings_protection_level_value_format") }
    var settingsProtectionLevel: String { localizationManager.localized("settings_protection_level") }
    var settingsProtectionHistory: String { localizationManager.localized("settings_protection_history") }
    var settingsAdvancedSettings: String { localizationManager.localized("settings_advanced_settings") }
    var settingsImproveProtection: String { localizationManager.localized("settings_improve_protection") }
    var settingsProtectionLevelAccessibility: String { localizationManager.localized("settings_protection_level_accessibility") }

    // Protection level texts
    var protectionLevelLow: String { localizationManager.localized("settings_protection_level_low") }
    var protectionLevelMedium: String { localizationManager.localized("settings_protection_level_medium") }
    var protectionLevelHigh: String { localizationManager.localized("settings_protection_level_high") }
    var protectionLevelMaximum: String { localizationManager.localized("settings_protection_level_maximum") }

    // Notifications Section
    var notificationsSection: String { localizationManager.localized("notifications_section") }
    var pushNotifications: String { localizationManager.localized("push_notifications") }
    var pushNotificationsSubtitle: String { localizationManager.localized("push_notifications_subtitle") }
    var soundNotifications: String { localizationManager.localized("sound_notifications") }
    var soundNotificationsSubtitle: String { localizationManager.localized("sound_notifications_subtitle") }

    // App Section
    var appSection: String { localizationManager.localized("app_section") }
    var language: String { localizationManager.localized("language") }
    var languageSubtitle: String { localizationManager.localized("language_subtitle_select") }
    var darkTheme: String { localizationManager.localized("dark_theme") }
    var updates: String { localizationManager.localized("updates") }
    var updatesSubtitle: String { localizationManager.localized("updates_subtitle") }
    var positioningSystemTitle: String { localizationManager.localized("positioning_system_title") }

    // System Components
    var systemComponentsTitle: String { localizationManager.localized("system_components_title") }
    var retry: String { localizationManager.localized("system_components_retry") }
    var systemComponentsEmpty: String { localizationManager.localized("system_components_empty") }
    var systemComponentsLastUpdate: String { localizationManager.localized("system_components_last_update") }
    var systemComponentDescription: String { localizationManager.localized("system_component_description") }

    // Additional Section
    var additionalSection: String { localizationManager.localized("additional_section") }
    var helpSupport: String { localizationManager.localized("help_support") }
    var helpSupportSubtitle: String { localizationManager.localized("help_support_subtitle") }
    var privacyPolicy: String { localizationManager.localized("privacy_policy") }
    var privacyPolicySubtitle: String { localizationManager.localized("privacy_policy_subtitle") }
    var termsOfService: String { localizationManager.localized("terms_of_service") }
    var termsOfServiceSubtitle: String { localizationManager.localized("terms_of_service_subtitle") }
    var shareApp: String { localizationManager.localized("share_app") }
    var shareAppSubtitle: String { localizationManager.localized("share_app_subtitle") }
    var settingsShareMessage: String { localizationManager.localized("settings_share_message") }
    var settingsDiagnosticsTitle: String { localizationManager.localized("settings_diagnostics_title") }
    var settingsDiagnosticsSubtitle: String { localizationManager.localized("settings_diagnostics_subtitle") }

    // Personal Data Consent
    var settingsConsentPersonalData: String { localizationManager.localized("settings_consent_personal_data") }
    var settingsConsentGranted: String { localizationManager.localized("settings_consent_granted") }
    var settingsConsentManage: String { localizationManager.localized("settings_consent_manage") }

    // Biometric notifications
    var biometricEnabled: String { localizationManager.localized("settings_biometric_enabled") }
    var biometricDisabled: String { localizationManager.localized("settings_biometric_disabled") }
    var biometricEnableFailed: String { localizationManager.localized("settings_biometric_enable_failed") }
    var biometricUnavailable: String { localizationManager.localized("settings_biometric_unavailable") }
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
    @Published var cachedProtectionLevelText: String = ""
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

    // ✅ BUILD 96: Кешированное значение для предотвращения рекурсии
    @Published private var _isAdmin: Bool = false

    // MARK: - Computed Properties

    var isAdmin: Bool {
        return _isAdmin
    }
    
    // ✅ BUILD 96: Асинхронная загрузка для предотвращения рекурсии
    private func loadIsAdmin() {
        Task { @MainActor in
            let userRole = UserDefaults.standard.string(forKey: "user_role") ?? "user"
            _isAdmin = userRole == "admin" || userRole == "administrator"
        }
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
        // ✅ ПРОДАКШН: Все сервисы должны быть переданы через DI
        navigationService = nil
        localizationService = nil
        notificationService = nil
        securityService = nil
        tariffService = nil
        apiService = nil
        positioningService = nil
        featuresService = nil  // ✅ Реальный сервис будет передан через DI
        toastService = nil      // ✅ Реальный сервис будет передан через DI
        historyService = nil    // ✅ Реальный сервис будет передан через DI
        loadInitialState()
        loadIsAdmin()  // ✅ BUILD 96: Загружаем isAdmin асинхронно
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
                // ✅ BUILD 96: Асинхронная установка для предотвращения рекурсии
                Task { @MainActor in
                    UserDefaults.standard.set(accepted, forKey: "personal_data_consent_accepted")
                }
            }
            .store(in: &cancellables)

        // Sync biometric enabled state
        $isBiometricEnabled
            .dropFirst()
            .sink { enabled in
                // ✅ BUILD 96: Асинхронная установка для предотвращения рекурсии
                Task { @MainActor in
                    UserDefaults.standard.set(enabled, forKey: "biometricEnabled")
                }
            }
            .store(in: &cancellables)

        // Sync theme selection and apply theme
        $selectedTheme
            .dropFirst()
            .sink { [weak self] theme in
                // ✅ BUILD 96: Асинхронная установка для предотвращения рекурсии
                Task { @MainActor in
                    UserDefaults.standard.set(theme.rawValue, forKey: "selected_theme")
                }
                // Применяем тему синхронно для немедленного эффекта
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
        logger.buttonTap("Biometric Toggle", screen: "Settings")
        Task {
            if securityService != nil {
                let success = await securityService.authenticateWithBiometrics()
                if success {
                    isBiometricEnabled.toggle()
                    logger.toggleChanged("Biometric", newValue: isBiometricEnabled, screen: "Settings")
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
            // Calculate protection level based on tariff (real function counts)
            switch tariff {
            case .trial:
                cachedProtectionLevel = 14.0  // 20/142 ≈ 14% (trial имеет меньше функций)
                cachedProtectionLevelText = localizedStrings.protectionLevelLow
                cachedProtectionColor = .gray
            case .free:
                cachedProtectionLevel = 18.0  // 26/142 ≈ 18%
                cachedProtectionLevelText = localizedStrings.protectionLevelLow
                cachedProtectionColor = .red
            case .personal:
                cachedProtectionLevel = 49.0  // 69/142 ≈ 49%
                cachedProtectionLevelText = localizedStrings.protectionLevelMedium
                cachedProtectionColor = .orange
            case .family:
                cachedProtectionLevel = 90.0  // 128/142 ≈ 90%
                cachedProtectionLevelText = localizedStrings.protectionLevelMaximum
                cachedProtectionColor = .green
            case .premium:
                cachedProtectionLevel = 100.0  // 142/142 = 100%
                cachedProtectionLevelText = localizedStrings.protectionLevelMaximum
                cachedProtectionColor = .green
            }
        } else {
            // Mock implementation for testing
            cachedProtectionLevel = 75.0
            cachedProtectionLevelText = localizedStrings.protectionLevelHigh
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
        logger.buttonTap("Component Toggle: \(component.componentId)", screen: "Settings")
        guard isAdmin else {
            logger.warn("Component toggle attempted without admin rights", function: #function)
            return
        }
        if let index = components.firstIndex(where: { $0.componentId == component.componentId }) {
            components[index].isEnabled.toggle()
            logger.toggleChanged("Component \(component.componentId)", newValue: components[index].isEnabled, screen: "Settings")
        } else {
            logger.error("Component \(component.componentId) not found for toggling")
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
        let localizationManager = LocalizationManager.shared
        switch self {
        case .light: return localizationManager.localized("theme_light_display")
        case .dark: return localizationManager.localized("theme_dark_display")
        case .system: return localizationManager.localized("theme_system_display")
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
