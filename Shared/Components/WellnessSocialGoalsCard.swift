import SwiftUI

/// fws-17 — post check-in social goal nudge (dismissable, 48h cooldown on server).
struct WellnessSocialGoalsCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager

    let block: WellnessSocialGoalsBlock
    var onDismiss: () -> Void

    @State private var expanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Image(systemName: "person.2.fill")
                    .foregroundColor(.cyan)
                Text(localizationManager.localized("wellness_social_goals_title"))
                    .font(.subheadline.bold())
                Spacer()
                Button {
                    Task { await dismiss() }
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.white.opacity(0.5))
                }
                .buttonStyle(.plain)
            }

            if let key = block.goalKey {
                Text(localizationManager.localized(key))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.9))
            }

            Button {
                withAnimation { expanded.toggle() }
            } label: {
                Text(localizationManager.localized("wellness_social_goals_steps_toggle"))
                    .font(.caption.weight(.semibold))
            }
            .buttonStyle(.plain)
            .foregroundColor(.secondaryGold)

            if expanded, let steps = block.playbookSteps {
                ForEach(Array(steps.enumerated()), id: \.offset) { index, stepKey in
                    Text("\(index + 1). \(localizationManager.localized(stepKey))")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.85))
                }
            }

            HStack(spacing: 12) {
                if block.cta == "family_chat" {
                    Button {
                        navigationManager.navigateTo(.familyChat)
                    } label: {
                        Text(localizationManager.localized("companion_social_bridge_family_cta"))
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(.cyan)
                }
                Button {
                    navigationManager.navigateToCompanionHome(returnTo: navigationManager.currentScreen)
                } label: {
                    Text(localizationManager.localized("wellness_social_goals_companion_cta"))
                }
                .buttonStyle(.bordered)
                .tint(.white)
            }
        }
        .padding(12)
        .stormGlassCard(cornerRadius: 12)
        .accessibilityIdentifier("wellness_social_goals_card")
    }

    @MainActor
    private func dismiss() async {
        if let key = block.goalKey {
            try? await WellnessAPIService.shared.dismissSocialNudge(goalKey: key)
        }
        onDismiss()
    }
}
