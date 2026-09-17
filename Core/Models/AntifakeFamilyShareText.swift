import Foundation

/// afhub-p2-04 — plain-text payload for one-tap «share with family».
enum AntifakeFamilyShareText {
    static func build(
        verdict: SecurityVerdict,
        localizationManager: LocalizationManager
    ) -> String {
        let title = localizationManager.localized(verdict.presentation.verdictTitleKey)
        let pct = verdict.presentation.riskPercent
        let header = localizationManager.localized("antifake_share_family_header")

        var lines: [String] = [
            header,
            "",
            "\(title) · \(pct)%",
        ]

        if let summary = verdict.summaryHuman?.trimmingCharacters(in: .whitespacesAndNewlines),
           !summary.isEmpty {
            lines.append("")
            lines.append(summary)
        }

        let reasons: [String]
        if !verdict.reasonsHuman.isEmpty {
            reasons = Array(verdict.reasonsHuman.prefix(3))
        } else {
            reasons = Array(verdict.reasons.prefix(3)).map { raw in
                verdict.presentation.localizedReason(raw, localizationManager: localizationManager)
            }
        }
        if !reasons.isEmpty {
            lines.append("")
            lines.append(localizationManager.localized("antifake_share_family_reasons_title"))
            for reason in reasons {
                lines.append("• \(reason)")
            }
        }

        lines.append("")
        lines.append(localizationManager.localized("antifake_share_family_footer"))
        return lines.joined(separator: "\n")
    }
}
