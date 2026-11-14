import SwiftUI

/**
 * 👤 User Selector View
 * Accordion (DisclosureGroup) single-select — no horizontal overflow pills (P1 S15).
 * Driving reports are per-member; multi-select Set not required for this modal.
 */

struct UserSelectorView: View {

    @Binding var selectedUserId: String?
    let users: [UserOption]
    let currentUserId: String
    let showCurrentUser: Bool
    /// P1.2c: apply + collapse after Готово.
    var onDone: (() -> Void)? = nil

    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var isExpanded = true
    @State private var draftSelection: String?

    struct UserOption: Identifiable {
        let id: String
        let name: String
        let role: String
        let avatar: String?

        var displayName: String { name }

        var icon: String {
            avatar ?? defaultIcon
        }

        private var defaultIcon: String {
            switch role.lowercased() {
            case "parent": return "person.2.fill"
            case "child": return "person.fill"
            case "teenager": return "person.3.fill"
            case "elderly": return "heart.circle.fill"
            case "self": return "person.crop.circle"
            default: return "person.fill"
            }
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            DisclosureGroup(
                isExpanded: $isExpanded,
                content: {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        if showCurrentUser {
                            memberRow(
                                id: currentUserId,
                                title: localizationManager.localized("where_phone_you"),
                                icon: "person.crop.circle"
                            )
                        }
                        ForEach(users) { user in
                            if !(showCurrentUser && user.id == currentUserId) {
                                memberRow(
                                    id: user.id,
                                    title: localizedDisplayName(for: user),
                                    icon: user.icon
                                )
                            }
                        }
                        Button {
                            HapticFeedback.selection()
                            selectedUserId = draftSelection ?? currentUserId
                            isExpanded = false
                            onDone?()
                        } label: {
                            Text(localizationManager.localized("driving_reports_done"))
                                .font(.subheadline.weight(.bold))
                                .foregroundColor(.backgroundDark)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, Spacing.s)
                                .background(Color.secondaryGold)
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }
                        .buttonStyle(.plain)
                        .padding(.top, Spacing.s)
                        .accessibilityIdentifier("driving_reports_user_done")
                    }
                    .padding(.top, Spacing.s)
                },
                label: {
                    HStack {
                        Text(localizationManager.localized("driving_reports_select_members"))
                            .font(.body.weight(.semibold))
                            .foregroundColor(.textPrimary)
                        Spacer()
                        Text(selectedLabel)
                            .font(.caption.weight(.semibold))
                            .foregroundColor(.secondaryGold)
                            .lineLimit(1)
                    }
                }
            )
            .tint(Color.secondaryGold)
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.45))
            )
            .accessibilityIdentifier("driving_reports_user_accordion")
            .onAppear {
                draftSelection = selectedUserId ?? currentUserId
            }
            .onChange(of: selectedUserId) { newValue in
                draftSelection = newValue ?? currentUserId
            }
        }
    }

    private var selectedLabel: String {
        let id = selectedUserId ?? currentUserId
        if id == currentUserId || id == "current" {
            return localizationManager.localized("where_phone_you")
        }
        if let u = users.first(where: { $0.id == id }) {
            return localizedDisplayName(for: u)
        }
        return localizationManager.localized("where_phone_you")
    }

    private func memberRow(id: String, title: String, icon: String) -> some View {
        let selected = (draftSelection ?? selectedUserId) == id
        return Button {
            HapticFeedback.selection()
            draftSelection = id
        } label: {
            HStack(spacing: Spacing.s) {
                Image(systemName: icon.hasPrefix("person") || icon.hasPrefix("heart") ? icon : "person.fill")
                    .foregroundColor(selected ? .secondaryGold : .textSecondary)
                Text(title)
                    .font(.subheadline.weight(selected ? .semibold : .regular))
                    .foregroundColor(.textPrimary)
                Spacer()
                Image(systemName: selected ? "checkmark.circle.fill" : "circle")
                    .foregroundColor(selected ? .secondaryGold : .textSecondary)
            }
            .padding(.vertical, 6)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(selected ? .isSelected : [])
    }

    private func localizedDisplayName(for user: UserOption) -> String {
        if user.role.lowercased() == "self" || user.id == currentUserId {
            return localizationManager.localized("where_phone_you")
        }
        let role: FamilyMemberCard.FamilyRole?
        switch user.role.lowercased() {
        case "parent": role = .parent
        case "child": role = .child
        case "teenager", "teen": role = .teenager
        case "elderly", "grandparent": role = .elderly
        default: role = nil
        }
        return FamilyMemberDisplayNameFormatter.displayName(
            storedName: user.displayName,
            role: role,
            localization: localizationManager
        )
    }
}

#if DEBUG
struct UserSelectorView_Previews: PreviewProvider {
    static var previews: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            UserSelectorView(
                selectedUserId: .constant(nil),
                users: [
                    UserSelectorView.UserOption(id: "1", name: "Маша", role: "child", avatar: nil),
                    UserSelectorView.UserOption(id: "2", name: "Сергей", role: "teenager", avatar: nil)
                ],
                currentUserId: "current",
                showCurrentUser: true
            )
            .padding()
        }
        .environmentObject(LocalizationManager())
    }
}
#endif
