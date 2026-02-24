import Foundation
import UIKit

// Master Logger for profile manager logging
private let logger = MasterLogger.shared

/// 👤 User Profile Manager
/// Singleton класс для управления профилем пользователя
/// Предоставляет быстрый доступ к данным пользователя из кеша
class UserProfileManager {
    static let shared = UserProfileManager()

    private let apiService = APIService.shared
    private let userDefaults = UserDefaults.standard
    private let keychainManager = KeychainManager.shared

    private let displayNameKey = "user_display_name"
    private let profileNameKey = "user_profile_name"
    private let emailKey = "user_email"
    private let lastUpdateKey = "user_profile_last_update"

    private init() {
        // Загружаем профиль при инициализации
        loadProfileInBackground()
        
        // ✅ УВЕДОМЛЕНИЕ: Подписываемся на уведомление о успешной авторизации
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleUserDidLogin),
            name: NSNotification.Name("UserDidLogin"),
            object: nil
        )
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
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
    /// ✅ ИСПРАВЛЕНО: Использует гибридный подход - сначала getUserProfile, потом syncUserProfile
    func loadProfile(completion: ((Bool) -> Void)? = nil) {
        logger.business("Loading user profile data")
        // ✅ ПРОВЕРКА ТОКЕНА: Если нет токена, не загружаем профиль
        guard keychainManager.isDataAvailable(forKey: .authToken) else {
            print("⚠️ UserProfileManager: Нет токена - пропускаем загрузку профиля")
            completion?(false)
            return
        }
        
        // ✅ ПОПЫТКА 1: Стандартный endpoint /api/user/profile
        apiService.getUserProfile { [weak self] result in
            guard let self = self else { return }

            DispatchQueue.main.async {
                switch result {
                case .success(let profile):
                    // ✅ Успех - используем стандартный endpoint
                    self.saveProfileToCache(profile)
                    print("✅ User profile loaded via /api/user/profile: \(profile.name)")
                    completion?(true)

                case .failure(let error):
                    // ✅ ПОПЫТКА 2: Fallback на syncUserProfile
                    print("⚠️ UserProfileManager: getUserProfile failed: \(error.localizedDescription)")
                    print("🔄 UserProfileManager: Попытка 2 - используем syncUserProfile")
                    
                    // Получаем userId из UserDefaults
                    guard let userId = UserDefaults.standard.string(forKey: "your_member_id") else {
                        print("❌ UserProfileManager: your_member_id не найден в UserDefaults")
                        completion?(false)
                        return
                    }
                    
                    // Получаем deviceId
                    let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? "unknown"
                    
                    // Используем syncUserProfile
                    self.apiService.syncUserProfile(userId: userId, deviceId: deviceId) { [weak self] syncResult in
                        guard let self = self else { return }
                        
                        DispatchQueue.main.async {
                            switch syncResult {
                            case .success(let syncResponse):
                                // ✅ Конвертируем SyncUserProfileResponse в UserProfile
                                let profile = UserProfile(
                                    id: syncResponse.profile.userId,
                                    name: syncResponse.profile.name,
                                    email: syncResponse.profile.email ?? "",
                                    phone: syncResponse.profile.phone,
                                    registrationDate: syncResponse.profile.registrationDate,
                                    subscriptionType: "free", // Дефолтное значение
                                    subscriptionEndDate: nil,
                                    threatsBlocked: 0, // Дефолтное значение
                                    familyMembers: 0, // Дефолтное значение
                                    devices: 1 // Дефолтное значение
                                )
                                self.saveProfileToCache(profile)
                                print("✅ User profile loaded via syncUserProfile: \(profile.name)")
                                completion?(true)
                                
                            case .failure(let syncError):
                                print("❌ UserProfileManager: syncUserProfile failed: \(syncError.localizedDescription)")
                                completion?(false)
                            }
                        }
                    }
                }
            }
        }
    }

    /// Очистить кеш профиля
    func clearProfileCache() {
        logger.business("Clearing user profile cache")
        userDefaults.removeObject(forKey: displayNameKey)
        userDefaults.removeObject(forKey: profileNameKey)
        userDefaults.removeObject(forKey: emailKey)
        userDefaults.removeObject(forKey: lastUpdateKey)
        userDefaults.synchronize()
        print("🗑️ User profile cache cleared")
    }

    // MARK: - Private Methods

    private func loadProfileInBackground() {
        logger.business("Loading user profile in background")
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
        logger.business("Saving user profile to cache: \(profile.name)")
        userDefaults.set(profile.name, forKey: displayNameKey)
        userDefaults.set(profile.name, forKey: profileNameKey) // Для совместимости
        userDefaults.set(profile.email, forKey: emailKey)
        userDefaults.set(Date().timeIntervalSince1970, forKey: lastUpdateKey)
        userDefaults.synchronize()
    }
    
    // ✅ ОБРАБОТЧИК: Перезагружаем профиль после успешной авторизации
    @objc private func handleUserDidLogin() {
        logger.business("User login detected - refreshing profile data")
        print("🔄 UserProfileManager: Получено уведомление о авторизации - перезагружаем профиль")
        DispatchQueue.global(qos: .background).async { [weak self] in
            self?.loadProfile { success in
                if success {
                    print("✅ UserProfileManager: Профиль успешно перезагружен после авторизации")
                } else {
                    print("⚠️ UserProfileManager: Не удалось перезагрузить профиль после авторизации")
                }
            }
        }
    }
}