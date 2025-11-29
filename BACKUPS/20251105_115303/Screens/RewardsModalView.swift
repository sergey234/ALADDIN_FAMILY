import SwiftUI

/// 🦄 Rewards Modal View
/// Модальное окно управления вознаграждениями ребёнка (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ!)
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
@available(iOS 14.0, *)
struct RewardsModalView: View {
    
    // MARK: - Properties
    
    @Environment(\.presentationMode) var presentationMode
    @Binding var unicornBalance: Int
    @Binding var weeklyRewarded: Int
    @Binding var weeklyPunished: Int
    
    // Альтернативный способ закрытия (совместимо с iOS 14+)
    private func dismiss() {
        presentationMode.wrappedValue.dismiss()
    }
    
    // Проверка роли пользователя (ТОЛЬКО РОДИТЕЛИ могут видеть кнопки)
    private var isUserParent: Bool {
        guard let roleString = UserDefaults.standard.string(forKey: "current_user_role"),
              let role = FamilyRole(rawValue: roleString) else {
            return false
        }
        return role == .parent
    }
    
    // Запросы на цели (из AppStorage)
    @AppStorage("child_goal_title_pending") private var goalTitlePending: String = ""
    @AppStorage("child_goal_cost_pending") private var goalCostPending: Int = 0
    @AppStorage("child_goal_approval_pending") private var goalApprovalPending: Bool = false
    
    // Запросы на достижения (из AppStorage)
    @State private var achievementRequests: [AchievementRequest] = []
    
    // История операций (из AppStorage)
    @AppStorage("rewards_history") private var rewardsHistoryData: String = "[]"
    
    @State private var showRewardInput: Bool = false
    @State private var showPunishInput: Bool = false
    @State private var rewardAmount: String = "10"
    @State private var punishAmount: String = "10"
    @State private var rewardReason: String = ""
    @State private var punishReason: String = ""
    
    // Управление магазином наград
    @State private var showShopManagement: Bool = false
    @AppStorage("shop_rewards_list") private var shopRewardsData: String = ""
    @State private var shopRewards: [ShopReward] = []
    
    // Управление играми
    @State private var showGamesSettings: Bool = false
    @StateObject private var gamesSettingsManager = GamesSettingsManager.shared
    
    // Раздвигающиеся секции
    @State private var isEarningWaysExpanded: Bool = false
    @State private var isPunishmentReasonsExpanded: Bool = false
    @State private var isShopManagementExpanded: Bool = false
    @State private var isGamesManagementExpanded: Bool = false
    @State private var isOperationsHistoryExpanded: Bool = false
    
    // Редактируемые данные
    @AppStorage("earning_ways_list") private var earningWaysData: String = ""
    @AppStorage("punishment_reasons_list") private var punishmentReasonsData: String = ""
    
    @State private var earningWays: [EarningWay] = []
    @State private var punishmentReasons: [PunishmentReason] = []
    
    // Модалы для редактирования
    @State private var showAddEarningWay: Bool = false
    @State private var showEditEarningWay: Bool = false
    @State private var editingEarningWay: EarningWay?
    
    @State private var showAddPunishmentReason: Bool = false
    @State private var showEditPunishmentReason: Bool = false
    @State private var editingPunishmentReason: PunishmentReason?
    
    // MARK: - Achievement Request Model
    
    struct AchievementRequest: Identifiable {
        let id: String
        let achievement: String
        let timestamp: TimeInterval
        var status: String // "pending", "approved", "rejected"
        
        var dateString: String {
            let date = Date(timeIntervalSince1970: timestamp)
            let formatter = DateFormatter()
            formatter.dateStyle = .short
            formatter.timeStyle = .short
            return formatter.string(from: date)
        }
    }
    
    // MARK: - Body
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel("Фон модального окна вознаграждений")
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Баланс единорогов
                        balanceCard
                        
                        // Быстрые действия (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ!)
                        if isUserParent {
                            quickActions
                        }
                        
                        // 🎯 Запросы на установку цели
                        if goalApprovalPending {
                            goalRequestCard
                        }
                        
                        // 📣 Запросы на достижения от ребёнка
                        if !achievementRequests.isEmpty {
                            achievementRequestsSection
                        }
                        
                        // Как заработать
                        earningWaysSection
                        
                        // За что можно наказать
                        punishmentReasonsSection
                        
                        // 🏪 Управление магазином наград (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ)
                        if isUserParent {
                            shopManagementSection
                        }
                        
                        // 🎮 Управление играми (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ)
                        if isUserParent {
                            gamesManagementSection
                        }
                        
