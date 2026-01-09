import SwiftUI

struct RoleSelectionModal: View {
    @Binding var isPresented: Bool
    @State private var selectedRole: FamilyRole = FamilyRole.selectableRoles.first ?? .parent
    let onRoleSelected: (FamilyRole) -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    private var roles: [FamilyRole] {
        FamilyRole.selectableRoles
    }
    
    var body: some View {
        VStack(spacing: 20) {
            VStack(spacing: 12) {
                Text(localizationManager.localized("role_selection_title"))
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.primary)
                
                Text(localizationManager.localized("role_selection_subtitle"))
                    .font(.body)
                    .foregroundColor(.secondary)
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
                
                Button(localizationManager.localized("common_continue")) {
                    onRoleSelected(selectedRole)
                    isPresented = false
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(20)
        .background(Color(.systemBackground))
        .cornerRadius(16)
        .shadow(radius: 20)
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
                    .foregroundColor(isSelected ? .blue : .secondary)
                    .frame(width: 30)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizedName)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.primary)
                    
                    if hasDescription {
                        Text(descriptionText)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.blue)
                        .font(.title3)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? Color.blue.opacity(0.1) : Color.gray.opacity(0.1))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(isSelected ? Color.blue : Color.clear, lineWidth: 2)
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
