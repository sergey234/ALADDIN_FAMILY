import SwiftUI

/// 📭 Empty State View
/// Универсальный компонент для отображения пустых состояний
/// Используется вместо дефолтных данных, когда список пуст
struct EmptyStateView: View {
    
    // MARK: - Properties
    
    let icon: String
    let title: String
    let description: String
    let actionTitle: String?
    let action: (() -> Void)?
    
    // MARK: - Init
    
    init(
        icon: String,
        title: String,
        description: String,
        actionTitle: String? = nil,
        action: (() -> Void)? = nil
    ) {
        self.icon = icon
        self.title = title
        self.description = description
        self.actionTitle = actionTitle
        self.action = action
    }
    
    // MARK: - Body
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 64))
                .opacity(0.6)
                .accessibilityLabel("Иконка \(icon)")
            
            // Заголовок
            Text(title)
                .font(.h3)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
                .accessibilityAddTraits(.isHeader)
                .accessibilityLabel("Заголовок: \(title)")
            
            // Описание
            Text(description)
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .lineLimit(nil)
                .accessibilityLabel("Описание: \(description)")
            
            // Кнопка действия (опционально)
            if let actionTitle = actionTitle, let action = action {
                Button(action: {
                    HapticFeedback.impact(.light)
                    action()
                }) {
                    Text(actionTitle)
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.secondaryGold)
                        .padding(.vertical, Spacing.s)
                        .padding(.horizontal, Spacing.m)
                        .background(Color.secondaryGold.opacity(0.1))
                        .cornerRadius(CornerRadius.medium)
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                        )
                }
                .accessibilityLabel("Действие: \(actionTitle)")
            }
        }
        .padding(Spacing.xl)
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Пустое состояние: \(title). \(description)")
    }
}

// MARK: - Preview

struct EmptyStateView_Previews: PreviewProvider {
    static var previews: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: Spacing.l) {
                    // Пример 1: С кнопкой
                    EmptyStateView(
                        icon: "👨‍👩‍👧‍👦",
                        title: "Семья ещё не добавлена",
                        description: "Члены семьи появятся здесь после присоединения к вашей семье",
                        actionTitle: "➕ Добавить членов семьи",
                        action: {
                            print("Добавить членов семьи")
                        }
                    )
                    
                    // Пример 2: Без кнопки
                    EmptyStateView(
                        icon: "💊",
                        title: "Список лекарств пуст",
                        description: "Добавьте лекарства для напоминаний о приёме"
                    )
                    
                    // Пример 3: Для детей
                    EmptyStateView(
                        icon: "📞",
                        title: "Контакты ещё не добавлены",
                        description: "Попросите родителей добавить контакты членов семьи",
                        actionTitle: "💬 Попросить родителей",
                        action: {
                            print("Попросить родителей")
                        }
                    )
                }
                .padding(.top, Spacing.xxl)
            }
        }
    }
}