                        // 📊 История операций
                        operationsHistorySection
                        
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Содержимое модального окна вознаграждений")
            }
            .navigationBarTitleDisplayMode(.inline)
            .safeAreaInset(edge: .top) {
                Color.clear.frame(height: Spacing.m)
            }
        .task {
            print("🚨 RewardsModalView загружен!")
            loadAchievementRequests()
        }
        .onAppear {
            loadAchievementRequests()
            loadShopRewards()
            loadEarningWays()
            loadPunishmentReasons()
            // Синхронизация баланса из UserDefaults с @Binding
            let currentBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
            let currentEarned = UserDefaults.standard.integer(forKey: "child_weekly_earned")
            let currentPunished = UserDefaults.standard.integer(forKey: "child_weekly_punished")
            if unicornBalance != currentBalance {
                unicornBalance = currentBalance
            }
            if weeklyRewarded != currentEarned {
                weeklyRewarded = currentEarned
            }
            if weeklyPunished != currentPunished {
                weeklyPunished = currentPunished
            }
            
            // ✅ ДИАГНОСТИКА: Логирование для проверки секции управления магазином
            let isParent = isUserParent
            let roleString = UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА"
            print("═══════════════════════════════════════════════════════════")
            print("🔍 DEBUG RewardsModalView.onAppear:")
            print("   📋 Роль пользователя: '\(roleString)'")
            print("   👨‍👩‍👧 isUserParent = \(isParent)")
            print("   🏪 shopRewards.count = \(shopRewards.count)")
            print("   ✅ earningWays.count = \(earningWays.count)")
            print("   ❌ punishmentReasons.count = \(punishmentReasons.count)")
            print("   ✅ Секция 'Управление магазином' будет \(isParent ? "ВИДНА" : "СКРЫТА")")
            print("═══════════════════════════════════════════════════════════")
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
        .sheet(isPresented: $showShopManagement) {
            ShopManagementModal(
                rewards: $shopRewards,
                onSave: {
                    saveShopRewards()
                    showShopManagement = false
                }
            )
        }
        .sheet(isPresented: $showGamesSettings) {
            GamesParentalControlView()
                .environmentObject(NavigationManager())
        }
        .sheet(isPresented: $showAddEarningWay) {
            AddEarningWayModal(
                isPresented: $showAddEarningWay,
                onAdd: { newWay in
                    earningWays.append(newWay)
                    saveEarningWays()
                    showAddEarningWay = false
                }
            )
        }
        .sheet(isPresented: $showEditEarningWay) {
            if let editing = editingEarningWay {
                EditEarningWayModal(
                    isPresented: $showEditEarningWay,
                    earningWay: Binding(
                        get: { editing },
                        set: { newValue in
                            if let index = earningWays.firstIndex(where: { $0.id == editing.id }) {
                                earningWays[index] = newValue
                                saveEarningWays()
                            }
                        }
                    ),
                    onSave: {
                        saveEarningWays()
                        showEditEarningWay = false
                    },
                    onDelete: {
                        earningWays.removeAll { $0.id == editing.id }
                        saveEarningWays()
                        showEditEarningWay = false
                    }
                )
            }
        }
        .sheet(isPresented: $showAddPunishmentReason) {
            AddPunishmentReasonModal(
                isPresented: $showAddPunishmentReason,
                onAdd: { newReason in
                    punishmentReasons.append(newReason)
                    savePunishmentReasons()
                    showAddPunishmentReason = false
                }
            )
        }
        .sheet(isPresented: $showEditPunishmentReason) {
            if let editing = editingPunishmentReason {
                EditPunishmentReasonModal(
                    isPresented: $showEditPunishmentReason,
                    punishmentReason: Binding(
                        get: { editing },
                        set: { newValue in
                            if let index = punishmentReasons.firstIndex(where: { $0.id == editing.id }) {
                                punishmentReasons[index] = newValue
                                savePunishmentReasons()
                            }
                        }
                    ),
                    onSave: {
                        savePunishmentReasons()
                        showEditPunishmentReason = false
                    },
                    onDelete: {
                        punishmentReasons.removeAll { $0.id == editing.id }
                        savePunishmentReasons()
                        showEditPunishmentReason = false
                    }
                )
            }
        }
        .toolbar {
                // ⚙️ Кнопка настроек игр (СЛЕВА) - ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ
                ToolbarItem(placement: .navigationBarLeading) {
                    if isUserParent {
                        Button(action: {
                            HapticFeedback.impact(.light)
                            print("🔍 DEBUG: Открываем настройки игр")
                            showGamesSettings = true
                        }) {
                            Image(systemName: "gearshape.fill")
                                .font(.system(size: 20))
                                .foregroundColor(.secondaryGold)
                        }
                        .accessibilityLabel("Настройки игр")
                        .accessibilityHint("Нажмите для открытия настроек игр")
                    }
                }
                
                // Заголовок по центру
                ToolbarItem(placement: .principal) {
                    HStack(spacing: Spacing.xs) {
                        Text("🦄")
                            .font(.system(size: 20))
                            .accessibilityLabel("Единорог")
                        Text("Вознаграждение ребёнка")
                            .font(.h3)
                            .foregroundColor(Color(hex: "C084FC"))
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Вознаграждение ребёнка")
                }
                
                // Кнопка закрытия (СПРАВА)
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        dismiss()
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.textSecondary)
                    }
                    .accessibilityLabel("Закрыть")
                    .accessibilityHint("Нажмите для закрытия модального окна")
                }
            }
        }
    }
    
    // MARK: - Balance Card
    
    private var balanceCard: some View {
        VStack(spacing: Spacing.m) {
            // Иконка
            Text("🦄")
                .font(.system(size: 56))
                .accessibilityLabel("Единорог")
            
            // Баланс
            Text("\(unicornBalance)")
                .font(.system(size: 36, weight: .bold))
                .foregroundColor(Color(hex: "C084FC"))
                .accessibilityLabel("Баланс: \(unicornBalance) единорогов")
            
            Text("Единорогов на счету")
                .font(.caption)
                .foregroundColor(.textSecondary)
                .accessibilityLabel("Единорогов на счету")
            
            // Статистика за неделю
            Divider()
                .background(Color.textSecondary.opacity(0.3))
                .padding(.vertical, Spacing.s)
                .accessibilityElement(children: .ignore)
            
            HStack(spacing: Spacing.xxl) {
                VStack(spacing: Spacing.xs) {
                    Text("+\(weeklyRewarded)")
                        .font(.h2)
                        .foregroundColor(.successGreen)
                    Text("Вознаграждено\nза неделю")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Вознаграждено за неделю: \(weeklyRewarded) единорогов")
                
                VStack(spacing: Spacing.xs) {
                    Text("-\(weeklyPunished)")
                        .font(.h2)
                        .foregroundColor(.dangerRed)
                    Text("Наказано\nза неделю")
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Наказано за неделю: \(weeklyPunished) единорогов")
            }
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.l)
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
        .cardShadow()
        .appGlassmorphism()
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Карточка баланса единорогов")
    }
    
    // MARK: - Shop Management Section (Collapsible)
    
    private var shopManagementSection: some View {
        CollapsibleSection(
            icon: "🏪",
            title: "Управление магазином наград",
            subtitle: "Активных: \(shopRewards.filter { $0.isEnabled }.count) из \(shopRewards.count)",
            isExpanded: $isShopManagementExpanded
        ) {
            VStack(spacing: Spacing.m) {
                // Кнопка "Настроить" (открывает полный модал)
                Button(action: {
                    print("🔍 DEBUG: Открываем управление магазином наград")
                    showShopManagement = true
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "gearshape.fill")
                            .font(.system(size: 16))
                        Text("⚙️ Настроить магазин")
                            .font(.body)
                            .fontWeight(.semibold)
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.s)
                    .background(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.secondaryGold, Color.secondaryGold.opacity(0.8)]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .clipShape(Capsule())
                    .shadow(color: Color.secondaryGold.opacity(0.4), radius: 4, x: 0, y: 2)
                }
                
                // Полный список наград (только для родителей)
                if isUserParent && !shopRewards.isEmpty {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("📋 Все награды в магазине:")
                            .font(.body)
                            .fontWeight(.semibold)
                            .foregroundColor(.textPrimary)
                        
                        ForEach($shopRewards) { $reward in
                            shopRewardEditRow(reward: $reward)
                        }
                    }
                } else if !isUserParent && !shopRewards.isEmpty {
                    // Для детей - только предпросмотр активных наград
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("📋 Доступные награды:")
                            .font(.body)
                            .fontWeight(.semibold)
                            .foregroundColor(.textPrimary)
                        
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: Spacing.s) {
                                ForEach(shopRewards.filter { $0.isEnabled }) { reward in
                                    rewardPreviewCard(reward: reward)
                                }
                            }
                        }
                    }
                }
            }
        }
        .padding(.vertical, Spacing.s)
    }
    
    /// Строка редактирования награды из магазина (для родителей)
    private func shopRewardEditRow(reward: Binding<ShopReward>) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text(reward.icon.wrappedValue)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(reward.title.wrappedValue)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    Text(reward.desc.wrappedValue)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                Text("\(reward.price.wrappedValue) 🦄")
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
            }
            
            // Панель управления
            HStack(spacing: Spacing.m) {
                // Toggle вкл/выкл
                VStack(spacing: Spacing.xxs) {
                    Toggle("", isOn: reward.isEnabled)
                        .labelsHidden()
                        .scaleEffect(0.8)
                        .onChange(of: reward.isEnabled.wrappedValue) { _ in
                            saveShopRewards()
                        }
                    Text(reward.isEnabled.wrappedValue ? "Вкл" : "Выкл")
                        .font(.captionSmall)
                        .foregroundColor(reward.isEnabled.wrappedValue ? .successGreen : .textSecondary)
                }
                
                Spacer()
                
                // Кнопка редактирования открывает модал через showShopManagement
                Button(action: {
                    // Можно открыть модал редактирования конкретной награды
                    showShopManagement = true
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "pencil.circle.fill")
                            .font(.caption)
                        Text("Изменить")
                            .font(.caption)
                    }
                    .foregroundColor(.secondaryGold)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.small)
                            .fill(Color.secondaryGold.opacity(0.1))
                    )
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(reward.isEnabled.wrappedValue ? Color.secondaryGold.opacity(0.05) : Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(
                            reward.isEnabled.wrappedValue ? Color.secondaryGold.opacity(0.3) : Color.textSecondary.opacity(0.2),
                            lineWidth: 1
                        )
                )
        )
    }
    
    // MARK: - Games Management Section (Collapsible)
    
    private var gamesManagementSection: some View {
        CollapsibleSection(
            icon: "🎮",
            title: "Управление играми",
            subtitle: "Всего игр: 4 | Настройте награды и параметры",
            isExpanded: $isGamesManagementExpanded
        ) {
            VStack(spacing: Spacing.m) {
                // Кнопка "Настроить игры" (открывает полный модал)
                Button(action: {
                    print("🔍 DEBUG: Открываем настройки игр из секции")
                    showGamesSettings = true
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "gearshape.fill")
                            .font(.system(size: 16))
                        Text("⚙️ Настроить игры")
                            .font(.body)
                            .fontWeight(.semibold)
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.s)
                    .background(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.primaryBlue, Color.primaryBlue.opacity(0.8)]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .clipShape(Capsule())
                    .shadow(color: Color.primaryBlue.opacity(0.4), radius: 4, x: 0, y: 2)
                }
                
                // Полный список игр с параметрами
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("📋 Все игры:")
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    // 🛡️ Юный защитник
                    gameDetailCard(
                        icon: "🛡️",
                        title: "Юный защитник",
                        description: "Образовательная игра: 6 уроков безопасности",
                        isEnabled: gamesSettingsManager.youngDefenderEnabled,
                        parameters: [
                            ("Награда за урок", gamesSettingsManager.lessonReward),
                            ("Бонус за 5 уроков", gamesSettingsManager.bonus5Lessons),
                            ("Бонус за все 6 уроков", gamesSettingsManager.bonusAll6)
                        ]
                    )
                    
                    // 🦄 Мой питомец (всегда вкл)
                    gameDetailCard(
                        icon: "🦄",
                        title: "Мой питомец",
                        description: "Тамагочи-питомец с индикаторами ❤️🍎⭐😊",
                        isEnabled: true,
                        isLocked: true,
                        parameters: [
                            ("Покормить", gamesSettingsManager.petFeedCost),
                            ("Поиграть", gamesSettingsManager.petPlayCost),
                            ("Погладить", gamesSettingsManager.petPetCost)
                        ]
                    )
                    
                    // 🕵️ Я защитник
                    gameDetailCard(
                        icon: "🕵️",
                        title: "Я защитник",
                        description: "Квесты по безопасности для семьи",
                        isEnabled: gamesSettingsManager.protectorEnabled,
                        parameters: [
                            ("Детектив фишинга", gamesSettingsManager.phishingReward),
                            ("Защитник устройства", gamesSettingsManager.deviceReward)
                        ]
                    )
                    
                    // 🏆 Турнир семьи
                    gameDetailCard(
                        icon: "🏆",
                        title: "Турнир семьи",
                        description: "Соревнование между членами семьи",
                        isEnabled: gamesSettingsManager.tournamentEnabled,
                        parameters: [
                            ("Первое место", gamesSettingsManager.firstPlaceReward),
                            ("Второе место", gamesSettingsManager.secondPlaceReward),
                            ("Третье место", gamesSettingsManager.thirdPlaceReward)
                        ]
                    )
                }
            }
        }
        .padding(.vertical, Spacing.s)
    }
    
    /// Детальная карточка игры с параметрами
    private func gameDetailCard(icon: String, title: String, description: String, isEnabled: Bool, isLocked: Bool = false, parameters: [(String, Int)]) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text(icon)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(title)
                            .font(.body)
                            .fontWeight(.semibold)
                            .foregroundColor(.textPrimary)
                        
                        if isLocked {
                            Text("🔒 ВСЕГДА ВКЛ")
                                .font(.captionSmall)
                                .foregroundColor(.primaryBlue)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(
                                    Capsule()
                                        .fill(Color.primaryBlue.opacity(0.2))
                                )
                        } else {
                            Circle()
                                .fill(isEnabled ? Color.successGreen : Color.textTertiary)
                                .frame(width: 8, height: 8)
                            Text(isEnabled ? "Вкл" : "Выкл")
                                .font(.captionSmall)
                                .foregroundColor(isEnabled ? .successGreen : .textSecondary)
                        }
                    }
                    
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
            }
            
            // Параметры игры
            if isEnabled || isLocked {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    ForEach(parameters, id: \.0) { param in
                        HStack {
                            Text(param.0)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(param.1) 🦄")
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundColor(.primaryBlue)
                        }
                    }
                }
                .padding(Spacing.s)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.small)
                        .fill(Color.primaryBlue.opacity(0.05))
                )
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(isEnabled || isLocked ? Color.primaryBlue.opacity(0.05) : Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(
                            isEnabled || isLocked ? Color.primaryBlue.opacity(0.2) : Color.textSecondary.opacity(0.2),
                            lineWidth: 1
                        )
                )
        )
    }
    
    
    /// Карточка предпросмотра награды (как она выглядит для детей)
    private func rewardPreviewCard(reward: ShopReward) -> some View {
        VStack(spacing: Spacing.xs) {
            Text(reward.icon)
                .font(.system(size: 32))
            
            Text(reward.title)
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(.textPrimary)
                .lineLimit(2)
                .multilineTextAlignment(.center)
                .frame(width: 80)
            
            Text("\(reward.price) 🦄")
                .font(.captionSmall)
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.s)
        .frame(width: 100, height: 100)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(Color.textSecondary.opacity(0.2), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Quick Actions
    
    private var quickActions: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            // Заголовок секции с улучшенной видимостью
            HStack {
                Text("👨‍👩‍👧")
                    .font(.system(size: 24))  // УВЕЛИЧЕНО с 18
                Text("Воспитание ребенка:")
                    .font(.h2)  // УВЕЛИЧЕНО с .h3
                    .foregroundColor(.textPrimary)
                    .fontWeight(.bold)  // ДОБАВЛЕНО
            }
            .padding(.horizontal, Spacing.screenPadding)
            .padding(.bottom, Spacing.s)  // ДОБАВЛЕНО отступ снизу
            
            // Кнопки действий
            HStack(spacing: Spacing.m) {
                // Кнопка "Вознаградить"
                Button(action: {
                    print("🔍 DEBUG: Нажата кнопка 'Вознаградить'")
                    print("🔍 DEBUG: showRewardInput до = \(showRewardInput)")
                    HapticFeedback.impact(.medium)
                    showRewardInput = true
                    print("🔍 DEBUG: showRewardInput после = \(showRewardInput)")
                }) {
                    VStack(spacing: Spacing.xs) {
                        Text("✅")
                            .font(.system(size: 36))  // УВЕЛИЧЕНО с 32
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
                    print("🔍 DEBUG: Нажата кнопка 'Наказать'")
                    print("🔍 DEBUG: showPunishInput до = \(showPunishInput)")
                    HapticFeedback.impact(.medium)
                    showPunishInput = true
                    print("🔍 DEBUG: showPunishInput после = \(showPunishInput)")
                }) {
                    VStack(spacing: Spacing.xs) {
                        Text("❌")
                            .font(.system(size: 36))  // УВЕЛИЧЕНО с 32
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
            .padding(.top, Spacing.xs)  // ДОБАВЛЕНО отступ сверху
        }
        .padding(.vertical, Spacing.m)
        .padding(.horizontal, Spacing.screenPadding)  // ДОБАВЛЕН внешний padding
        .background(
            // ДОБАВЛЕН фоновый цвет для лучшей видимости
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .onAppear {
            print("🔍 DEBUG RewardsModalView: quickActions рендерится")
        }
    }
    
    // MARK: - Earning Ways Section (Collapsible)
    
    private var earningWaysSection: some View {
        CollapsibleSection(
            icon: "✅",
            title: "Как заработать",
            subtitle: "\(earningWays.filter { $0.isEnabled }.count) активных способов",
            isExpanded: $isEarningWaysExpanded
        ) {
            VStack(spacing: Spacing.s) {
                ForEach($earningWays) { $earningWay in
                    if isUserParent {
                        // Для родителей - редактируемая строка
                        earningWayEditableRow(earningWay: $earningWay)
                    } else {
                        // Для детей - только просмотр
                        earningWayRow(icon: earningWay.icon, title: earningWay.title, subtitle: earningWay.subtitle, amount: "+\(earningWay.amount) 🦄")
                    }
                }
                
                // Кнопка добавления (только для родителей)
                if isUserParent {
                    Button(action: {
                        showAddEarningWay = true
                    }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 18))
                                .foregroundColor(.successGreen)
                            Text("Добавить новый способ заработка")
                                .font(.body)
                                .foregroundColor(.successGreen)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.successGreen.opacity(0.1))
                                .overlay(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .stroke(Color.successGreen.opacity(0.3), lineWidth: 1)
                                )
                        )
                    }
                }
            }
        }
        .padding(.vertical, Spacing.s)
    }
    
    private func earningWayRow(icon: String, title: String, subtitle: String, amount: String) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 24))
                .accessibilityLabel("Иконка: \(icon)")
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(subtitle)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(title): \(subtitle)")
            
            Spacer()
            
            Text(amount)
                .font(.body)
                .fontWeight(.bold)
                .foregroundColor(.successGreen)
                .accessibilityLabel("Награда: \(amount)")
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(subtitle), награда \(amount)")
    }
    
    /// Редактируемая строка способа заработка (только для родителей)
    private func earningWayEditableRow(earningWay: Binding<EarningWay>) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text(earningWay.icon.wrappedValue)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(earningWay.title.wrappedValue)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    Text(earningWay.subtitle.wrappedValue)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                Text("+\(earningWay.amount.wrappedValue) 🦄")
                    .font(.bodyBold)
                    .foregroundColor(.successGreen)
            }
            
            // Панель управления (только для родителей)
            HStack(spacing: Spacing.m) {
                // Toggle вкл/выкл
                VStack(spacing: Spacing.xxs) {
                    Toggle("", isOn: earningWay.isEnabled)
                        .labelsHidden()
                        .scaleEffect(0.8)
                        .onChange(of: earningWay.isEnabled.wrappedValue) { _ in
                            saveEarningWays()
                        }
                    Text(earningWay.isEnabled.wrappedValue ? "Вкл" : "Выкл")
                        .font(.captionSmall)
                        .foregroundColor(earningWay.isEnabled.wrappedValue ? .successGreen : .textSecondary)
                }
                
                // Кнопка редактирования
                Button(action: {
                    editingEarningWay = earningWay.wrappedValue
                    showEditEarningWay = true
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "pencil.circle.fill")
                            .font(.caption)
                        Text("Изменить")
                            .font(.caption)
                    }
                    .foregroundColor(.secondaryGold)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.small)
                            .fill(Color.secondaryGold.opacity(0.1))
                    )
                }
                
                // Быстрое изменение награды (+/-)
                HStack(spacing: Spacing.xs) {
                    Button(action: {
                        if earningWay.amount.wrappedValue > 1 {
                            earningWay.amount.wrappedValue -= 1
                            saveEarningWays()
                        }
                    }) {
                        Image(systemName: "minus.circle.fill")
                            .foregroundColor(.dangerRed)
                            .font(.system(size: 18))
                    }
                    
                    Text("\(earningWay.amount.wrappedValue)")
                        .font(.caption)
                        .frame(width: 30)
                    
                    Button(action: {
                        earningWay.amount.wrappedValue += 1
                        saveEarningWays()
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .foregroundColor(.successGreen)
                            .font(.system(size: 18))
                    }
                }
                
                Spacer()
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(earningWay.isEnabled.wrappedValue ? Color.successGreen.opacity(0.05) : Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(
                            earningWay.isEnabled.wrappedValue ? Color.successGreen.opacity(0.3) : Color.textSecondary.opacity(0.2),
                            lineWidth: 1
                        )
                )
        )
    }
    
    // MARK: - Punishment Reasons Section (Collapsible)
    
    private var punishmentReasonsSection: some View {
        CollapsibleSection(
            icon: "❌",
            title: "За что можно наказать",
            subtitle: "\(punishmentReasons.filter { $0.isEnabled }.count) активных причин",
            isExpanded: $isPunishmentReasonsExpanded
        ) {
            VStack(spacing: Spacing.s) {
                ForEach($punishmentReasons) { $punishmentReason in
                    if isUserParent {
                        // Для родителей - редактируемая строка
                        punishmentReasonEditableRow(punishmentReason: $punishmentReason)
                    } else {
                        // Для детей - только просмотр
                        punishmentReasonRow(icon: punishmentReason.icon, title: punishmentReason.title, subtitle: punishmentReason.subtitle, amount: "-\(punishmentReason.amount) 🦄")
                    }
                }
                
                // Кнопка добавления (только для родителей)
                if isUserParent {
                    Button(action: {
                        showAddPunishmentReason = true
                    }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 18))
                                .foregroundColor(.dangerRed)
                            Text("Добавить новую причину наказания")
                                .font(.body)
                                .foregroundColor(.dangerRed)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .fill(Color.dangerRed.opacity(0.1))
                                .overlay(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .stroke(Color.dangerRed.opacity(0.3), lineWidth: 1)
                                )
                        )
                    }
                }
            }
        }
        .padding(.vertical, Spacing.s)
    }
    
    private func punishmentReasonRow(icon: String, title: String, subtitle: String, amount: String) -> some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 24))
                .accessibilityLabel("Иконка: \(icon)")
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(subtitle)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(title): \(subtitle)")
            
            Spacer()
            
            Text(amount)
                .font(.body)
                .fontWeight(.bold)
                .foregroundColor(.dangerRed)
                .accessibilityLabel("Штраф: \(amount)")
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(subtitle), штраф \(amount)")
    }
    
    /// Редактируемая строка причины наказания (только для родителей)
    private func punishmentReasonEditableRow(punishmentReason: Binding<PunishmentReason>) -> some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text(punishmentReason.icon.wrappedValue)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(punishmentReason.title.wrappedValue)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    Text(punishmentReason.subtitle.wrappedValue)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                Text("-\(punishmentReason.amount.wrappedValue) 🦄")
                    .font(.bodyBold)
                    .foregroundColor(.dangerRed)
            }
            
            // Панель управления (только для родителей)
            HStack(spacing: Spacing.m) {
                // Toggle вкл/выкл
                VStack(spacing: Spacing.xxs) {
                    Toggle("", isOn: punishmentReason.isEnabled)
                        .labelsHidden()
                        .scaleEffect(0.8)
                        .onChange(of: punishmentReason.isEnabled.wrappedValue) { _ in
                            savePunishmentReasons()
                        }
                    Text(punishmentReason.isEnabled.wrappedValue ? "Вкл" : "Выкл")
                        .font(.captionSmall)
                        .foregroundColor(punishmentReason.isEnabled.wrappedValue ? .dangerRed : .textSecondary)
                }
                
                // Кнопка редактирования
                Button(action: {
                    editingPunishmentReason = punishmentReason.wrappedValue
                    showEditPunishmentReason = true
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "pencil.circle.fill")
                            .font(.caption)
                        Text("Изменить")
                            .font(.caption)
                    }
                    .foregroundColor(.secondaryGold)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.small)
                            .fill(Color.secondaryGold.opacity(0.1))
                    )
                }
                
                // Быстрое изменение штрафа (+/-)
                HStack(spacing: Spacing.xs) {
                    Button(action: {
                        if punishmentReason.amount.wrappedValue > 1 {
                            punishmentReason.amount.wrappedValue -= 1
                            savePunishmentReasons()
                        }
                    }) {
                        Image(systemName: "minus.circle.fill")
                            .foregroundColor(.dangerRed)
                            .font(.system(size: 18))
                    }
                    
                    Text("\(punishmentReason.amount.wrappedValue)")
                        .font(.caption)
                        .frame(width: 30)
                    
                    Button(action: {
                        punishmentReason.amount.wrappedValue += 1
                        savePunishmentReasons()
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .foregroundColor(.dangerRed)
                            .font(.system(size: 18))
                    }
                }
                
                Spacer()
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(punishmentReason.isEnabled.wrappedValue ? Color.dangerRed.opacity(0.05) : Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(
                            punishmentReason.isEnabled.wrappedValue ? Color.dangerRed.opacity(0.3) : Color.textSecondary.opacity(0.2),
                            lineWidth: 1
                        )
                )
        )
    }
    
    // MARK: - Goal Request Card
    
    private var goalRequestCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("🎯")
                    .font(.system(size: 24))
                Text("Запрос на установку цели")
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            Text("Ребёнок хочет получить:")
                .font(.caption)
                .foregroundColor(.textSecondary)
            
            HStack {
                Text(goalTitlePending.isEmpty ? "Новая игра" : goalTitlePending)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Spacer()
                Text("\(goalCostPending) 🦄")
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
            }
            .padding(Spacing.s)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.secondaryGold.opacity(0.1))
            )
            
            HStack(spacing: Spacing.s) {
                Button(action: {
                    HapticFeedback.impact(.medium)
                    approveGoal()
                }) {
                    Text("✅ Одобрить")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.successGreen)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(PlainButtonStyle())
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    rejectGoal()
                }) {
                    Text("❌ Отклонить")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.dangerRed)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.secondaryGold.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 2)
                )
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Operations History Section (Collapsible)
    
    private var operationsHistorySection: some View {
        let recentOperations = getRecentOperations()
        
        return CollapsibleSection(
            icon: "📊",
            title: "История операций",
            subtitle: recentOperations.isEmpty ? "Пусто" : "Последние \(min(recentOperations.count, 10)) операций",
            isExpanded: $isOperationsHistoryExpanded
        ) {
            Group {
                if recentOperations.isEmpty {
                    // Сообщение, если история пуста
                    VStack(spacing: Spacing.m) {
                        Text("📝")
                            .font(.system(size: 48))
                        Text("История операций пуста")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Text("Здесь будут отображаться все награды и наказания ребёнка")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(Spacing.xxl)
                } else {
                    // Показываем последние 10 операций
                    VStack(spacing: Spacing.s) {
                        ForEach(recentOperations.prefix(10), id: \.id) { operation in
                            operationHistoryRow(operation: operation)
                        }
                    }
                }
            }
        }
        .padding(.vertical, Spacing.s)
    }
    
    private func operationHistoryRow(operation: RewardOperation) -> some View {
        HStack(spacing: Spacing.m) {
            Text(operation.isReward ? "✅" : "❌")
                .font(.system(size: 24))
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(operation.title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(operation.reason)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
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
                .fill(operation.isReward ? Color.successGreen.opacity(0.08) : Color.dangerRed.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(operation.isReward ? Color.successGreen.opacity(0.2) : Color.dangerRed.opacity(0.2), lineWidth: 1)
                )
        )
    }
    
    // MARK: - Achievement Requests Section
    
    private var achievementRequestsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("📣")
                    .font(.system(size: 24))
                Text("Запросы на достижения")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                ForEach(achievementRequests.filter { $0.status == "pending" }) { request in
                    achievementRequestCard(request: request)
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func achievementRequestCard(request: AchievementRequest) -> some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("📣")
                    .font(.system(size: 20))
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text("Ребёнок сообщил:")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    Text(request.achievement)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    Text(request.dateString)
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                }
                Spacer()
            }
            
            HStack(spacing: Spacing.s) {
                Button(action: {
                    HapticFeedback.impact(.medium)
                    approveAchievement(request: request, rewardAmount: 15)
                }) {
                    Text("✅ Наградить (+15 🦄)")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.successGreen)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(PlainButtonStyle())
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    rejectAchievement(request: request)
                }) {
                    Text("❌ Отклонить")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.dangerRed)
                        .cornerRadius(CornerRadius.medium)
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.primaryBlue.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.primaryBlue.opacity(0.3), lineWidth: 2)
                )
        )
    }
    
    // MARK: - Helper Methods
    
    /// Загрузка запросов на достижения из AppStorage
    private func loadAchievementRequests() {
        guard let data = UserDefaults.standard.data(forKey: "child_achievement_requests"),
              let decoded = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            achievementRequests = []
            return
        }
        
        achievementRequests = decoded.compactMap { dict in
            guard let id = dict["id"] as? String,
                  let achievement = dict["achievement"] as? String,
                  let timestamp = dict["timestamp"] as? TimeInterval,
                  let status = dict["status"] as? String else {
                return nil
            }
            return AchievementRequest(id: id, achievement: achievement, timestamp: timestamp, status: status)
        }
        
        print("📣 Загружено запросов на достижения: \(achievementRequests.count)")
    }
    
    /// Одобрение достижения и награждение единорогами
    private func approveAchievement(request: AchievementRequest, rewardAmount: Int) {
        // Обновляем баланс в AppStorage (синхронизация с ChildRewardsScreen)
        let currentBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
        let newBalance = currentBalance + rewardAmount
        UserDefaults.standard.set(newBalance, forKey: "child_unicorn_balance")
        
        // Обновляем локальный баланс
        unicornBalance = newBalance
        
        // Обновляем статистику за неделю
        let currentWeekly = UserDefaults.standard.integer(forKey: "child_weekly_earned")
        UserDefaults.standard.set(currentWeekly + rewardAmount, forKey: "child_weekly_earned")
        weeklyRewarded += rewardAmount
        
        // Обновляем статус запроса
        updateAchievementRequestStatus(requestId: request.id, status: "approved")
        
        // Добавляем в историю
        addToHistory(isReward: true, title: "Достижение: \(request.achievement)", reason: "Одобрено достижение ребёнка", amount: rewardAmount)
        
        HapticFeedback.notification(.success)
        print("✅ Достижение одобрено: \(request.achievement), награда: +\(rewardAmount) 🦄")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    /// Отклонение достижения
    private func rejectAchievement(request: AchievementRequest) {
        // Обновляем статус запроса
        updateAchievementRequestStatus(requestId: request.id, status: "rejected")
        
        // Добавляем в историю
        addToHistory(isReward: false, title: "Достижение отклонено", reason: "Отклонено: \(request.achievement)", amount: 0)
        
        HapticFeedback.notification(.warning)
        print("❌ Достижение отклонено: \(request.achievement)")
    }
    
    /// Обновление статуса запроса на достижение
    private func updateAchievementRequestStatus(requestId: String, status: String) {
        guard let data = UserDefaults.standard.data(forKey: "child_achievement_requests"),
              var requests = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] else {
            return
        }
        
        // Находим и обновляем запрос
        for i in 0..<requests.count {
            if requests[i]["id"] as? String == requestId {
                requests[i]["status"] = status
                break
            }
        }
        
        // Сохраняем обратно
        if let encoded = try? JSONSerialization.data(withJSONObject: requests) {
            UserDefaults.standard.set(encoded, forKey: "child_achievement_requests")
            loadAchievementRequests() // Перезагружаем список
        }
    }
    
    private func approveGoal() {
        @AppStorage("child_goal_title") var goalTitle: String = ""
        @AppStorage("child_goal_cost") var goalCost: Int = 0
        
        goalTitle = goalTitlePending
        goalCost = goalCostPending
        goalApprovalPending = false
        
        // Добавляем в историю
        addToHistory(isReward: false, title: "Цель одобрена", reason: "Одобрена цель: \(goalTitlePending)", amount: 0)
        
        goalTitlePending = ""
        goalCostPending = 0
        
        HapticFeedback.notification(.success)
        print("✅ Цель одобрена: \(goalTitle)")
    }
    
    private func rejectGoal() {
        // Добавляем в историю
        addToHistory(isReward: false, title: "Цель отклонена", reason: "Отклонена цель: \(goalTitlePending)", amount: 0)
        
        goalTitlePending = ""
        goalCostPending = 0
        goalApprovalPending = false
        
        HapticFeedback.impact(.medium)
        print("❌ Цель отклонена")
    }
    
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
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")
        return formatter.string(from: date)
    }
    
    // MARK: - Actions
    
    private func rewardChild(amount: Int, reason: String) {
        // ✅ БЕЗОПАСНОСТЬ: Только родители могут награждать
        guard isUserParent else {
            print("⚠️ ПРОБЛЕМА БЕЗОПАСНОСТИ: Попытка наградить ребёнка не родителем!")
            HapticFeedback.notification(.error)
            return
        }
        let finalReason = reason.isEmpty ? "Вознаграждение родителем" : reason
        
        // Определяем иконку по причине (используется косвенно через getRewardIcon)
        let _ = getRewardIcon(for: reason)
        let title = reason.isEmpty ? "Вознаграждение" : reason
        
        addToHistory(isReward: true, title: title, reason: finalReason, amount: amount)
        
        // Обновляем баланс в AppStorage (синхронизация с ChildRewardsScreen)
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
        weeklyRewarded += amount
        
        HapticFeedback.notification(.success)
        print("✅ Вознаградили ребёнка: +\(amount) 🦄, причина: \(finalReason)")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    private func punishChild(amount: Int, reason: String) {
        // ✅ БЕЗОПАСНОСТЬ: Только родители могут наказывать
        guard isUserParent else {
            print("⚠️ ПРОБЛЕМА БЕЗОПАСНОСТИ: Попытка наказать ребёнка не родителем!")
            HapticFeedback.notification(.error)
            return
        }
        let finalReason = reason.isEmpty ? "Наказание родителем" : reason
        
        // Определяем иконку по причине (используется косвенно через getPunishmentIcon)
        let _ = getPunishmentIcon(for: reason)
        let title = reason.isEmpty ? "Наказание" : reason
        
        addToHistory(isReward: false, title: title, reason: finalReason, amount: amount)
        
        // Обновляем баланс в AppStorage (синхронизация с ChildRewardsScreen)
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
        
        HapticFeedback.notification(.warning)
        print("❌ Наказали ребёнка: -\(amount) 🦄, причина: \(finalReason)")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    /// Определение иконки для награды
    private func getRewardIcon(for reason: String) -> String {
        let lowercased = reason.lowercased()
        if lowercased.contains("домашнее задание") || lowercased.contains("дз") {
            return "📚"
        } else if lowercased.contains("убрал") || lowercased.contains("уборк") {
            return "🧹"
        } else if lowercased.contains("поведение") || lowercased.contains("хорош") {
            return "😊"
        } else if lowercased.contains("книг") || lowercased.contains("читал") {
            return "📖"
        } else if lowercased.contains("5") || lowercased.contains("оценк") || lowercased.contains("четверт") {
            return "🏆"
        }
        return "✅"
    }
    
    /// Определение иконки для наказания
    private func getPunishmentIcon(for reason: String) -> String {
        let lowercased = reason.lowercased()
        if lowercased.contains("домашнее задание") || lowercased.contains("дз") {
            return "📚"
        } else if lowercased.contains("поведение") || lowercased.contains("грубост") || lowercased.contains("ссор") {
            return "😡"
        } else if lowercased.contains("лимит") || lowercased.contains("врем") || lowercased.contains("экран") {
            return "⏰"
        } else if lowercased.contains("обход") || lowercased.contains("блокировк") {
            return "🚫"
        }
        return "❌"
    }
    
    // MARK: - Shop Rewards Management
    
    private func loadShopRewards() {
        if shopRewardsData.isEmpty {
            // Первый запуск - используем дефолтные награды
            shopRewards = ShopReward.defaultRewards
            saveShopRewards()
        } else {
            // Загружаем из UserDefaults
            if let data = shopRewardsData.data(using: .utf8),
               let rewards = try? JSONDecoder().decode([ShopReward].self, from: data) {
                shopRewards = rewards
            } else {
                // Ошибка декодирования - используем дефолтные
                shopRewards = ShopReward.defaultRewards
                saveShopRewards()
            }
        }
    }
    
    private func saveShopRewards() {
        if let data = try? JSONEncoder().encode(shopRewards),
           let jsonString = String(data: data, encoding: .utf8) {
            shopRewardsData = jsonString
            // Отправляем уведомление для обновления ChildRewardsScreen
            NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        }
    }
    
    // MARK: - Earning Ways Management
    
    private func loadEarningWays() {
        if earningWaysData.isEmpty {
            // Первый запуск - используем дефолтные способы заработка
            earningWays = EarningWay.defaultEarningWays
            saveEarningWays()
        } else {
            // Загружаем из UserDefaults
            if let data = earningWaysData.data(using: .utf8),
               let ways = try? JSONDecoder().decode([EarningWay].self, from: data) {
                earningWays = ways
            } else {
                // Ошибка декодирования - используем дефолтные
                earningWays = EarningWay.defaultEarningWays
                saveEarningWays()
            }
        }
    }
    
    private func saveEarningWays() {
        if let data = try? JSONEncoder().encode(earningWays),
           let jsonString = String(data: data, encoding: .utf8) {
            earningWaysData = jsonString
            NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        }
    }
    
    // MARK: - Punishment Reasons Management
    
    private func loadPunishmentReasons() {
        if punishmentReasonsData.isEmpty {
            // Первый запуск - используем дефолтные причины наказания
            punishmentReasons = PunishmentReason.defaultPunishmentReasons
            savePunishmentReasons()
        } else {
            // Загружаем из UserDefaults
            if let data = punishmentReasonsData.data(using: .utf8),
               let reasons = try? JSONDecoder().decode([PunishmentReason].self, from: data) {
                punishmentReasons = reasons
            } else {
                // Ошибка декодирования - используем дефолтные
                punishmentReasons = PunishmentReason.defaultPunishmentReasons
                savePunishmentReasons()
            }
        }
    }
    
    private func savePunishmentReasons() {
        if let data = try? JSONEncoder().encode(punishmentReasons),
           let jsonString = String(data: data, encoding: .utf8) {
            punishmentReasonsData = jsonString
            NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        }
    }
}

// MARK: - Reward/Punish Input Modals

struct RewardInputModal: View {
    @Binding var isPresented: Bool
    @Binding var amount: String
    @Binding var reason: String
    let onConfirm: (Int, String) -> Void
    
    // Используем earningWays из UserDefaults вместо захардкоженных шаблонов
    @AppStorage("earning_ways_list") private var earningWaysData: String = ""
    @State private var earningWays: [EarningWay] = []
    
    @State private var selectedTemplate: String? = nil
    
    // Дефолтные шаблоны (используются только если earningWays пустые)
    private let defaultTemplates = [
        ("📚", "Домашнее задание", "+10"),
        ("🧹", "Домашние обязанности", "+5"),
        ("😊", "Хорошее поведение", "+15"),
        ("📖", "Чтение книг", "+20"),
        ("🏆", "Достижения в учёбе", "+50")
    ]
    
    // Активные способы заработка (только включенные)
    private var activeEarningWays: [EarningWay] {
        earningWays.filter { $0.isEnabled }
    }
    
    // Используем earningWays если они есть, иначе дефолтные шаблоны
    private var templates: [(String, String, String)] {
        if !activeEarningWays.isEmpty {
            return activeEarningWays.map { way in
                (way.icon, way.title, "+\(way.amount)")
            }
        } else {
            return defaultTemplates
        }
    }
    
    private func loadEarningWays() {
        if earningWaysData.isEmpty {
            earningWays = EarningWay.defaultEarningWays
        } else {
            if let data = earningWaysData.data(using: .utf8),
               let ways = try? JSONDecoder().decode([EarningWay].self, from: data) {
                earningWays = ways
            } else {
                earningWays = EarningWay.defaultEarningWays
            }
        }
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        Text("✅ Вознаградить ребёнка")
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                            .padding(.top, Spacing.m)
                        
                        // Шаблоны
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Шаблоны:")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            VStack(spacing: Spacing.s) {
                                ForEach(Array(templates.enumerated()), id: \.offset) { index, template in
                                    Button(action: {
                                        selectedTemplate = template.1
                                        reason = template.1
                                        amount = template.2.replacingOccurrences(of: "+", with: "")
                                    }) {
                                        HStack {
                                            Text(template.0)
                                                .font(.system(size: 24))
                                            VStack(alignment: .leading, spacing: Spacing.xxs) {
                                                Text(template.1)
                                                    .font(.body)
                                                    .foregroundColor(.textPrimary)
                                                // Показываем описание из earningWay, если есть
                                                if !activeEarningWays.isEmpty && index < activeEarningWays.count {
                                                    Text(activeEarningWays[index].subtitle)
                                                        .font(.caption)
                                                        .foregroundColor(.textSecondary)
                                                }
                                            }
                                            Spacer()
                                            Text(template.2)
                                                .font(.bodyBold)
                                                .foregroundColor(.successGreen)
                                        }
                                        .padding(Spacing.m)
                                        .background(
                                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                                .fill(selectedTemplate == template.1 ? Color.successGreen.opacity(0.2) : Color.backgroundMedium.opacity(0.5))
                                        )
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                }
                            }
                            .padding(.horizontal, Spacing.screenPadding)
                            .onAppear {
                                loadEarningWays()
                            }
                        }
                        
                        // Своя причина
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Своя причина:")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            TextField("Например: Помог бабушке", text: $reason)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .fill(Color.backgroundMedium.opacity(0.5))
                                )
                                .foregroundColor(.textPrimary)
                                .padding(.horizontal, Spacing.screenPadding)
                                .onChange(of: reason) { _ in
                                    if !reason.isEmpty {
                                        selectedTemplate = nil
                                    }
                                }
                        }
                        
                        // Сумма
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Сумма награды (🦄):")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            TextField("10", text: $amount)
                                .keyboardType(.numberPad)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .fill(Color.backgroundMedium.opacity(0.5))
                                )
                                .foregroundColor(.textPrimary)
                                .padding(.horizontal, Spacing.screenPadding)
                        }
                        
                        // Кнопка подтверждения
                        Button(action: {
                            let amountInt = Int(amount) ?? 10
                            onConfirm(amountInt, reason)
                            isPresented = false
                        }) {
                            Text("✅ Подтвердить")
                                .font(.bodyBold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.successGreen)
                                .cornerRadius(CornerRadius.large)
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.top, Spacing.m)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("✅ Вознаградить")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

