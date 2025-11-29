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
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    // Зависимости
    private let apiService: APIService
    private let networkManager: NetworkManager
    
    init(apiService: APIService? = nil, networkManager: NetworkManager? = nil) {
        self.networkManager = networkManager ?? NetworkManager()
        self.apiService = apiService ?? APIService(networkManager: self.networkManager)
    }
    
    // Загрузка профиля из API
    func loadProfile() {
        isLoading = true
        errorMessage = nil
        
        apiService.getUserProfile { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let profile):
                    // ✅ ИСПРАВЛЕНО: profile.name и profile.email - не опциональные (String), убрали ??
                    self?.userName = profile.name
                    self?.userEmail = profile.email
                    // ✅ phone опциональный (String?), используем ?? для него
                    self?.userPhone = profile.phone ?? "+7 (999) 123-45-67"
                    self?.registrationDate = profile.registrationDate
                    self?.subscriptionType = profile.subscriptionType
                    self?.subscriptionEndDate = profile.subscriptionEndDate ?? ""
                    self?.threatsBlocked = profile.threatsBlocked
                    self?.familyMembers = profile.familyMembers
                    self?.devices = profile.devices
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    print("❌ Ошибка загрузки профиля: \(error.localizedDescription)")
                }
            }
        }
    }
    
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



