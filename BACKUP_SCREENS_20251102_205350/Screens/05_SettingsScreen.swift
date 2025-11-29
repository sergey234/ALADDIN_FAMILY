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
        
        var displayName: String {
            switch self {
            case .light: return "Светлая"
            case .dark: return "Тёмная"
            case .system: return "Автоматически"
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
    @StateObject private var notificationManager = NotificationManager.shared
    @StateObject private var securityManager = SecurityManager.shared
    @State private var isVPNEnabled: Bool = true
    @State private var isNotificationsEnabled: Bool = true
    @State private var isBiometricEnabled: Bool = UserDefaults.standard.bool(forKey: "biometricEnabled")
    @State private var protectionLevel: Double = 75
    @State private var showProfileEdit: Bool = false
    @State private var showLanguageSettings: Bool = false
    @State private var showNotificationSettings: Bool = false
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
                .accessibilityLabel("Фон экрана настроек")
            
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
                        
                        // Дополнительно
                        additionalSection
                        
                        // Отступ снизу для удобства прокрутки
                        Spacer(minLength: 100)
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Список настроек приложения")
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showProfileEdit) {
            ProfileEditView()
        }
        .sheet(isPresented: $showLanguageSettings) {
            LanguageSettingsScreen()
        }
        .sheet(isPresented: $showNotificationSettings) {
            NotificationSettingsScreen()
                .environmentObject(notificationManager)
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
                "🎁 Присоединяйся к ALADDIN! Мы оба получим скидку -20% на 1 месяц после тестового периода! Используй мой код: ALADDIN-SH2024\n\nСкачай приложение: https://aladdin.family\n\nС тобой на защите! 🛡️"
            ])
        }
        .sheet(isPresented: $showProtectionExplanation) {
            ProtectionLevelExplanationModal(isPresented: $showProtectionExplanation, currentLevel: Int(protectionLevel))
        }
        .sheet(isPresented: $showAdvancedProtection) {
            AdvancedProtectionSettingsScreen()
        }
        .sheet(isPresented: $showProtectionHistory) {
            ProtectionLevelHistoryModal(isPresented: $showProtectionHistory)
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
            title: "НАСТРОЙКИ",
            subtitle: "Управление приложением",
            showBackButton: true,
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель настроек")
    }
    
    // MARK: - Profile Section
    
    private var profileSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ПРОФИЛЬ")
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
                        Text("С")
                            .font(.h2)
                            .foregroundColor(.white)
                    )
                    .accessibilityLabel("Аватар пользователя")
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text("Сергей Хлыстов")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .accessibilityLabel("Имя пользователя: Сергей Хлыстов")
                    
                    Text("sergey@aladdin.app")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel("Email: sergey@aladdin.app")
                    
                    Text("Premium подписка")
                        .font(.caption)
                        .foregroundColor(.primaryBlue)
                        .padding(.horizontal, Spacing.s)
                        .padding(.vertical, Spacing.xxs)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.small)
                                .fill(Color.primaryBlue.opacity(0.1))
                        )
                        .accessibilityLabel("Статус: Premium подписка")
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
                .accessibilityLabel("Редактировать профиль")
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
                Text("ЗАЩИТА И БЕЗОПАСНОСТЬ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                // VPN
                settingRow(
                    icon: "shield.fill",
                    title: "VPN защита",
                    subtitle: "Защищённое соединение",
                    isEnabled: $isVPNEnabled
                )
                
                // Биометрическая аутентификация
                settingRow(
                    icon: "faceid",
                    title: "Face ID / Touch ID",
                    subtitle: "Быстрый вход",
                    isEnabled: $isBiometricEnabled
                )
                
                // Уровень защиты
                VStack(spacing: Spacing.s) {
                    HStack {
                        Image(systemName: "lock.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.primaryBlue)
                        
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            HStack {
                                Text("Уровень защиты")
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
                            
                            Text("\(Int(protectionLevel))% - \(protectionLevelText)")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                    }
                    
                    HStack {
                        Text("0%")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Slider(value: $protectionLevel, in: 0...100, step: 5) {
                            Text("Уровень защиты")
                        } minimumValueLabel: {
                            Text("0%")
                        } maximumValueLabel: {
                            Text("100%")
                        }
                        .accentColor(protectionColor)
                        .onChange(of: protectionLevel) { newValue in
                            handleProtectionLevelChange(newValue)
                        }
                        
                        Text("100%")
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
                                Text("История защиты")
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
                                Text("Расширенные настройки")
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
                .accessibilityLabel("Уровень защиты: \(Int(protectionLevel))%")
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
                Text("УВЕДОМЛЕНИЯ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                settingRow(
                    icon: "bell.fill",
                    title: "Push уведомления",
                    subtitle: "Система ALADDIN отправляет уведомления о безопасности",
                    isEnabled: $notificationManager.notificationSettings.securityEnabled
                )
                
                settingRow(
                    icon: "speaker.wave.2.fill",
                    title: "Звуковые уведомления",
                    subtitle: "Звук при обнаружении угроз",
                    isEnabled: $notificationManager.notificationSettings.soundEnabled
                )
                
                // Кнопка для перехода в детальные настройки уведомлений
                settingsButton(
                    icon: "slider.horizontal.3",
                    title: "Настройки уведомлений",
                    subtitle: "Режимы, приоритеты, частота",
                    action: {
                        showNotificationSettings = true
                    }
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
                Text("ПРИЛОЖЕНИЕ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "globe",
                    title: "Язык",
                    subtitle: "Русский",
                    action: {
                        showLanguageSettings = true
                    }
                )
                
                settingsButton(
                    icon: selectedTheme.icon,
                    title: "Тёмная тема",
                    subtitle: selectedTheme.displayName,
                    action: {
                        cycleTheme()
                    }
                )
                
                settingsButton(
                    icon: "arrow.clockwise",
                    title: "Обновления",
                    subtitle: "Версия 1.0.0",
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
                Text("ДОПОЛНИТЕЛЬНО")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "questionmark.circle",
                    title: "Помощь и поддержка",
                    subtitle: "FAQ и контакты",
                    action: {
                        showSupportScreen = true
                    }
                )
                
                settingsButton(
                    icon: "doc.text",
                    title: "Политика конфиденциальности",
                    subtitle: "Как мы защищаем ваши данные",
                    action: {
                        showPrivacyPolicy = true
                    }
                )
                
                settingsButton(
                    icon: "doc.plaintext",
                    title: "Условия использования",
                    subtitle: "Правила использования сервиса",
                    action: {
                        showTermsOfService = true
                    }
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func settingRow(icon: String, title: String, subtitle: String, isEnabled: Binding<Bool>) -> some View {
        // Создаём специальный binding для Face ID / Touch ID
        let binding: Binding<Bool>
        if title == "Face ID / Touch ID" {
            binding = Binding(
                get: { isEnabled.wrappedValue },
                set: { newValue in
                    isEnabled.wrappedValue = newValue
                    handleBiometricToggle(newValue)
                }
            )
        } else {
            binding = isEnabled
        }
        
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
            
            // ✅ УНИФИЦИРОВАНО: Используем ALADDINToggle с размером 40 для соответствия дизайну карточек родительского контроля
            ALADDINToggle(isOn: binding, size: 40)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(isEnabled.wrappedValue ? "включено" : "выключено")")
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
                    message: "⚠️ Face ID / Touch ID недоступен\nНа этом устройстве нет биометрии",
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
                        message: "⚠️ Не удалось включить Face ID / Touch ID\nПроверьте настройки устройства",
                        type: .warning
                    )
                } else {
                    print("✅ Биометрическая аутентификация успешна")
                    UserDefaults.standard.set(true, forKey: "biometricEnabled")
                    toastManager.show(
                        message: "✅ Face ID / Touch ID включен",
                        type: .success
                    )
                }
            }
        } else {
            // При выключении просто сохраняем
            print("🔐 Биометрия выключена")
            UserDefaults.standard.set(false, forKey: "biometricEnabled")
            toastManager.show(
                message: "Face ID / Touch ID выключен",
                type: .info
            )
        }
    }
    
    private func settingsButton(icon: String, title: String, subtitle: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.s) {
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
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.s)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.2))
            )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(subtitle)")
    }
    
    private var protectionLevelText: String {
        switch protectionLevel {
        case 0...25: return "Низкий"
        case 26...50: return "Средний"
        case 51...75: return "Высокий"
        case 76...100: return "Максимальный"
        default: return "Средний"
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
            message = "⚠️ Низкий уровень защиты\nВключено \(enabledCount) функций"
            toastType = .warning
        case 26...50:
            message = "⚠️ Средний уровень защиты\nВключено \(enabledCount) функций"
            toastType = .warning
        case 51...75:
            message = "✅ Высокий уровень защиты\nВключено \(enabledCount) функций"
            toastType = .success
        case 76...100:
            message = "🛡️ Максимальный уровень защиты\nВключено \(enabledCount) функций"
            toastType = .success
        default:
            message = "Уровень защиты: \(Int(level))%"
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
                    message: "⚠️ Низкий уровень защиты!\nРекомендуем увеличить для лучшей защиты семьи",
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
