import Foundation

/// 📊 Parental Control Reports Manager
/// B6-03 — reports derived from `GET …/monitoring/detail` + PDF/CSV export.
@MainActor
class ParentalControlReportsManager {
    static let shared = ParentalControlReportsManager()

    private let apiService = APIService.shared

    private init() {}

    // MARK: - Daily Reports

    func getDailyReport(childId: String, date: Date = Date()) async -> Result<DailyReport, Error> {
        await fetchMonitoringReport(childId: childId, date: date)
    }

    // MARK: - Weekly Reports

    func getWeeklyReport(childId: String, weekStartDate: Date = Date()) async -> Result<WeeklyReport, Error> {
        let daily = await getDailyReport(childId: childId, date: weekStartDate)
        switch daily {
        case .success(let report):
            let total = report.totalScreenTime
            return .success(
                WeeklyReport(
                    weekStartDate: weekStartDate,
                    dailyReports: [report],
                    totalScreenTime: total,
                    averageScreenTime: total
                )
            )
        case .failure(let error):
            return .failure(error)
        }
    }

    // MARK: - Monthly Reports

    func getMonthlyReport(childId: String, month: Int, year: Int) async -> Result<MonthlyReport, Error> {
        let daily = await getDailyReport(childId: childId)
        switch daily {
        case .success(let report):
            let weekly = WeeklyReport(
                weekStartDate: Date(),
                dailyReports: [report],
                totalScreenTime: report.totalScreenTime,
                averageScreenTime: report.totalScreenTime
            )
            return .success(
                MonthlyReport(
                    month: month,
                    year: year,
                    weeklyReports: [weekly],
                    totalScreenTime: report.totalScreenTime,
                    topApps: report.appsUsage
                )
            )
        case .failure(let error):
            return .failure(error)
        }
    }

    // MARK: - Export Reports

    func exportMonitoringDetailToPDF(
        _ detail: ParentalMonitoringDetailResponse,
        labels: ParentalMonitoringReportLabels
    ) -> URL? {
        let model = buildReportModel(from: detail, labels: labels)
        return try? ParentalMonitoringReportExporter.buildTemporaryFile(model: model, format: .pdf)
    }

    func exportMonitoringDetailToCSV(
        _ detail: ParentalMonitoringDetailResponse,
        labels: ParentalMonitoringReportLabels
    ) -> URL? {
        let model = buildReportModel(from: detail, labels: labels)
        return try? ParentalMonitoringReportExporter.buildTemporaryFile(model: model, format: .csv)
    }

    func exportReportToPDF(_ report: DailyReport, labels: ParentalMonitoringReportLabels) -> URL? {
        let model = ParentalMonitoringReportModel(
            generatedAt: Date(),
            reportTitle: labels.reportTitle,
            generatedLabel: labels.generatedLabel,
            summarySectionTitle: labels.summarySectionTitle,
            summaryRows: [
                (labels.screenTimeLabel, formatDuration(report.totalScreenTime)),
                (labels.websitesBlockedLabel, "\(report.websitesBlocked)"),
                (labels.threatsBlockedLabel, "\(report.threatsBlocked)")
            ],
            topSitesSectionTitle: labels.topSitesSectionTitle,
            topSiteRows: [],
            topAppsSectionTitle: labels.topAppsSectionTitle,
            topAppRows: report.appsUsage.map {
                (name: $0.appName, usage: formatDuration($0.timeSpent), limit: formatDuration($0.limit))
            },
            suspiciousSectionTitle: labels.suspiciousSectionTitle,
            suspiciousRows: []
        )
        return try? ParentalMonitoringReportExporter.buildTemporaryFile(model: model, format: .pdf)
    }

    func exportReportToCSV(_ report: DailyReport, labels: ParentalMonitoringReportLabels) -> URL? {
        let model = ParentalMonitoringReportModel(
            generatedAt: Date(),
            reportTitle: labels.reportTitle,
            generatedLabel: labels.generatedLabel,
            summarySectionTitle: labels.summarySectionTitle,
            summaryRows: [
                (labels.screenTimeLabel, formatDuration(report.totalScreenTime)),
                (labels.websitesBlockedLabel, "\(report.websitesBlocked)"),
                (labels.threatsBlockedLabel, "\(report.threatsBlocked)")
            ],
            topSitesSectionTitle: labels.topSitesSectionTitle,
            topSiteRows: [],
            topAppsSectionTitle: labels.topAppsSectionTitle,
            topAppRows: report.appsUsage.map {
                (name: $0.appName, usage: formatDuration($0.timeSpent), limit: formatDuration($0.limit))
            },
            suspiciousSectionTitle: labels.suspiciousSectionTitle,
            suspiciousRows: []
        )
        return try? ParentalMonitoringReportExporter.buildTemporaryFile(model: model, format: .csv)
    }

