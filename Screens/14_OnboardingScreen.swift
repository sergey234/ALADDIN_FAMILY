import SwiftUI

/// 👋 Onboarding Screen
/// Экран онбординга - первое знакомство с приложением + прогрессивная регистрация
/// Источник: стандартный паттерн iOS онбординга
struct OnboardingScreen: View {
    
    // MARK: - State
    
    @State private var currentPage: Int = 0
    @State private var isCompleted: Bool = false
    @State private var showJoinFamily: Bool = false
    @State private var showRecovery: Bool = false
    
    // @StateObject private var registrationVM = FamilyRegistrationViewModel()
    
    struct OnboardingPage {
        let icon: String
        let title: String
        let description: String
        let color: Color
    }
    
    private let pages: [OnboardingPage] = [
        OnboardingPage(
            icon: "🛡️",
            title: "ЗАЩИТА СЕМЬИ",
            description: "Комплексная защита для всей вашей семьи от цифровых угроз",
            color: Color.primaryBlue
        ),
        OnboardingPage(
            icon: "🤖",
            title: "AI ПОМОЩНИК",
            description: "Умный ассистент всегда готов помочь с вопросами безопасности",
            color: Color.successGreen
        ),
        OnboardingPage(
            icon: "👶",
            title: "РОДИТЕЛЬСКИЙ КОНТРОЛЬ",
            description: "Полный контроль над устройствами детей и их безопасностью",
            color: Color.orange
        ),
        OnboardingPage(
            icon: "📊",
            title: "АНАЛИТИКА",
            description: "Подробная статистика угроз и защиты в реальном времени",
            color: Color.red
        )
    ]
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Кнопка пропустить
                HStack {
                    Spacer()
                    
                    Button(action: {
                        isCompleted = true
                    }) {
                        Text("Пропустить")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                
                // Контент страниц
                TabView(selection: $currentPage) {
                    ForEach(0..<pages.count, id: \.self) { index in
                        onboardingPage(pages[index])
                            .tag(index)
                    }
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                
                // Индикаторы страниц
                HStack(spacing: Spacing.sm) {
                    ForEach(0..<pages.count, id: \.self) { index in
                        Circle()
                            .fill(currentPage == index ? Color.primaryBlue : Color.textSecondary.opacity(0.3))
                            .frame(width: currentPage == index ? 12 : 8, height: currentPage == index ? 12 : 8)
                            .animation(.spring(), value: currentPage)
                    }
                }
                .padding(.vertical, Spacing.lg)
                
                // Кнопки (на последнем слайде показываем дополнительные)
                VStack(spacing: Spacing.m) {
                    // Основная кнопка
                    Button(action: {
                        if currentPage < pages.count - 1 {
                            withAnimation {
                                currentPage += 1
                            }
                        } else {
                            // Начать регистрацию
                            isCompleted = true
                        }
                    }) {
                        Text(currentPage < pages.count - 1 ? "ПРОДОЛЖИТЬ" : "НАЧАТЬ")
                            .font(.buttonText)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 50)
                            .background(
                                LinearGradient(
                                    colors: [Color.primaryBlue, Color.secondaryBlue],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .cornerRadius(CornerRadius.large)
                    }
                    
                    // Дополнительные кнопки на последнем слайде
                    if currentPage == pages.count - 1 {
                        HStack(spacing: Spacing.m) {
                            // У меня есть код
                            Button(action: {
                                showJoinFamily = true
                                let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                                impactFeedback.impactOccurred()
                            }) {
                                Text("У МЕНЯ ЕСТЬ КОД")
                                    .font(.caption)
                                    .foregroundColor(.secondaryGold)
                                    .frame(maxWidth: .infinity)
                                    .frame(height: 44)
                                    .background(Color.secondaryGold.opacity(0.15))
                                    .cornerRadius(CornerRadius.medium)
                            }
                            
                            // Восстановить доступ
                            Button(action: {
                                showRecovery = true
                                let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                                impactFeedback.impactOccurred()
                            }) {
                                Text("ВОССТАНОВИТЬ")
                                    .font(.caption)
                                    .foregroundColor(.primaryBlue)
                                    .frame(maxWidth: .infinity)
                                    .frame(height: 44)
                                    .background(Color.primaryBlue.opacity(0.15))
                                    .cornerRadius(CornerRadius.medium)
                            }
                        }
                        .transition(.move(edge: .bottom).combined(with: .opacity))
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                .padding(.bottom, Spacing.xl)
            }
        }
        .fullScreenCover(isPresented: $isCompleted) {
            MainScreen()
        }
        .sheet(isPresented: $showJoinFamily) {
            QRScannerModal(
                isPresented: $showJoinFamily
            )
        }
        .sheet(isPresented: $showRecovery) {
            RecoveryOptionsModal(
                isPresented: $showRecovery
            )
        }
    }
    
    // MARK: - Onboarding Page
    
    private func onboardingPage(_ page: OnboardingPage) -> some View {
        VStack(spacing: Spacing.xxl) {
            Spacer()
            
            // Иконка
            ZStack {
                Circle()
                    .fill(page.color.opacity(0.2))
                    .frame(width: 200, height: 200)
                
                Circle()
                    .fill(page.color.opacity(0.1))
                    .frame(width: 160, height: 160)
                
                Text(page.icon)
                    .font(.system(size: 80))
            }
            
            // Текст
            VStack(spacing: Spacing.m) {
                Text(page.title)
                    .font(.system(size: 32, weight: .bold))
                    .foregroundColor(.white)
                    .multilineTextAlignment(.center)
                
                Text(page.description)
                    .font(.system(size: 18))
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineSpacing(6)
            }
            .padding(.horizontal, Spacing.xl)
            
            Spacer()
        }
    }
}

// MARK: - Preview

struct OnboardingScreen_Previews: PreviewProvider {
    static var previews: some View {
        OnboardingScreen()
    }
}

