import SwiftUI
import Combine

// Master Logger for UI logging
private let logger = MasterLogger.shared

// AppCoordinator is accessed via shared instance

// Spacing is imported from Shared/Styles/Spacing.swift

// Временные определения типов для компиляции
typealias ALADDINScreen = String
typealias Language = String

/// ⚙️ Settings Screen - MVVM ВЕРСИЯ БЕЗ КРАШЕЙ
/// Экран настроек - управление приложением и профилем
/// Источник дизайна: /mobile/wireframes/05_settings_screen.html
struct SettingsScreen: View {
    @StateObject private var viewModel: SettingsViewModel

    // ✅ BUILD 95: Встроенный просмотр логов крашей/диагностики прямо на устройстве
    @State private var showCrashLogsView: Bool = false

    // ✅ BUILD 100: Убран testLogger из struct - логирование перемещено в .onAppear
    // Это предотвращает избыточное логирование при пересоздании View

    // Конструктор с dependency injection
    init(viewModel: SettingsViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }

    // Удобный конструктор для создания с mock сервисами
    init() {
        let viewModel = SettingsViewModel()
        _viewModel = StateObject(wrappedValue: viewModel)
    }
    
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
    
    // MARK: - Environment

    @Environment(\.dismiss) private var dismiss

    // MARK: - UI Sections

    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: viewModel.localizedStrings.settingsTitle,
            subtitle: viewModel.localizedStrings.settingsSubtitle,
            showBackButton: true,
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(viewModel.localizedStrings.settingsAccessibilityNavbar)
    }
    
    private var profileSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(viewModel.localizedStrings.profileSection)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
                .padding(.bottom, Spacing.xs)
                .accessibilityAddTraits(.isHeader)

            // Profile Card
            ZStack {
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.secondary.opacity(0.1))

                VStack(spacing: Spacing.m) {
                    // Avatar and Name
            HStack(spacing: Spacing.m) {
                        ZStack {
                Circle()
                                .fill(Color.blue.opacity(0.2))
                    .frame(width: 60, height: 60)

                        Text(userInitial)
                                .font(.title)
                                .fontWeight(.bold)
                                .foregroundColor(.blue)
                        }
                        .accessibilityLabel(viewModel.localizedStrings.profileAvatarAccessibility)
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(userName)
                                .font(.headline)
                                .foregroundColor(.textPrimary)
                                .accessibilityLabel(String(format: viewModel.localizedStrings.profileNameAccessibilityFormat, userName))
                    
                    Text(userAlias)
                                .font(.subheadline)
                                .foregroundColor(.textSecondary)
                                .accessibilityLabel(String(format: viewModel.localizedStrings.profileEmailAccessibilityFormat, userAlias))

                            Text(viewModel.localizedStrings.profileStatus)
                        .font(.caption)
                                .foregroundColor(.textSecondary)
                                .accessibilityLabel(String(format: viewModel.localizedStrings.profileStatusAccessibilityFormat, viewModel.localizedStrings.profileStatus))
                }
                
                Spacer()
                    }
                
                    // Edit Button
                Button(action: {
                        print("🧪 DIRECT PRINT: Edit Profile button tapped")
                        logger.buttonTap("Edit Profile", screen: "Settings")
                        print("🧪 DIRECT PRINT: Logger called for Edit Profile")
                        viewModel.showProfileEdit = true
                    }) {
                        HStack {
                            Text("Редактировать профиль")
                                .fontWeight(.medium)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.textSecondary)
                        }
                        .foregroundColor(.textPrimary)
                        .padding(.vertical, Spacing.s)
                    }
                    .accessibilityLabel(viewModel.localizedStrings.settingsProfileEditAccessibility)
                }
                .padding(Spacing.m)
            }
        }
    }

    private var userInitial: String {
        viewModel.displayName.isEmpty ? "?" : String(viewModel.displayName.prefix(1).uppercased())
    }

    private var userName: String {
        viewModel.displayName.isEmpty ? viewModel.localizedStrings.profileNamePlaceholder : viewModel.displayName
    }

    private var userAlias: String {
        viewModel.displayAlias.isEmpty ? viewModel.localizedStrings.profileEmailPlaceholder : viewModel.displayAlias
    }

    private var securitySection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(viewModel.localizedStrings.securitySection)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
                .padding(.bottom, Spacing.xs)
                .accessibilityAddTraits(.isHeader)

            VStack(spacing: 0) {
                // Network Protection
                settingRow(
                    icon: "shield.fill",
                    title: viewModel.localizedStrings.networkProtectionProtection,
                    subtitle: viewModel.localizedStrings.networkProtectionProtectionSubtitle,
                    isEnabled: $viewModel.isNetworkProtectionEnabled
                )

                Divider()

                // Biometric Auth
                settingRow(
                    icon: "faceid",
                    title: viewModel.localizedStrings.biometricAuth,
                    subtitle: viewModel.localizedStrings.biometricAuthSubtitle,
                    isEnabled: $viewModel.isBiometricEnabled,
                    isBiometric: true
                )
                
                Divider()

                // Protection Level
                            HStack {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(viewModel.localizedStrings.protectionLevel)
                            .font(.headline)
                            .foregroundColor(.textPrimary)

                        Text(String(format: viewModel.localizedStrings.settingsProtectionLevelValueFormat, Int(viewModel.cachedProtectionLevel)))
                            .font(.subheadline)
                            .foregroundColor(.textSecondary)

                        Text(viewModel.cachedProtectionLevelText)
                            .font(.caption)
                            .foregroundColor(viewModel.cachedProtectionColor)
                    }

                    Spacer()
                                
                                Button(action: {
                        viewModel.showProtectionExplanation = true
                                }) {
                                    Image(systemName: "info.circle")
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .accessibilityLabel(viewModel.localizedStrings.settingsProtectionLevelAccessibility)
            }
            .background(Color.secondary.opacity(0.05))
            .clipShape(RoundedRectangle(cornerRadius: 12))

            // Advanced Settings Button
            Button(action: {
                logger.buttonTap("Advanced Protection", screen: "Settings")
                viewModel.showAdvancedProtection = true
            }) {
                HStack {
                    Text(viewModel.localizedStrings.settingsAdvancedSettings)
                        .foregroundColor(.blue)
                        Spacer()
                    Image(systemName: "chevron.right")
                        .foregroundColor(.secondary)
                }
                .padding(Spacing.m)
                .background(Color.blue.opacity(0.1))
                .clipShape(RoundedRectangle(cornerRadius: 8))
            }
        }
    }

    private var notificationsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(viewModel.localizedStrings.notificationsSection)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
                .padding(.bottom, Spacing.xs)
                .accessibilityAddTraits(.isHeader)

            VStack(spacing: 0) {
                // Security Notifications (Push)
                settingRow(
                    icon: "bell.fill",
                    title: viewModel.localizedStrings.pushNotifications,
                    subtitle: viewModel.localizedStrings.pushNotificationsSubtitle,
                    isEnabled: $viewModel.securityEnabled
                )

                Divider()

                // Sound Notifications
                settingRow(
                    icon: "speaker.wave.2.fill",
                    title: viewModel.localizedStrings.soundNotifications,
                    subtitle: viewModel.localizedStrings.soundNotificationsSubtitle,
                    isEnabled: $viewModel.soundEnabled
                )
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }

    private var appSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(viewModel.localizedStrings.appSection)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
                .padding(.bottom, Spacing.xs)
                .accessibilityAddTraits(.isHeader)

            VStack(spacing: 0) {
                // Language
                Button(action: {
                    logger.buttonTap("Language Settings", screen: "Settings")
                    viewModel.showLanguageSettings = true
                }) {
            HStack {
                        Image(systemName: "globe")
                            .foregroundColor(.secondary)
                            .frame(width: 24)
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(viewModel.localizedStrings.language)
                                .foregroundColor(.primary)
                            Text(viewModel.localizedStrings.languageSubtitle)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundColor(.secondary)
                    }
                    .padding(Spacing.m)
                }

                Divider()

                // Theme
            HStack {
                    Image(systemName: viewModel.selectedTheme.icon)
                        .foregroundColor(.secondary)
                        .frame(width: 24)
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(viewModel.localizedStrings.darkTheme)
                            .foregroundColor(.primary)
                        Text(viewModel.selectedTheme.displayName)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                Spacer()
                    Button(action: {
                        logger.buttonTap("Cycle Theme", screen: "Settings")
                        viewModel.cycleTheme()
                    }) {
                        Image(systemName: "chevron.right")
                            .foregroundColor(.secondary)
                    }
                }
                .padding(Spacing.m)

                Divider()

                // Updates
                Button(action: {
                    logger.buttonTap("Check Updates", screen: "Settings")
                    viewModel.checkForUpdates()
                }) {
                    HStack {
                        Image(systemName: "arrow.clockwise")
                            .foregroundColor(.secondary)
                            .frame(width: 24)
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(viewModel.localizedStrings.updates)
                                .foregroundColor(.primary)
                            Text(viewModel.localizedStrings.updatesSubtitle)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundColor(.secondary)
                    }
                    .padding(Spacing.m)
                }

                Divider()

                // Positioning System
                Button(action: {
                    viewModel.showPositioningSystemPicker = true
                }) {
                    HStack {
                        Image(systemName: viewModel.selectedPositioningSystem.icon)
                            .foregroundColor(.secondary)
                            .frame(width: 24)
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text("Система позиционирования")
                                .foregroundColor(.primary)
                            Text(viewModel.selectedPositioningSystem.displayName)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundColor(.secondary)
                    }
                    .padding(Spacing.m)
                }
            }
            .background(Color.secondary.opacity(0.05))
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
    }
    
    private var systemComponentsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text(viewModel.localizedStrings.systemComponentsTitle)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                if viewModel.isLoadingComponents {
                    ProgressView()
                        .scaleEffect(0.8)
                } else {
                Button(action: {
                        viewModel.loadComponents()
                }) {
                    Image(systemName: "arrow.clockwise")
                            .foregroundColor(.blue)
                            .rotationEffect(.degrees(viewModel.isLoadingComponents ? 360 : 0))
                            .animation(viewModel.isLoadingComponents ? Animation.linear(duration: 1).repeatForever(autoreverses: false) : .default, value: viewModel.isLoadingComponents)
                    }
                    .disabled(viewModel.isLoadingComponents)
                }
            }
            .padding(.bottom, Spacing.xs)

            if let error = viewModel.componentsError {
                HStack {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                    Spacer()
                    Button(viewModel.localizedStrings.retry) {
                        viewModel.loadComponents()
                    }
                    .foregroundColor(.blue)
                    .font(.caption)
                }
                .padding(Spacing.m)
                .background(Color.red.opacity(0.1))
                .clipShape(RoundedRectangle(cornerRadius: 8))
            } else if viewModel.components.isEmpty {
                Text(viewModel.localizedStrings.systemComponentsEmpty)
                    .foregroundColor(.secondary)
                    .padding(Spacing.m)
                    .frame(maxWidth: .infinity, alignment: .center)
            } else {
                LazyVStack(spacing: 0) {
                    ForEach(viewModel.components, id: \.componentId) { component in
                        ComponentRow(component: component) {
                            viewModel.toggleComponent(component)
                        }
                    }
                }
                .background(Color.secondary.opacity(0.05))
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
        }
        .onAppear {
            if viewModel.isAdmin && viewModel.components.isEmpty {
                viewModel.loadComponents()
            }
        }
    }

    private var additionalSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(viewModel.localizedStrings.additionalSection)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)
                .padding(.bottom, Spacing.xs)

            VStack(spacing: 0) {
                // Help & Support
                Button(action: {
                    viewModel.showSupportScreen = true
                }) {
                    HStack {
                        Image(systemName: "questionmark.circle.fill")
                            .foregroundColor(.secondary)
                            .frame(width: 24)
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(viewModel.localizedStrings.helpSupport)
                                .foregroundColor(.primary)
                            Text(viewModel.localizedStrings.helpSupportSubtitle)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundColor(.secondary)
                    }
                    .padding(Spacing.m)
                }

                Divider()

                // Политика конфиденциальности
                settingsButton(
                    "doc.text",
                    viewModel.localizedStrings.privacyPolicy,
                    viewModel.localizedStrings.privacyPolicySubtitle
                ) {
                    viewModel.showPrivacyPolicy = true
                }

                // Условия использования
                settingsButton(
                    "doc.plaintext",
                    viewModel.localizedStrings.termsOfService,
                    viewModel.localizedStrings.termsOfServiceSubtitle
                ) {
                    viewModel.showTermsOfService = true
                }

                // Согласие на обработку персональных данных
                settingsButton(
                    "checkmark.shield",
                    viewModel.localizedStrings.settingsConsentPersonalData,
                    viewModel.consentAccepted ? viewModel.localizedStrings.settingsConsentGranted : viewModel.localizedStrings.settingsConsentManage
                ) {
                    viewModel.showPrivacyPolicy = true
                }

                // Поделиться приложением
                settingsButton(
                    "square.and.arrow.up",
                    viewModel.localizedStrings.shareApp,
                    viewModel.localizedStrings.shareAppSubtitle
                ) {
                    viewModel.showShareSheet = true
                }

                Divider()

                // ✅ BUILD 95: Диагностика (лог крашей/предупреждений памяти/Pre-Crash State)
                settingsButton(
                    "ladybug.fill",
                    "Диагностика (Crash Logs)",
                    "Просмотр/копирование/шаринг логов на устройстве"
                ) {
                    showCrashLogsView = true
                }

            }
            .background(Color.secondary.opacity(0.05))
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
    }

    // MARK: - Body
        
        var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(viewModel.localizedStrings.settingsAccessibilityBackground)

            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader

                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Profile Section
                        profileSection

                        // Security Section
                        securitySection

                        // Notifications Section
                        notificationsSection

                        // App Section
                        appSection

                        // System Components (только для админов)
                        if viewModel.isAdmin {
                            systemComponentsSection
                        }

                        // Additional Section
                        additionalSection

                        // Отступ снизу
                        Spacer(minLength: 100)
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(viewModel.localizedStrings.settingsAccessibilityList)
            }
        }
        .navigationBarHidden(true)
        .onAppear {
            // ✅ BUILD 100: Логирование загрузки экрана перемещено из testLogger в .onAppear
            // Это предотвращает избыточное логирование при пересоздании View
            logger.screenLoad("SettingsScreen")
            viewModel.initializeView()
        }
        .sheet(isPresented: $viewModel.showProfileEdit) {
            ProfileEditView()
        }
        .sheet(isPresented: $viewModel.showLanguageSettings) {
            LanguageSettingsScreen()
        }
        .sheet(isPresented: $viewModel.showSupportScreen) {
            SupportScreen()
        }
        .sheet(isPresented: $viewModel.showPrivacyPolicy) {
            PrivacyPolicyScreen()
        }
        .sheet(isPresented: $viewModel.showTermsOfService) {
            TermsOfServiceScreen()
        }
        .sheet(isPresented: $viewModel.showShareSheet) {
            ShareSheet(activityItems: [viewModel.localizedStrings.settingsShareMessage])
        }
        .sheet(isPresented: $showCrashLogsView) {
            CrashLogsView()
        }
        .sheet(isPresented: $viewModel.showProtectionExplanation) {
            ProtectionLevelExplanationModal(isPresented: $viewModel.showProtectionExplanation, currentTariff: viewModel.currentTariff)
        }
        .sheet(isPresented: $viewModel.showAdvancedProtection) {
            AdvancedProtectionSettingsScreen()
        }
        .sheet(isPresented: $viewModel.showProtectionHistory) {
            ProtectionLevelHistoryModal(isPresented: $viewModel.showProtectionHistory)
        }
        .sheet(isPresented: $viewModel.showEmergencyContacts) {
            EmergencyContactsView()
        }
        .sheet(isPresented: $viewModel.showEmergencyNotifications) {
            EmergencyNotificationsView()
        }
        .sheet(isPresented: $viewModel.showVoiceControl) {
            VoiceControlView()
        }
        .sheet(isPresented: $viewModel.showChildProtectionCompliance) {
            ComplianceView(section: .childProtection)
        }
        .sheet(isPresented: $viewModel.showDataProtectionCompliance) {
            ComplianceView(section: .dataProtection)
        }
        .sheet(isPresented: $viewModel.showPositioningSystemPicker) {
            PositioningSystemPickerView(
                selectedSystem: $viewModel.selectedPositioningSystem,
                currentSystem: viewModel.currentPositioningSystem,
                currentRegion: viewModel.currentRegionName
            )
        }
    }

    // MARK: - Helper Functions

    private func percentText(_ value: Int) -> String {
        "\(value)%"
    }

    private func settingsButton(_ icon: String, _ title: String, _ subtitle: String, action: @escaping () -> Void) -> some View {
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
                        .fixedSize(horizontal: false, vertical: true)
                        .multilineTextAlignment(.leading)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .lineLimit(2)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.textSecondary.opacity(0.6))
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.2))
            )
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title), \(subtitle)")
        .accessibilityAddTraits(.isButton)
    }

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
                    logger.toggleChanged("Biometric", newValue: newValue, screen: "Settings")
                    isEnabled.wrappedValue = newValue
                    viewModel.handleBiometricToggle(newValue)
                }
            )
            : isEnabled

        return HStack(spacing: Spacing.s) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundColor(.primaryBlue)
                .frame(width: 24, alignment: .leading)
                .fixedSize(horizontal: true, vertical: false)

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

            Toggle("", isOn: binding)
                .labelsHidden()
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title), включено")
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
                    // Не даём словам "ломаться" по слогам и держим предсказуемую высоту:
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
                            .stroke(Color.white.opacity(0.2), lineWidth: 0.5)
                    )
            )
        }
    }

    private struct ComponentRow: View {
        let component: SettingsComponentStatus
        let onToggle: () -> Void

        var body: some View {
            HStack {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(component.componentId.capitalized)
                        .font(.headline)
                        .foregroundColor(.primary)

                    Text("Системный компонент")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Toggle("", isOn: Binding(
                    get: { component.isEnabled },
                    set: { newValue in
                        logger.toggleChanged("Component: \(component.componentId)", newValue: newValue, screen: "Settings")
                        onToggle()
                    }
                ))
                .labelsHidden()
            }
            .padding(Spacing.m)
        }
    }
}
// MARK: - Preview
struct SettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        // Создаем mock ViewModel для preview
        let mockViewModel = SettingsViewModel()
        SettingsScreen(viewModel: mockViewModel)
    }
}

