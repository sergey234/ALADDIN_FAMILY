import SwiftUI

/// ⚙️ Advanced Protection Settings Screen
/// Экран расширенных настроек защиты с 13 компонентами
/// Разделы: Защита в мессенджерах, Приватность, Мониторинг

struct AdvancedProtectionSettingsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = ProtectionSettingsViewModel()
    
    // Состояния для аккордеонов
    @State private var messengersExpanded = false
    @State private var privacyExpanded = false
    @State private var monitoringExpanded = false
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: localizationManager.localized("settings_advanced_title"),
                    subtitle: localizationManager.localized("settings_advanced_subtitle"),
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Разделы с компонентами
                        componentsSections
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, Spacing.m)
                    .padding(.horizontal, Spacing.screenPadding)
                }
            }
        }
        .navigationBarHidden(true)
        .id("advanced_protection_settings_screen_lang_\(localizationManager.currentLanguage.rawValue)")
        // Модальные окна для настроек
        .sheet(isPresented: $viewModel.showTelegramSettings) {
            ComponentSettingsModal(
                componentId: "telegram_security_bot",
                title: localizationManager.localized("component_telegram_security_bot_title"),
                isPresented: $viewModel.showTelegramSettings
            ) {
                Text(localizationManager.localized("component_telegram_security_bot_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showWhatsAppSettings) {
            ComponentSettingsModal(
                componentId: "whatsapp_security_bot",
                title: localizationManager.localized("component_whatsapp_security_bot_title"),
                isPresented: $viewModel.showWhatsAppSettings
            ) {
                Text(localizationManager.localized("component_whatsapp_security_bot_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showInstagramSettings) {
            ComponentSettingsModal(
                componentId: "instagram_security_bot",
                title: localizationManager.localized("component_instagram_security_bot_title"),
                isPresented: $viewModel.showInstagramSettings
            ) {
                Text(localizationManager.localized("component_instagram_security_bot_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showMaxMessengerSettings) {
            ComponentSettingsModal(
                componentId: "max_messenger_security_bot",
                title: localizationManager.localized("component_max_messenger_security_bot_title"),
                isPresented: $viewModel.showMaxMessengerSettings
            ) {
                Text(localizationManager.localized("component_max_messenger_security_bot_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showGamingSettings) {
            ComponentSettingsModal(
                componentId: "gaming_security_bot",
                title: localizationManager.localized("component_gaming_security_bot_title"),
                isPresented: $viewModel.showGamingSettings
            ) {
                Text(localizationManager.localized("component_gaming_security_bot_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showBrowserSettings) {
            ComponentSettingsModal(
                componentId: "browser_security_bot",
                title: localizationManager.localized("component_browser_security_bot_title"),
                isPresented: $viewModel.showBrowserSettings
            ) {
                Text(localizationManager.localized("component_browser_security_bot_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showLocationBubbleSettings) {
            ComponentSettingsModal(
                componentId: "location_bubble_agent",
                title: localizationManager.localized("component_location_bubble_agent_title"),
                isPresented: $viewModel.showLocationBubbleSettings
            ) {
                Text(localizationManager.localized("component_location_bubble_agent_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showPersonalDataCleanupSettings) {
            ComponentSettingsModal(
                componentId: "personal_data_cleanup_agent",
                title: localizationManager.localized("component_personal_data_cleanup_agent_title"),
                isPresented: $viewModel.showPersonalDataCleanupSettings
            ) {
                Text(localizationManager.localized("component_personal_data_cleanup_agent_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showAntiTrackerSettings) {
            ComponentSettingsModal(
                componentId: "anti_tracker_agent",
                title: localizationManager.localized("component_anti_tracker_agent_title"),
                isPresented: $viewModel.showAntiTrackerSettings
            ) {
                Text(localizationManager.localized("component_anti_tracker_agent_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showDarkWebMonitoringSettings) {
            ComponentSettingsModal(
                componentId: "dark_web_monitoring_agent",
                title: localizationManager.localized("component_dark_web_monitoring_agent_title"),
                isPresented: $viewModel.showDarkWebMonitoringSettings
            ) {
                Text(localizationManager.localized("component_dark_web_monitoring_agent_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showIdentityTheftProtectionSettings) {
            ComponentSettingsModal(
                componentId: "russian_identity_theft_protection_agent",
                title: localizationManager.localized("component_russian_identity_theft_protection_agent_title"),
                isPresented: $viewModel.showIdentityTheftProtectionSettings
            ) {
                Text(localizationManager.localized("component_russian_identity_theft_protection_agent_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showAICategoriesSettings) {
            ComponentSettingsModal(
                componentId: "ai_categories_agent",
                title: localizationManager.localized("component_ai_categories_agent_title"),
                isPresented: $viewModel.showAICategoriesSettings
            ) {
                Text(localizationManager.localized("component_ai_categories_agent_description"))
                    .foregroundColor(.textSecondary)
            }
        }
        .sheet(isPresented: $viewModel.showDrivingReportsSettings) {
            ComponentSettingsModal(
                componentId: "driving_reports_agent",
                title: localizationManager.localized("component_driving_reports_agent_title"),
                isPresented: $viewModel.showDrivingReportsSettings
            ) {
                Text(localizationManager.localized("component_driving_reports_agent_description"))
                    .foregroundColor(.textSecondary)
            }
        }
    }
    
    // MARK: - Components Sections
    
    private var componentsSections: some View {
        VStack(spacing: Spacing.l) {
            // Раздел: Защита в мессенджерах (6 компонентов)
            SettingsAccordion(
                icon: "💬",
                title: localizationManager.localized("protection_settings_messengers_title"),
                subtitle: localizationManager.localized("protection_settings_messengers_subtitle"),
                isExpanded: $messengersExpanded
            ) {
                VStack(spacing: Spacing.m) {
                    // Telegram
                    ComponentToggleCard(
                        componentId: "telegram_security_bot",
                        title: localizationManager.localized("component_telegram_security_bot_title"),
                        description: localizationManager.localized("component_telegram_security_bot_description"),
                        isEnabled: $viewModel.telegramSecurityEnabled,
                        icon: "📱",
                        onToggle: {
                            viewModel.toggleTelegramSecurity()
                        }
                    )
                    .onTapGesture {
                        viewModel.showTelegramSettings = true
                    }
                    
                    // WhatsApp
                    ComponentToggleCard(
                        componentId: "whatsapp_security_bot",
                        title: localizationManager.localized("component_whatsapp_security_bot_title"),
                        description: localizationManager.localized("component_whatsapp_security_bot_description"),
                        isEnabled: $viewModel.whatsappSecurityEnabled,
                        icon: "💬",
                        onToggle: {
                            viewModel.toggleWhatsAppSecurity()
                        }
                    )
                    .onTapGesture {
                        viewModel.showWhatsAppSettings = true
                    }
                    
                    // Instagram
                    ComponentToggleCard(
                        componentId: "instagram_security_bot",
                        title: localizationManager.localized("component_instagram_security_bot_title"),
                        description: localizationManager.localized("component_instagram_security_bot_description"),
                        isEnabled: $viewModel.instagramSecurityEnabled,
                        icon: "📷",
                        onToggle: {
                            viewModel.toggleInstagramSecurity()
                        }
                    )
                    .onTapGesture {
                        viewModel.showInstagramSettings = true
                    }
                    
                    // Max Messenger
                    ComponentToggleCard(
                        componentId: "max_messenger_security_bot",
                        title: localizationManager.localized("component_max_messenger_security_bot_title"),
                        description: localizationManager.localized("component_max_messenger_security_bot_description"),
                        isEnabled: $viewModel.maxMessengerSecurityEnabled,
                        icon: "💭",
                        onToggle: {
                            viewModel.toggleMaxMessengerSecurity()
                        }
                    )
                    .onTapGesture {
                        viewModel.showMaxMessengerSettings = true
                    }
                    
                    // Gaming
                    ComponentToggleCard(
                        componentId: "gaming_security_bot",
                        title: localizationManager.localized("component_gaming_security_bot_title"),
                        description: localizationManager.localized("component_gaming_security_bot_description"),
                        isEnabled: $viewModel.gamingSecurityEnabled,
                        icon: "🎮",
                        onToggle: {
                            viewModel.toggleGamingSecurity()
                        }
                    )
                    .onTapGesture {
                        viewModel.showGamingSettings = true
                    }
                    
                    // Browser
                    ComponentToggleCard(
                        componentId: "browser_security_bot",
                        title: localizationManager.localized("component_browser_security_bot_title"),
                        description: localizationManager.localized("component_browser_security_bot_description"),
                        isEnabled: $viewModel.browserSecurityEnabled,
                        icon: "🌐",
                        onToggle: {
                            viewModel.toggleBrowserSecurity()
                        }
                    )
                    .onTapGesture {
                        viewModel.showBrowserSettings = true
                    }
                }
                .padding(.top, Spacing.m)
            }
            
            // Раздел: Приватность (3 компонента)
            SettingsAccordion(
                icon: "🔒",
                title: localizationManager.localized("protection_settings_privacy_title"),
                subtitle: localizationManager.localized("protection_settings_privacy_subtitle"),
                isExpanded: $privacyExpanded
            ) {
                VStack(spacing: Spacing.m) {
                    // Location Bubble
                    ComponentToggleCard(
                        componentId: "location_bubble_agent",
                        title: localizationManager.localized("component_location_bubble_agent_title"),
                        description: localizationManager.localized("component_location_bubble_agent_description"),
                        isEnabled: $viewModel.locationBubbleEnabled,
                        icon: "📍",
                        onToggle: {
                            viewModel.toggleLocationBubble()
                        }
                    )
                    .onTapGesture {
                        viewModel.showLocationBubbleSettings = true
                    }
                    
                    // Personal Data Cleanup
                    ComponentToggleCard(
                        componentId: "personal_data_cleanup_agent",
                        title: localizationManager.localized("component_personal_data_cleanup_agent_title"),
                        description: localizationManager.localized("component_personal_data_cleanup_agent_description"),
                        isEnabled: $viewModel.personalDataCleanupEnabled,
                        icon: "🧹",
                        onToggle: {
                            viewModel.togglePersonalDataCleanup()
                        }
                    )
                    .onTapGesture {
                        viewModel.showPersonalDataCleanupSettings = true
                    }
                    
                    // Anti Tracker
                    ComponentToggleCard(
                        componentId: "anti_tracker_agent",
                        title: localizationManager.localized("component_anti_tracker_agent_title"),
                        description: localizationManager.localized("component_anti_tracker_agent_description"),
                        isEnabled: $viewModel.antiTrackerEnabled,
                        icon: "🚫",
                        onToggle: {
                            viewModel.toggleAntiTracker()
                        }
                    )
                    .onTapGesture {
                        viewModel.showAntiTrackerSettings = true
                    }
                }
                .padding(.top, Spacing.m)
            }
            
            // Раздел: Мониторинг (4 компонента)
            SettingsAccordion(
                icon: "👁️",
                title: localizationManager.localized("protection_settings_monitoring_title"),
                subtitle: localizationManager.localized("protection_settings_monitoring_subtitle"),
                isExpanded: $monitoringExpanded
            ) {
                VStack(spacing: Spacing.m) {
                    // Dark Web Monitoring
                    ComponentToggleCard(
                        componentId: "dark_web_monitoring_agent",
                        title: localizationManager.localized("component_dark_web_monitoring_agent_title"),
                        description: localizationManager.localized("component_dark_web_monitoring_agent_description"),
                        isEnabled: $viewModel.darkWebMonitoringEnabled,
                        icon: "🌑",
                        onToggle: {
                            viewModel.toggleDarkWebMonitoring()
                        }
                    )
                    .onTapGesture {
                        viewModel.showDarkWebMonitoringSettings = true
                    }
                    
                    // Identity Theft Protection
                    ComponentToggleCard(
                        componentId: "russian_identity_theft_protection_agent",
                        title: localizationManager.localized("component_russian_identity_theft_protection_agent_title"),
                        description: localizationManager.localized("component_russian_identity_theft_protection_agent_description"),
                        isEnabled: $viewModel.identityTheftProtectionEnabled,
                        icon: "🆔",
                        onToggle: {
                            viewModel.toggleIdentityTheftProtection()
                        }
                    )
                    .onTapGesture {
                        viewModel.showIdentityTheftProtectionSettings = true
                    }
                    
                    // AI Categories
                    ComponentToggleCard(
                        componentId: "ai_categories_agent",
                        title: localizationManager.localized("component_ai_categories_agent_title"),
                        description: localizationManager.localized("component_ai_categories_agent_description"),
                        isEnabled: $viewModel.aiCategoriesEnabled,
                        icon: "🤖",
                        onToggle: {
                            viewModel.toggleAICategories()
                        }
                    )
                    .onTapGesture {
                        viewModel.showAICategoriesSettings = true
                    }
                    
                    // Driving Reports
                    ComponentToggleCard(
                        componentId: "driving_reports_agent",
                        title: localizationManager.localized("component_driving_reports_agent_title"),
                        description: localizationManager.localized("component_driving_reports_agent_description"),
                        isEnabled: $viewModel.drivingReportsEnabled,
                        icon: "🚗",
                        onToggle: {
                            viewModel.toggleDrivingReports()
                        }
                    )
                    .onTapGesture {
                        viewModel.showDrivingReportsSettings = true
                    }
                }
                .padding(.top, Spacing.m)
            }
        }
    }
}

// MARK: - Preview

struct AdvancedProtectionSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        AdvancedProtectionSettingsScreen()
            .environmentObject(LocalizationManager())
    }
}
