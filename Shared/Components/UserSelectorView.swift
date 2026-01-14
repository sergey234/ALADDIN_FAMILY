import SwiftUI

/**
 * 👤 User Selector View
 * Компонент для выбора пользователя/ребенка для просмотра отчетов
 * Используется в модальных окнах отчетов (DrivingReportsModal, AICategoriesModal)
 */

struct UserSelectorView: View {
    
    // MARK: - Properties
    
    @Binding var selectedUserId: String?
    let users: [UserOption]
    let currentUserId: String
    let showCurrentUser: Bool // Показывать ли "Я" (текущий пользователь)
    
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    struct UserOption: Identifiable {
        let id: String
        let name: String
        let role: String
        let avatar: String?
        
        var displayName: String {
            name
        }
        
        var icon: String {
            avatar ?? defaultIcon
        }
        
        private var defaultIcon: String {
            switch role.lowercased() {
            case "parent": return "person.2.fill"
            case "child": return "figure.child"
            case "teenager": return "person.3.fill"
            case "elderly": return "heart.circle.fill"
            default: return "person.fill"
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Text(localizationManager.localized("reports_select_user"))
                .font(.body)
                .foregroundColor(.textSecondary)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: Spacing.s) {
                    // "Я" (текущий пользователь)
                    if showCurrentUser {
                        UserChip(
                            id: currentUserId,
                            name: localizationManager.localized("reports_current_user"),
                            icon: "person.fill",
                            isSelected: selectedUserId == currentUserId || selectedUserId == nil,
                            onTap: {
                                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                                    selectedUserId = currentUserId
                                }
                            }
                        )
                    }
                    
                    // Другие пользователи
                    ForEach(users) { user in
                        UserChip(
                            id: user.id,
                            name: user.displayName,
                            icon: user.icon,
                            isSelected: selectedUserId == user.id,
                            onTap: {
                                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                                    selectedUserId = user.id
                                }
                            }
                        )
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
        }
    }
}

// MARK: - User Chip

struct UserChip: View {
    let id: String
    let name: String
    let icon: String
    let isSelected: Bool
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: Spacing.xs) {
                // Иконка
                if icon.hasPrefix("person.") || icon.hasPrefix("figure.") || icon.hasPrefix("heart.") {
                    Image(systemName: icon)
                        .font(.caption)
                } else {
                    Text(icon)
                        .font(.caption)
                }
                
                Text(name)
                    .font(.body)
            }
            .foregroundColor(isSelected ? .white : .textPrimary)
            .padding(.horizontal, Spacing.m)
            .padding(.vertical, Spacing.s)
            .background(
                Capsule()
                    .fill(isSelected ? Color.primaryBlue : Color.backgroundMedium)
            )
            .overlay(
                Capsule()
                    .stroke(isSelected ? Color.primaryBlue.opacity(0.5) : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(PlainButtonStyle())
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(name), \(isSelected ? "выбран" : "не выбран")")
        .accessibilityHint("Нажмите для выбора")
        .accessibilityAddTraits(isSelected ? .isSelected : [])
    }
}

// MARK: - Preview

#if DEBUG
struct UserSelectorView_Previews: PreviewProvider {
    static var previews: some View {
    ZStack {
        LinearGradient.backgroundGradient
            .ignoresSafeArea()
        
        VStack(spacing: Spacing.l) {
            UserSelectorView(
                selectedUserId: .constant(nil),
                users: [
                    UserSelectorView.UserOption(
                        id: "1",
                        name: "Маша",
                        role: "child",
                        avatar: nil
                    ),
                    UserSelectorView.UserOption(
                        id: "2",
                        name: "Сергей",
                        role: "teenager",
                        avatar: nil
                    )
                ],
                currentUserId: "current",
                showCurrentUser: true
            )
            .padding()
        }
    }
    .environmentObject(LocalizationManager())
    }
}
#endif

