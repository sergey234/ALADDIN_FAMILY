import SwiftUI

/// 👶 Parental Control Screen - НОВЫЙ ДИЗАЙН С КАРТОЧКАМИ 2x3
/// Экран родительского контроля с системой вознаграждений единорогами 🦄
/// Источник дизайна: /mobile/wireframes/14_parental_control_screen.html
/// Стиль оформления: единообразие с Privacy/Terms (золотые акценты)
struct ParentalControlScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @StateObject private var manager = ParentalControlManager.shared
    
    // Выбранный ребёнок с сохранением в AppStorage
    @AppStorage("parental_selected_child") private var selectedChild: String = "Маша"
    
    // Состояния для карточек
    @State private var isContentBlockEnabled: Bool = true
    @State private var isTimeControlEnabled: Bool = true
    @State private var isMonitoringEnabled: Bool = true
    @State private var isLocationEnabled: Bool = true
    @State private var isReportsEnabled: Bool = true
    @State private var isAdditionalEnabled: Bool = true
    @State private var isBypassProtectionEnabled: Bool = true
    
    // Модалы
    @State private var showContentBlockModal: Bool = false
    @State private var showTimeControlModal: Bool = false
    @State private var showMonitoringModal: Bool = false
    @State private var showLocationModal: Bool = false
    @State private var showReportsModal: Bool = false
    @State private var showAdditionalModal: Bool = false
    @State private var showBypassProtectionModal: Bool = false
    @State private var showRewardsModal: Bool = false
    
    // Система вознаграждений с единорогами 🦄 (синхронизация с UserDefaults)
    @AppStorage("child_unicorn_balance") private var unicornBalance: Int = 245
    @AppStorage("child_weekly_earned") private var weeklyRewarded: Int = 0
    @AppStorage("child_weekly_punished") private var weeklyPunished: Int = 0
    
    // Актуальный баланс из UserDefaults (реактивный)
    @State private var actualBalance: Int = 0
    
    // Данные для карточек (из wireframe)
    @State private var contentBlockActive: Int = 3
    @State private var contentBlockTotal: Int = 4
    @State private var contentBlockedCount: Int = 1245
    
    @State private var timeRemaining: String = "1ч 24мин"
    @State private var timeSchedules: Int = 3
    
    @State private var monitoringWebsites: Int = 342
    @State private var monitoringApps: Int = 28
    
    @State private var locationStatus: String = "Дома"
    @State private var locationLastUpdate: String = "2 мин назад"
    @State private var locationWarnings: Int = 2
    
    @State private var reportsToday: Bool = true
    @State private var reportsAlerts: Int = 2
    
    @State private var additionalRequests: Int = 2
    @State private var additionalProtection: Bool = true
    
    // Состояния для 7-й карточки "Защита от обхода"
    @State private var bypassAttemptsToday: Int = 0
    @State private var bypassAttemptsWeek: Int = 47
    @State private var bypassAttemptsBlocked: Int = 47
    @State private var bypassDetectionActive: Int = 3  // 3 из 3 активно
    
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
                        
                        // Сетка карточек родительского контроля
                        parentalControlCards
                        
                        // Карточка вознаграждения (после всех карточек)
                        rewardsCard
                        
                        // Spacer для нижней части
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.top, Spacing.m)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Карточки родительского контроля")
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showContentBlockModal) {
            FamilyContentBlockModal(isPresented: $showContentBlockModal, isEnabled: $isContentBlockEnabled)
        }
        .sheet(isPresented: $showTimeControlModal) {
            FamilyTimeControlModal(isPresented: $showTimeControlModal, isEnabled: $isTimeControlEnabled)
        }
        .sheet(isPresented: $showMonitoringModal) {
            FamilyMonitoringModal(isPresented: $showMonitoringModal, isEnabled: $isMonitoringEnabled)
        }
        .sheet(isPresented: $showLocationModal) {
            FamilyLocationModal(isPresented: $showLocationModal, isEnabled: $isLocationEnabled)
        }
        .sheet(isPresented: $showReportsModal) {
            FamilyReportsModal(isPresented: $showReportsModal, isEnabled: $isReportsEnabled)
        }
        .sheet(isPresented: $showAdditionalModal) {
            FamilyAdditionalModal(isPresented: $showAdditionalModal, isEnabled: $isAdditionalEnabled)
        }
        .sheet(isPresented: $showBypassProtectionModal) {
            FamilyBypassProtectionModal(
                isPresented: $showBypassProtectionModal,
                isEnabled: $isBypassProtectionEnabled
            )
        }
        .sheet(isPresented: $showRewardsModal) {
            RewardsModalView(
                unicornBalance: $unicornBalance,
                weeklyRewarded: $weeklyRewarded,
                weeklyPunished: $weeklyPunished
            )
        }
        .onAppear {
            loadParentalControlStats()
            
            // Инициализация и синхронизация баланса
            actualBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
            if actualBalance == 0 && unicornBalance > 0 {
                actualBalance = unicornBalance
            }
            
            // Отладка роли пользователя
            let currentRole = UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА"
            print("🔍 DEBUG ParentalControlScreen:")
            print("   - Текущая роль: '\(currentRole)'")
            print("   - actualBalance: \(actualBalance)")
            print("   - unicornBalance: \(unicornBalance)")
            
            // Подписка на изменения UserDefaults для автоматического обновления
            // Используем .onReceive для SwiftUI вместо NotificationCenter.addObserver
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            let newBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
            if newBalance != actualBalance {
                actualBalance = newBalance
                print("🔍 DEBUG: actualBalance обновлён до \(actualBalance)")
            }
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "РОДИТЕЛЬСКИЙ КОНТРОЛЬ",
            subtitle: "Управление для \(selectedChild)",
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
            onBack: {
                print("🔍 DEBUG: Кнопка 'Назад' нажата в ParentalControlScreen")
                navigationManager.goBack()
                print("🔍 DEBUG: NavigationManager.goBack() вызван")
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель родительского контроля")
    }
    
    // MARK: - Child Selector
    
    private var childSelector: some View {
        VStack(spacing: Spacing.s) {
            HStack {
                Text("ВЫБЕРИТЕ РЕБЁНКА")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            HStack(spacing: Spacing.s) {
                ForEach(["Маша", "Петя", "Аня"], id: \.self) { child in
                    Button(action: {
                        withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                            selectedChild = child
                        }
                        HapticFeedback.selection()
                        // Загружаем статистику для выбранного ребёнка
                        loadParentalControlStats()
                    }) {
                        VStack(spacing: Spacing.xs) {
                            Text("👶")
                                .font(.system(size: 28))
                            
                            Text(child)
                                .font(.bodyBold)
                                .foregroundColor(selectedChild == child ? .white : .textPrimary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.s)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(selectedChild == child ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(
                                    selectedChild == child ? Color.secondaryGold.opacity(0.5) : Color.white.opacity(0.1),
                                    lineWidth: selectedChild == child ? 2 : 1
                                )
                        )
                    }
                    .accessibilityLabel("Выбрать ребёнка: \(child)")
                    .accessibilityAddTraits(selectedChild == child ? .isSelected : [])
                }
            }
        }
        .padding(Spacing.m)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Parental Control Cards Grid
    
    private var parentalControlCards: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("РОДИТЕЛЬСКИЙ КОНТРОЛЬ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            // Сетка 2x3
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: Spacing.s), count: 2), spacing: Spacing.s) {
                // 1. Блокировка контента
                ParentalControlCard(
                    icon: "🔒",
                    title: "Блокировка\nконтента",
                    statusBadge: "\(contentBlockActive)/\(contentBlockTotal)",
                    statusText: "✅ \(contentBlockActive) активно",
                    metric: "\(contentBlockedCount) заблокировано",
                    cardColor: .red.opacity(0.2),
                    borderColor: .red.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: $isContentBlockEnabled,
                    action: { showContentBlockModal = true }
                )
                
                // 2. Управление временем
                ParentalControlCard(
                    icon: "⏱️",
                    title: "Управление\nвременем",
                    statusBadge: "⏳",
                    statusText: "⏳ \(timeRemaining)",
                    metric: "\(timeSchedules) расписания",
                    cardColor: .blue.opacity(0.2),
                    borderColor: .blue.opacity(0.4),
                    badgeColor: .warningOrange,
                    isEnabled: $isTimeControlEnabled,
                    action: { showTimeControlModal = true }
                )
                
                // 3. Мониторинг
                ParentalControlCard(
                    icon: "👀",
                    title: "Мониторинг",
                    statusBadge: "4/5",
                    statusText: "📊 \(monitoringWebsites) сайта",
                    metric: "\(monitoringApps) приложений",
                    cardColor: .purple.opacity(0.2),
                    borderColor: .purple.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: $isMonitoringEnabled,
                    action: { showMonitoringModal = true }
                )
                
                // 4. Геолокация
                ParentalControlCard(
                    icon: "📍",
                    title: "Геолокация",
                    statusBadge: "🏠",
                    statusText: "🏠 \(locationStatus)",
                    metric: locationLastUpdate + (locationWarnings > 0 ? " • ⚠️ \(locationWarnings)" : ""),
                    cardColor: .green.opacity(0.2),
                    borderColor: .green.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: $isLocationEnabled,
                    action: { showLocationModal = true }
                )
                
                // 5. Отчёты
                ParentalControlCard(
                    icon: "📊",
                    title: "Отчёты",
                    statusBadge: "⚠️ \(reportsAlerts)",
                    statusText: reportsToday ? "📅 Сегодня" : "📅 За неделю",
                    metric: "\(reportsAlerts) тревоги",
                    cardColor: .orange.opacity(0.2),
                    borderColor: .orange.opacity(0.4),
                    badgeColor: .dangerRed,
                    isEnabled: $isReportsEnabled,
                    action: { showReportsModal = true }
                )
                
                // 6. Дополнительно
                ParentalControlCard(
                    icon: "⚙️",
                    title: "Дополнительно",
                    statusBadge: "✋ \(additionalRequests)",
                    statusText: "✋ \(additionalRequests) запроса",
                    metric: additionalProtection ? "🛡️ Защита ON" : "🛡️ Защита OFF",
                    cardColor: .gray.opacity(0.2),
                    borderColor: .gray.opacity(0.4),
                    badgeColor: .warningOrange,
                    isEnabled: $isAdditionalEnabled,
                    action: { showAdditionalModal = true }
                )
                
                // 7. Защита от обхода (НОВАЯ)
                ParentalControlCard(
                    icon: "🚨",
                    title: "Защита от\nобхода",
                    statusBadge: bypassAttemptsToday > 0 ? "🚨 \(bypassAttemptsToday)" : "✅ 0",
                    statusText: "🚫 \(bypassAttemptsBlocked) заблокировано",
                    metric: "\(bypassDetectionActive)/3 активно",
                    cardColor: Color.warningOrange.opacity(0.2),  // Янтарный (новый цвет!)
                    borderColor: Color.warningOrange.opacity(0.4),
                    badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen,
                    isEnabled: $isBypassProtectionEnabled,
                    action: { showBypassProtectionModal = true }
                )
            }
        }
        .padding(Spacing.m)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Rewards Card
    
    private var rewardsCard: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            showRewardsModal = true
        }) {
            HStack(spacing: Spacing.m) {
                // Название "Вознаграждение ребенка" на всю ширину карточки (без переносов)
                Text("Вознаграждение ребенка")
                    .font(.bodyBold)
                    .foregroundColor(Color(red: 0.75, green: 0.52, blue: 0.99))
                    .lineLimit(1)
                    .minimumScaleFactor(0.85)
                    .multilineTextAlignment(.leading)
                
                Spacer(minLength: Spacing.s)
                
                // Только количество единорогов в зеленом овале (актуальное из UserDefaults)
                HStack(spacing: Spacing.xs) {
                    Text("\(actualBalance)")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                    Text("🦄")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                }
                .padding(.horizontal, Spacing.m)
                .padding(.vertical, Spacing.s)
                .background(
                    Capsule()
                        .fill(Color.successGreen)
                )
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14))
                    .foregroundColor(.textTertiary)
                    .padding(.leading, Spacing.xs)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(Spacing.m)
            .background(
                LinearGradient(
                    colors: [
                        Color(red: 0.66, green: 0.33, blue: 0.97).opacity(0.15),
                        Color(red: 0.93, green: 0.28, blue: 0.6).opacity(0.15)
                    ],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color(red: 0.66, green: 0.33, blue: 0.97).opacity(0.4), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
        }
        .buttonStyle(PlainButtonStyle())
        .cardShadow()
        .id("rewardsCard_\(actualBalance)")  // Принудительное обновление при изменении баланса
    }
    
    // MARK: - Helper Views
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.secondaryGold.opacity(0.2), lineWidth: 1)
            )
    }
    
    // MARK: - Data Loading
    
    /// Загружает статистику родительского контроля через Manager
    private func loadParentalControlStats() {
        manager.getStats(childId: selectedChild) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    // Обновляем данные для карточек
                    contentBlockActive = stats.contentBlocked.activeFilters
                    contentBlockTotal = 4 // Общее количество фильтров
                    contentBlockedCount = stats.contentBlocked.websitesBlocked
                    
                    timeRemaining = stats.screenTime.remaining
                    timeSchedules = stats.screenTime.schedulesCount
                    
                    monitoringWebsites = stats.monitoring.sitesTracked
                    monitoringApps = stats.monitoring.appsTracked
                    
                    locationStatus = stats.location.currentLocation ?? "Неизвестно"
                    locationLastUpdate = stats.location.lastUpdate ?? "Не обновлялось"
                    locationWarnings = stats.location.eventsToday
                    
                case .failure(let error):
                    print("❌ Ошибка загрузки статистики: \(error.localizedDescription)")
                    // Оставляем значения по умолчанию
                }
            }
        }
    }
}

