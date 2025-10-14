import SwiftUI

/// 🏠 Main Screen
/// Главный экран ALADDIN - центр управления защитой семьи
/// Источник дизайна: /mobile/wireframes/01_main_screen.html
struct MainScreen: View {
    
    // MARK: - State
    
    @State private var selectedTab: Int = 0
    @State private var isVPNEnabled: Bool = true
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                ALADDINNavigationBar(
                    title: "ALADDIN",
                    subtitle: "AI Защита Семьи",
                    rightButtons: [
                        .init(icon: "bell") {
                            print("Уведомления")
                        },
                        .init(icon: "gearshape") {
                            print("Настройки")
                        }
                    ]
                )
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.m) {
                        // VPN Статус
                        vpnStatusCard
                        
                        // Заголовок секции
                        HStack {
                            Text("ОСНОВНЫЕ ФУНКЦИИ")
                                .font(.h3)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.top, Spacing.s)
                        
                        // Функциональные карточки (2x2 grid)
                        functionsGrid
                        
                        // Быстрые действия
                        quickActionsSection
                        
                        // Spacer для bottom nav
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
                
                // Bottom Navigation
                bottomNavigation
            }
        }
    }
    
    // MARK: - VPN Status Card
    
    private var vpnStatusCard: some View {
        HStack(spacing: Spacing.m) {
            // Иконка VPN
            Text("🛡️")
                .font(.system(size: 32))
            
            // Информация
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text("VPN ЗАЩИТА")
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                Text(isVPNEnabled ? "Подключено • Безопасно" : "Отключено")
                    .font(.caption)
                    .foregroundColor(isVPNEnabled ? .successGreen : .textSecondary)
            }
            
            Spacer()
            
            // Toggle VPN
            Button(action: {
                let generator = UIImpactFeedbackGenerator(style: .medium)
                generator.impactOccurred()
                
                withAnimation(.spring()) {
                    isVPNEnabled.toggle()
                }
            }) {
                Circle()
                    .fill(isVPNEnabled ? Color.successGreen : Color.textSecondary)
                    .frame(width: 20, height: 20)
                    .overlay(
                        Image(systemName: isVPNEnabled ? "checkmark" : "xmark")
                            .font(.system(size: 12, weight: .bold))
                            .foregroundColor(.white)
                    )
            }
        }
        .padding(Spacing.cardPadding)
        .background(
            LinearGradient(
                colors: isVPNEnabled ? 
                    [Color.secondaryGold, Color(hex: "#D97706")] :
                    [Color.backgroundMedium, Color.backgroundMedium],
                startPoint: .leading,
                endPoint: .trailing
            )
        )
        .cornerRadius(CornerRadius.large)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Functions Grid
    
    private var functionsGrid: some View {
        VStack(spacing: Spacing.m) {
            HStack(spacing: Spacing.m) {
                // Семья
                FunctionCard(
                    icon: "👨‍👩‍👧‍👦",
                    title: "СЕМЬЯ",
                    subtitle: "4 члена • Всё в порядке",
                    status: .active
                ) {
                    print("Открыть семью")
                }
                
                // VPN
                FunctionCard(
                    icon: "🌐",
                    title: "VPN",
                    subtitle: "Подключено",
                    status: .active
                ) {
                    print("Открыть VPN")
                }
            }
            
            HStack(spacing: Spacing.m) {
                // Аналитика
                FunctionCard(
                    icon: "📊",
                    title: "АНАЛИТИКА",
                    subtitle: "47 угроз заблокировано",
                    status: .warning
                ) {
                    print("Открыть аналитику")
                }
                
                // AI Помощник
                FunctionCard(
                    icon: "🤖",
                    title: "AI",
                    subtitle: "Всегда готов помочь",
                    status: .neutral
                ) {
                    print("Открыть AI")
                }
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Quick Actions
    
    private var quickActionsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Заголовок
            HStack {
                Text("БЫСТРЫЕ ДЕЙСТВИЯ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Кнопки действий
            VStack(spacing: Spacing.s) {
                quickActionButton(
                    icon: "🚨",
                    title: "Экстренная помощь",
                    subtitle: "Быстрый вызов службы безопасности"
                ) {
                    print("SOS")
                }
                
                quickActionButton(
                    icon: "👶",
                    title: "Детский контроль",
                    subtitle: "Управление доступом детей"
                ) {
                    print("Родительский контроль")
                }
                
                quickActionButton(
                    icon: "📱",
                    title: "Безопасность устройств",
                    subtitle: "Статус защиты всех устройств"
                ) {
                    print("Устройства")
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
        .padding(.top, Spacing.m)
    }
    
    private func quickActionButton(
        icon: String,
        title: String,
        subtitle: String,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .light)
            generator.impactOccurred()
            action()
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка
                Text(icon)
                    .font(.system(size: 28))
                
                // Текст
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                // Стрелка
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.textSecondary)
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.5))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Bottom Navigation
    
    private var bottomNavigation: some View {
        HStack(spacing: 0) {
            navButton(icon: "house.fill", label: "Главная", index: 0)
            navButton(icon: "person.3.fill", label: "Семья", index: 1)
            navButton(icon: "chart.bar.fill", label: "Статистика", index: 2)
            navButton(icon: "gearshape.fill", label: "Настройки", index: 3)
        }
        .padding(.vertical, Spacing.s)
        .padding(.horizontal, Spacing.xs)
        .background(
            Color.backgroundDark.opacity(0.95)
                .blur(radius: 10)
        )
        .overlay(
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
                .frame(height: 1),
            alignment: .top
        )
    }
    
    private func navButton(icon: String, label: String, index: Int) -> some View {
        Button(action: {
            let generator = UIImpactFeedbackGenerator(style: .light)
            generator.impactOccurred()
            selectedTab = index
        }) {
            VStack(spacing: Spacing.xxs) {
                Image(systemName: icon)
                    .font(.system(size: 20))
                    .foregroundColor(selectedTab == index ? .primaryBlue : .textSecondary)
                
                Text(label)
                    .font(.captionSmall)
                    .foregroundColor(selectedTab == index ? .primaryBlue : .textSecondary)
            }
            .frame(maxWidth: .infinity)
        }
    }
}

// MARK: - Preview

#Preview {
    MainScreen()
}




