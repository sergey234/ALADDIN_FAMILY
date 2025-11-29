import SwiftUI
import Combine

/// ⚙️ Settings View Model
/// Логика для экрана настроек
class SettingsViewModel: ObservableObject {
    
    @Published var isVPNEnabled: Bool = true
    @Published var isNotificationsEnabled: Bool = true
    @Published var isBiometricEnabled: Bool = true
    @Published var protectionLevel: Double = 75
    @Published var selectedLanguage: String = "Русский"
    @Published var selectedTheme: String = "Тёмная"
    @Published var cacheSize: String = "47 MB"
    
    func toggleVPN() {
        isVPNEnabled.toggle()
    }
    
    func toggleNotifications() {
        isNotificationsEnabled.toggle()
    }
    
    func toggleBiometric() {
        isBiometricEnabled.toggle()
    }
    
    func updateProtectionLevel(_ value: Double) {
        protectionLevel = value
    }
    
    func changeLanguage() {
        print("Show language picker")
    }
    
    func changeTheme() {
        print("Show theme picker")
    }
    
    func clearCache() {
        print("Clear cache")
        cacheSize = "0 MB"
    }
    
    func logout() {
        print("Logout user")
    }
}



