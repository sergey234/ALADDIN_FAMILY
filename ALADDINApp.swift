import SwiftUI
import Foundation

/// 👤 User Profile Manager
/// Singleton класс для управления профилем пользователя
/// Предоставляет быстрый доступ к данным пользователя из кеша
class UserProfileManager {
    static let shared = UserProfileManager()

    private let apiService = APIService.shared
    private let userDefaults = UserDefaults.standard

    private let displayNameKey = "user_display_name"
    private let profileNameKey = "user_profile_name"
    private let emailKey = "user_email"
    private let lastUpdateKey = "user_profile_last_update"

    private init() {
        // Загружаем профиль при инициализации
        loadProfileInBackground()
    }

    // MARK: - Public Methods

    /// Получить отображаемое имя пользователя
    var displayName: String {
        if let cachedName = userDefaults.string(forKey: displayNameKey),
           !cachedName.isEmpty {
            return cachedName
        }
        return NSLocalizedString("child_interface_default_name", comment: "Default user name")
    }

    /// Получить email пользователя
    var email: String? {
        return userDefaults.string(forKey: emailKey)
    }

    /// Проверить, загружен ли профиль
    var isProfileLoaded: Bool {
        return userDefaults.string(forKey: displayNameKey) != nil
    }

    /// Получить время последнего обновления профиля
    var lastUpdateTime: Date? {
        if let timestamp = userDefaults.double(forKey: lastUpdateKey) as Double?, timestamp > 0 {
            return Date(timeIntervalSince1970: timestamp)
        }
        return nil
    }

    /// Загрузить профиль из API и сохранить в кеш
    func loadProfile(completion: ((Bool) -> Void)? = nil) {
        apiService.getUserProfile { [weak self] result in
            guard let self = self else { return }

            DispatchQueue.main.async {
                switch result {
                case .success(let profile):
                    // Сохраняем данные в кеш
                    self.saveProfileToCache(profile)
                    print("✅ User profile loaded and cached: \(profile.name)")
                    completion?(true)

                case .failure(let error):
                    print("⚠️ Failed to load user profile: \(error.localizedDescription)")
                    completion?(false)
                }
            }
        }
    }

    /// Очистить кеш профиля
    func clearProfileCache() {
        userDefaults.removeObject(forKey: displayNameKey)
        userDefaults.removeObject(forKey: profileNameKey)
        userDefaults.removeObject(forKey: emailKey)
        userDefaults.removeObject(forKey: lastUpdateKey)
        userDefaults.synchronize()
        print("🗑️ User profile cache cleared")
    }

    // MARK: - Private Methods

    private func loadProfileInBackground() {
        // Загружаем профиль в фоне при инициализации
        // Если профиль старше 24 часов, обновляем
        if shouldRefreshProfile() {
            DispatchQueue.global(qos: .background).async { [weak self] in
                self?.loadProfile()
            }
        }
    }

    private func shouldRefreshProfile() -> Bool {
        guard let lastUpdate = lastUpdateTime else {
            return true // Нет данных, нужно загрузить
        }

        let twentyFourHours: TimeInterval = 24 * 60 * 60
        return Date().timeIntervalSince(lastUpdate) > twentyFourHours
    }

    private func saveProfileToCache(_ profile: UserProfile) {
        userDefaults.set(profile.name, forKey: displayNameKey)
        userDefaults.set(profile.name, forKey: profileNameKey) // Для совместимости
        userDefaults.set(profile.email, forKey: emailKey)
        userDefaults.set(Date().timeIntervalSince1970, forKey: lastUpdateKey)
        userDefaults.synchronize()
    }
}

@main
struct ALADDINApp: App {

    // 🔍 ТЕСТОВОЕ ЛОГИРОВАНИЕ - проверяем работу при старте приложения
    private let appStartLogger: Void = {
        print("🚀 ALADDIN_APP: Application starting...")
        print("🚀 ALADDIN_APP: Testing logger initialization...")
        return ()
    }()

    // 🚫 ВРЕМЕННО ОТКЛЮЧЕНО: @StateObject могут вызывать краш при SwiftUI рендеринге
    // @StateObject private var navigationManager = NavigationManager()
    // @StateObject private var localizationManager = LocalizationManager()

    // ВРЕМЕННАЯ ЗАГЛУШКА: обычные объекты вместо ObservableObject
    private let navigationManager = NavigationManager()
    private let localizationManager = LocalizationManager()
    // ✅ Добавляем SubscriptionManager для JWT токенов
    private var subscriptionManager = SubscriptionManager.shared
    @AppStorage("selected_theme") private var selectedTheme: String = "system"

    // ✅ ИСПРАВЛЕНИЕ: Отслеживаем состояние приложения для предотвращения сброса навигации
    @Environment(\.scenePhase) private var scenePhase
    // Убрали @AppStorage для онбординга
    // private var hasCompletedOnboarding: Bool = false // больше не используется

    // ✅ Состояние навигации
    @State private var navigationInitialized: Bool = false