struct PunishInputModal: View {
    @Binding var isPresented: Bool
    @Binding var amount: String
    @Binding var reason: String
    let onConfirm: (Int, String) -> Void
    
    // Используем punishmentReasons из UserDefaults вместо захардкоженных шаблонов
    @AppStorage("punishment_reasons_list") private var punishmentReasonsData: String = ""
    @State private var punishmentReasons: [PunishmentReason] = []
    
    @State private var selectedTemplate: String? = nil
    
    // Дефолтные шаблоны (используются только если punishmentReasons пустые)
    private let defaultTemplates = [
        ("📚", "Не сделал ДЗ", "-10"),
        ("😡", "Плохое поведение", "-15"),
        ("⏰", "Нарушение лимитов", "-5"),
        ("🚫", "Обход блокировок", "-20"),
        ("😤", "Грубость с бабушкой", "-15")
    ]
    
    // Активные причины наказания (только включенные)
    private var activePunishmentReasons: [PunishmentReason] {
        punishmentReasons.filter { $0.isEnabled }
    }
    
    // Используем punishmentReasons если они есть, иначе дефолтные шаблоны
    private var templates: [(String, String, String)] {
        if !activePunishmentReasons.isEmpty {
            return activePunishmentReasons.map { reason in
                (reason.icon, reason.title, "-\(reason.amount)")
            }
        } else {
            return defaultTemplates
        }
    }
    
