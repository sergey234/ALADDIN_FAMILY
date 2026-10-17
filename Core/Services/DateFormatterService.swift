import Foundation

/**
 * 📅 Date Formatter Service
 * Централизованный сервис для форматирования дат
 * Предотвращает рекурсию через использование статических форматтеров и Calendar
 * 
 * ✅ BUILD 100: Рефакторинг для предотвращения рекурсии
 * - Все форматтеры статические
 * - Используется статический Calendar вместо Calendar.current
 * - Thread-safe операции на main thread
 */
@MainActor
class DateFormatterService {
    
    // MARK: - Singleton
    
    static let shared = DateFormatterService()
    
    // MARK: - Private Initialization
    
    private init() {
        // Singleton - приватный инициализатор
    }
    
    // MARK: - Dynamic Locale-aware Calendar
    
    /// ✅ BUILD 100: Calendar с локалью, зависящей от текущего языка приложения
    /// Это обеспечивает правильное отображение дат (январь/January, мая/May и т.д.)
    private static var currentLocale: Locale {
        locale(for: currentLanguage)
    }

    private static var currentLanguage: LocalizationManager.Language {
        if let raw = UserDefaults.standard.string(forKey: AppConfig.UserDefaultsKeys.appLanguage),
           let language = LocalizationManager.Language(rawValue: raw) {
            return language
        }
        return LocalizationManager.shared.currentLanguage
    }
    
    private static var calendar: Calendar {
        var cal = Calendar(identifier: .gregorian)
        cal.locale = currentLocale
        return cal
    }

    private static func locale(for language: LocalizationManager.Language) -> Locale {
        switch language {
        case .russian:
            return Locale(identifier: "ru_RU")
        case .english:
            return Locale(identifier: "en_US")
        case .chinese:
            return Locale(identifier: "zh_Hans")
        case .arabic:
            return Locale(identifier: "ar")
        }
    }
    
    // MARK: - ISO8601 Formatters
    
    /// Статический ISO8601DateFormatter для парсинга дат с fractional seconds
    private static let isoFormatter: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()
    
    /// Статический ISO8601DateFormatter без fractional seconds (fallback)
    private static let isoFormatterFallback: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        return formatter
    }()
    
    // MARK: - Display Formatters (Locale-aware)
    
    /// DateFormatter для отображения дат (medium style)
    /// Локаль определяется динамически на основе текущего языка приложения
    private static var displayFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        formatter.locale = currentLocale
        formatter.calendar = calendar
        return formatter
    }
    
    /// DateFormatter для отображения дат и времени
    private static var dateTimeFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        formatter.locale = currentLocale
        formatter.calendar = calendar
        return formatter
    }
    
    /// DateFormatter для отображения только времени
    private static var timeFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateStyle = .none
        formatter.timeStyle = .short
        formatter.locale = currentLocale
        formatter.calendar = calendar
        return formatter
    }
    
    /// DateFormatter для полного отображения даты и времени
    private static var fullFormatter: DateFormatter {
        let formatter = DateFormatter()
        formatter.dateStyle = .full
        formatter.timeStyle = .full
        formatter.locale = currentLocale
        formatter.calendar = calendar
        return formatter
    }
    
    // MARK: - Public Methods
    
    /// Парсит ISO8601 строку в Date
    /// Поддерживает форматы с fractional seconds и без
    func parseISO8601(_ isoString: String) -> Date? {
        // Пробуем сначала с fractional seconds
        if let date = Self.isoFormatter.date(from: isoString) {
            return date
        }
        // Fallback на формат без fractional seconds
        return Self.isoFormatterFallback.date(from: isoString)
    }
    
    /// Форматирует Date в строку для отображения (medium style)
    /// Локаль определяется динамически - даты показываются на языке приложения (январь/January)
    func formatDisplayDate(_ date: Date) -> String {
        return Self.displayFormatter.string(from: date)
    }

    /// Форматирует Date в строку для отображения на явно выбранном языке приложения.
    func formatDisplayDate(_ date: Date, language: LocalizationManager.Language) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        formatter.locale = Self.locale(for: language)
        var cal = Calendar(identifier: .gregorian)
        cal.locale = formatter.locale
        formatter.calendar = cal
        return formatter.string(from: date)
    }
    
    /// Форматирует Date в строку с датой и временем
    func formatDateTime(_ date: Date) -> String {
        return Self.dateTimeFormatter.string(from: date)
    }
    
    /// Форматирует Date в строку только с временем
    func formatTime(_ date: Date) -> String {
        return Self.timeFormatter.string(from: date)
    }
    
    /// Форматирует Date в полную строку с датой и временем
    func formatFull(_ date: Date) -> String {
        return Self.fullFormatter.string(from: date)
    }
    
    /// Форматирует ISO8601 строку в строку для отображения
    /// ✅ BUILD 100: Полный цикл парсинга и форматирования на main thread
    func formatExpirationDate(from isoString: String) -> String? {
        guard let date = parseISO8601(isoString) else {
            return nil
        }
        return formatDisplayDate(date)
    }

    /// Форматирует ISO8601 строку на явно выбранном языке приложения.
    func formatExpirationDate(from isoString: String, language: LocalizationManager.Language) -> String? {
        guard let date = parseISO8601(isoString) else {
            return nil
        }
        return formatDisplayDate(date, language: language)
    }
    
    // MARK: - Calendar Helpers
    
    /// Проверяет, является ли дата сегодняшней
    /// ✅ BUILD 100: Использует статический Calendar вместо Calendar.current
    func isDateInToday(_ date: Date) -> Bool {
        return Self.calendar.isDateInToday(date)
    }
    
    /// Проверяет, является ли дата вчерашней
    func isDateInYesterday(_ date: Date) -> Bool {
        return Self.calendar.isDateInYesterday(date)
    }
    
    /// Добавляет дни к дате
    func date(byAdding days: Int, to date: Date) -> Date? {
        return Self.calendar.date(byAdding: .day, value: days, to: date)
    }
    
    /// Получает компонент даты (месяц, день, год и т.д.)
    func component(_ component: Calendar.Component, from date: Date) -> Int {
        return Self.calendar.component(component, from: date)
    }
}
