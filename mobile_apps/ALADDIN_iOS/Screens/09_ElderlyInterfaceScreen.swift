import SwiftUI

/// 👴 Elderly Interface Screen
/// Интерфейс для пожилых - упрощённый с крупными элементами
/// Источник дизайна: /mobile/wireframes/07_elderly_interface.html
struct ElderlyInterfaceScreen: View {
    
    // MARK: - State
    
    @State private var selectedTab: Int = 0
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон (контрастный для пожилых)
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Простая навигация
                elderlyHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.xl) {
                        // Приветствие
                        greetingCard
                        
                        // Очень большие кнопки
                        bigButtonsList
                        
                        // Кнопка SOS
                        sosButton
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.l)
                }
            }
        }
    }
    
    // MARK: - Elderly Header
    
    private var elderlyHeader: some View {
        HStack(spacing: Spacing.m) {
            // Аватар
            Text("👴")
                .font(.system(size: 50))
                .frame(width: 70, height: 70)
                .background(
                    Circle()
                        .fill(Color.white.opacity(0.2))
                )
            
            // Приветствие
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("Здравствуйте!")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(.white)
                
                Text("Вы под защитой")
                    .font(.system(size: 20))
                    .foregroundColor(.white.opacity(0.8))
            }
            
            Spacer()
        }
        .padding(Spacing.cardPadding)
        .background(
            Color.white.opacity(0.1)
        )
    }
    
    // MARK: - Greeting Card
    
    private var greetingCard: some View {
        VStack(spacing: Spacing.l) {
            Text("✅")
                .font(.system(size: 80))
            
            Text("ВСЁ ХОРОШО")
                .font(.system(size: 32, weight: .bold))
                .foregroundColor(.successGreen)
            
            Text("Угроз не обнаружено")
                .font(.system(size: 20))
                .foregroundColor(.white.opacity(0.9))
        }
        .padding(Spacing.xl)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.xlarge)
                .fill(Color.white.opacity(0.15))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Big Buttons List
    
    private var bigButtonsList: some View {
        VStack(spacing: Spacing.l) {
            // Позвонить родным
            bigElderlyButton(
                icon: "📞",
                title: "ПОЗВОНИТЬ РОДНЫМ",
                subtitle: "Быстрый набор",
                color: .successGreen
            )
            
            // Безопасность
            bigElderlyButton(
                icon: "🛡️",
                title: "БЕЗОПАСНОСТЬ",
                subtitle: "Статус защиты",
                color: .primaryBlue
            )
            
            // Инструкции
            bigElderlyButton(
                icon: "📖",
                title: "ИНСТРУКЦИИ",
                subtitle: "Помощь и советы",
                color: .warningOrange
            )
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func bigElderlyButton(
        icon: String,
        title: String,
        subtitle: String,
        color: Color
    ) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .heavy)
            generator.impactOccurred()
            print(title)
        }) {
            HStack(spacing: Spacing.l) {
                // Иконка
                Text(icon)
                    .font(.system(size: 56))
                    .frame(width: 80, height: 80)
                    .background(
                        Circle()
                            .fill(color.opacity(0.2))
                    )
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(title)
                        .font(.system(size: 22, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text(subtitle)
                        .font(.system(size: 18))
                        .foregroundColor(.white.opacity(0.8))
                }
                
                Spacer()
            }
            .padding(Spacing.l)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(color.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .stroke(color, lineWidth: 3)
                    )
            )
            .shadow(color: color.opacity(0.3), radius: 12, x: 0, y: 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - SOS Button
    
    private var sosButton: some View {
        Button(action: {
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(.warning)
            print("SOS!")
        }) {
            VStack(spacing: Spacing.m) {
                Text("🚨")
                    .font(.system(size: 64))
                
                Text("КНОПКА SOS")
                    .font(.system(size: 28, weight: .heavy))
                    .foregroundColor(.white)
                
                Text("Экстренная помощь")
                    .font(.system(size: 18))
                    .foregroundColor(.white.opacity(0.9))
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, Spacing.xl)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.xlarge)
                    .fill(
                        LinearGradient(
                            colors: [Color.dangerRed, Color(hex: "#DC2626")],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
            )
            .shadow(color: Color.dangerRed.opacity(0.5), radius: 20, x: 0, y: 8)
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Preview

#Preview {
    ChildInterfaceScreen()
}



