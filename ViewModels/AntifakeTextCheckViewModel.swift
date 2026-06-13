import Foundation

enum AntifakeTextInputMode: String, CaseIterable, Identifiable {
    case text
    case url

    var id: String { rawValue }

    var titleKey: String {
        switch self {
        case .text: return "antifake_mode_text"
        case .url: return "antifake_mode_url"
        }
    }

    var hintKey: String {
        switch self {
        case .text: return "antifake_text_hint"
        case .url: return "antifake_url_hint"
        }
    }
}

@MainActor
final class AntifakeTextCheckViewModel: ObservableObject {

    @Published var inputMode: AntifakeTextInputMode = .text
    @Published var inputText = ""
    @Published var inputUrl = ""
    @Published var verdict: SecurityVerdict?
    @Published var isChecking = false
    @Published var errorMessage: String?
    @Published var requiresPremiumUpgrade = false

    private let apiService: APIService
    private let localizationManager: LocalizationManager

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

    private var trimmedInput: String {
        switch inputMode {
        case .text:
            return inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        case .url:
            return inputUrl.trimmingCharacters(in: .whitespacesAndNewlines)
        }
    }

    func applySharePayload(_ payload: AntifakeSharePayload) {
        switch payload.mode {
        case .text:
            inputMode = .text
            inputText = payload.value
        case .url:
            inputMode = .url
            inputUrl = payload.value
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
                result = try await performTextCheck(payload)
            case .url:
                result = try await performUrlCheck(payload)
            }
            verdict = result
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

    private func performTextCheck(_ text: String) async throws -> SecurityVerdict {
        try await withCheckedThrowingContinuation { continuation in
            apiService.antifakeCheckText(text: text) { result in
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
