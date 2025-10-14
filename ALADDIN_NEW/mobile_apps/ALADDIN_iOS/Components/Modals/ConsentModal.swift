import SwiftUI

struct ConsentModal: View {
    @Binding var isPresented: Bool
    let onAccept: () -> Void
    let onReadMore: () -> Void
    
    @State private var isAnimating = false
    
    var body: some View {
        ZStack {
            // Затемнённый фон с размытием (Glassmorphism)
            Color.black.opacity(0.85)
                .ignoresSafeArea()
                .background(
                    .ultraThinMaterial
                )
                .blur(radius: isAnimating ? 0 : 20)
            
            // Модальное окно
            VStack(spacing: 0) {
                // Заголовок
                consentHeader
                    .padding(.bottom, 20)
                
                // Прокручиваемый контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: 12) {
                        // ❌ Что НЕ собираем
                        notCollectingSection
                        
                        // ✅ Военные технологии
                        militaryTechSection
                        
                        // 🛡️ Гарантии
                        guaranteesSection
                    }
                }
                .frame(maxHeight: 280)
                
                // Кнопки
                buttonsSection
                    .padding(.top, 12)
                
                // Юридический текст
                legalText
                    .padding(.top, 10)
            }
            .padding(25)
            .frame(maxWidth: 340)
            .background(
                // Космический градиент с glassmorphism
                LinearGradient(
                    colors: [
                        Color(hex: "#0F172A"),
                        Color(hex: "#1E3A8A"),
                        Color(hex: "#3B82F6")
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .overlay(
                    Color.white.opacity(0.05) // Glassmorphism overlay
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: 20))
            .overlay(
                RoundedRectangle(cornerRadius: 20)
                    .stroke(
                        LinearGradient(
                            colors: [
                                Color(hex: "#FCD34D").opacity(0.5),
                                Color(hex: "#F59E0B").opacity(0.3)
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 2
                    )
            )
            .shadow(color: Color.black.opacity(0.5), radius: 30, x: 0, y: 20)
            .scaleEffect(isAnimating ? 1 : 0.8)
            .opacity(isAnimating ? 1 : 0)
            .offset(y: isAnimating ? 0 : 50)
        }
        .onAppear {
            withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                isAnimating = true
            }
        }
    }
    
    // MARK: - Заголовок
    private var consentHeader: some View {
        VStack(spacing: 10) {
            // Лого с пульсацией
            Text("🛡️")
                .font(.system(size: 48))
                .scaleEffect(isAnimating ? 1.05 : 1.0)
                .animation(
                    .easeInOut(duration: 2.0).repeatForever(autoreverses: true),
                    value: isAnimating
                )
            
            Text("ALADDIN")
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(Color(hex: "#FCD34D"))
            
            Text("Добро пожаловать в систему\nсемейной безопасности!")
                .font(.system(size: 13))
                .foregroundColor(.white.opacity(0.8))
                .multilineTextAlignment(.center)
                .lineSpacing(4)
        }
    }
    
    // MARK: - ❌ Что НЕ собираем
    private var notCollectingSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("❌ Мы НЕ собираем ваши данные:")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(Color(hex: "#FCD34D"))
            
            VStack(alignment: .leading, spacing: 6) {
                Text("• Имя, email, телефон")
                Text("• Адрес, паспортные данные")
                Text("• История посещений")
                Text("• Личные сообщения")
            }
            .font(.system(size: 12))
            .foregroundColor(.white.opacity(0.9))
        }
        .padding(15)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            Color.black.opacity(0.3)
                .overlay(
                    Color.white.opacity(0.03) // Glassmorphism
                )
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
    
    // MARK: - ✅ Военные технологии
    private var militaryTechSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("✅ Военные технологии защиты:")
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(Color(hex: "#10B981"))
            
