import SwiftUI

/// 📇 Status Card
/// Карточка со статусом (используется на главном экране и в семье)
/// Источник дизайна: HTML .status-card
struct StatusCard: View {
    
    // MARK: - Properties
    
    let icon: String
    let title: String
    let value: String
    let status: StatusType
    let action: (() -> Void)?
    
    // MARK: - Status Type
    
    enum StatusType {
        case protected  // 🟢 Защищено
        case threat     // 🔴 Угроза
        case warning    // ⚠️ Предупреждение
        case neutral    // ⚪ Нейтрально
        
        var color: Color {
            switch self {
            case .protected: return .statusProtected
            case .threat: return .statusThreat
            case .warning: return .statusWarning
            case .neutral: return .textSecondary
            }
        }
        
        var indicator: String {
            switch self {
            case .protected: return "🟢"
            case .threat: return "🔴"
            case .warning: return "⚠️"
            case .neutral: return "⚪"
            }
        }
    }
    
    // MARK: - Init
    
    init(
        icon: String,
        title: String,
        value: String,
        status: StatusType = .neutral,
        action: (() -> Void)? = nil
    ) {
        self.icon = icon
        self.title = title
        self.value = value
        self.status = status
        self.action = action
    }
    
    // MARK: - Body
    
    var body: some View {
        Button(action: {
            if let action = action {
                let generator = UIImpactFeedbackGenerator(style: .light)
                generator.impactOccurred()
                action()
            }
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.primaryBlue.opacity(0.3), Color.primaryBlue.opacity(0.1)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 56, height: 56)
                    
                    Image(systemName: icon)
                        .font(.system(size: 24, weight: .semibold))
                        .foregroundColor(.secondaryGold)
                }
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Text(value)
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                }
                
                Spacer()
                
                // Индикатор статуса
                VStack(spacing: Spacing.xxs) {
                    Text(status.indicator)
                        .font(.system(size: 20))
                    
                    Circle()
                        .fill(status.color)
                        .frame(width: Size.statusIndicator, height: Size.statusIndicator)
                }
            }
            .padding(Spacing.cardPadding)
            .background(
                // Градиент фона как в HTML
                LinearGradient.cardGradient
            )
            .cornerRadius(CornerRadius.large)
            .cardShadow()
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(action == nil)
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: Spacing.m) {
        // Защищено
        StatusCard(
            icon: "shield.fill",
            title: "VPN Статус",
            value: "Защищено",
            status: .protected
        ) {
            print("Открыть VPN")
        }
        
        // Угроза
        StatusCard(
            icon: "exclamationmark.triangle.fill",
            title: "Угрозы",
            value: "3 обнаружено",
            status: .threat
        ) {
            print("Показать угрозы")
        }
        
        // Предупреждение
        StatusCard(
            icon: "eye.fill",
            title: "Мошенники",
            value: "1 подозрительный",
            status: .warning
        ) {
            print("Показать мошенников")
        }
        
        // Нейтральная (без действия)
        StatusCard(
            icon: "chart.bar.fill",
            title: "Статистика",
            value: "47 угроз за неделю",
            status: .neutral
        )
    }
    .padding()
    .background(Color.backgroundDark)
}




