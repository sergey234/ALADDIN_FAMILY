import SwiftUI

// MARK: - L-03 Family shared scam reports

struct AntifakeFamilyReportsSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var isExpanded = false
    @State private var reports: [AntifakeFamilySharedReport] = []
    @State private var isLoading = false
    @State private var loadError: String?
    @State private var hasLoadedOnce = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    isExpanded.toggle()
                }
                HapticFeedback.selection()
                if isExpanded, !hasLoadedOnce {
                    Task { await loadReports() }
                }
            } label: {
                HStack(alignment: .top, spacing: Spacing.s) {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Label(
                            localizationManager.localized("antifake_family_reports_title"),
                            systemImage: "person.3.fill"
                        )
                        .font(.headline)
                        .foregroundColor(.white)

                        Text(localizationManager.localized("antifake_family_reports_subtitle"))
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.75))
                            .multilineTextAlignment(.leading)

                        if !isExpanded {
                            Text(localizationManager.localized("antifake_family_reports_collapsed_hint"))
                                .font(.caption2)
                                .foregroundColor(.white.opacity(0.6))
                                .multilineTextAlignment(.leading)
                        }
                    }

                    Spacer(minLength: Spacing.s)

                    if !isExpanded, !reports.isEmpty {
                        Text("\(reports.count)")
                            .font(.caption.weight(.bold))
                            .foregroundColor(.white)
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, 4)
                            .background(Color.secondaryGold.opacity(0.45))
                            .clipShape(Capsule())
                            .accessibilityIdentifier("antifake_family_reports_count_badge")
                    }

                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.white.opacity(0.7))
                }
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("antifake_family_reports_header")
            .accessibilityLabel(localizationManager.localized("antifake_family_reports_title"))
            .accessibilityValue(
                isExpanded
                    ? localizationManager.localized("accordion_expanded", localizationManager.localized("antifake_family_reports_title"))
                    : localizationManager.localized("accordion_collapsed", localizationManager.localized("antifake_family_reports_title"))
            )
            .accessibilityHint(
                isExpanded
                    ? localizationManager.localized("accordion_collapse_hint")
                    : localizationManager.localized("accordion_expand_hint")
            )

            if isExpanded {
                expandedContent
                    .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .secondaryGold)
        .accessibilityIdentifier("antifake_family_reports_section")
    }

    @ViewBuilder
    private var expandedContent: some View {
        if isLoading {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .white))
        } else if let loadError {
            Text(loadError)
                .font(.caption)
                .foregroundColor(.warningOrange)
        } else if reports.isEmpty {
            Text(localizationManager.localized("antifake_family_reports_empty"))
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.7))
                .accessibilityIdentifier("antifake_family_reports_empty")
        } else {
            ForEach(reports) { report in
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(report.phoneMasked)
                            .font(.subheadline.weight(.semibold))
                            .foregroundColor(.white)
                        if let label = report.label, !label.isEmpty {
                            Text(label)
                                .font(.caption)
                                .foregroundColor(.white.opacity(0.75))
                        }
                    }
                    Spacer()
                    if let conf = report.jobConfidence {
                        Text("\(conf)%")
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.dangerRed)
                    }
                }
                .padding(.vertical, Spacing.xxs)
            }
        }
    }

    @MainActor
    private func loadReports() async {
        isLoading = true
        loadError = nil
        let result: Result<AntifakeFamilyReportsResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getAntifakeFamilyReports { continuation.resume(returning: $0) }
        }
        isLoading = false
        hasLoadedOnce = true
        switch result {
        case .success(let payload):
            reports = payload.reports
        case .failure:
            loadError = localizationManager.localized("antifake_family_reports_load_error")
        }
    }
}

// MARK: - L-05 Parent Call Directory dashboard

struct AntifakeFamilyCDParentCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var members: [AntifakeFamilyCDMemberStatus] = []
    @State private var isLoading = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Label(
                localizationManager.localized("antifake_family_cd_title"),
                systemImage: "phone.badge.checkmark"
            )
            .font(.headline)
            .foregroundColor(.white)

            Text(localizationManager.localized("antifake_family_cd_subtitle"))
                .font(.caption)
                .foregroundColor(.white.opacity(0.75))

            if isLoading {
                ProgressView()
            } else if members.isEmpty {
                Text(localizationManager.localized("antifake_family_cd_empty"))
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.7))
            } else {
                ForEach(members, id: \.userId) { member in
                    HStack {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(member.displayName ?? localizationManager.localized("antifake_family_cd_member"))
                                .font(.subheadline.weight(.semibold))
                                .foregroundColor(.white)
                            Text(
                                member.extensionEnabled
                                    ? localizationManager.localized("antifake_call_directory_status_enabled")
                                    : localizationManager.localized("antifake_call_directory_status_disabled")
                            )
                            .font(.caption)
                            .foregroundColor(member.extensionEnabled ? .successGreen : .warningOrange)
                        }
                        Spacer()
                        Text("\(member.syncedCount)")
                            .font(.caption.weight(.bold))
                            .foregroundColor(.white.opacity(0.85))
                    }
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .primaryBlue)
        .accessibilityIdentifier("antifake_family_cd_parent_card")
        .task { await loadStatus() }
    }

    @MainActor
    private func loadStatus() async {
        isLoading = true
        let result: Result<AntifakeFamilyCDStatusResponse, Error> = await withCheckedContinuation { continuation in
            APIService.shared.getAntifakeFamilyCDStatus { continuation.resume(returning: $0) }
        }
        isLoading = false
        if case .success(let payload) = result {
            members = payload.members
        }
    }
}

/// L-02 helper: report local CD status to family dashboard after sync.
enum AntifakeFamilyCDStatusReporter {
    @MainActor
    static func report(extensionEnabled: Bool, syncedCount: Int) {
        APIService.shared.reportAntifakeFamilyCDStatus(
            extensionEnabled: extensionEnabled,
            syncedCount: syncedCount
        ) { _ in }
    }
}
