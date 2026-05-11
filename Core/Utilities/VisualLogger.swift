import SwiftUI
import Foundation
import UIKit

// MARK: - Machine-readable export pointer (agents / ML pipelines / Cursor)

/// Overwritten on each export. Stable path in app **Documents**: `aladdin_latest_export_manifest.json`
private struct AladdinLatestExportManifestV1: Codable {
    var schemaVersion: Int
    /// e.g. `visual_logs`, `startup_trace`
    var exportKind: String
    var primaryFileName: String
    /// Path on **this device** (simulator or phone). On Mac, pull via Xcode container or `simctl get_app_container`.
    var primaryFileAbsolutePath: String
    var byteCount: Int
    var createdAtISO8601: String
    /// Same moment as export, in device locale (for humans and matching the filename stamp when applicable).
    var humanReadableLocalTime: String
    /// Copy into an ML / agent chat so it knows exactly which file and session to open.
    var mlSearchPhrase: String
    var bundleIdentifier: String
    /// Natural-language hint for automated tools
    var analyzeNext: String
}

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
    @Published var lastExportPath: String? = nil
    /// Localized date+time of the last successful file export (visual logs or manifest refresh for Share Trace).
    @Published var lastExportHumanTime: String? = nil
    @Published var selectedLogLevelFilter: LogLevel? = nil

    /// Публичный доступ к логам для отладки (можно просмотреть в Xcode debugger)
    public var allLogsText: String {
        logs.map { "[\($0.formattedTime)] [\($0.level.rawValue)] [\($0.category)] \($0.message)" }
            .joined(separator: "\n")
    }

    /// Получить все логи для анализа
    func getLogs() -> String {
        return allLogsText
    }

    /// Direct clipboard copy with minimal side effects (for debugging)
    func forceCopyToClipboard() {
        let sourceLogs = logs.isEmpty ? getSavedLogs() : logs
        let logText = sourceLogs.isEmpty ? "VisualLogger: no logs available to copy." : sourceLogs.map { entry in
            "[\(entry.formattedTime)] [\(entry.level.rawValue)] [\(entry.category)] \(entry.message)"
        }.joined(separator: "\n")

        DispatchQueue.main.async {
            self.lastExportPath = nil
            self.lastExportHumanTime = nil
            UIPasteboard.general.string = logText
            let pasted = UIPasteboard.general.string ?? ""
            print("✅ Force copied \(sourceLogs.count) logs to clipboard (\(logText.count) chars, readback=\(pasted.count))")
            self.showCopySuccess = true

            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                self.showCopySuccess = false
            }
        }
    }
    
    private let maxLogs = 50
    private var logQueue = DispatchQueue(label: "com.aladdin.visualLogger", qos: .utility)
    
    // ✅ BUILD 113: Защита от повторных вызовов loadLogsAsync()
    // SwiftUI может вызывать onAppear несколько раз при пересоздании View
    private static var hasLoadedLogs = false
    private static let loadLogsLock = NSLock()
    
    /// Stable filename in **Documents** — external tools read this first to find the latest export.
    static let latestExportManifestFileName = "aladdin_latest_export_manifest.json"

    private init() {
        // ✅ ИСПРАВЛЕНИЕ BUILD 93: Убрано чтение UserDefaults из init() - может вызывать рекурсию
        // Логи будут загружены асинхронно после инициализации через loadLogsAsync()
    }

    /// File-safe stamp for export filenames: `2026-04-17T14-30-00-123` (device local timezone, ms suffix avoids collisions).
    static func exportFilenameTimestamp(for date: Date = Date()) -> String {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone.current
        f.dateFormat = "yyyy-MM-dd'T'HH-mm-ss-SSS"
        return f.string(from: date)
    }

    /// Medium date + time in current locale (UI and manifest).
    static func exportHumanReadableLocalTime(for date: Date = Date()) -> String {
        let f = DateFormatter()
        f.locale = .current
        f.timeZone = TimeZone.current
        f.dateStyle = .medium
        f.timeStyle = .medium
        return f.string(from: date)
    }

    /// Writes `Documents/aladdin_latest_export_manifest.json` so scripts/agents know **which file to analyze next**.
    func writeLatestExportManifestForAgents(exportKind: String, fileURL: URL, byteCount: Int, exportDate: Date = Date()) {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        let manifestURL = docs.appendingPathComponent(Self.latestExportManifestFileName)
        let bundleId = Bundle.main.bundleIdentifier ?? "unknown"
        let iso = ISO8601DateFormatter().string(from: exportDate)
        let human = Self.exportHumanReadableLocalTime(for: exportDate)
        let name = fileURL.lastPathComponent
        let mlSearchPhrase =
            "Диагностика ALADDIN (iOS), exportKind=\(exportKind): открой в контейнере приложения папку Documents и файл «\(name)» (или по абсолютному пути primaryFileAbsolutePath из манифеста). Это актуальный экспорт на момент \(human) (ISO8601: \(iso)). Сначала можно прочитать «\(Self.latestExportManifestFileName)» — там primaryFileName и путь."
        let analyzeNext =
            "ALADDIN diagnostic export kind=\(exportKind). UTF-8 file: primaryFileAbsolutePath. Same session: createdAtISO8601=\(iso), humanReadableLocalTime=\(human). Use mlSearchPhrase for LLM prompts. Manifest path: Documents/\(Self.latestExportManifestFileName)."
        let manifest = AladdinLatestExportManifestV1(
            schemaVersion: 1,
            exportKind: exportKind,
            primaryFileName: name,
            primaryFileAbsolutePath: fileURL.path,
            byteCount: byteCount,
            createdAtISO8601: iso,
            humanReadableLocalTime: human,
            mlSearchPhrase: mlSearchPhrase,
            bundleIdentifier: bundleId,
            analyzeNext: analyzeNext
        )
        do {
            let enc = JSONEncoder()
            enc.outputFormatting = [.prettyPrinted, .sortedKeys]
            let data = try enc.encode(manifest)
            try data.write(to: manifestURL, options: .atomic)
            print("🤖 ALADDIN_EXPORT_MANIFEST → \(manifestURL.path)")
            print("   primary: \(name) (\(byteCount) bytes) @ \(iso) / \(human)")
            print("   mlSearchPhrase: \(mlSearchPhrase)")
        } catch {
            print("⚠️ ALADDIN_EXPORT_MANIFEST write failed: \(error)")
        }
    }
    
    // ✅ НОВОЕ: Асинхронная загрузка логов после инициализации
    // ✅ BUILD 113: Добавлена защита от повторных вызовов для предотвращения множественных запусков
    func loadLogsAsync() {
        Self.loadLogsLock.lock()
        defer { Self.loadLogsLock.unlock() }
        
        guard !Self.hasLoadedLogs else {
            print("⚠️ VisualLogger.loadLogsAsync() уже вызван, пропускаем повторный вызов")
            return
        }
        
        Self.hasLoadedLogs = true
        
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
        let category: String // ✅ BUILD 115: Добавляем категорию лога
        let file: String
        let line: Int

        init(timestamp: Date, message: String, level: LogLevel, category: String, file: String, line: Int) { // ✅ BUILD 115: Добавляем категорию лога
            self.id = UUID()
            self.timestamp = timestamp
            self.message = message
            self.level = level
            self.category = category // ✅ BUILD 115: Добавляем категорию лога
            self.file = file
            self.line = line
        }
        
        var formattedTime: String {
            let formatter = DateFormatter()
            formatter.dateFormat = "HH:mm:ss.SSS"
            return formatter.string(from: timestamp)
        }
    }
    
    enum LogLevel: String, Codable, CaseIterable {
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
    
    func log(_ message: String, level: LogLevel = .info, category: String = "SYSTEM", file: String = #file, line: Int = #line) { // ✅ BUILD 115: Добавляем категорию лога
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
                category: category, // ✅ BUILD 115: Передаем категорию
                file: fileName,
                line: line
            )
            
            self.logs.append(entry)
            if self.logs.count > self.maxLogs {
                self.logs.removeFirst()
            }
            
            // 💾 СОХРАНЯЕМ ЛОГИ В UserDefaults ДЛЯ ВОССТАНОВЛЕНИЯ ПОСЛЕ КРАША
            self.saveLogToUserDefaults(entry)

            #if DEBUG
            print("[\(entry.formattedTime)] [\(level.rawValue)] [\(fileName):\(line)] \(message)")
            #endif
        }
    }
    
    func clear() {
        DispatchQueue.main.async {
            self.logs.removeAll()
        }
    }

    func copyLogsToClipboard() {
        let sourceLogs = logs.isEmpty ? getSavedLogs() : logs
        let logText = sourceLogs.isEmpty ? "VisualLogger: no logs available to copy." : sourceLogs.map { entry in
            "[\(entry.formattedTime)] [\(entry.level.rawValue)] [\(entry.category)] \(entry.message)"
        }.joined(separator: "\n")

        // CRITICAL: Do ALL work on main thread, NO recursive self.log() calls
        DispatchQueue.main.async {
            self.lastExportPath = nil
            self.lastExportHumanTime = nil
            UIPasteboard.general.string = logText
            self.showCopySuccess = true

            let pasted = UIPasteboard.general.string ?? ""
            print("✅ VisualLogger: Successfully copied \(sourceLogs.count) logs to clipboard (\(logText.count) chars, readback=\(pasted.count))")

            // Auto-hide success message WITHOUT calling log()
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                self.showCopySuccess = false
            }
        }
    }

    /// Export logs to **Documents** (`visual-logs-<yyyy-MM-dd'T'HH-mm-ss>.txt`) so the path is stable on simulator/device
    /// and easy to pull with `simctl` / Finder container. Also printed to Xcode console.
    @discardableResult
    func exportLogsToTempFile() -> URL? {
        let exportDate = Date()
        let stamp = Self.exportFilenameTimestamp(for: exportDate)
        let iso = ISO8601DateFormatter().string(from: exportDate)
        let human = Self.exportHumanReadableLocalTime(for: exportDate)
        let bundleId = Bundle.main.bundleIdentifier ?? "unknown"
        let sourceLogs = logs.isEmpty ? getSavedLogs() : logs
        let logBody = sourceLogs.isEmpty ? "VisualLogger: no logs available to export." : sourceLogs.map { entry in
            "[\(entry.formattedTime)] [\(entry.level.rawValue)] [\(entry.category)] \(entry.message)"
        }.joined(separator: "\n")
        let header = """
# ALADDIN Visual Logger Export
# Local time: \(human)
# ISO8601: \(iso)
# File stamp: \(stamp)
# Bundle: \(bundleId)

"""
        let logText = header + logBody

        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        let fileURL = docs.appendingPathComponent("visual-logs-\(stamp).txt")
        do {
            try logText.write(to: fileURL, atomically: true, encoding: .utf8)
            let byteCount: Int = {
                if let n = try? FileManager.default.attributesOfItem(atPath: fileURL.path)[.size] as? NSNumber {
                    return n.intValue
                }
                if let i = try? FileManager.default.attributesOfItem(atPath: fileURL.path)[.size] as? Int64 {
                    return Int(i)
                }
                return logText.utf8.count
            }()
            writeLatestExportManifestForAgents(exportKind: "visual_logs", fileURL: fileURL, byteCount: byteCount, exportDate: exportDate)
            DispatchQueue.main.async {
                self.lastExportPath = fileURL.path
                self.lastExportHumanTime = human
                self.showCopySuccess = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 3.5) {
                    self.showCopySuccess = false
                }
            }
            print("✅ VisualLogger: logs exported to Documents → \(fileURL.path)")
            print("   Simulator: copy from app container …/Documents/visual-logs-*.txt or use Share (if added).")
            print("   Agents: also read Documents/\(Self.latestExportManifestFileName)")
            return fileURL
        } catch {
            print("❌ VisualLogger: failed to export logs file: \(error)")
            DispatchQueue.main.async {
                self.lastExportPath = "export failed: \(error.localizedDescription)"
                self.lastExportHumanTime = nil
                self.showCopySuccess = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
                    self.showCopySuccess = false
                }
            }
            return nil
        }
    }

    func startupTraceURL() -> URL {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
        return (docs ?? FileManager.default.temporaryDirectory).appendingPathComponent("startup_trace.txt")
    }

    func lifecycleTraceURL() -> URL {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
        return (docs ?? FileManager.default.temporaryDirectory).appendingPathComponent("app_lifecycle_trace.txt")
    }
}

