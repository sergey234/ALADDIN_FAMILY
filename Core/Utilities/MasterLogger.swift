import Foundation
import SwiftUI
import os.log
import UIKit

/**
 * 🎯 Master Logger - Единая система логирования для всего приложения
 *
 * Объединяет:
 * - SettingsDiagnosticsLogger (основное логирование)
 * - VisualLogger (отображение на экране)
 * - NetworkLogger (сетевые запросы)
 * - MetricsService (производительность)
 *
 * Уровни: TRACE, DEBUG, INFO, WARN, ERROR, FATAL
 * Вывод: print() + os_log() + VisualLogView + файл
 */
class MasterLogger {

    // MARK: - Singleton
    static let shared = MasterLogger()

    // MARK: - Properties
    private let settingsLogger = SettingsDiagnosticsLogger.shared
    private let visualLogger = VisualLogger.shared

    /// Флаг включения визуального логирования
    @AppStorage("enable_visual_logging") private var enableVisualLogging = false

    /// Флаг включения логирования в консоль
    private let enableConsoleLogging = true

    /// Максимальный уровень логирования (ниже этого уровня не логируется)
    private var maxLogLevel: LogLevel = .trace

    // MARK: - Initialization
    private init() {
        // Настройка уровней логирования
        #if DEBUG
        maxLogLevel = .trace  // В DEBUG все уровни
        enableVisualLogging = true  // В DEBUG включаем визуальное логирование
        #else
        maxLogLevel = .info   // В RELEASE только INFO и выше
        #endif

        // 🚨 КРИТИЧНОЕ ИСПРАВЛЕНИЕ: ПОЛНОСТЬЮ УБРАНО ЛОГИРОВАНИЕ ИЗ INIT
        // Даже закомментированное логирование может вызывать проблемы!
    }

    // MARK: - Log Levels
    enum LogLevel: String, Codable {
        case trace = "TRACE"
        case debug = "DEBUG"
        case info = "INFO"
        case warn = "WARN"
        case error = "ERROR"
        case fatal = "FATAL"

        var priority: Int {
            switch self {
            case .trace: return 0
            case .debug: return 1
            case .info: return 2
            case .warn: return 3
            case .error: return 4
            case .fatal: return 5
            }
        }

        var emoji: String {
            switch self {
            case .trace: return "🔍"
            case .debug: return "🔧"
            case .info: return "ℹ️"
            case .warn: return "⚠️"
            case .error: return "❌"
            case .fatal: return "🚨"
            }
        }

        var osLogType: OSLogType {
            switch self {
            case .trace, .debug: return .debug
            case .info: return .info
            case .warn: return .default
            case .error: return .error
            case .fatal: return .fault
            }
        }

        var settingsDiagnosticsLevel: SettingsDiagnosticsLogger.LogLevel {
            switch self {
            case .trace, .debug: return .info
            case .info: return .info
            case .warn: return .warning
            case .error: return .error
            case .fatal: return .critical
            }
        }
    }

    // MARK: - Categories
    enum LogCategory: String {
        case system = "SYSTEM"
        case ui = "UI"
        case network = "NETWORK"
        case business = "BUSINESS"
        case security = "SECURITY"
        case performance = "PERFORMANCE"
        case error = "ERROR"
    }

    // MARK: - Public Methods

    /// Основной метод логирования
    func log(
        _ level: LogLevel,
        category: LogCategory = .system,
        message: String,
        function: String = #function,
        file: String = #file,
        line: Int = #line
    ) {
        // Проверка уровня логирования
        guard level.priority >= maxLogLevel.priority else { return }

        let fileName = (file as NSString).lastPathComponent
        let fullMessage = "[\(category.rawValue)] \(message)"

        // 1. SettingsDiagnosticsLogger (основное логирование)
        switch level {
        case .trace, .debug, .info:
            settingsLogger.logFunction(function, message: fullMessage, section: category.rawValue)
        case .warn:
            settingsLogger.logFunction(function, message: "WARNING: \(fullMessage)", section: category.rawValue)
        case .error:
            settingsLogger.logError(function, message: fullMessage, section: category.rawValue)
        case .fatal:
            settingsLogger.logCritical(function, message: fullMessage, section: category.rawValue)
        }

        // 2. Visual Logger (если включено)
        if enableVisualLogging {
            visualLogger.log(
                fullMessage,
                level: VisualLogger.LogLevel(rawValue: level.emoji) ?? .info,
                file: fileName,
                line: line
            )
        }

        // 3. Console logging (всегда для DEBUG)
        #if DEBUG
        if enableConsoleLogging {
            print("\(level.emoji) [\(level.rawValue)] [\(category.rawValue)] [\(fileName):\(line)] \(message)")
        }
        #endif
    }

    // MARK: - Convenience Methods

    /// Логирование UI действий
    func ui(_ message: String, function: String = #function, file: String = #file, line: Int = #line) {
        log(.info, category: .ui, message: message, function: function, file: file, line: line)
    }

    /// Логирование сетевых запросов
    func network(_ message: String, function: String = #function, file: String = #file, line: Int = #line) {
        log(.info, category: .network, message: message, function: function, file: file, line: line)
    }

    /// Логирование бизнес-логики
    func business(_ message: String, function: String = #function, file: String = #file, line: Int = #line) {
        log(.info, category: .business, message: message, function: function, file: file, line: line)
    }

