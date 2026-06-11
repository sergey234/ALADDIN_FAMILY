import Foundation

@MainActor
final class IdentityMonitorViewModel: ObservableObject {

    @Published private(set) var isFraudProtectionEnabled = false
    @Published var stats: IdentityTheftStats?
    @Published var monitorVerdict: SecurityVerdict?
    @Published var isLoadingStats = false
    @Published var isUpdatingToggle = false
    @Published var isRunningMonitor = false
    @Published var errorMessage: String?
    @Published var requiresPremiumUpgrade = false

    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private let protectionSettingsManager: ProtectionSettingsManager
    private let tariffManager: TariffManager

    init(
        apiService: APIService? = nil,
        localizationManager: LocalizationManager = LocalizationManager(),
        protectionSettingsManager: ProtectionSettingsManager? = nil,
        tariffManager: TariffManager? = nil
    ) {
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
        self.protectionSettingsManager = protectionSettingsManager ?? ProtectionSettingsManager.shared
        self.tariffManager = tariffManager ?? TariffManager.shared
        syncFraudEnabledFromLocalSettings()
    }

    var isFraudCategoryAvailable: Bool {
        tariffManager.isCategoryAvailable(.fraud)
    }

    var canRunCreditMonitor: Bool {
        isFraudProtectionEnabled && !isRunningMonitor && !isUpdatingToggle
    }

    func syncFraudEnabledFromLocalSettings() {
        isFraudProtectionEnabled = protectionSettingsManager.settings.isEnabled(.fraud)
    }

    func refresh() async {
        await loadStats()
        if isFraudProtectionEnabled {
            await runCreditMonitor(showErrors: false)
        }
    }

    func setFraudProtectionEnabled(_ enabled: Bool) async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }

        guard isFraudCategoryAvailable else {
            requiresPremiumUpgrade = true
            errorMessage = localizationManager.localized("antifake_premium_required_body")
            syncFraudEnabledFromLocalSettings()
            return
        }

        if enabled == isFraudProtectionEnabled {
            return
        }

        isUpdatingToggle = true
        errorMessage = nil
        requiresPremiumUpgrade = false
        defer { isUpdatingToggle = false }

        do {
            if enabled {
                try await enableFraudProtection()
                isFraudProtectionEnabled = true
                await runCreditMonitor(showErrors: true)
            } else {
                try await disableFraudProtection()
                isFraudProtectionEnabled = false
                monitorVerdict = nil
            }
        } catch {
            syncFraudEnabledFromLocalSettings()
            applyFailure(error)
        }
    }

    func runCreditMonitor(showErrors: Bool = true) async {
        guard isFraudProtectionEnabled else { return }
        guard AppConfig.authToken != nil else {
            if showErrors {
                errorMessage = localizationManager.localized("antifake_error_unauthorized")
            }
            return
        }

        isRunningMonitor = true
        if showErrors {
            errorMessage = nil
            requiresPremiumUpgrade = false
        }
        defer { isRunningMonitor = false }

        do {
            let verdict = try await performCreditMonitor()
            monitorVerdict = verdict
        } catch {
            if showErrors {
                applyFailure(error)
            }
        }
    }

    private func loadStats() async {
        guard AppConfig.authToken != nil else { return }

        isLoadingStats = true
        defer { isLoadingStats = false }

        do {
            stats = try await withCheckedThrowingContinuation { continuation in
                apiService.getIdentityTheftStats { result in
                    continuation.resume(with: result)
                }
            }
        } catch {
            let networkError = NetworkError.from(error)
            if case .notFound = networkError {
                stats = nil
                return
            }
            if showStatsError(networkError) {
                applyFailure(error)
            }
        }
    }

    private func enableFraudProtection() async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            apiService.enableProtectionCategory(ThreatProtectionCategory.fraud.rawValue) { result in
                switch result {
                case .success(let response):
                    guard response.success else {
                        continuation.resume(throwing: NetworkError.apiError(response.message ?? "enable_failed", nil))
                        return
                    }
                    continuation.resume()
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
        applyLocalFraudEnabled(true)
    }

    private func disableFraudProtection() async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            apiService.disableProtectionCategory(ThreatProtectionCategory.fraud.rawValue) { result in
                switch result {
                case .success(let response):
                    guard response.success else {
                        continuation.resume(throwing: NetworkError.apiError(response.message ?? "disable_failed", nil))
                        return
                    }
                    continuation.resume()
                case .failure(let error):
                    continuation.resume(throwing: error)
                }
            }
        }
        applyLocalFraudEnabled(false)
    }

    private func performCreditMonitor() async throws -> SecurityVerdict {
        try await withCheckedThrowingContinuation { continuation in
            apiService.monitorIdentityCredit { result in
                continuation.resume(with: result)
            }
        }
    }

    private func applyLocalFraudEnabled(_ enabled: Bool) {
        var updated = protectionSettingsManager.settings
        updated.setEnabled(.fraud, enabled)
        protectionSettingsManager.settings = updated
        protectionSettingsManager.saveSettings()
    }

    private func applyFailure(_ error: Error) {
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

    private func showStatsError(_ networkError: NetworkError) -> Bool {
        switch networkError {
        case .unauthorized, .notFound:
            return false
        default:
            return networkError.isCritical || !networkError.isRetryable
        }
    }
}
