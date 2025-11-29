import SwiftUI

/// 🔘 ALADDIN Toggle
/// Кастомный переключатель вкл/выкл с дизайном ALADDIN
/// Источник: HTML toggle switches на 09_settings.html
struct ALADDINToggle: View {
    
    // MARK: - Properties
    
    let title: String
    let subtitle: String?
    let icon: String?
    @Binding var isOn: Bool
    let isDisabled: Bool
    
    // MARK: - Init
    
    init(
        _ title: String,
        subtitle: String? = nil,
        icon: String? = nil,
        isOn: Binding<Bool>,
        isDisabled: Bool = false
    ) {
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self._isOn = isOn
        self.isDisabled = isDisabled
    }
    
    // MARK: - Body
    
    var body: some View {
        Button(action: {
            if !isDisabled {
                let generator = UIImpactFeedbackGenerator(style: .light)
                generator.impactOccurred()
                
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    isOn.toggle()
                }
            }
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка
                if let icon = icon {
                    Text(icon)
                        .font(.system(size: 28))
                }
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.body)
                        .foregroundColor(isDisabled ? .textSecondary : .textPrimary)
                    
                    if let subtitle = subtitle {
                        Text(subtitle)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
                
                // Переключатель
                ZStack {
                    // Фон
                    RoundedRectangle(cornerRadius: CornerRadius.full)
                        .fill(
                            isOn ?
                            LinearGradient(
                                colors: [Color.primaryBlue, Color.secondaryBlue],
                                startPoint: .leading,
                                endPoint: .trailing
                            ) :
                            LinearGradient(
                                colors: [Color.backgroundMedium, Color.backgroundMedium],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: Size.toggleWidth, height: Size.toggleHeight)
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.full)
                                .stroke(
                                    isOn ? Color.primaryBlue : Color.white.opacity(0.2),
                                    lineWidth: 1
                                )
                        )
                    
                    // Ползунок
                    Circle()
                        .fill(Color.white)
                        .frame(width: Size.toggleKnob, height: Size.toggleKnob)
                        .shadow(color: Color.black.opacity(0.3), radius: 2, x: 0, y: 1)
                        .offset(
                            x: isOn ?
                                (Size.toggleWidth / 2 - Size.toggleKnob / 2 - 3) :
                                -(Size.toggleWidth / 2 - Size.toggleKnob / 2 - 3)
                        )
                }
                .opacity(isDisabled ? 0.5 : 1.0)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(isDisabled)
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: Spacing.m) {
        // Включено
        ALADDINToggle(
            "VPN Защита",
            subtitle: "Шифрование трафика",
            icon: "🛡️",
            isOn: .constant(true)
        )
        
        // Выключено
        ALADDINToggle(
            "Блокировка рекламы",
            subtitle: "Блокирует назойливую рекламу",
            icon: "🚫",
            isOn: .constant(false)
        )
        
        // Без иконки
        ALADDINToggle(
            "Уведомления",
            isOn: .constant(true)
        )
        
        // Отключено
        ALADDINToggle(
            "Премиум функция",
            subtitle: "Доступно в Premium",
            icon: "⭐",
            isOn: .constant(false),
            isDisabled: true
        )
    }
    .padding()
    .background(LinearGradient.backgroundGradient)
}



