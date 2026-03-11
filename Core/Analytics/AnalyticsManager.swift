import Foundation
// import Firebase // Uncomment when Firebase SDK added

/**
 * 📊 Analytics Manager
 * Управление аналитикой пользователей
 * Firebase Analytics интеграция
 */

@MainActor
class AnalyticsManager {
    
    // MARK: - Recursion Protection
    private static let recursionKey = "AnalyticsManager.isTracking"
    
    // MARK: - Singleton
    
    static let shared = AnalyticsManager()
    
    private let lock = NSLock()
    
    private init() {
        print("📊 [AnalyticsManager] Initializing")
        // Firebase будет инициализирован в AppDelegate
    }
    
    // MARK: - Screen Tracking
    
    /**
     * Отслеживать просмотр экрана
     */
    func trackScreen(_ screenName: String, screenClass: String? = nil) {
        // 🛡️ BUILD 110: Защита от рекурсии
        let threadDict = Thread.current.threadDictionary
        if threadDict[Self.recursionKey] != nil { return }
        threadDict[Self.recursionKey] = true
        defer { threadDict.removeObject(forKey: Self.recursionKey) }
        
        lock.lock()
        defer { lock.unlock() }
        
        print("📊 [Analytics] Screen view: \(screenName)")
    }
    
    // MARK: - Event Tracking
    
    /**
     * Отслеживать событие
     * ✅ BUILD 102: Убраны parameters ?? [:] и parameters?.description для предотвращения создания Dictionary в background thread
     */
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        // 🛡️ BUILD 110: Защита от рекурсии
        let threadDict = Thread.current.threadDictionary
        if threadDict[Self.recursionKey] != nil { return }
        threadDict[Self.recursionKey] = true
        defer { threadDict.removeObject(forKey: Self.recursionKey) }
        
        // 🛡️ BUILD 108: Максимальная изоляция
        // Используем lock только для критических операций
        lock.lock()
        defer { lock.unlock() }
        
        #if DEBUG
        // Печатаем только имя события, чтобы избежать тяжелого описания словаря в Lock
        print("📊 [AnalyticsManager] Event: \(eventName)")
        #endif
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



