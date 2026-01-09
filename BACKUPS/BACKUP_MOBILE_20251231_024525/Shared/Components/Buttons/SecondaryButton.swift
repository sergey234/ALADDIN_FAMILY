import SwiftUI

/// 🔘 Secondary Button
/// Вторичная кнопка ALADDIN (обводка, не заполненная)
/// Источник дизайна: HTML .secondary-button
struct SecondaryButton: View {
    
    // MARK: - Properties
    
    let title: String
    let icon: String?
    let action: () -> Void
    let isDisabled: Bool
    
    // MARK: - Init
    
    init(
        _ title: String,
        icon: String? = nil,
        isDisabled: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.isDisabled = isDisabled
        self.action = action
    }
    
    // MARK: - Body
    
    var body: some View {
        Button(action: {
            if !isDisabled {
                // Haptic feedback
                let generator = UIImpactFeedbackGenerator(style: .light)
                generator.impactOccurred()
                
                action()
            }
        }) {
            HStack(spacing: Spacing.xs) {
                if let icon = icon {
                    Image(systemName: icon)
                        .font(.system(size: 18, weight: .semibold))
                }
                
                Text(title)
                    .font(.button)
            }
            .frame(maxWidth: .infinity)
            .frame(height: Size.buttonHeight)
            .foregroundColor(isDisabled ? .textSecondary : .primaryBlue)
            .background(Color.clear)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .stroke(
                        isDisabled ? Color.textSecondary : Color.primaryBlue,
                        lineWidth: 2
                    )
            )
            .opacity(isDisabled ? 0.6 : 1.0)
        }
        .disabled(isDisabled)
    }
}

// MARK: - Preview

#if DEBUG
struct SecondaryButton_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: Spacing.m) {
            // Обычная кнопка
            SecondaryButton("Отменить") {
                print("Отменено")
            }
            
            // Кнопка с иконкой
            SecondaryButton("Настройки", icon: "gear") {
                print("Открыть настройки")
            }
            
            // Отключённая кнопка
            SecondaryButton("Недоступно", isDisabled: true) {
                // Не выполнится
            }
        }
        .padding()
        .background(Color.backgroundDark)
    }
}
#endif



