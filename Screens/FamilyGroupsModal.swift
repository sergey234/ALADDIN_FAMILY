import SwiftUI

/// Circles B — family group labels (same roster only; no second invite list).
struct FamilyGroupsModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager

    @State private var groups: [FamilyGroupLabelStore.Group] = []
    @State private var roster: [FamilyMemberData] = []
    @State private var editing: FamilyGroupLabelStore.Group?
    @State private var draftTitle = ""
    @State private var draftMemberIds: Set<String> = []
    @State private var showEditor = false

    var body: some View {
        FamilyModalBaseView(
            title: localizationManager.localized("family_groups_title"),
            isPresented: $isPresented
        ) {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("family_groups_subtitle"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)

                /// JOB09 CapCut · H25 FamilyHug Kneel · Groups hero · UI 320×220.
                Image("ICON_ALIVE_HERO_H25_FamilyHugKneel")
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: .infinity)
                    .frame(height: 200)
                    .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                    .accessibilityHidden(true)
                    .accessibilityIdentifier("family_groups_hero_hug")

                if groups.isEmpty && !showEditor {
                    Text(localizationManager.localized("family_groups_empty"))
                        .font(.subheadline)
                        .foregroundColor(.textSecondary)
                        .padding(Spacing.m)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .aladdinProductCard(cornerRadius: CornerRadius.medium)
                }

                ForEach(groups) { group in
                    HStack(alignment: .top, spacing: Spacing.m) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(group.title)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            Text(memberSummary(for: group))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        Spacer(minLength: 0)
                        Button {
                            HapticFeedback.selection()
                            FamilyGroupLabelStore.selectedFilterGroupId = group.id
                        } label: {
                            Text(localizationManager.localized("family_groups_map_filter"))
                                .font(.caption.weight(.bold))
                                .foregroundColor(.secondaryGold)
                        }
                        .buttonStyle(.plain)
                        Button {
                            openEditor(group)
                        } label: {
                            Image(systemName: "pencil")
                                .foregroundColor(.secondaryGold)
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(Spacing.m)
                    .background(Color.white.opacity(0.10))
                    .cornerRadius(CornerRadius.medium)
                    .accessibilityIdentifier("family_group_row_\(group.id.uuidString)")
                }

                if showEditor {
                    editorCard
                } else {
                    Button {
                        openEditor(nil)
                    } label: {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                            Text(localizationManager.localized("family_groups_create"))
                                .font(.bodyBold)
                        }
                        .foregroundColor(.secondaryGold)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold.opacity(0.18))
                        .cornerRadius(CornerRadius.medium)
                    }
                    .buttonStyle(.plain)
                    .accessibilityIdentifier("family_groups_create")
                }
            }
        }
        .onAppear {
            reload()
        }
    }

    private var editorCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            ZStack(alignment: .leading) {
                if draftTitle.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    Text(localizationManager.localized("family_groups_name_placeholder"))
                        .font(.body)
                        .foregroundColor(Color.textTertiary)
                }
                TextField("", text: $draftTitle)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                    .accentColor(.secondaryGold)
            }
            .padding(Spacing.m)
            .background(Color.white.opacity(0.12))
            .cornerRadius(CornerRadius.medium)

            Text(localizationManager.localized("family_groups_pick_members"))
                .font(.subheadline.weight(.semibold))
                .foregroundColor(.textPrimary)

            if roster.isEmpty {
                Text(localizationManager.localized("family_groups_subtitle"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            } else {
                ForEach(roster) { member in
                    let mid = member.canonicalId
                    Button {
                        if draftMemberIds.contains(mid) {
                            draftMemberIds.remove(mid)
                        } else {
                            draftMemberIds.insert(mid)
                        }
                        HapticFeedback.selection()
                    } label: {
                        HStack {
                            Image(systemName: draftMemberIds.contains(mid) ? "checkmark.circle.fill" : "circle")
                                .foregroundColor(draftMemberIds.contains(mid) ? .secondaryGold : .textSecondary)
                            Text(member.name)
                                .font(.subheadline)
                                .foregroundColor(.textPrimary)
                            Spacer()
                        }
                        .padding(.vertical, 6)
                    }
                    .buttonStyle(.plain)
                }
            }

            HStack(spacing: Spacing.m) {
                Button {
                    showEditor = false
                    editing = nil
                } label: {
                    Text(localizationManager.localized("edit_profile_cancel"))
                        .font(.body.weight(.semibold))
                        .foregroundColor(.textSecondary)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.white.opacity(0.10))
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)

                Button {
                    saveDraft()
                } label: {
                    Text(localizationManager.localized("family_groups_save"))
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("family_groups_save")
            }

            if editing != nil {
                Button(role: .destructive) {
                    if let id = editing?.id {
                        FamilyGroupLabelStore.delete(id: id)
                        reload()
                        showEditor = false
                        editing = nil
                        HapticFeedback.notification(.warning)
                    }
                } label: {
                    Text(localizationManager.localized("family_groups_delete"))
                        .font(.caption.weight(.bold))
                        .foregroundColor(.dangerRed)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(Spacing.m)
        .background(Color.secondaryGold.opacity(0.10))
        .cornerRadius(CornerRadius.medium)
    }

    private func reload() {
        groups = FamilyGroupLabelStore.load()
        roster = FamilyGroupLabelStore.loadRosterMembers()
    }

    private func openEditor(_ group: FamilyGroupLabelStore.Group?) {
        editing = group
        draftTitle = group?.title ?? ""
        draftMemberIds = Set(group?.memberIds ?? [])
        showEditor = true
        HapticFeedback.impact(.light)
    }

    private func saveDraft() {
        let title = draftTitle.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !title.isEmpty else { return }
        // Only current roster IDs — never invent a second list.
        let allowed = Set(roster.map(\.canonicalId))
        let members = draftMemberIds.filter { allowed.contains($0) }.sorted()
        let group = FamilyGroupLabelStore.Group(
            id: editing?.id ?? UUID(),
            title: title,
            memberIds: members
        )
        FamilyGroupLabelStore.upsert(group)
        reload()
        showEditor = false
        editing = nil
        HapticFeedback.notification(.success)
    }

    private func memberSummary(for group: FamilyGroupLabelStore.Group) -> String {
        let names = roster
            .filter { group.memberIds.contains($0.canonicalId) }
            .map(\.name)
        if names.isEmpty {
            return "—"
        }
        return names.joined(separator: ", ")
    }
}
