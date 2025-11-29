import Foundation
import Security

/**
 * ⚙️ App Config
 * Конфигурация приложения
 * Настройки для подключения к Python backend
 */

struct AppConfig {
    
    // MARK: - API Configuration
    
    /**
     * URL вашего Python backend
     * ВАЖНО: Измените на свой реальный URL!
     */
    static let apiBaseURL: String = {
        #if DEBUG
        // ✅ ИСПРАВЛЕНИЕ: Используем реальный сервер для DEBUG тоже
        // localhost НЕ РАБОТАЕТ на реальном iPhone/iPad и в симуляторе если backend не локальный
        // Для локального тестирования измените на IP вашего Mac: "http://192.168.X.X:8080/api"
        return "https://api.aladdin.family/api"
        #else
        return "https://api.aladdin.family/api"
        #endif
    }()
    
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
     * TODO: В будущем заменить на Keychain для безопасности
     */
    static var authToken: String? {
        get {
            UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.authToken)
        }
        set {
            UserDefaults.standard.set(newValue, forKey: AppConfig.UserDefaultsKeys.authToken)
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
        // VPN
        static let vpnStatus = "/vpn/status"
        static let vpnConnect = "/vpn/connect"
        static let vpnDisconnect = "/vpn/disconnect"
        static let vpnServers = "/vpn/servers"
        
        // Family
        static let familyMembers = "/family/members"
        static let addFamilyMember = "/family/add"
        static let removeFamilyMember = "/family/remove"
        static let memberProfile = "/family/member"
        
        // Analytics
        static let analytics = "/analytics"
        static let threats = "/analytics/threats"
        static let topThreats = "/analytics/top-threats"
        
        // AI Assistant
        static let aiChat = "/ai/chat"
        static let aiSendMessage = "/ai/message"
        
        // Parental Control
        static let parentalControl = "/parental/control"
        static let updateLimits = "/parental/limits"
        static let blockDevice = "/parental/block"
        
        // User
        static let profile = "/user/profile"
        static let updateProfile = "/user/update"
        static let changePassword = "/user/password"
        
        // Notifications
        static let notifications = "/notifications"
        static let markRead = "/notifications/read"
        static let deviceRegister = "/devices/register-ios"
        
        // Auth
        static let login = "/auth/login"
        static let logout = "/auth/logout"
        static let register = "/auth/register"
        
        // Subscription
        static let tariffs = "/subscription/tariffs"
        static let subscribe = "/subscription/subscribe"
        static let cancelSubscription = "/subscription/cancel"
    }
    
    // MARK: - Feature Flags
    
    static let isVPNEnabled = true
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
     * В России IAP недоступен → ВСЕГДА используем QR оплату
     * 
     * ✅ ИЗМЕНЕНИЕ: Принудительно используем QR оплату всегда
     * Так как в России IAP недоступен, и симулятор может неправильно определить регион
     */
    static var useAlternativePayments: Bool {
        // ✅ ВСЕГДА true - используем только QR оплату (IAP в России недоступен)
        return true
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
    
}

