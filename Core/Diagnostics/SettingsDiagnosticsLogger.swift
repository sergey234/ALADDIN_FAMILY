import Foundation
import os

/// 🔍 Settings Diagnostics Logger
/// Централизованное логирование для диагностики краша Settings Screen
class SettingsDiagnosticsLogger {
    
    // MARK: - Singleton
    
    static let shared = SettingsDiagnosticsLogger()
    
    // MARK: - Properties
    
    /// Флаг включения логирования (verbose ring buffer — DEBUG; warn+ в RELEASE)
    #if DEBUG
    static let ENABLE_LOGS = true
    #else
    static let ENABLE_LOGS = true
    #endif

    private func shouldPersist(level: LogLevel) -> Bool {
        #if DEBUG
        return true
        #else
        return level == .warning || level == .error || level == .critical
        #endif
    }

    /// Subsystem для фильтра в Console.app (совпадает с bundle приложения).
    static var logSubsystem: String {
        Bundle.main.bundleIdentifier ?? "ALADDIN"
    }

    /// Unified logging (DEBUG + Release): безопасные строки после `removeEmoji`.
    private let unifiedLog = Logger(
        subsystem: SettingsDiagnosticsLogger.logSubsystem,
        category: "SETTINGS_DIAG"
    )
    
    /// Массив логов для экспорта (ограничен размером)
    private var logs: [LogEntry] = []
    private let maxLogs = 1000
    
    /// Очередь для thread-safe доступа
    private let logQueue = DispatchQueue(
        label: "com.aladdin.settings.logger",
        qos: .utility
    )

    /// 🛡️ Флаг защиты от рекурсии - предотвращает бесконечный цикл
    private var isLoggingInProgress = false

    // MARK: - Models
    
    struct LogEntry: Codable {
        let timestamp: Date
        let level: LogLevel
        let section: String?
        let function: String
        let message: String
        let thread: String
        let stackTrace: [String]?
        
        var formattedMessage: String {
            let time = DateFormatter.logFormatter.string(from: timestamp)
            let levelIcon = level.icon
            let sectionStr = section.map { "[\($0)] " } ?? ""
            return "\(time) \(levelIcon) \(sectionStr)\(function): \(message) [\(thread)]"
        }
    }
    
    enum LogLevel: String, Codable {
        case info = "INFO"
        case warning = "WARNING"
        case error = "ERROR"
        case critical = "CRITICAL"
        
        var icon: String {
            switch self {
            case .info: return "🔍"
            case .warning: return "⚠️"
            case .error: return "❌"
            case .critical: return "🔴"
            }
        }
        
    }
    
    // MARK: - Initialization
    
    private init() {
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Убрано логирование из init() - оно может вызывать рекурсию
        // Логирование будет происходить при первом вызове log()
    }
    
    // MARK: - Public Methods
    
    /// Логирование секции
    func logSection(_ section: String, function: String, message: String = "НАЧАЛО") {
        log(level: .info, section: section, function: function, message: message)
    }
    
    /// Логирование функции
    func logFunction(_ function: String, message: String, section: String? = nil) {
        log(level: .info, section: section, function: function, message: message)
    }
    
    /// Логирование ошибки
    func logError(_ function: String, message: String, section: String? = nil, error: Error? = nil) {
        let fullMessage = error.map { "\(message): \($0.localizedDescription)" } ?? message
        log(level: .error, section: section, function: function, message: fullMessage)
    }
    
    /// Логирование критичной ошибки
    func logCritical(_ function: String, message: String, section: String? = nil) {
        log(level: .critical, section: section, function: function, message: message)
    }
    
    /// Логирование предупреждения
    func logWarning(_ function: String, message: String, section: String? = nil) {
        log(level: .warning, section: section, function: function, message: message)
    }
    
    /// Логирование API вызова
    func logAPI(_ function: String, message: String, section: String? = nil) {
        log(level: .info, section: section, function: function, message: "API: \(message)")
    }
    
    // MARK: - String Sanitization
    