// MARK: - Parental Control Card Component

struct ParentalControlCard: View {
    let icon: String
    let title: String
    let statusBadge: String
    let statusText: String
    let metric: String
    let cardColor: Color
    let borderColor: Color
    let badgeColor: Color
    @Binding var isEnabled: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            action()
        }) {
            VStack(spacing: Spacing.xs) {
                // Badge в верхнем правом углу
            HStack {
                    Spacer()
                    Text(statusBadge)
                        .font(.caption2)
                        .fontWeight(.bold)
                        .foregroundColor(badgeColor)
                        .padding(.horizontal, Spacing.xs)
                        .padding(.vertical, 2)
                        .background(badgeColor.opacity(0.2))
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(badgeColor.opacity(0.5), lineWidth: 1)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }
                
                Spacer()
                
                // Иконка
                Text(icon)
                    .font(.system(size: 32))
                
                // Название
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
                
                // Статус
                Text(statusText)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                
                // Метрика
                Text(metric)
                    .font(.caption2)
                    .foregroundColor(.textTertiary)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                
                // Быстрый toggle
                HStack {
                    Text(isEnabled ? "ON" : "OFF")
                        .font(.caption2)
                        .fontWeight(.semibold)
                        .foregroundColor(isEnabled ? .successGreen : .textTertiary)
                    
                    ALADDINToggle(isOn: $isEnabled)
                        .scaleEffect(0.7)
                }
                .padding(.top, Spacing.xxs)
            }
            .frame(height: 160)
        .frame(maxWidth: .infinity)
            .padding(Spacing.s)
            .background(cardColor)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .stroke(
                        isEnabled ? Color.secondaryGold.opacity(0.5) : Color.white.opacity(0.1),
                        lineWidth: isEnabled ? 2 : 1
                    )
            )
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
        }
        .buttonStyle(PlainButtonStyle())
        .cardShadow()
    }
}

// MARK: - Modal Views
// Используются Family* модалы из 02_FamilyScreen.swift

// MARK: - Preview

struct ParentalControlScreen_Previews: PreviewProvider {
    static var previews: some View {
        ParentalControlScreen()
            .environmentObject(NavigationManager())
    }
}
