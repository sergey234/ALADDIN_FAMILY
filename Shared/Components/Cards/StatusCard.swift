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
            case .protected: return .green
            case .threat: return .red
            case .warning: return .orange
            case .neutral: return .gray
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
            HStack(spacing: 16) {
                // Иконка
                ZStack {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color.blue.opacity(0.3), Color.blue.opacity(0.1)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 56, height: 56)
                    
                    Image(systemName: icon)
                        .font(.system(size: 24, weight: .semibold))
                        .foregroundColor(.orange)
                }
                
                // Текст
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Text(value)
                        .font(.system(size: 18, weight: .bold))
                        .foregroundColor(.primary)
                }
                
                Spacer()
                
                // Индикатор статуса
                VStack(spacing: 4) {
                    Text(status.indicator)
                        .font(.system(size: 20))
                    
                    Circle()
                        .fill(status.color)
                        .frame(width: 8, height: 8)
                }
            }
            .padding(16)
            .background(
                // Градиент фона как в HTML
                LinearGradient(
                    colors: [Color.blue.opacity(0.1), Color.purple.opacity(0.05)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(16)
            .cardShadow()
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(action == nil)
    }
}

// MARK: - Preview

struct StatusCard_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 16) {
        // Защищено
        StatusCard(
            icon: "shield.fill",
            title: "Статус защиты сети",
            value: "Защищено",
            status: .protected
        ) {
            print("Открыть защиту сети")
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
        .background(Color.black.opacity(0.1))
    }
}



