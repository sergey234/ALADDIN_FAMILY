import SwiftUI
import Foundation

/// 👤 Profile View Model
/// Логика для экрана профиля
class ProfileViewModel: ObservableObject {
    
    @Published var userName: String = ""
    @Published var userEmail: String = ""
    @Published var userPhone: String = ""
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
    
    init(apiService: APIService? = nil) {
        self.networkManager = NetworkManager() // Для обратной совместимости, но не используется
        self.apiService = apiService ?? APIService.shared
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
                    
                    // ✅ ПЛАНИРОВАНИЕ УВЕДОМЛЕНИЙ О ПОДПИСКЕ (при загрузке профиля)
                    // Если есть активная подписка с датой окончания, планируем уведомления
                    if let endDateString = profile.subscriptionEndDate,
                       !endDateString.isEmpty,
                       let endDate = self?.parseSubscriptionEndDate(endDateString),
                       endDate > Date() {
                        NotificationManager.shared.scheduleRenewalNotifications(subscriptionEndDate: endDate)
                        print("✅ Уведомления о подписке запланированы при загрузке профиля до \(endDate)")
                    }
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
    
    // MARK: - Subscription End Date Parsing
    
    /**
     * Парсинг даты окончания подписки из строки
     * Поддерживает различные форматы: ISO8601, "dd.MM.yyyy", "yyyy-MM-dd"
     */
    private func parseSubscriptionEndDate(_ dateString: String) -> Date? {
        // Пробуем ISO8601 формат
        let isoFormatter = ISO8601DateFormatter()
        if let date = isoFormatter.date(from: dateString) {
            return date
        }
        
        // Пробуем формат "dd.MM.yyyy" (например, "31.12.2025")
        let dotFormatter = DateFormatter()
        dotFormatter.dateFormat = "dd.MM.yyyy"
        dotFormatter.locale = Locale(identifier: "ru_RU")
        if let date = dotFormatter.date(from: dateString) {
            return date
        }
        
        // Пробуем формат "yyyy-MM-dd"
        let dashFormatter = DateFormatter()
        dashFormatter.dateFormat = "yyyy-MM-dd"
        if let date = dashFormatter.date(from: dateString) {
            return date
        }
        
        // Пробуем стандартный формат
        let standardFormatter = DateFormatter()
        standardFormatter.dateStyle = .medium
        standardFormatter.timeStyle = .none
        if let date = standardFormatter.date(from: dateString) {
            return date
        }
        
        print("⚠️ Не удалось распарсить дату окончания подписки: \(dateString)")
        return nil
    }
}



