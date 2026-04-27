import SwiftUI

/// 🧾 CrashLogsView (BUILD 95)
/// Экран просмотра диагностических логов прямо на устройстве (TestFlight/Release).
struct CrashLogsView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var text: String = "Загрузка логов..."
    @State private var showShare = false

    private var shareItems: [Any] { [text] }

    var body: some View {
        NavigationView {
            VStack(spacing: 12) {
                TextEditor(text: $text)
                    .font(.system(.footnote, design: .monospaced))
                    .padding(8)
                    .background(Color.black.opacity(0.06))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .padding(.horizontal, 12)

                HStack(spacing: 12) {
                    Button("Обновить") {
                        loadLogs()
                    }
                    .buttonStyle(.bordered)

                    Button("Поделиться") {
                        showShare = true
                    }
                    .buttonStyle(.borderedProminent)

                    Button("Очистить") {
                        _ = clearCrashLogs()
                        loadLogs()
                    }
                    .buttonStyle(.bordered)
                }
                .padding(.bottom, 12)
            }
            .navigationTitle(localizationManager.localized("crash_logs_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Закрыть") { dismiss() }
                }
            }
            .onAppear { loadLogs() }
            .sheet(isPresented: $showShare) {
                ShareSheet(activityItems: shareItems)
            }
        }
    }

    private func loadLogs() {
        var result = ""

        // 1) Собранный набор (UserDefaults + файлы crash_log/crash_stack)
        result += getAllCrashLogs()

        // 2) Memory warning
        if let mw = UserDefaults.standard.string(forKey: "memory_warning_log") {
            result += "\n\n=== 🚨 MEMORY WARNING (UserDefaults) ===\n"
            result += mw
        }

        // 3) Pre-crash state (UserDefaults)
        if let data = UserDefaults.standard.data(forKey: "pre_crash_state"),
           let json = String(data: data, encoding: .utf8) {
            result += "\n\n=== 🧠 PRE-CRASH STATE (UserDefaults) ===\n"
            result += json
        }

        // 4) SETTINGS_DIAG ring buffer (MasterLogger → SettingsDiagnosticsLogger)
        let settingsRing = SettingsDiagnosticsLogger.shared.exportLogs()
        if !settingsRing.isEmpty {
            result += "\n\n=== SETTINGS_DIAG (in-memory, Console category SETTINGS_DIAG) ===\n"
            result += settingsRing
        }

        text = result.isEmpty ? "Логи не найдены." : result
    }
}

