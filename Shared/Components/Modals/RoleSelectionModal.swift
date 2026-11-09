import SwiftUI

struct RoleSelectionModal: View {
    @Binding var isPresented: Bool
    @State private var selectedRole: FamilyRole = FamilyRole.selectableRoles.first ?? .parent
    let onRoleSelected: (FamilyRole) -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager

    /// QA16 I1: тёплый персик (план Snowball-warm), не белая клиника.
    static let peachFill = Color(red: 0.96, green: 0.82, blue: 0.71) // #F5D0B5
    static let peachInk = Color(red: 0.22, green: 0.14, blue: 0.10)
    
    private var roles: [FamilyRole] {
        FamilyRole.selectableRoles
    }
    
    var body: some View {
        VStack(spacing: 20) {
            VStack(spacing: 12) {
                Text(localizationManager.localized("role_selection_title"))
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(Self.peachInk)
                
                Text(localizationManager.localized("role_selection_subtitle"))
                    .font(.body)
                    .foregroundColor(Self.peachInk.opacity(0.72))
                    .multilineTextAlignment(.center)
            }
            
            VStack(spacing: 12) {
                ForEach(roles, id: \.self) { role in
                    RoleSelectionCard(
                        role: role,
                        isSelected: selectedRole == role,
                        onTap: {
                            selectedRole = role
                        }
                    )
                }
            }
            
            HStack(spacing: 16) {
                Button(localizationManager.localized("common_cancel")) {
                    isPresented = false
                }
                .buttonStyle(.bordered)
                .tint(Self.peachInk)
                
                Button(localizationManager.localized("common_continue")) {
                    onRoleSelected(selectedRole)
                    isPresented = false
                }
                .buttonStyle(.borderedProminent)
                .tint(Color.secondaryGold)
            }
        }
        .padding(20)
        .background(Self.peachFill)
        .cornerRadius(16)
        .shadow(radius: 20)
        .accessibilityIdentifier("role_selection_modal_peach")
    }
}

struct RoleSelectionCard: View {
    let role: FamilyRole
    let isSelected: Bool
    let onTap: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    private var localizedName: String {
        localizationManager.localized(role.nameLocalizationKey)
    }
    
    private var descriptionText: String {
        localizationManager.localized(role.descriptionLocalizationKey)
    }
    
    private var hasDescription: Bool {
        !descriptionText.isEmpty && descriptionText != role.descriptionLocalizationKey
    }
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 16) {
                Image(systemName: role.systemImageName)
                    .font(.title2)
                    .foregroundColor(isSelected ? Color.secondaryGold : RoleSelectionModal.peachInk.opacity(0.55))
                    .frame(width: 30)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizedName)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(RoleSelectionModal.peachInk)
                    
                    if hasDescription {
                        Text(descriptionText)
                            .font(.caption)
                            .foregroundColor(RoleSelectionModal.peachInk.opacity(0.7))
                    }
                }
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(Color.secondaryGold)
                        .font(.title3)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? Color.secondaryGold.opacity(0.18) : Color.white.opacity(0.45))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(isSelected ? Color.secondaryGold : Color.white.opacity(0.35), lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct RoleSelectionModal_Previews: PreviewProvider {
    @State static var isPresented = true
    
    static var previews: some View {
        RoleSelectionModal(isPresented: $isPresented, onRoleSelected: { _ in })
            .environmentObject(LocalizationManager())
    }
}
