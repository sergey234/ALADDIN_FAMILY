import Foundation

@MainActor
final class DeviceIoTPanelViewModel: ObservableObject {

    @Published private(set) var devicesCount = 0
    @Published private(set) var threatsCount = 0
    @Published private(set) var protectionLevel = 0
    @Published private(set) var threats: [IoTThreat] = []
    @Published private(set) var isIoTProtectionEnabled = false
    @Published var isLoading = false
    @Published var isScanning = false
    @Published var fixingThreatId: String?
    @Published var errorMessage: String?
    @Published var requiresPremiumUpgrade = false

    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private let protectionSettingsManager: ProtectionSettingsManager
    private let tariffManager: TariffManager
    private let module: IoTSecurityModule

    init(
        apiService: APIService? = nil,
        localizationManager: LocalizationManager = LocalizationManager(),
        protectionSettingsManager: ProtectionSettingsManager? = nil,
        tariffManager: TariffManager? = nil,
        module: IoTSecurityModule? = nil
    ) {
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
        self.protectionSettingsManager = protectionSettingsManager ?? ProtectionSettingsManager.shared
        self.tariffManager = tariffManager ?? TariffManager.shared
        self.module = module ?? IoTSecurityModule()
        syncIoTEnabledFromLocalSettings()
    }

    var homeId: String { IoTHomeIdResolver.current }

    var isIoTCategoryAvailable: Bool {
        tariffManager.isCategoryAvailable(.iotThreats)
    }

    func syncIoTEnabledFromLocalSettings() {
        isIoTProtectionEnabled = protectionSettingsManager.settings.isEnabled(.iotThreats)
    }

    func refresh() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            try await module.loadStatus(homeId: homeId)
            devicesCount = module.iotDevices.count
            threats = module.threatsDetected
            threatsCount = module.threatsDetected.count
            protectionLevel = module.protectionLevel
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func runHomeScan() async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }

        isScanning = true
        errorMessage = nil
        defer { isScanning = false }

        do {
            _ = try await apiService.startIoTScan(homeId: homeId)
            await refresh()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func fixThreat(_ threatId: String) async {
        fixingThreatId = threatId
        errorMessage = nil
        defer { fixingThreatId = nil }

        do {
            _ = try await module.fixThreat(threatId: threatId)
            await refresh()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func setIoTProtectionEnabled(_ enabled: Bool) async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }
        guard isIoTCategoryAvailable else {
            requiresPremiumUpgrade = true
            errorMessage = localizationManager.localized("antifake_premium_required_body")
            syncIoTEnabledFromLocalSettings()
            return
        }
        if enabled == isIoTProtectionEnabled { return }

        errorMessage = nil
        requiresPremiumUpgrade = false

        do {
            if enabled {
                try await enableIoTProtection()
                isIoTProtectionEnabled = true
                await runHomeScan()
            } else {
                try await disableIoTProtection()
                isIoTProtectionEnabled = false
            }
        } catch {
            syncIoTEnabledFromLocalSettings()
            handleError(error)
        }
    }

    private func enableIoTProtection() async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            apiService.enableProtectionCategory(ThreatProtectionCategory.iotThreats.rawValue) { result in
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
        applyLocalIoTEnabled(true)
    }

    private func disableIoTProtection() async throws {
        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            apiService.disableProtectionCategory(ThreatProtectionCategory.iotThreats.rawValue) { result in
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
        applyLocalIoTEnabled(false)
    }

    private func applyLocalIoTEnabled(_ enabled: Bool) {
        var updated = protectionSettingsManager.settings
        updated.setEnabled(.iotThreats, enabled)
        protectionSettingsManager.settings = updated
        protectionSettingsManager.saveSettings()
    }

    private func handleError(_ error: Error) {
        let gateOutcome = PremiumGateHandler.outcome(from: error)
        if gateOutcome.requiresUpgrade {
            requiresPremiumUpgrade = true
            errorMessage = gateOutcome.premiumMessage
                ?? localizationManager.localized("antifake_premium_required_body")
            return
        }
        requiresPremiumUpgrade = false
        switch NetworkError.from(error) {
        case .notFound:
            errorMessage = localizationManager.localized("device_hub_iot_not_found")
        default:
            errorMessage = localizationManager.localized("device_hub_iot_enable_failed")
        }
    }
}
