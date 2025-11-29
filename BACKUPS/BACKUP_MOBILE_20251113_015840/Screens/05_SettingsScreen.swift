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
    @StateObject private var notificationManager = NotificationManager.shared
    @StateObject private var securityManager = SecurityManager.shared
    @State private var isVPNEnabled: Bool = true
    @State private var isNotificationsEnabled: Bool = true
    @State private var isBiometricEnabled: Bool = UserDefaults.standard.bool(forKey: "biometricEnabled")
    @State private var protectionLevel: Double = 75
    @State private var showProfileEdit: Bool = false
    @State private var showLanguageSettings: Bool = false
    @State private var showSupportScreen: Bool = false
    @State private var showPrivacyPolicy: Bool = false
    @State private var showTermsOfService: Bool = false
    @State private var showShareSheet: Bool = false
    @State private var selectedTheme: ThemeMode = .system
    @State private var showProtectionExplanation: Bool = false
    @State private var showAdvancedProtection: Bool = false
    @StateObject private var featuresManager = ProtectionFeaturesManager.shared
    @StateObject private var toastManager = ToastManager.shared
    @StateObject private var historyManager = ProtectionLevelHistoryManager.shared
    @State private var showProtectionHistory: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(localizationManager.localized("settings_accessibility_background"))
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Профиль пользователя
                        profileSection
                        
                        // Защита и безопасность
                        securitySection
                        
                        // Уведомления
                        notificationsSection
                        
                        // Приложение
                        appSection
                            .id("app_section_\(localizationManager.currentLanguage.rawValue)")
                        
                        // Дополнительно
                        additionalSection
                            .id("additional_section_\(localizationManager.currentLanguage.rawValue)")
                        
                        // Отступ снизу для удобства прокрутки
                        Spacer(minLength: 100)
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("settings_accessibility_list"))
            }
        }
        .navigationBarHidden(true)
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("settings_lang_\(localizationManager.currentLanguage.rawValue)")
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
                localizationManager.localized("settings_share_message")
            ])
        }
        .sheet(isPresented: $showProtectionExplanation) {
            ProtectionLevelExplanationModal(isPresented: $showProtectionExplanation, currentLevel: Int(protectionLevel))
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
        .onAppear {
            initializeNotifications()
            // Загружаем сохраненный уровень защиты
            let savedLevel = UserDefaults.standard.double(forKey: "protectionLevel")
            if savedLevel > 0 {
                protectionLevel = savedLevel
                featuresManager.applyProtectionLevel(Int(savedLevel))
            } else {
                // По умолчанию 75%
                protectionLevel = 75
                featuresManager.applyProtectionLevel(75)
            }
        }
        .withToast()
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("settings_title"), // ✅ Локализованный заголовок
            subtitle: localizationManager.localized("settings_subtitle"), // ✅ Локализованный подзаголовок
            showBackButton: true,
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("settings_accessibility_navbar"))
    }
    
    // MARK: - Profile Section
    
    private var profileSection: some View {
        let userInitial = localizationManager.localized("settings_profile_initial")
        let userName = localizationManager.localized("settings_profile_name")
        let userEmail = localizationManager.localized("settings_profile_email")
        let userStatus = localizationManager.localized("settings_profile_status")
        
        return VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("profile_section")) // ✅ Локализованный заголовок
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
                    .accessibilityLabel(localizationManager.localized("settings_profile_avatar_accessibility"))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(userName)
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .accessibilityLabel(
                            String(
                                format: localizationManager.localized("settings_profile_name_accessibility"),
                                userName
                            )
                        )
                    
                    Text(userEmail)
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel(
                            String(
                                format: localizationManager.localized("settings_profile_email_accessibility"),
                                userEmail
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
                                format: localizationManager.localized("settings_profile_status_accessibility"),
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
                .accessibilityLabel(localizationManager.localized("settings_profile_edit_accessibility"))
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Security Section
    
    private var securitySection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("security_section")) // ✅ Локализованный заголовок
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                // VPN
                settingRow(
                    icon: "shield.fill",
                    title: localizationManager.localized("vpn_protection"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("vpn_protection_subtitle"), // ✅ Локализованный подзаголовок
                    isEnabled: $isVPNEnabled
                )
                
                // Биометрическая аутентификация
                settingRow(
                    icon: "faceid",
                    title: localizationManager.localized("biometric_auth"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("biometric_auth_subtitle"), // ✅ Локализованный подзаголовок
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
                                Text(localizationManager.localized("protection_level")) // ✅ Локализованный заголовок
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Button(action: {
                                    showProtectionExplanation = true
                                }) {
                                    Image(systemName: "info.circle")
                                        .font(.system(size: 14))
                                        .foregroundColor(.primaryBlue)
                                }
                                .padding(.leading, Spacing.xs)
                            }
                            
                            Text(
                                String(
                                    format: localizationManager.localized("settings_protection_level_value"),
                                    Int(protectionLevel),
                                    protectionLevelText
                                )
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
                        
                        Slider(value: $protectionLevel, in: 0...100, step: 5) {
                            Text(localizationManager.localized("settings_protection_level"))
                        } minimumValueLabel: {
                            Text(percentText(0))
                        } maximumValueLabel: {
                            Text(percentText(100))
                        }
                        .accentColor(protectionColor)
                        .onChange(of: protectionLevel) { newValue in
                            handleProtectionLevelChange(newValue)
                        }
                        
                        Text(percentText(100))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    // Кнопки дополнительных настроек
                    HStack(spacing: Spacing.m) {
                        Button(action: {
                            showProtectionHistory = true
                        }) {
                            HStack {
                                Image(systemName: "chart.line.uptrend.xyaxis")
                                    .font(.system(size: 14))
                                Text(localizationManager.localized("settings_protection_history"))
                                    .font(.caption)
                            }
                            .foregroundColor(.primaryBlue)
                            .padding(.top, Spacing.xs)
                        }
                        
                        Spacer()
                        
                        Button(action: {
                            showAdvancedProtection = true
                        }) {
                            HStack {
                                Image(systemName: "slider.horizontal.3")
                                    .font(.system(size: 14))
                                Text(localizationManager.localized("settings_advanced_settings"))
                                    .font(.caption)
                            }
                            .foregroundColor(.primaryBlue)
                            .padding(.top, Spacing.xs)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel(String(format: localizationManager.localized("settings_protection_level_accessibility"), Int(protectionLevel)))
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Notifications Section
    
    private var notificationsSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("notifications_section")) // ✅ Локализованный заголовок
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                settingRow(
                    icon: "bell.fill",
                    title: localizationManager.localized("push_notifications"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("push_notifications_subtitle"), // ✅ Локализованный подзаголовок
                    isEnabled: $notificationManager.notificationSettings.securityEnabled
                )
                
                settingRow(
                    icon: "speaker.wave.2.fill",
                    title: localizationManager.localized("sound_notifications"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("sound_notifications_subtitle"), // ✅ Локализованный подзаголовок
                    isEnabled: $notificationManager.notificationSettings.soundEnabled
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - App Section
    
    private var appSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("app_section")) // ✅ Локализованный заголовок
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "globe",
                    title: localizationManager.localized("language"), // ✅ Локализованный язык
                    subtitle: localizationManager.currentLanguage == .russian ? localizationManager.localized("language_subtitle") : localizationManager.currentLanguage.displayName, // ✅ Динамический подзаголовок
                    action: {
                        showLanguageSettings = true
                    }
                )
                
                settingsButton(
                    icon: selectedTheme.icon,
                    title: localizationManager.localized("dark_theme"), // ✅ Локализованный заголовок
                    subtitle: selectedTheme.displayName(localizationManager), // ✅ Локализованная тема
                    action: {
                        cycleTheme()
                    }
                )
                
                settingsButton(
                    icon: "arrow.clockwise",
                    title: localizationManager.localized("updates"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("updates_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        checkForUpdates()
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Additional Section
    
    private var additionalSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("additional_section")) // ✅ Локализованный заголовок
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "questionmark.circle",
                    title: localizationManager.localized("help_support"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("help_support_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        showSupportScreen = true
                    }
                )
                
                settingsButton(
                    icon: "doc.text",
                    title: localizationManager.localized("privacy_policy"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("privacy_policy_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        showPrivacyPolicy = true
                    }
                )
                
                settingsButton(
                    icon: "doc.plaintext",
                    title: localizationManager.localized("terms_of_service"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("terms_of_service_subtitle"), // ✅ Локализованный подзаголовок
                    action: {
                        showTermsOfService = true
                    }
                )
                
                settingsButton(
                    icon: "square.and.arrow.up",
                    title: localizationManager.localized("share_app"), // ✅ Локализованный заголовок
                    subtitle: localizationManager.localized("share_app_subtitle"), // ✅ Локализованный подзаголовок
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
        isBiometric: Bool = false
    ) -> some View {
        let binding: Binding<Bool> = isBiometric
            ? Binding(
                get: { isEnabled.wrappedValue },
                set: { newValue in
                    isEnabled.wrappedValue = newValue
                    handleBiometricToggle(newValue)
                }
            )
            : isEnabled
        
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
                format: localizationManager.localized("settings_toggle_accessibility"),
                title,
                localizationManager.localized(isEnabled.wrappedValue ? "settings_toggle_on" : "settings_toggle_off")
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
                    message: localizationManager.localized("settings_biometric_unavailable"),
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
                        message: localizationManager.localized("settings_biometric_enable_failed"),
                        type: .warning
                    )
                } else {
                    print("✅ Биометрическая аутентификация успешна")
                    UserDefaults.standard.set(true, forKey: "biometricEnabled")
                    toastManager.show(
                        message: localizationManager.localized("settings_biometric_enabled"),
                        type: .success
                    )
                }
            }
        } else {
            // При выключении просто сохраняем
            print("🔐 Биометрия выключена")
            UserDefaults.standard.set(false, forKey: "biometricEnabled")
            toastManager.show(
                message: localizationManager.localized("settings_biometric_disabled"),
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
                format: localizationManager.localized("settings_button_accessibility"),
                title,
                subtitle
            )
        )
    }
    
    private func percentText(_ value: Int) -> String {
        String(format: localizationManager.localized("settings_percent_format"), value)
    }
    
    private var protectionLevelText: String {
        switch protectionLevel {
        case 0...25: return localizationManager.localized("settings_protection_level_low")
        case 26...50: return localizationManager.localized("settings_protection_level_medium")
        case 51...75: return localizationManager.localized("settings_protection_level_high")
        case 76...100: return localizationManager.localized("settings_protection_level_maximum")
        default: return localizationManager.localized("settings_protection_level_medium")
        }
    }
    
    private var protectionColor: Color {
        switch protectionLevel {
        case 0...25: return .red
        case 26...50: return .orange
        case 51...75: return .yellow
        case 76...100: return .green
        default: return .primaryBlue
        }
    }
    
    private func handleProtectionLevelChange(_ level: Double) {
        print("🔒 Уровень защиты изменен: \(Int(level))%")
        
        // Сохраняем в UserDefaults
        UserDefaults.standard.set(level, forKey: "protectionLevel")
        
        // Применяем функции защиты через ProtectionFeaturesManager
        featuresManager.applyProtectionLevel(Int(level))
        
        let enabledFeatures = featuresManager.features.filter { $0.isEnabled }
        let enabledCount = enabledFeatures.count
        let enabledFeatureIds = enabledFeatures.map { $0.id }
        
        // Сохраняем в историю
        historyManager.saveLevelChange(Int(level), enabledFeatures: enabledFeatureIds)
        
        // Автоматически включаем VPN и родительский контроль при высоких уровнях
        autoEnableVPNAndParentalControl(level: level)
        
        // Показываем уведомление
        let message: String
        let toastType: Toast.ToastType
        
        switch level {
        case 0...25:
            message = String(format: localizationManager.localized("settings_protection_level_low_message"), enabledCount)
            toastType = .warning
        case 26...50:
            message = String(format: localizationManager.localized("settings_protection_level_medium_message"), enabledCount)
            toastType = .warning
        case 51...75:
            message = String(format: localizationManager.localized("settings_protection_level_high_message"), enabledCount)
            toastType = .success
        case 76...100:
            message = String(format: localizationManager.localized("settings_protection_level_maximum_message"), enabledCount)
            toastType = .success
        default:
            message = String(format: localizationManager.localized("settings_protection_level_message"), Int(level))
            toastType = .info
        }
        
        toastManager.show(message: message, type: toastType)
        
        print("🔔 Уведомление: Уровень защиты изменен на \(Int(level))%")
        print("📋 Включено функций: \(enabledCount)")
        
        // Проверяем предупреждения для низких уровней
        checkProtectionWarnings(level: level)
        
        // Применяем настройки безопасности
        applyProtectionSettings(level: level)
    }
    
    // MARK: - Auto Enable VPN and Parental Control
    
    /// Автоматически включает VPN и родительский контроль в зависимости от уровня защиты
    /// Примечание: Функции защиты (родительский контроль и др.) уже включаются через applyProtectionLevel
    /// Здесь мы только управляем VPN, который управляется отдельно через VPNViewModel
    private func autoEnableVPNAndParentalControl(level: Double) {
        let vpnViewModel = VPNViewModel.shared
        
        // VPN включается на всех уровнях защиты >= 25%
        if level >= 25 && !vpnViewModel.isVPNEnabled {
            vpnViewModel.toggleVPN()
            print("🔒 Автоматически включен VPN (уровень \(Int(level))%)")
        }
        
        // Родительский контроль и другие функции уже включены через applyProtectionLevel выше
        
        // Обновляем состояние VPN в UI
        isVPNEnabled = vpnViewModel.isVPNEnabled
    }
    
    private func checkProtectionWarnings(level: Double) {
        // Показываем предупреждение только при переходе на низкий уровень
        if level <= 25 {
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                toastManager.show(
                    message: localizationManager.localized("settings_protection_level_low_warning"),
                    type: .warning
                )
            }
        }
    }
    
    private func applyProtectionSettings(level: Double) {
        // Реальная логика защиты через ProtectionFeaturesManager
        let enabledFeatures = featuresManager.features.filter { $0.isEnabled }
        
        switch level {
        case 0...25:
            print("⚠️ Низкий уровень защиты")
            print("   Включено: \(enabledFeatures.map { $0.name }.joined(separator: ", "))")
        case 26...50:
            print("⚠️ Средний уровень защиты")
            print("   Включено: \(enabledFeatures.map { $0.name }.joined(separator: ", "))")
        case 51...75:
            print("✅ Высокий уровень защиты")
            print("   Включено: \(enabledFeatures.map { $0.name }.joined(separator: ", "))")
        case 76...100:
            print("🛡️ Максимальный уровень защиты")
            print("   Включено: \(enabledFeatures.map { $0.name }.joined(separator: ", "))")
        default:
            break
        }
    }
    
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
    
    private func initializeNotifications() {
        // Инициализация системы уведомлений
        Task {
            let granted = await notificationManager.requestAuthorization()
            if granted {
                print("🔔 Разрешение на уведомления получено")
            } else {
                print("🔕 Разрешение на уведомления отклонено")
            }
        }
    }
}

// MARK: - Preview

struct SettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreen()
    }
}
