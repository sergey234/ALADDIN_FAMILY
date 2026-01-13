import SwiftUI

@main
struct ALADDINApp: App {
    // КРИТИЧНО: Инициализация NavigationManager
    @StateObject private var navigationManager = NavigationManager()
    // ✅ Добавляем LocalizationManager
    @StateObject private var localizationManager = LocalizationManager()
    @AppStorage("selected_theme") private var selectedTheme: String = "system"
    // ✅ ИСПРАВЛЕНИЕ: Отслеживаем состояние приложения для предотвращения сброса навигации
    @Environment(\.scenePhase) private var scenePhase
    // Убрали @AppStorage для онбординга
    // private var hasCompletedOnboarding: Bool = false // больше не используется
    
    init() {
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
        DebugAuthTokenSeeder.seedIfNeeded()
#endif
    }
    
    var body: some Scene {
        WindowGroup {
            // КРИТИЧНО: NavigationView для работы навигации
            NavigationView {
                // ✅ КРИТИЧНО: Используем AnyView для каждого case - это заставит SwiftUI пересчитать
                Group {
                    switch navigationManager.currentScreen {
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
                    }
                }
                .id("screen_\(navigationManager.currentScreen.rawValue)")  // ✅ Дополнительный ID для принудительного обновления
                .onAppear {
                    print("🔍 DEBUG ALADDINApp: Рендер currentScreen = \(navigationManager.currentScreen)")
                }
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
            // ✅ КРИТИЧНО: Инициализация навигации при первом появлении
            .onAppear {
                // Используем замыкание с захватом для безопасного доступа к StateObject
                let navManager = navigationManager
                let locManager = localizationManager
                initializeNavigation(navigationManager: navManager, localizationManager: locManager)
            }
            // ✅ ИСПРАВЛЕНИЕ: Отслеживаем возврат из Safari/других приложений
            .onChange(of: scenePhase) { newPhase in
                if newPhase == .active {
                    // Приложение стало активным (вернулись из Safari/фона)
                    // НЕ перенаправляем на онбординг, если уже прошли его
                    let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
                    if onboardingDone {
                        if navigationManager.currentScreen == .onboarding {
                            // Если случайно оказались на онбординге, возвращаемся на главную
                            print("🔄 Возврат из фона: обнаружен онбординг при пройденном онбординге - исправляем")
                            navigationManager.currentScreen = .main
                        }
                        // ✅ КРИТИЧНО: Не вызываем initializeNavigation повторно при возврате из фона
                        // Это предотвращает сброс навигации на реальном устройстве
                        print("🔄 Возврат из фона: онбординг пройден, текущий экран = \(navigationManager.currentScreen)")
                    }
                }
            }
            // ✅ КРИТИЧНО: Дополнительное отслеживание изменений
            .onChange(of: navigationManager.currentScreen) { newScreen in
                print("🚨🚨🚨 ALADDINApp.onChange: currentScreen изменился на \(newScreen)")
                print("🚨🚨🚨 ALADDINApp: Обновляем switch statement")
                
                // ✅ КРИТИЧНО: Принудительное обновление через RunLoop
                RunLoop.main.perform {
                    print("🚨 ALADDINApp: RunLoop.perform выполнен")
                }
            }
            // 🌓 ПРИМЕНЯЕМ ТЕМУ
            .preferredColorScheme(getPreferredColorScheme())
        }
    }  // ✅ Закрывает body: some Scene
    
    // MARK: - Theme Helper
    
    private func getPreferredColorScheme() -> ColorScheme? {
        switch selectedTheme {
        case "light": return .light
        case "dark": return .dark
        case "system": return nil // nil = системная тема
        default: return nil
        }
    }
    
    // MARK: - Инициализация навигации
    
    /// ✅ Инициализация навигации при первом запуске приложения
    /// Вызывается в .onAppear, когда все @StateObject уже созданы
    private static var hasInitialized = false
    
    private func initializeNavigation(navigationManager: NavigationManager, localizationManager: LocalizationManager) {
        // ✅ Используем статический флаг для предотвращения повторной инициализации
        if ALADDINApp.hasInitialized {
            print("🛠️ [ALADDINApp.initializeNavigation] Уже инициализировано, пропускаем")
            // ✅ КРИТИЧНО: Даже если уже инициализировано, проверяем что мы не на онбординге случайно
            let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            if onboardingDone && navigationManager.currentScreen == .onboarding {
                print("⚠️ [ALADDINApp.initializeNavigation] Обнаружен онбординг при уже пройденном онбординге - исправляем")
                navigationManager.currentScreen = .main
            }
            return
        }
        
        ALADDINApp.hasInitialized = true
        print("🛠️ [ALADDINApp.initializeNavigation] Начинаем инициализацию...")
        
        // ✅ Активируем бесплатный тариф при первом запуске
        let storeManager = StoreManager()
        if !storeManager.hasFreeTariff && !storeManager.hasActiveSubscription() {
            storeManager.activateFreeTariff()
            print("✅ First launch: Free tariff activated automatically")
        }
        
        let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        print("🛠️ [ALADDINApp.initializeNavigation] onboardingDone = \(onboardingDone)")
        
        // ✅ ИСПРАВЛЕНИЕ: НЕ используем задержку, проверяем сразу и только если действительно первый запуск
        // ✅ КРИТИЧНО: Не перенаправляем на онбординг, если пользователь уже на другом экране
        if !onboardingDone {
            // Только если онбординг не пройден И мы на главной странице (первый запуск)
            // ✅ КРИТИЧНО: Проверяем, что это действительно первый запуск, а не возврат из фона
            if navigationManager.currentScreen == .main && navigationManager.navigationStack.isEmpty {
                print("🔴 ONBOARDING: Показываю онбординг на первом запуске")
                navigationManager.navigationStack.removeAll()
                navigationManager.currentScreen = .onboarding
            } else {
                print("🟡 ONBOARDING: Онбординг не пройден, но уже на экране \(navigationManager.currentScreen) или стек не пуст - не перенаправляем")
            }
        } else {
            print("🟢 ONBOARDING: Пропущен, остаёмся на текущем экране \(navigationManager.currentScreen)")
            // ✅ ИСПРАВЛЕНИЕ: НЕ меняем currentScreen, если онбординг уже пройден
            // Пользователь может быть на любом экране, не нужно его сбрасывать на main
            // ✅ КРИТИЧНО: Если случайно оказались на онбординге, возвращаемся на главную
            if navigationManager.currentScreen == .onboarding {
                print("⚠️ ONBOARDING: Обнаружен онбординг при пройденном онбординге - исправляем")
                navigationManager.currentScreen = .main
            }
        }
    }
    
    // MARK: - Проверка роли при запуске
    
    // ✅ ОТКЛЮЧЕНО: Автоматическое перенаправление по ролям
    // Пользователь сам выбирает экран через главное меню
    private func checkAndNavigateToUserInterface(navigationManager: NavigationManager) {
        // Остаёмся на главной странице
        print("✅ Остаёмся на главной странице")
        navigationManager.currentScreen = .main
    }
}

#if DEBUG
private enum DebugAuthTokenSeeder {
    private static let demoAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQwOTk2ODAwMDAsInN1YiI6ImRlYnVnLWF1dGgiLCJuYW1lIjoiQUxBRERJTiBEZWJ1ZyBUb2tlbiJ9.debugsignature"
    private static let demoRefreshToken = "debug-refresh-token"
    
    static func seedIfNeeded() {
        let keychain = KeychainManager.shared
        let hasAccessToken = keychain.isDataAvailable(forKey: .authToken)
        
        guard !hasAccessToken else {
            #if DEBUG
            print("✅ DEBUG: auth_token уже есть в Keychain")
            #endif
            return
        }

        if let accessData = try? JSONEncoder().encode(demoAccessToken) {
            keychain.save(accessData, forKey: .authToken)
        }
        if let refreshData = try? JSONEncoder().encode(demoRefreshToken) {
            keychain.save(refreshData, forKey: .refreshToken)
        }
        #if DEBUG
        print("✅ DEBUG: Тестовые auth/refresh токены сохранены в Keychain (seedIfNeeded)")
        #endif
    }
}
#endif
