import SwiftUI

@main
struct TestApp: App {
    var body: some Scene {
        WindowGroup {
            MainScreen()
                .environmentObject(MainViewModel())
                .environmentObject(NavigationManager())
                .environmentObject(LocalizationManager.shared)
                .environmentObject(SubscriptionManager.shared)
        }
    }
}

