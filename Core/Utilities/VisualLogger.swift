import SwiftUI
import Foundation
import UIKit

/**
 * 🔍 Visual Logger - для отображения логов на экране
 * Используется когда Xcode консоль недоступна
 */
class VisualLogger: ObservableObject {
    static let shared = VisualLogger()
    
    @Published var logs: [LogEntry] = []
    @Published var isVisible: Bool = true
    @Published var showErrorOnly: Bool = false
    @Published var showCopySuccess: Bool = false

    /// Публичный доступ к логам для отладки (можно просмотреть в Xcode debugger)
    public var allLogsText: String {
        logs.map { "[\($0.formattedTime)] [\($0.level.rawValue)] \($0.message)" }
            .joined(separator: "\n")
    }

    /// Получить все логи для анализа
    func getLogs() -> String {
        return allLogsText
    }
    
    private let maxLogs = 50
    private var logQueue = DispatchQueue(label: "com.aladdin.visualLogger", qos: .utility)
    
    private init() {
        // ✅ ИСПРАВЛЕНИЕ BUILD 93: Убрано чтение UserDefaults из init() - может вызывать рекурсию
        // Логи будут загружены асинхронно после инициализации через loadLogsAsync()
    }
    
    // ✅ НОВОЕ: Асинхронная загрузка логов после инициализации
    func loadLogsAsync() {
        Task { @MainActor in
            loadLogsFromUserDefaults()
            log("🚀 VisualLogger initialized with \(logs.count) restored logs", level: .info)
        }
    }

    // 💾 СОХРАНЕНИЕ ЛОГА В UserDefaults
    private func saveLogToUserDefaults(_ entry: LogEntry) {
        let key = "visual_logger_logs"
        let encoder = JSONEncoder()

        do {
            // Добавляем новый лог к существующим
            var savedLogs = getSavedLogs()
            savedLogs.append(entry)

            // Ограничиваем количество сохраненных логов
            if savedLogs.count > maxLogs {
                savedLogs.removeFirst(savedLogs.count - maxLogs)
            }

            let data = try encoder.encode(savedLogs)
            UserDefaults.standard.set(data, forKey: key)
            UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "visual_logger_last_save")
        } catch {
            print("❌ Failed to save log to UserDefaults: \(error)")
        }
    }

    // 🔄 ЗАГРУЗКА ЛОГОВ ИЗ UserDefaults
    private func loadLogsFromUserDefaults() {
        let savedLogs = getSavedLogs()

        // Добавляем сохраненные логи в текущий массив
        DispatchQueue.main.async {
            self.logs.append(contentsOf: savedLogs)
            if self.logs.count > self.maxLogs {
                self.logs = Array(self.logs.suffix(self.maxLogs))
            }
        }
    }

    // 📖 ПОЛУЧЕНИЕ СОХРАНЕННЫХ ЛОГОВ
    private func getSavedLogs() -> [LogEntry] {
        let key = "visual_logger_logs"
        guard let data = UserDefaults.standard.data(forKey: key) else { return [] }

        let decoder = JSONDecoder()
        do {
            return try decoder.decode([LogEntry].self, from: data)
        } catch {
            print("❌ Failed to load logs from UserDefaults: \(error)")
            return []
        }
    }

    // 🧹 ОЧИСТКА СОХРАНЕННЫХ ЛОГОВ
    func clearSavedLogs() {
        UserDefaults.standard.removeObject(forKey: "visual_logger_logs")
        UserDefaults.standard.removeObject(forKey: "visual_logger_last_save")
        UserDefaults.standard.synchronize()
    }
    
    struct LogEntry: Identifiable, Codable {
        let id: UUID
        let timestamp: Date
        let message: String
        let level: LogLevel
        let file: String
        let line: Int

        init(timestamp: Date, message: String, level: LogLevel, file: String, line: Int) {
            self.id = UUID()
            self.timestamp = timestamp
            self.message = message
            self.level = level
            self.file = file
            self.line = line
        }
        
        var formattedTime: String {
            let formatter = DateFormatter()
            formatter.dateFormat = "HH:mm:ss.SSS"
            return formatter.string(from: timestamp)
        }
    }
    
    enum LogLevel: String, Codable {
        case debug = "🔍"
        case info = "ℹ️"
        case success = "✅"
        case warning = "⚠️"
        case error = "❌"
        case critical = "🚨"
        
        var color: Color {
            switch self {
            case .debug: return .gray
            case .info: return .blue
            case .success: return .green
            case .warning: return .orange
            case .error: return .red
            case .critical: return .purple
            }
        }
    }
    
    /// 🛡️ Флаг защиты от рекурсии - предотвращает бесконечный цикл
    private var isLoggingInProgress = false
    
    func log(_ message: String, level: LogLevel = .info, file: String = #file, line: Int = #line) {
        // ✅ BUILD 113: Внутренняя асинхронность для разрыва петли рекурсии
        // Все операции с UserDefaults и массивом logs должны быть на Main Thread асинхронно
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            // 🛡️ ЗАЩИТА ОТ РЕКУРСИИ - если уже логируем, выходим
            guard !self.isLoggingInProgress else { return }
            self.isLoggingInProgress = true
            defer { self.isLoggingInProgress = false }
            
            let fileName = (file as NSString).lastPathComponent
            let entry = LogEntry(
                timestamp: Date(),
                message: message,
                level: level,
                file: fileName,
                line: line
            )
            
            self.logs.append(entry)
            if self.logs.count > self.maxLogs {
                self.logs.removeFirst()
            }
            
            // 💾 СОХРАНЯЕМ ЛОГИ В UserDefaults ДЛЯ ВОССТАНОВЛЕНИЯ ПОСЛЕ КРАША
            self.saveLogToUserDefaults(entry)

            // Также пишем в консоль для Xcode
            print("[\(entry.formattedTime)] [\(level.rawValue)] [\(fileName):\(line)] \(message)")
        }
    }
    
    func clear() {
        DispatchQueue.main.async {
            self.logs.removeAll()
        }
    }

    func copyLogsToClipboard() {
        let logText = logs.map { entry in
            "[\(entry.formattedTime)] [\(entry.level.rawValue)] \(entry.message)"
        }.joined(separator: "\n")

        DispatchQueue.main.async {
            UIPasteboard.general.string = logText
            self.showCopySuccess = true
            // Добавим временный лог о копировании
            self.log("📋 Logs copied to clipboard (\(self.logs.count) entries)", level: .success)

            // Скрываем подтверждение через 2 секунды
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                self.showCopySuccess = false
            }
        }
    }
}

