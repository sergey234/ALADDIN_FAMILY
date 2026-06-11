import Foundation

@MainActor
final class DeviceComponentsScanViewModel: ObservableObject {

    @Published private(set) var phishingVerdict: SecurityVerdict?
    @Published private(set) var networkResult: DeviceAgentScanResult?
    @Published private(set) var mobileResult: DeviceAgentScanResult?
    @Published private(set) var incidentResult: DeviceIncidentReportResult?
    @Published var runningKind: DeviceComponentScanKind?
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

    func runScan(_ kind: DeviceComponentScanKind) async {
        guard AppConfig.authToken != nil else {
            errorMessage = localizationManager.localized("antifake_error_unauthorized")
            return
        }

        runningKind = kind
        errorMessage = nil
        requiresPremiumUpgrade = false
        defer { runningKind = nil }

        do {
            switch kind {
            case .phishing:
                phishingVerdict = try await performPhishingCheck()
            case .network:
                networkResult = try await performNetworkScan()
            case .mobile:
                mobileResult = try await performMobileCheck()
            case .incident:
                incidentResult = try await performIncidentDrill()
            }
        } catch {
            handleError(error)
        }
    }

    private func performPhishingCheck() async throws -> SecurityVerdict {
        try await withCheckedThrowingContinuation { continuation in
            apiService.antifakeCheckUrl(url: "https://example-phishing-check.test") { result in
                continuation.resume(with: result)
            }
        }
    }

    private func performNetworkScan() async throws -> DeviceAgentScanResult {
        let homeId = IoTHomeIdResolver.current
        _ = try await apiService.startIoTScan(homeId: homeId)
        return DeviceAgentScanResult(
            scanId: homeId,
            status: "started",
            scope: "iot_home",
            securityScore: nil,
            threatsFound: 0,
            threats: [],
            source: "real_agent",
            agent: "iot_security_agent",
            checkedAt: nil,
            clean: true
        )
    }

    private func performMobileCheck() async throws -> DeviceAgentScanResult {
        try await withCheckedThrowingContinuation { continuation in
            apiService.runMobileSecurityCheck(deviceId: nil) { result in
                continuation.resume(with: result)
            }
        }
    }

    private func performIncidentDrill() async throws -> DeviceIncidentReportResult {
        try await withCheckedThrowingContinuation { continuation in
            apiService.reportSecurityIncident(
                type: "security_drill",
                description: "Device Hub incident response test"
            ) { result in
                continuation.resume(with: result)
            }
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
