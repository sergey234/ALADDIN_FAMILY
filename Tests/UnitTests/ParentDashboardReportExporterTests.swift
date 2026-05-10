import XCTest
@testable import ALADDIN

@MainActor
final class ParentDashboardReportExporterTests: XCTestCase {

    private func sampleModel() -> ParentDashboardReportModel {
        let day = Date(timeIntervalSince1970: 1_700_000_000)
        return ParentDashboardReportModel(
            generatedAt: day,
            reportTitle: "Test report",
            generatedLabel: "Generated",
            summarySectionTitle: "Summary",
            summaryRows: [("Opens", "3"), ("Completions", "1")],
            trendsSectionTitle: "Trends",
            trendWindowLabel: "Week",
            trendColumnDay: "Day",
            trendColumnOpens: "Opens",
            trendColumnCompletions: "Completions",
            trendColumnUsedMinutes: "Minutes",
            trendRows: [("2024-01-02", 1, 0, 5)]
        )
    }

    func testCSVWritesUTF8WithBOMAndSummary() throws {
        let url = try ParentDashboardReportExporter.buildTemporaryFile(model: sampleModel(), format: .csv)
        defer { try? FileManager.default.removeItem(at: url) }
        let raw = try Data(contentsOf: url)
        XCTAssertGreaterThan(raw.count, 40)
        XCTAssertTrue(raw.starts(with: Data([0xEF, 0xBB, 0xBF])))
        let text = String(data: raw, encoding: .utf8) ?? ""
        XCTAssertTrue(text.contains("label,value"))
        XCTAssertTrue(text.contains("Summary"))
        XCTAssertTrue(text.contains("Opens"))
    }

    func testPDFWritesNonEmptyDocument() throws {
        let url = try ParentDashboardReportExporter.buildTemporaryFile(model: sampleModel(), format: .pdf)
        defer { try? FileManager.default.removeItem(at: url) }
        let raw = try Data(contentsOf: url)
        XCTAssertGreaterThan(raw.count, 400)
        XCTAssertEqual(raw.prefix(4), Data("%PDF".utf8))
    }
}
