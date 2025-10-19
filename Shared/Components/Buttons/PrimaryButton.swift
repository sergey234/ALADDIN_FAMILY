import SwiftUI

/// 🔘 Primary Button
/// Основная кнопка ALADDIN (синяя, заполненная)
/// Источник дизайна: HTML .primary-button
struct PrimaryButton: View {
    
    // MARK: - Properties
    
    let title: String
    let icon: String?
    let action: () -> Void
    let isLoading: Bool
    let isDisabled: Bool
    
    // MARK: - Init
    
    init(
        _ title: String,
        icon: String? = nil,
        isLoading: Bool = false,
        isDisabled: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.action = action
        self.isLoading = isLoading
        self.isDisabled = isDisabled
    }
    
    // MARK: - Body
    
    var body: some View {
        Button(action: {
            if !isLoading && !isDisabled {
                // Haptic feedback (вибрация при нажатии)
                let generator = UIImpactFeedbackGenerator(style: .medium)
                generator.impactOccurred()
                
                action()
            }
        }) {
            HStack(spacing: Spacing.xs) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    if let icon = icon {
                        Image(systemName: icon)
                            .font(.system(size: 20, weight: .semibold))
                    }
                    
                    Text(title)
                        .font(.button)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: Size.buttonHeight)
            .foregroundColor(.white)
            .background(
                // Градиент как в HTML
                LinearGradient(
                    colors: isDisabled
                        ? [Color.gray, Color.gray.opacity(0.8)]
                        : [Color.primaryBlue, Color.primaryBlue.opacity(0.8)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(CornerRadius.medium)
            .cardShadow()
            .opacity(isDisabled ? 0.6 : 1.0)
        }
        .disabled(isDisabled || isLoading)
        // Анимация нажатия
        .scaleEffect(isDisabled ? 1.0 : 1.0)
        .animation(.easeInOut(duration: 0.1), value: isDisabled)
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: Spacing.m) {
        // Обычная кнопка
        PrimaryButton("Продолжить") {
            print("Нажато!")
        }
        
        // Кнопка с иконкой
        PrimaryButton("Подключить VPN", icon: "shield.fill") {
            print("VPN включается...")
        }
        
        // Кнопка в состоянии загрузки
        PrimaryButton("Загрузка...", isLoading: true) {
            // Не выполнится во время загрузки
        }
        
        // Отключённая кнопка
        PrimaryButton("Недоступно", isDisabled: true) {
            // Не выполнится
        }
    }
    .padding()
    .background(Color.backgroundDark)
}



