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
            case .active: return .green
            case .warning: return .orange
            case .inactive: return .red
            case .neutral: return .blue
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
            VStack(spacing: 16) {
                // Иконка
                Text(icon)
                    .font(.system(size: 40))
                
                // Текст
                VStack(spacing: 4) {
                    Text(title)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.primary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                
                // Индикатор статуса
                HStack(spacing: 4) {
                    Circle()
                        .fill(.green)
                        .frame(width: 8, height: 8)
                    
                    Text(status.indicator)
                        .font(.caption)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 120)
            .padding(16)
            .background(
                // Градиент как в HTML
                LinearGradient(
                    colors: [Color.blue.opacity(0.1), Color.purple.opacity(0.05)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .overlay(
                    // Glassmorphism эффект
                    Color.white.opacity(0.05)
                )
            )
            .cornerRadius(16)
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
            .cardShadow()
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

struct FunctionCard_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 16) {
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
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
    }
}



