import Foundation
// import Firebase // Uncomment when Firebase SDK added

// Master Logger for analytics logging
private let logger = MasterLogger.shared

/**
 * 📊 Analytics Manager
 * Управление аналитикой пользователей
 * Firebase Analytics интеграция
 */

class AnalyticsManager {
    
    // MARK: - Singleton
    
    static let shared = AnalyticsManager()
    
    private init() {
        logger.business("Initializing AnalyticsManager")
        // Firebase будет инициализирован в AppDelegate
    }
    
    // MARK: - Screen Tracking
    
    /**
     * Отслеживать просмотр экрана
     */
    func trackScreen(_ screenName: String, screenClass: String? = nil) {
        logger.business("Analytics: Screen view - \(screenName)")
        #if DEBUG
        print("📊 Screen: \(screenName)")
        #endif
        
        // В production:
        // Analytics.logEvent(AnalyticsEventScreenView, parameters: [
        //     AnalyticsParameterScreenName: screenName,
        //     AnalyticsParameterScreenClass: screenClass ?? screenName
        // ])
    }
    
    // MARK: - Event Tracking
    
    /**
     * Отслеживать событие
     */
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        logger.business("Analytics: Event - \(eventName) with params: \(parameters?.description ?? "none")")
        #if DEBUG
        print("📊 Event: \(eventName), params: \(parameters ?? [:])")
        #endif
        
        // В production:
        // Analytics.logEvent(eventName, parameters: parameters)
    }
    
    // MARK: - User Properties
    
    /**
     * Установить свойство пользователя
     */
    func setUserProperty(_ value: String?, forName name: String) {
        #if DEBUG
        print("📊 User Property: \(name) = \(value ?? "nil")")
        #endif
        
        // В production:
        // Analytics.setUserProperty(value, forName: name)
    }
    
    /**
     * Установить User ID
     */
    func setUserID(_ userID: String?) {
        #if DEBUG
        print("📊 User ID: \(userID ?? "nil")")
        #endif
        
        // В production:
        // Analytics.setUserID(userID)
    }
    
    // MARK: - Predefined Events
    
    /**
     * Отследить вход пользователя
     */
    func trackLogin(method: String) {
        trackEvent("login", parameters: ["method": method])
    }
    
    /**
     * Отследить регистрацию
     */
    func trackSignUp(method: String) {
        trackEvent("sign_up", parameters: ["method": method])
    }
    
    /**
     * Отследить подписку
     */
    func trackPurchase(subscriptionID: String, price: Double, currency: String = "RUB") {
        trackEvent("purchase", parameters: [
            "subscription_id": subscriptionID,
            "value": price,
            "currency": currency
        ])
    }
    
    /**
     * Отследить Network Protection подключение
     */
    func trackNetworkProtectionConnect(server: String) {
        trackEvent("network_protection_connect", parameters: ["server": server])
    }
    
    /**
     * Отследить Network Protection отключение
     */
    func trackNetworkProtectionDisconnect() {
        trackEvent("network_protection_disconnect")
    }
    
    /**
     * Отследить добавление члена семьи
     */
    func trackAddFamilyMember(role: String) {
        trackEvent("add_family_member", parameters: ["role": role])
    }
    
    /**
     * Отследить блокировку угрозы
     */
    func trackThreatBlocked(type: String) {
        trackEvent("threat_blocked", parameters: ["threat_type": type])
    }
    
    /**
     * Отследить использование AI помощника
     */
    func trackAIAssistantMessage() {
        trackEvent("ai_assistant_message")
    }
    
    /**
     * Отследить использование родительского контроля
     */
    func trackParentalControlUsed(action: String) {
        trackEvent("parental_control", parameters: ["action": action])
    }
    
    /**
     * Отследить добавление устройства
     */
    func trackAddDevice(deviceType: String) {
        trackEvent("add_device", parameters: ["device_type": deviceType])
    }
    
    /**
     * Отследить реферальное приглашение
     */
    func trackReferralShare(method: String) {
        trackEvent("referral_share", parameters: ["method": method])
    }
    
    /**
     * Отследить сообщение в семейном чате
     */
    func trackFamilyChatMessage() {
        trackEvent("family_chat_message")
    }
    
    // MARK: - Conversion Tracking
    
    /**
     * Отследить начало бесплатного триала
     */
    func trackTrialStarted(subscriptionID: String) {
        trackEvent("trial_started", parameters: ["subscription_id": subscriptionID])
    }
    
    /**
     * Отследить конверсию из триала в подписку
     */
    func trackTrialConverted(subscriptionID: String) {
        trackEvent("trial_converted", parameters: ["subscription_id": subscriptionID])
    }
    
    /**
     * Отследить отмену подписки
     */
    func trackSubscriptionCancelled(subscriptionID: String, reason: String?) {
        var params: [String: Any] = ["subscription_id": subscriptionID]
        if let reason = reason {
            params["cancellation_reason"] = reason
        }
        trackEvent("subscription_cancelled", parameters: params)
    }
}

// MARK: - Analytics Events Constants

enum AnalyticsEvent {
    static let appLaunched = "app_launched"
    static let appBackgrounded = "app_backgrounded"
    static let appForegrounded = "app_foregrounded"
    static let screenView = "screen_view"
    static let buttonTapped = "button_tapped"
    static let errorOccurred = "error_occurred"
}

// MARK: - Analytics Parameters Constants

enum AnalyticsParameter {
    static let screenName = "screen_name"
    static let buttonName = "button_name"
    static let errorMessage = "error_message"
    static let userId = "user_id"
    static let subscriptionType = "subscription_type"
}



