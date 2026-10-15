import SwiftUI

/// ProdQA S06 — parent can add/remove custom blocked domains (hybrid with catalog).
struct ParentalCustomBlockedSitesSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var sites: [String] = []
    @State private var draft: String = ""
    @State private var feedback: String?

    private let storageKey = "parental_blocked_websites"

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("parental_custom_sites_title"))
                .font(.bodyBold)
                .foregroundColor(.textPrimary)

            Text(localizationManager.localized("parental_custom_sites_subtitle"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .fixedSize(horizontal: false, vertical: true)

            HStack(spacing: Spacing.s) {
                TextField(
                    localizationManager.localized("parental_custom_sites_placeholder"),
                    text: $draft
                )
                .textInputAutocapitalization(.never)
                .keyboardType(.URL)
                .disableAutocorrection(true)
                .padding(Spacing.s)
                .background(Color.white.opacity(0.08))
                .cornerRadius(CornerRadius.small)
                .foregroundColor(.white)

                Button {
                    addSite()
                } label: {
                    Text(localizationManager.localized("parental_custom_sites_add"))
                        .font(.caption.weight(.bold))
                        .foregroundColor(.black)
                        .padding(.horizontal, Spacing.m)
                        .padding(.vertical, Spacing.s)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.small)
                }
                .buttonStyle(.plain)
                .disabled(normalizedDraft() == nil)
                .opacity(normalizedDraft() == nil ? 0.45 : 1)
            }

            if sites.isEmpty {
                Text(localizationManager.localized("parental_custom_sites_empty"))
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.55))
            } else {
                ForEach(sites, id: \.self) { site in
                    HStack {
                        Text(site)
                            .font(.subheadline)
                            .foregroundColor(.white)
                            .lineLimit(1)
                        Spacer()
                        Button {
                            removeSite(site)
                        } label: {
                            Image(systemName: "trash")
                                .font(.caption.weight(.semibold))
                                .foregroundColor(.dangerRed)
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel(localizationManager.localized("parental_custom_sites_remove"))
                    }
                    .padding(.vertical, 4)
                }
            }

            if let feedback, !feedback.isEmpty {
                Text(feedback)
                    .font(.caption)
                    .foregroundColor(.secondaryGold)
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.medium)
        .onAppear { reloadFromStorage() }
        .accessibilityIdentifier("parental_custom_blocked_sites")
    }

    private func reloadFromStorage() {
        sites = (UserDefaults.standard.stringArray(forKey: storageKey) ?? [])
            .map { normalize($0) }
            .filter { !$0.isEmpty }
        // Unique, stable order
        var seen = Set<String>()
        sites = sites.filter { seen.insert($0).inserted }
    }

    private func normalizedDraft() -> String? {
        let value = normalize(draft)
        return value.isEmpty ? nil : value
    }

    private func normalize(_ raw: String) -> String {
        var s = raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if s.hasPrefix("https://") { s = String(s.dropFirst(8)) }
        if s.hasPrefix("http://") { s = String(s.dropFirst(7)) }
        if s.hasPrefix("www.") { s = String(s.dropFirst(4)) }
        if s.hasSuffix("/") { s = String(s.dropLast()) }
        return s
    }

    private func addSite() {
        guard let site = normalizedDraft() else { return }
        if sites.contains(site) {
            feedback = localizationManager.localized("parental_custom_sites_already")
            draft = ""
            return
        }
        sites.append(site)
        draft = ""
        persistAndSync()
        feedback = localizationManager.localized("parental_custom_sites_saved")
        HapticFeedback.impact(.light)
    }

    private func removeSite(_ site: String) {
        sites.removeAll { $0 == site }
        persistAndSync()
        feedback = localizationManager.localized("parental_custom_sites_removed")
        HapticFeedback.impact(.light)
    }

    private func persistAndSync() {
        UserDefaults.standard.set(sites, forKey: storageKey)
        let familyId = FamilyLocalStore.loadPersistedFamilyId()
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let childId = UserDefaults.standard.string(forKey: "parental_selected_child_id")?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let childOrNil = (childId?.isEmpty == false) ? childId : nil

        if !familyId.isEmpty {
            ParentalControlManager.shared.saveSettingsToServer(
                familyId: familyId,
                childId: childOrNil,
                isContentFilterEnabled: true,
                blockedWebsites: sites
            ) { result in
                if case .failure = result {
                    DispatchQueue.main.async {
                        feedback = localizationManager.localized("parental_custom_sites_sync_local")
                    }
                }
            }
        }

        Task {
            await ContentBlockerManager.shared.applyParentalBlockedWebsites(
                sites,
                contentFilterEnabled: !sites.isEmpty
            )
        }
    }
}
