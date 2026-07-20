import SwiftUI
import UIKit

/// Settings → Support → «Подключить Telegram»: JWT → POST /api/telegram/link-code → 6-char code for `/link` in bot.
struct TelegramLinkScreen: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var isLoading = false
    @State private var code: String?
    @State private var botUsername: String = "AladdinchatAI_bot"
    @State private var expiresAt: Date?
    @State private var remainingSeconds: Int = 0
    @State private var errorMessage: String?
    @State private var didCopy = false

    private let apiService = APIService.shared
    private let ticker = Timer.publish(every: 1.0, on: .main, in: .common).autoconnect()

    var body: some View {
        NavigationView {
            ScrollView(.vertical, showsIndicators: true) {
                VStack(alignment: .leading, spacing: 20) {
                    Text(localizationManager.localized("tg_link_intro"))
                        .font(.body)
                        .foregroundColor(.secondary)
                        .fixedSize(horizontal: false, vertical: true)

                    memWarningBanner

                    if let errorMessage {
                        Text(errorMessage)
                            .font(.subheadline)
                            .foregroundColor(.red)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    if let code {
                        codeBlock(code)
                        ttlLabel
                        actionButtons(for: code)
                        commandHint(for: code)
                    } else {
                        getCodeButton
                    }
                }
                .padding(20)
            }
            .background(Color(.systemGroupedBackground).ignoresSafeArea())
            .navigationTitle(localizationManager.localized("tg_link_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("common_close")) {
                        dismiss()
                    }
                }
            }
            .onReceive(ticker) { _ in
                refreshCountdown()
            }
        }
    }

    // MARK: - Sections

    private var memWarningBanner: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.orange)
            Text(localizationManager.localized("tg_link_mem_warning"))
                .font(.subheadline)
                .foregroundColor(.primary)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.orange.opacity(0.12))
        .cornerRadius(10)
        .accessibilityElement(children: .combine)
    }

    private func codeBlock(_ code: String) -> some View {
        Text(code)
            .font(.system(size: 36, weight: .bold, design: .monospaced))
            .foregroundColor(.primary)
            .tracking(4)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 24)
            .background(Color(.secondarySystemBackground))
            .cornerRadius(12)
            .accessibilityLabel(code)
            .textSelection(.enabled)
    }

    private var ttlLabel: some View {
        Group {
            if remainingSeconds > 0 {
                let minutes = max(1, Int(ceil(Double(remainingSeconds) / 60.0)))
                Text(String(format: localizationManager.localized("tg_link_ttl"), "\(minutes)"))
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            } else if code != nil {
                Text(localizationManager.localized("tg_link_expired"))
                    .font(.subheadline)
                    .foregroundColor(.red)
            }
        }
    }

    private var getCodeButton: some View {
        Button(action: requestCode) {
            HStack {
                if isLoading {
                    ProgressView()
                        .tint(.white)
                }
                Text(isLoading
                     ? localizationManager.localized("tg_link_loading")
                     : localizationManager.localized("tg_link_get_code"))
                    .font(.body.bold())
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .foregroundColor(.white)
            .background(Color.blue)
            .cornerRadius(12)
        }
        .disabled(isLoading)
        .buttonStyle(PlainButtonStyle())
        .accessibilityLabel(localizationManager.localized("tg_link_get_code"))
    }

    private func actionButtons(for code: String) -> some View {
        VStack(spacing: 10) {
            Button(action: { copyCode(code) }) {
                HStack {
                    Image(systemName: didCopy ? "checkmark" : "doc.on.doc")
                    Text(didCopy
                         ? localizationManager.localized("tg_link_copied")
                         : localizationManager.localized("tg_link_copy"))
                        .font(.body.bold())
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .foregroundColor(.blue)
                .background(Color.blue.opacity(0.12))
                .cornerRadius(12)
            }
            .buttonStyle(PlainButtonStyle())

            Button(action: openBot) {
                HStack {
                    Image(systemName: "paperplane.fill")
                    Text(localizationManager.localized("tg_link_open_bot"))
                        .font(.body.bold())
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .foregroundColor(.white)
                .background(Color.blue)
                .cornerRadius(12)
            }
            .buttonStyle(PlainButtonStyle())

            Button(action: requestCode) {
                Text(localizationManager.localized("tg_link_refresh"))
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .disabled(isLoading)
            .buttonStyle(PlainButtonStyle())
            .padding(.top, 4)
        }
    }

    private func commandHint(for code: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(String(format: localizationManager.localized("tg_link_bot_label"), botUsername))
                .font(.subheadline.bold())
            Text(String(format: localizationManager.localized("tg_link_hint_command"), code))
                .font(.system(.body, design: .monospaced))
                .foregroundColor(.secondary)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemBackground))
        .cornerRadius(10)
    }

    // MARK: - Actions

    private func requestCode() {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil
        didCopy = false

        apiService.createTelegramLinkCode { result in
            Task { @MainActor in
                isLoading = false
                switch result {
                case .success(let response):
                    let trimmed = response.code.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
                    guard !trimmed.isEmpty else {
                        errorMessage = localizationManager.localized("tg_link_error_generic")
                        return
                    }
                    code = trimmed
                    botUsername = Self.normalizedBotUsername(response.botUsername)
                    let ttl = max(1, response.expiresInSec)
                    expiresAt = Date().addingTimeInterval(TimeInterval(ttl))
                    remainingSeconds = ttl
                case .failure(let error):
                    code = nil
                    expiresAt = nil
                    remainingSeconds = 0
                    errorMessage = Self.userFacingError(error, localize: localizationManager.localized)
                }
            }
        }
    }

    private func copyCode(_ code: String) {
        UIPasteboard.general.string = code
        HapticFeedback.selection()
        didCopy = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            didCopy = false
        }
    }

    private func openBot() {
        let urlString = "https://t.me/\(botUsername)"
        guard let url = URL(string: urlString) else { return }
        UIApplication.shared.open(url)
    }

    private func refreshCountdown() {
        guard let expiresAt else { return }
        let left = Int(expiresAt.timeIntervalSinceNow)
        remainingSeconds = max(0, left)
        if remainingSeconds == 0 {
            // Keep code visible but mark expired via ttlLabel.
        }
    }

    private static func normalizedBotUsername(_ raw: String) -> String {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.hasPrefix("@") {
            return String(trimmed.dropFirst())
        }
        return trimmed.isEmpty ? "AladdinchatAI_bot" : trimmed
    }

    private static func userFacingError(
        _ error: Error,
        localize: (String) -> String
    ) -> String {
        if let networkError = error as? NetworkError {
            switch networkError {
            case .unauthorized:
                return localize("tg_link_error_unauthorized")
            default:
                break
            }
        }
        let lower = error.localizedDescription.lowercased()
        if lower.contains("unauthorized") || lower.contains("токен") || lower.contains("401") {
            return localize("tg_link_error_unauthorized")
        }
        return localize("tg_link_error_generic")
    }
}

#if DEBUG
struct TelegramLinkScreen_Previews: PreviewProvider {
    static var previews: some View {
        TelegramLinkScreen()
            .environmentObject(LocalizationManager.shared)
    }
}
#endif
