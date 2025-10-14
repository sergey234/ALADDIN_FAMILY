import SwiftUI

/**
 * 🎉 Registration Success Modal
 * Модальное окно успешной регистрации
 */
struct RegistrationSuccessModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    let onContinue: () -> Void
    
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
                // Иконка успеха
                Text("🎉")
                    .font(.system(size: 80))
                
                // Заголовок
                Text("Регистрация успешна!")
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                
                // Текст
                Text("Добро пожаловать в ALADDIN! Ваша семья теперь под защитой.")
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                
                // Кнопка
                PrimaryButton("Продолжить") {
                    onContinue()
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
}

#if DEBUG
struct RegistrationSuccessModal_Previews: PreviewProvider {
    static var previews: some View {
        RegistrationSuccessModal(
            isPresented: .constant(true),
            onContinue: { print("Продолжить") }
        )
    }
}
#endif
