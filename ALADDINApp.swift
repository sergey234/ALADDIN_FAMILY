import SwiftUI

@main
struct ALADDINApp: App {
    // КРИТИЧНО: Инициализация NavigationManager
    @StateObject private var navigationManager = NavigationManager()
    
    var body: some Scene {
        WindowGroup {
            // КРИТИЧНО: NavigationView для работы навигации
            NavigationView {
                MainScreen()
                    .navigationBarHidden(true)
            }
            .navigationViewStyle(StackNavigationViewStyle())
            // КРИТИЧНО: Передача NavigationManager через EnvironmentObject
            .environmentObject(navigationManager)
        }
    }
}