    private func loadPunishmentReasons() {
        if punishmentReasonsData.isEmpty {
            punishmentReasons = PunishmentReason.defaultPunishmentReasons
        } else {
            if let data = punishmentReasonsData.data(using: .utf8),
               let reasons = try? JSONDecoder().decode([PunishmentReason].self, from: data) {
                punishmentReasons = reasons
            } else {
                punishmentReasons = PunishmentReason.defaultPunishmentReasons
            }
        }
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        Text("❌ Наказать ребёнка")
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                            .padding(.top, Spacing.m)
                        
                        // Шаблоны
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Шаблоны:")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            VStack(spacing: Spacing.s) {
                                ForEach(Array(templates.enumerated()), id: \.offset) { index, template in
                                    Button(action: {
                                        selectedTemplate = template.1
                                        reason = template.1
                                        amount = template.2.replacingOccurrences(of: "-", with: "")
                                    }) {
                                        HStack {
                                            Text(template.0)
                                                .font(.system(size: 24))
                                            VStack(alignment: .leading, spacing: Spacing.xxs) {
                                                Text(template.1)
                                                    .font(.body)
                                                    .foregroundColor(.textPrimary)
                                                // Показываем описание из punishmentReason, если есть
                                                if !activePunishmentReasons.isEmpty && index < activePunishmentReasons.count {
                                                    Text(activePunishmentReasons[index].subtitle)
                                                        .font(.caption)
                                                        .foregroundColor(.textSecondary)
                                                }
                                            }
                                            Spacer()
                                            Text(template.2)
                                                .font(.bodyBold)
                                                .foregroundColor(.dangerRed)
                                        }
                                        .padding(Spacing.m)
                                        .background(
                                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                                .fill(selectedTemplate == template.1 ? Color.dangerRed.opacity(0.2) : Color.backgroundMedium.opacity(0.5))
                                        )
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                }
                            }
                            .padding(.horizontal, Spacing.screenPadding)
                            .onAppear {
                                loadPunishmentReasons()
                            }
                        }
                        
