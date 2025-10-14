package family.aladdin.android.config

import android.content.Context
import android.content.SharedPreferences

/**
 * ⚙️ App Config
 * Конфигурация Android приложения
 * Настройки для подключения к Python backend
 */

object AppConfig {
    
    // ═══════════════════════════════════════════════════════════════
    // Debug (должно быть в начале!)
    // ═══════════════════════════════════════════════════════════════
    
    const val isDebugMode = true  // Change to false for production
    
    // ═══════════════════════════════════════════════════════════════
    // API Configuration
    // ═══════════════════════════════════════════════════════════════
    
    /**
     * URL вашего Python backend
     * ВАЖНО: Измените на свой реальный URL!
     */
    val apiBaseURL: String = if (isDebugMode) {
        // Для разработки (локальный сервер)
        "http://10.0.2.2:8000/api"  // 10.0.2.2 для Android Emulator → localhost
    } else {
        // Для production (реальный сервер)
        "https://api.aladdin.family/api"
    }
    
    // ═══════════════════════════════════════════════════════════════
    // Auth (SharedPreferences)
    // ═══════════════════════════════════════════════════════════════
    
    private var sharedPreferences: SharedPreferences? = null
    
    fun init(context: Context) {
        sharedPreferences = context.getSharedPreferences("aladdin_prefs", Context.MODE_PRIVATE)
    }
    
    var authToken: String?
        get() = sharedPreferences?.getString("authToken", null)
        set(value) {
            sharedPreferences?.edit()?.putString("authToken", value)?.apply()
        }
    
    // ═══════════════════════════════════════════════════════════════
    // App Info
    // ═══════════════════════════════════════════════════════════════
    
    const val appVersion = "1.0.0"
    const val buildNumber = "1"
    const val packageName = "family.aladdin.android"
    const val appName = "ALADDIN"
    const val appDisplayName = "ALADDIN - AI Защита Семьи"
    
    // ═══════════════════════════════════════════════════════════════
    // Feature Flags
    // ═══════════════════════════════════════════════════════════════
    
    const val isVPNEnabled = true
    const val isAIEnabled = true
    const val isParentalControlEnabled = true
    const val isAnalyticsEnabled = true
    
    // ═══════════════════════════════════════════════════════════════
    // Payment Configuration (QR оплата)
    // ═══════════════════════════════════════════════════════════════
    
    /**
     * Проверка региона пользователя
     * Если Россия → используем QR оплату
     * Если не Россия → используем IAP (Google Play)
     */
    val isRussianRegion: Boolean
        get() = java.util.Locale.getDefault().country == "RU"
    
    /**
     * Включить альтернативные способы оплаты (QR-коды)
     * В России Google Play Billing ограничен, поэтому используем СБП/SberPay
     */
    val useAlternativePayments: Boolean
        get() = isRussianRegion
    
    /**
     * Использовать IAP (In-App Purchase через Google Play)
     */
    val useIAP: Boolean
        get() = !isRussianRegion
    
    /**
     * API ключ для бэкенда (замените на свой!)
     */
    const val apiKey = "YOUR_SECURE_API_KEY"
    
    /**
     * Базовый URL для backward compatibility
     */
    val baseURL: String
        get() = apiBaseURL
    
    // Log Level
    enum class LogLevel {
        VERBOSE, INFO, WARNING, ERROR, NONE
    }
    
    val logLevel: LogLevel = if (isDebugMode) LogLevel.VERBOSE else LogLevel.ERROR
    
    // ═══════════════════════════════════════════════════════════════
    // Timeouts
    // ═══════════════════════════════════════════════════════════════
    
    const val CONNECTION_TIMEOUT = 30L // seconds
    const val READ_TIMEOUT = 30L // seconds
    const val WRITE_TIMEOUT = 30L // seconds
}

