import Foundation

enum LocalizationManagerNamespace {}

class LocalizationManager {
    enum Language: String, CaseIterable {
        case russian = "ru"
        case english = "en"
        case chinese = "zh-Hans"
        case arabic = "ar"
    }
    var currentLanguage: Language
    var translations: [Language: [String: String]]
    init(language: Language = .russian, translations: [Language: [String: String]] = [:]) {
        self.currentLanguage = language
        self.translations = translations
    }
    func localized(_ key: String) -> String {
        translations[currentLanguage]?[key] ?? key
    }
    var locale: Locale {
        Locale(identifier: currentLanguage.rawValue)
    }
}
