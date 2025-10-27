import SwiftUI

@main
struct ALADDINApp: App {
    // КРИТИЧНО: Инициализация NavigationManager
    @StateObject private var navigationManager = NavigationManager()
    
    var body: some Scene {
        WindowGroup {
            // КРИТИЧНО: NavigationView для работы навигации
            NavigationView {
                // КРИТИЧНО: Отслеживаем currentScreen и показываем нужный экран
                Group {
                    let _ = print("🔍 DEBUG ALADDINApp: Рендер currentScreen = \(navigationManager.currentScreen)")
                    
                    switch navigationManager.currentScreen {
                    case .main:
                        MainScreen()
                    case .family:
                        FamilyScreen()
                    case .vpn:
                        VPNScreen()
                    case .analytics:
                        AnalyticsScreen()
                    case .settings:
                        SettingsScreen()
                    case .aiAssistant:
                        AIAssistantScreen()
                    case .parentalControl:
                        ParentalControlScreen()
                            .onAppear { print("🔍 DEBUG: ParentalControlScreen отображён") }
                    case .childInterface:
                        ChildInterfaceScreen()
                            .onAppear { print("🔍 DEBUG: ChildInterfaceScreen отображён") }
                    case .elderlyInterface:
                        ElderlyInterfaceScreen()
                            .onAppear { print("🔍 DEBUG: ElderlyInterfaceScreen отображён") }
                    case .tariffs:
                        TariffsScreen()
                    case .profile:
                        ProfileScreen()
                    case .notifications:
                        NotificationsScreen()
                    default:
                        MainScreen()
                    }
                }
                .navigationBarHidden(true)
            }
            .navigationViewStyle(StackNavigationViewStyle())
            // КРИТИЧНО: Передача NavigationManager через EnvironmentObject
            .environmentObject(navigationManager)
        }
    }
}
