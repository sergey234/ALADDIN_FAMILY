import SwiftUI

/// 👤 Profile View Model
/// Логика для экрана профиля
class ProfileViewModel: ObservableObject {
    
    @Published var userName: String = "Сергей Хлыстов"
    @Published var userEmail: String = "sergey@aladdin.family"
    @Published var userPhone: String = "+7 (999) 123-45-67"
    @Published var registrationDate: String = "15 сентября 2025"
    @Published var subscriptionType: String = "Premium"
    @Published var subscriptionEndDate: String = "31.12.2025"
    @Published var threatsBlocked: Int = 47
    @Published var familyMembers: Int = 4
    @Published var devices: Int = 8
    
    func editProfile() {
        print("Show edit profile sheet")
    }
    
    func changePassword() {
        print("Show change password")
    }
    
    func manageTwoFactor() {
        print("Manage 2FA")
    }
    
    func showActiveSessions() {
        print("Show active sessions")
    }
    
    func deleteAccount() {
        print("Show delete account confirmation")
    }
}



