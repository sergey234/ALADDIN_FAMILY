import Foundation
import UIKit

enum AntifakeTextInputMode: String, CaseIterable, Identifiable {
    case text
    case url
    case contact

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .text: return "antifake_mode_text"
        case .url: return "antifake_mode_url"
        case .contact: return "antifake_mode_contact"
        }
    }

    var hintKey: String {
        switch self {
        case .text: return "antifake_text_hint"
        case .url: return "antifake_url_hint"
        case .contact: return "antifake_contact_hint"
        }
    }
}

@MainActor
final class AntifakeTextCheckViewModel: ObservableObject {

    @Published var inputMode: AntifakeTextInputMode = .text
    @Published var inputText = ""
    @Published var inputUrl = ""
    @Published var callerId = ""
    @Published var displayName = ""
    @Published var verdict: SecurityVerdict?
    @Published var isChecking = false
    @Published var errorMessage: String?
    @Published var requiresPremiumUpgrade = false

    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private var lastSubmitAt: Date?
    private let submitDebounceInterval: TimeInterval = 0.85

    init(
        apiService: APIService? = nil,
        localizationManager: LocalizationManager = LocalizationManager()
    ) {
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
    }

    var canSubmit: Bool {
        !trimmedInput.isEmpty && !isChecking
    }

    var hasClipboardContent: Bool {
        guard let string = UIPasteboard.general.string else { return false }
        return !string.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private var trimmedInput: String {
        switch inputMode {
        case .text:
            return inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        case .url:
            return inputUrl.trimmingCharacters(in: .whitespacesAndNewlines)
        case .contact:
            return AntifakeTextInputClassifier.composeContactCheckText(
                callerId: callerId,
                displayName: displayName,
                localizationManager: localizationManager
            )
        }
    }

    func applySharePayload(_ payload: AntifakeSharePayload) {
        switch payload.mode {
        case .text:
            applyPastedContent(payload.value)
        case .url:
            inputMode = .url
            inputUrl = AntifakeTextInputClassifier.normalizeURL(payload.value)
        }
        verdict = nil
        errorMessage = nil
        requiresPremiumUpgrade = false
    }

    func pasteFromClipboard() {
        guard let string = UIPasteboard.general.string else { return }
        applyPastedContent(string)
    }

    func applyPastedContent(_ raw: String) {
        switch AntifakeTextInputClassifier.classify(raw) {
        case .url(let url):
            inputMode = .url
            inputUrl = url
            inputText = ""
            callerId = ""
            displayName = ""
        case .phone(let phone):
            inputMode = .contact
            callerId = phone
            inputText = ""
            inputUrl = ""
        case .text(let text):
            if AntifakeTextInputClassifier.extractURL(from: text) != nil {
                inputMode = .url
                inputUrl = AntifakeTextInputClassifier.extractURL(from: text) ?? text
            } else {
                inputMode = .text
                inputText = text
            }
        }
        verdict = nil
        errorMessage = nil
        requiresPremiumUpgrade = false
    }

    func submitCheck() async -> Bool {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return false
        }
        guard !isChecking else { return false }
        let now = Date()
        if let lastSubmitAt, now.timeIntervalSince(lastSubmitAt) < submitDebounceInterval {
            return false
        }
        lastSubmitAt = now

        if inputMode == .text, let url = AntifakeTextInputClassifier.extractURL(from: inputText) {
            inputMode = .url
            inputUrl = url
            inputText = ""
        }

        let payload = trimmedInput
        guard !payload.isEmpty else { return false }

        isChecking = true
        errorMessage = nil
        verdict = nil
        requiresPremiumUpgrade = false
        defer { isChecking = false }

        do {
            let result: SecurityVerdict
            switch inputMode {
            case .text:
                result = try await performTextCheck(payload, mode: "news")
            case .url:
                result = try await performUrlCheck(payload)
            case .contact:
                result = try await performTextCheck(payload, mode: "message")
            }
            verdict = result
            AntifakeAnalytics.trackCheckComplete(
                kind: inputMode.rawValue,
                verdict: result.verdict.rawValue,
                source: result.source
            )
            AntifakeHistoryRecorder.record(
                verdict: result,
                kind: inputMode.rawValue,
                summary: String(payload.prefix(120))
            )
            return true
        } catch {
            handleCheckError(error)
            return false
        }
    }

    private func performTextCheck(_ text: String, mode: String) async throws -> SecurityVerdict {
        try await withCheckedThrowingContinuation { continuation in
            apiService.antifakeCheckText(text: text, mode: mode) { result in
                continuation.resume(with: result)
            }
        }
    }

    private func performUrlCheck(_ url: String) async throws -> SecurityVerdict {
        try await withCheckedThrowingContinuation { continuation in
            apiService.antifakeCheckUrl(url: url) { result in
                continuation.resume(with: result)
            }
        }
    }

    private func handleCheckError(_ error: Error) {
        let presentation = AntifakeCheckFailureHandler.present(
            error: error,
            localizationManager: localizationManager
        )
        requiresPremiumUpgrade = presentation.requiresPremiumUpgrade
        errorMessage = presentation.errorMessage
    }
}
