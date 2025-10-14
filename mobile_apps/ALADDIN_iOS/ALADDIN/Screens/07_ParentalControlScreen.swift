import SwiftUI

/// 👶 Parental Control Screen
/// Экран родительского контроля - управление детскими устройствами
/// Источник дизайна: /mobile/wireframes/14_parental_control_screen.html
struct ParentalControlScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var isContentFilterEnabled: Bool = true
    @State private var isAppBlockingEnabled: Bool = true
    @State private var screenTimeLimit: Double = 3
    @State private var selectedChild: String = "Маша"
    
    // НОВОЕ: Вознаграждения с единорогами 🦄
    @State private var showRewardsModal: Bool = false
    @State private var unicornBalance: Int = 245
    @State private var weeklyRewarded: Int = 128
    @State private var weeklyPunished: Int = 45
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "РОДИТЕЛЬСКИЙ КОНТРОЛЬ",
                    subtitle: "Управление для детей",
                    leftButton: .init(icon: "chevron.left") {
                        dismiss()
                    }
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Выбор ребёнка
                        childSelector
                        
                        // Статистика ребёнка
                        childStats
                        
                        // Фильтр контента
                        contentFilterSection
                        
                        // Блокировка приложений
                        appBlockingSection
                        
                        // Лимит времени экрана
                        screenTimeLimitSection
                        
                        // НОВОЕ: Вознаграждение ребёнка 🦄
                        rewardsSection
                        
                        // Быстрые действия
                        quickActionsSection
                        
                        // Spacer
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
    }
    
    // MARK: - Child Selector
    
    private var childSelector: some View {
        Button(action: {
            print("Выбрать ребёнка")
        }) {
            HStack(spacing: Spacing.m) {
                // Аватар
                Text("👧")
                    .font(.system(size: 40))
                    .frame(width: 60, height: 60)
                    .background(
                        Circle()
                            .fill(Color.primaryBlue.opacity(0.3))
                    )
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(selectedChild)
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    
                    HStack(spacing: Spacing.xs) {
                        Text("Ребёнок")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Text("•")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Text("10 лет")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.cardPadding)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(Color.backgroundMedium.opacity(0.5))
            )
            .cardShadow()
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Child Stats
    
    private var childStats: some View {
        HStack(spacing: Spacing.m) {
            statBox(icon: "⏰", value: "2:45", label: "Сегодня\nна экране", color: .successGreen)
            statBox(icon: "🚫", value: "12", label: "Заблокиров.\nсайтов", color: .dangerRed)
            statBox(icon: "📱", value: "8", label: "Доступных\nприложений", color: .primaryBlue)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func statBox(icon: String, value: String, label: String, color: Color) -> some View {
        VStack(spacing: Spacing.s) {
            Text(icon)
                .font(.system(size: 28))
            
            Text(value)
                .font(.h2)
                .foregroundColor(color)
            
            Text(label)
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
    
    // MARK: - Content Filter Section
    
    private var contentFilterSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text("🛡️")
                    .font(.system(size: 20))
                Text("ФИЛЬТР КОНТЕНТА")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                ALADDINToggle(
                    "Блокировка опасного контента",
                    subtitle: "Автоматическая блокировка",
                    icon: "🚫",
                    isOn: $isContentFilterEnabled
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - App Blocking Section
    
    private var appBlockingSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text("📱")
                    .font(.system(size: 20))
                Text("БЛОКИРОВКА ПРИЛОЖЕНИЙ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                ALADDINToggle(
                    "Ограничение приложений",
                    subtitle: "Только одобренные приложения",
                    icon: "🔒",
                    isOn: $isAppBlockingEnabled
                )
                
                Button(action: {
                    print("Управление приложениями")
                }) {
                    HStack {
                        Text("Список приложений")
                            .font(.body)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("8 разрешено")
                            .font(.caption)
                            .foregroundColor(.successGreen)
                        
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
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Screen Time Limit Section
    
    private var screenTimeLimitSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text("⏰")
                    .font(.system(size: 20))
                Text("ЛИМИТ ВРЕМЕНИ ЭКРАНА")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                ALADDINSlider(
                    "Дневной лимит",
                    subtitle: "Ограничение использования устройства",
                    icon: "⏱️",
                    value: $screenTimeLimit,
                    range: 1...12,
                    unit: " ч"
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    // MARK: - Rewards Section (НОВОЕ! 🦄)
    
    private var rewardsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text("🦄")
                    .font(.system(size: 20))
                Text("ВОЗНАГРАЖДЕНИЕ РЕБЁНКА")
                    .font(.h3)
                    .foregroundColor(Color(hex: "C084FC"))
                Spacer()
                
                // Бейдж с балансом
                Text("\(unicornBalance) 🦄")
                    .font(.caption)
                    .foregroundColor(Color(hex: "C084FC"))
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(
                        Capsule()
                            .fill(Color(hex: "A855F7").opacity(0.2))
                            .overlay(
                                Capsule()
                                    .stroke(Color(hex: "C084FC"), lineWidth: 1)
                            )
                    )
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Карточка с информацией
            Button(action: {
                showRewardsModal = true
            }) {
                VStack(spacing: Spacing.m) {
                    // Иконка единорога с анимацией
                    Text("🦄")
                        .font(.system(size: 40))
                    
                    // Баланс
                    HStack(spacing: Spacing.xs) {
                        Text("💰")
                            .font(.system(size: 16))
                        Text("\(unicornBalance) единорогов")
                            .font(.body)
                            .foregroundColor(.textPrimary)
                    }
                    
                    // Статистика за неделю
                    HStack(spacing: Spacing.l) {
                        VStack(spacing: Spacing.xxs) {
                            Text("+\(weeklyRewarded)")
                                .font(.h3)
                                .foregroundColor(.successGreen)
                            Text("Вознаграждено")
                                .font(.captionSmall)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Rectangle()
                            .fill(Color.textSecondary.opacity(0.3))
                            .frame(width: 1, height: 30)
                        
                        VStack(spacing: Spacing.xxs) {
                            Text("-\(weeklyPunished)")
                                .font(.h3)
                                .foregroundColor(.dangerRed)
                            Text("Наказано")
                                .font(.captionSmall)
                                .foregroundColor(.textSecondary)
                        }
                    }
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.cardPadding)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .fill(
                            LinearGradient(
                                gradient: Gradient(colors: [
                                    Color(hex: "A855F7").opacity(0.12),
                                    Color(hex: "EC4899").opacity(0.18)
                                ]),
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.large)
                                .stroke(Color(hex: "A855F7").opacity(0.4), lineWidth: 2)
                        )
                )
            }
            .buttonStyle(PlainButtonStyle())
            .padding(.horizontal, Spacing.screenPadding)
        }
        .sheet(isPresented: $showRewardsModal) {
            RewardsModalView(
                unicornBalance: $unicornBalance,
                weeklyRewarded: $weeklyRewarded,
                weeklyPunished: $weeklyPunished
            )
        }
    }
    
    // MARK: - Quick Actions Section
    
    private var quickActionsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text("БЫСТРЫЕ ДЕЙСТВИЯ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                quickActionButton(
                    icon: "🕐",
                    title: "Добавить время",
                    subtitle: "+30 минут к лимиту"
                )
                
                quickActionButton(
                    icon: "🔒",
                    title: "Заблокировать устройство",
                    subtitle: "Мгновенная блокировка"
                )
                
                quickActionButton(
                    icon: "📍",
                    title: "Где ребёнок?",
                    subtitle: "Показать на карте"
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func quickActionButton(icon: String, title: String, subtitle: String) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .light)
            generator.impactOccurred()
            print(title)
        }) {
            HStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 28))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.body)
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

// MARK: - Preview

#if DEBUG
struct ParentalControlScreen_Previews: PreviewProvider {
    static var previews: some View {
        ParentalControlScreen()
    }
}
#endif

