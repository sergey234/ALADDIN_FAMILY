import Foundation
import Security

/**
 * ⚙️ App Config
 * Конфигурация приложения
 * Настройки для подключения к Python backend
 */

struct AppConfig {
    
    // MARK: - API Configuration
    
    /// Окружения API
    enum Environment {
        case development
        case staging
        case production
        
        var baseURL: String {
            switch self {
            case .development:
                return "https://aladdin-ai.ru/api"  // Используем payment_service
            case .staging:
                return "https://aladdin-ai.ru/api"  // Используем payment_service
            case .production:
                return "https://aladdin-ai.ru/api"  // Используем payment_service
            }
        }
    }
    
    /// Текущее окружение
    static let currentEnvironment: Environment = {
        #if DEBUG
        return .development
        #else
        return .production
        #endif
    }()
    
    /**
     * URL вашего Python backend
     * ВАЖНО: Измените на свой реальный URL!
     */
    static let apiBaseURL: String = currentEnvironment.baseURL
    
    /// Использовать Mock API вместо реального (только для DEBUG)
    static let useMockAPI: Bool = false
    
    /// Режим съёмки скриншотов (принудительно включает русский язык)
    static let screenshotMode: Bool = false
    
    /// Показывать отладочные оверлеи
    static let showDebugOverlays: Bool = false
    
    // ✅ ИСПРАВЛЕНИЕ #5: Метод для безопасной проверки доступности API
    static func isAPIURLValid() -> Bool {
        guard !apiBaseURL.isEmpty else { return false }
        // Если localhost в DEBUG режиме - всегда возвращаем true (будет ошибка при запросе, но не краш)
        #if DEBUG
        return true
        #else
        return apiBaseURL.hasPrefix("https://")
        #endif
    }
    
    // MARK: - Auth
    