// MARK: - Mock Services for Preview
class MockNavigationService {
    func navigateTo(_ screen: ALADDINScreen) {}
}

class MockLocalizationService: LocalizationService {
    var currentLanguage: Language = "russian"
    var languageChanged: AnyPublisher<Language, Never> {
        Just("russian").eraseToAnyPublisher()
    }

    func localized(_ key: String) -> String { key }
    func localized(_ key: String, _ arguments: CVarArg...) -> String { key }
}

class MockNotificationService {
    var notificationSettings = NotificationSettings()

    func saveSettings() {}
    func requestAuthorization() async -> Bool { true }
    func sendLocalNotification(title: String, body: String, userInfo: [AnyHashable : Any]?) {}
    func updateNotificationSettings(_ settings: NotificationSettings) {}
}

class MockSecurityService {
    var biometricAuthAvailable: Bool = true
    func authenticateWithBiometrics() async -> Bool { true }
}

class MockTariffService {
    var currentTariff = "standard"
    func createCard(localizationService: Any) -> Any {
        return "mock card"
    }
}

// ✅ ПРОДАКШН: Mock сервисы удалены - используются только реальные сервисы



// MARK: - Preview Support (iOS 17+ only)
// Note: Preview functionality available in Xcode 15+ with iOS 17+
// For iOS 15.2 compatibility, previews are disabled
