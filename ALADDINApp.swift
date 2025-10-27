import SwiftUI

@main
struct ALADDINApp: App {
    // КРИТИЧНО: Инициализация NavigationManager
    @StateObject private var navigationManager = NavigationManager()
    
    init() {
        // ✅ ПРОВЕРЯЕМ РОЛЬ ПРИ ЗАПУСКЕ
        checkAndNavigateToUserInterface()
    }
    
    var body: some Scene {
        WindowGroup {
            // КРИТИЧНО: NavigationView для работы навигации
            NavigationView {
                // КРИТИЧНО: ID принудительно обновляет SwiftUI при изменении currentScreen
                Group {
                    let _ = print("🔍 DEBUG ALADDINApp: Рендер currentScreen = \(navigationManager.currentScreen)")
                    
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
                    case .elderlyInterface:
                        ElderlyInterfaceScreen()
                            .id("elderlyInterface")
                            .onAppear { print("🔍 DEBUG: ElderlyInterfaceScreen отображён") }
                    case .tariffs:
                        TariffsScreen()
                            .id("tariffs")
                    case .profile:
                        ProfileScreen()
                            .id("profile")
                    case .notifications:
                        NotificationsScreen()
                            .id("notifications")
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
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            switch role {
            case .parent:
                self.navigationManager.navigateTo(.parentalControl)
                print("👨‍👩‍👧 Переход к ParentalControlScreen")
            case .child:
                self.navigationManager.navigateTo(.childInterface)
                print("👶 Переход к ChildInterfaceScreen")
            case .grandparent:
                self.navigationManager.navigateTo(.elderlyInterface)
                print("👵 Переход к ElderlyInterfaceScreen")
            }
        }
    }
}

