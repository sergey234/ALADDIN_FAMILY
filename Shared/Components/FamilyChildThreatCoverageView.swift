import SwiftUI

/// B6-05 — 17 child threats with L3 pipeline routing.
struct FamilyChildThreatCoverageView: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("family_hub_coverage_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            Text(localizationManager.localized("family_hub_coverage_count"))
                .font(.caption.weight(.semibold))
                .foregroundColor(.secondaryGold)

            ForEach(FamilyChildThreat.allCases) { threat in
                threatRow(threat)
            }
        }
    }

    private func threatRow(_ threat: FamilyChildThreat) -> some View {
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
        .accessibilityIdentifier("family_hub_chd_\(threat.catalogIndex)")
    }

    private func navigate(for route: FamilyChildThreatRoute) {
        switch route {
        case .familyRoot:
            navigationManager.navigateToRoot(.family)
        case .parentalControl:
            navigationManager.navigateTo(.parentalControl)
        case .networkProtection:
            navigationManager.navigateTo(.networkProtection)
        case .antifakeTab(let tab, let textMode):
            navigationManager.navigateToAntifakeHub(tab: tab, textMode: textMode)
        }
    }
}
