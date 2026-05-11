import SwiftUI
import UIKit

/// 🧾 CrashLogsView (BUILD 95)
/// Экран просмотра диагностических логов прямо на устройстве (TestFlight/Release).
struct CrashLogsView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var text: String = "Загрузка логов..."
    @State private var showShareFullScreen = false
    @State private var shareExportURL: URL?

    @State private var showTelegramConsentAlert = false
    @State private var showTelegramErrorAlert = false
    @State private var telegramErrorText = ""

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
                        prepareShareExport()
                    }
                    .buttonStyle(.borderedProminent)

                    Button("Очистить") {
                        _ = clearCrashLogs()
                        loadLogs()
                    }
                    .buttonStyle(.bordered)
                }

                Button(localizationManager.localized("crash_logs_support_telegram_button")) {
                    showTelegramConsentAlert = true
                }
                .buttonStyle(.bordered)

                Text(localizationManager.localized("crash_logs_support_footer"))
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 12)

                Spacer(minLength: 0)
            }
            .padding(.bottom, 12)
            .navigationTitle(localizationManager.localized("crash_logs_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Закрыть") { dismiss() }
                }
            }
            .onAppear { loadLogs() }
            .alert(
                localizationManager.localized("crash_logs_support_telegram_alert_title"),
                isPresented: $showTelegramConsentAlert
            ) {
                Button(localizationManager.localized("crash_logs_support_telegram_cancel"), role: .cancel) {}
                Button(localizationManager.localized("crash_logs_support_telegram_continue")) {
                    openTelegramSupportChat()
                }
            } message: {
                Text(localizationManager.localized("crash_logs_support_telegram_alert_message"))
            }
            .alert("Telegram", isPresented: $showTelegramErrorAlert) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(telegramErrorText)
            }
            /// Вложенный `.sheet` поверх `.sheet` (Настройки → Логи) часто ломает `UIActivityViewController`.
            /// `fullScreenCover` поднимает share над текущим модальным окном.
            .fullScreenCover(isPresented: $showShareFullScreen, onDismiss: {
                if let url = shareExportURL {
                    try? FileManager.default.removeItem(at: url)
                }
                shareExportURL = nil
            }) {
                if let url = shareExportURL {
                    ShareSheet(activityItems: [url]) {
                        showShareFullScreen = false
                    }
                }
            }
        }
    }

    private func loadLogs() {
        text = composeDiagnosticsText()
    }

    /// Deep link в бота: `tg://resolve?domain=…&start=…` или fallback `https://t.me/…?start=…`.
    /// `start` — только [A-Za-z0-9_], до 64 символов (см. `AppConfig.supportTelegramStartToken()`).
    private func openTelegramSupportChat() {
        let bot = AppConfig.supportTelegramBotUsername
        guard !bot.isEmpty else {
            telegramErrorText = localizationManager.localized("crash_logs_support_bot_missing")
            showTelegramErrorAlert = true
            return
        }
        let token = AppConfig.supportTelegramStartToken()
        guard let httpsURL = URL(string: "https://t.me/\(bot)?start=\(token)") else {
            telegramErrorText = localizationManager.localized("crash_logs_support_telegram_failed")
            showTelegramErrorAlert = true
            return
        }
        guard let tgURL = URL(string: "tg://resolve?domain=\(bot)&start=\(token)") else {
            UIApplication.shared.open(httpsURL) { _ in }
            return
        }

        if UIApplication.shared.canOpenURL(tgURL) {
            UIApplication.shared.open(tgURL, options: [:]) { success in
                if !success {
                    DispatchQueue.main.async {
                        UIApplication.shared.open(httpsURL, options: [:]) { ok in
                            DispatchQueue.main.async {
                                if !ok {
                                    telegramErrorText = localizationManager.localized("crash_logs_support_telegram_failed")
                                    showTelegramErrorAlert = true
                                }
                            }
                        }
                    }
                }
            }
        } else {
            UIApplication.shared.open(httpsURL, options: [:]) { success in
                DispatchQueue.main.async {
                    if !success {
                        telegramErrorText = localizationManager.localized("crash_logs_support_telegram_failed")
                        showTelegramErrorAlert = true
                    }
                }
            }
        }
    }

    /// Полный текст для экрана и для экспорта (UTF-8 файл — надёжнее для Почты, чем огромное тело письма).
    private func composeDiagnosticsText() -> String {
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

        // 5) Launch trace files (persist across SIGKILL / Xcode disconnect)
        result += appendFileSection(
            title: "STARTUP_TRACE (Documents/startup_trace.txt)",
            fileName: "startup_trace.txt"
        )
        result += appendFileSection(
            title: "LIFECYCLE_TRACE (Documents/app_lifecycle_trace.txt)",
            fileName: "app_lifecycle_trace.txt"
        )

        // 6) Статус последней попытки авто-отправки (если когда-либо включали NSSetUncaughtExceptionHandler)
        if let sendErr = UserDefaults.standard.string(forKey: "crash_log_send_error") {
            result += "\n\n=== LAST CRASH AUTO-SEND ERROR (UserDefaults) ===\n\(sendErr)\n"
        }
        if let sendOk = UserDefaults.standard.string(forKey: "crash_log_send_status") {
            result += "\n=== LAST CRASH AUTO-SEND STATUS (UserDefaults) ===\n\(sendOk)\n"
        }

        return result.isEmpty ? "Логи не найдены." : result
    }

    private func appendFileSection(title: String, fileName: String) -> String {
        guard let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first else {
            return ""
        }
        let url = documentsPath.appendingPathComponent(fileName)
        guard let content = try? String(contentsOf: url, encoding: .utf8), !content.isEmpty else {
            return ""
        }
        return "\n\n=== \(title) ===\n\(content)"
    }

    private func prepareShareExport() {
        let payload = composeDiagnosticsText()
        let name = "aladdin_diagnostics_\(Int(Date().timeIntervalSince1970)).txt"
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(name)
        do {
            try payload.write(to: url, atomically: true, encoding: .utf8)
            shareExportURL = url
            showShareFullScreen = true
        } catch {
            text = payload + "\n\n=== EXPORT ERROR ===\nНе удалось подготовить файл для отправки: \(error.localizedDescription)\n"
        }
    }
}
