import SwiftUI

/// 👶 Parental Control Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран родительского контроля с системой вознаграждений единорогами 🦄
/// Источник дизайна: /mobile/wireframes/14_parental_control_screen.html
struct ParentalControlScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var isContentFilterEnabled: Bool = true
    @State private var isAppBlockingEnabled: Bool = true
    @State private var screenTimeLimit: Double = 3
    @State private var selectedChild: String = "Маша"
    
    // Система вознаграждений с единорогами 🦄
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
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана родительского контроля")
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Выбор ребёнка
                        childSelector
                        
                        // Система вознаграждений
                        rewardsSection
                        
                        // Настройки контроля
                        controlSettings
                        
                        // Статистика
                        statisticsSection
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Список настроек родительского контроля")
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showRewardsModal) {
            RewardsModalView(
                unicornBalance: $unicornBalance,
                weeklyRewarded: $weeklyRewarded,
                weeklyPunished: $weeklyPunished
            )
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "РОДИТЕЛЬСКИЙ КОНТРОЛЬ",
            subtitle: "Управление для детей",
            showBackButton: true,
            onBack: {
                dismiss()
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель родительского контроля")
    }
    
    // MARK: - Child Selector
    
    private var childSelector: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ВЫБЕРИТЕ РЕБЁНКА")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            HStack(spacing: Spacing.m) {
                ForEach(["Маша", "Петя", "Аня"], id: \.self) { child in
                    Button(action: {
                        selectedChild = child
                    }) {
                        VStack(spacing: Spacing.xs) {
                            Text("👶")
                                .font(.system(size: 32))
                            
                            Text(child)
                                .font(.bodyBold)
                                .foregroundColor(selectedChild == child ? .white : .textPrimary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(selectedChild == child ? Color.primaryBlue : Color.backgroundMedium)
                        )
                    }
                    .accessibilityLabel("Выбрать ребёнка: \(child)")
                    .accessibilityAddTraits(selectedChild == child ? .isSelected : [])
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Rewards Section
    
    private var rewardsSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("🦄 СИСТЕМА ВОЗНАГРАЖДЕНИЙ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                Button(action: {
                    showRewardsModal = true
                }) {
                    Text("Подробнее")
                        .font(.body)
                        .foregroundColor(.primaryBlue)
                }
                .accessibilityLabel("Подробнее о системе вознаграждений")
            }
            
            HStack(spacing: Spacing.m) {
                // Баланс единорогов
                VStack(spacing: Spacing.xs) {
                    Text("\(unicornBalance)")
                        .font(.h1)
                        .foregroundColor(.primaryBlue)
                    
                    Text("Единорогов")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.primaryBlue.opacity(0.1))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Баланс единорогов: \(unicornBalance)")
                
                // Награды за неделю
                VStack(spacing: Spacing.xs) {
                    Text("\(weeklyRewarded)")
                        .font(.h2)
                        .foregroundColor(.successGreen)
                    
                    Text("Наград")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.successGreen.opacity(0.1))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Наград за неделю: \(weeklyRewarded)")
                
                // Наказания за неделю
                VStack(spacing: Spacing.xs) {
                    Text("\(weeklyPunished)")
                        .font(.h2)
                        .foregroundColor(.warningOrange)
                    
                    Text("Наказаний")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.warningOrange.opacity(0.1))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Наказаний за неделю: \(weeklyPunished)")
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Control Settings
    
    private var controlSettings: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("НАСТРОЙКИ КОНТРОЛЯ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.m) {
                // Фильтрация контента
                settingRow(
                    icon: "shield.fill",
                    title: "Фильтрация контента",
                    subtitle: "Блокировка нежелательного контента",
                    isEnabled: $isContentFilterEnabled
                )
                
                // Блокировка приложений
                settingRow(
                    icon: "app.badge.checkmark",
                    title: "Блокировка приложений",
                    subtitle: "Ограничение доступа к приложениям",
                    isEnabled: $isAppBlockingEnabled
                )
                
                // Ограничение времени экрана
                VStack(spacing: Spacing.s) {
                    HStack {
                        Image(systemName: "clock.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.primaryBlue)
                        
                        VStack(alignment: .leading, spacing: Spacing.xxs) {
                            Text("Ограничение времени экрана")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Text("\(Int(screenTimeLimit)) часов в день")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                    }
                    
                    HStack {
                        Text("1ч")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Slider(value: $screenTimeLimit, in: 1...8, step: 0.5)
                            .accentColor(.primaryBlue)
                        
                        Text("8ч")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.3))
                )
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Ограничение времени экрана: \(Int(screenTimeLimit)) часов")
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Statistics Section
    
    private var statisticsSection: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("СТАТИСТИКА ЗА НЕДЕЛЮ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            HStack(spacing: Spacing.m) {
                statCard(
                    icon: "clock.fill",
                    title: "Время экрана",
                    value: "2ч 34м",
                    color: .primaryBlue
                )
                
                statCard(
                    icon: "shield.fill",
                    title: "Заблокировано",
                    value: "47",
                    color: .successGreen
                )
                
                statCard(
                    icon: "exclamationmark.triangle.fill",
                    title: "Предупреждения",
                    value: "3",
                    color: .warningOrange
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Helper Views
    
    private func settingRow(icon: String, title: String, subtitle: String, isEnabled: Binding<Bool>) -> some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundColor(.primaryBlue)
                .frame(width: 24)
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            ALADDINToggle(isOn: isEnabled)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(isEnabled.wrappedValue ? "включено" : "выключено")")
    }
    
    private func statCard(icon: String, title: String, value: String, color: Color) -> some View {
        VStack(spacing: Spacing.xs) {
            Image(systemName: icon)
                .font(.system(size: 24))
                .foregroundColor(color)
            
            Text(value)
                .font(.h2)
                .foregroundColor(.textPrimary)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(color.opacity(0.1))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value)")
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
}

// MARK: - Preview

struct ParentalControlScreen_Previews: PreviewProvider {
    static var previews: some View {
        ParentalControlScreen()
    }
}
