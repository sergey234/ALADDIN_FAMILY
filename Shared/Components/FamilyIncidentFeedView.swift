import SwiftUI

// MARK: - fws-09 Family incident feed (parent/elderly)

struct FamilyIncidentFeedView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var service = FamilyIncidentFeedService.shared

    let members: [FamilyMemberData]

    @State private var expandedIds: Set<String> = []

    private var canView: Bool {
        FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: members)
    }

    var body: some View {
        if canView {
            VStack(alignment: .leading, spacing: Spacing.s) {
                Label(
                    localizationManager.localized("family_incident_feed_title"),
                    systemImage: "bell.and.waves.left.and.right.fill"
                )
                .font(.headline)
                .foregroundColor(.white)

                Text(localizationManager.localized("family_incident_feed_subtitle"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.75))
                    .fixedSize(horizontal: false, vertical: true)

                if service.isLoading && service.incidents.isEmpty {
                    HStack(spacing: Spacing.s) {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        Text(localizationManager.localized("family_incident_feed_loading"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.7))
                    }
                } else if service.incidents.isEmpty {
                    Text(localizationManager.localized("family_incident_feed_empty"))
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.65))
                } else {
                    ForEach(service.incidents) { item in
                        incidentRow(item)
                    }
                }
            }
            .padding(Spacing.m)
            .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .warningOrange)
            .accessibilityIdentifier("family_incident_feed_section")
            .task {
                await service.refresh(members: members)
            }
        }
    }

    @ViewBuilder
    private func incidentRow(_ item: FamilyIncidentItem) -> some View {
        let isExpanded = expandedIds.contains(item.id)
        VStack(alignment: .leading, spacing: Spacing.xs) {
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    if isExpanded {
                        expandedIds.remove(item.id)
                    } else {
                        expandedIds.insert(item.id)
                    }
                }
                HapticFeedback.selection()
            } label: {
                HStack(alignment: .top, spacing: Spacing.s) {
                    Image(systemName: iconName(for: item.incidentType))
                        .foregroundColor(severityColor(item.severity))
                        .font(.body)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(localizationManager.localized(item.titleKey))
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                            .multilineTextAlignment(.leading)
                        if let createdAt = item.createdAt {
                            Text(formattedDate(createdAt))
                                .font(.caption2)
                                .foregroundColor(.white.opacity(0.55))
                        }
                    }
                    Spacer(minLength: 0)
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.white.opacity(0.5))
                }
            }
            .buttonStyle(.plain)

            if isExpanded {
                Text(localizationManager.localized("family_incident_playbook_header"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primaryBlue.opacity(0.9))
                    .padding(.top, Spacing.xxs)

                ForEach(Array(item.playbookSteps.enumerated()), id: \.offset) { index, stepKey in
                    HStack(alignment: .top, spacing: Spacing.xs) {
                        Text("\(index + 1).")
                            .font(.caption.weight(.bold))
                            .foregroundColor(.secondaryGold)
                        Text(localizationManager.localized(stepKey))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.9))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
        }
        .padding(Spacing.s)
        .background(Color.white.opacity(0.06))
        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
        .accessibilityIdentifier("family_incident_row_\(item.incidentType.rawValue)")
    }

    private func iconName(for type: FamilyIncidentType) -> String {
        switch type {
        case .antifakeAlert: return "shield.lefthalf.filled.slash"
        case .wellnessCrisis: return "heart.text.square.fill"
        case .bedtimeBreach: return "moon.zzz.fill"
        }
    }

    private func severityColor(_ severity: FamilyIncidentSeverity) -> Color {
        switch severity {
        case .critical, .high: return .dangerRed
        case .medium: return .warningOrange
        case .low: return .primaryBlue
        }
    }

    private func formattedDate(_ iso: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = formatter.date(from: iso) ?? ISO8601DateFormatter().date(from: iso) {
            let display = DateFormatter()
            display.locale = localizationManager.locale
            display.dateStyle = .short
            display.timeStyle = .short
            return display.string(from: date)
        }
        return iso
    }
}