    /// Удаляет эмодзи из строки для безопасного использования в os_log.
    /// Весь ASCII (включая цифры в URL, HTTP status, UUID) всегда сохраняем: на части SDK `isEmoji`
    /// давал ложные срабатывания и в Console исчезали цифры (`status=`, `FAM_…` без hex).
    private func removeEmoji(_ string: String) -> String {
        string.unicodeScalars
            .filter { scalar in
                let v = scalar.value
                if v <= 0x7F { return true }
                if scalar.properties.isEmoji || scalar.properties.isEmojiPresentation { return false }
                if v == 0xFE0F { return false }
                return true
            }
            .reduce("") { $0 + String($1) }
    }
    
    // MARK: - Private Methods
    
    private func log(
        level: LogLevel,
        section: String?,
        function: String,
        message: String,
        includeStackTrace: Bool = false
    ) {
        guard Self.ENABLE_LOGS else { return }

        // 🛡️ ЗАЩИТА ОТ РЕКУРСИИ - если уже логируем, выходим
        guard !isLoggingInProgress else { return }
        isLoggingInProgress = true
        defer { isLoggingInProgress = false }

        let thread = Thread.isMainThread ? "MAIN" : "BACKGROUND"
        let stackTrace: [String]? = includeStackTrace ? Array(Thread.callStackSymbols.prefix(5)) : nil
        
        let entry = LogEntry(
            timestamp: Date(),
            level: level,
            section: section,
            function: function,
            message: message,
            thread: thread,
            stackTrace: stackTrace
        )

        // 🔒 ОГРАНИЧИТЬ ДЛИНУ СООБЩЕНИЯ ДЛЯ БЕЗОПАСНОСТИ
        let safeMessage = entry.formattedMessage.count > 500 ?
            String(entry.formattedMessage.prefix(500)) + "..." : entry.formattedMessage

        // DEBUG: print для Xcode. RELEASE: только os_log (без дубля print).
        #if DEBUG
        print("🔍 SETTINGS_DIAG: \(safeMessage)")
        #endif

        guard shouldPersist(level: level) else { return }

        // 1. Системный лог (Console.app): `Logger` + строка без эмодзи.
        let messageForOSLog = removeEmoji(safeMessage)
        switch level {
        case .info:
            unifiedLog.info("\(messageForOSLog, privacy: .public)")
        case .warning:
            unifiedLog.warning("\(messageForOSLog, privacy: .public)")
        case .error:
            unifiedLog.error("\(messageForOSLog, privacy: .public)")
        case .critical:
            unifiedLog.critical("\(messageForOSLog, privacy: .public)")
        }

        // 2. Массив (для экспорта) - асинхронно
        logQueue.async { [weak self] in
            guard let self = self else { return }
            
            self.logs.append(entry)
            
            // Ограничение размера
            if self.logs.count > self.maxLogs {
                self.logs.removeFirst(self.logs.count - self.maxLogs)
            }
        }
    }
    
    // MARK: - Export
    
    /// Экспорт всех логов
    func exportLogs() -> String {
        return logQueue.sync {
            logs.map { $0.formattedMessage }.joined(separator: "\n")
        }
    }
    
    /// Экспорт логов в файл
    func exportLogsToFile() -> URL? {
        let logsString = exportLogs()
        let fileName = "settings_logs_\(Date().timeIntervalSince1970).txt"
        
        guard let documentsDirectory = FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        ).first else {
            return nil
        }
        
        let fileURL = documentsDirectory.appendingPathComponent(fileName)
        
        do {
            try logsString.write(to: fileURL, atomically: true, encoding: .utf8)
            return fileURL
        } catch {
            logError("SettingsDiagnosticsLogger", message: "Ошибка экспорта логов", error: error)
            return nil
        }
    }
    
    /// Очистить логи
    func clearLogs() {
        logQueue.async { [weak self] in
            self?.logs.removeAll()
        }
    }
}

// MARK: - DateFormatter Extension

extension DateFormatter {
    static let logFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss.SSS"
        return formatter
    }()
}
