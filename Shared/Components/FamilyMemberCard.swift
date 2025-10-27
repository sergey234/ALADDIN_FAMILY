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
            case .protected: return .green
            case .warning: return .orange
            case .danger: return .red
            case .offline: return .gray
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
            VStack(spacing: 4) {
                // Верхняя часть: Аватар и имя
                HStack(spacing: 4) {
                    Text(avatar)
                        .font(.system(size: 16))
                    
                    Text(name)
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                        .lineLimit(1)
                }
                
                // Роль
                Text(role.label)
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.9))
                    .lineLimit(1)
                
                Spacer()
                
                // Статус
                Text(status.indicator)
                    .font(.system(size: 28))
                    .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: status)
            }
            .frame(height: 90)
            .frame(maxWidth: .infinity)
            .padding(8)
            .background(Color(red: 0.96, green: 0.62, blue: 0.04).opacity(0.1))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(red: 0.96, green: 0.62, blue: 0.04), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

#if DEBUG
struct FamilyMemberCard_Previews: PreviewProvider {
    static var previews: some View {
    VStack(spacing: 16) {
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
    .background(
        LinearGradient(
            colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    )
    }
}
#endif



