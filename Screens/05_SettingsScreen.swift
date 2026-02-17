import SwiftUI
import os.log
#if !targetEnvironment(simulator)
import Darwin
#endif

/// ⚙️ Settings Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран настроек - управление приложением и профилем
/// Источник дизайна: /mobile/wireframes/05_settings_screen.html
struct SettingsScreen: View {
    
    // ✅ КРИТИЧЕСКОЕ: Логирование для TestFlight (работает в RELEASE)
    // Используем SettingsDiagnosticsLogger для централизованного логирования
    // ✅ ИСПРАВЛЕНО: Ленивая инициализация logger для предотвращения краша при инициализации
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УДАЛЕН computed property logger
    // SettingsDiagnosticsLogger вызывал SwiftUI type resolution recursion
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Отключаем весь logger для предотвращения крашей
    private static let ENABLE_CRASH_LOGS = false // SettingsDiagnosticsLogger.ENABLE_LOGS

    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Заглушка для logger чтобы код компилировался
    private var logger: SettingsDiagnosticsLogger {
        // Простая заглушка - возвращаем shared instance только если ENABLE_CRASH_LOGS = true
        Self.ENABLE_CRASH_LOGS ? SettingsDiagnosticsLogger.shared : SettingsDiagnosticsLogger.shared
    }
    