                        // Своя причина
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Своя причина:")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            TextField("Например: Не слушался", text: $reason)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .fill(Color.backgroundMedium.opacity(0.5))
                                )
                                .foregroundColor(.textPrimary)
                                .padding(.horizontal, Spacing.screenPadding)
                                .onChange(of: reason) { _ in
                                    if !reason.isEmpty {
                                        selectedTemplate = nil
                                    }
                                }
                        }
                        
                        // Сумма
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Сумма наказания (🦄):")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            TextField("10", text: $amount)
                                .keyboardType(.numberPad)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .fill(Color.backgroundMedium.opacity(0.5))
                                )
                                .foregroundColor(.textPrimary)
                                .padding(.horizontal, Spacing.screenPadding)
                        }
                        
                        // Кнопка подтверждения
                        Button(action: {
                            let amountInt = Int(amount) ?? 10
                            onConfirm(amountInt, reason)
                            isPresented = false
                        }) {
                            Text("❌ Подтвердить")
                                .font(.bodyBold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.dangerRed)
                                .cornerRadius(CornerRadius.large)
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.top, Spacing.m)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text("❌ Наказать")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

// MARK: - Reward Operation Model
// RewardOperation is defined in Shared/Models/RewardModels.swift

// MARK: - Shop Management Modal

