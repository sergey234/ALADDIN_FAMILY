import Foundation
import UIKit

enum ParentalMonitoringReportFormat {
    case csv
    case pdf
}

/// B6-03 — localized parental monitoring snapshot for PDF/CSV export.
struct ParentalMonitoringReportModel {
    let generatedAt: Date
    let reportTitle: String
    let generatedLabel: String
    let summarySectionTitle: String
    let summaryRows: [(label: String, value: String)]
    let topSitesSectionTitle: String
    let topSiteRows: [(site: String, visits: String, duration: String)]
    let topAppsSectionTitle: String
    let topAppRows: [(name: String, usage: String, limit: String)]
    let suspiciousSectionTitle: String
    let suspiciousRows: [String]
}

enum ParentalMonitoringReportExporter {
    static func buildTemporaryFile(model: ParentalMonitoringReportModel, format: ParentalMonitoringReportFormat) throws -> URL {
        let stamp = fileStamp(model.generatedAt)
        switch format {
        case .csv:
            return try writeCSV(model, stamp: stamp)
        case .pdf:
            return try writePDF(model, stamp: stamp)
        }
    }

    private static func fileStamp(_ date: Date) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withFullDate, .withTime, .withDashSeparatorInDate, .withColonSeparatorInTime]
        return formatter.string(from: date)
            .replacingOccurrences(of: ":", with: "-")
    }

    private static func composePlainText(from model: ParentalMonitoringReportModel) -> String {
        var lines: [String] = []
        lines.append(model.reportTitle)
        lines.append("\(model.generatedLabel): \(ISO8601DateFormatter().string(from: model.generatedAt))")
        lines.append("")
        lines.append(model.summarySectionTitle)
        for row in model.summaryRows {
            lines.append("\(row.label): \(row.value)")
        }
        lines.append("")
        lines.append(model.topSitesSectionTitle)
        for row in model.topSiteRows {
            lines.append("\(row.site)\t\(row.visits)\t\(row.duration)")
        }
        lines.append("")
        lines.append(model.topAppsSectionTitle)
        for row in model.topAppRows {
            lines.append("\(row.name)\t\(row.usage)\t\(row.limit)")
        }
        lines.append("")
        lines.append(model.suspiciousSectionTitle)
        for row in model.suspiciousRows {
            lines.append("• \(row)")
        }
        return lines.joined(separator: "\n")
    }

    private static func writeCSV(_ model: ParentalMonitoringReportModel, stamp: String) throws -> URL {
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("ALADDIN_parental_monitoring_\(stamp).csv")
        var parts: [String] = ["\u{FEFF}"]
        parts.append(csvLine([model.reportTitle]))
        parts.append(csvLine([model.generatedLabel, ISO8601DateFormatter().string(from: model.generatedAt)]))
        parts.append("")
        parts.append(csvLine([model.summarySectionTitle]))
        parts.append("label,value")
        for row in model.summaryRows {
            parts.append(csvLine([row.label, row.value]))
        }
        parts.append("")
        parts.append(csvLine([model.topSitesSectionTitle]))
        parts.append("site,visits,duration")
        for row in model.topSiteRows {
            parts.append(csvLine([row.site, row.visits, row.duration]))
        }
        parts.append("")
        parts.append(csvLine([model.topAppsSectionTitle]))
        parts.append("app,usage,limit")
        for row in model.topAppRows {
            parts.append(csvLine([row.name, row.usage, row.limit]))
        }
        parts.append("")
        parts.append(csvLine([model.suspiciousSectionTitle]))
        for row in model.suspiciousRows {
            parts.append(csvLine([row]))
        }
        try parts.joined(separator: "\n").data(using: .utf8)?.write(to: url, options: .atomic)
        guard FileManager.default.fileExists(atPath: url.path) else {
            throw NSError(domain: "ParentalMonitoringReportExporter", code: 1, userInfo: nil)
        }
        return url
    }

    private static func writePDF(_ model: ParentalMonitoringReportModel, stamp: String) throws -> URL {
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("ALADDIN_parental_monitoring_\(stamp).pdf")
        let pageRect = CGRect(x: 0, y: 0, width: 595, height: 842)
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect)
        let lines = composePlainText(from: model)
            .split(separator: "\n", omittingEmptySubsequences: false)
            .map(String.init)
        let data = renderer.pdfData { ctx in
            ctx.beginPage()
            var y: CGFloat = 36
            let attrs: [NSAttributedString.Key: Any] = [
                .font: UIFont.monospacedSystemFont(ofSize: 9, weight: .regular)
            ]
            for line in lines {
                if y > pageRect.height - 36 {
                    ctx.beginPage()
                    y = 36
                }
                (line as NSString).draw(at: CGPoint(x: 36, y: y), withAttributes: attrs)
                y += 13
            }
        }
        try data.write(to: url, options: .atomic)
        return url
    }

    private static func csvLine(_ fields: [String]) -> String {
        fields.map(csvEscape).joined(separator: ",")
    }

    private static func csvEscape(_ value: String) -> String {
        if value.contains(",") || value.contains("\"") || value.contains("\n") || value.contains("\r") {
            return "\"" + value.replacingOccurrences(of: "\"", with: "\"\"") + "\""
        }
        return value
    }
}
