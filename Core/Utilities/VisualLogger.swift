import SwiftUI
import Foundation

/**
 * 🔍 Visual Logger - для отображения логов на экране
 * Используется когда Xcode консоль недоступна
 */
class VisualLogger: ObservableObject {
    static let shared = VisualLogger()
    
    @Published var logs: [LogEntry] = []
    @Published var isVisible: Bool = true
    @Published var showErrorOnly: Bool = false
    
    private let maxLogs = 50
    private var logQueue = DispatchQueue(label: "com.aladdin.visualLogger", qos: .utility)
    
    private init() {}
    
    struct LogEntry: Identifiable {
        let id = UUID()
        let timestamp: Date
        let message: String
        let level: LogLevel
        let file: String
        let line: Int
        
        var formattedTime: String {
            let formatter = DateFormatter()
            formatter.dateFormat = "HH:mm:ss.SSS"
            return formatter.string(from: timestamp)
        }
    }
    
    enum LogLevel: String {
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
    
    func log(_ message: String, level: LogLevel = .info, file: String = #file, line: Int = #line) {
        let fileName = (file as NSString).lastPathComponent
        let entry = LogEntry(
            timestamp: Date(),
            message: message,
            level: level,
            file: fileName,
            line: line
        )
        
        DispatchQueue.main.async {
            self.logs.append(entry)
            if self.logs.count > self.maxLogs {
                self.logs.removeFirst()
            }
        }
        
        // Также пишем в консоль для Xcode
        print("[\(entry.formattedTime)] [\(level.rawValue)] [\(fileName):\(line)] \(message)")
    }
    
    func clear() {
        DispatchQueue.main.async {
            self.logs.removeAll()
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
                Button(action: { logger.clear() }) {
                    Text("Очистить")
                        .font(.caption)
                        .foregroundColor(.white)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.red)
                        .cornerRadius(4)
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