    // MARK: - Theme Helper
    private var preferredColorScheme: ColorScheme? {
        switch selectedTheme {
        case "light": return .light
        case "dark": return .dark
        case "system": return nil // nil = системная тема
        default: return nil
        }
    }
    
    init() {
        // 🔴 ДОБАВИТЬ ГЛОБАЛЬНЫЙ EXCEPTION HANDLER - поймать точную причину crash
        NSSetUncaughtExceptionHandler { exception in
            print("💥💥💥 GLOBAL CRASH DETECTED! 💥💥💥")
            print("💥 Exception Name: \(exception.name)")
            print("💥 Exception Reason: \(exception.reason ?? "No reason provided")")
            print("💥 Stack Trace:")
            for (index, symbol) in exception.callStackSymbols.enumerated() {
                print("💥   [\(index)] \(symbol)")
            }
            print("💥💥💥 END OF CRASH REPORT 💥💥💥")
        }

        print("🚀🚀🚀 ALADDINApp.init() called - APP STARTING")
        print("🚀🚀🚀 SubscriptionManager.shared created: \(SubscriptionManager.shared)")
        VisualLogger.shared.log("🚀🚀🚀 ALADDINApp.init() called", level: .info)
        print("📱📱📱 VISUAL_LOGGER_TEST: If you see this in Xcode Console, VisualLogger overlay may not be visible")
        print("🚀 ALADDINApp: Начало инициализации приложения")
        // ✅ ИСПРАВЛЕНИЕ: В init() НЕ используем @StateObject, они еще не созданы!
        // Вся логика инициализации перенесена в .onAppear
        if ProcessInfo.processInfo.environment["RESET_ONBOARDING"] == "1" {
            UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            #if DEBUG
            print("🌍 RESET_ONBOARDING активирован — ключ сброшен")
            #endif
        }
        
#if DEBUG
        KeychainAutoRecoveryService.repairTokensIfNeeded()
        
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сначала проверяем и удаляем debug токены СИНХРОННО
        // Это нужно сделать ДО создания новых debug токенов
        let hadDebugTokens = Self.autoFixDebugTokensIfNeeded()

        // ✅ ИСПРАВЛЕНИЕ: Проверяем, нужно ли создавать debug токены
        // Если установлена переменная окружения SKIP_DEBUG_TOKENS=1, пропускаем создание debug токенов
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Тримируем значение, чтобы убрать возможные пробелы
        let skipDebugTokensRaw = ProcessInfo.processInfo.environment["SKIP_DEBUG_TOKENS"] ?? ""
        let skipDebugTokens = skipDebugTokensRaw.trimmingCharacters(in: .whitespacesAndNewlines) == "1"

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Если есть AUTO_LOGIN_EMAIL, автоматически считаем, что нужно пропустить debug токены
        let hasAutoLogin = ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"] != nil &&
                          !ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"]!.isEmpty

        let shouldSkipDebugTokens = skipDebugTokens || hasAutoLogin

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Всегда создаем debug токены после удаления старых
        // Если мы удалили debug токены, обязательно создаем новые
        if hadDebugTokens || !shouldSkipDebugTokens {
            if !shouldSkipDebugTokens {
                // Создаем debug токены независимо от того, были ли они удалены
                DebugAuthTokenSeeder.seedIfNeeded()
            } else if hadDebugTokens {
                // Если токены были удалены, но skipDebugTokens = true, создаем токены в любом случае
                DebugAuthTokenSeeder.seedIfNeeded()
            }
        } else {
            if skipDebugTokens {
                print("⚠️ DEBUG: Пропущено создание debug токенов (SKIP_DEBUG_TOKENS=1)")
            } else if hasAutoLogin {
                print("⚠️ DEBUG: Пропущено создание debug токенов (настроен автоматический логин)")
            }
            print("   Для получения валидных токенов используйте performRealLogin() в Debug Console")
        }
        
        // 🧪 ТЕСТИРОВАНИЕ CRASH: Добавляем изолированный тест сети
        print("🧪🧪🧪 CRASH TESTING: Starting EMERGENCY network test (GET instead of POST)")
        Task {
            let networkTestResult = await SubscriptionManager.shared.emergencyTestGET()
            print("🧪🧪🧪 CRASH TESTING: Emergency test result = \(networkTestResult)")
        }

        // ✅ АВТОМАТИЧЕСКИЙ ЛОГИН: Если установлены переменные окружения, выполняем логин автоматически
        // ✅ ПРОДАКШЕН: Проверяем сохраненные credentials для автоматического логина
        DispatchQueue.global(qos: .utility).async {
            // ✅ ДИАГНОСТИКА: Проверяем переменные окружения
            let email = ProcessInfo.processInfo.environment["AUTO_LOGIN_EMAIL"]
            let password = ProcessInfo.processInfo.environment["AUTO_LOGIN_PASSWORD"]

            // ✅ ПРОДАКШЕН: Проверяем сохраненные credentials
            let savedEmail = UserDefaults.standard.string(forKey: "saved_login_email")
            let savedPassword = UserDefaults.standard.string(forKey: "saved_login_password")
            let autoLoginEnabled = UserDefaults.standard.bool(forKey: "auto_login_enabled")
            
            print("🔍 ALADDINApp: Проверка переменных окружения...")
            let skipDebugTokensValue = ProcessInfo.processInfo.environment["SKIP_DEBUG_TOKENS"] ?? ""
            let skipDebugTokensTrimmed = skipDebugTokensValue.trimmingCharacters(in: .whitespacesAndNewlines)
            let skipDebugTokensIsSet = skipDebugTokensTrimmed == "1"
            print("   - AUTO_LOGIN_EMAIL: \(email != nil ? "✅ установлен (\(email?.prefix(3) ?? "")...)" : "❌ не установлен")")
            print("   - AUTO_LOGIN_PASSWORD: \(password != nil ? "✅ установлен (\(password?.count ?? 0) символов)" : "❌ не установлен")")
            print("   - SKIP_DEBUG_TOKENS: \(skipDebugTokensValue.isEmpty ? "❌ НЕ УСТАНОВЛЕН" : "✅ установлен = '\(skipDebugTokensTrimmed)' (\(skipDebugTokensIsSet ? "активен" : "не активен"))")")
            
            // ✅ ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА: Выводим все переменные окружения, начинающиеся с AUTO_ или SKIP_
            let allEnvVars = ProcessInfo.processInfo.environment
            let relevantVars = allEnvVars.keys.filter { $0.hasPrefix("AUTO_") || $0.hasPrefix("SKIP_") }
            if !relevantVars.isEmpty {
                print("   - Все найденные переменные: \(relevantVars.joined(separator: ", "))")
                for varName in relevantVars {
                    let value = allEnvVars[varName] ?? ""
                    if varName.contains("PASSWORD") {
                        print("     • \(varName) = '\(value.count) символов'")
                    } else {
                        print("     • \(varName) = '\(value)'")
                    }
                }
            } else {
                print("   - ⚠️ ВНИМАНИЕ: Не найдено ни одной переменной окружения с префиксом AUTO_ или SKIP_!")
                print("   - Проверьте, что переменные установлены в правильной схеме (Run)")
            }
            
            // ✅ ПРОДАКШЕН: Проверяем условия для автоматического логина
            let shouldAutoLogin = (email != nil && password != nil && !email!.isEmpty && !password!.isEmpty) ||
                                 (autoLoginEnabled && savedEmail != nil && savedPassword != nil)

            if shouldAutoLogin {
                let loginEmail = email ?? savedEmail!
                let loginPassword = password ?? savedPassword!

                print("🔐 ALADDINApp: Автоматический логин...")
                print("   - Email: \(loginEmail)")
                print("   - Тип: \(email != nil ? "переменные окружения" : "сохраненные credentials")")

                // Небольшая задержка, чтобы приложение успело запуститься
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                    performRealLogin(email: loginEmail, password: loginPassword) { success in
                        if success {
                            print("✅ ALADDINApp: Автоматический логин успешен!")

                            // ✅ ПРОВЕРКА: Убеждаемся, что токены действительно сохранены
                            let keychain = KeychainManager.shared
                            // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
                            if let token = keychain.loadString(forKey: .authToken) {
                                print("✅ ALADDINApp: Токен подтвержден в Keychain (длина: \(token.count))")
                            } else {
                                print("⚠️ ALADDINApp: ВНИМАНИЕ! Токен не найден в Keychain после успешного логина!")
                            }
                        } else {
                            print("❌ ALADDINApp: Ошибка автоматического логина")
                            print("   - Проверьте правильность email и password")
                            print("   - Проверьте доступность сервера")
                            // В продакшене не показываем детали для безопасности
                            #if DEBUG
                            print("   - Проверьте endpoint /auth/login на сервере")
                            #endif
                        }
                    }
                }
            } else {
                #if DEBUG
                if email == nil || password == nil || email!.isEmpty || password!.isEmpty {
                    print("⚠️ ALADDINApp: Переменные окружения для автоматического логина не установлены")
                    print("   - Установите AUTO_LOGIN_EMAIL и AUTO_LOGIN_PASSWORD в Scheme → Run → Arguments → Environment Variables")
                }
                #endif
                print("ℹ️ ALADDINApp: Автоматический логин не настроен - пользователь должен войти вручную")
            }
        }
#endif
    }
    
    var body: some Scene {
        WindowGroup {
            // 🚫 АБСОЛЮТНЫЙ МИНИМУМ: Только базовый SwiftUI, без наших компонентов
            Text("ALADDIN")
                .font(.largeTitle)
                .foregroundColor(.blue)
            .onAppear {
                // 🚫 АБСОЛЮТНЫЙ МИНИМУМ: Никаких инициализаций, только тест SwiftUI
                print("🎯 ALADDIN_APP: onAppear - ABSOLUTE MINIMUM TEST")
                print("✅ SwiftUI Text rendered successfully - no crashes!")
            }
        }
    }

    // ✅ НОВОЕ: Основное содержимое приложения
    private func mainAppContent() -> some View {
        // КРИТИЧНО: NavigationView для работы навигации
        NavigationView {
                // ✅ КРИТИЧНО: Используем AnyView для каждого case - это заставит SwiftUI пересчитать
                Group {
                    switch navigationManager.currentScreen {
                    case .loading:
                        AnyView(AppLoadingView().id("loading"))
                    case .main:
                        AnyView(MainScreen().id("main").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .family:
                        AnyView(FamilyScreen().id("family").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .networkProtection:
                        AnyView(NetworkProtectionScreen().id("network_protection").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .analytics:
                        AnyView(AnalyticsScreen().id("analytics").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .settings:
                        AnyView(SettingsScreen()
                            .id("settings")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)) // ✅ Добавляем LocalizationManager
                    case .aiAssistant:
                        AnyView(AIAssistantScreen().id("aiAssistant").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .parentalControl:
                        AnyView(ParentalControlScreen()
                            .id("parentalControl")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ParentalControlScreen отображён")
                                #endif
                            })
                    case .childInterface:
                        AnyView(ChildInterfaceScreen()
                            .id("childInterface")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ChildInterfaceScreen отображён")
                                #endif
                            })
                    case .securityEducation:
                        AnyView(SecurityEducationScreen()
                            .id("securityEducation")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: SecurityEducationScreen отображён")
                                #endif
                            })
                    case .elderlyInterface:
                        AnyView(ElderlyInterfaceScreen()
                            .id("elderlyInterface")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear {
                                #if DEBUG
                                print("🔍 DEBUG: ElderlyInterfaceScreen отображён")
                                #endif
                            })
                    case .tariffs:
                        AnyView(TariffsScreen().id("tariffs").environmentObject(navigationManager).environmentObject(localizationManager))
#if !APP_STORE_BUILD
                    case .paymentQR:
                        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем AnyView для отложенного создания View
                        // Это предотвращает попытку SwiftUI вычислить body до готовности данных
                        if let tariff = navigationManager.selectedTariffForPayment {
                            // ✅ Дополнительная проверка валидности тарифа
                            if !tariff.id.isEmpty && !tariff.title.isEmpty {
                                // ✅ Обертка в AnyView для безопасности инициализации
                                AnyView(
                                    PaymentQRScreen(tariff: tariff) {
                                        print("🔍 ALADDINApp: onPaymentCompleted вызван")
                                        navigationManager.beginManualPaymentQRClose()
                                        navigationManager.goBack(reason: "PaymentQR.onPaymentCompleted")
                                        navigationManager.selectedTariffForPayment = nil
                                    }
                                    .id("paymentQR")
                                    .environmentObject(navigationManager)
                                    .environmentObject(localizationManager)
                                    .onAppear { 
                                        print("🚨 PaymentQRScreen открыт через NavigationLink!")
                                        print("🚨 Tariff ID: \(tariff.id)")
                                    }
                                )
                            } else {
                                // ✅ Fallback если тариф невалиден
                                AnyView(
                                    VStack(spacing: 20) {
                                        Text("Ошибка: тариф невалиден")
                                            .font(.headline)
                                        Text("ID: \(tariff.id.isEmpty ? "пусто" : tariff.id)")
                                        Text("Title: \(tariff.title.isEmpty ? "пусто" : tariff.title)")
                                        Button("Назад") {
                                                navigationManager.beginManualPaymentQRClose()
                                                navigationManager.goBack(reason: "PaymentQR.invalidTariffFallback")
                                            navigationManager.selectedTariffForPayment = nil
                                        }
                                    }
                                    .padding()
                                    .id("paymentQR_error_invalid")
                                    .environmentObject(navigationManager)
                                    .environmentObject(localizationManager)
                                )
                            }
                        } else {
                            // ✅ Fallback если тариф не передан
                            AnyView(
                                VStack(spacing: 20) {
                                    Text("Ошибка: тариф не выбран")
                                        .font(.headline)
                                    Button("Назад") {
                                            navigationManager.beginManualPaymentQRClose()
                                            navigationManager.goBack(reason: "PaymentQR.nilTariffFallback")
                                    }
                                }
                                .padding()
                                .id("paymentQR_error_nil")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                            )
                        }
#endif
                    case .activationCode:
                        AnyView(
                            ActivationCodeScreen()
                                .id("activationCode")
                                .environmentObject(navigationManager)
                                .environmentObject(localizationManager)
                        )
                    case .profile:
                        AnyView(ProfileScreen()
                            .id("profile")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                            .onAppear { 
                                print("🔍 DEBUG ALADDINApp: ProfileScreen отображён!")
                                print("🔍 DEBUG ALADDINApp: currentScreen = \(navigationManager.currentScreen)")
                            })
                    case .notifications:
                        AnyView(NotificationsScreen().id("notifications").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .privacyPolicy:
                        AnyView(PrivacyPolicyScreen().id("privacyPolicy").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .termsOfService:
                        AnyView(TermsOfServiceScreen().id("termsOfService").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .onboarding:
                        AnyView(OnboardingScreen().id("onboarding").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .devices:
                        AnyView(DevicesScreen().id("devices").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .referral:
                        AnyView(ReferralScreen().id("referral").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .deviceDetail:
                        AnyView(DeviceDetailScreen(
                            device: Device(
                                name: "iPhone 13",
                                owner: "Пользователь",
                                type: .iphone,
                                status: .protected,
                                lastActive: "Только что"
                            )
                        )
                        .id("deviceDetail")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .familyChat:
                        AnyView(FamilyChatScreen().id("familyChat").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .support:
                        AnyView(SupportScreen().id("support").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .addMemberOptions:
                        AnyView(AddMemberOptionsScreen().id("addMemberOptions").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .childRewards:
                        AnyView(ChildRewardsScreen().id("childRewards").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .familyTournament:
                        AnyView(FamilyTournamentView().id("familyTournament").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .unicornPet:
                        AnyView(UnicornPetView().id("unicornPet").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .youngDefender:
                        AnyView(YoungDefenderView().id("youngDefender").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .familyProtector:
                        AnyView(FamilyProtectorView().id("familyProtector").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .childGoalEditor:
                        AnyView(ChildGoalEditorView().id("childGoalEditor").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .gamesParentalControl:
                        AnyView(GamesParentalControlView().id("gamesParentalControl").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .languageSettings:
                        AnyView(LanguageSettingsScreen()
                            .id("languageSettings")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .notificationSettings:
                        AnyView(NotificationSettingsScreen().id("notificationSettings").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .widgetConfiguration:
                        AnyView(WidgetConfigurationScreen().id("widgetConfiguration").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .mainWithRegistration:
                        AnyView(MainScreenWithRegistration(
                            registrationVM: FamilyRegistrationViewModel()
                        )
                        .id("mainWithRegistration")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .childContent:
                        AnyView(ChildContentScreen(
                            category: "Игры",
                            ageGroup: .school
                        )
                        .id("childContent")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .rewardsModal:
                        AnyView(RewardsModalView(
                            unicornBalance: .constant(245),
                            weeklyRewarded: .constant(128),
                            weeklyPunished: .constant(45)
                        )
                        .id("rewardsModal")
                        .environmentObject(navigationManager)
                        .environmentObject(localizationManager))
                    case .rewardsQuickModal:
                        AnyView(RewardsQuickModal(unicornBalance: .constant(245))
                            .id("rewardsQuickModal")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager))
                    case .threatProtection:
                        AnyView(ThreatProtectionScreen().id("threatProtection").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .threatProtectionSettings:
                        AnyView(ThreatProtectionSettingsScreen().id("threatProtectionSettings").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .iotSecurity:
                        // TODO: Создать IoTSecurityScreen или использовать существующий
                        AnyView(ThreatProtectionScreen().id("iotSecurity").environmentObject(navigationManager).environmentObject(localizationManager))
                    case .advancedProtection:
                        AnyView(AdvancedProtectionSettingsScreen().id("advancedProtection").environmentObject(navigationManager).environmentObject(localizationManager))
                    default:
                        AnyView(
                            VStack(spacing: 20) {
                                Text("🚧")
                                    .font(.system(size: 60))
                                Text("Экран в разработке")
                                    .font(.title)
                                    .fontWeight(.bold)
                                Text(navigationManager.currentScreen.rawValue)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background(LinearGradient.backgroundGradient)
                            .id("default_screen")
                            .environmentObject(navigationManager)
                            .environmentObject(localizationManager)
                        )
                    }
                }
                .id("screen_\(navigationManager.currentScreen.rawValue)")
                .navigationBarHidden(true)
            }
            .navigationViewStyle(StackNavigationViewStyle())
            // КРИТИЧНО: Передача NavigationManager через EnvironmentObject
            .environmentObject(navigationManager)
            // ✅ Передаём LocalizationManager через EnvironmentObject
            .environmentObject(localizationManager)
            // ✅ Применяем локализацию через environment
            .environment(\.locale, localizationManager.locale)
            // ✅ КРИТИЧНО: Пересоздаём NavigationView при изменении currentScreen
            .id("nav_\(navigationManager.currentScreen.rawValue)_\(localizationManager.currentLanguage.rawValue)")
            // ✅ Инициализация навигации при первом появлении
            .onAppear {
                let navManager = navigationManager
                let locManager = localizationManager
                Self.initializeNavigation(navigationManager: navManager, localizationManager: locManager)
            }
            // ✅ ИСПРАВЛЕНИЕ: Упрощенная обработка возврата из фона - без лишних проверок
            .onChange(of: scenePhase) { newPhase in
                if newPhase == .active {
                    // Приложение стало активным (вернулись из Safari/фона)
                    print("🔄 Возврат из фона: приложение активно, экран = \(navigationManager.currentScreen)")
                    // НЕ вызываем initializeNavigation - это может вызвать двойную загрузку
                }
            }
            // 🌓 ПРИМЕНЯЕМ ТЕМУ
            .preferredColorScheme(preferredColorScheme)

            // 🔍 VISUAL LOGGING: Добавляем визуальное логирование в DEBUG режиме
            #if DEBUG
            .overlay(
                VStack {
                    Spacer()
                    HStack {
                        Spacer()
                        MasterLogger.shared.visualLogView
                            .frame(maxWidth: 280) // Ограничиваем только ширину
                            .padding(.trailing, 16)
                            .padding(.bottom, 120) // Подняли чуть выше, чтобы не мешало кнопке отправки
                    }
                }
                // .ignoresSafeArea() // Убрали, чтобы окно логов поднималось вместе с клавиатурой
            )
            #endif
        }
    }



    // MARK: - Static Helper Functions
// MARK: - Static Helper Functions

extension ALADDINApp {
    // MARK: - Static Properties
    private static var hasInitializedNavigation = false

    // MARK: - Navigation Initialization
    private static func initializeNavigation(navigationManager: NavigationManager, localizationManager: LocalizationManager) {
        // 📊 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ: Замер времени инициализации
        let startTime = Date()

        // ✅ КРИТИЧНО: ПЕРВЫЙ ЗАПУСК - СБРАСЫВАЕМ ВСЕ СОСТОЯНИЕ
        if !ALADDINApp.hasInitializedNavigation {
            print("🛠️ [ALADDINApp.initializeNavigation] Первый запуск - сбрасываем состояние")
            // Принудительный сброс онбординга для первого запуска
            UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            UserDefaults.standard.synchronize()
        }

        // ✅ Используем статический флаг для предотвращения повторной инициализации
        if ALADDINApp.hasInitializedNavigation {
            print("🛠️ [ALADDINApp.initializeNavigation] Уже инициализировано, пропускаем")
            return
        }

        ALADDINApp.hasInitializedNavigation = true
        print("🛠️ [ALADDINApp.initializeNavigation] Начинаем инициализацию...")

        // ✅ Активируем бесплатный тариф при первом запуске
        let storeManager = StoreManager()
        if !storeManager.hasFreeTariff && !storeManager.hasActiveSubscription() {
            storeManager.activateFreeTariff()
            print("✅ First launch: Free tariff activated automatically")
        }

        // ✅ ЗАГРУЖАЕМ ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
        // UserProfileManager инициализируется автоматически при первом обращении
        // и загружает профиль в фоне
        // ВРЕМЕННО ОТКЛЮЧЕНО: _ = UserProfileManager.shared (может вызывать сетевые запросы)
        print("🚫 UserProfileManager initialization SKIPPED (temporary)")
        // _ = UserProfileManager.shared
        // print("✅ UserProfileManager initialized and profile loading started")

        // 🔔 ИНИЦИАЛИЗИРУЕМ PUSH УВЕДОМЛЕНИЯ
        // NotificationManager инициализируется для обработки push уведомлений
        // ВРЕМЕННО ОТКЛЮЧЕНО: _ = NotificationManager.shared (логирует в init)
        print("🚫 NotificationManager initialization SKIPPED (temporary)")
        // _ = NotificationManager.shared
        // ВРЕМЕННО ОТКЛЮЧЕНО: MasterLogger.shared.business("NotificationManager initialized for push notifications")

        // Запрашиваем разрешение на push уведомления (асинхронно, не блокирует UI)
        Task {
            let granted = await NotificationManager.shared.requestAuthorization()
            if granted {
                // ВРЕМЕННО ОТКЛЮЧЕНО: MasterLogger.shared.business("Push notifications authorized by user")
                print("✅ Push notifications authorized by user")
            } else {
                // ВРЕМЕННО ОТКЛЮЧЕНО: MasterLogger.shared.business("Push notifications denied by user")
                print("❌ Push notifications denied by user")
            }
        }

        let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        print("🛠️ [ALADDINApp.initializeNavigation] onboardingDone = \(onboardingDone)")

        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Всегда начинаем с онбординга при первом запуске
        if !onboardingDone {
            // Первый запуск - всегда показываем онбординг
            print("🔴 ONBOARDING: Первый запуск - показываем онбординг")
            navigationManager.currentScreen = .onboarding
        } else {
            // Онбординг пройден - переходим на main
            print("🟢 ONBOARDING: Пройден - переходим на главный экран")
            navigationManager.currentScreen = .main
        }

        // 📊 МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ: Логируем время инициализации
        let initTime = Date().timeIntervalSince(startTime)
        // ВРЕМЕННО ОТКЛЮЧЕНО: MasterLogger.shared.performance("App initialization completed in \(String(format: "%.2f", initTime)) seconds")
        print("✅ App initialization completed in \(String(format: "%.2f", initTime)) seconds")
    }

    /// Автоматически проверяет и удаляет debug токены при запуске
    /// Возвращает true, если были обнаружены и удалены debug токены
    static func autoFixDebugTokensIfNeeded() -> Bool {
        let keychain = KeychainManager.shared

        // Проверяем access token
        var isDebugToken = false
        // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
        if let accessToken = keychain.loadString(forKey: .authToken) {
            // Проверяем признаки debug токена
            if accessToken.contains(".debugsignature") {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug access token (содержит .debugsignature)")
            } else if accessToken.count == 140 && accessToken.contains("eyJhbGciOi") {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug access token (длина 140)")
            }
        }

        // Проверяем refresh token
        // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
        if let refreshToken = keychain.loadString(forKey: .refreshToken) {
            if refreshToken == "debug-refresh-token" {
                isDebugToken = true
                print("⚠️ ALADDINApp: Обнаружен debug refresh token")
            }
        }

        // Если обнаружены debug токены - удаляем их
        if isDebugToken {
            print("🔧 ALADDINApp: Автоматически удаляем debug токены...")
            keychain.delete(forKey: .authToken)
            keychain.delete(forKey: .refreshToken)
            AppConfig.authToken = nil
            UserDefaults.standard.removeObject(forKey: "refresh_token_not_supported")
            print("✅ ALADDINApp: Debug токены удалены!")
            print("⚠️ ALADDINApp: ВАЖНО! Выполните реальный логин через Debug Console:")
            print("   performRealLogin(email: \"ваш_email\", password: \"ваш_пароль\") { _ in }")
            return true
        } else {
            print("✅ ALADDINApp: Debug токены не обнаружены")
            return false
        }
    }

    
}

#if DEBUG
private enum DebugAuthTokenSeeder {
    // ✅ ИСПРАВЛЕНИЕ: Убираем debug токены, которые не принимает сервер
    // Вместо этого приложение будет работать в демо режиме
    private static let demoAccessToken = ""
    private static let demoRefreshToken = ""
    
    static func seedIfNeeded() {
        // ✅ ИСПРАВЛЕНИЕ: Не создаем debug токены - приложение работает в демо режиме
        #if DEBUG
        print("ℹ️ DEBUG: Debug токены отключены - приложение работает в демо режиме")
        print("ℹ️ DEBUG: Для тестирования API используйте performRealLogin() в Debug Console")
        #endif
    }
}
#endif

#if DEBUG
// MARK: - Debug Console Functions

func clearDebugTokens() -> Bool {
    let keychain = KeychainManager.shared
    keychain.delete(forKey: .authToken)
    keychain.delete(forKey: .refreshToken)
    AppConfig.authToken = nil
    UserDefaults.standard.removeObject(forKey: "refresh_token_not_supported")
    print("✅ Debug токены удалены. Выполните реальный логин.")
    return true
}

func performRealLogin(email: String, password: String, completion: @escaping (Bool) -> Void) {
    print("🔐 Выполняем логин для \(email)...")
    print("   - Endpoint: \(AppConfig.Endpoint.login)")
    print("   - Base URL: \(AppConfig.apiBaseURL)")
    print("   - Full URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
    
    APIService.shared.login(email: email, password: password) { result in
        switch result {
        case .success(_):
            print("✅ Логин успешен! Токены сохранены в Keychain.")
            
            // ✅ ПРОВЕРКА: Убеждаемся, что токены действительно сохранены
            let keychain = KeychainManager.shared
            var tokensSaved = true
            
            // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
            if let accessToken = keychain.loadString(forKey: .authToken) {
                print("   - Access token сохранен (длина: \(accessToken.count))")
            } else {
                print("   - ⚠️ Access token НЕ найден в Keychain!")
                tokensSaved = false
            }
            
            if let refreshToken = keychain.loadString(forKey: .refreshToken) {
                print("   - Refresh token сохранен (длина: \(refreshToken.count))")
            } else {
                print("   - ⚠️ Refresh token НЕ найден в Keychain!")
                tokensSaved = false
            }
            
            if tokensSaved {
                print("✅ Теперь тумблеры должны работать!")

                // 🔄 Синхронизация демо-настроек после логина
                syncDemoSettingsToServer()

                completion(true)
            } else {
                print("❌ Токены не были сохранены в Keychain!")
                completion(false)
            }
        case .failure(let error):
            print("❌ Ошибка логина: \(error.localizedDescription)")
            
            // ✅ ДЕТАЛЬНАЯ ДИАГНОСТИКА ОШИБКИ
            if let networkError = error as? NetworkError {
                switch networkError {
                case .invalidStatusCode(let code):
                    print("   - HTTP Status: \(code)")
                    if code == 404 {
                        print("   - ⚠️ Endpoint не найден! Проверьте правильность endpoint на сервере")
                        print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                    } else if code == 401 {
                        print("   - ⚠️ Неверные credentials (email или password)")
                    } else if code == 403 {
                        print("   - ⚠️ Доступ запрещен")
                    }
                case .httpError(let code):
                    print("   - HTTP Error \(code)")
                    if code == 404 {
                        print("   - ⚠️ Endpoint не найден! Проверьте правильность endpoint на сервере")
                        print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                    } else if code == 401 {
                        print("   - ⚠️ Неверные credentials (email или password)")
                    } else if code == 403 {
                        print("   - ⚠️ Доступ запрещен")
                    }
                case .notFound(let message):
                    print("   - ⚠️ Endpoint не найден: \(message ?? "Not Found")")
                    print("   - Проверьте: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                case .unauthorized(let message):
                    print("   - ⚠️ Неверные credentials: \(message ?? "Unauthorized")")
                case .forbidden(let message):
                    print("   - ⚠️ Доступ запрещен: \(message ?? "Forbidden")")
                case .invalidURL:
                    print("   - ⚠️ Неверный URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
                default:
                    print("   - Тип ошибки: \(networkError)")
                }
            }
            
            print("⚠️ Проверьте:")
            print("   1. Правильность email и password")
            print("   2. Доступность сервера: \(AppConfig.apiBaseURL)")
            print("   3. Правильность endpoint: \(AppConfig.Endpoint.login)")
            print("   4. Полный URL: \(AppConfig.apiBaseURL)\(AppConfig.Endpoint.login)")
            
            completion(false)
        }
    }
}

/// Проверяет, являются ли текущие токены debug токенами
/// Использование в Debug Console: checkIfTokensAreDebug()
func checkIfTokensAreDebug() -> Bool {
    let keychain = KeychainManager.shared
    var isDebug = false
    
    // ✅ ИСПРАВЛЕНО: Используем loadString вместо load(String.self, ...)
    if let accessToken = keychain.loadString(forKey: .authToken) {
        if accessToken.contains(".debugsignature") || (accessToken.count == 140 && accessToken.contains("eyJhbGciOi")) {
            print("⚠️ Обнаружен debug access token")
            isDebug = true
        }
    }
    
    if let refreshToken = keychain.loadString(forKey: .refreshToken) {
        if refreshToken == "debug-refresh-token" {
            print("⚠️ Обнаружен debug refresh token")
            isDebug = true
        }
    }
    
    if isDebug {
        print("❌ Токены являются debug токенами. Выполните: clearDebugTokens() и затем performRealLogin()")
    } else {
        print("✅ Токены не являются debug токенами")
    }
    
    return isDebug
}

/// 🔄 Синхронизация демо-настроек на сервер после авторизации
func syncDemoSettingsToServer() {
    print("🔄 Начинаем синхронизацию демо-настроек на сервер...")

    let demoComponentIds = [
        "crash_detection_agent",
        "roadside_assistance_agent",
        "incident_response_agent",
        "emergency_response_bot",
        "emergency_event_manager",
        "phishing_protection_agent",
        "malware_detection_agent",
        "mobile_security_agent",
        "network_security_agent",
        "password_security_agent"
    ]

    Task {
        for componentId in demoComponentIds {
            let demoKey = "demo_\(componentId)"
            if let demoValue = UserDefaults.standard.object(forKey: demoKey) as? Bool {
                print("   📤 Синхронизируем \(componentId): \(demoValue)")

                do {
                    try await APIService.shared.updateComponentStatus(
                        componentId: componentId,
                        isEnabled: demoValue
                    )
                    print("   ✅ \(componentId) синхронизирован")

                    // Удаляем демо-настройку после успешной синхронизации
                    UserDefaults.standard.removeObject(forKey: demoKey)
                } catch {
                    print("   ❌ Ошибка синхронизации \(componentId): \(error.localizedDescription)")
                }
            } else {
                print("   ⏭️ Нет демо-настройки для \(componentId)")
            }
        }

        print("✅ Синхронизация демо-настроек завершена")
    }
}
#endif

// MARK: - Loading View

/// ✅ НОВОЕ: View для отображения загрузки приложения
struct AppLoadingView: View {
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color.primaryBlue.opacity(0.8), Color.secondaryBlue.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: Spacing.xl) {
                Spacer()

                // Логотип или иконка приложения
                ZStack {
                    Circle()
                        .fill(Color.secondaryGold.opacity(0.2))
                        .frame(width: 120, height: 120)

                    Text("🦄")
                        .font(.system(size: 60))
                }

                // Текст загрузки
                Text("ALADDIN")
                    .font(.system(size: 32, weight: .bold))
                    .foregroundColor(.secondaryGold)
                    .shadow(color: Color.secondaryGold.opacity(0.5), radius: 10)

                Text("Подготовка приложения...")
                    .font(.body)
                    .foregroundColor(.white.opacity(0.8))

                // Анимация загрузки
                ProgressView()
                    .scaleEffect(1.2)
                    .tint(.secondaryGold)
                    .padding(.top, Spacing.m)

                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
}