// MARK: - Visual Logger View

struct VisualLogView: View {
    @ObservedObject var logger = VisualLogger.shared
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Header
            HStack {
                Text("📋 ЛОГИ")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                HStack(spacing: 4) {
                    if logger.showCopySuccess {
                        Text("✅ Скопировано!")
                            .font(.caption)
                            .foregroundColor(.green)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.white.opacity(0.2))
                            .cornerRadius(4)
                    }
                    Button(action: { logger.copyLogsToClipboard() }) {
                        Text("Копировать")
                            .font(.caption)
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.blue)
                            .cornerRadius(4)
                    }
                    Button(action: { logger.clear() }) {
                        Text("Очистить")
                            .font(.caption)
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.red)
                            .cornerRadius(4)
                    }
                }
                Button(action: { logger.isVisible.toggle() }) {
                    Image(systemName: logger.isVisible ? "eye.slash" : "eye")
                        .foregroundColor(.white)
                }
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.black.opacity(0.7))
            
            if logger.isVisible {
                ScrollView {
                    VStack(alignment: .leading, spacing: 2) {
                        ForEach(logger.logs.reversed()) { entry in
                            HStack(alignment: .top, spacing: 4) {
                                Text(entry.level.rawValue)
                                    .font(.caption)
                                Text("[\(entry.formattedTime)]")
                                    .font(.caption2)
                                    .foregroundColor(.gray)
                                Text(entry.message)
                                    .font(.caption)
                                    .foregroundColor(entry.level.color)
                                    .multilineTextAlignment(.leading)
                            }
                            .padding(.horizontal, 4)
                            .padding(.vertical, 2)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }
                .frame(maxHeight: 200)
                .background(Color.black.opacity(0.8))
            }
        }
        .font(.system(size: 10, design: .monospaced))
        .cornerRadius(8)
        .padding(8)
    }
}

