import SwiftUI

/// 🧭 ALADDIN Navigation Bar
/// Кастомная верхняя панель навигации с дизайном ALADDIN
/// Источник: HTML navigation на всех экранах
struct ALADDINNavigationBar: View {
    
    // MARK: - Properties
    
    let title: String
    let subtitle: String?
    let leftButton: NavButton?
    let rightButtons: [NavButton]
    
    // MARK: - Nav Button
    
    struct NavButton {
        let icon: String
        let action: () -> Void
        
        init(icon: String, action: @escaping () -> Void) {
            self.icon = icon
            self.action = action
        }
    }
    
    // MARK: - Init
    
    init(
        title: String,
        subtitle: String? = nil,
        leftButton: NavButton? = nil,
        rightButtons: [NavButton] = []
    ) {
        self.title = title
        self.subtitle = subtitle
        self.leftButton = leftButton
        self.rightButtons = rightButtons
    }
    
    // MARK: - Body
    
    var body: some View {
        VStack(spacing: 0) {
            // Навигационная панель
            HStack(spacing: Spacing.m) {
                // Левая кнопка
                if let leftButton = leftButton {
                    Button(action: {
                        let generator = UIImpactFeedbackGenerator(style: .light)
                        generator.impactOccurred()
                        leftButton.action()
                    }) {
                        Image(systemName: leftButton.icon)
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundColor(.textPrimary)
                            .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                            .background(
                                Circle()
                                    .fill(Color.backgroundMedium.opacity(0.5))
                            )
                    }
                } else {
                    Spacer()
                        .frame(width: Size.navButtonSize)
                }
                
                // Заголовок
                VStack(spacing: Spacing.xxs) {
                    Text(title)
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    if let subtitle = subtitle {
                        Text(subtitle)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                .frame(maxWidth: .infinity)
                
                // Правые кнопки
                HStack(spacing: Spacing.s) {
                    ForEach(0..<rightButtons.count, id: \.self) { index in
                        Button(action: {
                            let generator = UIImpactFeedbackGenerator(style: .light)
                            generator.impactOccurred()
                            rightButtons[index].action()
                        }) {
                            Image(systemName: rightButtons[index].icon)
                                .font(.system(size: 20, weight: .semibold))
                                .foregroundColor(.textPrimary)
                                .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                                .background(
                                    Circle()
                                        .fill(Color.backgroundMedium.opacity(0.5))
                                )
                        }
                    }
                }
                .frame(width: rightButtons.isEmpty ? Size.navButtonSize : nil)
            }
            .padding(.horizontal, Spacing.m)
            .padding(.vertical, Spacing.s)
            .background(
                LinearGradient(
                    colors: [
                        Color.backgroundDark.opacity(0.95),
                        Color.backgroundDark.opacity(0.9)
                    ],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .blur(radius: 10)
            )
            
            // Разделитель
            Rectangle()
                .fill(
                    LinearGradient(
                        colors: [
                            Color.primaryBlue.opacity(0.3),
                            Color.secondaryBlue.opacity(0.1)
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .frame(height: 1)
        }
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 0) {
        // Главный экран
        ALADDINNavigationBar(
            title: "ALADDIN",
            subtitle: "AI Защита Семьи",
            rightButtons: [
                .init(icon: "bell", action: { print("Уведомления") }),
                .init(icon: "gear", action: { print("Настройки") })
            ]
        )
        
        Spacer().frame(height: 20)
        
        // Экран семьи
        ALADDINNavigationBar(
            title: "СЕМЬЯ",
            subtitle: "4 члена под защитой",
            leftButton: .init(icon: "chevron.left", action: { print("Назад") }),
            rightButtons: [
                .init(icon: "plus", action: { print("Добавить") })
            ]
        )
        
        Spacer().frame(height: 20)
        
        // Экран настроек
        ALADDINNavigationBar(
            title: "НАСТРОЙКИ",
            leftButton: .init(icon: "chevron.left", action: { print("Назад") })
        )
        
        Spacer()
    }
    .background(LinearGradient.backgroundGradient)
}




