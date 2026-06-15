import Foundation

/// M-01 — Antifake API routes use HTTPS `NetworkManager` with SSL pinning (same as all ALADDIN JWT traffic).
enum AntifakeTLSRouting {
    static let pinnedAPIHost = "aladdin-ai.ru"

    static let endpointPaths: [String] = [
        AppConfig.Endpoint.antifakeCheckText,
        AppConfig.Endpoint.antifakeCheckUrl,
        AppConfig.Endpoint.antifakeCheckAudio,
        AppConfig.Endpoint.antifakeCheckVideo,
        AppConfig.Endpoint.antifakeCheckDocument,
        AppConfig.Endpoint.antifakeCallAnalyze,
        AppConfig.Endpoint.antifakeMetrics,
        AppConfig.Endpoint.antifakeCallDirectory,
        AppConfig.Endpoint.antifakeReport,
        AppConfig.Endpoint.antifakeAppeal,
        AppConfig.Endpoint.antifakeWhitelist,
        AppConfig.Endpoint.antifakeFamilyPushToken,
        AppConfig.Endpoint.antifakeFamilyReports,
        AppConfig.Endpoint.antifakeFamilyCDStatus
    ]

    /// Production antifake traffic must go through pinned HTTPS host (not raw IP HTTP).
    static func validatesProductionRouting(baseURL: String = AppConfig.apiBaseURL) -> Bool {
        guard let url = URL(string: baseURL),
              url.scheme?.lowercased() == "https",
              let host = url.host?.lowercased()
        else {
            return false
        }
        return host == pinnedAPIHost
    }

    static func allEndpointsAreRelativeAntifakePaths() -> Bool {
        endpointPaths.allSatisfy { $0.hasPrefix("/api/antifake/") }
    }
}
