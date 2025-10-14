import SwiftUI

/**
 * 🎉 Registration Success Modal
 * Модальное окно успешного присоединения/восстановления
 * Окно #8 - показывает список членов семьи
 */

struct RegistrationSuccessModal: View {
    
    @Binding var isPresented: Bool
    let mode: SuccessMode
    let familyMembers: [FamilyMember]
    var onContinue: () -> Void
    
    // MARK: - Success Mode
    
    enum SuccessMode {
        case familyCreated    // Семья создана
        case joined           // Присоединились к семье
        case recovered        // Доступ восстановлен
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Backdrop blur
            Color.black.opacity(0.5)
                .ignoresSafeArea()
                .blur(radius: 20)
            
            // Modal content
            VStack(spacing: Spacing.xl) {
                // Celebration icon
                Text("🎉")
                    .font(.system(size: 80))
                    .scaleEffect(animationScale)
                    .onAppear {
                        withAnimation(.spring(response: 0.6, dampingFraction: 0.6)) {
                            animationScale = 1.0
                        }
                    }
                
                // Title
                Text(successTitle)
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.successGreen)
                
                // Family members list
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("👥 Ваша семья:")
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.textPrimary)
                    
                    VStack(spacing: Spacing.s) {
                        ForEach(familyMembers) { member in
                            FamilyMemberRow(member: member, isCurrentUser: member.isYou)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.white.opacity(0.05))
                    .cornerRadius(12)
                }
                
                // Continue button
                PrimaryButton(
                    title: "НАЧАТЬ ИСПОЛЬЗОВАНИЕ 🚀",
                    action: {
                        HapticFeedback.success()
                        onContinue()
                    }
                )
                .shadow(color: .successGreen.opacity(0.3), radius: 10)
            }
            .padding(Spacing.xl)
            .frame(width: 340)
            .background(
                LinearGradient(
                    colors: [Color(hex: "#1e3a5f"), Color(hex: "#2e5090")],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(24)
            .shadow(color: .black.opacity(0.5), radius: 30, x: 0, y: 20)
        }
    }
    
    // MARK: - Computed Properties
    
    @State private var animationScale: CGFloat = 0.5
    
    private var successTitle: String {
        switch mode {
        case .familyCreated:
            return "СЕМЬЯ СОЗДАНА!"
        case .joined:
            return "ВЫ ПРИСОЕДИНИЛИСЬ!"
        case .recovered:
            return "ДОСТУП ВОССТАНОВЛЕН!"
        }
    }
}

// MARK: - Family Member Model

struct FamilyMember: Identifiable {
    let id: String
    let letter: String
    let role: FamilyRole
    let ageGroup: AgeGroup
    let isYou: Bool
}

// MARK: - Family Member Row

struct FamilyMemberRow: View {
    let member: FamilyMember
    let isCurrentUser: Bool
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Icon
            Text(roleIcon)
                .font(.system(size: 24))
            
            // Info
            HStack(spacing: Spacing.xs) {
                Text(member.letter)
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(.secondaryGold)
                
                Text("-")
                    .foregroundColor(.textSecondary)
                
                Text(roleText)
                    .font(.system(size: 14))
                    .foregroundColor(.textPrimary)
                
                Text("(\(member.ageGroup.rawValue))")
                    .font(.system(size: 12))
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            // Current user badge
            if isCurrentUser {
                Text("⭐ Вы!")
                    .font(.caption)
                    .foregroundColor(.secondaryGold)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, 4)
                    .background(Color.secondaryGold.opacity(0.2))
                    .cornerRadius(6)
            }
        }
        .frame(height: 36)
    }
    
    private var roleIcon: String {
        switch member.role {
        case .parent: return "👨‍👩‍👧‍👦"
        case .child: return "👶"
        case .elderly: return "👴"
        case .other: return "👤"
        }
    }
    
    private var roleText: String {
        switch member.role {
        case .parent: return "Родитель"
        case .child: return "Ребёнок"
        case .elderly: return "Пожилой"
        case .other: return "Другой"
        }
    }
}

// MARK: - Preview

struct RegistrationSuccessModal_Previews: PreviewProvider {
    static var previews: some View {
        RegistrationSuccessModal(
            isPresented: .constant(true),
            mode: .joined,
            familyMembers: [
                FamilyMember(id: "1", letter: "А", role: .parent, ageGroup: .adult_24_55, isYou: false),
                FamilyMember(id: "2", letter: "Б", role: .child, ageGroup: .child_7_12, isYou: false),
                FamilyMember(id: "3", letter: "В", role: .child, ageGroup: .child_7_12, isYou: true)
            ],
            onContinue: {}
        )
    }
}