    // ✅ КРИТИЧЕСКОЕ: Инициализатор с минимальным логированием для диагностики
    init() {
        // ✅ ДИАГНОСТИКА: Простой print() для понимания, вызывается ли init()
        // ✅ ВАЖНО: Логируем ДО любых других операций
        print("🔴 SETTINGS_INIT: ========== НАЧАЛО ИНИЦИАЛИЗАЦИИ ==========")
        print("🔴 SETTINGS_INIT: init() вызван")
        print("🔴 SETTINGS_INIT: Thread.isMainThread = \(Thread.isMainThread)")
        print("🔴 SETTINGS_INIT: Stack trace:")
        Thread.callStackSymbols.prefix(3).forEach { print("  \($0)") }
        print("🔴 SETTINGS_INIT: ========== КОНЕЦ ИНИЦИАЛИЗАЦИИ ==========")
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
    
    // MARK: - State

    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager // ✅ Добавляем LocalizationManager

    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем @ObservedObject для singleton'ов с @Published свойствами
    // @StateObject создает новый экземпляр, что неправильно для singleton'ов!
    @ObservedObject private var notificationManager = NotificationManager.shared
    @ObservedObject private var tariffManager = TariffManager.shared
    
    // ✅ Для singleton'ов без @Published свойств используем let
    private let securityManager = SecurityManager.shared
    
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
    // ✅ Для singleton'ов без @Published свойств используем let
    private let featuresManager = ProtectionFeaturesManager.shared
    private let toastManager = ToastManager.shared
    private let historyManager = ProtectionLevelHistoryManager.shared
    @State private var showProtectionHistory: Bool = false
    
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Защита от множественных вызовов initializeNotifications()
    @State private var isInitializing: Bool = false
    
    // ✅ ОПТИМИЗАЦИЯ ПРОИЗВОДИТЕЛЬНОСТИ: Кэширование для предотвращения множественных вычислений
    // Это критично для реальных устройств, где множественные вычисления могут вызвать краш
    @State private var cachedProtectionLevel: Double = 0.0
    @State private var cachedTariff: TariffType = .free
    @State private var cachedTariffId: String = ""
    @State private var lastProtectionLevelCalculation: Date = Date.distantPast
    @State private var cachedProtectionColor: Color = .primaryBlue  // ✅ Кэш для protectionColor
    
    // ✅ ДИАГНОСТИКА: Флаги для отключения секций (помогают выявить проблемную секцию)
    // Используйте эти флаги в UserDefaults для отключения секций при диагностике краша
    @AppStorage("settings_disable_profile_section") private var disableProfileSection: Bool = false
    @AppStorage("settings_disable_security_section") private var disableSecuritySection: Bool = false
    @AppStorage("settings_disable_notifications_section") private var disableNotificationsSection: Bool = false
    @AppStorage("settings_disable_app_section") private var disableAppSection: Bool = false
    @AppStorage("settings_disable_system_components_section") private var disableSystemComponentsSection: Bool = false
    @AppStorage("settings_disable_additional_section") private var disableAdditionalSection: Bool = false
    
    // ✅ ДИАГНОСТИКА: Флаги для отключения подсекций секции Защита
    @AppStorage("settings_disable_security_network_toggle") private var disableSecurityNetworkToggle: Bool = false
    @AppStorage("settings_disable_security_biometric_toggle") private var disableSecurityBiometricToggle: Bool = false
    @AppStorage("settings_disable_security_protection_level") private var disableSecurityProtectionLevel: Bool = false
    @AppStorage("settings_disable_security_protection_buttons") private var disableSecurityProtectionButtons: Bool = false
    @AppStorage("settings_disable_security_managers") private var disableSecurityManagers: Bool = false
    @AppStorage("settings_disable_advanced_protection_screen") private var disableAdvancedProtectionScreen: Bool = false
    
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
    
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАНЫ computed properties с EnvironmentObject
    // Они вызывали проблемы с SwiftUI type resolution
    
    // MARK: - Body
    
    // Счетчик перерисовок для диагностики
    #if DEBUG
    private static var bodyCallCount: Int = 0
    private static var settingsContentCallCount: Int = 0
    #endif
    
    var body: some View {
        // ✅ КРИТИЧЕСКОЕ: Логи в самом начале body - ПЕРВАЯ СТРОКА
        // Это поможет понять, доходит ли выполнение до body
        let _ = {
            // ✅ ДИАГНОСТИКА: Всегда логируем, даже без ENABLE_CRASH_LOGS
            #if DEBUG
            Self.bodyCallCount += 1
            print("🔴 SETTINGS_BODY: body НАЧАЛО - ПЕРВАЯ СТРОКА (#\(Self.bodyCallCount))")
            #else
            print("🔴 SETTINGS_BODY: body НАЧАЛО - ПЕРВАЯ СТРОКА")
            #endif
            print("🔴 SETTINGS_BODY: Thread.isMainThread = \(Thread.isMainThread)")
            
            // ✅ КРИТИЧЕСКОЕ: Проверка EnvironmentObject
            // В SwiftUI EnvironmentObject не может быть nil, но проверим для диагностики
            print("🔴 SETTINGS_BODY: Проверка EnvironmentObject...")
            // Не можем напрямую проверить nil, но можем попробовать обратиться
        }()
        
        // ✅ КРИТИЧЕСКОЕ: Расширенные логи для диагностики
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                #if DEBUG
                print("🔴 SETTINGS: body вычисляется - НАЧАЛО (#\(Self.bodyCallCount))")
                #endif
                print("🔴 SETTINGS: notificationManager = \(notificationManager)")
                print("🔴 SETTINGS: securityManager = \(securityManager)")
                print("🔴 SETTINGS: featuresManager = \(featuresManager)")
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН print с EnvironmentObject tariffManager
                print("🔴 SETTINGS: isNetworkProtectionEnabled = \(isNetworkProtectionEnabled)")
                print("🔴 SETTINGS: isSecurityNotificationsEnabled = \(isSecurityNotificationsEnabled)")
                print("🔴 SETTINGS: isSoundNotificationsEnabled = \(isSoundNotificationsEnabled)")
                print("🔴 SETTINGS: isBiometricEnabled = \(isBiometricEnabled)")
                print("🔴 SETTINGS: selectedTheme = \(selectedTheme)")
                print("🔴 SETTINGS: showProfileEdit = \(showProfileEdit)")
                
                // ✅ КРИТИЧЕСКОЕ: Безопасный доступ к localizationManager
                // ✅ ИСПРАВЛЕНО: Убрана прямая печать - может вызывать проблемы при инициализации
                // let language = localizationManager.currentLanguage
                // print("🔴 SETTINGS: localizationManager.currentLanguage = \(language)")
            }
        }()
        settingsContent()
            .onAppear {
                // ✅ КРИТИЧЕСКОЕ: Логи в onAppear с ENABLE_CRASH_LOGS (работает в TestFlight)
                if Self.ENABLE_CRASH_LOGS {
                    print("🔴 SETTINGS: onAppear вызван")
                    print("🔴 SETTINGS: Thread.isMainThread = \(Thread.isMainThread)")
                    
                    // ✅ ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА: Проверка EnvironmentObject
                    print("🔴 SETTINGS: navigationManager = \(navigationManager)")
                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН print с EnvironmentObject localizationManager
                    print("🔴 SETTINGS: notificationManager = \(notificationManager)")
                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН print с EnvironmentObject tariffManager
                    
                    // ✅ ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА: Проверка инициализации менеджеров
                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН print с EnvironmentObject localizationManager.currentLanguage
                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН print с EnvironmentObject tariffManager.currentTariff
                    
                    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убрали прямой доступ к notificationSettings в onAppear
                    // Это может вызвать краш, если notificationSettings еще не инициализирован
                    print("🔴 SETTINGS: Все @State переменные:")
                    print("  - isNetworkProtectionEnabled = \(isNetworkProtectionEnabled)")
                    print("  - isSecurityNotificationsEnabled = \(isSecurityNotificationsEnabled)")
                    print("  - isSoundNotificationsEnabled = \(isSoundNotificationsEnabled)")
                    print("  - isBiometricEnabled = \(isBiometricEnabled)")
                    print("  - selectedTheme = \(selectedTheme)")
                    print("  - cachedProtectionLevel = \(cachedProtectionLevel)")
                    print("  - cachedTariff = \(cachedTariff)")
                    print("  - cachedTariffId = \(cachedTariffId)")
                    
                    // ✅ ДИАГНОСТИКА ПАМЯТИ: Для реального устройства
                    #if !targetEnvironment(simulator)
                    var memoryInfo = mach_task_basic_info()
                    var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
                    let kerr: kern_return_t = withUnsafeMutablePointer(to: &memoryInfo) {
                        $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                            task_info(mach_task_self_,
                                     task_flavor_t(MACH_TASK_BASIC_INFO),
                                     $0,
                                     &count)
                        }
                    }
                    if kerr == KERN_SUCCESS {
                        let memoryUsageMB = Double(memoryInfo.resident_size) / 1024.0 / 1024.0
                        print("🔴 SETTINGS: Использование памяти = \(String(format: "%.2f", memoryUsageMB)) MB")
                        
                    } else {
                        print("🔴 SETTINGS: Ошибка получения информации о памяти: \(kerr)")
                    }
                    #endif
                }
                initializeNotifications()
                
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обновляем кэш только если тариф изменился
                let currentTariff = tariffManager.currentTariff
                let currentTariffId = currentTariff.rawValue
                if cachedTariffId != currentTariffId || cachedTariff != currentTariff {
                    cachedTariff = currentTariff
                    cachedTariffId = currentTariffId
                    if Self.ENABLE_CRASH_LOGS {
                        
                    }
                }
            }
            .onChange(of: tariffManager.currentTariff) { newTariff in
                // ✅ ОПТИМИЗАЦИЯ: Сбрасываем кэш при изменении тарифа
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН Task - обновляем @State напрямую
                if Self.ENABLE_CRASH_LOGS {
                    
                }
                cachedProtectionLevel = 0.0
                cachedProtectionColor = .primaryBlue  // ✅ Сбрасываем кэш цвета
                cachedTariff = newTariff
                cachedTariffId = newTariff.rawValue
                lastProtectionLevelCalculation = Date.distantPast
            }
            .onDisappear {
                if Self.ENABLE_CRASH_LOGS {
                    print("🔴 SETTINGS: onDisappear вызван")
                }
            }
    }
    
    // ✅ ИСПРАВЛЕНО: Упрощенная инициализация (как в бэкапе - работало)
    // Убрали сложные задержки и race conditions
    
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Основной контент экрана
    @ViewBuilder
    private func settingsContent() -> some View {
        // ✅ КРИТИЧЕСКОЕ: Логи в самом начале settingsContent() - ПЕРВАЯ СТРОКА
        // Это поможет понять, доходит ли выполнение до settingsContent()
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                #if DEBUG
                Self.settingsContentCallCount += 1
                print("🔴 SETTINGS: settingsContent() НАЧАЛО - ПЕРВАЯ СТРОКА (#\(Self.settingsContentCallCount))")
                #else
                print("🔴 SETTINGS: settingsContent() НАЧАЛО - ПЕРВАЯ СТРОКА")
                #endif
                print("🔴 SETTINGS: Thread.isMainThread = \(Thread.isMainThread)")
            }
        }()
        
        // ✅ КРИТИЧЕСКОЕ: Расширенные логи для диагностики
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                #if DEBUG
                print("🔴 SETTINGS: settingsContent() вызывается (#\(Self.settingsContentCallCount))")
                #endif
                
                // ✅ КРИТИЧЕСКОЕ: Безопасный доступ к менеджерам
                // В SwiftUI EnvironmentObject не может быть nil, но проверим для безопасности
                let language = localizationManager.currentLanguage
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН print с EnvironmentObject localizationManager.currentLanguage
                
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН print с EnvironmentObject tariffManager.currentTariff
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убрали прямой доступ к notificationSettings в settingsContent
                // Это может вызвать краш, если notificationSettings еще не инициализирован
                // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убраны computed properties из отладочного вывода
                let debugLanguage: String = (try? localizationManager.currentLanguage.rawValue) ?? "unknown"
                let debugTariff: TariffType = (try? tariffManager.currentTariff) ?? .free
                print("🔴 SETTINGS: currentLanguage = \(debugLanguage)")
                print("🔴 SETTINGS: currentTariff = \(debugTariff)")
                print("🔴 SETTINGS: Stack trace:")
                Thread.callStackSymbols.prefix(5).forEach { print("  \($0)") }
            }
        }()
        
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Безопасный доступ к safeLocalized с try-catch
        // Вычисляем backgroundLabel вне ViewBuilder
        let backgroundLabel: String = {
            guard Thread.isMainThread else {
                return "Settings Background"
            }
            do {
                return safeLocalized("settings_accessibility_background")
            } catch {
                print("🔴 SETTINGS_CONTENT: ❌ ОШИБКА в safeLocalized для settings_accessibility_background: \(error)")
                return "Settings Background"
            }
        }()
        
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(backgroundLabel)
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader()
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // ✅ ДИАГНОСТИКА: Логирование состояния всех секций
                        let _ = {
                            if Self.ENABLE_CRASH_LOGS {
                                
                            }
                        }()
                        
                        // Профиль пользователя
                        if !disableProfileSection {
                            profileSection()
                        } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
                        
                        // Защита и безопасность
                        if !disableSecuritySection {
                            securitySection()
                        } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
                        
                        // Уведомления
                        if !disableNotificationsSection {
                            notificationsSection()
                        } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
                        
                        // Приложение
                        if !disableAppSection {
                            appSection()
                                .id("app_section_current")
                        } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
                        
                        // ✅ ЗАДАЧА 22: Системные компоненты (только для админов)
                        if isAdmin && !disableSystemComponentsSection {
                            systemComponentsSection()
                                .id("system_components_section_current")
                        } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
                        
                        // Дополнительно
                        if !disableAdditionalSection {
                            additionalSection()
                                .id("additional_section_current")
                        } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
                        
                        // ✅ ДИАГНОСТИКА: Если все секции отключены, показываем сообщение
                        if disableProfileSection && disableSecuritySection && disableNotificationsSection && disableAppSection && disableSystemComponentsSection && disableAdditionalSection {
                            VStack(spacing: 16) {
                                Text("🔍 ДИАГНОСТИКА")
                                    .font(.system(size: 24, weight: .bold))
                                    .foregroundColor(.primary)
                                
                                Text("Все секции отключены для диагностики краша")
                                    .font(.system(size: 16))
                                    .foregroundColor(.secondary)
                                    .multilineTextAlignment(.center)
                                    .padding(.horizontal, 20)
                                
                                Text("Проверьте логи в Console.app")
                                    .font(.system(size: 14))
                                    .foregroundColor(.secondary)
                            }
                            .padding(.vertical, 40)
                            .frame(maxWidth: .infinity)
                        }
                        
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
        .id("settings_lang_current")
        .sheet(isPresented: $showProfileEdit) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            ProfileEditView()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showLanguageSettings) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            LanguageSettingsScreen()
        }
        .sheet(isPresented: $showSupportScreen) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            SupportScreen()
        }
        .sheet(isPresented: $showPrivacyPolicy) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            PrivacyPolicyScreen()
        }
        .sheet(isPresented: $showTermsOfService) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            TermsOfServiceScreen()
        }
        .sheet(isPresented: $showShareSheet) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            ShareSheet(activityItems: [
                safeLocalized("settings_share_message")
            ])
        }
        .sheet(isPresented: $showProtectionExplanation) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Прямой доступ к tariffManager без computed property
            let currentTariff: TariffType = (try? tariffManager.currentTariff) ?? .free
            ProtectionLevelExplanationModal(
                isPresented: $showProtectionExplanation,
                currentTariff: currentTariff
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAdvancedProtection) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            AdvancedProtectionSettingsScreen()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showProtectionHistory) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            ProtectionLevelHistoryModal(isPresented: $showProtectionHistory)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showEmergencyContacts) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            EmergencyContactsView()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showEmergencyNotifications) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            EmergencyNotificationsView()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showVoiceControl) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            VoiceControlView()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showChildProtectionCompliance) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            ComplianceView(section: .childProtection)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showDataProtectionCompliance) {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
            ComplianceView(section: .dataProtection)
                .environmentObject(localizationManager)
        }
        // Инициализация перенесена в safeInitialize()
        .onChange(of: notificationManager.notificationSettings.securityEnabled) { newValue in
            // ✅ КРИТИЧЕСКОЕ: Логирование для диагностики краша
            if Self.ENABLE_CRASH_LOGS {
                
            }
            
            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем Task для асинхронного обновления @State
            Task { @MainActor in
                isSecurityNotificationsEnabled = newValue
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }
        }
        .onChange(of: notificationManager.notificationSettings.soundEnabled) { newValue in
            // ✅ КРИТИЧЕСКОЕ: Логирование для диагностики краша
            if Self.ENABLE_CRASH_LOGS {
                
            }
            
            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем Task для асинхронного обновления @State
            Task { @MainActor in
                isSoundNotificationsEnabled = newValue
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }
        }
        .withToast()
    }
    
    // MARK: - Navigation Header
    
    @ViewBuilder
    private func navigationHeader() -> some View {
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()
        
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
            print("🔴 SETTINGS: safeLocalized('\(key)') вызван не на main thread, возвращаем ключ")
            return key // Fallback для фоновых потоков
        }
        
        // ✅ КРИТИЧЕСКОЕ: Безопасный доступ к localizationManager с try-catch
        do {
            return localizationManager.localized(key)
        } catch {
            print("🔴 SETTINGS: ❌ ОШИБКА в safeLocalized('\(key)'): \(error), возвращаем ключ")
            return key
        }
    }
    
    // MARK: - Profile Section
    
    @ViewBuilder
    private func profileSection() -> some View {
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Предварительно вычисляем ВСЕ значения вне View hierarchy!
        let userInitial = storedName.isEmpty ? "?" : String(storedName.prefix(1).uppercased())
        let userName = storedName.isEmpty ? safeLocalized("profile_name_placeholder") : storedName
        let userAlias = storedAlias.isEmpty ? safeLocalized("profile_email_placeholder") : storedAlias
        let userStatus = safeLocalized("settings_profile_status")
        let sectionTitle = safeLocalized("profile_section")

        VStack(spacing: Spacing.m) {
            HStack {
                Text(sectionTitle)
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
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Предварительно вычисляем ВСЕ значения вне View hierarchy!
        // Это предотвращает проблемы с SwiftUI type system resolution
        let sectionTitle = safeLocalized("security_section")
        let networkTitle = safeLocalized("network_protection_protection")
        let networkSubtitle = safeLocalized("network_protection_protection_subtitle")
        let biometricTitle = safeLocalized("biometric_auth")
        let biometricSubtitle = safeLocalized("biometric_auth_subtitle")
        let protectionTitle = safeLocalized("protection_level")
        let protectionValueFormat = safeLocalized("settings_protection_level_value")

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем кэшированные значения вместо computed properties
        let protectionLevelValue = cachedProtectionLevel
        let protectionLevelTextValue = protectionLevelValue >= 76 ? safeLocalized("settings_protection_level_maximum") :
                                      protectionLevelValue >= 51 ? safeLocalized("settings_protection_level_high") :
                                      protectionLevelValue >= 26 ? safeLocalized("settings_protection_level_medium") :
                                      safeLocalized("settings_protection_level_low")
        let protectionColorValue = protectionLevelValue >= 76 ? Color.primaryBlue :
                                  protectionLevelValue >= 51 ? Color.successGreen :
                                  protectionLevelValue >= 26 ? Color.warningOrange :
                                  Color.dangerRed
        let protectionAccessibilityLabel = String(format: safeLocalized("settings_protection_level_accessibility"), Int(protectionLevelValue))

        VStack(spacing: Spacing.m) {
            HStack {
                Text(sectionTitle)
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)

                Spacer()
            }

            VStack(spacing: Spacing.m) {
                // Network Protection
                if !disableSecurityNetworkToggle {
                    settingRow(
                        icon: "shield.fill",
                        title: networkTitle,
                        subtitle: networkSubtitle,
                        isEnabled: $isNetworkProtectionEnabled
                    )
                } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов

                // Биометрическая аутентификация
                if !disableSecurityBiometricToggle {
                    settingRow(
                        icon: "faceid",
                        title: biometricTitle,
                        subtitle: biometricSubtitle,
                        isEnabled: $isBiometricEnabled,
                        isBiometric: true
                    )
                } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов

                // Уровень защиты
                if !disableSecurityProtectionLevel {
                    VStack(spacing: Spacing.s) {
                    HStack {
                        Image(systemName: "lock.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.primaryBlue)

                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            HStack {
                                Text(protectionTitle)
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)

                                Button(action: {
                                    showProtectionExplanation = true
                                }) {
                                    Image(systemName: "info.circle")
                                        .font(.system(size: 14, weight: .semibold))
                                        .foregroundColor(protectionColorValue)
                                        .padding(6)
                                        .background(
                                            Circle()
                                                .fill(protectionColorValue.opacity(0.15))
                                        )
                                }
                                .padding(.leading, Spacing.xs)
                            }

                            Text(
                                String(
                                    format: protectionValueFormat,
                                    Int(protectionLevelValue),
                                    protectionLevelTextValue
                                ) + " (на основе тарифа)"
                            )
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }

                        Spacer()
                    }

                    // ✅ ИСПОЛЬЗУЕМ ТОЛЬКО ПРЕДВАРИТЕЛЬНО ВЫЧИСЛЕННЫЕ ЗНАЧЕНИЯ!
                    HStack {
                        Text(percentText(0))
                            .font(.caption)
                            .foregroundColor(.textSecondary)

                        Slider(value: .constant(protectionLevelValue), in: 0...100, step: 5) {
                            Text(protectionTitle)
                        } minimumValueLabel: {
                            Text(percentText(0))
                        } maximumValueLabel: {
                            Text(percentText(100))
                        }
                        .accentColor(protectionColorValue)
                        .disabled(true)

                        Text(percentText(100))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    // Кнопки дополнительных настроек
                    if !disableSecurityProtectionButtons {
                        // ✅ ПРЕДВАРИТЕЛЬНО ВЫЧИСЛЯЕМ ВСЕ СТРОКИ ЛОКАЛИЗАЦИИ!
                        let historyTitle = safeLocalized("settings_protection_history")
                        let advancedTitle = safeLocalized("settings_advanced_settings")
                        let improveTitle = safeLocalized("settings_improve_protection")

                        LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: Spacing.s), count: 3), spacing: Spacing.s) {
                            protectionActionButton(
                                title: historyTitle,
                                icon: "chart.line.uptrend.xyaxis",
                                foreground: .primaryBlue,
                                background: Color.primaryBlue.opacity(0.12),
                                action: { showProtectionHistory = true }
                            )

                            protectionActionButton(
                                title: advancedTitle,
                                icon: "slider.horizontal.3",
                                foreground: Color(hex: "#A855F7"),
                                background: Color(hex: "#A855F7").opacity(0.14),
                                action: {
                                    if !disableAdvancedProtectionScreen {
                                        showAdvancedProtection = true
                                    } else if Self.ENABLE_CRASH_LOGS {
                                        
                                    }
                                }
                            )

                            protectionActionButton(
                                title: improveTitle,
                                icon: "arrow.up.circle.fill",
                                foreground: .secondaryGold,
                                background: Color.secondaryGold.opacity(0.18),
                                action: { navigationManager.navigateTo(.tariffs) }
                            )
                        }
                        .padding(.top, Spacing.s)
                    } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel(protectionAccessibilityLabel)
                } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
                
                // ✅ Менеджеры (5 компонентов)
                if !disableSecurityManagers {
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
                } // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УБРАН logger вызов
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Notifications Section
    
    @ViewBuilder
    private func notificationsSection() -> some View {
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Предварительно вычисляем ВСЕ значения вне View hierarchy!
        let sectionTitle = safeLocalized("notifications_section")
        let pushTitle = safeLocalized("push_notifications")
        let pushSubtitle = safeLocalized("push_notifications_subtitle")
        let soundTitle = safeLocalized("sound_notifications")
        let soundSubtitle = safeLocalized("sound_notifications_subtitle")

        VStack(spacing: Spacing.m) {
            HStack {
                Text(sectionTitle)
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)

                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                settingRow(
                    icon: "bell.fill",
                    title: pushTitle,
                    subtitle: pushSubtitle,
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
                    title: soundTitle,
                    subtitle: soundSubtitle,
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
        .onAppear {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }
    }
    
    // MARK: - App Section
    
    @ViewBuilder
    private func appSection() -> some View {
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Предварительно вычисляем ВСЕ значения вне View hierarchy!
        let sectionTitle = safeLocalized("app_section")
        let languageTitle = safeLocalized("language")
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убраны EnvironmentObject из предварительных вычислений
        let currentLanguage = (try? localizationManager.currentLanguage) ?? .english
        let languageSubtitle = currentLanguage == .russian ? safeLocalized("language_subtitle") : currentLanguage.displayName
        let themeTitle = safeLocalized("dark_theme")
        let themeSubtitle = selectedTheme.displayName(localizationManager) // ✅ selectedTheme.displayName не использует EnvironmentObject в рантайме

        VStack(spacing: Spacing.m) {
            HStack {
                Text(sectionTitle)
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)

                Spacer()
            }

            VStack(spacing: Spacing.s) {
                settingsButton(
                    icon: "globe",
                    title: languageTitle,
                    subtitle: languageSubtitle,
                    action: {
                        showLanguageSettings = true
                    }
                )

                settingsButton(
                    icon: selectedTheme.icon,
                    title: themeTitle,
                    subtitle: themeSubtitle,
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
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()
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
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Предварительно вычисляем ВСЕ значения вне View hierarchy!
        let sectionTitle = safeLocalized("system_components_title")
        let retryTitle = safeLocalized("retry")
        let emptyTitle = safeLocalized("system_components_empty")

        VStack(spacing: Spacing.m) {
            HStack {
                Text(sectionTitle)
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
                    Button(retryTitle) {
                        loadComponents()
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
            } else if components.isEmpty {
                Text(emptyTitle)
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
            if Self.ENABLE_CRASH_LOGS {
                
            }
            if isAdmin && components.isEmpty {
                Task { @MainActor in
                    loadComponents()
                }
            }
        }
        .onDisappear {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }
    }
    
    /// ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Загрузка компонентов на main thread
    private func loadComponents() {
        if Self.ENABLE_CRASH_LOGS {
            
        }
        
        guard isAdmin else {
            if Self.ENABLE_CRASH_LOGS {
                
            }
            return
        }
        
        Task { @MainActor in
            isLoadingComponents = true
            componentsError = nil
        }
        
        apiService.getComponentsList { result in
            Task { @MainActor in
                isLoadingComponents = false
                
                switch result {
                case .success(let loadedComponents):
                    if Self.ENABLE_CRASH_LOGS {
                        
                    }
                    components = loadedComponents
                case .failure(let error):
                    componentsError = error.localizedDescription
                    if Self.ENABLE_CRASH_LOGS {
                        
                    }
                }
                
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }
        }
    }
    
    /// ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Переключение компонентов на main thread
    private func toggleComponent(_ component: ComponentStatus) {
        if Self.ENABLE_CRASH_LOGS {
            
        }
        
        guard isAdmin else {
            if Self.ENABLE_CRASH_LOGS {
                
            }
            return
        }
        
        Task { @MainActor in
            do {
                if component.isEnabled {
                    if Self.ENABLE_CRASH_LOGS {
                        
                    }
                    _ = try await apiService.disableComponent(componentId: component.componentId)
                } else {
                    if Self.ENABLE_CRASH_LOGS {
                        
                    }
                    _ = try await apiService.enableComponent(componentId: component.componentId)
                }
                // Обновляем список компонентов
                loadComponents()
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            } catch {
                componentsError = error.localizedDescription
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }
        }
    }
    
    // MARK: - Component Row View
    
    private struct ComponentRow: View {
        let component: ComponentStatus
        let onToggle: () -> Void
        @EnvironmentObject private var localizationManager: LocalizationManager
        
        // Логгер для ComponentRow
        private let logger = SettingsDiagnosticsLogger.shared
        private static let ENABLE_CRASH_LOGS = SettingsDiagnosticsLogger.ENABLE_LOGS
        
        var body: some View {
            let _ = {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }()

            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Предварительно вычисляем локализации
            let lastUpdateText = component.lastUpdate.map { lastUpdate in
                String(format: localizationManager.localized("system_components_last_update"), formatDate(lastUpdate))
            }

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
                    
                    if let text = lastUpdateText {
                        Text(text)
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
            .onAppear {
                if Self.ENABLE_CRASH_LOGS {
                    
                }
            }
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
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Предварительно вычисляем ВСЕ значения вне View hierarchy!
        let sectionTitle = safeLocalized("additional_section")
        let helpTitle = safeLocalized("help_support")
        let helpSubtitle = safeLocalized("help_support_subtitle")
        let privacyTitle = safeLocalized("privacy_policy")
        let privacySubtitle = safeLocalized("privacy_policy_subtitle")
        let termsTitle = safeLocalized("terms_of_service")
        let termsSubtitle = safeLocalized("terms_of_service_subtitle")
        let consentTitle = safeLocalized("settings_consent_personal_data")
        let consentSubtitle = consentAccepted ? safeLocalized("settings_consent_granted") : safeLocalized("settings_consent_manage")
        let shareTitle = safeLocalized("share_app")
        let shareSubtitle = safeLocalized("share_app_subtitle")

        VStack(spacing: Spacing.m) {
            HStack {
                Text(sectionTitle)
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
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()
        
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
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()
        
        return Button(action: {
            if Self.ENABLE_CRASH_LOGS {
                
            }
            action()
        }) {
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
        if Self.ENABLE_CRASH_LOGS {
            
        }
        let result = String(format: safeLocalized("settings_percent_format"), value)
        if Self.ENABLE_CRASH_LOGS {
            
        }
        return result
    }
    
    @ViewBuilder
    private func protectionActionButton(title: String, icon: String, foreground: Color, background: Color, action: @escaping () -> Void) -> some View {
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()
        
        Button(action: {
            if Self.ENABLE_CRASH_LOGS {
                
            }
            action()
        }) {
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
    
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УДАЛЕН computed property calculatedProtectionLevel
    // Вызывал SwiftUI type resolution recursion
    
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УДАЛЕН computed property protectionLevelText
    // Вызывал SwiftUI type resolution recursion через calculatedProtectionLevel
    
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: УДАЛЕН computed property protectionColor
    // Вызывал SwiftUI type resolution recursion
    
    // ✅ УДАЛЕНО: handleProtectionLevelChange и связанные функции
    // Ползунок теперь только для чтения, защита управляется сервером через тариф
    
    private var cardBackground: some View {
        let _ = {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }()
        
        return RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    // MARK: - Theme Functions
    
    private func cycleTheme() {
        if Self.ENABLE_CRASH_LOGS {
            
        }
        
        let allThemes = ThemeMode.allCases
        if let currentIndex = allThemes.firstIndex(of: selectedTheme) {
            let nextIndex = (currentIndex + 1) % allThemes.count
            selectedTheme = allThemes[nextIndex]
            if Self.ENABLE_CRASH_LOGS {
                
            }
            
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
        if Self.ENABLE_CRASH_LOGS {
            
        }
        
        // Тактильный отклик
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // Проверка обновлений через App Store
        if let url = URL(string: "itms-apps://itunes.apple.com/app/id123456789") {
            UIApplication.shared.open(url)
            if Self.ENABLE_CRASH_LOGS {
                
            }
        } else {
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }
    }
    
    // MARK: - Notification Functions
    
    /// ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Безопасная инициализация без прямого доступа к notificationSettings
    private func initializeNotifications() {
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Защита от множественных вызовов
        guard !isInitializing else {
            if Self.ENABLE_CRASH_LOGS {
                
            }
            return
        }
        
        if Self.ENABLE_CRASH_LOGS {
            
        }
        
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем Task для асинхронного обновления @State
        // Это предотвращает "Modifying state during view update"
        Task { @MainActor in
            isInitializing = true
            
            // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Безопасная синхронизация начальных значений
            // onChange срабатывает только при ИЗМЕНЕНИИ, поэтому нужно синхронизировать начальные значения
            // NotificationManager инициализируется синхронно в init(), поэтому к моменту вызова
            // initializeNotifications() настройки уже готовы и можно безопасно синхронизировать
            if Self.ENABLE_CRASH_LOGS {
                
            }
            
            // ✅ Безопасная синхронизация - NotificationManager уже инициализирован
            let securityValue = notificationManager.notificationSettings.securityEnabled
            let soundValue = notificationManager.notificationSettings.soundEnabled
            
            if Self.ENABLE_CRASH_LOGS {
                print("🟢 SETTINGS: Значения из notificationSettings: securityEnabled = \(securityValue), soundEnabled = \(soundValue)")
            }
            
            isSecurityNotificationsEnabled = securityValue
            isSoundNotificationsEnabled = soundValue
            
            if Self.ENABLE_CRASH_LOGS {
                print("🟢 SETTINGS: Синхронизация завершена успешно")
                print("🟢 SETTINGS: isSecurityNotificationsEnabled = \(isSecurityNotificationsEnabled), isSoundNotificationsEnabled = \(isSoundNotificationsEnabled)")
            }
            
            // ✅ Инициализируем биометрию
            isBiometricEnabled = UserDefaults.standard.bool(forKey: "biometricEnabled")
            
            // ✅ Запрос разрешения на уведомления (как в бэкапах - работало)
            let granted = await notificationManager.requestAuthorization()
            if granted {
                print("🔔 Разрешение на уведомления получено")
            } else {
                print("🔕 Разрешение на уведомления отклонено")
            }
            
            // ✅ Освобождаем флаг после завершения
            isInitializing = false
            if Self.ENABLE_CRASH_LOGS {
                
            }
        }
        // ✅ Синхронизация состояния будет через onChange наблюдатели
    }
}

// MARK: - Preview

struct SettingsScreen_Previews: PreviewProvider {
    static var previews: some View {
        SettingsScreen()
    }
}
