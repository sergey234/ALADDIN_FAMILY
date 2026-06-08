import SwiftUI

/// p1-24 — Trust Center: data, escalation, teen parent visibility.
struct WellnessTrustCenterScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var parentShareOn = false
    @State private var canEditShare = false
    @State private var isLoading = true
    @State private var errorText: String?
    @State private var showHelplineSheet = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header
                trustBlock(
                    title: localizationManager.localized("wellness_trust_data_stored"),
                    body: localizationManager.localized("wellness_trust_data_stored_body")
                )
                trustBlock(
                    title: localizationManager.localized("wellness_trust_data_not_stored"),
                    body: localizationManager.localized("wellness_trust_data_not_stored_body")
                )
                Text(localizationManager.localized("wellness_trust_escalation_title"))
                    .font(.headline)
                ForEach(["l0", "l1", "l2", "l3"], id: \.self) { level in
                    Text(localizationManager.localized("wellness_trust_escalation_\(level)"))
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Text(localizationManager.localized("wellness_trust_crisis_no_chat_log"))
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .padding(.top, 4)

                Button {
                    showHelplineSheet = true
                } label: {
                    Label(
                        localizationManager.localized("wellness_helpline_open"),
                        systemImage: "phone.fill"
                    )
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                }
                .buttonStyle(.borderedProminent)
                .tint(.red)

                Text(localizationManager.localized("wellness_teen_privacy_title"))
                    .font(.headline)
                Text(localizationManager.localized("wellness_teen_privacy_summary"))
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(localizationManager.localized("wellness_teen_privacy_crisis_only"))
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(localizationManager.localized("wellness_teen_privacy_none"))
                    .font(.caption)
                    .foregroundStyle(.secondary)

                if canEditShare {
                    Toggle(
                        localizationManager.localized("wellness_teen_parent_share_toggle"),
                        isOn: $parentShareOn
                    )
                    .onChange(of: parentShareOn) { newValue in
                        Task { await saveParentShare(newValue) }
                    }
                }
                if let errorText {
                    Text(errorText).foregroundStyle(.orange).font(.caption)
                }
            }
            .padding()
        }
        .task { await load() }
        .sheet(isPresented: $showHelplineSheet) {
            WellnessReferralSheet(level: "L2")
                .environmentObject(localizationManager)
        }
    }

    private var header: some View {
        HStack {
            Button { navigationManager.goBack() } label: {
                Image(systemName: "chevron.left")
            }
            Text(localizationManager.localized("wellness_trust_title"))
                .font(.headline.bold())
            Spacer()
        }
    }

    private func trustBlock(title: String, body: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title).font(.subheadline.bold())
            Text(body).font(.caption).foregroundStyle(.secondary)
        }
    }

    private func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let s = try await WellnessAPIService.shared.fetchSettings()
            canEditShare = s.canEditParentShare
            parentShareOn = (s.settings.parentShareAggregate ?? 0) != 0
        } catch {
            errorText = localizationManager.localized("wellness_error_network")
        }
    }

    private func saveParentShare(_ on: Bool) async {
        do {
            _ = try await WellnessAPIService.shared.setParentShareAggregate(on)
        } catch {
            errorText = localizationManager.localized("wellness_error_network")
            parentShareOn = !on
        }
    }
}
