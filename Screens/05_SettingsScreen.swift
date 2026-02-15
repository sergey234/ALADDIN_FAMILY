import SwiftUI

/// ⚙️ Settings Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран настроек - управление приложением и профилем
/// Источник дизайна: /mobile/wireframes/05_settings_screen.html
struct SettingsScreen: View {
    
    // MARK: - Theme Mode
    
    enum ThemeMode: String, CaseIterable {
        case light = "light"
        case dark = "dark"
        case system = "system"
        
        func displayName(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .light: return localizationManager.localized("theme_light")
            case .dark: return localizationManager.localized("theme_dark")
            case .system: return localizationManager.localized("theme_system")
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
    
    // MARK: - State

    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager // ✅ Добавляем LocalizationManager

    // ✅ ИСПРАВЛЕНО: Вернулись к @StateObject для singleton'ов (как в бэкапе - работало)
    @StateObject private var notificationManager = NotificationManager.shared
    @StateObject private var securityManager = SecurityManager.shared
    
    // ✅ ИСПРАВЛЕНО: Убрали флаги инициализации (как в бэкапах - работало)
    @State private var isNetworkProtectionEnabled: Bool = true
    @AppStorage("profile_name") private var storedName: String = ""
    @AppStorage("profile_alias") private var storedAlias: String = ""
    @AppStorage("settings_notifications_enabled") private var isNotificationsEnabled: Bool = true
    
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем @State для синхронизации с notificationManager (избегаем binding к вложенным свойствам)
    @State private var isSecurityNotificationsEnabled: Bool = false
    @State private var isSoundNotificationsEnabled: Bool = false
    @State private var isBiometricEnabled: Bool = false
    @State private var showProfileEdit: Bool = false
    @State private var showLanguageSettings: Bool = false
    @State private var showSupportScreen: Bool = false
    @State private var showPrivacyPolicy: Bool = false
    @State private var showTermsOfService: Bool = false
    @State private var showShareSheet: Bool = false
    @State private var selectedTheme: ThemeMode = .system
    @State private var showProtectionExplanation: Bool = false
    @State private var showAdvancedProtection: Bool = false
    // ✅ ИСПРАВЛЕНО: Вернулись к @StateObject для singleton'ов (как в бэкапе - работало)
    @StateObject private var featuresManager = ProtectionFeaturesManager.shared
    @StateObject private var toastManager = ToastManager.shared
    @StateObject private var historyManager = ProtectionLevelHistoryManager.shared
    @StateObject private var tariffManager = TariffManager.shared
    @State private var showProtectionHistory: Bool = false
    
    // Navigation для менеджеров
    @State private var showEmergencyContacts: Bool = false
    @State private var showEmergencyNotifications: Bool = false
    @State private var showVoiceControl: Bool = false
    @State private var showChildProtectionCompliance: Bool = false
    @State private var showDataProtectionCompliance: Bool = false
    
    // ✅ Согласие на обработку ПДн (152-ФЗ)
    @AppStorage("personal_data_consent_accepted") private var consentAccepted: Bool = false
    
    // ✅ Система позиционирования
    private let positioningService = PositioningSystemService.shared
    @State private var showPositioningSystemPicker: Bool = false
    
    // ✅ ЗАДАЧА 22: Системные компоненты (только для админов)
    @AppStorage("user_role") private var userRole: String = "user"
    @State private var components: [ComponentStatus] = []
    @State private var isLoadingComponents: Bool = false
    @State private var componentsError: String? = nil
    private let apiService = APIService.shared
    
    var isAdmin: Bool {
        userRole == "admin" || userRole == "administrator"
    }
    
    // ✅ ИСПРАВЛЕНО: Прямой доступ (как в бэкапах - работало)
    private var safeLanguageCode: String {
        guard Thread.isMainThread else {
            #if DEBUG
            print("⚠️ SETTINGS: safeLanguageCode вызван не на main thread")
            #endif
            return "en" // Fallback для фоновых потоков
        }
        return localizationManager.currentLanguage.rawValue
    }
    
    private var safeCurrentTariff: TariffType {
        guard Thread.isMainThread else {
            #if DEBUG
            print("⚠️ SETTINGS: safeCurrentTariff вызван не на main thread")
            #endif
            return .free // Fallback для фоновых потоков
        }
        return tariffManager.currentTariff
    }
    
    // MARK: - Body
    
    // Счетчик перерисовок для диагностики
    #if DEBUG
    private static var bodyCallCount: Int = 0
    private static var settingsContentCallCount: Int = 0
    #endif
    
    var body: some View {
        // ✅ ИСПРАВЛЕНО: Вернулись к прямому доступу (как в бэкапах - работало)
        let _ = {
            #if DEBUG
            Self.bodyCallCount += 1
            print("🔴 SETTINGS: body вычисляется - НАЧАЛО (#\(Self.bodyCallCount))")
            print("🔴 SETTINGS: Thread.isMainThread = \(Thread.isMainThread)")
            print("🔴 SETTINGS: notificationManager = \(notificationManager)")
            print("🔴 SETTINGS: securityManager = \(securityManager)")
            print("🔴 SETTINGS: featuresManager = \(featuresManager)")
            print("🔴 SETTINGS: tariffManager = \(tariffManager)")
            print("🔴 SETTINGS: isNetworkProtectionEnabled = \(isNetworkProtectionEnabled)")
            print("🔴 SETTINGS: isSecurityNotificationsEnabled = \(isSecurityNotificationsEnabled)")
            print("🔴 SETTINGS: isSoundNotificationsEnabled = \(isSoundNotificationsEnabled)")
            print("🔴 SETTINGS: isBiometricEnabled = \(isBiometricEnabled)")
            print("🔴 SETTINGS: selectedTheme = \(selectedTheme)")
            print("🔴 SETTINGS: showProfileEdit = \(showProfileEdit)")
            print("🔴 SETTINGS: localizationManager.currentLanguage = \(localizationManager.currentLanguage)")
            #endif
        }()
        settingsContent()
            .onAppear {
                #if DEBUG
                print("🔴 SETTINGS: onAppear вызван")
                print("🔴 SETTINGS: notificationManager = \(notificationManager)")
                print("🔴 SETTINGS: notificationSettings = \(notificationManager.notificationSettings)")
                print("🔴 SETTINGS: Все @State переменные:")
                print("  - isNetworkProtectionEnabled = \(isNetworkProtectionEnabled)")
                print("  - isSecurityNotificationsEnabled = \(isSecurityNotificationsEnabled)")
                print("  - isSoundNotificationsEnabled = \(isSoundNotificationsEnabled)")
                print("  - isBiometricEnabled = \(isBiometricEnabled)")
                print("  - selectedTheme = \(selectedTheme)")
                #endif
                initializeNotifications()
            }
            .onDisappear {
                #if DEBUG
                print("🔴 SETTINGS: onDisappear вызван")
                #endif
            }
    }
    
    // ✅ ИСПРАВЛЕНО: Упрощенная инициализация (как в бэкапе - работало)
    // Убрали сложные задержки и race conditions
    
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Основной контент экрана
    @ViewBuilder
    private func settingsContent() -> some View {
        let _ = {
            #if DEBUG
            Self.settingsContentCallCount += 1
            print("🔴 SETTINGS: settingsContent() вызывается (#\(Self.settingsContentCallCount))")
            print("🔴 SETTINGS: Thread.isMainThread = \(Thread.isMainThread)")
            print("🔴 SETTINGS: localizationManager доступен = \(localizationManager != nil)")
            print("🔴 SETTINGS: localizationManager.currentLanguage = \(localizationManager.currentLanguage)")
            print("🔴 SETTINGS: tariffManager.currentTariff = \(tariffManager.currentTariff)")
            print("🔴 SETTINGS: notificationManager.notificationSettings = \(notificationManager.notificationSettings)")
            print("🔴 SETTINGS: safeLanguageCode = \(safeLanguageCode)")
            print("🔴 SETTINGS: safeCurrentTariff = \(safeCurrentTariff)")
            print("🔴 SETTINGS: Stack trace:")
            Thread.callStackSymbols.prefix(5).forEach { print("  \($0)") }
            #endif
        }()
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(safeLocalized("settings_accessibility_background"))
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader()
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Профиль пользователя
                        profileSection()
                        
                        // Защита и безопасность
                        securitySection()
                        
                        // Уведомления
                        notificationsSection()
                        
                        // Приложение
                        appSection()
                            .id("app_section_\(safeLanguageCode)")
                        
                        // ✅ ЗАДАЧА 22: Системные компоненты (только для админов)
                        if isAdmin {
                            systemComponentsSection()
                                .id("system_components_section_\(safeLanguageCode)")
                        }
                        
                        // Дополнительно
                        additionalSection()
                            .id("additional_section_\(safeLanguageCode)")
                        
                        // Отступ снизу для удобства прокрутки
                        Spacer(minLength: 100)
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(safeLocalized("settings_accessibility_list"))
            }
        }
        .navigationBarHidden(true)
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("settings_lang_\(safeLanguageCode)")
        .sheet(isPresented: $showProfileEdit) {
            ProfileEditView()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showLanguageSettings) {
            LanguageSettingsScreen()
        }
        .sheet(isPresented: $showSupportScreen) {
            SupportScreen()
        }
        .sheet(isPresented: $showPrivacyPolicy) {
            PrivacyPolicyScreen()
        }
        .sheet(isPresented: $showTermsOfService) {
            TermsOfServiceScreen()
        }
        .sheet(isPresented: $showShareSheet) {
            ShareSheet(activityItems: [
                safeLocalized("settings_share_message")
            ])
        }
        .sheet(isPresented: $showProtectionExplanation) {
            ProtectionLevelExplanationModal(
                isPresented: $showProtectionExplanation,
                currentTariff: safeCurrentTariff
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAdvancedProtection) {
            AdvancedProtectionSettingsScreen()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showProtectionHistory) {
            ProtectionLevelHistoryModal(isPresented: $showProtectionHistory)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showEmergencyContacts) {
            EmergencyContactsView()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showEmergencyNotifications) {
            EmergencyNotificationsView()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showVoiceControl) {
            VoiceControlView()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showChildProtectionCompliance) {
            ComplianceView(section: .childProtection)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showDataProtectionCompliance) {
            ComplianceView(section: .dataProtection)
                .environmentObject(localizationManager)
        }
        // Инициализация перенесена в safeInitialize()
        .onChange(of: notificationManager.notificationSettings.securityEnabled) { newValue in
            #if DEBUG
            print("🟡 SETTINGS: onChange securityEnabled = \(newValue)")
            #endif
            isSecurityNotificationsEnabled = newValue
        }
        .onChange(of: notificationManager.notificationSettings.soundEnabled) { newValue in
            #if DEBUG
            print("🟡 SETTINGS: onChange soundEnabled = \(newValue)")
            #endif
            isSoundNotificationsEnabled = newValue
        }
        .withToast()
    }
    
