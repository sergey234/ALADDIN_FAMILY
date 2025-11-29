import SwiftUI

@main
struct ALADDINApp: App {
    // КРИТИЧНО: Инициализация NavigationManager
    @StateObject private var navigationManager = NavigationManager()
    @AppStorage("selected_theme") private var selectedTheme: String = "system"
    // Убрали @AppStorage для онбординга
    // private var hasCompletedOnboarding: Bool = false // больше не используется
    
    init() {
        if ProcessInfo.processInfo.environment["RESET_ONBOARDING"] == "1" {
            UserDefaults.standard.set(false, forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
            print("🌍 RESET_ONBOARDING активирован — ключ сброшен")
        }
        let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        print("🛠️ [ALADDINApp.init] Текущее значение onboardingDone = \(onboardingDone)")
        if !onboardingDone {
            navigationManager.navigationStack.removeAll()
            navigationManager.currentScreen = .onboarding
            print("🔴 ONBOARDING: Показываю онбординг на старте (hasCompletedOnboarding=\(onboardingDone))")
            return
        }
        print("🟢 ONBOARDING: Пропущен, продолжаю обычную навигацию")
        checkAndNavigateToUserInterface()
    }
    
    var body: some Scene {
        WindowGroup {
            // КРИТИЧНО: NavigationView для работы навигации
            NavigationView {
                // КРИТИЧНО: ID принудительно обновляет SwiftUI при изменении currentScreen
                Group {
                    // ✅ УБРАЛИ print из body - может замедлить SwiftUI рендеринг
                    // let _ = print("🔍 DEBUG ALADDINApp: Рендер currentScreen = \(navigationManager.currentScreen)")
                    
                    switch navigationManager.currentScreen {
                    case .main:
                        MainScreen()
                            .id("main")
                    case .family:
                        FamilyScreen()
                            .id("family")
                    case .vpn:
                        VPNScreen()
                            .id("vpn")
                    case .analytics:
                        AnalyticsScreen()
                            .id("analytics")
                    case .settings:
                        SettingsScreen()
                            .id("settings")
                    case .aiAssistant:
                        AIAssistantScreen()
                            .id("aiAssistant")
                    case .parentalControl:
                        ParentalControlScreen()
                            .id("parentalControl")
                            .onAppear { print("🔍 DEBUG: ParentalControlScreen отображён") }
                    case .childInterface:
                        ChildInterfaceScreen()
                            .id("childInterface")
                            .onAppear { print("🔍 DEBUG: ChildInterfaceScreen отображён") }
                    case .securityEducation:
                        SecurityEducationScreen()
                            .id("securityEducation")
                            .onAppear { print("🔍 DEBUG: SecurityEducationScreen отображён") }
                    case .elderlyInterface:
                        ElderlyInterfaceScreen()
                            .id("elderlyInterface")
                            .onAppear { print("🔍 DEBUG: ElderlyInterfaceScreen отображён") }
                    case .tariffs:
                        TariffsScreen()
                            .id("tariffs")
                    case .paymentQR:
                        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Используем AnyView для отложенного создания View
                        // Это предотвращает попытку SwiftUI вычислить body до готовности данных
                        let _ = print("🚨🚨🚨 ALADDINApp: РЕНДЕР .paymentQR - НАЧАЛО 🚨🚨🚨")
                        let _ = print("🔍 selectedTariffForPayment: \(navigationManager.selectedTariffForPayment != nil ? "НЕ nil" : "nil")")
                        
                        if let tariff = navigationManager.selectedTariffForPayment {
                            let _ = print("🔍 ALADDINApp: Tariff найден - id: '\(tariff.id)', title: '\(tariff.title)'")
                            
                            // ✅ Дополнительная проверка валидности тарифа
                            if !tariff.id.isEmpty && !tariff.title.isEmpty {
                                let _ = print("✅ ALADDINApp: Tariff валиден, создаём PaymentQRScreen...")
                                
                                // ✅ Обертка в AnyView для безопасности инициализации
                                AnyView(
                                    PaymentQRScreen(tariff: tariff) {
                                        print("🔍 ALADDINApp: onPaymentCompleted вызван")
                                        navigationManager.goBack()
                                        navigationManager.selectedTariffForPayment = nil
                                    }
                                    .id("paymentQR")
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
                                            navigationManager.goBack()
                                            navigationManager.selectedTariffForPayment = nil
                                        }
                                    }
                                    .padding()
                                    .id("paymentQR_error_invalid")
                                )
                            }
                        } else {
                            // ✅ Fallback если тариф не передан
                            AnyView(
                                VStack(spacing: 20) {
                                    Text("Ошибка: тариф не выбран")
                                        .font(.headline)
                                    Button("Назад") {
                                        navigationManager.goBack()
                                    }
                                }
                                .padding()
                                .id("paymentQR_error_nil")
                            )
                        }
                    case .profile:
                        ProfileScreen()
                            .id("profile")
                    case .notifications:
                        NotificationsScreen()
                            .id("notifications")
                    case .privacyPolicy:
                        PrivacyPolicyScreen()
                            .id("privacyPolicy")
                    case .termsOfService:
                        TermsOfServiceScreen()
                            .id("termsOfService")
                    default:
                        MainScreen()
                            .id("default")
                    }
                }
                .navigationBarHidden(true)
            }
            .navigationViewStyle(StackNavigationViewStyle())
            // КРИТИЧНО: Передача NavigationManager через EnvironmentObject
            .environmentObject(navigationManager)
            // КРИТИЧНО: Принудительное обновление при изменении currentScreen
            .id(navigationManager.currentScreen.rawValue)
            // 🌓 ПРИМЕНЯЕМ ТЕМУ
            .preferredColorScheme(getPreferredColorScheme())
        }
    }
    
    // MARK: - Theme Helper
    
    private func getPreferredColorScheme() -> ColorScheme? {
        switch selectedTheme {
        case "light": return .light
        case "dark": return .dark
        case "system": return nil // nil = системная тема
        default: return nil
        }
    }
    
    // MARK: - Проверка роли при запуске
    
    private func checkAndNavigateToUserInterface() {
        guard let roleString = UserDefaults.standard.string(forKey: "current_user_role") else {
            // Роли нет - остаёмся на главной
            print("ℹ️ Роль пользователя не найдена, остаёмся на Main")
            return
        }
        
        // Проверяем, что роль валидна
        guard let role = FamilyRole(rawValue: roleString) else {
            print("⚠️ Неизвестная роль: \(roleString)")
            return
        }
        
        print("✅ Найдена роль: \(role.rawValue)")
        
        // Автопереход на соответствующий интерфейс
        // Используем async для гарантированного выполнения после инициализации
        DispatchQueue.main.async {
            // Небольшая задержка для завершения инициализации NavigationManager
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                switch role {
                case .parent:
                    self.navigationManager.navigateTo(.parentalControl)
                    print("👨‍👩‍👧 Переход к ParentalControlScreen")
                    print("🔍 DEBUG: currentScreen после перехода = \(self.navigationManager.currentScreen)")
                case .child:
                    self.navigationManager.navigateTo(.childInterface)
                    print("👶 Переход к ChildInterfaceScreen")
                    print("🔍 DEBUG: currentScreen после перехода = \(self.navigationManager.currentScreen)")
                case .grandparent:
                    self.navigationManager.navigateTo(.elderlyInterface)
                    print("👵 Переход к ElderlyInterfaceScreen")
                    print("🔍 DEBUG: currentScreen после перехода = \(self.navigationManager.currentScreen)")
                }
            }
        }
    }
}

