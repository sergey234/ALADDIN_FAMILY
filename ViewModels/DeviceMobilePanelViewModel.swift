import Foundation

@MainActor
final class DeviceMobilePanelViewModel: ObservableObject {

    @Published private(set) var isMobileProtectionEnabled = false
    @Published private(set) var lastScan: DeviceAgentScanResult?
    @Published var isUpdatingToggle = false
    @Published var isRunningScan = false
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
        syncMobileEnabledFromLocalSettings()
    }

    var isMobileCategoryAvailable: Bool {
        tariffManager.isCategoryAvailable(.mobileThreats)
    }

    func syncMobileEnabledFromLocalSettings() {
        isMobileProtectionEnabled = protectionSettingsManager.settings.isEnabled(.mobileThreats)
    }

    func setMobileProtectionEnabled(_ enabled: Bool) async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }
        guard isMobileCategoryAvailable else {
            requiresPremiumUpgrade = true
            errorMessage = localizationManager.localized("antifake_premium_required_body")
            syncMobileEnabledFromLocalSettings()
            return
        }
        if enabled == isMobileProtectionEnabled { return }

        isUpdatingToggle = true
        errorMessage = nil
        requiresPremiumUpgrade = false
        defer { isUpdatingToggle = false }

        do {
            if enabled {
                try await enableMobileProtection()
                isMobileProtectionEnabled = true
                await runDeviceScan()
            } else {
                try await disableMobileProtection()
                isMobileProtectionEnabled = false
            }
        } catch {
            syncMobileEnabledFromLocalSettings()
            handleError(error)
        }
    }

    func runSecurityCheck() async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }

        isRunningScan = true
        errorMessage = nil
        defer { isRunningScan = false }

        do {
            lastScan = try await withCheckedThrowingContinuation { continuation in
                apiService.runMobileSecurityCheck(deviceId: nil) { result in
                    continuation.resume(with: result)
                }
            }
        } catch {
            handleError(error)
        }
    }

    func runDeviceScan() async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }

        isRunningScan = true
        errorMessage = nil
        defer { isRunningScan = false }

        do {
            lastScan = try await withCheckedThrowingContinuation { continuation in
                apiService.runMobileDeviceScan(deviceId: nil) { result in
                    continuation.resume(with: result)
                }
            }
        } catch {
            handleError(error)
        }
    }

    private func enableMobileProtection() async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            apiService.enableProtectionCategory(ThreatProtectionCategory.mobileThreats.rawValue) { result in
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
        applyLocalMobileEnabled(true)
    }

    private func disableMobileProtection() async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            apiService.disableProtectionCategory(ThreatProtectionCategory.mobileThreats.rawValue) { result in
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
        applyLocalMobileEnabled(false)
    }

    private func applyLocalMobileEnabled(_ enabled: Bool) {
        var updated = protectionSettingsManager.settings
        updated.setEnabled(.mobileThreats, enabled)
        protectionSettingsManager.settings = updated
        protectionSettingsManager.saveSettings()
    }

    private func handleError(_ error: Error) {
        let presentation = AntifakeCheckFailureHandler.present(
            error: error,
            localizationManager: localizationManager
        )
        requiresPremiumUpgrade = presentation.requiresPremiumUpgrade
        errorMessage = presentation.errorMessage
    }
}
