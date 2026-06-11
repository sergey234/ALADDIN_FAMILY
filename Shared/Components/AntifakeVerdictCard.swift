import SwiftUI

/// Result card for sync antifake checks (B2-04).
struct AntifakeVerdictCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let verdict: SecurityVerdict

    private var accentColor: Color {
        switch verdict.verdict {
        case .likelyFake: return .dangerRed
        case .uncertain: return .warningOrange
        case .likelyReal: return .successGreen
        }
    }

    private var iconName: String {
        switch verdict.verdict {
        case .likelyFake: return "exclamationmark.shield.fill"
        case .uncertain: return "questionmark.circle.fill"
        case .likelyReal: return "checkmark.shield.fill"
        }
    }

    private var verdictTitleKey: String {
        switch verdict.verdict {
        case .likelyFake: return "antifake_verdict_likely_fake"
        case .uncertain: return "antifake_verdict_uncertain"
        case .likelyReal: return "antifake_verdict_likely_real"
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Label(localizationManager.localized(verdictTitleKey), systemImage: iconName)
                .font(.headline)
                .foregroundColor(.white)

            HStack {
                Text(localizationManager.localized("antifake_verdict_confidence"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.75))
                Spacer()
                Text("\(Int((verdict.confidence * 100).rounded()))%")
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(accentColor)
            }

            if !verdict.reasons.isEmpty {
                Text(localizationManager.localized("antifake_verdict_reasons"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.7))

                ForEach(Array(verdict.reasons.enumerated()), id: \.offset) { _, reason in
                    HStack(alignment: .top, spacing: Spacing.xs) {
                        Text("•")
                            .foregroundColor(accentColor)
                        Text(reason)
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.9))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
        }
        .padding(Spacing.l)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: accentColor)
        .accessibilityIdentifier("antifake_verdict_card")
    }
}