struct ShopManagementModal: View {
    @Binding var rewards: [ShopReward]
    let onSave: () -> Void
    
    @Environment(\.presentationMode) var presentationMode
    @State private var editingReward: ShopReward?
    @State private var showAddReward: Bool = false
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Инструкция
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            HStack {
                                Image(systemName: "info.circle.fill")
                                    .foregroundColor(.secondaryGold)
                                Text("Редактирование наград")
                                    .font(.body)
                                    .fontWeight(.semibold)
                            }
                            Text("Здесь вы можете управлять наградами в магазине. Дети видят только активные награды (Toggle включен).")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        .padding(.horizontal, Spacing.screenPadding)
                        .padding(.top, Spacing.m)
                        
                        // Список существующих наград
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text("Награды в магазине (\(rewards.count)):")
                                .font(.body)
                                .fontWeight(.semibold)
                                .foregroundColor(.textPrimary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            ForEach($rewards) { $reward in
                                rewardEditRow(reward: $reward)
                            }
                        }
                        
                        // Кнопка добавить новую награду
                        Button(action: {
                            print("🔍 DEBUG: Добавление новой награды")
                            showAddReward = true
                        }) {
                            HStack {
                                Image(systemName: "plus.circle.fill")
                                    .font(.system(size: 24))
                                    .foregroundColor(.successGreen)
                                Text("Добавить новую награду")
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.large)
                                    .fill(Color.successGreen.opacity(0.1))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: CornerRadius.large)
                                            .stroke(Color.successGreen.opacity(0.3), lineWidth: 1)
                                    )
                            )
                        }
                        .padding(.horizontal, Spacing.screenPadding)
                    }
                }
            }
            .navigationTitle("Управление магазином")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Сохранить") {
                        onSave()
                    }
                }
            }
            .sheet(isPresented: $showAddReward) {
                AddRewardModal(
                    onAdd: { newReward in
                        rewards.append(newReward)
                        showAddReward = false
                    },
                    onCancel: {
                        showAddReward = false
                    }
                )
            }
            .sheet(item: $editingReward) { reward in
                EditRewardModal(
                    reward: reward,
                    onSave: { updatedReward in
                        if let index = rewards.firstIndex(where: { $0.id == updatedReward.id }) {
                            rewards[index] = updatedReward
                        }
                        editingReward = nil
                    },
                    onCancel: {
                        editingReward = nil
                    }
                )
            }
        }
    }
    
    private func rewardEditRow(reward: Binding<ShopReward>) -> some View {
        VStack(spacing: Spacing.m) {
            HStack(spacing: Spacing.m) {
                Text(reward.icon.wrappedValue)
                    .font(.system(size: 40))
                    .frame(width: 50)
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(reward.title.wrappedValue)
                            .font(.body)
                            .fontWeight(.semibold)
                            .foregroundColor(.textPrimary)
                        
                        // Индикатор активности
                        if reward.isEnabled.wrappedValue {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.caption)
                                .foregroundColor(.successGreen)
                        } else {
                            Image(systemName: "xmark.circle.fill")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    
                    Text(reward.desc.wrappedValue)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    HStack(spacing: Spacing.xs) {
                        Text("Цена:")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        TextField("", value: reward.price, format: .number)
                            .textFieldStyle(.plain)
                            .keyboardType(.numberPad)
                            .frame(width: 70)
                            .padding(.horizontal, Spacing.s)
                            .padding(.vertical, Spacing.xs)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(reward.isEnabled.wrappedValue ? Color.successGreen.opacity(0.1) : Color.backgroundMedium.opacity(0.5))
                            )
                            .foregroundColor(.textPrimary)
                        Text("🦄")
                            .font(.caption)
                    }
                }
                
                Spacer()
                
                VStack(spacing: Spacing.m) {
                    // Toggle с подписью
                    VStack(spacing: Spacing.xxs) {
                        Toggle("", isOn: reward.isEnabled)
                            .labelsHidden()
                            .scaleEffect(0.9)
                        Text(reward.isEnabled.wrappedValue ? "Вкл" : "Выкл")
                            .font(.captionSmall)
                            .foregroundColor(reward.isEnabled.wrappedValue ? .successGreen : .textSecondary)
                    }
                    
                    // Кнопка редактирования
                    Button(action: {
                        print("🔍 DEBUG: Редактирование награды: \(reward.title.wrappedValue)")
                        editingReward = reward.wrappedValue
                    }) {
                        Image(systemName: "pencil.circle.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.secondaryGold)
                            .background(Color.white)
                            .clipShape(Circle())
                    }
                }
            }
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(reward.isEnabled.wrappedValue ? Color.successGreen.opacity(0.05) : Color.backgroundMedium.opacity(0.3))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(
                            reward.isEnabled.wrappedValue ? Color.successGreen.opacity(0.3) : Color.textSecondary.opacity(0.2),
                            lineWidth: 1
                        )
                )
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Add Reward Modal

