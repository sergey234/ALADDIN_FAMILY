import SwiftUI

/**
 * 🚀 ALADDIN App
 * Главный файл iOS приложения
 * Entry point для всего приложения
 */

@main
struct ALADDINApp: App {
    
    // MARK: - State
    
    @StateObject private var navigationManager = NavigationManager()
    @StateObject private var networkManager = NetworkManager()
    @AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding = false
    
    // MARK: - Body
    
    var body: some Scene {
        WindowGroup {
            ZStack {
                // Фон приложения
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                // Главный контент
                if hasCompletedOnboarding {
                    // Основное приложение
                    NavigationStack(path: $navigationManager.path) {
                        MainScreen()
                            .navigationDestination(for: NavigationDestination.self) { destination in
                                destinationView(for: destination)
                            }
                    }
                    .environmentObject(navigationManager)
                    .environmentObject(networkManager)
                } else {
                    // Онбординг
                    OnboardingScreen()
                        .onAppear {
                            // После завершения онбординга установится hasCompletedOnboarding = true
                        }
                }
            }
        }
    }
    
    // MARK: - Navigation Destination Views
    
    @ViewBuilder
    private func destinationView(for destination: NavigationDestination) -> some View {
        switch destination {
        case .family:
            FamilyScreen()
        case .vpn:
            VPNScreen()
        case .analytics:
            AnalyticsScreen()
        case .aiAssistant:
            AIAssistantScreen()
        case .parentalControl:
            ParentalControlScreen()
        case .childInterface:
            ChildInterfaceScreen()
        case .elderlyInterface:
            ElderlyInterfaceScreen()
        case .settings:
            SettingsScreen()
        case .tariffs:
            TariffsScreen()
        case .profile:
            ProfileScreen()
        case .notifications:
            NotificationsScreen()
        case .support:
            SupportScreen()
        }
    }
}

/**
 * 🧭 Navigation Destination
 * Enum для всех экранов приложения
 */
enum NavigationDestination: Hashable {
    case family
    case vpn
    case analytics
    case aiAssistant
    case parentalControl
    case childInterface
    case elderlyInterface
    case settings
    case tariffs
    case profile
    case notifications
    case support
}




