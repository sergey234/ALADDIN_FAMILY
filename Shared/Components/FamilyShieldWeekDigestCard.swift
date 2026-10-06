import SwiftUI

/// fsl-14 — карточка недельного дайджеста на экране Семья.
struct FamilyShieldWeekDigestCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var snapshot = FamilyShieldWeekDigestStore.build()

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(
                localizationManager.localized("week_digest_title"),
                systemImage: "chart.bar.doc.horizontal"
            )
            .font(.headline)
            .foregroundColor(.white)

            Text(
                String(
                    format: localizationManager.localized("week_digest_subtitle_fmt"),
                    snapshot.weekLabel
                )
            )
            .font(.caption)
            .foregroundColor(.white.opacity(0.75))
            .fixedSize(horizontal: false, vertical: true)

            if snapshot.isEmpty {
                Text(localizationManager.localized("week_digest_empty"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.65))
            } else {
                digestLine(
                    formatKey: "week_digest_checks_fmt",
                    value: snapshot.checksCount
                )
                digestLine(
                    formatKey: "week_digest_alerts_fmt",
                    value: snapshot.alertsCount
                )
                digestLine(
                    formatKey: "week_digest_school_fmt",
                    value: snapshot.schoolArrivalsCount
                )
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .secondaryGold)
        .accessibilityIdentifier("family_shield_week_digest")
        .onAppear {
            snapshot = FamilyShieldWeekDigestStore.build(localization: localizationManager)
            FamilyShieldWeekDigestStore.scheduleWeeklyReminderIfNeeded(
                localization: localizationManager
            )
        }
    }

    private func digestLine(formatKey: String, value: Int) -> some View {
        Text(String(format: localizationManager.localized(formatKey), value))
            .font(.subheadline.weight(.semibold))
            .foregroundColor(.white.opacity(0.95))
    }
}