            VStack(alignment: .leading, spacing: 4) {
                Text("🆔 Только персональный ID номер")
                Text("🔐 AES-256-GCM (банковский сейф А+)")
                Text("🔒 ChaCha20-Poly1305 (защита ⭐⭐⭐⭐⭐)")
                Text("🛡️ XChaCha20-Poly1305 (космический уровень)")
                Text("🇷🇺 Российские серверы (152-ФЗ РФ)")
                Text("📊 Обезличенная статистика")
            }
            .font(.system(size: 11))
            .foregroundColor(.white.opacity(0.9))
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [
                    Color(hex: "#10B981").opacity(0.15),
                    Color(hex: "#059669").opacity(0.10)
                ],
                startPoint: .leading,
                endPoint: .trailing
            )
            .overlay(
                Color.white.opacity(0.05) // Glassmorphism
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color(hex: "#10B981"), lineWidth: 1)
        )
    }
    
    // MARK: - 🛡️ Гарантии
    private var guaranteesSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("🛡️ Наши гарантии:")
                .font(.system(size: 11, weight: .bold))
                .foregroundColor(Color(hex: "#10B981"))
            
            VStack(alignment: .leading, spacing: 3) {
                Text("✅ Полная анонимность")
                Text("✅ Шифрование E2E (сквозное)")
                Text("✅ Zero-logs VPN (нет логов)")
                Text("✅ Соответствие 152-ФЗ")
            }
            .font(.system(size: 11))
            .foregroundColor(.white.opacity(0.9))
        }
        .padding(15)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            Color.black.opacity(0.2)
                .overlay(
                    Color.white.opacity(0.03) // Glassmorphism
                )
        )
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
    
    // MARK: - Кнопки
    private var buttonsSection: some View {
        HStack(spacing: 10) {
            // Кнопка "Подробнее"
            Button(action: {
                onReadMore()
            }) {
                Text("Подробнее")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 48)
                    .background(
                        Color.white.opacity(0.1)
                            .overlay(
                                Color.white.opacity(0.05) // Glassmorphism
                            )
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.white.opacity(0.3), lineWidth: 1)
                    )
            }
            .buttonStyle(ScaleButtonStyle())
            
            // Кнопка "Принять ✓"
            Button(action: {
                acceptWithAnimation()
            }) {
                Text("Принять ✓")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 48)
                    .background(
                        LinearGradient(
                            colors: [
                                Color(hex: "#FCD34D"),
                                Color(hex: "#F59E0B"),
                                Color(hex: "#D97706")
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                        .overlay(
                            Color.white.opacity(0.1) // Glassmorphism shine
                        )
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .shadow(color: Color(hex: "#F59E0B").opacity(0.5), radius: 15, x: 0, y: 5)
            }
            .buttonStyle(PulseButtonStyle())
        }
    }
    
    // MARK: - Юридический текст
    private var legalText: some View {
        VStack(spacing: 4) {
            Text("Нажимая кнопку \"Принять\", вы подтверждаете,")
                .font(.system(size: 10))
                .foregroundColor(.white.opacity(0.7))
            
            (Text("что ознакомлены и согласны с ")
                .foregroundColor(.white.opacity(0.7)) +
             Text("Политикой конфиденциальности")
                .foregroundColor(Color(hex: "#3B82F6"))
                .underline() +
             Text(" системы семейной безопасности ALADDIN и Политикой обработки данных VPN-сервиса в соответствии с требованиями ")
                .foregroundColor(.white.opacity(0.7)) +
             Text("Федерального закона от 27.07.2006 № 152-ФЗ \"О персональных данных\" (статья 9)")
                .foregroundColor(.white.opacity(0.7))
                .bold()
            )
            .font(.system(size: 10))
            .multilineTextAlignment(.center)
        }
        .padding(10)
        .background(
            Color.black.opacity(0.2)
                .overlay(
                    Color.white.opacity(0.02) // Glassmorphism
                )
        )
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
    
    // MARK: - Actions
    private func acceptWithAnimation() {
        withAnimation(.spring(response: 0.3)) {
            isAnimating = false
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            onAccept()
            isPresented = false
        }
    }
}

// MARK: - Button Styles
struct ScaleButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .animation(.spring(response: 0.2), value: configuration.isPressed)
    }
}

struct PulseButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 1.05 : 1.0)
            .animation(.spring(response: 0.2), value: configuration.isPressed)
    }
}

// MARK: - Preview
struct ConsentModal_Previews: PreviewProvider {
    static var previews: some View {
        ConsentModal(
            isPresented: .constant(true),
            onAccept: {
                print("Consent accepted!")
            },
            onReadMore: {
                print("Read more tapped!")
            }
        )
    }
}



