import SwiftUI

/// B5-06…08 — cyb / mob / iot coverage with L3 routing.
struct DeviceHubThreatCoverageView: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.l) {
            Text(localizationManager.localized("device_hub_coverage_hint"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.85))

            cyberSection
            mobileSection
            iotSection
        }
    }

    private var cyberSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("device_hub_coverage_cyber"))
                .font(.caption.weight(.bold))
                .foregroundColor(.secondaryGold)
            ForEach(DeviceCyberThreat.allCases) { threat in
                threatRow(
                    id: threat.rawValue,
                    titleKey: threat.titleKey,
                    pipelineKey: threat.pipelineKey,
                    icon: threat.systemImage,
                    route: threat.route
                )
            }
        }
    }

    private var mobileSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("device_hub_coverage_mobile"))
                .font(.caption.weight(.bold))
                .foregroundColor(.secondaryGold)
            ForEach(DeviceMobileThreat.allCases) { threat in
                threatRow(
                    id: threat.rawValue,
                    titleKey: threat.titleKey,
                    pipelineKey: threat.pipelineKey,
                    icon: threat.systemImage,
                    route: threat.route
                )
            }
        }
    }

    private var iotSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("device_hub_coverage_iot"))
                .font(.caption.weight(.bold))
                .foregroundColor(.secondaryGold)
            ForEach(DeviceIoTThreat.allCases) { threat in
                threatRow(
                    id: threat.rawValue,
                    titleKey: threat.titleKey,
                    pipelineKey: threat.pipelineKey,
                    icon: threat.systemImage,
                    route: threat.route
                )
            }
        }
    }

    private func threatRow(
        id: String,
        titleKey: String,
        pipelineKey: String,
        icon: String,
        route: DeviceThreatRoute
    ) -> some View {
        Button {
            HapticFeedback.selection()
            navigate(for: route)
        } label: {
            HStack(alignment: .top, spacing: Spacing.s) {
                Image(systemName: icon)
                    .font(.body.weight(.semibold))
                    .foregroundColor(.secondaryGold)
                    .frame(width: 24)

                VStack(alignment: .leading, spacing: 4) {
                    HStack(spacing: Spacing.xs) {
                        Text(id.uppercased())
                            .font(.caption2.weight(.bold))
                            .foregroundColor(.white.opacity(0.55))
                        Text(localizationManager.localized(titleKey))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                            .multilineTextAlignment(.leading)
                    }
                    Text(localizationManager.localized(pipelineKey))
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
        .accessibilityIdentifier("device_hub_\(id.replacingOccurrences(of: "-", with: "_"))")
    }

    private func navigate(for route: DeviceThreatRoute) {
        switch route {
        case .deviceTab(let tab):
            navigationManager.navigateToDeviceHub(tab: tab)
        case .antifakeTab(let tab, let textMode):
            navigationManager.navigateToAntifakeHub(tab: tab, textMode: textMode)
        }
    }
}
