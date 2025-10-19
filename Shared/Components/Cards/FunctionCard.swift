import SwiftUI

/// 📇 Function Card
/// Карточка функции для главного экрана (Семья, Защита, Аналитика, AI)
/// Источник дизайна: HTML .function-card на 01_main_screen.html
struct FunctionCard: View {
    
    // MARK: - Properties
    
    let icon: String
    let title: String
    let subtitle: String
    let status: StatusType
    let action: () -> Void
    
    // MARK: - Status Type
    
    enum StatusType {
        case active     // 🟢 Активно
        case warning    // ⚠️ Предупреждение
        case inactive   // 🔴 Неактивно
        case neutral    // ⚪ Нейтрально
        
        var indicator: String {
            switch self {
            case .active: return "🟢"
            case .warning: return "⚠️"
            case .inactive: return "🔴"
            case .neutral: return "✅"
            }
        }
        
        var color: Color {
            switch self {
            case .active: return .successGreen
            case .warning: return .warningOrange
            case .inactive: return .dangerRed
            case .neutral: return .primaryBlue
            }
        }
    }
    
    // MARK: - Init
    
    init(
        icon: String,
        title: String,
        subtitle: String,
        status: StatusType = .neutral,
        action: @escaping () -> Void
    ) {
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.status = status
        self.action = action
    }
    
    // MARK: - Body
    
    var body: some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
            action()
        }) {
            VStack(spacing: Spacing.m) {
                // Иконка
                Text(icon)
                    .font(.system(size: Size.iconLarge))
                
                // Текст
                VStack(spacing: Spacing.xxs) {
                    Text(title)
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                // Индикатор статуса
                HStack(spacing: Spacing.xxs) {
                    Circle()
                        .fill(status.color)
                        .frame(width: Size.statusIndicator, height: Size.statusIndicator)
                    
                    Text(status.indicator)
                        .font(.caption)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: Size.functionCardHeight)
            .padding(Spacing.cardPadding)
            .background(
                // Градиент как в HTML
                LinearGradient.cardGradient
                    .overlay(
                        // Glassmorphism эффект
                        Color.white.opacity(0.05)
                    )
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
        // Активная карточка
        FunctionCard(
            icon: "👨‍👩‍👧‍👦",
            title: "СЕМЬЯ",
            subtitle: "4 члена • Всё под защитой",
            status: .active
        ) {
            print("Открыть семью")
        }
        
        // Предупреждение
        FunctionCard(
            icon: "📊",
            title: "АНАЛИТИКА",
            subtitle: "47 угроз заблокировано",
            status: .warning
        ) {
            print("Открыть аналитику")
        }
        
        // Нейтральная
        FunctionCard(
            icon: "🤖",
            title: "AI ПОМОЩНИК",
            subtitle: "Всегда готов помочь",
            status: .neutral
        ) {
            print("Открыть AI")
        }
    }
    .padding()
    .background(
        LinearGradient.backgroundGradient
    )
}



