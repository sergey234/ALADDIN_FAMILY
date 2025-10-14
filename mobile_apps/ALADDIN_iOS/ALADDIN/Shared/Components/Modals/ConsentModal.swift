import SwiftUI

/**
 * ✅ Consent Modal
 * Модальное окно согласия на обработку данных
 */
struct ConsentModal: View {
    
    // MARK: - Properties
    
    @Binding var isPresented: Bool
    let onAccept: () -> Void
    let onDecline: () -> Void
    
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
                Text("Согласие на обработку данных")
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                
                // Текст
                Text("Для обеспечения безопасности вашей семьи мы обрабатываем персональные данные в соответствии с политикой конфиденциальности.")
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                
                // Кнопки
                HStack(spacing: Spacing.m) {
                    SecondaryButton("Отклонить") {
                        onDecline()
                        isPresented = false
                    }
                    
                    PrimaryButton("Принять") {
                        onAccept()
                        isPresented = false
                    }
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
struct ConsentModal_Previews: PreviewProvider {
    static var previews: some View {
        ConsentModal(
            isPresented: .constant(true),
            onAccept: { print("Принято") },
            onDecline: { print("Отклонено") }
        )
    }
}
#endif