struct AddRewardModal: View {
    let onAdd: (ShopReward) -> Void
    let onCancel: () -> Void
    
    @Environment(\.presentationMode) var presentationMode
    @State private var icon: String = "🎁"
    @State private var title: String = ""
    @State private var desc: String = ""
    @State private var price: Int = 100
    
    let availableIcons = ["🎮", "📱", "🌙", "🍕", "🎬", "🎁", "🎂", "🍦", "🎨", "📚", "⚽", "🎸"]
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Выбор иконки
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text("Выберите иконку:")
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 6), spacing: Spacing.m) {
                                ForEach(availableIcons, id: \.self) { iconEmoji in
                                    Button(action: {
                                        icon = iconEmoji
                                    }) {
                                        Text(iconEmoji)
                                            .font(.system(size: 32))
                                            .frame(width: 50, height: 50)
                                            .background(icon == iconEmoji ? Color.secondaryGold.opacity(0.3) : Color.backgroundMedium.opacity(0.5))
                                            .clipShape(RoundedRectangle(cornerRadius: 10))
                                    }
                                }
                            }
                        }
                        
                        // Название
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text("Название награды:")
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField("Например: +1 час игр", text: $title)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }
                        
                        // Описание
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text("Описание:")
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField("Краткое описание", text: $desc)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }
                        
                        // Цена
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text("Цена (единороги):")
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField("", value: $price, format: .number)
                                .textFieldStyle(.plain)
                                .keyboardType(.numberPad)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }
                        
                        Button(action: {
                            guard !title.isEmpty else { return }
                            let newReward = ShopReward(icon: icon, title: title, desc: desc.isEmpty ? "Новая награда" : desc, price: price)
                            onAdd(newReward)
                        }) {
                            Text("Добавить награду")
                                .font(.bodyBold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(title.isEmpty ? Color.textSecondary : Color.successGreen)
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
                        }
                        .disabled(title.isEmpty)
                    }
                    .padding(Spacing.l)
                }
            }
            .navigationTitle("Новая награда")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Отмена") {
                        onCancel()
                    }
                }
            }
        }
    }
}

