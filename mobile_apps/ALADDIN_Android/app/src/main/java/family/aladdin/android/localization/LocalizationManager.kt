package family.aladdin.android.localization

import android.content.Context
import android.content.res.Configuration
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import java.util.Locale

/**
 * 🌍 Localization Manager
 * Управление локализацией приложения
 * Поддержка RU + EN
 */

object LocalizationManager {
    
    // MARK: - Supported Languages
    
    enum class Language(val code: String, val displayName: String, val flag: String) {
        RUSSIAN("ru", "Русский", "🇷🇺"),
        ENGLISH("en", "English", "🇬🇧");
        
        companion object {
            fun fromCode(code: String): Language {
                return values().firstOrNull { it.code == code } ?: RUSSIAN
            }
        }
    }
    
    // MARK: - Current Language
    
    private const val LANGUAGE_KEY = "app_language"
    
    /**
     * Получить текущий язык
     */
    fun getCurrentLanguage(context: Context): Language {
        val prefs = context.getSharedPreferences("aladdin_prefs", Context.MODE_PRIVATE)
        val savedLanguage = prefs.getString(LANGUAGE_KEY, null)
        
        return if (savedLanguage != null) {
            Language.fromCode(savedLanguage)
        } else {
            // Определить язык системы
            val systemLanguage = Locale.getDefault().language
            Language.fromCode(systemLanguage)
        }
    }
    
    /**
     * Сменить язык приложения
     */
    fun changeLanguage(context: Context, language: Language) {
        // Сохранить в SharedPreferences
        val prefs = context.getSharedPreferences("aladdin_prefs", Context.MODE_PRIVATE)
        prefs.edit().putString(LANGUAGE_KEY, language.code).apply()
        
        // Применить язык
        applyLanguage(context, language)
        
        println("✅ Language changed to: ${language.displayName}")
    }
    
    /**
     * Применить язык к Context
     */
    fun applyLanguage(context: Context, language: Language): Context {
        val locale = Locale(language.code)
        Locale.setDefault(locale)
        
        val config = Configuration(context.resources.configuration)
        config.setLocale(locale)
        
        return context.createConfigurationContext(config)
    }
    
    /**
     * Получить локализованную строку
     */
    fun getString(context: Context, stringRes: Int): String {
        return context.getString(stringRes)
    }
    
    /**
     * Получить локализованную строку с параметрами
     */
    fun getString(context: Context, stringRes: Int, vararg formatArgs: Any): String {
        return context.getString(stringRes, *formatArgs)
    }
}

// MARK: - Composable Helper

/**
 * Composable helper для получения строки
 */
@Composable
fun localizedString(stringRes: Int): String {
    val context = LocalContext.current
    return context.getString(stringRes)
}

/**
 * Composable helper для получения строки с параметрами
 */
@Composable
fun localizedString(stringRes: Int, vararg formatArgs: Any): String {
    val context = LocalContext.current
    return context.getString(stringRes, *formatArgs)
}