    // MARK: - Private Helpers

    private func fetchMonitoringReport(childId: String, date: Date) async -> Result<DailyReport, Error> {
        await withCheckedContinuation { continuation in
            apiService.getParentalMonitoringDetail(childId: childId.isEmpty ? nil : childId) { result in
                switch result {
                case .success(let detail):
                    continuation.resume(returning: .success(ParentalMonitoringDetailMapper.dailyReport(from: detail, date: date)))
                case .failure(let error):
                    continuation.resume(returning: .failure(error))
                }
            }
        }
    }

    private func buildReportModel(
        from detail: ParentalMonitoringDetailResponse,
        labels: ParentalMonitoringReportLabels
    ) -> ParentalMonitoringReportModel {
        let summary = detail.summary
        let totalMinutes = detail.topApps.reduce(0) { $0 + $1.usageMinutes }
        return ParentalMonitoringReportModel(
            generatedAt: Date(),
            reportTitle: labels.reportTitle,
            generatedLabel: labels.generatedLabel,
            summarySectionTitle: labels.summarySectionTitle,
            summaryRows: [
                (labels.browserSitesLabel, "\(summary.browserSitesWeek)"),
                (labels.appsUsedLabel, "\(summary.appsUsedWeek)"),
                (labels.contactsActiveLabel, "\(summary.contactsActive)"),
                (labels.screenTimeLabel, formatDuration(TimeInterval(totalMinutes * 60)))
            ],
            topSitesSectionTitle: labels.topSitesSectionTitle,
            topSiteRows: detail.topSites.map { row in
                (
                    site: row.site,
                    visits: "\(row.visits)",
                    duration: "\(row.hours)h \(row.minutes)m"
                )
            },
            topAppsSectionTitle: labels.topAppsSectionTitle,
            topAppRows: detail.topApps.map { row in
                (
                    name: row.name,
                    usage: "\(row.usageMinutes) min",
                    limit: "\(row.limitMinutes) min"
                )
            },
            suspiciousSectionTitle: labels.suspiciousSectionTitle,
            suspiciousRows: detail.suspicious.map { "\($0.text) (\($0.level)) \($0.time)" }
        )
    }

    private func formatDuration(_ interval: TimeInterval) -> String {
        let minutes = max(0, Int(interval / 60))
        let hours = minutes / 60
        let mins = minutes % 60
        if hours == 0 { return "\(mins) min" }
        if mins == 0 { return "\(hours) h" }
        return "\(hours) h \(mins) min"
    }
}

struct ParentalMonitoringReportLabels {
    let reportTitle: String
    let generatedLabel: String
    let summarySectionTitle: String
    let browserSitesLabel: String
    let appsUsedLabel: String
    let contactsActiveLabel: String
    let screenTimeLabel: String
    let websitesBlockedLabel: String
    let threatsBlockedLabel: String
    let topSitesSectionTitle: String
    let topAppsSectionTitle: String
    let suspiciousSectionTitle: String
}

// MARK: - Report Models

/// Ежедневный отчёт о деятельности ребёнка
struct DailyReport: Codable {
    let date: String
    let totalScreenTime: TimeInterval
    let appsUsage: [ReportAppUsage]
    let websitesBlocked: Int
    let threatsBlocked: Int

    init(date: Date, totalScreenTime: TimeInterval, appsUsage: [ReportAppUsage], websitesBlocked: Int, threatsBlocked: Int) {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        self.date = formatter.string(from: date)
        self.totalScreenTime = totalScreenTime
        self.appsUsage = appsUsage
        self.websitesBlocked = websitesBlocked
        self.threatsBlocked = threatsBlocked
    }
}

struct ReportAppUsage: Codable {
    let appName: String
    let timeSpent: TimeInterval
    let limit: TimeInterval
}

struct WeeklyReport: Codable {
    let weekStartDate: String
    let dailyReports: [DailyReport]
    let totalScreenTime: TimeInterval
    let averageScreenTime: TimeInterval

    init(weekStartDate: Date, dailyReports: [DailyReport], totalScreenTime: TimeInterval, averageScreenTime: TimeInterval) {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        self.weekStartDate = formatter.string(from: weekStartDate)
        self.dailyReports = dailyReports
        self.totalScreenTime = totalScreenTime
        self.averageScreenTime = averageScreenTime
    }
}

struct MonthlyReport: Codable {
    let month: Int
    let year: Int
    let weeklyReports: [WeeklyReport]
    let totalScreenTime: TimeInterval
    let topApps: [ReportAppUsage]
}
