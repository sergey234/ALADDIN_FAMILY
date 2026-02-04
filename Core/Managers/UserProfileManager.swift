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

    /// Загрузить профиль из API и сохранить в кеш
    func loadProfile(completion: ((Bool) -> Void)? = nil) {
        apiService.getUserProfile { [weak self] result in
            guard let self = self else { return }

            DispatchQueue.main.async {
                switch result {
                case .success(let profile):
                    // Сохраняем данные в кеш
                    self.saveProfileToCache(profile)
                    print("✅ User profile loaded and cached: \(profile.name)")
                    completion?(true)

                case .failure(let error):
                    print("⚠️ Failed to load user profile: \(error.localizedDescription)")
                    completion?(false)
                }
            }
        }
    }

    /// Очистить кеш профиля
    func clearProfileCache() {
        userDefaults.removeObject(forKey: displayNameKey)
        userDefaults.removeObject(forKey: profileNameKey)
        userDefaults.removeObject(forKey: emailKey)
        userDefaults.removeObject(forKey: lastUpdateKey)
        userDefaults.synchronize()
        print("🗑️ User profile cache cleared")
    }

    // MARK: - Private Methods

    private func loadProfileInBackground() {
        // Загружаем профиль в фоне при инициализации
        // Если профиль старше 24 часов, обновляем
        if shouldRefreshProfile() {
            DispatchQueue.global(qos: .background).async { [weak self] in
                self?.loadProfile()
            }
        }
    }

    private func shouldRefreshProfile() -> Bool {
        guard let lastUpdate = lastUpdateTime else {
            return true // Нет данных, нужно загрузить
        }

        let twentyFourHours: TimeInterval = 24 * 60 * 60
        return Date().timeIntervalSince(lastUpdate) > twentyFourHours
    }

    private func saveProfileToCache(_ profile: UserProfile) {
        userDefaults.set(profile.name, forKey: displayNameKey)
        userDefaults.set(profile.name, forKey: profileNameKey) // Для совместимости
        userDefaults.set(profile.email, forKey: emailKey)
        userDefaults.set(Date().timeIntervalSince1970, forKey: lastUpdateKey)
        userDefaults.synchronize()
    }
}