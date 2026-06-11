import XCTest
@testable import ALADDIN

final class ParentalMonitoringValidationTests: XCTestCase {

    func testValidDetailPassesValidation() throws {
        let detail = ParentalMonitoringDetailResponse(
            topSites: [],
            topApps: [],
            browserHistory: [],
            appHistory: [],
            peakHours: [],
            suspicious: [],
            contacts: [],
            summary: ParentalMonitoringSummaryBlock(
                browserSitesWeek: 0,
                appsUsedWeek: 0,
                contactsActive: 0
            )
        )
        XCTAssertNoThrow(try detail.validateForProduction())
    }

    func testMockMarkerRejected() {
        let detail = ParentalMonitoringDetailResponse(
            topSites: [
                ParentalMonitoringTopSiteRow(
                    site: "sfm_mock.example",
                    visits: 1,
                    hours: 0,
                    minutes: 1,
                    category: "search"
                )
            ],
            topApps: [],
            browserHistory: [],
            appHistory: [],
            peakHours: [],
            suspicious: [],
            contacts: [],
            summary: ParentalMonitoringSummaryBlock(
                browserSitesWeek: 1,
                appsUsedWeek: 0,
                contactsActive: 0
            )
        )
        XCTAssertThrowsError(try detail.validateForProduction()) { error in
            guard case SecurityVerdictValidationError.mockSourceRejected = error else {
                return XCTFail("Expected mockSourceRejected, got \(error)")
            }
        }
    }

    func testDailyReportMapperUsesTopApps() {
        let detail = ParentalMonitoringDetailResponse(
            topSites: [],
            topApps: [
                ParentalMonitoringTopAppRow(
                    name: "TestApp",
                    usageMinutes: 30,
                    limitMinutes: 60,
                    exceeded: false
                )
            ],
            browserHistory: [],
            appHistory: [],
            peakHours: [],
            suspicious: [
                ParentalMonitoringSuspiciousRow(text: "warn", level: "high", time: "12:00")
            ],
            contacts: [],
            summary: ParentalMonitoringSummaryBlock(
                browserSitesWeek: 5,
                appsUsedWeek: 1,
                contactsActive: 0
            )
        )
        let report = ParentalMonitoringDetailMapper.dailyReport(from: detail)
        XCTAssertEqual(report.websitesBlocked, 5)
        XCTAssertEqual(report.threatsBlocked, 1)
        XCTAssertEqual(report.appsUsage.first?.appName, "TestApp")
    }
}