// MARK: - Launch file traces (shared; callable before WindowGroup appears)

/// Writes to Documents `startup_trace.txt` / `app_lifecycle_trace.txt` so diagnostics survive Xcode disconnect and SIGKILL.
enum LaunchDiagnostics {
    private static let ioQueue = DispatchQueue(label: "com.aladdin.launchDiagnostics.io", qos: .utility)

    static func appendStartupTrace(_ message: String) {
        appendLine(message, fileName: "startup_trace.txt", consolePrefix: "STARTUP_TRACE")
    }

    static func appendLifecycleTrace(_ message: String) {
        appendLine(message, fileName: "app_lifecycle_trace.txt", consolePrefix: "LIFECYCLE_TRACE")
    }

    private static func appendLine(_ message: String, fileName: String, consolePrefix: String) {
        let ts = ISO8601DateFormatter().string(from: Date())
        let line = "[\(ts)] \(message)\n"
        ioQueue.async {
            let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
            let fileURL = (docs ?? FileManager.default.temporaryDirectory).appendingPathComponent(fileName)
            do {
                if FileManager.default.fileExists(atPath: fileURL.path) {
                    let handle = try FileHandle(forWritingTo: fileURL)
                    defer { try? handle.close() }
                    try handle.seekToEnd()
                    if let data = line.data(using: .utf8) {
                        try handle.write(contentsOf: data)
                    }
                } else {
                    try line.write(to: fileURL, atomically: true, encoding: .utf8)
                }
            } catch {
                print("⚠️ LaunchDiagnostics write failed (\(fileName)): \(error)")
            }
            #if DEBUG
            print("🧭 \(consolePrefix): \(message)")
            #endif
        }
    }
}

