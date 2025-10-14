package family.aladdin.android.analytics

import android.content.Context
import android.os.Bundle
import family.aladdin.android.config.AppConfig
// import com.google.firebase.analytics.FirebaseAnalytics // Uncomment when Firebase SDK added
// import com.google.firebase.analytics.ktx.analytics
// import com.google.firebase.ktx.Firebase

/**
 * 📊 Analytics Manager
 * Управление аналитикой пользователей
 * Firebase Analytics интеграция
 */

class AnalyticsManager(private val context: Context) {
    
    companion object {
        private var instance: AnalyticsManager? = null
        
        fun initialize(context: Context) {
            instance = AnalyticsManager(context.applicationContext)
        }
        
        fun getInstance(): AnalyticsManager {
            return instance ?: throw IllegalStateException("AnalyticsManager not initialized")
        }
        
        fun logEvent(eventName: String, parameters: Map<String, Any>? = null) {
            instance?.trackEvent(eventName, parameters)
        }
    }
    
    // MARK: - Properties
    
    // private val firebaseAnalytics: FirebaseAnalytics = Firebase.analytics
    
    // MARK: - Screen Tracking
    
    /**
     * Отслеживать просмотр экрана
     */
    fun trackScreen(screenName: String, screenClass: String? = null) {
        if (AppConfig.isDebugMode) {
            println("📊 Screen: $screenName${screenClass?.let { " ($it)" } ?: ""}")
        }
        
        // В production:
        // val bundle = Bundle().apply {
        //     putString(FirebaseAnalytics.Param.SCREEN_NAME, screenName)
        //     putString(FirebaseAnalytics.Param.SCREEN_CLASS, screenClass ?: screenName)
        // }
        // firebaseAnalytics.logEvent(FirebaseAnalytics.Event.SCREEN_VIEW, bundle)
    }
    
    // MARK: - Event Tracking
    
    /**
     * Отслеживать событие
     */
    fun trackEvent(eventName: String, parameters: Map<String, Any>? = null) {
        if (AppConfig.isDebugMode) {
            println("📊 Event: $eventName, params: $parameters")
        }
        
        // В production:
        // val bundle = Bundle().apply {
        //     parameters?.forEach { (key, value) ->
        //         when (value) {
        //             is String -> putString(key, value)
        //             is Int -> putInt(key, value)
        //             is Long -> putLong(key, value)
        //             is Double -> putDouble(key, value)
        //             is Boolean -> putBoolean(key, value)
        //         }
        //     }
        // }
        // firebaseAnalytics.logEvent(eventName, bundle)
    }
    
    // MARK: - User Properties
    
    /**
     * Установить свойство пользователя
     */
    fun setUserProperty(name: String, value: String?) {
        if (AppConfig.isDebugMode) {
            println("📊 User Property: $name = $value")
        }
        
        // В production:
        // firebaseAnalytics.setUserProperty(name, value)
    }
    
    /**
     * Установить User ID
     */
    fun setUserID(userID: String?) {
        if (AppConfig.isDebugMode) {
            println("📊 User ID: $userID")
        }
        
        // В production:
        // firebaseAnalytics.setUserId(userID)
    }
    
    // MARK: - Predefined Events
    
    /**
     * Отследить вход пользователя
     */
    fun trackLogin(method: String) {
        trackEvent("login", mapOf("method" to method))
    }
    
    /**
     * Отследить регистрацию
     */
    fun trackSignUp(method: String) {
        trackEvent("sign_up", mapOf("method" to method))
    }
    
    /**
     * Отследить подписку
     */
    fun trackPurchase(subscriptionID: String, price: Double, currency: String = "RUB") {
        trackEvent("purchase", mapOf(
            "subscription_id" to subscriptionID,
            "value" to price,
            "currency" to currency
        ))
    }
    
    /**
     * Отследить VPN подключение
     */
    fun trackVPNConnect(server: String) {
        trackEvent("vpn_connect", mapOf("server" to server))
    }
    
    /**
     * Отследить VPN отключение
     */
    fun trackVPNDisconnect() {
        trackEvent("vpn_disconnect")
    }
    
    /**
     * Отследить добавление члена семьи
     */
    fun trackAddFamilyMember(role: String) {
        trackEvent("add_family_member", mapOf("role" to role))
    }
    
    /**
     * Отследить блокировку угрозы
     */
    fun trackThreatBlocked(type: String) {
        trackEvent("threat_blocked", mapOf("threat_type" to type))
    }
    
    /**
     * Отследить использование AI помощника
     */
    fun trackAIAssistantMessage() {
        trackEvent("ai_assistant_message")
    }
    
    /**
     * Отследить использование родительского контроля
     */
    fun trackParentalControlUsed(action: String) {
        trackEvent("parental_control", mapOf("action" to action))
    }
    
    /**
     * Отследить добавление устройства
     */
    fun trackAddDevice(deviceType: String) {
        trackEvent("add_device", mapOf("device_type" to deviceType))
    }
    
    /**
     * Отследить реферальное приглашение
     */
    fun trackReferralShare(method: String) {
        trackEvent("referral_share", mapOf("method" to method))
    }
    
    /**
     * Отследить сообщение в семейном чате
     */
    fun trackFamilyChatMessage() {
        trackEvent("family_chat_message")
    }
    
    // MARK: - Conversion Tracking
    
    /**
     * Отследить начало бесплатного триала
     */
    fun trackTrialStarted(subscriptionID: String) {
        trackEvent("trial_started", mapOf("subscription_id" to subscriptionID))
    }
    
    /**
     * Отследить конверсию из триала в подписку
     */
    fun trackTrialConverted(subscriptionID: String) {
        trackEvent("trial_converted", mapOf("subscription_id" to subscriptionID))
    }
    
    /**
     * Отследить отмену подписки
     */
    fun trackSubscriptionCancelled(subscriptionID: String, reason: String?) {
        val params = mutableMapOf<String, Any>("subscription_id" to subscriptionID)
        reason?.let { params["cancellation_reason"] = it }
        trackEvent("subscription_cancelled", params)
    }
    
    // MARK: - Session Tracking
    
    /**
     * Отследить запуск приложения
     */
    fun trackAppLaunched() {
        trackEvent("app_launched")
    }
    
    /**
     * Отследить уход в фон
     */
    fun trackAppBackgrounded() {
        trackEvent("app_backgrounded")
    }
    
    /**
     * Отследить возврат из фона
     */
    fun trackAppForegrounded() {
        trackEvent("app_foregrounded")
    }
}

// MARK: - Analytics Events Constants

object AnalyticsEvent {
    const val APP_LAUNCHED = "app_launched"
    const val APP_BACKGROUNDED = "app_backgrounded"
    const val APP_FOREGROUNDED = "app_foregrounded"
    const val SCREEN_VIEW = "screen_view"
    const val BUTTON_TAPPED = "button_tapped"
    const val ERROR_OCCURRED = "error_occurred"
}

// MARK: - Analytics Parameters Constants

object AnalyticsParameter {
    const val SCREEN_NAME = "screen_name"
    const val BUTTON_NAME = "button_name"
    const val ERROR_MESSAGE = "error_message"
    const val USER_ID = "user_id"
    const val SUBSCRIPTION_TYPE = "subscription_type"
}



