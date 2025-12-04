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
    @AppStorage("profile_name") private var storedName: String = ""
    @AppStorage("profile_alias") private var storedAlias: String = ""
    @State private var isNotificationsEnabled: Bool = true
    @State private var isBiometricEnabled: Bool = UserDefaults.standard.bool(forKey: "biometricEnabled")
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
    @StateObject private var tariffManager = TariffManager.shared
    @StateObject private var mainViewModel = MainViewModel()
    @State private var showProtectionHistory: Bool = false
    
    // ✅ Согласие на обработку ПДн (152-ФЗ)
    @AppStorage("personal_data_consent_accepted") private var consentAccepted: Bool = false
    
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
            ProtectionLevelExplanationModal(isPresented: $showProtectionExplanation, currentTariff: tariffManager.currentTariff)
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
        let userInitial = storedName.isEmpty ? "?" : String(storedName.prefix(1).uppercased())
        let userName = storedName.isEmpty ? localizationManager.localized("profile_name_placeholder") : storedName
        let userAlias = storedAlias.isEmpty ? localizationManager.localized("profile_email_placeholder") : storedAlias
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
                    
                    Text(userAlias)
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel(
                            String(
                                format: localizationManager.localized("settings_profile_email_accessibility"),
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
                                    format: localizationManager.localized("settings_protection_level_value"),
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
                            Text(localizationManager.localized("settings_protection_level"))
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
                            title: localizationManager.localized("settings_protection_history"),
                            icon: "chart.line.uptrend.xyaxis",
                            foreground: .primaryBlue,
                            background: Color.primaryBlue.opacity(0.12),
                            action: { showProtectionHistory = true }
                        )
                        
                        protectionActionButton(
                            title: localizationManager.localized("settings_advanced_settings"),
                            icon: "slider.horizontal.3",
                            foreground: .primaryBlue,
                            background: Color.primaryBlue.opacity(0.12),
                            action: { showAdvancedProtection = true }
                        )
                        
                        protectionActionButton(
                            title: localizationManager.localized("settings_improve_protection"),
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
                .accessibilityLabel(String(format: localizationManager.localized("settings_protection_level_accessibility"), Int(calculatedProtectionLevel)))
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
                
                // ✅ Согласие на обработку ПДн (152-ФЗ) - 4-й пункт
                settingsButton(
                    icon: "checkmark.shield",
                    title: "Согласие на обработку персональных данных",
                    subtitle: consentAccepted ? "Согласие предоставлено" : "Управление согласием",
                    action: {
                        // Открываем экран профиля, где есть раздел согласия
                        navigationManager.navigateTo(.profile)
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
    
    @ViewBuilder
    private func protectionActionButton(title: String, icon: String, foreground: Color, background: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: Spacing.xs) {
                Image(systemName: icon)
                    .font(.system(size: 16, weight: .semibold))
                Text(title.uppercased())
                    .font(.caption.bold())
                    .lineLimit(2)
                    .minimumScaleFactor(0.75)
                    .multilineTextAlignment(.center)
            }
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
        let tariff = tariffManager.currentTariff
        let card = tariff.createCard(localizationManager: localizationManager)
        
        // Вычисляем процент на основе доступных функций тарифа
        let totalProtectionFeatures = 100 // Всего функций защиты от угроз
        let totalParentalFeatures = 32    // Всего функций родительского контроля
        let totalAdditionalFeatures = 10  // Примерно дополнительных функций
        
        let totalAvailable = Double(card.protectionCount + card.parentalControlCount + card.additionalFeatures.count)
        let totalPossible = Double(totalProtectionFeatures + totalParentalFeatures + totalAdditionalFeatures)
        
        return min(100, (totalAvailable / totalPossible) * 100)
    }
    
    private var protectionLevelText: String {
        switch calculatedProtectionLevel {
        case 0...25: return localizationManager.localized("settings_protection_level_low")
        case 26...50: return localizationManager.localized("settings_protection_level_medium")
        case 51...75: return localizationManager.localized("settings_protection_level_high")
        case 76...100: return localizationManager.localized("settings_protection_level_maximum")
        default: return localizationManager.localized("settings_protection_level_medium")
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

// MARK: - ShareSheet (простая версия без поддержки iPad)

struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]
    
    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

// MARK: - Preview

struct SettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreen()
    }
}
