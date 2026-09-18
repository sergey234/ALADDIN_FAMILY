import SwiftUI

/// VSL-C P2 — weekly digest sheet.
struct VoiceWeeklyDigestSheet: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss

    let result: VoiceWeeklyDigestResult

    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .warm).ignoresSafeArea()
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(alignment: .leading, spacing: 14) {
                        Text(result.weekLabel)
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))

                        VStack(alignment: .leading, spacing: 6) {
                            Text(localizationManager.localized("voice_weekly_digest_stats"))
                                .font(.subheadline.weight(.semibold))
                            statRow("voice_day_recap_stats_security", result.stats.securityChecks)
                            statRow("voice_day_recap_stats_incidents", result.stats.incidents)
                            statRow("voice_day_recap_stats_ideas", result.stats.ideas)
                            statRow("voice_day_recap_stats_reminds", result.stats.reminds)
                            statRow("voice_day_recap_stats_notes", result.stats.notes)
                        }
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.08))
                        .cornerRadius(10)

                        if !result.topLines.isEmpty {
                            Text(localizationManager.localized("voice_weekly_digest_highlights"))
                                .font(.subheadline.weight(.semibold))
                            ForEach(Array(result.topLines.enumerated()), id: \.offset) { _, line in
                                Text("• \(line)")
                                    .font(.subheadline)
                            }
                        } else {
                            Text(localizationManager.localized("voice_weekly_digest_empty"))
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.6))
                        }
                    }
                    .padding()
                }
            }
            .foregroundColor(.white)
            .navigationTitle(localizationManager.localized("voice_weekly_digest_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(localizationManager.localized("common_close")) { dismiss() }
                }
            }
        }
        .accessibilityIdentifier("voice_weekly_digest_sheet")
    }

    @ViewBuilder
    private func statRow(_ key: String, _ value: Int) -> some View {
        if value > 0 {
            Text(localizationManager.localized(key, value))
                .font(.subheadline)
        }
    }
}
