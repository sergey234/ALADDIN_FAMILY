import Foundation

enum IdentitySNILSNormalizer {
    static func digits(from raw: String) -> String {
        raw.filter(\.isNumber)
    }

    static func isValid(_ raw: String) -> Bool {
        digits(from: raw).count == 11
    }
}

@MainActor
final class IdentityDetectViewModel: ObservableObject {

    @Published var snilsInput = ""
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
        IdentitySNILSNormalizer.isValid(snilsInput) && !isChecking
    }

    func submitDetect() async -> Bool {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return false
        }

        guard IdentitySNILSNormalizer.isValid(snilsInput) else {
            errorMessage = localizationManager.localized("identity_hub_snils_invalid")
            return false
        }

        let snils = snilsInput.trimmingCharacters(in: .whitespacesAndNewlines)

        isChecking = true
        errorMessage = nil
        verdict = nil
        requiresPremiumUpgrade = false
        defer { isChecking = false }

        do {
            let result = try await performDetect(snils)
            verdict = result
            return true
        } catch {
            handleCheckError(error)
            return false
        }
    }

    private func performDetect(_ snils: String) async throws -> SecurityVerdict {
        try await withCheckedThrowingContinuation { continuation in
            apiService.detectIdentityTheft(snils: snils) { result in
                continuation.resume(with: result)
            }
        }
    }

    private func handleCheckError(_ error: Error) {
        let networkError = NetworkError.from(error)
        if case .badRequest(let detail) = networkError, detail?.contains("invalid_snils") == true {
            errorMessage = localizationManager.localized("identity_hub_snils_invalid")
            return
        }

        let presentation = AntifakeCheckFailureHandler.present(
            error: error,
            localizationManager: localizationManager
        )
        requiresPremiumUpgrade = presentation.requiresPremiumUpgrade
        errorMessage = presentation.errorMessage
    }
}
