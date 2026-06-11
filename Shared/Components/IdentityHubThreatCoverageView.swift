import SwiftUI

/// B4-05 — 12 fraud threats with L3 pipeline routing.
struct IdentityHubThreatCoverageView: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("identity_hub_coverage_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            Text(localizationManager.localized("identity_hub_coverage_count"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)

            ForEach(IdentityFraudThreat.allCases) { threat in
                threatRow(threat)
            }
        }
    }

    private func threatRow(_ threat: IdentityFraudThreat) -> some View {
        Button {
            HapticFeedback.selection()
            navigate(for: threat.route)
        } label: {
            HStack(alignment: .top, spacing: Spacing.s) {
                Image(systemName: threat.systemImage)
                    .font(.body.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .frame(width: 24)

                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: Spacing.xs) {
                        Text(threat.rawValue.uppercased())
                            .font(.caption2.weight(.bold))
                            .foregroundColor(.white.opacity(0.55))
                        Text(localizationManager.localized(threat.titleKey))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                            .multilineTextAlignment(.leading)
                    }
                    Text(localizationManager.localized(threat.pipelineKey))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.7))
                        .multilineTextAlignment(.leading)
                }

                Spacer(minLength: 0)

                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.45))
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.medium)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("identity_hub_frd_\(threat.catalogIndex)")
    }

    private func navigate(for route: IdentityFraudThreatRoute) {
        switch route {
        case .identityTab(let tab):
            navigationManager.navigateToIdentityHub(tab: tab)
        case .antifakeTab(let tab, let textMode):
            navigationManager.navigateToAntifakeHub(tab: tab, textMode: textMode)
        }
    }
}
