import Foundation
import UIKit

enum ParentDashboardReportFormat {
    case csv
    case pdf
}

/// Localized strings and numeric fields assembled on the main thread before export.
struct ParentDashboardReportModel {
    let generatedAt: Date
    let reportTitle: String
    let generatedLabel: String
    let summarySectionTitle: String
    let summaryRows: [(label: String, value: String)]
    let trendsSectionTitle: String
    let trendWindowLabel: String
    let trendColumnDay: String
    let trendColumnOpens: String
    let trendColumnCompletions: String
    let trendColumnUsedMinutes: String
    let trendRows: [(day: String, opens: Int, completions: Int, usedMinutes: Int)]
}

enum ParentDashboardReportExporter {
    static func buildTemporaryFile(model: ParentDashboardReportModel, format: ParentDashboardReportFormat) throws -> URL {
        let stamp = fileStamp(model.generatedAt)
        switch format {
        case .csv:
            return try writeCSV(model, stamp: stamp)
        case .pdf:
            return try writePDF(model, stamp: stamp)
        }
    }

    private static func fileStamp(_ date: Date) -> String {
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withFullDate, .withTime, .withDashSeparatorInDate, .withColonSeparatorInTime]
        return f.string(from: date)
            .replacingOccurrences(of: ":", with: "-")
    }

    private static func composePlainText(from model: ParentDashboardReportModel) -> String {
        var lines: [String] = []
        lines.append(model.reportTitle)
        lines.append("\(model.generatedLabel): \(ISO8601DateFormatter().string(from: model.generatedAt))")
        lines.append("")
        lines.append(model.summarySectionTitle)
        for row in model.summaryRows {
            lines.append("\(row.label): \(row.value)")
        }
        lines.append("")
        lines.append(model.trendsSectionTitle)
        lines.append("\(model.trendWindowLabel)")
        lines.append("\(model.trendColumnDay)\t\(model.trendColumnOpens)\t\(model.trendColumnCompletions)\t\(model.trendColumnUsedMinutes)")
        for r in model.trendRows {
            lines.append("\(r.day)\t\(r.opens)\t\(r.completions)\t\(r.usedMinutes)")
        }
        return lines.joined(separator: "\n")
    }

    private static func writeCSV(_ model: ParentDashboardReportModel, stamp: String) throws -> URL {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("ALADDIN_parent_report_\(stamp).csv")
        var parts: [String] = []
        parts.append("\u{FEFF}")
        parts.append(csvLine([model.reportTitle]))
        parts.append(csvLine([model.generatedLabel, ISO8601DateFormatter().string(from: model.generatedAt)]))
        parts.append("")
        parts.append(csvLine([model.summarySectionTitle]))
        parts.append("label,value")
        for row in model.summaryRows {
            parts.append(csvLine([row.label, row.value]))
        }
        parts.append("")
        parts.append(csvLine([model.trendsSectionTitle]))
        parts.append(csvLine([model.trendWindowLabel]))
        parts.append(csvLine([model.trendColumnDay, model.trendColumnOpens, model.trendColumnCompletions, model.trendColumnUsedMinutes]))
        for r in model.trendRows {
            parts.append(csvLine([r.day, "\(r.opens)", "\(r.completions)", "\(r.usedMinutes)"]))
        }
        let data = parts.joined(separator: "\n").data(using: .utf8) ?? Data()
        try data.write(to: url, options: .atomic)
        return url
    }

    private static func csvLine(_ fields: [String]) -> String {
        fields.map(csvEscape).joined(separator: ",")
    }

    private static func csvEscape(_ s: String) -> String {
        if s.contains(",") || s.contains("\"") || s.contains("\n") || s.contains("\r") {
            return "\"" + s.replacingOccurrences(of: "\"", with: "\"\"") + "\""
        }
        return s
    }

    private static func writePDF(_ model: ParentDashboardReportModel, stamp: String) throws -> URL {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent("ALADDIN_parent_report_\(stamp).pdf")
        let pageRect = CGRect(x: 0, y: 0, width: 595, height: 842)
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect)
        let lines = composePlainText(from: model).split(separator: "\n", omittingEmptySubsequences: false).map(String.init)
        let data = renderer.pdfData { ctx in
            ctx.beginPage()
            var y: CGFloat = 36
            let x: CGFloat = 36
            let attrs: [NSAttributedString.Key: Any] = [.font: UIFont.monospacedSystemFont(ofSize: 9, weight: .regular)]
            for line in lines {
                if y > pageRect.height - 36 {
                    ctx.beginPage()
                    y = 36
                }
                (line as NSString).draw(at: CGPoint(x: x, y: y), withAttributes: attrs)
                y += 13
            }
        }
        try data.write(to: url, options: .atomic)
        return url
    }
}
