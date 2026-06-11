import SwiftUI

/// Scan result card for Device Hub L3 agents (B5).
struct DeviceScanResultCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let result: DeviceAgentScanResult

    private var accentColor: Color {
        result.isClean ? .successGreen : .dangerRed
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Label(
                result.isClean
                    ? localizationManager.localized("device_hub_scan_clean")
                    : localizationManager.localized("device_hub_scan_threats_found"),
                systemImage: result.isClean ? "checkmark.shield.fill" : "exclamationmark.shield.fill"
            )
            .font(.headline)
            .foregroundColor(.white)

            if let score = result.securityScore {
                HStack {
                    Text(localizationManager.localized("device_hub_security_score"))
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.75))
                    Spacer()
                    Text("\(score)")
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(accentColor)
                }
            }

            if result.threatsFound > 0 {
                Text(localizationManager.localized("device_hub_threats_count"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.white.opacity(0.7))
                Text("\(result.threatsFound)")
                    .font(.title3.weight(.bold))
                    .foregroundColor(accentColor)
            }

            if !result.threats.isEmpty {
                ForEach(result.threats) { threat in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(threat.name ?? threat.id)
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                        if let description = threat.description {
                            Text(description)
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.75))
                        }
                    }
                }
            }

            if let agent = result.agent, !agent.isEmpty {
                Text("\(localizationManager.localized("device_hub_agent")): \(agent)")
                    .font(.caption2)
                    .foregroundColor(.white.opacity(0.55))
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }
}

struct DeviceIncidentResultCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let result: DeviceIncidentReportResult

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(
                localizationManager.localized("device_hub_incident_reported"),
                systemImage: "checkmark.circle.fill"
            )
            .font(.headline)
            .foregroundColor(.successGreen)

            if let incidentId = result.incidentId {
                Text("\(localizationManager.localized("device_hub_incident_id")): \(incidentId)")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.85))
            }
            if let status = result.status {
                Text("\(localizationManager.localized("device_hub_incident_status")): \(status)")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }
}