// MARK: - Visual Logger View

struct VisualLogView: View {
    @ObservedObject var logger = VisualLogger.shared
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var shareURL: URL? = nil
    @State private var showShareSheet = false
    
    // ✅ Computed property to break up complex body and fix "unable to type-check this expression" error
    private var logLevelFilterPicker: some View {
        Picker(localizationManager.localized("visual_logger_filter_title"), selection: $logger.selectedLogLevelFilter) {
            Text(localizationManager.localized("visual_logger_filter_all")).tag(nil as VisualLogger.LogLevel?)
            ForEach(VisualLogger.LogLevel.allCases, id: \.self) { level in
                Text(level.rawValue).tag(Optional(level) as VisualLogger.LogLevel?)
            }
        }
        .pickerStyle(.menu)
        .font(.caption2)
        .foregroundColor(.white)
        .background(Color.black.opacity(0.3))
        .cornerRadius(4)
    }
    
    var body: some View {
        mainContent
    }
    
    // Final extraction - entire body moved to separate property to resolve persistent type-check timeout
    private var mainContent: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Header
            HStack {
                Text(localizationManager.localized("visual_logger_title"))
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(.white)
                
                logLevelFilterPicker
                
                Spacer()
                actionButtons
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.black.opacity(0.7))
            
            if logger.isVisible {
                logContentView
            }
        }
        .font(.system(size: 11, design: .monospaced))
        .background(Color.black.opacity(0.7))
        .cornerRadius(10)
        .padding(8)
        .shadow(color: Color.black.opacity(0.4), radius: 10, x: 0, y: 5)
    }
    
    // ✅ Extracted to fix "unable to type-check this expression" compiler error
    private var actionButtons: some View {
        HStack(spacing: 4) {
            if logger.showCopySuccess {
                Group {
                    if let path = logger.lastExportPath {
                        let timeLine = logger.lastExportHumanTime.map { "🕐 \($0)\n" } ?? ""
                        Text(path.hasPrefix("/") ? "✅ Экспорт\n\(timeLine)\(path)" : "✅ \(timeLine)\(path)")
                            .font(.caption2)
                            .foregroundColor(.green)
                            .lineLimit(6)
                            .multilineTextAlignment(.leading)
                    } else {
                        Text(localizationManager.localized("visual_logger_copy_success"))
                            .font(.caption)
                            .foregroundColor(.green)
                    }
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.white.opacity(0.2))
                .cornerRadius(4)
            }
            Button(action: {
                logger.forceCopyToClipboard()
            }) {
                Text(localizationManager.localized("visual_logger_copy_button"))
                    .font(.caption)
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue)
                    .cornerRadius(4)
            }
            Button(action: {
                _ = logger.exportLogsToTempFile()
            }) {
                Text(localizationManager.localized("visual_logger_export_button"))
                    .font(.caption)
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.orange)
                    .cornerRadius(4)
            }
            Button(action: {
                let startup = logger.startupTraceURL()
                if FileManager.default.fileExists(atPath: startup.path) {
                    let shareDate = Date()
                    let sz: Int = {
                        if let n = try? FileManager.default.attributesOfItem(atPath: startup.path)[.size] as? NSNumber {
                            return n.intValue
                        }
                        if let i = try? FileManager.default.attributesOfItem(atPath: startup.path)[.size] as? Int64 {
                            return Int(i)
                        }
                        return 0
                    }()
                    logger.writeLatestExportManifestForAgents(exportKind: "startup_trace", fileURL: startup, byteCount: sz, exportDate: shareDate)
                    let human = VisualLogger.exportHumanReadableLocalTime(for: shareDate)
                    logger.lastExportPath = startup.path
                    logger.lastExportHumanTime = human
                    shareURL = startup
                    showShareSheet = true
                } else {
                    logger.lastExportPath = "startup_trace.txt not found"
                    logger.lastExportHumanTime = nil
                    logger.showCopySuccess = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                        logger.showCopySuccess = false
                    }
                }
            }) {
                Text(localizationManager.localized("visual_logger_share_trace_button"))
                    .font(.caption)
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.purple)
                    .cornerRadius(4)
            }
            Button(action: { logger.clear() }) {
                Text(localizationManager.localized("visual_logger_clear_button"))
                    .font(.caption)
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.red)
                    .cornerRadius(4)
            }
        }
    }
    
    // ✅ Extracted ScrollView to fix remaining type-check timeout error
    private var logContentView: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 2) {
                ForEach(logger.logs.reversed().filter { entry in
                    logger.selectedLogLevelFilter == nil || entry.level == logger.selectedLogLevelFilter
                }) { entry in
                    HStack(alignment: .top, spacing: 4) {
                        Text("[\(entry.formattedTime)]")
                            .font(.system(size: 9))
                            .foregroundColor(.gray)
                        Text("[\(entry.category)]")
                            .font(.system(size: 9))
                            .foregroundColor(.white.opacity(0.8))
                        Text(entry.level.rawValue)
                            .font(.system(size: 10))
                            .foregroundColor(entry.level.color)
                        Text(entry.message)
                            .font(.system(size: 10))
                            .foregroundColor(entry.level.color)
                            .multilineTextAlignment(.leading)
                    }
                    .padding(.horizontal, 4)
                    .padding(.vertical, 2)
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .textSelection(.enabled)
            .padding(4)
        }
        .frame(maxHeight: 200)
        .background(Color.black.opacity(0.85))
        .cornerRadius(6)
        .overlay(
            RoundedRectangle(cornerRadius: 6)
                .stroke(Color.white.opacity(0.2), lineWidth: 1)
        )
        .onLongPressGesture {
            logger.forceCopyToClipboard()
        }
        .sheet(isPresented: $showShareSheet) {
            if let url = shareURL {
                ActivityViewController(activityItems: [url])
            }
        }
        .overlay(alignment: .bottomLeading) {
            if let lastPath = logger.lastExportPath, lastPath.hasPrefix("/") {
                let suffix = logger.lastExportHumanTime.map { "\n🕐 \($0)" } ?? ""
                Text("📄 \(lastPath)\(suffix)")
                    .font(.system(size: 8))
                    .foregroundColor(.white.opacity(0.8))
                    .padding(4)
            }
        }
    }
}

struct ActivityViewController: UIViewControllerRepresentable {
    let activityItems: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}

// MARK: - View Modifier для добавления VisualLogView на любой экран

extension View {
    /// ✅ ИСПРАВЛЕНИЕ: Модификатор для добавления VisualLogView на любой экран
    /// Используется для отображения логов на всех страницах приложения, включая модальные окна и подстраницы
    func withVisualLogger() -> some View {
        #if DEBUG
        return self.overlay(
            VStack {
                Spacer()
                HStack {
                    Spacer()
                    VisualLogView()
                        .environmentObject(LocalizationManager.shared)
                        .frame(maxWidth: 280)
                        .padding(.trailing, 16)
                        .padding(.bottom, 120)
                        .allowsHitTesting(true) // Only the logger widget should capture taps
                }
            }
            .allowsHitTesting(false) // Do not block interactions with underlying screens
        )
        #else
        return self
        #endif
    }
}