    /**
     * Токен авторизации (если есть)
     * Читается из Keychain для безопасности с fallback на UserDefaults
     */
    static var authToken: String? {
        get {
            // Сначала пробуем Keychain (основное хранилище)
            if let keychainToken = KeychainManager.shared.load(String.self, forKey: .authToken) {
                return keychainToken
            }
            // Fallback на UserDefaults для обратной совместимости
            return UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.authToken)
        }
        set {
            if let token = newValue {
                // Сохраняем в Keychain
                KeychainManager.shared.save(token, forKey: .authToken)
                // И в UserDefaults для обратной совместимости
                UserDefaults.standard.set(token, forKey: AppConfig.UserDefaultsKeys.authToken)
            } else {
                // Удаляем из обоих мест
                KeychainManager.shared.delete(forKey: .authToken)
                UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
            }
        }
    }
    
    // MARK: - App Info
    
    static let appVersion = "1.0.0"
    static let buildNumber = "1"
    static let bundleIdentifier = "family.aladdin.ios"
    static let appName = "ALADDIN"
    static let appDisplayName = "ALADDIN - AI Защита Семьи"
    
    // MARK: - API Endpoints
    
    enum Endpoint {
        // Network Protection
        static let networkProtectionStatus = "/network-protection/status"
        static let networkProtectionConnect = "/network-protection/connect"
        static let networkProtectionDisconnect = "/network-protection/disconnect"
        static let networkProtectionServers = "/network-protection/servers"
        static let networkProtectionSettings = "/network-protection/settings"
        
        // Family
        static let createFamily = "/family/create"
        static let joinFamily = "/family/join"
        static let recoverFamily = "/family/recover"
        static let familyMembers = "/family/members"
        static let addFamilyMember = "/family/add"
        static let removeFamilyMember = "/family/remove"
        static let memberProfile = "/family/member"
        static let familyStats = "/family/stats"
        
        // Family Chat
        static let familyChatMessages = "/family/chat/messages"
        static let familyChatSend = "/family/chat/send"
        
        // Components (42 components API)
        static let componentStatus = "/components/status"
        static let componentStatusBatch = "/components/status/batch"  // 🚀 Batch endpoint для оптимизации
        static let componentEnable = "/components/enable"
        static let componentDisable = "/components/disable"
        static let componentConfiguration = "/components/config"
        
        // Analytics
        static let analytics = "/analytics"
        static let threats = "/analytics/threats"
        static let topThreats = "/analytics/top-threats"
        
        // Component Reports
        // Driving Reports
        static let drivingReports = "/reports/driving"
        static let drivingStats = "/reports/driving/stats"
        static let drivingExport = "/reports/driving/export"
        
        // Dark Web Monitoring
        static let darkWebLeaks = "/reports/dark-web/leaks"
        static let darkWebStats = "/reports/dark-web/stats"
        static let darkWebScans = "/reports/dark-web/scans"
        static let darkWebResolve = "/reports/dark-web/resolve"
        static let darkWebScanStart = "/reports/dark-web/scan/start"
        static let darkWebScanSecure = "/reports/dark-web/scan/secure"
        static let darkWebScanFast = "/reports/dark-web/scan/fast"
        
        // Identity Theft
        static let identityTheftAttempts = "/reports/identity-theft/attempts"
        static let identityTheftStats = "/reports/identity-theft/stats"
        static let identityTheftAllow = "/reports/identity-theft/allow"
        static let identityTheftBlock = "/reports/identity-theft/block"
        static let identityTheftWhitelist = "/reports/identity-theft/whitelist"
        
        // Privacy Reports
        static let locationStats = "/reports/privacy/location/stats"
        static let locationRequests = "/reports/privacy/location/requests"
        static let locationAllow = "/reports/privacy/location/allow"
        static let locationBlock = "/reports/privacy/location/block"
        static let locationUpdateAccuracy = "/reports/privacy/location/update-accuracy"
        static let dataCleanupStats = "/reports/privacy/cleanup/stats"
        static let dataCleanupRecords = "/reports/privacy/cleanup/records"
        static let dataCleanupStart = "/reports/privacy/cleanup/start"
        static let antiTrackerStats = "/reports/privacy/tracker/stats"
        static let topTrackers = "/reports/privacy/tracker/top"
        static let trackerWhitelist = "/reports/privacy/tracker/whitelist"
        
        // AI Categories
        static let aiCategoriesStats = "/reports/ai-categories/stats"
        static let aiCategoryReports = "/reports/ai-categories/reports"
        static let aiCategoriesAllow = "/reports/ai-categories/allow"
        static let aiCategoriesBlock = "/reports/ai-categories/block"
        
        // AI Assistant
        static let aiChat = "/ai/chat"
        static let aiSendMessage = "/ai/message"
        
        // Parental Control
        static let parentalControl = "/parental/control"
        static let applyBlocking = "/api/v1/parental-control/blocking"
        static let applyRules = "/api/v1/parental-control/rules"
        static let getAccessRequests = "/api/v1/parental-control/access-requests"
        static let handleAccessRequest = "/api/v1/parental-control/access-requests"
        static let getStats = "/api/v1/parental-control/stats"
        static let updateLimits = "/parental/limits"
        static let blockDevice = "/parental/block"
        
        // User
        static let profile = "/user/profile"
        static let updateProfile = "/user/update"
        static let changePassword = "/user/password"
        static let deleteAccount = "/user/delete"
        static let twoFactorStatus = "/user/2fa/status"
        static let twoFactorUpdate = "/user/2fa/update"
        
        // Notifications
        static let notifications = "/notifications"
        static let markRead = "/notifications/read"
        
        // Devices
        static let devices = "/devices"
        static let deviceRegister = "/devices/register-ios"
        static let deviceDetail = "/devices" // /devices/{deviceId}
        static let deviceSettings = "/devices" // /devices/{deviceId}/settings
        
        // Auth
        static let login = "/auth/login"
        static let logout = "/auth/logout"
        static let register = "/auth/register"
        
        // Subscription
        static let tariffs = "/subscription/tariffs"
        static let subscribe = "/subscription/subscribe"
        static let cancelSubscription = "/subscription/cancel"
        static let activateSubscription = "/subscription/activate"
        static let activationVerify = "/subscription/activation/verify"
        static let activationActivate = "/subscription/activation/activate"
        
        // Protection
        static let protectionSettings = "/protection/settings"
        static let protectionStatus = "/protection/status"
        static let threatScenarios = "/protection/threat-scenarios"
        static let protectionEnable = "/protection/enable"
        static let protectionDisable = "/protection/disable"
        static let protectionStats = "/protection/stats"
        static let protectionSync = "/protection/sync"
        
        // Referral
        static let referralCode = "/referral/code"
        static let referralStats = "/referral/stats"
        static let referralHistory = "/referral/history"
        static let referralRewards = "/referral/rewards"

        // Crash Detection
        static let crashDetectionSetup = "/api/crash-detection/setup"
        static let crashDetectionAlert = "/api/crash-detection/alert"
        static let crashDetectionStart = "/api/crash-detection/start"
        static let crashDetectionStop = "/api/crash-detection/stop"
        static let crashDetectionData = "/api/crash-detection/data"
        static let crashDetectionStatus = "/api/crash-detection/status"

        // Location & Privacy
        static let locationBubble = "/reports/privacy/location/bubble"
        static let locationSend = "/reports/privacy/location/send"
        static let geofences = "/api/v1/parental-control/location/geofences"
        static let geofenceTrack = "/api/v1/parental-control/location/track"

        // Driving Reports
        static let drivingStart = "/reports/driving/start"
        static let drivingEnd = "/reports/driving/end"
    }
    
    // MARK: - Feature Flags
    
    static let isNetworkProtectionEnabled = true
    static let isAIEnabled = true
    static let isParentalControlEnabled = true
    static let isAnalyticsEnabled = true
    
    // MARK: - Payment Configuration
    
    /**
     * Проверка региона пользователя
     * Если Россия → используем QR оплату
     * Если не Россия → используем IAP (App Store)
     */
    static var isRussianRegion: Bool {
        return Locale.current.regionCode == "RU"
    }
    
    /**
     * Включить альтернативные способы оплаты (QR-коды)
     * В России IAP недоступен → используем QR оплату
     * Для остальных стран → используем IAP (App Store)
     * 
     * ✅ ИСПРАВЛЕНО: Использовать QR оплату ТОЛЬКО для России
     * Для соответствия Guideline 3.1.1 IAP должен быть доступен для всех стран кроме России
     */
    static var useAlternativePayments: Bool {
        // Использовать QR оплату ТОЛЬКО для России
        return isRussianRegion
    }
    
    /**
     * Использовать IAP (In-App Purchase через App Store)
     */
    static var useIAP: Bool {
        return !isRussianRegion
    }
    
    /**
     * API ключ для бэкенда (замените на свой!)
     */
    static let apiKey = "YOUR_SECURE_API_KEY"
    
    /**
     * Базовый URL для backward compatibility
     */
    static var baseURL: String {
        return apiBaseURL
    }
    
    // MARK: - Debug
    
    static let isDebugMode: Bool = {
        #if DEBUG
        return true
        #else
        return false
        #endif
    }()
    
    static let logLevel: LogLevel = isDebugMode ? .verbose : .error
    
    enum LogLevel {
        case verbose, info, warning, error, none
    }
}

