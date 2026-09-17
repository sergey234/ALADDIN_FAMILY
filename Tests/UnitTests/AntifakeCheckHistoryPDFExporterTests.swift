import XCTest
@testable import ALADDIN

final class AntifakeCheckHistoryPDFExporterTests: XCTestCase {
    func testExportCreatesNonEmptyPDF() throws {
        let entries = [
            AntifakeCheckHistoryEntry(
                kind: "text",
                summary: "Тестовая проверка SMS",
                verdict: "likely_fake"
            )
        ]
        let labels = AntifakeCheckHistoryPDFExporter.Labels(
            title: "Test",
            generated: "Generated",
            kindColumn: "Kind",
            verdictColumn: "Verdict",
            summaryColumn: "Summary",
            dateColumn: "Date",
            empty: "Empty"
        )
        let url = try AntifakeCheckHistoryPDFExporter.export(entries: entries, labels: labels)
        defer { try? FileManager.default.removeItem(at: url) }
        let data = try Data(contentsOf: url)
        XCTAssertGreaterThan(data.count, 100)
        XCTAssertTrue(String(data: data.prefix(4), encoding: .ascii) == "%PDF")
    }
}
