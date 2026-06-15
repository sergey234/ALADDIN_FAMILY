import Foundation
import UIKit

/// J-04 — export local antifake check history to shareable PDF.
enum AntifakeCheckHistoryPDFExporter {
    struct Labels {
        let title: String
        let generated: String
        let kindColumn: String
        let verdictColumn: String
        let summaryColumn: String
        let dateColumn: String
        let empty: String
    }

    static func export(entries: [AntifakeCheckHistoryEntry], labels: Labels) throws -> URL {
        let stamp = ISO8601DateFormatter().string(from: Date())
            .replacingOccurrences(of: ":", with: "-")
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("ALADDIN_antifake_history_\(stamp).pdf")

        let pageRect = CGRect(x: 0, y: 0, width: 612, height: 792)
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect)
        let bodyFont = UIFont.systemFont(ofSize: 11)
        let headerFont = UIFont.boldSystemFont(ofSize: 16)
        let metaFont = UIFont.systemFont(ofSize: 10)
        let lineHeight: CGFloat = 16
        let margin: CGFloat = 40
        let maxY = pageRect.height - margin

        try renderer.writePDF(to: url) { context in
            var y = margin
            func newPageIfNeeded(_ needed: CGFloat = lineHeight * 2) {
                if y + needed > maxY {
                    context.beginPage()
                    y = margin
                }
            }
            context.beginPage()
            (labels.title as NSString).draw(
                at: CGPoint(x: margin, y: y),
                withAttributes: [.font: headerFont]
            )
            y += lineHeight * 1.6
            let generatedLine = "\(labels.generated): \(DateFormatter.localizedString(from: Date(), dateStyle: .medium, timeStyle: .short))"
            (generatedLine as NSString).draw(
                at: CGPoint(x: margin, y: y),
                withAttributes: [.font: metaFont, .foregroundColor: UIColor.gray]
            )
            y += lineHeight * 1.4

            if entries.isEmpty {
                (labels.empty as NSString).draw(
                    at: CGPoint(x: margin, y: y),
                    withAttributes: [.font: bodyFont]
                )
                return
            }

            for entry in entries {
                newPageIfNeeded(lineHeight * 4)
                let header = "\(entry.kind.uppercased()) · \(entry.verdict)"
                (header as NSString).draw(
                    at: CGPoint(x: margin, y: y),
                    withAttributes: [.font: UIFont.boldSystemFont(ofSize: 11)]
                )
                y += lineHeight
                (entry.summary as NSString).draw(
                    in: CGRect(x: margin, y: y, width: pageRect.width - margin * 2, height: lineHeight * 2),
                    withAttributes: [.font: bodyFont]
                )
                y += lineHeight * 1.6
                let dateText = DateFormatter.localizedString(from: entry.checkedAt, dateStyle: .short, timeStyle: .short)
                (dateText as NSString).draw(
                    at: CGPoint(x: margin, y: y),
                    withAttributes: [.font: metaFont, .foregroundColor: UIColor.gray]
                )
                y += lineHeight * 1.4
            }
        }
        return url
    }
}
