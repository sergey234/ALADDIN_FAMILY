import SwiftUI

/// Last 50 antifake checks (af-m3 / af-6-08).
struct AntifakeCheckHistorySection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var entries: [AntifakeCheckHistoryEntry] = []

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Label(localizationManager.localized("antifake_history_title"), systemImage: "clock.arrow.circlepath")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                if !entries.isEmpty {
                    Button(localizationManager.localized("antifake_history_clear")) {
                        AntifakeCheckHistoryStore.clear()
                        entries = []
                    }
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primaryBlue)
                }
            }

            if entries.isEmpty {
                Text(localizationManager.localized("antifake_history_empty"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
            } else {
                ForEach(entries.prefix(10)) { entry in
                    historyRow(entry)
                }
                if entries.count > 10 {
                    Text(
                        String(
                            format: localizationManager.localized("antifake_history_more"),
                            entries.count - 10
                        )
                    )
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.65))
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .accessibilityIdentifier("antifake_history_section")
        .onAppear { entries = AntifakeCheckHistoryStore.load() }
    }

    private func historyRow(_ entry: AntifakeCheckHistoryEntry) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(entry.kind.uppercased())
                    .font(.caption2.weight(.bold))
                    .foregroundColor(.secondaryGold)
                Spacer()
                Text(entry.verdict)
                    .font(.caption2.weight(.semibold))
                    .foregroundColor(verdictColor(entry.verdict))
            }
            Text(entry.summary)
                .font(.caption)
                .foregroundColor(.white.opacity(0.9))
                .lineLimit(2)
            Text(entry.checkedAt, style: .relative)
                .font(.caption2)
                .foregroundColor(.white.opacity(0.55))
        }
        .padding(.vertical, 4)
    }

    private func verdictColor(_ verdict: String) -> Color {
        switch verdict.lowercased() {
        case "likely_fake": return .dangerRed
        case "likely_real": return .successGreen
        default: return .warningOrange
        }
    }
}

enum AntifakeHistoryRecorder {
    static func record(verdict: SecurityVerdict, kind: String, summary: String) {
        AntifakeCheckHistoryStore.append(
            kind: kind,
            summary: summary,
            verdict: verdict.verdict.rawValue
        )
    }
}
