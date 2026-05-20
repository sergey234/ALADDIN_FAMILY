import Foundation

/**
 * 🌍 LOCALIZED STRINGS CACHE
 * Кэшированные строки локализации для SettingsScreen
 * Создается один раз при инициализации ViewModel для предотвращения runtime зависимостей
 * Всего 58 ключей локализации, сгруппированных по секциям
 */

struct LocalizedStrings {
    // MARK: - Navigation & Common
    let settingsTitle: String
    let settingsSubtitle: String
    let settingsAccessibilityBackground: String
    let settingsAccessibilityList: String
    let settingsAccessibilityNavbar: String

    // MARK: - Profile Section (8 keys)
    let profileSection: String
    let profileNamePlaceholder: String
    let profileEmailPlaceholder: String
    let profileStatus: String
    let profileAvatarAccessibility: String
    let profileNameAccessibilityFormat: String
    let profileEmailAccessibilityFormat: String
    let profileStatusAccessibilityFormat: String

    // MARK: - Security Section (15 keys)
    let securitySection: String
    let networkProtectionProtection: String
    let networkProtectionProtectionSubtitle: String
    let biometricAuth: String
    let biometricAuthSubtitle: String
    let protectionLevel: String
    let settingsProtectionLevelValueFormat: String
    let settingsProtectionLevel: String
    let settingsProtectionHistory: String
    let settingsAdvancedSettings: String
    let settingsImproveProtection: String
    let settingsProtectionLevelAccessibility: String
    let componentEmergencyContactManagerTitle: String
    let componentEmergencyContactManagerDescription: String
    let componentEmergencyNotificationManagerTitle: String
    let componentEmergencyNotificationManagerDescription: String
    let componentVoiceControlManagerTitle: String
    let componentVoiceControlManagerDescription: String
    let componentRussianChildProtectionManagerTitle: String
    let componentRussianChildProtectionManagerDescription: String
    let componentRussianDataProtectionManagerTitle: String
    let componentRussianDataProtectionManagerDescription: String

    // MARK: - Notifications Section (6 keys)
    let notificationsSection: String
    let pushNotifications: String
    let pushNotificationsSubtitle: String
    let soundNotifications: String
    let soundNotificationsSubtitle: String
    let settingsToggleAccessibility: String
    let settingsToggleOn: String
    let settingsToggleOff: String

    // MARK: - App Section (8 keys)
    let appSection: String
    let language: String
    let languageSubtitle: String
    let darkTheme: String
    let updates: String
    let updatesSubtitle: String
    let positioningSystemTitle: String
    let positioningSystemAuto: String

    // MARK: - System Components (5 keys)
    let systemComponentsTitle: String
    let retry: String
    let systemComponentsEmpty: String
    let systemComponentsLastUpdate: String

    // MARK: - Additional Section (10 keys)
    let additionalSection: String
    let helpSupport: String
    let helpSupportSubtitle: String
    let privacyPolicy: String
    let privacyPolicySubtitle: String
    let termsOfService: String
    let termsOfServiceSubtitle: String
    let settingsConsentPersonalData: String
    let settingsConsentGranted: String
    let settingsConsentManage: String
    let shareApp: String
    let shareAppSubtitle: String
    let settingsShareMessage: String

    // MARK: - Biometric & Security Messages (6 keys)
    let biometricUnavailable: String
    let biometricEnableFailed: String
    let biometricEnabled: String
    let biometricDisabled: String
    let protectionLevelLow: String
    let protectionLevelMedium: String
    let protectionLevelHigh: String
    let protectionLevelMaximum: String

    // MARK: - Theme & Settings (9 keys)
    let themeLight: String
    let themeDark: String
    let themeSystem: String
    let settingsPercentFormat: String
    let settingsButtonAccessibility: String
    let settingsButtonAccessibilityFormat: String
    let settingsToggleAccessibilityFormat: String
    let settingsToggleOn: String
    let settingsShareMessage: String

