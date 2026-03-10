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
    
    // MARK: - Static Calendar
    
    /// ✅ BUILD 100: Статический Calendar для предотвращения рекурсии через Calendar.current
    /// Calendar.current может читать из UserDefaults, что вызывает рекурсию через ICU библиотеку
    private static let calendar: Calendar = {
        var cal = Calendar(identifier: .gregorian)
        cal.locale = Locale(identifier: "ru_RU")
        return cal
    }()
    
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
    
    // MARK: - Display Formatters
    
    /// Статический DateFormatter для отображения дат (medium style)
    /// ✅ BUILD 100: Используем статический Calendar вместо Calendar.current
    private static let displayFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        formatter.locale = Locale(identifier: "ru_RU")
        // ✅ BUILD 100: Используем статический Calendar - обращаемся напрямую к calendar
        formatter.calendar = DateFormatterService.calendar
        return formatter
    }()
    
    /// Статический DateFormatter для отображения дат и времени
    private static let dateTimeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.calendar = DateFormatterService.calendar
        return formatter
    }()
    
    /// Статический DateFormatter для отображения только времени
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .none
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.calendar = DateFormatterService.calendar
        return formatter
    }()
    
    /// Статический DateFormatter для полного отображения даты и времени
    private static let fullFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .full
        formatter.timeStyle = .full
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.calendar = DateFormatterService.calendar
        return formatter
    }()
    
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
    /// ✅ BUILD 100: Выполняется на main thread для предотвращения рекурсии
    func formatDisplayDate(_ date: Date) -> String {
        return Self.displayFormatter.string(from: date)
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
