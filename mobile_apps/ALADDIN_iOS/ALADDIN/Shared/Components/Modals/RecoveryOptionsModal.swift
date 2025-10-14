import SwiftUI

/**
 * 🔐 Recovery Options Modal
 * Модальное окно восстановления доступа
 */
struct RecoveryOptionsModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    let onEmailRecovery: () -> Void
    let onPhoneRecovery: () -> Void
    let onSecurityQuestions: () -> Void
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            Color.black.opacity(0.5)
                .ignoresSafeArea()
                .onTapGesture {
                    isPresented = false
                }
            
            // Модальное окно
            VStack(spacing: Spacing.l) {
                // Заголовок
                Text("Восстановление доступа")
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                
                // Опции восстановления
                VStack(spacing: Spacing.m) {
                    recoveryOption(
                        icon: "envelope.fill",
                        title: "Email восстановление",
                        subtitle: "Отправить код на email"
                    ) {
                        onEmailRecovery()
                        isPresented = false
                    }
                    
                    recoveryOption(
                        icon: "phone.fill",
                        title: "SMS восстановление",
                        subtitle: "Отправить код на телефон"
                    ) {
                        onPhoneRecovery()
                        isPresented = false
                    }
                    
                    recoveryOption(
                        icon: "questionmark.circle.fill",
                        title: "Секретные вопросы",
                        subtitle: "Ответить на вопросы безопасности"
                    ) {
                        onSecurityQuestions()
                        isPresented = false
                    }
                }
                
                // Кнопка отмены
                SecondaryButton("Отмена") {
                    isPresented = false
                }
            }
            .padding(Spacing.xl)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundLight)
            )
            .padding(Spacing.l)
        }
    }
    
    // MARK: - Recovery Option
    
    private func recoveryOption(
        icon: String,
        title: String,
        subtitle: String,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            HStack(spacing: Spacing.m) {
                Image(systemName: icon)
                    .font(.system(size: 24))
                    .foregroundColor(.primaryBlue)
                    .frame(width: 40, height: 40)
                    .background(
                        Circle()
                            .fill(Color.primaryBlue.opacity(0.1))
                    )
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

#if DEBUG
struct RecoveryOptionsModal_Previews: PreviewProvider {
    static var previews: some View {
        RecoveryOptionsModal(
            isPresented: .constant(true),
            onEmailRecovery: { print("Email восстановление") },
            onPhoneRecovery: { print("SMS восстановление") },
            onSecurityQuestions: { print("Секретные вопросы") }
        )
    }
}
#endif
