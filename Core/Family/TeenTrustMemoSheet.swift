import SwiftUI

/// Growth P.8: one-time honest memo for teenager role — what the family sees on the map.
struct TeenTrustMemoSheet: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager

    static let shownKey = "teen_trust_memo_shown_v1"

    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: Spacing.m) {
                Text(localizationManager.localized("trust_teen_memo_title"))
                    .font(.title3.weight(.semibold))
                    .foregroundColor(.textPrimary)
                Text(localizationManager.localized("trust_teen_memo_body"))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                Spacer()
                Button {
                    UserDefaults.standard.set(true, forKey: Self.shownKey)
                    isPresented = false
                } label: {
                    Text(localizationManager.localized("common_ok"))
                        .font(.headline)
                        .foregroundColor(.backgroundDark)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .accessibilityIdentifier("teen_trust_memo_ok")
            }
            .padding(Spacing.l)
            .background(AladdinSnowballPalette.canvasGradient.ignoresSafeArea())
            .navigationBarItems(trailing: Button(localizationManager.localized("common_close")) {
                UserDefaults.standard.set(true, forKey: Self.shownKey)
                isPresented = false
            })
        }
        .accessibilityIdentifier("teen_trust_memo_sheet")
    }

    /// Present once when current roster role is teenager.
    static func shouldPresent(members: [FamilyMemberData] = FamilyLocalStore.loadPersistedMembers()) -> Bool {
        if UserDefaults.standard.bool(forKey: shownKey) { return false }
        if let me = members.first(where: { $0.isCurrentUser }) {
            return me.role == .teenager
        }
        let role = (UserDefaults.standard.string(forKey: "current_user_role") ?? "").lowercased()
        return role == "teenager" || role == "teen"
    }
}
