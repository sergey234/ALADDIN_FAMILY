import Foundation

/// B6-01 — reject mock / gateway-empty envelopes for `GET …/monitoring/detail` (pc-02).
enum ParentalMonitoringSourceValidator {
    static let mockMarkers: [String] = Array(DeviceScanSourceValidator.mockSources)
}

extension ParentalMonitoringDetailResponse {
    func validateForProduction() throws {
        let data = (try? JSONEncoder().encode(self)) ?? Data()
        let raw = String(data: data, encoding: .utf8)?.lowercased() ?? ""
        for marker in ParentalMonitoringSourceValidator.mockMarkers where raw.contains(marker) {
            throw SecurityVerdictValidationError.mockSourceRejected(marker)
        }
    }
}

enum ParentalMonitoringDetailMapper {
    static func dailyReport(from detail: ParentalMonitoringDetailResponse, date: Date = Date()) -> DailyReport {
        let totalMinutes = detail.topApps.reduce(0) { $0 + $1.usageMinutes }
        let apps = detail.topApps.map { row in
            ReportAppUsage(
                appName: row.name,
                timeSpent: TimeInterval(row.usageMinutes * 60),
                limit: TimeInterval(row.limitMinutes * 60)
            )
        }
        let blockedSites = detail.summary.browserSitesWeek
        let threats = detail.suspicious.count
        return DailyReport(
            date: date,
            totalScreenTime: TimeInterval(totalMinutes * 60),
            appsUsage: apps,
            websitesBlocked: blockedSites,
            threatsBlocked: threats
        )
    }
}
