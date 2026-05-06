import SwiftUI
import Foundation

// Master Logger for profile logging
private let logger = MasterLogger.shared

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
    
    @MainActor init(apiService: APIService? = nil) {
        logger.business("Initializing ProfileViewModel")
        self.networkManager = NetworkManager() // Для обратной совместимости, но не используется
        self.apiService = apiService ?? APIService.shared
    }
    
    // Загрузка профиля из API
    func loadProfile() {
        logger.business("Loading user profile")
        isLoading = true
        errorMessage = nil
        
        apiService.getUserProfile { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                
                switch result {
                case .success(let profile):
                    // ✅ ИСПРАВЛЕНО: Используем safe-проперти для опциональных полей
                    self?.userName = profile.name
                    self?.userEmail = profile.safeEmail // ✅ Используем safe-проперти
                    // ✅ phone опциональный (String?), используем ?? для него
                    self?.userPhone = profile.phone ?? "+7 (999) 123-45-67"
                    self?.registrationDate = profile.safeRegistrationDate // ✅ Используем safe-проперти
                    self?.subscriptionType = profile.safeSubscriptionType // ✅ Используем safe-проперти
                    self?.subscriptionEndDate = profile.subscriptionEndDate ?? ""
                    self?.threatsBlocked = profile.safeThreatsBlocked // ✅ Используем safe-проперти
                    self?.familyMembers = profile.safeFamilyMembers // ✅ Используем safe-проперти
                    self?.devices = profile.safeDevices // ✅ Используем safe-проперти

                    // ✅ ДОБАВЛЕНО: Сохраняем имя пользователя для детского интерфейса
                    self?.saveUserNameToCache(profile.name)
                case .failure(let error):
                    self?.errorMessage = error.localizedDescription
                    print("❌ Ошибка загрузки профиля: \(error.localizedDescription)")
                }
            }
        }
    }
    
    func editProfile() {
        logger.business("User initiated profile edit")
        print("Show edit profile sheet")
    }
    
    func changePassword() {
        logger.business("User initiated password change")
        print("Show change password")
    }
    
    func manageTwoFactor() {
        logger.business("User accessed two-factor authentication settings")
        print("Manage 2FA")
    }
    
    func showActiveSessions() {
        logger.business("User accessed active sessions view")
        print("Show active sessions")
    }
    
    func deleteAccount() {
        logger.fatal("CRITICAL: User initiated account deletion process!")
        print("Show delete account confirmation")
    }
    
    // MARK: - Subscription End Date Parsing
    
    // ✅ ИСПРАВЛЕНИЕ BUILD 91+: Статические форматтеры для предотвращения рекурсии
    private static let isoFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        return formatter
    }()
    
    private static let dotFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "dd.MM.yyyy"
        formatter.locale = Locale(identifier: "ru_RU")
        return formatter
    }()
    
    private static let dashFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        formatter.locale = Locale(identifier: "ru_RU")
        return formatter
    }()
    
    private static let standardFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        formatter.locale = Locale(identifier: "ru_RU")
        return formatter
    }()
    
    /**
     * Парсинг даты окончания подписки из строки
     * Поддерживает различные форматы: ISO8601, "dd.MM.yyyy", "yyyy-MM-dd"
     */
    private func parseSubscriptionEndDate(_ dateString: String) -> Date? {
        // Пробуем ISO8601 формат
        if let date = Self.isoFormatter.date(from: dateString) {
            return date
        }
        
        // Пробуем формат "dd.MM.yyyy" (например, "31.12.2025")
        if let date = Self.dotFormatter.date(from: dateString) {
            return date
        }
        
        // Пробуем формат "yyyy-MM-dd"
        if let date = Self.dashFormatter.date(from: dateString) {
            return date
        }
        
        // Пробуем стандартный формат
        if let date = Self.standardFormatter.date(from: dateString) {
            return date
        }
        
        print("⚠️ Не удалось распарсить дату окончания подписки: \(dateString)")
        return nil
    }

    // MARK: - User Name Caching

    /// Сохраняет имя пользователя в кеш для быстрого доступа из детского интерфейса
    private func saveUserNameToCache(_ name: String) {
        logger.business("Saving user name to cache: \(name)")
        UserDefaults.standard.set(name, forKey: "user_display_name")
        UserDefaults.standard.set(name, forKey: "user_profile_name") // Дублируем для совместимости
        UserDefaults.standard.synchronize()

        print("✅ User name cached for child interface: \(name)")
    }
}



