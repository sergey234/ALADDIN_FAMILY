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
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    if let icon = icon {
                        Image(systemName: icon)
                            .font(.system(size: 20, weight: .semibold))
                    }
                    
                    Text(title)
                        .font(.system(size: 16, weight: .semibold))
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 50)
            .foregroundColor(.white)
            .background(
                // Градиент как в HTML
                LinearGradient(
                    colors: isDisabled
                        ? [Color.gray, Color.gray.opacity(0.8)]
                        : [Color.blue, Color.blue.opacity(0.8)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .cornerRadius(12)
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

struct PrimaryButton_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 16) {
        // Обычная кнопка
        PrimaryButton("Продолжить") {
            print("Нажато!")
        }
        
        // Кнопка с иконкой
        PrimaryButton("Подключить защиту сети", icon: "shield.fill") {
            print("Защита сети включается...")
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
        .background(Color.black.opacity(0.1))
    }
}