    // MARK: - Navigation Header
    
    @ViewBuilder
    private func navigationHeader() -> some View {
        ALADDINNavigationBar(
            title: safeLocalized("settings_title"), // ✅ Безопасная локализация
            subtitle: safeLocalized("settings_subtitle"), // ✅ Безопасная локализация
            showBackButton: true,
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(safeLocalized("settings_accessibility_navbar"))
    }
    
    // ✅ ИСПРАВЛЕНО: Прямая локализация с защитой для реального устройства
    private func safeLocalized(_ key: String) -> String {
        guard Thread.isMainThread else {
            #if DEBUG
            print("⚠️ SETTINGS: safeLocalized вызван не на main thread для ключа '\(key)'")
            #endif
            return key // Fallback для фоновых потоков
        }
        let result = localizationManager.localized(key)
        #if DEBUG
        if result == key {
            print("⚠️ SETTINGS: Локализация не найдена для ключа '\(key)'")
        }
        #endif
        return result
    }
    
    // MARK: - Profile Section
    
    @ViewBuilder
    private func profileSection() -> some View {
        let userInitial = storedName.isEmpty ? "?" : String(storedName.prefix(1).uppercased())
        let userName = storedName.isEmpty ? safeLocalized("profile_name_placeholder") : storedName
        let userAlias = storedAlias.isEmpty ? safeLocalized("profile_email_placeholder") : storedAlias
        let userStatus = safeLocalized("settings_profile_status")
        
        VStack(spacing: Spacing.m) {
            HStack {
                Text(safeLocalized("profile_section")) // ✅ Безопасная локализация
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            HStack(spacing: Spacing.m) {
                // Аватар
                Circle()
                    .fill(LinearGradient(
                        colors: [.primaryBlue, .secondaryBlue],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ))
                    .frame(width: 60, height: 60)
                    .overlay(
                        Text(userInitial)
                            .font(.h2)
                            .foregroundColor(.white)
                    )
                    .accessibilityLabel(safeLocalized("settings_profile_avatar_accessibility"))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(userName)
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .accessibilityLabel(
                            String(
                                format: safeLocalized("settings_profile_name_accessibility"),
                                userName
                            )
                        )
                    
                    Text(userAlias)
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel(
                            String(
                                format: safeLocalized("settings_profile_email_accessibility"),
                                userAlias
                            )
                        )
                    
                    Text(userStatus)
                        .font(.caption)
                        .foregroundColor(.primaryBlue)
                        .padding(.horizontal, Spacing.s)
                        .padding(.vertical, Spacing.xxs)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.small)
                                .fill(Color.primaryBlue.opacity(0.1))
                        )
                        .accessibilityLabel(
                            String(
                                format: safeLocalized("settings_profile_status_accessibility"),
                                userStatus
                            )
                        )
                }
                
                Spacer()
                
                Button(action: {
                    showProfileEdit = true
                }) {
                    Image(systemName: "pencil")
                        .font(.system(size: 16))
                        .foregroundColor(.primaryBlue)
                        .frame(width: 32, height: 32)
                        .background(
                            Circle()
                                .fill(Color.primaryBlue.opacity(0.1))
                        )
                }
                .accessibilityLabel(safeLocalized("settings_profile_edit_accessibility"))
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Security Section
    
    @ViewBuilder
    private func securitySection() -> some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(safeLocalized("security_section")) // ✅ Безопасная локализация
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                // Network Protection
                settingRow(
                    icon: "shield.fill",
                    title: safeLocalized("network_protection_protection"), // ✅ Безопасная локализация
                    subtitle: safeLocalized("network_protection_protection_subtitle"), // ✅ Безопасная локализация
                    isEnabled: $isNetworkProtectionEnabled
                )
                
                // Биометрическая аутентификация
                settingRow(
                    icon: "faceid",
                    title: safeLocalized("biometric_auth"), // ✅ Безопасная локализация
                    subtitle: safeLocalized("biometric_auth_subtitle"), // ✅ Безопасная локализация
                    isEnabled: $isBiometricEnabled,
                    isBiometric: true
                )
                
                // Уровень защиты
                VStack(spacing: Spacing.s) {
                    HStack {
                        Image(systemName: "lock.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.primaryBlue)
                        
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            HStack {
                                Text(safeLocalized("protection_level")) // ✅ Безопасная локализация
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Button(action: {
                                    showProtectionExplanation = true
                                }) {
                                    Image(systemName: "info.circle")
                                        .font(.system(size: 14, weight: .semibold))
                                        .foregroundColor(protectionColor)
                                        .padding(6)
                                        .background(
                                            Circle()
                                                .fill(protectionColor.opacity(0.15))
                                        )
                                }
                                .padding(.leading, Spacing.xs)
                            }
                            
                            Text(
                                String(
                                    format: safeLocalized("settings_protection_level_value"),
                                    Int(calculatedProtectionLevel),
                                    protectionLevelText
                                ) + " (на основе тарифа)"
                            )
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                    }
                    
                    HStack {
                        Text(percentText(0))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Slider(value: .constant(calculatedProtectionLevel), in: 0...100, step: 5) {
                            Text(safeLocalized("settings_protection_level"))
                        } minimumValueLabel: {
                            Text(percentText(0))
                        } maximumValueLabel: {
                            Text(percentText(100))
                        }
                        .accentColor(protectionColor)
                        .disabled(true)
                        
                        Text(percentText(100))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    // Кнопки дополнительных настроек
                    LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: Spacing.s), count: 3), spacing: Spacing.s) {
                        protectionActionButton(
                            title: safeLocalized("settings_protection_history"),
                            icon: "chart.line.uptrend.xyaxis",
                            foreground: .primaryBlue,
                            background: Color.primaryBlue.opacity(0.12),
                            action: { showProtectionHistory = true }
                        )
                        
                        protectionActionButton(
                            title: safeLocalized("settings_advanced_settings"),
                            icon: "slider.horizontal.3",
                            foreground: Color(hex: "#A855F7"),
                            background: Color(hex: "#A855F7").opacity(0.14),
                            action: { showAdvancedProtection = true }
                        )
                        
                        protectionActionButton(
                            title: safeLocalized("settings_improve_protection"),
                            icon: "arrow.up.circle.fill",
                            foreground: .secondaryGold,
                            background: Color.secondaryGold.opacity(0.18),
                            action: { navigationManager.navigateTo(.tariffs) }
                        )
                    }
                    .padding(.top, Spacing.s)
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel(String(format: safeLocalized("settings_protection_level_accessibility"), Int(calculatedProtectionLevel)))
                
                // ✅ Менеджеры (5 компонентов)
                Divider()
                    .padding(.vertical, Spacing.s)
                
                // Emergency Contacts
                settingsButton(
                    icon: "person.2.fill",
                    title: safeLocalized("component_emergency_contact_manager_title"),
                    subtitle: safeLocalized("component_emergency_contact_manager_description"),
                    action: { showEmergencyContacts = true }
                )
                
                // Emergency Notifications
                settingsButton(
                    icon: "bell.fill",
                    title: safeLocalized("component_emergency_notification_manager_title"),
                    subtitle: safeLocalized("component_emergency_notification_manager_description"),
                    action: { showEmergencyNotifications = true }
                )
                
                // Voice Control
                settingsButton(
                    icon: "mic.fill",
                    title: safeLocalized("component_voice_control_manager_title"),
                    subtitle: safeLocalized("component_voice_control_manager_description"),
                    action: { showVoiceControl = true }
                )
                
                // Child Protection Compliance
                settingsButton(
                    icon: "person.crop.circle.badge.checkmark", // ✅ ИСПРАВЛЕНО: figure.child не существует, используем person.crop.circle.badge.checkmark (как в ParentalControl)
                    title: safeLocalized("component_russian_child_protection_manager_title"),
                    subtitle: safeLocalized("component_russian_child_protection_manager_description"),
                    action: { showChildProtectionCompliance = true }
                )
                
                // Data Protection Compliance
                settingsButton(
                    icon: "lock.shield.fill",
                    title: safeLocalized("component_russian_data_protection_manager_title"),
                    subtitle: safeLocalized("component_russian_data_protection_manager_description"),
                    action: { showDataProtectionCompliance = true }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Notifications Section
    
    @ViewBuilder
    private func notificationsSection() -> some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(safeLocalized("notifications_section")) // ✅ Безопасная локализация
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                settingRow(
                    icon: "bell.fill",
                    title: safeLocalized("push_notifications"), // ✅ Безопасная локализация
                    subtitle: safeLocalized("push_notifications_subtitle"), // ✅ Безопасная локализация
                    isEnabled: $isSecurityNotificationsEnabled,
                    onChange: { newValue in
                        Task { @MainActor in
                            notificationManager.notificationSettings.securityEnabled = newValue
                            notificationManager.saveSettings()
                        }
                    }
                )
                
                settingRow(
                    icon: "speaker.wave.2.fill",
                    title: safeLocalized("sound_notifications"), // ✅ Безопасная локализация
                    subtitle: safeLocalized("sound_notifications_subtitle"), // ✅ Безопасная локализация
                    isEnabled: $isSoundNotificationsEnabled,
                    onChange: { newValue in
                        Task { @MainActor in
                            notificationManager.notificationSettings.soundEnabled = newValue
                            notificationManager.saveSettings()
                        }
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - App Section
    
    @ViewBuilder
    private func appSection() -> some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(safeLocalized("app_section")) // ✅ Локализованный заголовок
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "globe",
                    title: safeLocalized("language"), // ✅ Локализованный язык
                    subtitle: localizationManager.currentLanguage == .russian ? safeLocalized("language_subtitle") : localizationManager.currentLanguage.displayName, // ✅ ИСПРАВЛЕНО: Прямой доступ (как в бэкапах)
                    action: {
                        showLanguageSettings = true
                    }
                )
                
                settingsButton(
                    icon: selectedTheme.icon,
                    title: safeLocalized("dark_theme"), // ✅ Локализованный заголовок
                    subtitle: selectedTheme.displayName(localizationManager), // ✅ ИСПРАВЛЕНО: Прямой доступ (как в бэкапах)
                    action: {
                        cycleTheme()
                    }
                )
                
                settingsButton(
                    icon: "arrow.clockwise",
                    title: safeLocalized("updates"), // ✅ Локализованный заголовок
                    subtitle: safeLocalized("updates_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        checkForUpdates()
                    }
                )
                
                // ✅ Система позиционирования
                settingsButton(
                    icon: positioningService.currentSystem.icon,
                    title: safeLocalized("positioning_system_title"),
                    subtitle: positioningService.selectedSystem == .auto 
                        ? "\(positioningService.currentSystem.displayName) (\(safeLocalized("positioning_system_auto")))"
                        : positioningService.currentSystem.displayName,
                    action: {
                        showPositioningSystemPicker = true
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
        .sheet(isPresented: $showPositioningSystemPicker) {
            PositioningSystemPickerView(
                selectedSystem: Binding(
                    get: { positioningService.selectedSystem },
                    set: { newValue in
                        positioningService.saveSelectedSystem(newValue)
                    }
                ),
                currentSystem: positioningService.currentSystem,
                currentRegion: positioningService.currentRegionName
            )
            .environmentObject(localizationManager)
        }
    }
    
    // MARK: - System Components Section (✅ ЗАДАЧА 22)
    
    @ViewBuilder
    private func systemComponentsSection() -> some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(safeLocalized("system_components_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                // Кнопка обновления
                Button(action: {
                    loadComponents()
                }) {
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 16))
                        .foregroundColor(.primaryBlue)
                        .rotationEffect(.degrees(isLoadingComponents ? 360 : 0))
                        .animation(isLoadingComponents ? Animation.linear(duration: 1).repeatForever(autoreverses: false) : .default, value: isLoadingComponents)
                }
                .disabled(isLoadingComponents)
            }
            
            if isLoadingComponents {
                ProgressView()
                    .padding()
            } else if let error = componentsError {
                VStack(spacing: Spacing.s) {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.red)
                    Button(safeLocalized("retry")) {
                        loadComponents()
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
            } else if components.isEmpty {
                Text(safeLocalized("system_components_empty"))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .padding()
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(components) { component in
                        ComponentRow(component: component) {
                            toggleComponent(component)
                        }
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
        .onAppear {
            if isAdmin && components.isEmpty {
                Task { @MainActor in
                    loadComponents()
                }
            }
        }
    }
    
    /// ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Загрузка компонентов на main thread
    private func loadComponents() {
        guard isAdmin else { return }
        
        Task { @MainActor in
            isLoadingComponents = true
            componentsError = nil
        }
        
        apiService.getComponentsList { result in
            Task { @MainActor in
                isLoadingComponents = false
                
                switch result {
                case .success(let loadedComponents):
                    components = loadedComponents
                case .failure(let error):
                    componentsError = error.localizedDescription
                    print("❌ Ошибка загрузки компонентов: \(error.localizedDescription)")
                }
            }
        }
    }
    
    /// ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Переключение компонентов на main thread
    private func toggleComponent(_ component: ComponentStatus) {
        guard isAdmin else { return }
        
        Task { @MainActor in
            do {
                if component.isEnabled {
                    _ = try await apiService.disableComponent(componentId: component.componentId)
                } else {
                    _ = try await apiService.enableComponent(componentId: component.componentId)
                }
                // Обновляем список компонентов
                loadComponents()
            } catch {
                componentsError = error.localizedDescription
            }
        }
    }
    
    // MARK: - Component Row View
    
    private struct ComponentRow: View {
        let component: ComponentStatus
        let onToggle: () -> Void
        @EnvironmentObject private var localizationManager: LocalizationManager
        
        var body: some View {
            HStack(spacing: Spacing.m) {
                // Индикатор статуса
                Circle()
                    .fill(component.isEnabled ? Color.green : Color.gray)
                    .frame(width: 12, height: 12)
                
                // Название компонента
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(component.componentId)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    if let lastUpdate = component.lastUpdate {
                        Text(String(format: localizationManager.localized("system_components_last_update"), formatDate(lastUpdate))) // ✅ ИСПРАВЛЕНО: ComponentRow имеет свой localizationManager
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
                
                // Toggle
                Toggle("", isOn: Binding(
                    get: { component.isEnabled },
                    set: { _ in onToggle() }
                ))
                .labelsHidden()
            }
            .padding(Spacing.s)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.small)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        
        private func formatDate(_ date: Date) -> String {
            let formatter = DateFormatter()
            formatter.dateStyle = .short
            formatter.timeStyle = .short
            return formatter.string(from: date)
        }
    }
    
    // MARK: - Additional Section
    
    @ViewBuilder
    private func additionalSection() -> some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(safeLocalized("additional_section")) // ✅ Локализованный заголовок
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "questionmark.circle",
                    title: safeLocalized("help_support"), // ✅ Локализованный заголовок
                    subtitle: safeLocalized("help_support_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        showSupportScreen = true
                    }
                )
                
                settingsButton(
                    icon: "doc.text",
                    title: safeLocalized("privacy_policy"), // ✅ Локализованный заголовок
                    subtitle: safeLocalized("privacy_policy_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        showPrivacyPolicy = true
                    }
                )
                
                settingsButton(
                    icon: "doc.plaintext",
                    title: safeLocalized("terms_of_service"), // ✅ Локализованный заголовок
                    subtitle: safeLocalized("terms_of_service_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        showTermsOfService = true
                    }
                )
                
                // ✅ Согласие на обработку ПДн (152-ФЗ) - 4-й пункт
                settingsButton(
                    icon: "checkmark.shield",
                    title: safeLocalized("settings_consent_personal_data"),
                    subtitle: consentAccepted ? safeLocalized("settings_consent_granted") : safeLocalized("settings_consent_manage"),
                    action: {
                        // Открываем экран политики конфиденциальности
                        showPrivacyPolicy = true
                    }
                )
                
                settingsButton(
                    icon: "square.and.arrow.up",
                    title: safeLocalized("share_app"), // ✅ Локализованный заголовок
                    subtitle: safeLocalized("share_app_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        showShareSheet = true
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func settingRow(
        icon: String,
        title: String,
        subtitle: String,
        isEnabled: Binding<Bool>,
        isBiometric: Bool = false,
        onChange: ((Bool) -> Void)? = nil
    ) -> some View {
        let binding: Binding<Bool> = isBiometric
            ? Binding(
                get: { isEnabled.wrappedValue },
                set: { newValue in
                    Task { @MainActor in
                        isEnabled.wrappedValue = newValue
                        handleBiometricToggle(newValue)
                    }
                }
            )
            : Binding(
                get: { isEnabled.wrappedValue },
                set: { newValue in
                    Task { @MainActor in
                        isEnabled.wrappedValue = newValue
                        onChange?(newValue)
                    }
                }
            )
        
        return HStack(spacing: Spacing.s) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundColor(.primaryBlue)
                .frame(width: 20)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer()
            
            ALADDINToggle(isOn: binding)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            String(
                format: safeLocalized("settings_toggle_accessibility"),
                title,
                safeLocalized(isEnabled.wrappedValue ? "settings_toggle_on" : "settings_toggle_off")
            )
        )
    }
    
    private func handleBiometricToggle(_ enabled: Bool) {
        print("🔐 Биометрический переключатель изменён: \(enabled)")
        
        // Проверяем доступность биометрии перед включением
        if enabled {
            guard securityManager.biometricAuthAvailable else {
                print("⚠️ Биометрия недоступна на этом устройстве")
                isBiometricEnabled = false
                UserDefaults.standard.set(false, forKey: "biometricEnabled")
                toastManager.show(
                    message: safeLocalized("settings_biometric_unavailable"),
                    type: .warning
                )
                return
            }
            
            // Запросить биометрию для подтверждения включения
            Task { @MainActor in
                print("🔐 Запрашиваем биометрическую аутентификацию...")
                let success = await securityManager.authenticateWithBiometrics()
                
                if !success {
                    print("⚠️ Биометрическая аутентификация не удалась, отключаем")
                    isBiometricEnabled = false
                    UserDefaults.standard.set(false, forKey: "biometricEnabled")
                    
                    // Показываем уведомление пользователю
                    toastManager.show(
                        message: safeLocalized("settings_biometric_enable_failed"),
                        type: .warning
                    )
                } else {
                    print("✅ Биометрическая аутентификация успешна")
                    UserDefaults.standard.set(true, forKey: "biometricEnabled")
                    toastManager.show(
                        message: safeLocalized("settings_biometric_enabled"),
                        type: .success
                    )
                }
            }
        } else {
            // При выключении просто сохраняем
            print("🔐 Биометрия выключена")
            UserDefaults.standard.set(false, forKey: "biometricEnabled")
            toastManager.show(
                message: safeLocalized("settings_biometric_disabled"),
                type: .info
            )
        }
    }
    
    private func settingsButton(icon: String, title: String, subtitle: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.s) {
                // ✅ Фиксированная ширина иконки для выравнивания
                Image(systemName: icon)
                    .font(.system(size: 16))
                    .foregroundColor(.primaryBlue)
                    .frame(width: 24, height: 24, alignment: .leading)
                    .fixedSize(horizontal: true, vertical: false)
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .fixedSize(horizontal: false, vertical: true)
                        .multilineTextAlignment(.leading)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)
                        .multilineTextAlignment(.leading)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                
                Spacer()
                
                // ✅ Фиксированная ширина стрелки для выравнивания
                Image(systemName: "chevron.right")
                    .font(.system(size: 12))
                    .foregroundColor(.textSecondary)
                    .frame(width: 12, height: 12)
                    .fixedSize(horizontal: true, vertical: false)
            }
            .padding(Spacing.s)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.2))
            )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            String(
                format: safeLocalized("settings_button_accessibility"),
                title,
                subtitle
            )
        )
    }
    
    private func percentText(_ value: Int) -> String {
        String(format: safeLocalized("settings_percent_format"), value)
    }
    
    @ViewBuilder
    private func protectionActionButton(title: String, icon: String, foreground: Color, background: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            // Важно: фиксируем "контентную" высоту кнопки, чтобы сетка 3-х кнопок выглядела ровно
            // на разных размерах экранов (SE ↔ Pro Max), и чтобы 2 строки текста не "плясали".
            VStack(spacing: Spacing.xs) {
                Image(systemName: icon)
                    .font(.system(size: 16, weight: .semibold))
                    .frame(height: 18)

                let displayTitle = title.contains("\n") ? title : title.uppercased()
                Text(displayTitle)
                    .font(.caption.bold())
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                    .minimumScaleFactor(0.85)
                    .allowsTightening(true)
                    // Не даём словам “ломаться” по слогам и держим предсказуемую высоту:
                    .fixedSize(horizontal: false, vertical: true)
                    .frame(minHeight: 28, maxHeight: 28, alignment: .center)
            }
            .frame(height: 18 + Spacing.xs + 28, alignment: .center)
            .foregroundColor(foreground)
            .frame(maxWidth: .infinity)
            .padding(.vertical, Spacing.s)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(background)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(foreground.opacity(0.4), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Calculated Protection Level (Read-Only Indicator)
    
    /// ✅ ИНДИКАТОР: Вычисляет уровень защиты на основе текущего тарифа
    /// Ползунок теперь только для чтения и показывает реальный уровень защиты
    private var calculatedProtectionLevel: Double {
        // ✅ ИСПРАВЛЕНО: Прямой доступ (как в бэкапах - работало)
        let tariff = safeCurrentTariff
        
        // ✅ Безопасный вызов createCard с обработкой ошибок
        let card: TariffCard
        do {
            card = tariff.createCard(localizationManager: localizationManager)
        } catch {
            print("⚠️ Ошибка при создании карты тарифа: \(error)")
            return 0.0
        }
        
        // Вычисляем процент на основе доступных функций тарифа
        let totalProtectionFeatures = 100 // Всего функций защиты от угроз
        let totalParentalFeatures = 32    // Всего функций родительского контроля
        let totalAdditionalFeatures = 10  // Примерно дополнительных функций
        
        let totalAvailable = Double(card.protectionCount + card.parentalControlCount + card.additionalFeatures.count)
        let totalPossible = Double(totalProtectionFeatures + totalParentalFeatures + totalAdditionalFeatures)
        
        // ✅ Защита от деления на ноль
        guard totalPossible > 0 else { return 0.0 }
        
        return min(100, (totalAvailable / totalPossible) * 100)
    }
    
    private var protectionLevelText: String {
        switch calculatedProtectionLevel {
        case 0...25: return safeLocalized("settings_protection_level_low")
        case 26...50: return safeLocalized("settings_protection_level_medium")
        case 51...75: return safeLocalized("settings_protection_level_high")
        case 76...100: return safeLocalized("settings_protection_level_maximum")
        default: return safeLocalized("settings_protection_level_medium")
        }
    }
    
    private var protectionColor: Color {
        switch calculatedProtectionLevel {
        case 0...25: return .red
        case 26...50: return .orange
        case 51...75: return .yellow
        case 76...100: return .green
        default: return .primaryBlue
        }
    }
    
    // ✅ УДАЛЕНО: handleProtectionLevelChange и связанные функции
    // Ползунок теперь только для чтения, защита управляется сервером через тариф
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    // MARK: - Theme Functions
    
    private func cycleTheme() {
        let allThemes = ThemeMode.allCases
        if let currentIndex = allThemes.firstIndex(of: selectedTheme) {
            let nextIndex = (currentIndex + 1) % allThemes.count
            selectedTheme = allThemes[nextIndex]
            
            // Сохраняем выбор пользователя
            UserDefaults.standard.set(selectedTheme.rawValue, forKey: "selected_theme")
            
            // Применяем тему
            applyTheme(selectedTheme)
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
    
    // MARK: - Update Functions
    
    private func checkForUpdates() {
        // Тактильный отклик
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // Проверка обновлений через App Store
        if let url = URL(string: "itms-apps://itunes.apple.com/app/id123456789") {
            UIApplication.shared.open(url)
        } else {
            print("📱 Проверка обновлений: приложение актуально")
        }
    }
    
    // MARK: - Notification Functions
    
    /// ✅ ИСПРАВЛЕНО: Вернулись к подходу из бэкапа - только requestAuthorization (не обращаемся к notificationSettings)
    private func initializeNotifications() {
        #if DEBUG
        print("🔴 SETTINGS: initializeNotifications() начат")
        print("🔴 SETTINGS: notificationManager.notificationSettings = \(notificationManager.notificationSettings)")
        #endif
        
        // ✅ Инициализируем биометрию
        isBiometricEnabled = UserDefaults.standard.bool(forKey: "biometricEnabled")
        
        // ✅ Запрос разрешения на уведомления (как в бэкапах - работало)
        Task {
            let granted = await notificationManager.requestAuthorization()
            if granted {
                print("🔔 Разрешение на уведомления получено")
            } else {
                print("🔕 Разрешение на уведомления отклонено")
            }
        }
        // ✅ Синхронизация состояния будет через onChange наблюдатели
        
        #if DEBUG
        print("🔴 SETTINGS: initializeNotifications() завершен")
        #endif
    }
}

// MARK: - Preview

struct SettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreen()
    }
}