    /// Логирование безопасности
    func security(_ message: String, function: String = #function, file: String = #file, line: Int = #line) {
        log(.info, category: .business, message: "🔒 \(message)", function: function, file: file, line: line)
    }

    /// Логирование производительности
    func performance(_ message: String, function: String = #function, file: String = #file, line: Int = #line) {
        log(.info, category: .performance, message: message, function: function, file: file, line: line)
    }

    /// Логирование предупреждений
    func warn(_ message: String, function: String = #function, file: String = #file, line: Int = #line) {
        log(.warn, category: .performance, message: message, function: function, file: file, line: line)
    }

    /// Логирование ошибок
    func error(_ message: String, error: Error? = nil, function: String = #function, file: String = #file, line: Int = #line) {
        let fullMessage = error.map { "\(message): \($0.localizedDescription)" } ?? message
        log(.error, category: .error, message: fullMessage, function: function, file: file, line: line)
    }

    /// Логирование фатальных ошибок
    func fatal(_ message: String, function: String = #function, file: String = #file, line: Int = #line) {
        log(.fatal, category: .error, message: message, function: function, file: file, line: line)
    }

    // MARK: - Network Integration

    /// Логирование HTTP запросов
    func logRequest(_ request: URLRequest, function: String = #function, file: String = #file, line: Int = #line) {
        var headers = request.allHTTPHeaderFields ?? [:]
        headers = LogSanitizer.sanitizeHeaders(headers)  // ✅ ПОЛНАЯ ЗАЩИТА ЗАГОЛОВКОВ

        let url = LogSanitizer.sanitizeURL(request.url?.absoluteString ?? "-")  // ✅ ЗАЩИТА URL
        let message = "➡️ \(request.httpMethod ?? "GET") \(url) headers=\(headers)"
        network(message, function: function, file: file, line: line)
    }

    /// Логирование HTTP ответов
    func logResponse(_ response: URLResponse?, data: Data?, function: String = #function, file: String = #file, line: Int = #line) {
        if let http = response as? HTTPURLResponse {
            let url = LogSanitizer.sanitizeURL(http.url?.absoluteString ?? "-")
            var message = "⬅️ status=\(http.statusCode) url=\(url)"

            // Санитизация тела ответа
            if let data = data, let jsonString = String(data: data, encoding: .utf8) {
                let sanitizedJSON = LogSanitizer.sanitizeJSON(jsonString)
                // Ограничиваем размер лога (первые 500 символов)
                let truncatedJSON = sanitizedJSON.count > 500 ? sanitizedJSON.prefix(500) + "..." : sanitizedJSON
                message += " body=\(truncatedJSON)"
            }

            network(message, function: function, file: file, line: line)
        }
    }

    // MARK: - Export & Management

    /// Экспорт всех логов
    func exportLogs() -> String {
        return settingsLogger.exportLogs()
    }

    /// Получить все логи для анализа (включая визуальные)
    func getAllLogs() -> String {
        var allLogs = settingsLogger.exportLogs()

        // Добавляем визуальные логи если они включены
        if enableVisualLogging {
            let visualLogs = visualLogger.getLogs()
            if !visualLogs.isEmpty {
                allLogs += "\n\n=== VISUAL LOGS ===\n" + visualLogs
            }
        }

        return allLogs
    }

    /// Экспорт логов в файл
    func exportLogsToFile() -> URL? {
        return settingsLogger.exportLogsToFile()
    }

    /// Очистить все логи
    func clearLogs() {
        settingsLogger.clearLogs()
        visualLogger.clear()
    }

    /// Включить/выключить визуальное логирование
    func setVisualLogging(enabled: Bool) {
        enableVisualLogging = enabled
        ui("Visual logging \(enabled ? "enabled" : "disabled")")
    }

    /// Получить VisualLogView для отображения
    var visualLogView: some View {
        VisualLogView()
    }

    /// Получить все логи из Visual Logger в текстовом формате
    func getVisualLogsText() -> String {
        return visualLogger.logs.map { entry in
            "[\(entry.formattedTime)] [\(entry.level.rawValue)] \(entry.message)"
        }.joined(separator: "\n")
    }
}

// MARK: - Convenience Extensions

extension MasterLogger {
    /// Логирование нажатий кнопок
    func buttonTap(_ buttonName: String, screen: String, function: String = #function, file: String = #file, line: Int = #line) {
        ui("🔘 Button tapped: \(buttonName) on \(screen)", function: function, file: file, line: line)
    }

    /// Логирование переключения тумблеров
    func toggleChanged(_ toggleName: String, newValue: Bool, screen: String, function: String = #function, file: String = #file, line: Int = #line) {
        ui("🔄 Toggle changed: \(toggleName) = \(newValue) on \(screen)", function: function, file: file, line: line)
    }

    /// Логирование навигации
    func navigation(from: String, to: String, function: String = #function, file: String = #file, line: Int = #line) {
        ui("🧭 Navigation: \(from) → \(to)", function: function, file: file, line: line)
    }

    /// Логирование загрузки экранов
    func screenLoad(_ screenName: String, function: String = #function, file: String = #file, line: Int = #line) {
        ui("📱 Screen loaded: \(screenName)", function: function, file: file, line: line)
    }
}