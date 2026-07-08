import SwiftUI

// MARK: - fws-13 Crisis one-tap (112 + 8-800, parent ping via BE)

struct WellnessCrisisOneTapCTA: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showCrisisSheet = false

    var body: some View {
        Button {
            HapticFeedback.impact(.heavy)
            showCrisisSheet = true
        } label: {
            HStack(alignment: .top, spacing: Spacing.m) {
                Image(systemName: "heart.circle.fill")
                    .font(.title)
                    .foregroundColor(.dangerRed)
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizationManager.localized("wellness_crisis_one_tap_title"))
                        .font(.subheadline.weight(.bold))
                        .foregroundColor(.white)
                        .multilineTextAlignment(.leading)
                    Text(localizationManager.localized("wellness_crisis_one_tap_subtitle"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.85))
                        .multilineTextAlignment(.leading)
                }
                Spacer(minLength: 0)
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .dangerRed)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("wellness_crisis_one_tap_cta")
        .fullScreenCover(isPresented: $showCrisisSheet) {
            WellnessReferralSheet(level: "L3", notifyParentsOnLoad: true, allowDismiss: true)
                .environmentObject(localizationManager)
        }
    }
}
