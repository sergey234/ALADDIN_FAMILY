import SwiftUI
import Combine

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
        HStack {
            Button(action: {
                dismiss()
            }) {
                Image(systemName: "chevron.left")
                    .foregroundColor(.primary)
                    .padding(Spacing.s)
                    .background(Color.secondary.opacity(0.1))
                    .clipShape(Circle())
            }

            Spacer()

            Text(viewModel.localizedStrings.settingsTitle)
                .font(.headline)
                .foregroundColor(.primary)

            Spacer()

            // Пустая кнопка для симметрии
            Color.clear
                .frame(width: 44, height: 44)
                    }
                    .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.m)
        .background(Color.clear)
                .accessibilityElement(children: .contain)
        .accessibilityLabel(viewModel.localizedStrings.settingsAccessibilityNavbar)
    }
    
    private var profileSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(viewModel.localizedStrings.profileSection)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.primary)
                .padding(.bottom, Spacing.xs)

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
                                .foregroundColor(.primary)
                                .accessibilityLabel(String(format: viewModel.localizedStrings.profileNameAccessibilityFormat, userName))
                    
                    Text(userAlias)
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                                .accessibilityLabel(String(format: viewModel.localizedStrings.profileEmailAccessibilityFormat, userAlias))

                            Text(viewModel.localizedStrings.profileStatus)
                        .font(.caption)
                                .foregroundColor(.secondary)
                                .accessibilityLabel(String(format: viewModel.localizedStrings.profileStatusAccessibilityFormat, viewModel.localizedStrings.profileStatus))
                }
                
                Spacer()
                    }
                
                    // Edit Button
                Button(action: {
                        viewModel.showProfileEdit = true
                    }) {
                        HStack {
                            Text("Редактировать профиль")
                                .fontWeight(.medium)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundColor(.secondary)
                        }
                        .foregroundColor(.primary)
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
                .foregroundColor(.primary)
                .padding(.bottom, Spacing.xs)

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
                            .foregroundColor(.primary)

                        Text(String(format: viewModel.localizedStrings.settingsProtectionLevelValueFormat, Int(viewModel.cachedProtectionLevel)))
                            .font(.subheadline)
                            .foregroundColor(.secondary)

                        Text(viewModel.cachedProtectionLevelText)
                            .font(.caption)
                            .foregroundColor(viewModel.cachedProtectionColor)
                    }

                    Spacer()
                                
                                Button(action: {
                        viewModel.showProtectionExplanation = true
                                }) {
                                    Image(systemName: "info.circle")
                            .foregroundColor(.secondary)
                    }
                }
                .padding(Spacing.m)
                .accessibilityLabel(viewModel.localizedStrings.settingsProtectionLevelAccessibility)
            }
            .background(Color.secondary.opacity(0.05))
            .clipShape(RoundedRectangle(cornerRadius: 12))

            // Advanced Settings Button
            Button(action: {
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
                .foregroundColor(.primary)
                .padding(.bottom, Spacing.xs)

            VStack(spacing: 0) {
                // Push Notifications
                settingRow(
                    icon: "bell.fill",
                    title: viewModel.localizedStrings.pushNotifications,
                    subtitle: viewModel.localizedStrings.pushNotificationsSubtitle,
                    isEnabled: $viewModel.isNotificationsEnabled
                )

                Divider()

                // Security Notifications
                settingRow(
                    icon: "exclamationmark.triangle.fill",
                    title: "Уведомления безопасности",
                    subtitle: "Важные оповещения о безопасности",
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
            .background(Color.secondary.opacity(0.05))
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
    }

    private var appSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(viewModel.localizedStrings.appSection)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.primary)
                .padding(.bottom, Spacing.xs)

            VStack(spacing: 0) {
                // Language
                Button(action: {
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
                    }
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
                VStack(spacing: 0) {
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
    }

    private var additionalSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(viewModel.localizedStrings.additionalSection)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(.primary)
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

                // Privacy Policy
                Button(action: {
                    viewModel.showPrivacyPolicy = true
                }) {
                    HStack {
                        Image(systemName: "hand.raised.fill")
                            .foregroundColor(.secondary)
                            .frame(width: 24)
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(viewModel.localizedStrings.privacyPolicy)
                                .foregroundColor(.primary)
                            Text(viewModel.localizedStrings.privacyPolicySubtitle)
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

                // Terms of Service
                Button(action: {
                    viewModel.showTermsOfService = true
                }) {
                    HStack {
                        Image(systemName: "doc.text.fill")
                            .foregroundColor(.secondary)
                            .frame(width: 24)
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(viewModel.localizedStrings.termsOfService)
                                .foregroundColor(.primary)
                            Text(viewModel.localizedStrings.termsOfServiceSubtitle)
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

                // Share App
                Button(action: {
                    viewModel.showShareSheet = true
                }) {
                    HStack {
                        Image(systemName: "square.and.arrow.up.fill")
                            .foregroundColor(.secondary)
                            .frame(width: 24)
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(viewModel.localizedStrings.shareApp)
                                .foregroundColor(.primary)
                            Text(viewModel.localizedStrings.shareAppSubtitle)
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
        .sheet(isPresented: $viewModel.showProtectionExplanation) {
            Text("Protection Explanation Screen - Coming Soon")
        }
        .sheet(isPresented: $viewModel.showAdvancedProtection) {
            Text("Advanced Protection Screen - Coming Soon")
        }
        .sheet(isPresented: $viewModel.showProtectionHistory) {
            Text("Protection History Screen - Coming Soon")
        }
        .sheet(isPresented: $viewModel.showEmergencyContacts) {
            Text("Emergency Contacts Screen - Coming Soon")
        }
        .sheet(isPresented: $viewModel.showEmergencyNotifications) {
            Text("Emergency Notifications Screen - Coming Soon")
        }
        .sheet(isPresented: $viewModel.showVoiceControl) {
            Text("Voice Control Screen - Coming Soon")
        }
        .sheet(isPresented: $viewModel.showChildProtectionCompliance) {
            Text("Child Protection Compliance Screen - Coming Soon")
        }
        .sheet(isPresented: $viewModel.showDataProtectionCompliance) {
            Text("Data Protection Compliance Screen - Coming Soon")
        }
        .sheet(isPresented: $viewModel.showPositioningSystemPicker) {
            Text("Positioning System Picker - Coming Soon")
        }
    }
    }
    
    // MARK: - Helper Views
    
private func settingRow(icon: String, title: String, subtitle: String? = nil, isEnabled: Binding<Bool>, isBiometric: Bool = false) -> some View {
    HStack {
            Image(systemName: icon)
            .foregroundColor(.secondary)
            .frame(width: 24)
            
        VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(title)
                .foregroundColor(.primary)
                .font(.headline)
                
            if let subtitle = subtitle {
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            }
            
            Spacer()
            
        if isBiometric {
            Button(action: {
                isEnabled.wrappedValue.toggle()
            }) {
                Image(systemName: isEnabled.wrappedValue ? "faceid" : "faceid")
                    .foregroundColor(isEnabled.wrappedValue ? .green : .secondary)
                    .font(.title2)
            }
                } else {
            Toggle("", isOn: isEnabled)
                .labelsHidden()
        }
    }
    .padding(Spacing.m)
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
                set: { _ in onToggle() }
            ))
            .labelsHidden()
        }
        .padding(Spacing.m)
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

class SettingsMockAPIService {
    func getComponentsList(completion: @escaping (Result<[Any], Error>) -> Void) {
        completion(.success([]))
    }
    func enableComponent(componentId: String) async throws -> Any {
        return "enabled"
    }
    func disableComponent(componentId: String) async throws -> Any {
        return "disabled"
    }
}

class MockPositioningService {
    var currentSystem = PositioningSystem.gps
    var selectedSystem = PositioningSystem.gps
    var currentRegionName: String = "Russia"
    func saveSelectedSystem(_ system: PositioningSystem) {}
}
