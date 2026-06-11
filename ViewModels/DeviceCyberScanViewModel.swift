import Foundation

@MainActor
final class DeviceCyberScanViewModel: ObservableObject {

    @Published private(set) var lastScan: DeviceAgentScanResult?
    @Published private(set) var eicarDetected = false
    @Published private(set) var serverThreatCount = 0
    @Published private(set) var protectionStats: ProtectionStatsResponse?
    @Published var isRunningQuickScan = false
    @Published var isRunningEicarTest = false
    @Published var isLoadingStats = false
    @Published var errorMessage: String?
    @Published var requiresPremiumUpgrade = false

    private let apiService: APIService
    private let localizationManager: LocalizationManager
    private let tariffManager: TariffManager

    init(
        apiService: APIService? = nil,
        localizationManager: LocalizationManager = LocalizationManager(),
        tariffManager: TariffManager? = nil
    ) {
        self.apiService = apiService ?? APIService.shared
        self.localizationManager = localizationManager
        self.tariffManager = tariffManager ?? TariffManager.shared
    }

    var isCyberCategoryAvailable: Bool {
        tariffManager.isCategoryAvailable(.cyberThreats)
    }

    func refresh() async {
        await loadProtectionStats()
        await refreshServerThreatCount()
    }

    func runQuickScan() async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }
        guard isCyberCategoryAvailable else {
            requiresPremiumUpgrade = true
            errorMessage = localizationManager.localized("antifake_premium_required_body")
            return
        }

        isRunningQuickScan = true
        errorMessage = nil
        requiresPremiumUpgrade = false
        defer { isRunningQuickScan = false }

        do {
            lastScan = try await performQuickScan()
        } catch {
            handleError(error)
        }
    }

    func runEicarTest() async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }

        isRunningEicarTest = true
        errorMessage = nil
        requiresPremiumUpgrade = false
        defer { isRunningEicarTest = false }

        do {
            let response = try await apiService.runEicarTestScan()
            eicarDetected = response.clean == false
            if let threats = response.threatsFound, !threats.isEmpty {
                lastScan = DeviceAgentScanResult(
                    scanId: nil,
                    status: eicarDetected ? "threat_found" : "clean",
                    scope: "eicar",
                    securityScore: eicarDetected ? 40 : 100,
                    threatsFound: threats.count,
                    threats: threats.compactMap { dto in
                        guard let id = dto.id ?? dto.name else { return nil }
                        return DeviceScanThreatItem(
                            id: id,
                            name: dto.name,
                            type: dto.type,
                            severity: dto.severity,
                            description: dto.description,
                            confidence: dto.confidence
                        )
                    },
                    source: "real_agent",
                    agent: "malware_detection_agent",
                    checkedAt: nil,
                    clean: response.clean
                )
            }
        } catch {
            handleError(error)
        }
    }

    private func performQuickScan() async throws -> DeviceAgentScanResult {
        try await withCheckedThrowingContinuation { continuation in
            apiService.runMalwareQuickScan { result in
                continuation.resume(with: result)
            }
        }
    }

    private func loadProtectionStats() async {
        isLoadingStats = true
        defer { isLoadingStats = false }

        do {
            protectionStats = try await withCheckedThrowingContinuation { continuation in
                apiService.getProtectionStats { result in
                    continuation.resume(with: result)
                }
            }
        } catch {
            // Stats are supplementary — keep scan UX usable.
            print("⚠️ DeviceCyberScanViewModel stats: \(error.localizedDescription)")
        }
    }

    private func refreshServerThreatCount() async {
        do {
            let threats = try await apiService.getUserThreatsAsync(status: nil)
            serverThreatCount = threats.count
        } catch {
            serverThreatCount = 0
        }
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
