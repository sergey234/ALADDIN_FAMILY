import Foundation
import Security
import SwiftUI

/**
 * 🌍 Localization Manager
 * Управление локализацией приложения
 * Поддержка RU + EN
 */

class LocalizationManager: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var currentLanguage: Language = .russian
    
    // MARK: - Supported Languages
    
    enum Language: String, CaseIterable {
        case russian = "ru"
        case english = "en"
        case chinese = "zh-Hans"
        case arabic = "ar"
        
        var displayName: String {
            switch self {
            case .russian: return "Русский"
            case .english: return "English"
            case .chinese: return "中文"
            case .arabic: return "العربية"
            }
        }
        
        var flag: String {
            switch self {
            case .russian: return "🇷🇺"
            case .english: return "🇬🇧"
            case .chinese: return "🇨🇳"
            case .arabic: return "🇦🇪"
            }
        }
        
        var isRTL: Bool {
            switch self {
            case .arabic: return true
            default: return false
            }
        }
    }
    
    // MARK: - Init
    
    init() {
        // Определить язык системы
        // TODO: В будущем заменить на Keychain для безопасности
        if let systemLanguage = Locale.current.languageCode,
           let language = Language(rawValue: systemLanguage) {
            currentLanguage = language
        } else {
            currentLanguage = .russian // По умолчанию русский
        }
    }
    
    // MARK: - Change Language
    
    /**
     * Сменить язык приложения
     */
    func changeLanguage(to language: Language) {
        currentLanguage = language
        // Сохраняем язык
        // TODO: В будущем заменить на Keychain для безопасности
        UserDefaults.standard.set(language.rawValue, forKey: AppConfig.UserDefaultsKeys.appLanguage)
        
        // В production здесь нужно перезапустить UI
        print("✅ Language changed to: \(language.displayName)")
    }
    
    // MARK: - Get Localized String
    
    /**
     * Получить локализованную строку
     */
    func localized(_ key: String) -> String {
        NSLocalizedString(key, comment: "")
    }
    
    /**
     * Получить локализованную строку с параметрами
     */
    func localized(_ key: String, _ arguments: CVarArg...) -> String {
        String(format: NSLocalizedString(key, comment: ""), arguments: arguments)
    }
}

// MARK: - String Extension

extension String {
    /**
     * Удобный helper для локализации
     * Использование: "main.title".localized
     */
    var localized: String {
        NSLocalizedString(self, comment: "")
    }
    
    /**
     * Локализация с параметрами
     * Использование: "family.subtitle".localized(4)
     */
    func localized(_ arguments: CVarArg...) -> String {
        String(format: NSLocalizedString(self, comment: ""), arguments: arguments)
    }
}

// MARK: - LocalizedStringKey Extension

extension LocalizedStringKey {
    /**
     * Создать из строки
     */
    static func key(_ string: String) -> LocalizedStringKey {
        LocalizedStringKey(string)
    }
}



