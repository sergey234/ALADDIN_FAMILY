import SwiftUI

/// 👤 Family Member Card
/// Карточка члена семьи для экрана Family
/// Источник дизайна: HTML .member-card на 02_family_screen.html
struct FamilyMemberCard: View {
    
    // MARK: - Properties
    
    let name: String
    let role: FamilyRole
    let avatar: String
    let status: ProtectionStatus
    let threatsBlocked: Int
    let lastActive: String
    let action: () -> Void
    
    // MARK: - Family Role
    
    enum FamilyRole {
        case parent      // Родитель
        case child       // Ребёнок
        case teenager    // Подросток
        case elderly     // Пожилой
        
        var label: String {
            switch self {
            case .parent: return "Родитель"
            case .child: return "Ребёнок"
            case .teenager: return "Подросток"
            case .elderly: return "Пожилой"
            }
        }
        
        var icon: String {
            switch self {
            case .parent: return "👨‍💼"
            case .child: return "👶"
            case .teenager: return "🧒"
            case .elderly: return "👴"
            }
        }
    }
    
    // MARK: - Protection Status
    
    enum ProtectionStatus {
        case protected   // 🟢 Защищён
        case warning     // ⚠️ Предупреждение
        case danger      // 🔴 Опасность
        case offline     // ⚫ Оффлайн
        
        var label: String {
            switch self {
            case .protected: return "Защищён"
            case .warning: return "Внимание"
            case .danger: return "Угроза"
            case .offline: return "Оффлайн"
            }
        }
        
        var color: Color {
            switch self {
            case .protected: return .successGreen
            case .warning: return .warningOrange
            case .danger: return .dangerRed
            case .offline: return .textSecondary
            }
        }
        
        var indicator: String {
            switch self {
            case .protected: return "🟢"
            case .warning: return "⚠️"
            case .danger: return "🔴"
            case .offline: return "⚫"
            }
        }
    }
    
    // MARK: - Init
    
    init(
        name: String,
        role: FamilyRole,
        avatar: String,
        status: ProtectionStatus,
        threatsBlocked: Int,
        lastActive: String = "Сейчас",
        action: @escaping () -> Void
    ) {
        self.name = name
        self.role = role
        self.avatar = avatar
        self.status = status
        self.threatsBlocked = threatsBlocked
        self.lastActive = lastActive
        self.action = action
    }
    
    // MARK: - Body
    
    var body: some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            action()
        }) {
            HStack(spacing: Spacing.m) {
                // Аватар
                Text(avatar)
                    .font(.system(size: Size.iconMedium))
                    .frame(width: Size.avatarSize, height: Size.avatarSize)
                    .background(
                        Circle()
                            .fill(
                                LinearGradient(
                                    colors: [
                                        Color.primaryBlue.opacity(0.3),
                                        Color.primaryBlue.opacity(0.1)
                                    ],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    )
                    .overlay(
                        Circle()
                            .stroke(status.color, lineWidth: 3)
                    )
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    // Имя и роль
                    HStack(spacing: Spacing.xs) {
                        Text(name)
                            .font(.h3)
                            .foregroundColor(.textPrimary)
                        
                        Text(role.icon)
                            .font(.caption)
                    }
                    
                    // Роль
                    Text(role.label)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    // Статистика
                    HStack(spacing: Spacing.m) {
                        // Угрозы заблокированы
                        HStack(spacing: Spacing.xxs) {
                            Text("🛡️")
                                .font(.caption)
                            Text("\(threatsBlocked)")
                                .font(.captionBold)
                                .foregroundColor(.successGreen)
                        }
                        
                        // Последняя активность
                        HStack(spacing: Spacing.xxs) {
                            Text("⏰")
                                .font(.caption)
                            Text(lastActive)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                }
                
                Spacer()
                
                // Статус
                VStack(spacing: Spacing.xs) {
                    Text(status.indicator)
                        .font(.system(size: 24))
                    
                    Text(status.label)
                        .font(.captionSmall)
                        .foregroundColor(status.color)
                }
            }
            .padding(Spacing.cardPadding)
            .background(
                LinearGradient.cardGradient
                    .overlay(Color.white.opacity(0.05))
            )
            .cornerRadius(CornerRadius.large)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
            .cardShadow()
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: Spacing.m) {
        // Родитель - защищён
        FamilyMemberCard(
            name: "Сергей",
            role: .parent,
            avatar: "👨",
            status: .protected,
            threatsBlocked: 47
        ) {
            print("Открыть профиль Сергея")
        }
        
        // Ребёнок - предупреждение
        FamilyMemberCard(
            name: "Маша",
            role: .child,
            avatar: "👧",
            status: .warning,
            threatsBlocked: 23,
            lastActive: "5 мин назад"
        ) {
            print("Открыть профиль Маши")
        }
        
        // Пожилой - оффлайн
        FamilyMemberCard(
            name: "Бабушка",
            role: .elderly,
            avatar: "👵",
            status: .offline,
            threatsBlocked: 12,
            lastActive: "2 часа назад"
        ) {
            print("Открыть профиль Бабушки")
        }
    }
    .padding()
    .background(LinearGradient.backgroundGradient)
}



