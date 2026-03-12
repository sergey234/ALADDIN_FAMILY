import Foundation

/// 👤 User Profile Manager
/// Singleton класс для управления профилем пользователя
/// Предоставляет быстрый доступ к данным пользователя из кеша
class UserProfileManager {
    static let shared = UserProfileManager()

    private let apiService = APIService.shared
    private let userDefaults = UserDefaults.standard

    private let displayNameKey = "user_display_name"
    private let profileNameKey = "user_profile_name"
    private let emailKey = "user_email"
    private let lastUpdateKey = "user_profile_last_update"

    private init() {
        // Загружаем профиль при инициализации
        loadProfileInBackground()
    }

    // MARK: - Public Methods

    /// Получить отображаемое имя пользователя
    var displayName: String {
        if let cachedName = userDefaults.string(forKey: displayNameKey),
           !cachedName.isEmpty {
            return cachedName
        }
        return NSLocalizedString("child_interface_default_name", comment: "Default user name")
    }

    /// Получить email пользователя
    var email: String? {
        return userDefaults.string(forKey: emailKey)
    }

    /// Проверить, загружен ли профиль
    var isProfileLoaded: Bool {
        return userDefaults.string(forKey: displayNameKey) != nil
    }

    /// Получить время последнего обновления профиля
    var lastUpdateTime: Date? {
        if let timestamp = userDefaults.double(forKey: lastUpdateKey) as Double?, timestamp > 0 {
            return Date(timeIntervalSince1970: timestamp)
        }
        return nil
    }

    /// Обновить профиль пользователя
    func updateProfile(displayName: String?, email: String?) {
        if let displayName = displayName {
            userDefaults.set(displayName, forKey: displayNameKey)
        }
        if let email = email {
            userDefaults.set(email, forKey: emailKey)
        }
        userDefaults.set(Date().timeIntervalSince1970, forKey: lastUpdateKey)
        // userDefaults.synchronize() - не требуется в современных версиях iOS
    }

    /// Очистить кеш профиля
    func clearProfile() {
        userDefaults.removeObject(forKey: displayNameKey)
        userDefaults.removeObject(forKey: profileNameKey)
        userDefaults.removeObject(forKey: emailKey)
        userDefaults.removeObject(forKey: lastUpdateKey)
        // userDefaults.synchronize() - не требуется в современных версиях iOS
    }

    // MARK: - Private Methods

    private func loadProfileInBackground() {
        // Загружаем профиль в фоне, если есть токен
        DispatchQueue.global(qos: .background).async { [weak self] in
            guard let self = self else { return }

            // Проверяем, есть ли токен для загрузки профиля
            if let token = AppConfig.authToken {
                // Загружаем профиль через API
                self.loadProfileFromAPI(token: token)
            }
        }
    }

    private func loadProfileFromAPI(token: String) {
        // Реализация загрузки профиля через API
        // Пока просто заглушка
        print("ℹ️ UserProfileManager: Profile loading not implemented yet")
    }
}