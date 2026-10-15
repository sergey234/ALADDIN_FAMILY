import SwiftUI
import UIKit

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

            if let status = result.status, !status.isEmpty {
                Text(ComponentStatusCopy.localized(status, localization: localizationManager))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.secondaryGold)
            }

            if !result.threats.isEmpty {
                ForEach(result.threats) { threat in
                    let card = DeviceThreatPresentation.present(
                        id: threat.id,
                        name: threat.name,
                        description: threat.description,
                        localization: localizationManager
                    )
                    VStack(alignment: .leading, spacing: 4) {
                        Text(card.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                        Text("\(localizationManager.localized("threat_card_what")): \(card.what)")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.9))
                            .fixedSize(horizontal: false, vertical: true)
                        Text("\(localizationManager.localized("threat_card_where")): \(card.whereText)")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.85))
                        Text("\(localizationManager.localized("threat_card_action")): \(card.action)")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.85))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(.top, 4)
                }
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

            if let incidentId = result.incidentId, !incidentId.isEmpty {
                // Soften INC-* — family UI, not a breach ticket. Long-press copies full id.
                Text("\(localizationManager.localized("device_hub_incident_id")): \(shortIncidentLabel(incidentId))")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.85))
                    .contextMenu {
                        Button(localizationManager.localized("common_copy")) {
                            UIPasteboard.general.string = incidentId
                        }
                    }
            }
            if let status = result.status {
                Text("\(localizationManager.localized("device_hub_incident_status")): \(ComponentStatusCopy.localized(status, localization: localizationManager))")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.85))
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }

    private func shortIncidentLabel(_ raw: String) -> String {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.count <= 12 { return trimmed }
        return String(trimmed.prefix(8)) + "…"
    }
}
