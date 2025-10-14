import Foundation
import SwiftUI

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
        // Для разработки (локальный сервер)
        return "http://localhost:8000/api"
        #else
        // Для production (реальный сервер)
        return "https://api.aladdin.family/api"
        #endif
    }()
    
    // MARK: - Auth
    
    /**
     * Токен авторизации (если есть)
     */
    static var authToken: String? {
        get {
            UserDefaults.standard.string(forKey: "authToken")
        }
        set {
            UserDefaults.standard.set(newValue, forKey: "authToken")
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
     * В России IAP ограничен, поэтому используем СБП/SberPay
     */
    static var useAlternativePayments: Bool {
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

