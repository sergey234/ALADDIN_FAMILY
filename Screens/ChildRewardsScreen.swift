import SwiftUI

/// 🦄 Child Rewards Screen
/// Экран наград для детского интерфейса
/// Источник дизайна: /mobile/wireframes/14b_child_rewards_screen.html
struct ChildRewardsScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @State private var selectedTab: RewardTab = .shop
    @State private var unicornBalance: Int = 245
    @State private var weeklyEarned: Int = 128
    @State private var weeklyPunished: Int = 45
    @State private var goalProgress: Double = 0.306
    @State private var goalTitle: String = "Новая игра PS5"
    @State private var goalCost: Int = 800
    @State private var showRequestModal: Bool = false
    
    // MARK: - Tabs
    
    enum RewardTab {
        case shop
        case history
        case achievements
        
        var title: String {
            switch self {
            case .shop: return "🏪 Магазин"
            case .history: return "📊 История"
            case .achievements: return "🏆 Успехи"
            }
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                header
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Баланс единорогов
                        balanceCard
                        
                        // Прогресс к цели
                        goalProgressCard
                        
                        // Кнопка "Сообщить родителям"
                        requestButton
                        
                        // Табы
                        tabSelector
                        
                        // Контент вкладок
                        tabContent
                        
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showRequestModal) {
            AchievementRequestModal(
                onSendRequest: { achievement in
                    sendRequestToParents(achievement)
                }
            )
        }
    }
    
    // MARK: - Header
    
    private var header: some View {
        HStack {
            Button(action: { dismiss() }) {
                Image(systemName: "chevron.left")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(.textPrimary)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.backgroundMedium.opacity(0.5))
                    )
            }
            
            Text("Мои единороги")
                .font(.h2)
                .foregroundColor(Color(hex: "C084FC"))
            
            Spacer()
            
            // Уровень
            HStack(spacing: Spacing.xs) {
                Text("💎")
                    .font(.system(size: 16))
                Text("Уровень 2")
                    .font(.caption)
                    .foregroundColor(.textPrimary)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(Color.primaryBlue.opacity(0.3))
            )
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.m)
    }
    
    // MARK: - Balance Card
    
    private var balanceCard: some View {
        VStack(spacing: Spacing.m) {
            // Иконка единорога
            Text("🦄")
                .font(.system(size: 60))
            
            // Баланс
            Text("\(unicornBalance)")
                .font(.system(size: 48, weight: .bold))
                .foregroundColor(Color(hex: "C084FC"))
            
            Text("Единорогов на счету")
                .font(.body)
                .foregroundColor(.textSecondary)
            
            // Разделитель
            Rectangle()
                .fill(Color.textSecondary.opacity(0.2))
                .frame(height: 1)
                .padding(.vertical, Spacing.s)
            
            // Статистика за неделю
            HStack(spacing: Spacing.xxl) {
                VStack(spacing: Spacing.xs) {
                    Text("+\(weeklyEarned)")
                        .font(.h2)
                        .foregroundColor(.successGreen)
                    Text("Заработано\nза неделю")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack(spacing: Spacing.xs) {
                    Text("-\(weeklyPunished)")
                        .font(.h2)
                        .foregroundColor(.dangerRed)
                    Text("Наказано\nза неделю")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
            }
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.l)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(
                    LinearGradient(
                        gradient: Gradient(colors: [
                            Color(hex: "A855F7").opacity(0.15),
                            Color(hex: "EC4899").opacity(0.2)
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
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Goal Progress Card
    
    private var goalProgressCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack(spacing: Spacing.xs) {
                Text("🎯")
                    .font(.system(size: 20))
                Text("Моя цель: \(goalTitle)")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
            }
            
            // Прогресс-бар
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    // Фон
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.backgroundMedium.opacity(0.5))
                        .frame(height: 20)
                    
                    // Прогресс
                    RoundedRectangle(cornerRadius: 10)
                        .fill(
                            LinearGradient(
                                gradient: Gradient(colors: [
                                    Color(hex: "A855F7"),
                                    Color(hex: "EC4899")
                                ]),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: geometry.size.width * goalProgress, height: 20)
                }
            }
            .frame(height: 20)
            
            // Текст прогресса
            HStack {
                Text("\(unicornBalance) 🦄 накоплено")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                Spacer()
                
                Text("Нужно: \(goalCost) 🦄")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Text("✅ Осталось: \(goalCost - unicornBalance) 🦄 (примерно 35 дней)")
                .font(.captionSmall)
                .foregroundColor(.successGreen)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Request Button
    
    private var requestButton: some View {
        Button(action: {
            showRequestModal = true
        }) {
            HStack(spacing: Spacing.m) {
                Text("📣")
                    .font(.system(size: 24))
                Text("Сообщить родителям о достижении")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
            }
            .frame(maxWidth: .infinity)
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(
                        LinearGradient(
                            gradient: Gradient(colors: [
                                Color(hex: "A855F7").opacity(0.2),
                                Color(hex: "EC4899").opacity(0.2)
                            ]),
                            startPoint: .leading,
                            endPoint: .trailing
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
    
    // MARK: - Tab Selector
    
    private var tabSelector: some View {
        HStack(spacing: 0) {
            ForEach([RewardTab.shop, .history, .achievements], id: \.self) { tab in
                Button(action: {
                    selectedTab = tab
                }) {
                    Text(tab.title)
                        .font(.body)
                        .fontWeight(selectedTab == tab ? .bold : .regular)
                        .foregroundColor(selectedTab == tab ? .textPrimary : .textSecondary)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, Spacing.m)
                        .background(
                            selectedTab == tab ?
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.primaryBlue.opacity(0.3)) :
                            nil
                        )
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(4)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Tab Content
    
    @ViewBuilder
    private var tabContent: some View {
        switch selectedTab {
        case .shop:
            rewardsShop
        case .history:
            rewardsHistory
        case .achievements:
            achievementsTab
        }
    }
    
    // MARK: - Rewards Shop
    
    private var rewardsShop: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("🏪")
                    .font(.system(size: 18))
                Text("Доступные награды:")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                rewardItem(icon: "🎮", title: "+30 минут игр", desc: "Дополнительное время", price: 50, canAfford: true)
                rewardItem(icon: "📱", title: "+1 час экранного времени", desc: "На любой день", price: 80, canAfford: true)
                rewardItem(icon: "🌙", title: "+30 минут перед сном", desc: "Сдвинуть время сна", price: 100, canAfford: true)
                rewardItem(icon: "🍕", title: "Заказ пиццы", desc: "Твоя любимая!", price: 150, canAfford: true)
                rewardItem(icon: "🎬", title: "Поход в кино", desc: "С друзьями!", price: 200, canAfford: unicornBalance >= 200)
                rewardItem(icon: "🎁", title: "Подарок по выбору", desc: "До 1000₽", price: 500, canAfford: unicornBalance >= 500)
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func rewardItem(icon: String, title: String, desc: String, price: Int, canAfford: Bool) -> some View {
        Button(action: {
            if canAfford {
                buyReward(price: price, title: title)
            }
        }) {
            HStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 32))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    Text(desc)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: Spacing.xxs) {
                    Text("\(price) 🦄")
                        .font(.body)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "C084FC"))
                    
                    Text(canAfford ? "Купить!" : "Копи еще")
                        .font(.captionSmall)
                        .foregroundColor(canAfford ? .successGreen : .dangerRed)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(
                            Capsule()
                                .fill(canAfford ? Color.successGreen.opacity(0.2) : Color.dangerRed.opacity(0.2))
                        )
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(canAfford ? Color.backgroundMedium.opacity(0.5) : Color.backgroundMedium.opacity(0.3))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(canAfford ? Color(hex: "A855F7").opacity(0.4) : Color.textSecondary.opacity(0.2), lineWidth: canAfford ? 2 : 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(!canAfford)
    }
    
    // MARK: - Rewards History
    
    private var rewardsHistory: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("📊")
                    .font(.system(size: 18))
                Text("История:")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                historyItem(icon: "🏆", title: "Получил '5' по математике", amount: "+50", isReward: true, date: "Сегодня, 14:30")
                historyItem(icon: "📚", title: "Сделал домашнее задание", amount: "+10", isReward: true, date: "Вчера, 18:00")
                historyItem(icon: "😡", title: "Плохое поведение", amount: "-15", isReward: false, date: "2 дня назад, 16:00")
                historyItem(icon: "🧹", title: "Убрал в комнате", amount: "+5", isReward: true, date: "3 дня назад, 10:00")
                historyItem(icon: "📖", title: "Прочитал книгу 'Гарри Поттер'", amount: "+20", isReward: true, date: "4 дня назад, 20:00")
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func historyItem(icon: String, title: String, amount: String, isReward: Bool, date: String) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 28))
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(date)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Text(amount)
                .font(.body)
                .fontWeight(.bold)
                .foregroundColor(isReward ? .successGreen : .dangerRed)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(isReward ? Color.backgroundMedium.opacity(0.5) : Color.dangerRed.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(isReward ? Color.textSecondary.opacity(0.2) : Color.dangerRed.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Achievements Tab
    
    private var achievementsTab: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("🏆")
                    .font(.system(size: 18))
                Text("Мои успехи:")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                achievementItem(icon: "📚", title: "Отличник", desc: "10 заданий подряд", progress: 0.7)
                achievementItem(icon: "🧹", title: "Помощник", desc: "30 дней помощи", progress: 0.5)
                achievementItem(icon: "📖", title: "Книжный червь", desc: "Прочитай 5 книг", progress: 0.4)
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func achievementItem(icon: String, title: String, desc: String, progress: Double) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 32))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    Text(desc)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                Text("\(Int(progress * 100))%")
                    .font(.caption)
                    .foregroundColor(.successGreen)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 5)
                        .fill(Color.backgroundMedium.opacity(0.5))
                        .frame(height: 8)
                    
                    RoundedRectangle(cornerRadius: 5)
                        .fill(Color.successGreen)
                        .frame(width: geometry.size.width * progress, height: 8)
                }
            }
            .frame(height: 8)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
    
    // MARK: - Actions
    
    private func buyReward(price: Int, title: String) {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        unicornBalance -= price
        print("🎁 Куплена награда: \(title) за \(price) 🦄")
    }
    
    private func sendRequestToParents(_ achievement: String) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        
        print("📣 Отправлен запрос родителям: \(achievement)")
    }
}

// MARK: - Achievement Request Modal

struct AchievementRequestModal: View {
    
    @Environment(\.dismiss) private var dismiss
    let onSendRequest: (String) -> Void
    
    @State private var selectedTemplate: String? = nil
    @State private var customMessage: String = ""
    
    let templates = [
        ("📚", "Сделал домашнее задание", "+10 🦄"),
        ("🧹", "Убрал в комнате", "+5 🦄"),
        ("📖", "Прочитал книгу", "+20 🦄"),
        ("🏆", "Получил '5' / закрыл четверть", "+50 🦄"),
        ("🏠", "Помог по дому", "+15 🦄")
    ]
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        Text("Выбери, о чём хочешь сообщить:")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        VStack(spacing: Spacing.s) {
                            ForEach(0..<templates.count, id: \.self) { index in
                                let template = templates[index]
                                templateButton(icon: template.0, title: template.1, reward: template.2)
                            }
                            
                            customMessageButton()
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        
                        if selectedTemplate != nil || !customMessage.isEmpty {
                            sendButton
                        }
                    }
                    .padding(.top, Spacing.m)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("📣 Сообщить родителям")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
    }
    
    private func templateButton(icon: String, title: String, reward: String) -> some View {
        Button(action: {
            selectedTemplate = title
            customMessage = ""
        }) {
            HStack(spacing: Spacing.m) {
                Text(icon)
                    .font(.system(size: 28))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                    Text(reward)
                        .font(.caption)
                        .foregroundColor(.successGreen)
                }
                
                Spacer()
                
                if selectedTemplate == title {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(.successGreen)
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(selectedTemplate == title ? Color.successGreen.opacity(0.2) : Color.backgroundMedium.opacity(0.5))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(selectedTemplate == title ? Color.successGreen : Color.textSecondary.opacity(0.2), lineWidth: selectedTemplate == title ? 2 : 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private func customMessageButton() -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text("✍️")
                    .font(.system(size: 28))
                Text("Написать своё")
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
            }
            
            TextField("Расскажи, что сделал...", text: $customMessage)
                .textFieldStyle(.plain)
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(Color.backgroundMedium.opacity(0.5))
                )
                .foregroundColor(.textPrimary)
                .onChange(of: customMessage) { _ in
                    if !customMessage.isEmpty {
                        selectedTemplate = nil
                    }
                }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
    
    private var sendButton: some View {
        Button(action: {
            let message = customMessage.isEmpty ? (selectedTemplate ?? "") : customMessage
            onSendRequest(message)
            dismiss()
        }) {
            Text("📤 Отправить запрос")
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .fill(
                            LinearGradient(
                                gradient: Gradient(colors: [.successGreen, .successGreen.opacity(0.8)]),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                )
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Preview

#if DEBUG
struct ChildRewardsScreen_Previews: PreviewProvider {
    static var previews: some View {
        ChildRewardsScreen()
    }
}
#endif



