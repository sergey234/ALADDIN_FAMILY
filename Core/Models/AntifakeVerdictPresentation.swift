import Foundation
import SwiftUI

/// Display layer for antifake verdicts — maps API `fake_risk` / `confidence` to clear UI copy.
struct AntifakeVerdictPresentation: Equatable, Sendable {
    let verdict: SecurityVerdict

    /// Canonical fake probability from API (`fake_risk` == `confidence`).
    var fakeRisk: Double {
        min(max(verdict.fakeRisk, 0), 1)
    }

    var riskPercent: Int {
        Int((fakeRisk * 100).rounded())
    }

    var showsRiskMeter: Bool {
        verdict.verdict != .insufficientData
    }

    var riskLevelKey: String {
        if fakeRisk < 0.35 { return "antifake_risk_low" }
        if fakeRisk < 0.65 { return "antifake_risk_medium" }
        return "antifake_risk_high"
    }

    var verdictTitleKey: String {
        switch verdict.verdict {
        case .likelyFake: return "antifake_verdict_likely_fake"
        case .uncertain: return "antifake_verdict_uncertain"
        case .likelyReal: return "antifake_verdict_likely_real"
        case .insufficientData: return "antifake_verdict_insufficient_data"
        }
    }

    var sourceBadgeKey: String {
        let normalized = verdict.source.lowercased()
        if normalized.contains("probe")
            || (normalized.contains("heuristic") && !normalized.contains("local_ml")) {
            return "antifake_verdict_source_probe"
        }
        if normalized.contains("real")
            || normalized.contains("agent")
            || normalized.contains("sfm")
            || normalized.contains("local_ml") {
            return "antifake_verdict_source_ai"
        }
        return "antifake_verdict_source_rules"
    }

    var accentColor: Color {
        switch verdict.verdict {
        case .likelyFake: return .dangerRed
        case .uncertain: return .warningOrange
        case .likelyReal: return .successGreen
        case .insufficientData: return .warningOrange
        }
    }

    var iconName: String {
        switch verdict.verdict {
        case .likelyFake: return "exclamationmark.shield.fill"
        case .uncertain: return "questionmark.circle.fill"
        case .likelyReal: return "checkmark.shield.fill"
        case .insufficientData: return "text.badge.minus"
        }
    }

    func localizedReason(_ reason: String, localizationManager: LocalizationManager) -> String {
        let trimmed = reason.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return reason }
        let key = "antifake_reason_\(trimmed)"
        let localized = localizationManager.localized(key)
        return localized == key ? trimmed : localized
    }
}

extension SecurityVerdict {
    var fakeRisk: Double {
        confidence
    }

    var presentation: AntifakeVerdictPresentation {
        AntifakeVerdictPresentation(verdict: self)
    }
}