    init(from localizationService: LocalizationService) {
        // Navigation & Common
        settingsTitle = localizationService.localized("settings_title")
        settingsSubtitle = localizationService.localized("settings_subtitle")
        settingsAccessibilityBackground = localizationService.localized("settings_accessibility_background")
        settingsAccessibilityList = localizationService.localized("settings_accessibility_list")
        settingsAccessibilityNavbar = localizationService.localized("settings_accessibility_navbar")

        // Profile Section
        profileSection = localizationService.localized("profile_section")
        profileNamePlaceholder = localizationService.localized("profile_name_placeholder")
        profileEmailPlaceholder = localizationService.localized("profile_email_placeholder")
        profileStatus = localizationService.localized("settings_profile_status")
        profileAvatarAccessibility = localizationService.localized("settings_profile_avatar_accessibility")
        profileNameAccessibilityFormat = localizationService.localized("settings_profile_name_accessibility")
        profileEmailAccessibilityFormat = localizationService.localized("settings_profile_email_accessibility")
        profileStatusAccessibilityFormat = localizationService.localized("settings_profile_status_accessibility")
        settingsProfileEditAccessibility = localizationService.localized("settings_profile_edit_accessibility")

        // Security Section
        securitySection = localizationService.localized("security_section")
        networkProtectionProtection = localizationService.localized("network_protection_protection")
        networkProtectionProtectionSubtitle = localizationService.localized("network_protection_protection_subtitle")
        biometricAuth = localizationService.localized("biometric_auth")
        biometricAuthSubtitle = localizationService.localized("biometric_auth_subtitle")
        protectionLevel = localizationService.localized("protection_level")
        settingsProtectionLevelValueFormat = localizationService.localized("settings_protection_level_value")
        settingsProtectionLevel = localizationService.localized("settings_protection_level")
        settingsProtectionHistory = localizationService.localized("settings_protection_history")
        settingsAdvancedSettings = localizationService.localized("settings_advanced_settings")
        settingsImproveProtection = localizationService.localized("settings_improve_protection")
        settingsProtectionLevelAccessibility = localizationService.localized("settings_protection_level_accessibility")
        settingsProtectionLevelAccessibility = localizationService.localized("settings_protection_level_accessibility")
        componentEmergencyContactManagerTitle = localizationService.localized("component_emergency_contact_manager_title")
        componentEmergencyContactManagerDescription = localizationService.localized("component_emergency_contact_manager_description")
        componentEmergencyNotificationManagerTitle = localizationService.localized("component_emergency_notification_manager_title")
        componentEmergencyNotificationManagerDescription = localizationService.localized("component_emergency_notification_manager_description")
        componentVoiceControlManagerTitle = localizationService.localized("component_voice_control_manager_title")
        componentVoiceControlManagerDescription = localizationService.localized("component_voice_control_manager_description")
        componentRussianChildProtectionManagerTitle = localizationService.localized("component_russian_child_protection_manager_title")
        componentRussianChildProtectionManagerDescription = localizationService.localized("component_russian_child_protection_manager_description")
        componentRussianDataProtectionManagerTitle = localizationService.localized("component_russian_data_protection_manager_title")
        componentRussianDataProtectionManagerDescription = localizationService.localized("component_russian_data_protection_manager_description")

        // Notifications Section
        notificationsSection = localizationService.localized("notifications_section")
        pushNotifications = localizationService.localized("push_notifications")
        pushNotificationsSubtitle = localizationService.localized("push_notifications_subtitle")
        soundNotifications = localizationService.localized("sound_notifications")
        soundNotificationsSubtitle = localizationService.localized("sound_notifications_subtitle")
        settingsToggleAccessibility = localizationService.localized("settings_toggle_accessibility")
        settingsToggleOn = localizationService.localized("settings_toggle_on")
        settingsToggleOff = localizationService.localized("settings_toggle_off")

        // App Section
        appSection = localizationService.localized("app_section")
        language = localizationService.localized("language")
        languageSubtitle = localizationService.localized("language_subtitle_select")
        darkTheme = localizationService.localized("dark_theme")
        updates = localizationService.localized("updates")
        updatesSubtitle = String(
            format: localizationService.localized("updates_subtitle_fmt"),
            AppConfig.appVersion
        )
        positioningSystemTitle = localizationService.localized("positioning_system_title")
        positioningSystemAuto = localizationService.localized("positioning_system_auto")

        // System Components
        systemComponentsTitle = localizationService.localized("system_components_title")
        retry = localizationService.localized("retry")
        systemComponentsEmpty = localizationService.localized("system_components_empty")
        systemComponentsLastUpdate = localizationService.localized("system_components_last_update")

        // Additional Section
        additionalSection = localizationService.localized("additional_section")
        helpSupport = localizationService.localized("help_support")
        helpSupportSubtitle = localizationService.localized("help_support_subtitle")
        privacyPolicy = localizationService.localized("privacy_policy")
        privacyPolicySubtitle = localizationService.localized("privacy_policy_subtitle")
        termsOfService = localizationService.localized("terms_of_service")
        termsOfServiceSubtitle = localizationService.localized("terms_of_service_subtitle")
        settingsConsentPersonalData = localizationService.localized("settings_consent_personal_data")
        settingsConsentGranted = localizationService.localized("settings_consent_granted")
        settingsConsentManage = localizationService.localized("settings_consent_manage")
        shareApp = localizationService.localized("share_app")
        shareAppSubtitle = localizationService.localized("share_app_subtitle")
        settingsShareMessage = localizationService.localized("settings_share_message")

        // Biometric & Security Messages
        biometricUnavailable = localizationService.localized("settings_biometric_unavailable")
        biometricEnableFailed = localizationService.localized("settings_biometric_enable_failed")
        biometricEnabled = localizationService.localized("settings_biometric_enabled")
        biometricDisabled = localizationService.localized("settings_biometric_disabled")
        protectionLevelLow = localizationService.localized("settings_protection_level_low")
        protectionLevelMedium = localizationService.localized("settings_protection_level_medium")
        protectionLevelHigh = localizationService.localized("settings_protection_level_high")
        protectionLevelMaximum = localizationService.localized("settings_protection_level_maximum")

        // Theme & Settings
        themeLight = localizationService.localized("theme_light")
        themeDark = localizationService.localized("theme_dark")
        themeSystem = localizationService.localized("theme_system")
        settingsPercentFormat = localizationService.localized("settings_percent_format")
        settingsButtonAccessibility = localizationService.localized("settings_button_accessibility")
        settingsButtonAccessibilityFormat = "%@, %@" // Format for button: title, subtitle
        settingsToggleAccessibilityFormat = "%@, %@" // Format for toggle: title, state
        settingsToggleOn = localizationService.localized("settings_toggle_on") ?? "включено"
        settingsShareMessage = localizationService.localized("settings_share_message")
    }
}