// MARK: - Constants Extension

extension AppConfig {
    
    // MARK: - UserDefaults Keys
    
    /// Ключи для UserDefaults
    struct UserDefaultsKeys {
        static let authToken = "authToken"
        static let familyId = "family_id"
        static let consentAccepted = "consent_accepted"
        static let consentDate = "consent_date"
        static let consentVersion = "consent_version"
        static let appLanguage = "appLanguage"
        static let hasCompletedOnboarding = "hasCompletedOnboarding"
    }
    
    // MARK: - Network Configuration
    
    /// Настройки сети
    struct Network {
        static let requestTimeout: TimeInterval = 30.0
        static let resourceTimeout: TimeInterval = 60.0
        static let waitsForConnectivity = true
    }
    
    // MARK: - Consent & Privacy
    
    /// Настройки согласий и приватности
    struct Consent {
        static let currentVersion = "2.0"
    }
    
    // MARK: - Support Contact Information
    
    /// Контактная информация для поддержки
    struct Support {
        /// Телефон поддержки (отображаемый формат)
        static let supportPhone = "+7 (927) 005-15-77"
        
        /// URL для Telegram бота поддержки
        /// ✅ Бот уже настроен и работает: https://t.me/aladdin_support_bot
        /// При нажатии на кнопку "Чат с поддержкой" откроется Telegram с этим ботом
        static let supportTelegramURL = "https://t.me/aladdin_support_bot"
        
        /// ✅ ИЗМЕНЕНИЕ: Email заменён на AI ассистента
        /// Вместо email пользователи могут отправлять пожелания и рекомендации через AI ассистента в приложении
        /// AI ассистент открывается через NavigationManager.navigateTo(.aiAssistant)
    }
    
    /// Телефон поддержки (для удобства)
    static var supportPhone: String {
        return Support.supportPhone
    }
    
    /// URL Telegram поддержки (для удобства)
    static var supportTelegramURL: String {
        return Support.supportTelegramURL
    }
    
    /// URL сайта для подписки
    static let subscriptionWebsiteURL = "https://aladdin-ai.ru"
    
    /// URL центра помощи поддержки
    static let supportHelpCenterURL = "https://aladdin-ai.ru/help-faq.html"
    
    /// URL FAQ поддержки
    static let supportFAQURL = "https://aladdin-ai.ru/help-faq.html"
    
    /// ✅ DEPRECATED: Email больше не используется
    /// Используйте AI ассистента вместо email для отправки пожеланий и рекомендаций
    @available(*, deprecated, message: "Используйте AI ассистента вместо email")
    static var supportEmail: String {
        return "support@aladdin.family" // Оставлено для обратной совместимости
    }
    
}

