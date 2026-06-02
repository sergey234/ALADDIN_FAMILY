import Foundation
import PDFKit
import UIKit

/// p3-19 — Weekly «Мой прогресс» PDF from timeline + labels API.
enum WellnessProgressPDFService {
    @MainActor
    static func generateWeeklyPDF(
        timeline: WellnessTimelineResponse,
        labels: [String: String],
        locale: LocalizationManager
    ) -> URL? {
        let title = labels["title"] ?? locale.localized(WellnessProgressPDFL10n.titleKey)
        let disclaimer = labels["disclaimer"] ?? locale.localized(WellnessProgressPDFL10n.disclaimerKey)
        let pageRect = CGRect(x: 0, y: 0, width: 612, height: 792)
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect)
        let data = renderer.pdfData { ctx in
            ctx.beginPage()
            let attrs: [NSAttributedString.Key: Any] = [
                .font: UIFont.systemFont(ofSize: 18, weight: .bold),
            ]
            title.draw(at: CGPoint(x: 40, y: 40), withAttributes: attrs)
            let bodyAttrs: [NSAttributedString.Key: Any] = [
                .font: UIFont.systemFont(ofSize: 12),
            ]
            var y: CGFloat = 80
            disclaimer.draw(
                in: CGRect(x: 40, y: y, width: 532, height: 40),
                withAttributes: bodyAttrs
            )
            y += 50
            let checkinsLabel = labels["section_checkins"]
                ?? locale.localized(WellnessProgressPDFL10n.sectionCheckinsKey)
            "\(checkinsLabel): \(timeline.checkins.count)".draw(
                at: CGPoint(x: 40, y: y),
                withAttributes: bodyAttrs
            )
            y += 24
            let exercisesLabel = labels["section_outcomes"]
                ?? locale.localized(WellnessProgressPDFL10n.sectionOutcomesKey)
            "\(exercisesLabel): \(timeline.exercises.count)".draw(
                at: CGPoint(x: 40, y: y),
                withAttributes: bodyAttrs
            )
            y += 32
            for checkin in timeline.checkins.prefix(14) {
                let line = "• \(checkin.moodEmoji ?? "—") — \(checkin.day)"
                line.draw(at: CGPoint(x: 48, y: y), withAttributes: bodyAttrs)
                y += 18
                if y > 720 { break }
            }
        }
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("wellness_progress_\(Int(Date().timeIntervalSince1970)).pdf")
        do {
            try data.write(to: url)
            return url
        } catch {
            return nil
        }
    }
}