// MARK: - Edit Reward Modal

struct EditRewardModal: View {
    let reward: ShopReward
    let onSave: (ShopReward) -> Void
    let onCancel: () -> Void
    
    @Environment(\.presentationMode) var presentationMode
    @State private var icon: String
    @State private var title: String
    @State private var desc: String
    @State private var price: Int
    
    let availableIcons = ["🎮", "📱", "🌙", "🍕", "🎬", "🎁", "🎂", "🍦", "🎨", "📚", "⚽", "🎸"]
    
    init(reward: ShopReward, onSave: @escaping (ShopReward) -> Void, onCancel: @escaping () -> Void) {
        self.reward = reward
        self.onSave = onSave
        self.onCancel = onCancel
        _icon = State(initialValue: reward.icon)
        _title = State(initialValue: reward.title)
        _desc = State(initialValue: reward.desc)
        _price = State(initialValue: reward.price)
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Выбор иконки
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text("Выберите иконку:")
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 6), spacing: Spacing.m) {
                                ForEach(availableIcons, id: \.self) { iconEmoji in
                                    Button(action: {
                                        icon = iconEmoji
                                    }) {
                                        Text(iconEmoji)
                                            .font(.system(size: 32))
                                            .frame(width: 50, height: 50)
                                            .background(icon == iconEmoji ? Color.secondaryGold.opacity(0.3) : Color.backgroundMedium.opacity(0.5))
                                            .clipShape(RoundedRectangle(cornerRadius: 10))
                                    }
                                }
                            }
                        }
                        
                        // Название
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text("Название награды:")
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField("", text: $title)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }
                        
                        // Описание
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text("Описание:")
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField("", text: $desc)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }
                        
                        // Цена
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text("Цена (единороги):")
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField("", value: $price, format: .number)
                                .textFieldStyle(.plain)
                                .keyboardType(.numberPad)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }
                        
                        Button(action: {
                            let updatedReward = ShopReward(id: reward.id, icon: icon, title: title, desc: desc, price: price, isEnabled: reward.isEnabled)
                            onSave(updatedReward)
                        }) {
                            Text("Сохранить изменения")
                                .font(.bodyBold)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(title.isEmpty ? Color.textSecondary : Color.successGreen)
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
                        }
                        .disabled(title.isEmpty)
                    }
                    .padding(Spacing.l)
                }
            }
            .navigationTitle("Редактировать награду")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Отмена") {
                        onCancel()
                    }
                }
            }
        }
    }
}

// MARK: - Add/Edit Earning Way Modals

struct AddEarningWayModal: View {
    @Binding var isPresented: Bool
    let onAdd: (EarningWay) -> Void
    
    @State private var icon: String = "📚"
    @State private var title: String = ""
    @State private var subtitle: String = ""
    @State private var amount: Int = 10
    
    var body: some View {
        NavigationView {
            Form {
                Section("Иконка") {
                    TextField("📚", text: $icon)
                }
                Section("Название") {
                    TextField("Домашнее задание", text: $title)
                }
                Section("Описание") {
                    TextField("+10 единорогов за задание", text: $subtitle)
                }
                Section("Награда (единороги)") {
                    Stepper("\(amount) 🦄", value: $amount, in: 1...1000)
                }
            }
            .navigationTitle("Добавить способ заработка")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Добавить") {
                        let newWay = EarningWay(icon: icon, title: title, subtitle: subtitle, amount: amount)
                        onAdd(newWay)
                    }
                    .disabled(title.isEmpty || subtitle.isEmpty)
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

struct EditEarningWayModal: View {
    @Binding var isPresented: Bool
    @Binding var earningWay: EarningWay
    let onSave: () -> Void
    let onDelete: () -> Void
    
    @State private var icon: String = ""
    @State private var title: String = ""
    @State private var subtitle: String = ""
    @State private var amount: Int = 0
    @State private var isEnabled: Bool = true
    
    var body: some View {
        NavigationView {
            Form {
                Section("Иконка") {
                    TextField("📚", text: $icon)
                }
                Section("Название") {
                    TextField("Домашнее задание", text: $title)
                }
                Section("Описание") {
                    TextField("+10 единорогов за задание", text: $subtitle)
                }
                Section("Награда (единороги)") {
                    Stepper("\(amount) 🦄", value: $amount, in: 1...1000)
                }
                Section("Статус") {
                    Toggle("Включено", isOn: $isEnabled)
                }
            }
            .navigationTitle("Редактировать")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Сохранить") {
                        earningWay.icon = icon
                        earningWay.title = title
                        earningWay.subtitle = subtitle
                        earningWay.amount = amount
                        earningWay.isEnabled = isEnabled
                        onSave()
                    }
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Удалить") {
                        onDelete()
                    }
                    .foregroundColor(.dangerRed)
                }
            }
            .onAppear {
                icon = earningWay.icon
                title = earningWay.title
                subtitle = earningWay.subtitle
                amount = earningWay.amount
                isEnabled = earningWay.isEnabled
            }
        }
    }
}

// MARK: - Add/Edit Punishment Reason Modals

struct AddPunishmentReasonModal: View {
    @Binding var isPresented: Bool
    let onAdd: (PunishmentReason) -> Void
    
    @State private var icon: String = "📚"
    @State private var title: String = ""
    @State private var subtitle: String = ""
    @State private var amount: Int = 10
    
    var body: some View {
        NavigationView {
            Form {
                Section("Иконка") {
                    TextField("📚", text: $icon)
                }
                Section("Название") {
                    TextField("Не сделал домашнее задание", text: $title)
                }
                Section("Описание") {
                    TextField("Забыл или отказался делать", text: $subtitle)
                }
                Section("Штраф (единороги)") {
                    Stepper("\(amount) 🦄", value: $amount, in: 1...100)
                }
            }
            .navigationTitle("Добавить причину наказания")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Добавить") {
                        let newReason = PunishmentReason(icon: icon, title: title, subtitle: subtitle, amount: amount)
                        onAdd(newReason)
                    }
                    .disabled(title.isEmpty || subtitle.isEmpty)
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

struct EditPunishmentReasonModal: View {
    @Binding var isPresented: Bool
    @Binding var punishmentReason: PunishmentReason
    let onSave: () -> Void
    let onDelete: () -> Void
    
    @State private var icon: String = ""
    @State private var title: String = ""
    @State private var subtitle: String = ""
    @State private var amount: Int = 0
    @State private var isEnabled: Bool = true
    
    var body: some View {
        NavigationView {
            Form {
                Section("Иконка") {
                    TextField("📚", text: $icon)
                }
                Section("Название") {
                    TextField("Не сделал домашнее задание", text: $title)
                }
                Section("Описание") {
                    TextField("Забыл или отказался делать", text: $subtitle)
                }
                Section("Штраф (единороги)") {
                    Stepper("\(amount) 🦄", value: $amount, in: 1...100)
                }
                Section("Статус") {
                    Toggle("Включено", isOn: $isEnabled)
                }
            }
            .navigationTitle("Редактировать")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Сохранить") {
                        punishmentReason.icon = icon
                        punishmentReason.title = title
                        punishmentReason.subtitle = subtitle
                        punishmentReason.amount = amount
                        punishmentReason.isEnabled = isEnabled
                        onSave()
                    }
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Удалить") {
                        onDelete()
                    }
                    .foregroundColor(.dangerRed)
                }
            }
            .onAppear {
                icon = punishmentReason.icon
                title = punishmentReason.title
                subtitle = punishmentReason.subtitle
                amount = punishmentReason.amount
                isEnabled = punishmentReason.isEnabled
            }
        }
    }
}

// MARK: - Preview

#if DEBUG
struct RewardsModalView_Previews: PreviewProvider {
    static var previews: some View {
        RewardsModalView(
            unicornBalance: .constant(245),
            weeklyRewarded: .constant(128),
            weeklyPunished: .constant(45)
        )
    }
}
#endif



