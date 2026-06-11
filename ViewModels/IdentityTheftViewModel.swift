import Foundation
import Combine

/**
 * 🛡️ Identity Theft Protection ViewModel
 * Управление данными для IdentityTheftModal и Identity Hub (B4-03).
 */

@MainActor
class IdentityTheftViewModel: ObservableObject {

    @Published var stats: IdentityTheftStats?
    @Published var attempts: [IdentityTheftAttempt] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var requiresPremiumUpgrade = false
    @Published var processingAttemptId: String?

    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private var cancellables = Set<AnyCancellable>()

    init(apiService: APIService? = nil, localizationManager: LocalizationManager = LocalizationManager()) {
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
    }

    func loadData(action: String? = nil, severity: String? = nil) async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            requiresPremiumUpgrade = false
            return
        }

        isLoading = true
        errorMessage = nil
        requiresPremiumUpgrade = false
        defer { isLoading = false }

        do {
            async let statsTask: IdentityTheftStats = withCheckedThrowingContinuation { continuation in
                Task { @MainActor in
                    self.apiService.getIdentityTheftStats { result in
                        continuation.resume(with: result)
                    }
                }
            }

            async let attemptsTask: [IdentityTheftAttempt] = withCheckedThrowingContinuation { continuation in
                Task { @MainActor in
                    self.apiService.getIdentityTheftAttempts(action: action, severity: severity) { result in
                        continuation.resume(with: result)
                    }
                }
            }

            let (stats, attempts) = try await (statsTask, attemptsTask)
            self.stats = stats
            self.attempts = attempts
            errorMessage = nil
        } catch {
            applyLoadFailure(error)
        }
    }

    func allowAttempt(attemptId: String) async {
        await performAttemptAction(attemptId: attemptId) { completion in
            apiService.allowIdentityTheftAttempt(attemptId: attemptId, completion: completion)
        }
    }

    func blockAttempt(attemptId: String) async {
        await performAttemptAction(attemptId: attemptId) { completion in
            apiService.blockIdentityTheftAttempt(attemptId: attemptId, completion: completion)
        }
    }

    func addToWhitelist(source: String) async {
        processingAttemptId = nil
        isLoading = true
        errorMessage = nil
        requiresPremiumUpgrade = false
        defer { isLoading = false }

        do {
            try await withCheckedThrowingContinuation { continuation in
                apiService.addToWhitelist(source: source) { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadData()
        } catch {
            applyActionFailure(error)
        }
    }

    private func performAttemptAction(
        attemptId: String,
        request: (@escaping (Result<APIResponse<Bool>, Error>) -> Void) -> Void
    ) async {
        processingAttemptId = attemptId
        errorMessage = nil
        requiresPremiumUpgrade = false
        defer { processingAttemptId = nil }

        do {
            try await withCheckedThrowingContinuation { continuation in
                request { result in
                    continuation.resume(with: result.map { _ in () })
                }
            }
            await loadData()
        } catch {
            applyActionFailure(error)
        }
    }

    private func applyLoadFailure(_ error: Error) {
        let presentation = identityFailurePresentation(for: error)
        requiresPremiumUpgrade = presentation.requiresPremiumUpgrade
        errorMessage = presentation.errorMessage

        if presentation.requiresPremiumUpgrade {
            stats = nil
            attempts = []
            return
        }

        let networkError = NetworkError.from(error)
        if case .unauthorized = networkError {
            stats = nil
            attempts = []
            return
        }

        if case .notFound = networkError {
            stats = nil
            attempts = []
            errorMessage = nil
            return
        }

        if case .mockSourceRejected = error as? SecurityVerdictValidationError {
            stats = nil
            attempts = []
            return
        }

        if !networkError.isCritical && networkError.isRetryable {
            errorMessage = nil
        }

        stats = nil
        attempts = []
    }

    private func applyActionFailure(_ error: Error) {
        let presentation = identityFailurePresentation(for: error)
        requiresPremiumUpgrade = presentation.requiresPremiumUpgrade
        errorMessage = presentation.errorMessage
    }

    private func identityFailurePresentation(for error: Error) -> AntifakeCheckFailurePresentation {
        if case .mockSourceRejected = error as? SecurityVerdictValidationError {
            return AntifakeCheckFailurePresentation(
                requiresPremiumUpgrade: false,
                errorMessage: localizationManager.localized("antifake_error_mock_rejected")
            )
        }
        return AntifakeCheckFailureHandler.present(error: error, localizationManager: localizationManager)
    }
}
