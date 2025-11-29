import SwiftUI

/// 🦄 Child Rewards Screen
/// Экран наград для детского интерфейса
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
struct ChildRewardsScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @Environment(\.dismiss) private var dismiss
    @State private var selectedTab: RewardTab = .shop
    
    // Награды магазина (загружаются из UserDefaults)
    @AppStorage("shop_rewards_list") private var shopRewardsData: String = ""
    @State private var availableRewards: [ShopReward] = []
    
    // Сохраняем игровой прогресс в AppStorage
    @AppStorage("child_unicorn_balance") private var storedUnicornBalance: Int = 245
    @State private var unicornBalance: Int = 245 {
        didSet {
            storedUnicornBalance = unicornBalance
        }
    }
    
    @AppStorage("child_weekly_earned") private var storedWeeklyEarned: Int = 128
    @State private var weeklyEarned: Int = 128 {
        didSet {
            storedWeeklyEarned = weeklyEarned
        }
    }
    
    @AppStorage("child_weekly_punished") private var storedWeeklyPunished: Int = 45
    @State private var weeklyPunished: Int = 45 {
        didSet {
            storedWeeklyPunished = weeklyPunished
        }
    }
    
    @AppStorage("child_goal_progress") private var storedGoalProgress: Double = 0.306
    @State private var goalProgress: Double = 0.306 {
        didSet {
            storedGoalProgress = goalProgress
        }
    }
    
    @AppStorage("child_goal_title") private var storedGoalTitle: String = "Новая игра PS5"
    @State private var goalTitle: String = "Новая игра PS5" {
        didSet {
            storedGoalTitle = goalTitle
        }
    }
    
    @AppStorage("child_goal_cost") private var storedGoalCost: Int = 800
    @State private var goalCost: Int = 800 {
        didSet {
            storedGoalCost = goalCost
        }
    }
    
    @State private var showRequestModal: Bool = false
    
    // Модальные окна для вознаграждения/наказания (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ)
    @State private var showRewardInput: Bool = false
    @State private var showPunishInput: Bool = false
    @State private var rewardAmount: String = "10"
    @State private var punishAmount: String = "10"
    @State private var rewardReason: String = ""
    @State private var punishReason: String = ""
    
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
                        
                        // ✅ БЕЗОПАСНОСТЬ: Разделение интерфейса по ролям
                        // Для родителей: секция "Воспитание ребенка" с кнопками "Вознаградить" и "Наказать"
                        // Для детей: НЕ показываем "Воспитание ребенка" - они НЕ должны видеть эту секцию!
                        // Детям показываем ТОЛЬКО историю (без заголовка "Воспитание ребенка")
                        
                        Group {
                            if isCurrentUserParent() {
                                // ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ
                                parentQuickActions
                                    .onAppear {
                                        print("✅ Родительский интерфейс: показана секция 'Воспитание ребенка'")
                                    }
                            } else {
                                // ТОЛЬКО ДЛЯ ДЕТЕЙ - показываем историю
                                childRewardsHistoryView
                                    .onAppear {
                                        print("✅ Детский интерфейс: показана история наград/наказаний (без 'Воспитание ребенка')")
                                    }
                            }
                        }
                        .onAppear {
                            print("🔍 ChildRewardsScreen: Проверка роли - isCurrentUserParent() = \(isCurrentUserParent())")
                        }
                        
                        // 🎮 Игровые карточки 2x3
                        gamesGrid
                        
                        // Табы (Магазин, История)
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
        .sheet(isPresented: $showPurchaseConfirmation) {
            PurchaseConfirmationModal(
                title: pendingPurchaseTitle,
                price: pendingPurchasePrice,
                balance: unicornBalance,
                onConfirm: {
                    confirmPurchase()
                },
                onCancel: {
                    showPurchaseConfirmation = false
                }
            )
        }
        .sheet(isPresented: $showRewardInput) {
            RewardInputModal(
                isPresented: $showRewardInput,
                amount: $rewardAmount,
                reason: $rewardReason,
                onConfirm: { amount, reason in
                    rewardChild(amount: amount, reason: reason)
                }
            )
        }
        .sheet(isPresented: $showPunishInput) {
            PunishInputModal(
                isPresented: $showPunishInput,
                amount: $punishAmount,
                reason: $punishReason,
                onConfirm: { amount, reason in
                    punishChild(amount: amount, reason: reason)
                }
            )
        }
        .onAppear {
            // Синхронизируем баланс из UserDefaults (единый источник истины)
            let currentBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
            if currentBalance > 0 {
                unicornBalance = currentBalance
                storedUnicornBalance = currentBalance
            } else {
                unicornBalance = storedUnicornBalance
            }
            
            // Восстанавливаем сохранённый прогресс из AppStorage
            weeklyEarned = storedWeeklyEarned
            weeklyPunished = storedWeeklyPunished
            goalProgress = storedGoalProgress
            goalTitle = storedGoalTitle
            goalCost = storedGoalCost
            
            // Загружаем награды магазина
            loadShopRewards()
            
            // ✅ КРИТИЧНО: Проверка роли и логирование для диагностики
            let isParent = isCurrentUserParent()
            let currentRole = UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА"
            print("═══════════════════════════════════════════════════════════")
            print("🔍 DEBUG ChildRewardsScreen.onAppear:")
            print("   📋 Роль пользователя:")
            print("      - UserDefaults: '\(currentRole)'")
            print("      - isCurrentUserParent() = \(isParent)")
            print("      - Интерфейс: \(isParent ? "👨‍👩‍👧 РОДИТЕЛЬСКИЙ" : "👶 ДЕТСКИЙ")")
            print("   🦄 Баланс единорогов: \(unicornBalance) 🦄")
            print("   🎁 Доступно наград: \(availableRewards.filter { $0.isEnabled }.count) из \(availableRewards.count)")
            print("   🔒 Секция 'Воспитание ребенка': \(isParent ? "✅ ВИДНА" : "❌ СКРЫТА")")
            print("   ⚙️ Кнопка настроек: \(isParent ? "✅ ВИДНА" : "❌ СКРЫТА")")
            print("═══════════════════════════════════════════════════════════")
            
            // ✅ Дополнительная проверка безопасности
            if !isParent {
                print("✅ БЕЗОПАСНОСТЬ: Детский интерфейс - все родительские функции заблокированы")
            }
        }
        .onChange(of: storedUnicornBalance) { newValue in
            // Автообновление баланса при изменении в UserDefaults (например, из RewardsModalView)
            unicornBalance = newValue
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            // Обновляем список наград при изменении в UserDefaults
            loadShopRewards()
            // Обновляем баланс из UserDefaults
            let newBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
            if unicornBalance != newBalance {
                unicornBalance = newBalance
                print("🔄 ChildRewardsScreen: Баланс обновлён через NotificationCenter: \(newBalance) 🦄")
            }
        }
        .onChange(of: storedWeeklyEarned) { newValue in
            weeklyEarned = newValue
        }
        .onChange(of: storedWeeklyPunished) { newValue in
            weeklyPunished = newValue
        }
    }
    
    // MARK: - Header
    
    private var header: some View {
        HStack {
            Button(action: {
                HapticFeedback.impact(.light)
                // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                dismiss()
                
                // Дополнительно синхронизируем NavigationManager для корректной работы стека
                DispatchQueue.main.async {
                    if navigationManager.canGoBack {
                        navigationManager.goBack()
                    }
                }
            }) {
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
            
            // ✅ БЕЗОПАСНОСТЬ: Кнопка настроек ТОЛЬКО для родителей
            // Дети НЕ должны видеть эту кнопку и НЕ должны попадать в родительский контроль!
            let isParent = isCurrentUserParent()
            if isParent {
                Button(action: {
                    print("🔍 DEBUG: Родитель нажал настройки в ChildRewardsScreen")
                    HapticFeedback.impact(.medium)
                    navigationManager.navigateTo(.gamesParentalControl)
                }) {
                    Image(systemName: "gearshape.fill")
                        .font(.system(size: 18))
                        .foregroundColor(.textSecondary)
                        .frame(width: 44, height: 44)
                        .background(
                            Circle()
                                .fill(Color.backgroundMedium.opacity(0.5))
                        )
                }
                .onAppear {
                    print("✅ Кнопка настроек видна (родитель)")
                }
            } else {
                // ДЛЯ ДЕТЕЙ: кнопка настроек НЕ показывается вообще
                EmptyView()
                    .onAppear {
                        print("✅ Кнопка настроек СКРЫТА (ребёнок)")
                    }
            }
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
    
    // MARK: - Games Grid (2x3)
    
    private var gamesGrid: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text("🎮 Мои игры")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .padding(.horizontal, Spacing.screenPadding)
            
            LazyVGrid(columns: [
                GridItem(.flexible(), spacing: Spacing.s),
                GridItem(.flexible(), spacing: Spacing.s)
            ], spacing: Spacing.s) {
                // Карточка 1: 🛡️ Юный защитник
                gameCardButton(
                    icon: "🛡️",
                    title: "Юный защитник",
                    status: "✅ Доступно",
                    metric: "\(getCompletedLessons())/6 уроков",
                    color: .primaryBlue,
                    destination: NavigationManager.ALADDINScreen.youngDefender
                )
                
                // Карточка 2: 🦄 Питомец
                gameCardButton(
                    icon: "🦄",
                    title: "Мой питомец",
                    status: "💎 Уровень \(getPetLevel())",
                    metric: "❤️ \(Int(getPetLove() * 100))%",
                    color: Color(hex: "A855F7"),
                    destination: NavigationManager.ALADDINScreen.unicornPet
                )
                
                // Карточка 3: 🕵️ Я защитник
                gameCardButton(
                    icon: "🕵️",
                    title: "Я защитник",
                    status: "✅ Доступно",
                    metric: "\(getCompletedQuests())/10 квестов",
                    color: Color(hex: "EC4899"),
                    destination: NavigationManager.ALADDINScreen.familyProtector
                )
                
                // Карточка 4: 🏆 Турнир
                gameCardButton(
                    icon: "🏆",
                    title: "Турнир",
                    status: "⏰ \(getTournamentDaysLeft())д осталось",
                    metric: "🥇 Лидер",
                    color: .warningOrange,
                    destination: NavigationManager.ALADDINScreen.familyTournament
                )
                
                // Карточка 5: 🏪 Магазин (встроенный таб)
                gameCardButton(
                    icon: "🏪",
                    title: "Магазин",
                    status: "💰 6 товаров",
                    metric: "от 50🦄",
                    color: .secondaryGold,
                    isTab: true,
                    tabDestination: .shop
                )
                
                // Карточка 6: 📊 История (встроенный таб)
                gameCardButton(
                    icon: "📊",
                    title: "История",
                    status: "📅 30 дней",
                    metric: "+128/-45 🦄",
                    color: Color.textSecondary,
                    isTab: true,
                    tabDestination: .history
                )
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func gameCardButton(
        icon: String,
        title: String,
        status: String,
        metric: String,
        color: Color,
        destination: NavigationManager.ALADDINScreen? = nil,
        isTab: Bool = false,
        tabDestination: RewardTab? = nil
    ) -> some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            if isTab, let tab = tabDestination {
                selectedTab = tab
            } else if let destination = destination {
                navigationManager.navigateTo(destination)
            }
        }) {
            VStack(spacing: 8) {
                // Badge
                HStack {
                    Spacer()
                    Text(status)
                        .font(.captionSmall)
                        .foregroundColor(color)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(color.opacity(0.2))
                        .clipShape(Capsule())
                }
                
                // Иконка
                Text(icon)
                    .font(.system(size: 36))
                
                // Название
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                
                // Метрика
                Text(metric)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                
                Spacer()
            }
            .frame(height: 160)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(color.opacity(0.15))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(color.opacity(0.3), lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Helper Methods
    
    /// Загрузка наград магазина из UserDefaults
    private func loadShopRewards() {
        if shopRewardsData.isEmpty {
            // Первый запуск - используем дефолтные награды
            availableRewards = ShopReward.defaultRewards
            saveShopRewards()
        } else {
            // Загружаем из UserDefaults
            if let data = shopRewardsData.data(using: .utf8),
               let rewards = try? JSONDecoder().decode([ShopReward].self, from: data) {
                availableRewards = rewards
            } else {
                // Ошибка декодирования - используем дефолтные
                availableRewards = ShopReward.defaultRewards
                saveShopRewards()
            }
        }
    }
    
    /// Сохранение наград магазина в UserDefaults
    private func saveShopRewards() {
        if let data = try? JSONEncoder().encode(availableRewards),
           let jsonString = String(data: data, encoding: .utf8) {
            shopRewardsData = jsonString
        }
    }
    
    /// Проверка: является ли текущий пользователь родителем
    /// ✅ КРИТИЧНО ДЛЯ БЕЗОПАСНОСТИ: Дети НЕ должны видеть родительские функции
    private func isCurrentUserParent() -> Bool {
        guard let roleString = UserDefaults.standard.string(forKey: "current_user_role"),
              let role = FamilyRole(rawValue: roleString) else {
            // Если роль не установлена или невалидна - считаем что это ребёнок (безопаснее)
            print("🚨 ChildRewardsScreen.isCurrentUserParent: роль не найдена или невалидна -> false (безопасность)")
            return false
        }
        
        let isParent = role == .parent
        print("🔍 ChildRewardsScreen.isCurrentUserParent:")
        print("   - Роль в UserDefaults: '\(roleString)'")
        print("   - FamilyRole: \(role.rawValue)")
        print("   - Результат: \(isParent ? "РОДИТЕЛЬ" : "РЕБЁНОК")")
        
        // Дополнительная проверка безопасности
        if isParent {
            print("   ✅ Разрешён доступ к родительским функциям")
        } else {
            print("   🔒 Доступ к родительским функциям ЗАБЛОКИРОВАН (ребёнок)")
        }
        
        return isParent
    }
    
    private func getCompletedLessons() -> Int {
        UserDefaults.standard.integer(forKey: "young_defender_completed_lessons")
    }
    
    private func getPetLevel() -> Int {
        UserDefaults.standard.integer(forKey: "pet_level")
    }
    
    private func getPetLove() -> Double {
        let love = UserDefaults.standard.double(forKey: "pet_love")
        return love > 0 ? love : 0.85  // Значение по умолчанию
    }
    
    private func getCompletedQuests() -> Int {
        UserDefaults.standard.integer(forKey: "family_protector_completed_quests")
    }
    
    private func getTournamentDaysLeft() -> Int {
        let days = UserDefaults.standard.integer(forKey: "tournament_days_left")
        return days > 0 ? days : 5  // Значение по умолчанию
    }
    
    // MARK: - Parent Quick Actions (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ)
    
    private var parentQuickActions: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок секции
            HStack {
                Text("👨‍👩‍👧")
                    .font(.system(size: 24))
                Text("Воспитание ребенка:")
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                    .fontWeight(.bold)
            }
            .padding(.horizontal, Spacing.screenPadding)
            .padding(.bottom, Spacing.s)
            
            // Кнопки действий
            HStack(spacing: Spacing.m) {
                // Кнопка "Вознаградить"
                Button(action: {
                    print("🔍 DEBUG: Нажата кнопка 'Вознаградить' в ChildRewardsScreen")
                    HapticFeedback.impact(.medium)
                    showRewardInput = true
                }) {
                    VStack(spacing: Spacing.xs) {
                        Text("✅")
                            .font(.system(size: 36))
                            .accessibilityLabel("Галочка")
                        Text("Вознаградить")
                            .font(.bodyBold)
                            .foregroundColor(.white)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 80)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .fill(Color.successGreen)
                            .shadow(color: Color.successGreen.opacity(0.4), radius: 8, x: 0, y: 4)
                    )
                }
                .buttonStyle(PlainButtonStyle())
                .accessibilityLabel("Вознаградить ребёнка")
                .accessibilityHint("Нажмите для вознаграждения ребёнка единорогами")
                
                // Кнопка "Наказать"
                Button(action: {
                    print("🔍 DEBUG: Нажата кнопка 'Наказать' в ChildRewardsScreen")
                    HapticFeedback.impact(.medium)
                    showPunishInput = true
                }) {
                    VStack(spacing: Spacing.xs) {
                        Text("❌")
                            .font(.system(size: 36))
                            .accessibilityLabel("Крестик")
                        Text("Наказать")
                            .font(.bodyBold)
                            .foregroundColor(.white)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 80)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .fill(Color.dangerRed)
                            .shadow(color: Color.dangerRed.opacity(0.4), radius: 8, x: 0, y: 4)
                    )
                }
                .buttonStyle(PlainButtonStyle())
                .accessibilityLabel("Наказать ребёнка")
                .accessibilityHint("Нажмите для наказания ребёнка единорогами")
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
        .padding(.vertical, Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Child Rewards History View (ТОЛЬКО ДЛЯ ДЕТЕЙ)
    
    /// Секция для просмотра истории наград/наказаний детьми
    /// ДЕТИ НЕ ВИДЯТ "Воспитание ребенка" - только историю!
    private var childRewardsHistoryView: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок секции - БЕЗ "Воспитание ребенка" для детей
            HStack {
                Text("📊")
                    .font(.system(size: 24))
                Text("За что меня наградили и наказали:")
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                    .fontWeight(.bold)
            }
            .padding(.horizontal, Spacing.screenPadding)
            .padding(.bottom, Spacing.s)
            
            // История наград/наказаний (последние 5)
            let recentOperations = getHistoryOperations().prefix(5)
            
            if recentOperations.isEmpty {
                VStack(spacing: Spacing.s) {
                    Text("📝")
                        .font(.system(size: 32))
                    Text("История пуста")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Text("Родители пока не награждали и не наказывали")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.l)
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(Array(recentOperations)) { operation in
                        childHistoryItem(operation: operation)
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
        }
        .padding(.vertical, Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    /// Элемент истории для детей (с объяснением причин)
    private func childHistoryItem(operation: RewardOperation) -> some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(getHistoryIcon(for: operation.title, isReward: operation.isReward))
                .font(.system(size: 32))
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                // Название действия
                Text(operation.title)
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                
                // Причина (почему наградили/наказали)
                if !operation.reason.isEmpty {
                    Text("Причина: \(operation.reason)")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                // Дата
                Text(formatDate(operation.date))
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
            }
            
            Spacer()
            
            // Количество единорогов (плюс или минус)
            VStack(alignment: .trailing, spacing: Spacing.xxs) {
                Text("\(operation.isReward ? "+" : "-")\(operation.amount)")
                    .font(.body)
                    .fontWeight(.bold)
                    .foregroundColor(operation.isReward ? .successGreen : .dangerRed)
                Text("🦄")
                    .font(.body)
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(operation.isReward ? Color.successGreen.opacity(0.1) : Color.dangerRed.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(operation.isReward ? Color.successGreen.opacity(0.3) : Color.dangerRed.opacity(0.3), lineWidth: 2)
                )
        )
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
                // Загружаем награды из UserDefaults или используем дефолтные
                let enabledRewards = availableRewards.filter { $0.isEnabled }
                
                if enabledRewards.isEmpty {
                    // Сообщение если наград нет
                    VStack(spacing: Spacing.m) {
                        Text("🎁")
                            .font(.system(size: 48))
                        Text("Наград пока нет")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Text("Родители скоро добавят награды в магазин")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(Spacing.xxl)
                } else {
                    ForEach(enabledRewards) { reward in
                        rewardItem(
                            icon: reward.icon,
                            title: reward.title,
                            desc: reward.desc,
                            price: reward.price,
                            canAfford: unicornBalance >= reward.price
                        )
                    }
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func rewardItem(icon: String, title: String, desc: String, price: Int, canAfford: Bool) -> some View {
        Button(action: {
            print("🛒 Нажата награда: \(title), цена: \(price) 🦄, баланс: \(unicornBalance) 🦄, можно купить: \(canAfford)")
            if canAfford {
                buyReward(price: price, title: title)
            } else {
                HapticFeedback.notification(.error)
                print("❌ Недостаточно единорогов для покупки: \(title)")
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
            
            // Загружаем реальную историю из AppStorage
            let operations = getHistoryOperations()
            
            if operations.isEmpty {
                VStack(spacing: Spacing.m) {
                    Text("📝")
                        .font(.system(size: 48))
                    Text("История пуста")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Text("Здесь будут отображаться все ваши награды и наказания")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.xxl)
            } else {
            VStack(spacing: Spacing.s) {
                    ForEach(operations) { operation in
                        historyItemFromOperation(operation: operation)
                    }
            }
            .padding(.horizontal, Spacing.screenPadding)
            }
        }
    }
    
    /// Загрузка истории из AppStorage
    private func getHistoryOperations() -> [RewardOperation] {
        guard let historyData = UserDefaults.standard.string(forKey: "rewards_history"),
              let data = historyData.data(using: .utf8),
              let operations = try? JSONDecoder().decode([RewardOperation].self, from: data) else {
            return []
        }
        return operations.sorted { $0.date > $1.date } // Новые сверху
    }
    
    /// Отображение элемента истории из RewardOperation
    private func historyItemFromOperation(operation: RewardOperation) -> some View {
        let icon = getHistoryIcon(for: operation.title, isReward: operation.isReward)
        
        return HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 28))
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(operation.title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                // Показываем причину (reason)
                if !operation.reason.isEmpty && operation.reason != operation.title {
                    Text(operation.reason)
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                }
                
                Text(formatDate(operation.date))
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Text("\(operation.isReward ? "+" : "-")\(operation.amount) 🦄")
                .font(.body)
                .fontWeight(.bold)
                .foregroundColor(operation.isReward ? .successGreen : .dangerRed)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(operation.isReward ? Color.backgroundMedium.opacity(0.5) : Color.dangerRed.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(operation.isReward ? Color.textSecondary.opacity(0.2) : Color.dangerRed.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    /// Определение иконки для истории
    private func getHistoryIcon(for title: String, isReward: Bool) -> String {
        let lowercased = title.lowercased()
        if lowercased.contains("домашнее задание") || lowercased.contains("дз") {
            return isReward ? "📚" : "📚"
        } else if lowercased.contains("убрал") || lowercased.contains("уборк") {
            return "🧹"
        } else if lowercased.contains("поведение") || lowercased.contains("грубост") {
            return isReward ? "😊" : "😡"
        } else if lowercased.contains("книг") || lowercased.contains("читал") {
            return "📖"
        } else if lowercased.contains("5") || lowercased.contains("оценк") || lowercased.contains("четверт") || lowercased.contains("достижение") {
            return "🏆"
        } else if lowercased.contains("лимит") || lowercased.contains("врем") {
            return "⏰"
        } else if lowercased.contains("обход") || lowercased.contains("блокировк") {
            return "🚫"
        }
        return isReward ? "✅" : "❌"
    }
    
    /// Форматирование даты
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        
        if Calendar.current.isDateInToday(date) {
            formatter.dateFormat = "Сегодня, HH:mm"
        } else if Calendar.current.isDateInYesterday(date) {
            formatter.dateFormat = "Вчера, HH:mm"
        } else {
            formatter.dateStyle = .short
            formatter.timeStyle = .short
        }
        
        return formatter.string(from: date)
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
    
    // Состояние для модального окна подтверждения покупки
    @State private var showPurchaseConfirmation: Bool = false
    @State private var pendingPurchaseTitle: String = ""
    @State private var pendingPurchasePrice: Int = 0
    
    private func buyReward(price: Int, title: String) {
        // ✅ БЕЗОПАСНОСТЬ: Дети могут только тратить единороги на награды, но не изменять баланс напрямую
        // Баланс может изменять только родитель через RewardsModalView
        
        // Проверяем, что баланс достаточен
        guard unicornBalance >= price else {
            print("⚠️ Недостаточно единорогов для покупки: \(title) (нужно \(price), есть \(unicornBalance))")
            HapticFeedback.notification(.error)
            return
        }
        
        // Показываем модальное окно подтверждения
        pendingPurchaseTitle = title
        pendingPurchasePrice = price
        showPurchaseConfirmation = true
    }
    
    /// Подтверждение и выполнение покупки
    private func confirmPurchase() {
        guard unicornBalance >= pendingPurchasePrice else {
            HapticFeedback.notification(.error)
            return
        }
        
        // Haptic feedback
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
        
        // Тратим единороги (это разрешено для детей)
        unicornBalance -= pendingPurchasePrice
        storedUnicornBalance = unicornBalance
        
        // ✅ БЕЗОПАСНОСТЬ: Дети могут ТОЛЬКО тратить единороги, но НЕ могут их добавлять напрямую
        // Обновляем в UserDefaults (единый источник истины)
        UserDefaults.standard.set(unicornBalance, forKey: "child_unicorn_balance")
        
        // Синхронизируем @AppStorage
        storedUnicornBalance = unicornBalance
        
        // Применяем награду в зависимости от типа
        applyReward(pendingPurchaseTitle)
        
        // Отправляем уведомление для обновления других экранов
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        
        print("💰 ChildRewardsScreen: Баланс после покупки: \(unicornBalance) 🦄")
        
        // Успешный feedback
        HapticFeedback.notification(.success)
        
        print("🎁 Куплена награда: \(pendingPurchaseTitle) за \(pendingPurchasePrice) 🦄. Осталось: \(unicornBalance) 🦄")
        
        // Закрываем модальное окно
        showPurchaseConfirmation = false
    }
    
    /// Применение купленной награды
    private func applyReward(_ title: String) {
        let lowercased = title.lowercased()
        
        if lowercased.contains("30 минут игр") || lowercased.contains("игр") {
            // +30 минут игр
            let currentExtraTime = UserDefaults.standard.integer(forKey: "extra_game_time_minutes")
            UserDefaults.standard.set(currentExtraTime + 30, forKey: "extra_game_time_minutes")
            print("✅ Добавлено 30 минут игрового времени")
        } else if lowercased.contains("1 час") || lowercased.contains("экранного времени") {
            // +1 час экранного времени
            let currentExtraTime = UserDefaults.standard.integer(forKey: "extra_screen_time_hours")
            UserDefaults.standard.set(currentExtraTime + 1, forKey: "extra_screen_time_hours")
            print("✅ Добавлен 1 час экранного времени")
        } else if lowercased.contains("30 минут перед сном") || lowercased.contains("время сна") {
            // +30 минут перед сном
            let currentBedtimeDelay = UserDefaults.standard.integer(forKey: "bedtime_delay_minutes")
            UserDefaults.standard.set(currentBedtimeDelay + 30, forKey: "bedtime_delay_minutes")
            print("✅ Добавлено 30 минут перед сном")
        } else if lowercased.contains("пицц") {
            // Заказ пиццы - добавляем в список запросов для родителей
            let _ = [
                "type": "pizza_order",
                "title": "Заказ пиццы",
                "timestamp": Date().timeIntervalSince1970
            ] as [String : Any]
            // TODO: Сохранить запрос в список для родителей
            print("✅ Запрос на заказ пиццы отправлен родителям")
        }
        // Остальные награды обрабатываются аналогично
    }
    
    // MARK: - Reward/Punish Actions (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ)
    
    /// Вознаграждение ребёнка (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ!)
    /// ✅ БЕЗОПАСНОСТЬ: Проверка роли обязательна
    private func rewardChild(amount: Int, reason: String) {
        // ✅ КРИТИЧНАЯ ПРОВЕРКА БЕЗОПАСНОСТИ
        guard isCurrentUserParent() else {
            print("🚨 ПРОБЛЕМА БЕЗОПАСНОСТИ: Попытка наградить ребёнка не родителем!")
            print("   - Роль: \(UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА")")
            HapticFeedback.notification(.error)
            return
        }
        
        let finalReason = reason.isEmpty ? "Вознаграждение родителем" : reason
        
        // Обновляем баланс в AppStorage (синхронизация)
        let currentBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
        let newBalance = currentBalance + amount
        UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
        
        // Обновляем статистику за неделю
        let currentWeekly = UserDefaults.standard.integer(forKey: "child_weekly_earned")
        UserDefaults.standard.set(currentWeekly + amount, forKey: "child_weekly_earned")
        
        // Явно отправляем уведомление для обновления других экранов
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        
        // Обновляем локальные переменные
        unicornBalance = newBalance
        weeklyEarned += amount
        
        // Добавляем в историю (используем ту же логику, что и в RewardsModalView)
        addToHistory(isReward: true, title: finalReason, reason: finalReason, amount: amount)
        
        HapticFeedback.notification(.success)
        print("✅ Вознаградили ребёнка: +\(amount) 🦄, причина: \(finalReason)")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    /// Наказание ребёнка (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ!)
    /// ✅ БЕЗОПАСНОСТЬ: Проверка роли обязательна
    private func punishChild(amount: Int, reason: String) {
        // ✅ КРИТИЧНАЯ ПРОВЕРКА БЕЗОПАСНОСТИ
        guard isCurrentUserParent() else {
            print("🚨 ПРОБЛЕМА БЕЗОПАСНОСТИ: Попытка наказать ребёнка не родителем!")
            print("   - Роль: \(UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА")")
            HapticFeedback.notification(.error)
            return
        }
        
        let finalReason = reason.isEmpty ? "Наказание родителем" : reason
        
        // Обновляем баланс в AppStorage (синхронизация)
        let currentBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
        let newBalance = max(0, currentBalance - amount) // Не может быть отрицательным
        UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
        
        // Обновляем статистику за неделю
        let currentWeekly = UserDefaults.standard.integer(forKey: "child_weekly_punished")
        UserDefaults.standard.set(currentWeekly + amount, forKey: "child_weekly_punished")
        
        // Явно отправляем уведомление для обновления других экранов
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        
        // Обновляем локальные переменные
        unicornBalance = newBalance
        weeklyPunished += amount
        
        // Добавляем в историю
        addToHistory(isReward: false, title: finalReason, reason: finalReason, amount: amount)
        
        HapticFeedback.notification(.warning)
        print("❌ Наказали ребёнка: -\(amount) 🦄, причина: \(finalReason)")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    // MARK: - History Management
    
    @AppStorage("rewards_history") private var rewardsHistoryData: String = "[]"
    
    private func addToHistory(isReward: Bool, title: String, reason: String, amount: Int) {
        let operation = RewardOperation(
            id: UUID().uuidString,
            title: title,
            reason: reason,
            amount: amount,
            isReward: isReward,
            date: Date()
        )
        
        var operations = getRecentOperations()
        operations.insert(operation, at: 0)
        
        // Сохраняем последние 50 операций
        let limitedOperations = Array(operations.prefix(50))
        
        if let data = try? JSONEncoder().encode(limitedOperations),
           let jsonString = String(data: data, encoding: .utf8) {
            rewardsHistoryData = jsonString
        }
    }
    
    private func getRecentOperations() -> [RewardOperation] {
        guard let data = rewardsHistoryData.data(using: .utf8),
              let operations = try? JSONDecoder().decode([RewardOperation].self, from: data) else {
            return []
        }
        return operations.sorted { $0.date > $1.date }
    }
    
    private func sendRequestToParents(_ achievement: String) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
        
        // Сохраняем запрос на достижение в AppStorage для родителей
        let timestamp = Date().timeIntervalSince1970
        let achievementRequest: [String: Any] = [
            "id": UUID().uuidString,
            "achievement": achievement,
            "timestamp": timestamp,
            "status": "pending" // pending, approved, rejected
        ]
        
        // Читаем существующие запросы
        var requests: [[String: Any]] = []
        if let existingData = UserDefaults.standard.data(forKey: "child_achievement_requests"),
           let decoded = try? JSONSerialization.jsonObject(with: existingData) as? [[String: Any]] {
            requests = decoded
        }
        
        // Добавляем новый запрос
        requests.append(achievementRequest)
        
        // Сохраняем обратно
        if let encoded = try? JSONSerialization.data(withJSONObject: requests) {
            UserDefaults.standard.set(encoded, forKey: "child_achievement_requests")
            print("📣 Отправлен запрос родителям: \(achievement) (ID: \(achievementRequest["id"] ?? ""))")
            print("📊 Всего запросов: \(requests.count)")
        }
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

// MARK: - Purchase Confirmation Modal

struct PurchaseConfirmationModal: View {
    let title: String
    let price: Int
    let balance: Int
    let onConfirm: () -> Void
    let onCancel: () -> Void
    
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("🎁")
                    .font(.system(size: 60))
                
                Text("Подтвердите покупку")
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text("Награда:")
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(title)
                            .foregroundColor(.textPrimary)
                            .fontWeight(.semibold)
                    }
                    
                    HStack {
                        Text("Стоимость:")
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(price) 🦄")
                            .foregroundColor(.textPrimary)
                            .fontWeight(.bold)
                    }
                    
                    HStack {
                        Text("Ваш баланс:")
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(balance) 🦄")
                            .foregroundColor(.textPrimary)
                    }
                    
                    HStack {
                        Text("Останется:")
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(balance - price) 🦄")
                            .foregroundColor(.successGreen)
                            .fontWeight(.bold)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.5))
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
                
                HStack(spacing: Spacing.m) {
                    Button(action: onCancel) {
                        Text("Отмена")
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(Color.dangerRed)
                            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                    }
                    
                    Button(action: onConfirm) {
                        Text("Купить")
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(Color.successGreen)
                            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                    }
                }
                
                Spacer()
            }
            .padding(Spacing.l)
            .background(LinearGradient.backgroundGradient)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Закрыть") {
                        onCancel()
                    }
                }
            }
        }
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



