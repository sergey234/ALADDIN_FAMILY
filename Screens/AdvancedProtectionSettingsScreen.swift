import SwiftUI

/// ⚙️ Advanced Protection Settings Screen
/// Экран расширенных настроек защиты с 13 компонентами
/// Разделы: Защита в мессенджерах, Приватность, Мониторинг

struct AdvancedProtectionSettingsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @Environment(\.scenePhase) private var scenePhase
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = ProtectionSettingsViewModel()
    @ObservedObject private var contentBlockerManager = ContentBlockerManager.shared
    @ObservedObject private var componentStatusService = ComponentStatusService.shared

    // MARK: - Family (AppStorage/UserDefaults)
    @AppStorage("parental_messages_monitoring") private var isMessagesMonitoringEnabled: Bool = false
    @AppStorage("parental_screenshots_enabled") private var isScreenshotsEnabled: Bool = false
    @State private var familyBrowserSitesCount: Int = 0
    @State private var familyAppsUsedCount: Int = 0
    @State private var familyTotalTimeUsed: String = "0m"
    @State private var familyTotalTimeLimit: String = "0m"
    @State private var familyAppLimitsCount: Int = 0
    
    // Состояния для аккордеонов
    @State private var messengersExpanded = false
    @State private var privacyExpanded = false
    @State private var monitoringExpanded = false
    @State private var safariExpanded = false
    @State private var familyExpanded = false
    @State private var threatExpanded = false
    
    // Safari sheets
    @State private var safariSettingsSheet: SafariSettingsSheet? = nil
    @State private var isApplyingSafariRules: Bool = false

    @AppStorage("advanced_safari_sites_enabled") private var safariSitesEnabled: Bool = false
    @AppStorage("advanced_safari_social_enabled") private var safariSocialEnabled: Bool = false
    @AppStorage("advanced_safari_sites_categories") private var safariSitesCategoriesData: Data = Data()
    
    private enum SafariSettingsSheet: String, Identifiable {
        case sites
        case social
        var id: String { rawValue }
    }

    // Family sheets
    @State private var showFamilyMonitoringModal: Bool = false
    @State private var showFamilyTimeControlModal: Bool = false
    @State private var showAppLimitsSettingsModal: Bool = false
    @State private var familyModalEnabledDummy: Bool = true

    // Threat settings sheets
    @State private var showThreatProtectionSheet: Bool = false
    @State private var threatDestination: ThreatDestination? = nil
    
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
        .onAppear {
            refreshContentBlockerStatus()
            loadFamilyStats()
            refreshThreatStatuses()
        }
        .onChange(of: scenePhase) { newPhase in
            if newPhase == .active {
                refreshContentBlockerStatus()
                loadFamilyStats()
                refreshThreatStatuses()
            }
        }
        .sheet(item: $safariSettingsSheet) { sheet in
            switch sheet {
            case .sites:
                FamilyContentBlockModal(
                    isPresented: Binding(
                        get: { safariSettingsSheet != nil },
                        set: { newValue in if !newValue { safariSettingsSheet = nil } }
                    ),
                    isEnabled: .constant(contentBlockerManager.isEnabled),
                    titleKey: "advanced_safari_sites_filter_title",
                    headerTitleKey: "advanced_safari_sites_filter_title",
                    descriptionKey: "advanced_safari_sites_filter_subtitle",
                    allowedCategories: [.adult, .violence, .gambling, .forums, .fileSharing],
                    initialSelectedCategories: getSafariSitesCategories(),
                    onAppliedCategories: { selected in
                        setSafariSitesCategories(Array(selected))
                        safariSitesEnabled = !selected.isEmpty
                        applySafariUnionRules(triggeredBy: .sites)
                    }
                )
                .environmentObject(localizationManager)
            case .social:
                FamilyContentBlockModal(
                    isPresented: Binding(
                        get: { safariSettingsSheet != nil },
                        set: { newValue in if !newValue { safariSettingsSheet = nil } }
                    ),
                    isEnabled: .constant(contentBlockerManager.isEnabled),
                    titleKey: "advanced_safari_social_restriction_title",
                    headerTitleKey: "advanced_safari_social_restriction_title",
                    descriptionKey: "advanced_safari_social_restriction_subtitle",
                    allowedCategories: [.socialMedia],
                    initialSelectedCategories: safariSocialEnabled ? [.socialMedia] : [],
                    onAppliedCategories: { selected in
                        safariSocialEnabled = selected.contains(.socialMedia)
                        applySafariUnionRules(triggeredBy: .social)
                    }
                )
                .environmentObject(localizationManager)
            }
        }
        .sheet(isPresented: $showFamilyMonitoringModal) {
            FamilyMonitoringModal(isPresented: $showFamilyMonitoringModal, isEnabled: $familyModalEnabledDummy)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showFamilyTimeControlModal) {
            FamilyTimeControlModal(isPresented: $showFamilyTimeControlModal, isEnabled: $familyModalEnabledDummy)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAppLimitsSettingsModal) {
            AppLimitsSettingsModal(isPresented: $showAppLimitsSettingsModal)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showThreatProtectionSheet) {
            ThreatProtectionFlowSheet(
                isPresented: $showThreatProtectionSheet,
                destination: $threatDestination
            )
            .environmentObject(localizationManager)
        }
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
            // Safari (Content Blocker)
            SettingsAccordion(
                icon: "🌐",
                title: localizationManager.localized("advanced_safari_section_title"),
                subtitle: localizationManager.localized("advanced_safari_section_subtitle"),
                isExpanded: $safariExpanded
            ) {
                VStack(spacing: Spacing.m) {
                    safariCard(
                        title: localizationManager.localized("advanced_safari_sites_filter_title"),
                        subtitle: localizationManager.localized("advanced_safari_sites_filter_subtitle"),
                        isOn: $safariSitesEnabled,
                        configureAction: { safariSettingsSheet = .sites },
                        trigger: .sites
                    )
                    
                    safariCard(
                        title: localizationManager.localized("advanced_safari_social_restriction_title"),
                        subtitle: localizationManager.localized("advanced_safari_social_restriction_subtitle"),
                        isOn: $safariSocialEnabled,
                        configureAction: { safariSettingsSheet = .social },
                        trigger: .social
                    )
                }
                .padding(.top, Spacing.m)
            }

            // Контроль и мониторинг (семья)
            SettingsAccordion(
                icon: "👨‍👩‍👧‍👦",
                title: localizationManager.localized("advanced_family_section_title"),
                subtitle: localizationManager.localized("advanced_family_section_subtitle"),
                isExpanded: $familyExpanded
            ) {
                VStack(spacing: Spacing.m) {
                    familyActivityMonitoringCard
                    familyTimeControlCard
                    familyAppLimitsCard
                }
                .padding(.top, Spacing.m)
            }

            // Защита от угроз (42 компонента, агрегатор)
            SettingsAccordion(
                icon: "🛡️",
                title: localizationManager.localized("component.threat_protection.title"),
                subtitle: localizationManager.localized("component.threat_protection.subtitle"),
                isExpanded: $threatExpanded
            ) {
                VStack(spacing: Spacing.m) {
                    threatProtectionAggregatorCard
                }
                .padding(.top, Spacing.m)
            }
            
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
                        onToggle: { value in
                            viewModel.setTelegramSecurity(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setWhatsAppSecurity(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setInstagramSecurity(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setMaxMessengerSecurity(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setGamingSecurity(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setBrowserSecurity(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setLocationBubble(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setPersonalDataCleanup(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setAntiTracker(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setDarkWebMonitoring(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setIdentityTheftProtection(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setAICategories(isEnabled: value)
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
                        onToggle: { value in
                            viewModel.setDrivingReports(isEnabled: value)
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

    // MARK: - Safari helpers
    
    private func refreshContentBlockerStatus() {
        Task {
            await contentBlockerManager.checkBlockingStatus()
            contentBlockerManager.loadActiveCategories()
            await MainActor.run {
                syncSafariCardsFromActiveCategories()
            }
        }
    }

    // MARK: - Threat helpers
    
    private func refreshThreatStatuses() {
        Task {
            await componentStatusService.refreshCriticalComponents()
        }
    }
    
    private var threatComponentIds: [String] {
        [
            "phishing_protection_agent",
            "malware_detection_agent",
            "mobile_security_agent",
            "network_security_agent"
        ]
    }
    
    private var threatEnabledCount: Int {
        threatComponentIds.reduce(0) { acc, id in
            let isEnabled = componentStatusService.componentStatuses[id]?.isEnabled ?? false
            return acc + (isEnabled ? 1 : 0)
        }
    }
    
    private var threatAggregateStatusText: String {
        if threatEnabledCount == 0 {
            return localizationManager.localized("advanced_threat_status_off")
        }
        if threatEnabledCount == threatComponentIds.count {
            return localizationManager.localized("advanced_threat_status_on")
        }
        return String(
            format: localizationManager.localized("advanced_threat_status_partial"),
            threatEnabledCount,
            threatComponentIds.count
        )
    }
    
    private var threatAggregateIsOn: Bool {
        threatEnabledCount == threatComponentIds.count
    }
    
    private func setThreatAggregate(isOn: Bool) {
        Task {
            for componentId in threatComponentIds {
                try? await componentStatusService.updateStatus(componentId: componentId, isEnabled: isOn)
            }
        }
    }
    
    private var threatProtectionAggregatorCard: some View {
        VStack(spacing: Spacing.s) {
            HStack(alignment: .top, spacing: Spacing.m) {
                Text("🛡️")
                    .font(.system(size: 24))
                    .frame(width: 34, height: 34)
                    .background(Circle().fill(Color.secondaryGold.opacity(0.15)))
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("advanced_threat_card_title"))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizationManager.localized("advanced_threat_card_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Text(threatAggregateStatusText)
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                ALADDINToggle(isOn: Binding(
                    get: { threatAggregateIsOn },
                    set: { newValue in setThreatAggregate(isOn: newValue) }
                ))
            }
            
            HStack {
                Button {
                    showThreatProtectionSheet = true
                } label: {
                    Text(localizationManager.localized("advanced_threat_configure"))
                        .font(.caption.bold())
                        .foregroundColor(.secondaryGold)
                }
                
                Spacer()
                
                Button {
                    refreshThreatStatuses()
                } label: {
                    Text(localizationManager.localized("advanced_threat_refresh"))
                        .font(.caption.bold())
                        .foregroundColor(.secondaryGold)
                }
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.large)
    }

    private func loadFamilyStats() {
        // Monitoring stats
        if let stats = UserDefaults.standard.dictionary(forKey: "parental_monitoring_stats") {
            familyBrowserSitesCount = stats["browserSitesCount"] as? Int ?? familyBrowserSitesCount
            familyAppsUsedCount = stats["appsUsedCount"] as? Int ?? familyAppsUsedCount
        }

        // Time stats
        if let stats = UserDefaults.standard.dictionary(forKey: "parental_time_stats") as? [String: String] {
            familyTotalTimeUsed = stats["totalTimeUsed"] ?? familyTotalTimeUsed
            familyTotalTimeLimit = stats["totalTimeLimit"] ?? familyTotalTimeLimit
        }

        // App limits count
        if let data = UserDefaults.standard.data(forKey: "app_limits_settings"),
           let decoded = try? JSONDecoder().decode([AppLimitItemCodable].self, from: data) {
            familyAppLimitsCount = decoded.count
        } else {
            familyAppLimitsCount = 0
        }
    }

    private var familyActivityMonitoringCard: some View {
        VStack(spacing: Spacing.s) {
            HStack(alignment: .top, spacing: Spacing.m) {
                Text("👀")
                    .font(.system(size: 24))
                    .frame(width: 34, height: 34)
                    .background(Circle().fill(Color.secondaryGold.opacity(0.15)))

                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("advanced_family_activity_title"))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)
                        .layoutPriority(2)

                    Text(localizationManager.localized("advanced_family_activity_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)
                        .layoutPriority(1)

                    Text(String(format: localizationManager.localized("advanced_family_activity_metrics"), familyBrowserSitesCount, familyAppsUsedCount))
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)
                        .layoutPriority(1)
                }

                Spacer()

                Button {
                    showFamilyMonitoringModal = true
                } label: {
                    Text(localizationManager.localized("advanced_family_details"))
                        .font(.caption.bold())
                        .foregroundColor(.secondaryGold)
                        .lineLimit(1)
                        .minimumScaleFactor(0.85)
                }
            }

            Divider().background(Color.white.opacity(0.15))

            VStack(spacing: Spacing.s) {
                HStack {
                    Text(localizationManager.localized("advanced_family_messages_toggle_title"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    ALADDINToggle(isOn: $isMessagesMonitoringEnabled)
                }

                HStack {
                    Text(localizationManager.localized("advanced_family_screenshots_toggle_title"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    ALADDINToggle(isOn: $isScreenshotsEnabled)
                }
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.large)
    }

    private var familyTimeControlCard: some View {
        VStack(spacing: Spacing.s) {
            HStack(alignment: .top, spacing: Spacing.m) {
                Text("⏱️")
                    .font(.system(size: 24))
                    .frame(width: 34, height: 34)
                    .background(Circle().fill(Color.secondaryGold.opacity(0.15)))

                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("advanced_family_time_title"))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)

                    Text(localizationManager.localized("advanced_family_time_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)

                    Text(String(format: localizationManager.localized("advanced_family_time_metrics"), familyTotalTimeUsed, familyTotalTimeLimit))
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }

                Spacer()

                Button {
                    showFamilyTimeControlModal = true
                } label: {
                    Text(localizationManager.localized("advanced_family_details"))
                        .font(.caption.bold())
                        .foregroundColor(.secondaryGold)
                }
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.large)
    }

    private var familyAppLimitsCard: some View {
        VStack(spacing: Spacing.s) {
            HStack(alignment: .top, spacing: Spacing.m) {
                Text("⏰")
                    .font(.system(size: 24))
                    .frame(width: 34, height: 34)
                    .background(Circle().fill(Color.secondaryGold.opacity(0.15)))

                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("advanced_family_app_limits_title"))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)

                    Text(localizationManager.localized("advanced_family_app_limits_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)

                    Text(String(format: localizationManager.localized("advanced_family_app_limits_metrics"), familyAppLimitsCount))
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }

                Spacer()

                Button {
                    showAppLimitsSettingsModal = true
                } label: {
                    Text(localizationManager.localized("advanced_family_details"))
                        .font(.caption.bold())
                        .foregroundColor(.secondaryGold)
                }
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.large)
    }
    
    private func safariCard(
        title: String,
        subtitle: String,
        isOn: Binding<Bool>,
        configureAction: @escaping () -> Void,
        trigger: SafariSettingsSheet
    ) -> some View {
        let statusText: String = {
            switch contentBlockerManager.status {
            case .enabled:
                return String(
                    format: localizationManager.localized("content_block_status_active"),
                    contentBlockerManager.blockedSitesCount
                )
            case .needsActivation:
                return localizationManager.localized("content_block_status_needs_activation")
            case .disabled:
                return localizationManager.localized("advanced_safari_status_disabled")
            case .error:
                return localizationManager.localized("advanced_safari_status_error")
            }
        }()
        
        return VStack(spacing: Spacing.s) {
            HStack(alignment: .top, spacing: Spacing.m) {
                Text("🟣")
                    .font(.system(size: 24))
                    .frame(width: 34, height: 34)
                    .background(Circle().fill(Color(hex: "#A855F7").opacity(0.15)))
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .fixedSize(horizontal: false, vertical: true)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                    
                    Text(statusText)
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                ALADDINToggle(isOn: Binding(
                    get: { isOn.wrappedValue },
                    set: { newValue in
                        isOn.wrappedValue = newValue
                        applySafariUnionRules(triggeredBy: trigger)
                    }
                ))
            }
            
            HStack {
                Button {
                    configureAction()
                } label: {
                    Text(localizationManager.localized("advanced_safari_configure_categories"))
                        .font(.caption.bold())
                        .foregroundColor(Color(hex: "#A855F7"))
                }
                
                Spacer()
                
                if case .needsActivation = contentBlockerManager.status {
                    Button {
                        contentBlockerManager.openSettings()
                    } label: {
                        Text(localizationManager.localized("content_block_open_settings"))
                            .font(.caption.bold())
                            .foregroundColor(Color(hex: "#A855F7"))
                    }
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color(hex: "#A855F7").opacity(0.25), lineWidth: 1)
                )
        )
    }

    private func getSafariSitesCategories() -> [ContentBlockerCategory] {
        guard !safariSitesCategoriesData.isEmpty,
              let decoded = try? JSONDecoder().decode([String].self, from: safariSitesCategoriesData) else {
            return [.adult, .violence, .gambling, .forums, .fileSharing]
        }
        let categories = decoded.compactMap { ContentBlockerCategory(rawValue: $0) }
        return categories.isEmpty ? [.adult, .violence, .gambling, .forums, .fileSharing] : categories
    }

    private func setSafariSitesCategories(_ categories: [ContentBlockerCategory]) {
        let raw = categories.map { $0.rawValue }
        safariSitesCategoriesData = (try? JSONEncoder().encode(raw)) ?? Data()
    }

    private func syncSafariCardsFromActiveCategories() {
        // Ensure we always have a stored preset for sites categories (even on first launch)
        if safariSitesCategoriesData.isEmpty {
            setSafariSitesCategories([.adult, .violence, .gambling, .forums, .fileSharing])
        }

        let active = Set(contentBlockerManager.activeCategories)
        safariSocialEnabled = active.contains(.socialMedia)

        let sitesCandidates: Set<ContentBlockerCategory> = [.adult, .violence, .gambling, .forums, .fileSharing]
        safariSitesEnabled = !active.intersection(sitesCandidates).isEmpty
    }

    private func applySafariUnionRules(triggeredBy trigger: SafariSettingsSheet) {
        guard !isApplyingSafariRules else { return }
        isApplyingSafariRules = true

        Task {
            defer { Task { @MainActor in isApplyingSafariRules = false } }
            await contentBlockerManager.checkBlockingStatus()

            // если пользователь пытается включить карточку, но extension выключен — показываем инструкцию и откатываем включение карточки
            if case .needsActivation = contentBlockerManager.status {
                await MainActor.run {
                    if trigger == .sites, safariSitesEnabled { safariSitesEnabled = false }
                    if trigger == .social, safariSocialEnabled { safariSocialEnabled = false }
                    safariSettingsSheet = trigger
                }
                return
            }

            let sitesCategories = safariSitesEnabled ? getSafariSitesCategories() : []
            let socialCategories: [ContentBlockerCategory] = safariSocialEnabled ? [.socialMedia] : []
            let union = Array(Set(sitesCategories + socialCategories))

            if union.isEmpty {
                await contentBlockerManager.disableContentBlocker()
            } else {
                try? await contentBlockerManager.enableContentBlocker(categories: union)
            }

            await contentBlockerManager.checkBlockingStatus()
            await MainActor.run {
                contentBlockerManager.loadActiveCategories()
            }
        }
    }
}

// MARK: - Threat Settings Sheet

private enum ThreatDestination: String, Identifiable {
    case phishing
    case malware
    case mobileSecurity
    case networkSecurity

    var id: String { rawValue }
}

private struct ThreatProtectionFlowSheet: View {
    @Binding var isPresented: Bool
    @Binding var destination: ThreatDestination?
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                if let destination = destination {
                    destinationView(destination)
                } else {
                    menuView
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button {
                        if destination != nil {
                            destination = nil
                        } else {
                            isPresented = false
                            dismiss()
                        }
                    } label: {
                        Text(destination != nil ? localizationManager.localized("common_back") : localizationManager.localized("common_close"))
                            .foregroundColor(.secondaryGold)
                    }
                }
            }
        }
    }

    private var menuView: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("advanced_threat_sheet_title"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .padding(.top, Spacing.l)

            VStack(spacing: Spacing.s) {
                Button { destination = .phishing } label: {
                    row(title: localizationManager.localized("component.phishing_protection_agent.title"))
                }
                Button { destination = .malware } label: {
                    row(title: localizationManager.localized("component.malware_detection_agent.title"))
                }
                Button { destination = .mobileSecurity } label: {
                    row(title: localizationManager.localized("component.mobile_security_agent.title"))
                }
                Button { destination = .networkSecurity } label: {
                    row(title: localizationManager.localized("component.network_security_agent.title"))
                }
            }
            .padding(.horizontal, Spacing.screenPadding)

            Spacer()
        }
    }

    @ViewBuilder
    private func destinationView(_ destination: ThreatDestination) -> some View {
        switch destination {
        case .phishing:
            PhishingProtectionSettingsModal(
                componentId: "phishing_protection_agent",
                isPresented: Binding(
                    get: { self.destination == .phishing },
                    set: { newValue in if !newValue { self.destination = nil } }
                )
            )
        case .malware:
            MalwareDetectionSettingsModal(
                componentId: "malware_detection_agent",
                isPresented: Binding(
                    get: { self.destination == .malware },
                    set: { newValue in if !newValue { self.destination = nil } }
                )
            )
        case .mobileSecurity:
            MobileSecuritySettingsModal(
                componentId: "mobile_security_agent",
                isPresented: Binding(
                    get: { self.destination == .mobileSecurity },
                    set: { newValue in if !newValue { self.destination = nil } }
                )
            )
        case .networkSecurity:
            NetworkSecuritySettingsModal(
                componentId: "network_security_agent",
                isPresented: Binding(
                    get: { self.destination == .networkSecurity },
                    set: { newValue in if !newValue { self.destination = nil } }
                )
            )
        }
    }
    
    private func row(title: String) -> some View {
        HStack {
            Text(title)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
            Spacer()
            Image(systemName: "chevron.right")
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.medium)
    }
}

// MARK: - Preview

struct AdvancedProtectionSettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        AdvancedProtectionSettingsScreen()
            .environmentObject(LocalizationManager())
    }
}
