import SwiftUI

/**
 * 👋 Role Selection Modal
 * Модальное окно выбора роли в семье (для прогрессивной регистрации)
 * Окно #1 в процессе регистрации
 */

struct RoleSelectionModal: View {
    
    @Binding var isPresented: Bool
    @Binding var selectedRole: FamilyRole?
    
    var onRoleSelected: (FamilyRole) -> Void
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Backdrop blur
            Color.black.opacity(0.5)
                .ignoresSafeArea()
                .blur(radius: 20)
            
            // Modal content
            VStack(spacing: Spacing.xl) {
                // Header
                VStack(spacing: Spacing.m) {
                    Text("👋")
                        .font(.system(size: 40))
                    
                    Text("Добро пожаловать!")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(Color(red: 0.988, green: 0.827, blue: 0.302))  // Яркое золото из иконки!
                    
                    Text("Кто вы в семье?")
                        .font(.system(size: 16))
                        .foregroundColor(.textPrimary)
                }
                
                // Role cards grid
                VStack(spacing: Spacing.m) {
                    HStack(spacing: Spacing.m) {
                        RoleCard(
                            icon: "👨‍👩‍👧‍👦",
                            title: "РОДИТЕЛЬ",
                            features: ["Полный доступ", "Контроль семьи"],
                            role: .parent,
                            isSelected: selectedRole == .parent
                        ) {
                            selectRole(.parent)
                        }
                        
                        RoleCard(
                            icon: "👶",
                            title: "РЕБЁНОК",
                            features: ["Детский режим", "Безопасность"],
                            role: .child,
                            isSelected: selectedRole == .child
                        ) {
                            selectRole(.child)
                        }
                    }
                    
                    HStack(spacing: Spacing.m) {
                        RoleCard(
                            icon: "👴",
                            title: "ЛЮДИ 60+",
                            features: ["Упрощённый UI", "Большие кнопки"],
                            role: .elderly,
                            isSelected: selectedRole == .elderly
                        ) {
                            selectRole(.elderly)
                        }
                        
                        RoleCard(
                            icon: "👤",
                            title: "ЧЕЛОВЕК",
                            features: ["Стандартный", "Полный доступ"],
                            role: .other,
                            isSelected: selectedRole == .other
                        ) {
                            selectRole(.other)
                        }
                    }
                }
            }
            .padding(Spacing.xl)
            .frame(width: 340)
            .background(
                LinearGradient(
                    colors: [
                        Color(red: 0.059, green: 0.090, blue: 0.165),  // Космический тёмный
                        Color(red: 0.118, green: 0.227, blue: 0.541),  // Глубокий синий
                        Color(red: 0.231, green: 0.510, blue: 0.965),  // Электрический синий
                        Color(red: 0.118, green: 0.251, blue: 0.686)   // Королевский синий
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(24)
            .shadow(color: .black.opacity(0.5), radius: 30, x: 0, y: 20)
        }
        .transition(.asymmetric(
            insertion: .scale(scale: 0.8).combined(with: .opacity),
            removal: .scale(scale: 0.8).combined(with: .opacity)
        ))
        .animation(.spring(response: 0.4, dampingFraction: 0.8), value: isPresented)
    }
    
    // MARK: - Actions
    
    private func selectRole(_ role: FamilyRole) {
        selectedRole = role
        
        // Haptic feedback
        let impactFeedback = UIImpactFeedbackGenerator(style: .medium)
        impactFeedback.impactOccurred()
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            onRoleSelected(role)
        }
    }
}

// MARK: - Role Card Component

struct RoleCard: View {
    let icon: String
    let title: String
    let features: [String]
    let role: FamilyRole
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: Spacing.m) {
                // Icon
                Text(icon)
                    .font(.system(size: 60))
                
                // Title
                Text(title)
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.white)
                
                // Features
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    ForEach(features, id: \.self) { feature in
                        HStack(spacing: 4) {
                            Text("•")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text(feature)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(width: 140, height: 160)  // Исправлено: 140 вместо 148 (безопасный размер!)
            .padding(Spacing.m)
            .background(
                isSelected
                    ? Color(red: 0.376, green: 0.647, blue: 0.980).opacity(0.3)  // Электрический синий из иконки!
                    : Color.white.opacity(0.1)
            )
            .cornerRadius(16)
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(
                        isSelected ? Color(red: 0.729, green: 0.902, blue: 0.992) : Color.clear,  // Sirius голубой!
                        lineWidth: 2
                    )
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Family Role Enum

enum FamilyRole: String, Codable {
    case parent = "parent"
    case child = "child"
    case elderly = "elderly"
    case other = "other"
}

// MARK: - Preview

struct RoleSelectionModal_Previews: PreviewProvider {
    static var previews: some View {
        RoleSelectionModal(
            isPresented: .constant(true),
            selectedRole: .constant(nil),
            onRoleSelected: { _ in }
        )
    }
}

