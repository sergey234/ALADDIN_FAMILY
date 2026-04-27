import SwiftUI

/// 🦄 Rewards Modal View
/// Модальное окно управления вознаграждениями ребёнка (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ!)
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
@available(iOS 14.0, *)
struct RewardsModalView: View {
    
    // MARK: - Properties
    
    @Environment(\.presentationMode) var presentationMode
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var unicornBalance: Int
    @Binding var weeklyRewarded: Int
    @Binding var weeklyPunished: Int
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    
    // Альтернативный способ закрытия (совместимо с iOS 14+)
    private func dismiss() {
        presentationMode.wrappedValue.dismiss()
    }
    
    // Проверка роли пользователя (ТОЛЬКО РОДИТЕЛИ могут видеть кнопки)
    private var isUserParent: Bool {
        guard let roleString = UserDefaults.standard.string(forKey: "current_user_role"),
              let role = FamilyRole(storageValue: roleString) else {
            return false
        }
        return role == .parent
    }

    private var rewardsScopeChildId: String? {
        let trimmed = selectedChildId.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty { return trimmed }
        return UnicornRewardsStore.resolveActiveChildId()
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
    
    @State private var showParentAuthDeniedAlert: Bool = false
    
    /// Чувствительные действия в модалке наград — только после подтверждения родителя (биометрия / PIN-сессия).
    private func runWithParentConfirmation(_ action: @escaping @MainActor () -> Void) {
        Task { @MainActor in
            let ok = await ParentSessionGate.confirmSensitiveAction(forceReauth: true)
            if ok {
                action()
            } else {
                showParentAuthDeniedAlert = true
            }
        }
    }
    
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
            .id("rewards_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        .task {
            print("🚨 RewardsModalView загружен!")
            loadAchievementRequests()
        }
        .onAppear {
            RewardLocalizationMigration.performIfNeeded()
            loadAchievementRequests()
            loadShopRewards()
            loadEarningWays()
            loadPunishmentReasons()
            // Синхронизация баланса из UserDefaults с @Binding
            let currentBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
            let currentEarned = UnicornRewardsStore.readWeeklyEarned(for: rewardsScopeChildId)
            let currentPunished = UnicornRewardsStore.readWeeklyPunished(for: rewardsScopeChildId)
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
                onConfirm: { amount, texts in
                    rewardChild(amount: amount, history: texts)
                }
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showPunishInput) {
            PunishInputModal(
                isPresented: $showPunishInput,
                amount: $punishAmount,
                reason: $punishReason,
                onConfirm: { amount, texts in
                    punishChild(amount: amount, history: texts)
                }
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showShopManagement) {
            ShopManagementModal(
                rewards: $shopRewards,
                onSave: {
                    saveShopRewards()
                    showShopManagement = false
                }
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showGamesSettings) {
            GamesParentalControlView()
                .environmentObject(NavigationManager())
                .environmentObject(localizationManager)
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
            .environmentObject(localizationManager)
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
                .environmentObject(localizationManager)
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
            .environmentObject(localizationManager)
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
                .environmentObject(localizationManager)
            }
        }
        .toolbar {
                // ⚙️ Кнопка настроек игр (СЛЕВА) - ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ
                ToolbarItem(placement: .navigationBarLeading) {
                    if isUserParent {
                        Button(action: {
                            HapticFeedback.impact(.light)
                            print("🔍 DEBUG: Открываем настройки игр")
                            runWithParentConfirmation {
                                showGamesSettings = true
                            }
                        }) {
                            Image(systemName: "gearshape.fill")
                                .font(.system(size: 20))
                                .foregroundColor(.secondaryGold)
                        }
                        .accessibilityLabel(localizationManager.localized("rewards_modal_games_settings_label"))
                        .accessibilityHint(localizationManager.localized("rewards_modal_games_settings_hint"))
                    }
                }
                
                // Заголовок по центру
                ToolbarItem(placement: .principal) {
                    HStack(spacing: Spacing.xs) {
                        Text("🦄")
                            .font(.system(size: 20))
                            .accessibilityLabel(localizationManager.localized("child_rewards_balance_label"))
                        Text(localizationManager.localized("child_rewards_title"))
                            .font(.h3)
                            .foregroundColor(Color(hex: "C084FC"))
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(localizationManager.localized("child_rewards_title"))
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
        .alert(isPresented: $showParentAuthDeniedAlert) {
            SwiftUI.Alert(
                title: Text(localizationManager.localized("games_parental_auth_alert_title")),
                message: Text(localizationManager.localized("child_rewards_parent_auth_required")),
                dismissButton: .default(Text(localizationManager.localized("common_ok")))
            )
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
            
            Text(localizationManager.localized("rewards_modal_balance_label"))
                .font(.caption)
                .foregroundColor(.textSecondary)
                .accessibilityLabel(localizationManager.localized("rewards_modal_balance_label"))
            
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
                    Text(localizationManager.localized("rewards_modal_earned_week"))
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel(String(format: localizationManager.localized("rewards_modal_earned_week"), weeklyRewarded))
                
                VStack(spacing: Spacing.xs) {
                    Text("-\(weeklyPunished)")
                        .font(.h2)
                        .foregroundColor(.dangerRed)
                    Text(localizationManager.localized("rewards_modal_punished_week"))
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel(String(format: localizationManager.localized("rewards_modal_punished_week"), weeklyPunished))
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
            title: localizationManager.localized("rewards_modal_shop_management_title"),
            subtitle: String(format: localizationManager.localized("rewards_modal_shop_management_subtitle"), shopRewards.filter { $0.isEnabled }.count, shopRewards.count),
            isExpanded: $isShopManagementExpanded
        ) {
            VStack(spacing: Spacing.m) {
                // Кнопка "Настроить" (открывает полный модал)
                Button(action: {
                    print("🔍 DEBUG: Открываем управление магазином наград")
                    runWithParentConfirmation {
                        showShopManagement = true
                    }
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "gearshape.fill")
                            .font(.system(size: 16))
                        Text(localizationManager.localized("rewards_modal_configure_shop"))
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
                        Text(localizationManager.localized("rewards_modal_all_rewards"))
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
                        Text(localizationManager.localized("rewards_modal_available_rewards"))
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
        let localizedTitle = reward.wrappedValue.localizedTitle(localizationManager)
        let localizedDesc = reward.wrappedValue.localizedDescription(localizationManager)
        return VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text(reward.icon.wrappedValue)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizedTitle)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizedDesc)
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
                    Text(reward.isEnabled.wrappedValue ? localizationManager.localized("rewards_modal_enabled") : localizationManager.localized("rewards_modal_disabled"))
                        .font(.captionSmall)
                        .foregroundColor(reward.isEnabled.wrappedValue ? .successGreen : .textSecondary)
                }
                
                Spacer()
                
                // Кнопка редактирования открывает модал через showShopManagement
                Button(action: {
                    runWithParentConfirmation {
                        showShopManagement = true
                    }
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "pencil.circle.fill")
                            .font(.caption)
                        Text(localizationManager.localized("rewards_modal_edit"))
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
            title: localizationManager.localized("rewards_modal_games_management_title"),
            subtitle: String(format: localizationManager.localized("rewards_modal_games_management_subtitle"), 4),
            isExpanded: $isGamesManagementExpanded
        ) {
            VStack(spacing: Spacing.m) {
                // Кнопка "Настроить игры" (открывает полный модал)
                Button(action: {
                    print("🔍 DEBUG: Открываем настройки игр из секции")
                    runWithParentConfirmation {
                        showGamesSettings = true
                    }
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "gearshape.fill")
                            .font(.system(size: 16))
                        Text(localizationManager.localized("rewards_modal_configure_games"))
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
                    Text(localizationManager.localized("games_list_all_title"))
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    // 🛡️ Юный защитник
                    gameDetailCard(
                        icon: "🛡️",
                        title: localizationManager.localized("games_young_defender_title"),
                        description: localizationManager.localized("games_young_defender_short_description"),
                        isEnabled: gamesSettingsManager.youngDefenderEnabled,
                        parameters: [
                            (localizationManager.localized("games_young_defender_reward_lesson"), gamesSettingsManager.lessonReward),
                            (localizationManager.localized("games_young_defender_bonus_5"), gamesSettingsManager.bonus5Lessons),
                            (localizationManager.localized("games_young_defender_bonus_6"), gamesSettingsManager.bonusAll6)
                        ]
                    )
                    
                    // 🦄 Мой питомец (всегда вкл)
                    gameDetailCard(
                        icon: "🦄",
                        title: localizationManager.localized("games_pet_title"),
                        description: localizationManager.localized("games_pet_short_description"),
                        isEnabled: true,
                        isLocked: true,
                        parameters: [
                            (localizationManager.localized("games_pet_feed"), gamesSettingsManager.petFeedCost),
                            (localizationManager.localized("games_pet_play"), gamesSettingsManager.petPlayCost),
                            (localizationManager.localized("games_pet_pet"), gamesSettingsManager.petPetCost)
                        ]
                    )
                    
                    // 🕵️ Я защитник
                    gameDetailCard(
                        icon: "🕵️",
                        title: localizationManager.localized("games_protector_title"),
                        description: localizationManager.localized("games_protector_short_description"),
                        isEnabled: gamesSettingsManager.protectorEnabled,
                        parameters: [
                            (localizationManager.localized("games_protector_phishing"), gamesSettingsManager.phishingReward),
                            (localizationManager.localized("games_protector_device"), gamesSettingsManager.deviceReward)
                        ]
                    )
                    
                    // 🏆 Турнир семьи
                    gameDetailCard(
                        icon: "🏆",
                        title: localizationManager.localized("games_tournament_title"),
                        description: localizationManager.localized("games_tournament_short_description"),
                        isEnabled: gamesSettingsManager.tournamentEnabled,
                        parameters: [
                            (localizationManager.localized("games_tournament_first_place"), gamesSettingsManager.firstPlaceReward),
                            (localizationManager.localized("games_tournament_second_place"), gamesSettingsManager.secondPlaceReward),
                            (localizationManager.localized("games_tournament_third_place"), gamesSettingsManager.thirdPlaceReward)
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
                            Text(localizationManager.localized("games_pet_always_on"))
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
                            Text(isEnabled ? localizationManager.localized("parental_toggle_on") : localizationManager.localized("parental_toggle_off"))
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
        let title = reward.localizedTitle(localizationManager)
        return VStack(spacing: Spacing.xs) {
            Text(reward.icon)
                .font(.system(size: 32))
            
            Text(title)
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
                Text(localizationManager.localized("rewards_modal_parenting_title"))
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
                    runWithParentConfirmation {
                        showRewardInput = true
                        print("🔍 DEBUG: showRewardInput после = \(showRewardInput)")
                    }
                }) {
                    VStack(spacing: Spacing.xs) {
                        Text("✅")
                            .font(.system(size: 36))  // УВЕЛИЧЕНО с 32
                            .accessibilityLabel("Галочка")
                        Text(localizationManager.localized("rewards_modal_reward_button"))
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
                .accessibilityLabel(localizationManager.localized("rewards_modal_reward_accessibility"))
                .accessibilityHint(localizationManager.localized("rewards_modal_reward_hint"))
                
                // Кнопка "Наказать"
                Button(action: {
                    print("🔍 DEBUG: Нажата кнопка 'Наказать'")
                    print("🔍 DEBUG: showPunishInput до = \(showPunishInput)")
                    HapticFeedback.impact(.medium)
                    runWithParentConfirmation {
                        showPunishInput = true
                        print("🔍 DEBUG: showPunishInput после = \(showPunishInput)")
                    }
                }) {
                    VStack(spacing: Spacing.xs) {
                        Text("❌")
                            .font(.system(size: 36))  // УВЕЛИЧЕНО с 32
                            .accessibilityLabel("Крестик")
                        Text(localizationManager.localized("rewards_modal_punish_button"))
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
                .accessibilityLabel(localizationManager.localized("rewards_modal_punish_accessibility"))
                .accessibilityHint(localizationManager.localized("rewards_modal_punish_hint"))
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
            title: localizationManager.localized("rewards_modal_earning_ways_title"),
            subtitle: String(format: localizationManager.localized("rewards_modal_earning_ways_subtitle"), earningWays.filter { $0.isEnabled }.count),
            isExpanded: $isEarningWaysExpanded
        ) {
            VStack(spacing: Spacing.s) {
                ForEach($earningWays) { $earningWay in
                    if isUserParent {
                        // Для родителей - редактируемая строка
                        earningWayEditableRow(earningWay: $earningWay)
                    } else {
                        // Для детей - только просмотр
                        earningWayRow(earningWay)
                    }
                }
                
                // Кнопка добавления (только для родителей)
                if isUserParent {
                    Button(action: {
                        runWithParentConfirmation {
                            showAddEarningWay = true
                        }
                    }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 18))
                                .foregroundColor(.successGreen)
                            Text(localizationManager.localized("rewards_modal_add_earning_way"))
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
    
    private func earningWayRow(_ earningWay: EarningWay) -> some View {
        let title = earningWay.localizedTitle(localizationManager)
        let subtitle = earningWay.localizedSubtitle(localizationManager)
        let amount = "+\(earningWay.amount) 🦄"
        return HStack(spacing: Spacing.m) {
            Text(earningWay.icon)
                .font(.system(size: 24))
                .accessibilityLabel("Иконка: \(earningWay.icon)")
            
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
        let localizedTitle = earningWay.wrappedValue.localizedTitle(localizationManager)
        let localizedSubtitle = earningWay.wrappedValue.localizedSubtitle(localizationManager)
        return VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text(earningWay.icon.wrappedValue)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizedTitle)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizedSubtitle)
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
                    Text(earningWay.isEnabled.wrappedValue ? localizationManager.localized("rewards_modal_enabled") : localizationManager.localized("rewards_modal_disabled"))
                        .font(.captionSmall)
                        .foregroundColor(earningWay.isEnabled.wrappedValue ? .successGreen : .textSecondary)
                }
                
                // Кнопка редактирования
                Button(action: {
                    runWithParentConfirmation {
                        editingEarningWay = earningWay.wrappedValue
                        showEditEarningWay = true
                    }
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "pencil.circle.fill")
                            .font(.caption)
                        Text(localizationManager.localized("rewards_modal_edit"))
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
            title: localizationManager.localized("rewards_modal_punishment_reasons_title"),
            subtitle: String(format: localizationManager.localized("rewards_modal_punishment_reasons_subtitle"), punishmentReasons.filter { $0.isEnabled }.count),
            isExpanded: $isPunishmentReasonsExpanded
        ) {
            VStack(spacing: Spacing.s) {
                ForEach($punishmentReasons) { $punishmentReason in
                    if isUserParent {
                        punishmentReasonEditableRow(punishmentReason: $punishmentReason)
                    } else {
                        punishmentReasonRow(
                            icon: punishmentReason.icon,
                            title: punishmentReason.localizedTitle(localizationManager),
                            subtitle: punishmentReason.localizedSubtitle(localizationManager),
                            amount: "-\(punishmentReason.amount) 🦄"
                        )
                    }
                }
                
                // Кнопка добавления (только для родителей)
                if isUserParent {
                    Button(action: {
                        runWithParentConfirmation {
                            showAddPunishmentReason = true
                        }
                    }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                                .font(.system(size: 18))
                                .foregroundColor(.dangerRed)
                            Text(localizationManager.localized("rewards_modal_add_punishment_reason"))
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
        return HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 24))
                .accessibilityLabel(localizationManager.localized("child_rewards_punish_field_icon"))
            
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
                .accessibilityLabel(amount)
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .cardShadow()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(subtitle), \(amount)")
    }
    
    /// Редактируемая строка причины наказания (только для родителей)
    private func punishmentReasonEditableRow(punishmentReason: Binding<PunishmentReason>) -> some View {
        let localizedTitle = punishmentReason.wrappedValue.localizedTitle(localizationManager)
        let localizedSubtitle = punishmentReason.wrappedValue.localizedSubtitle(localizationManager)
        return VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text(punishmentReason.icon.wrappedValue)
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizedTitle)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    Text(localizedSubtitle)
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
                    Text(punishmentReason.isEnabled.wrappedValue ? localizationManager.localized("rewards_modal_enabled") : localizationManager.localized("rewards_modal_disabled"))
                        .font(.captionSmall)
                        .foregroundColor(punishmentReason.isEnabled.wrappedValue ? .dangerRed : .textSecondary)
                }
                
                // Кнопка редактирования
                Button(action: {
                    runWithParentConfirmation {
                        editingPunishmentReason = punishmentReason.wrappedValue
                        showEditPunishmentReason = true
                    }
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "pencil.circle.fill")
                            .font(.caption)
                        Text(localizationManager.localized("rewards_modal_edit"))
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
                Text(localizationManager.localized("rewards_modal_goal_request_title"))
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            Text(localizationManager.localized("rewards_modal_goal_request_desc"))
                .font(.caption)
                .foregroundColor(.textSecondary)
            
            HStack {
                Text(goalTitlePending.isEmpty ? localizationManager.localized("rewards_modal_new_game") : goalTitlePending)
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
                    runWithParentConfirmation {
                        approveGoal()
                    }
                }) {
                    Text(localizationManager.localized("rewards_modal_goal_approve"))
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
                    runWithParentConfirmation {
                        rejectGoal()
                    }
                }) {
                    Text(localizationManager.localized("rewards_modal_goal_reject"))
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
            title: localizationManager.localized("rewards_modal_operations_history_title"),
            subtitle: recentOperations.isEmpty ? localizationManager.localized("rewards_modal_empty") : String(format: localizationManager.localized("rewards_modal_operations_history_subtitle"), min(recentOperations.count, 10)),
            isExpanded: $isOperationsHistoryExpanded
        ) {
            Group {
                if recentOperations.isEmpty {
                    // Сообщение, если история пуста
                    VStack(spacing: Spacing.m) {
                        Text("📝")
                            .font(.system(size: 48))
                        Text(localizationManager.localized("rewards_modal_operations_history_empty"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Text(localizationManager.localized("rewards_modal_operations_history_empty_desc"))
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
    
    private func operationHistoryRow(operation: RewardHistoryEntry) -> some View {
        let title = operation.title.resolved(with: localizationManager)
        let reason = operation.reason.resolved(with: localizationManager)
        return HStack(spacing: Spacing.m) {
            Text(operation.isReward ? "✅" : "❌")
                .font(.system(size: 24))
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                if !reason.isEmpty {
                    Text(reason)
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
                Text(localizationManager.localized("rewards_modal_achievement_requests_title"))
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
                    Text(localizationManager.localized("rewards_modal_achievement_child_reported"))
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
                    runWithParentConfirmation {
                        approveAchievement(request: request, rewardAmount: 15)
                    }
                }) {
                    Text(String(format: localizationManager.localized("rewards_modal_achievement_reward"), 15))
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
                    runWithParentConfirmation {
                        rejectAchievement(request: request)
                    }
                }) {
                    Text(localizationManager.localized("rewards_modal_achievement_reject"))
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
        let achievementHistory: RewardHistoryTexts = (
            title: RewardText(key: "child_rewards_history_achievement_title"),
            reason: RewardText.formatted(key: "child_rewards_history_achievement_reason_approved", argument: request.achievement, localizationManager: localizationManager)
        )
        addToHistory(isReward: true, texts: achievementHistory, amount: rewardAmount)
        
        HapticFeedback.notification(.success)
        print("✅ Достижение одобрено: \(request.achievement), награда: +\(rewardAmount) 🦄")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    /// Отклонение достижения
    private func rejectAchievement(request: AchievementRequest) {
        // Обновляем статус запроса
        updateAchievementRequestStatus(requestId: request.id, status: "rejected")
        
        // Добавляем в историю
        let achievementHistory: RewardHistoryTexts = (
            title: RewardText(key: "child_rewards_history_achievement_title"),
            reason: RewardText.formatted(key: "child_rewards_history_achievement_reason_rejected", argument: request.achievement, localizationManager: localizationManager)
        )
        addToHistory(isReward: false, texts: achievementHistory, amount: 0)
        
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
        let goalHistory: RewardHistoryTexts = (
            title: RewardText(key: "child_rewards_history_goal_title"),
            reason: RewardText.formatted(key: "child_rewards_history_goal_reason_approved", argument: goalTitlePending, localizationManager: localizationManager)
        )
        addToHistory(isReward: false, texts: goalHistory, amount: 0)
        
        goalTitlePending = ""
        goalCostPending = 0
        
        HapticFeedback.notification(.success)
        print("✅ Цель одобрена: \(goalTitle)")
    }
    
    private func rejectGoal() {
        // Добавляем в историю
        let goalHistory: RewardHistoryTexts = (
            title: RewardText(key: "child_rewards_history_goal_title"),
            reason: RewardText.formatted(key: "child_rewards_history_goal_reason_rejected", argument: goalTitlePending, localizationManager: localizationManager)
        )
        addToHistory(isReward: false, texts: goalHistory, amount: 0)
        
        goalTitlePending = ""
        goalCostPending = 0
        goalApprovalPending = false
        
        HapticFeedback.impact(.medium)
        print("❌ Цель отклонена")
    }
    
    private func addToHistory(isReward: Bool, texts: RewardHistoryTexts, amount: Int) {
        let operation = RewardHistoryEntry(
            title: texts.title,
            reason: texts.reason,
            amount: amount,
            isReward: isReward,
            date: Date()
        )
        var history = fetchHistory()
        history.insert(operation, at: 0)
        saveHistory(history)
    }
    
    private func fetchHistory() -> [RewardHistoryEntry] {
        guard let data = rewardsHistoryData.data(using: .utf8),
              let operations = try? JSONDecoder().decode([RewardHistoryEntry].self, from: data) else {
            return []
        }
        return operations
    }
    
    private func saveHistory(_ history: [RewardHistoryEntry]) {
        if let encoded = try? JSONEncoder().encode(history),
           let jsonString = String(data: encoded, encoding: .utf8) {
            rewardsHistoryData = jsonString
            NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        }
    }
    
    private func getRecentOperations() -> [RewardHistoryEntry] {
        guard let data = rewardsHistoryData.data(using: .utf8),
              let operations = try? JSONDecoder().decode([RewardHistoryEntry].self, from: data) else {
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
    
    private func rewardChild(amount: Int, history: RewardHistoryTexts) {
        // ✅ БЕЗОПАСНОСТЬ: Только родители могут наградить
        guard isUserParent else {
            print("⚠️ ПРОБЛЕМА БЕЗОПАСНОСТИ: Попытка наградить ребёнка не родителем!")
            HapticFeedback.notification(.error)
            return
        }
        let resolvedReason = history.reason.resolved(with: localizationManager)
        let resolvedTitle = history.title.resolved(with: localizationManager)

        // Определяем иконку по причине (используется косвенно через getRewardIcon)
        let _ = getRewardIcon(for: resolvedReason.isEmpty ? resolvedTitle : resolvedReason)

        addToHistory(isReward: true, texts: history, amount: amount)
        
        // Обновляем баланс в AppStorage (синхронизация с ChildRewardsScreen)
        let currentBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
        let newBalance = currentBalance + amount
        UnicornRewardsStore.writeBalance(newBalance, for: rewardsScopeChildId)
        
        // Обновляем статистику за неделю
        let currentWeekly = UnicornRewardsStore.readWeeklyEarned(for: rewardsScopeChildId)
        UnicornRewardsStore.writeWeeklyEarned(currentWeekly + amount, for: rewardsScopeChildId)
        
        // Явно отправляем уведомление для обновления других экранов
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        
        // Обновляем локальные переменные
        unicornBalance = newBalance
        weeklyRewarded += amount
        
        HapticFeedback.notification(.success)
        print("✅ Вознаградили ребёнка: +\(amount) 🦄, причина: \(resolvedReason)")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    private func punishChild(amount: Int, history: RewardHistoryTexts) {
        // ✅ БЕЗОПАСНОСТЬ: Только родители могут наказывать
        guard isUserParent else {
            print("⚠️ ПРОБЛЕМА БЕЗОПАСНОСТИ: Попытка наказать ребёнка не родителем!")
            HapticFeedback.notification(.error)
            return
        }
        let resolvedReason = history.reason.resolved(with: localizationManager)
        let resolvedTitle = history.title.resolved(with: localizationManager)

        // Определяем иконку по причине (используется косвенно через getPunishmentIcon)
        let _ = getPunishmentIcon(for: resolvedReason.isEmpty ? resolvedTitle : resolvedReason)

        addToHistory(isReward: false, texts: history, amount: amount)
        
        // Обновляем баланс в AppStorage (синхронизация с ChildRewardsScreen)
        let currentBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
        let newBalance = max(0, currentBalance - amount) // Не может быть отрицательным
        UnicornRewardsStore.writeBalance(newBalance, for: rewardsScopeChildId)
        
        // Обновляем статистику за неделю
        let currentWeekly = UnicornRewardsStore.readWeeklyPunished(for: rewardsScopeChildId)
        UnicornRewardsStore.writeWeeklyPunished(currentWeekly + amount, for: rewardsScopeChildId)
        
        // Явно отправляем уведомление для обновления других экранов
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
        
        // Обновляем локальные переменные
        unicornBalance = newBalance
        weeklyPunished += amount
        
        HapticFeedback.notification(.warning)
        print("❌ Наказали ребёнка: -\(amount) 🦄, причина: \(resolvedReason)")
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool
    @Binding var amount: String
    @Binding var reason: String
    let onConfirm: (Int, RewardHistoryTexts) -> Void
    
    // Используем earningWays из UserDefaults вместо захардкоженных шаблонов
    @AppStorage("earning_ways_list") private var earningWaysData: String = ""
    @State private var earningWays: [EarningWay] = []
    
    @State private var selectedWay: EarningWay? = nil
    
    // Дефолтные шаблоны (используются только если earningWays пустые)
    private var defaultTemplates: [EarningWay] {
        EarningWay.defaultEarningWays
    }
    
    // Активные способы заработка (только включенные)
    private var activeEarningWays: [EarningWay] {
        earningWays.filter { $0.isEnabled }
    }
    
    // Используем earningWays если они есть, иначе дефолтные шаблоны
    private var templates: [EarningWay] {
        if !activeEarningWays.isEmpty {
            return activeEarningWays
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
                        Text(localizationManager.localized("rewards_modal_reward_child_title"))
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                            .padding(.top, Spacing.m)
                        
                        // Шаблоны
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("rewards_modal_templates"))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            VStack(spacing: Spacing.s) {
                                ForEach(templates, id: \.id) { way in
                                    Button(action: {
                                        selectedWay = way
                                        reason = way.localizedTitle(localizationManager)
                                        amount = String(way.amount)
                                    }) {
                                        HStack {
                                            Text(way.icon)
                                                .font(.system(size: 24))
                                            VStack(alignment: .leading, spacing: Spacing.xxs) {
                                                Text(way.localizedTitle(localizationManager))
                                                    .font(.body)
                                                    .foregroundColor(.textPrimary)
                                                let subtitle = way.localizedSubtitle(localizationManager)
                                                if !subtitle.isEmpty {
                                                    Text(subtitle)
                                                        .font(.caption)
                                                        .foregroundColor(.textSecondary)
                                                }
                                            }
                                            Spacer()
                                            Text("+\(way.amount)")
                                                .font(.bodyBold)
                                                .foregroundColor(.successGreen)
                                        }
                                        .padding(Spacing.m)
                                        .background(
                                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                                .fill(selectedWay?.id == way.id ? Color.successGreen.opacity(0.2) : Color.backgroundMedium.opacity(0.5))
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
                            Text(localizationManager.localized("rewards_modal_custom_reason"))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            TextField(localizationManager.localized("rewards_modal_custom_reason_placeholder"), text: $reason)
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
                                        selectedWay = nil
                                    }
                                }
                        }
                        
                        // Сумма
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("rewards_modal_reward_amount"))
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
                            onConfirm(amountInt, buildHistoryTexts(amountValue: amountInt))
                            isPresented = false
                        }) {
                            Text(localizationManager.localized("rewards_modal_confirm"))
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
                    Text(localizationManager.localized("rewards_modal_reward_title"))
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("rewards_modal_cancel")) {
                        isPresented = false
                    }
                }
            }
            .id("reward_input_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        }
    }

    private func buildHistoryTexts(amountValue: Int) -> RewardHistoryTexts {
        let language = localizationManager.currentLanguage
        if let way = selectedWay {
            let titleText = way.title
            let subtitleText = way.subtitle
            let hasSubtitle = subtitleText.localizationKey != nil || subtitleText.translations.isEmpty == false
            let reasonText = hasSubtitle ? subtitleText : titleText
            return (title: titleText, reason: reasonText)
        }
        let trimmed = reason.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            return (
                title: RewardText(key: "child_rewards_history_reward_title"),
                reason: RewardText(key: "child_rewards_history_reward_reason_default")
            )
        }
        let customText = RewardText.custom(trimmed, language: language)
        return (title: customText, reason: customText)
    }
}

struct PunishInputModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool
    @Binding var amount: String
    @Binding var reason: String
    let onConfirm: (Int, RewardHistoryTexts) -> Void
    
    @AppStorage("punishment_reasons_list") private var punishmentReasonsData: String = ""
    @State private var punishmentReasons: [PunishmentReason] = []
    @State private var selectedReason: PunishmentReason? = nil
    
    private var defaultTemplates: [PunishmentReason] {
        PunishmentReason.defaultPunishmentReasons
    }
    
    private var activeReasons: [PunishmentReason] {
        punishmentReasons.filter { $0.isEnabled }
    }
    
    private var templates: [PunishmentReason] {
        if !activeReasons.isEmpty {
            return activeReasons
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
                        Text(localizationManager.localized("rewards_modal_punish_child_title"))
                            .font(.h2)
                            .foregroundColor(.textPrimary)
                            .padding(.top, Spacing.m)
                        
                        // Шаблоны
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("rewards_modal_punish_templates"))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            VStack(spacing: Spacing.s) {
                                ForEach(templates, id: \.id) { item in
                                    Button(action: {
                                        selectedReason = item
                                        reason = item.localizedTitle(localizationManager)
                                        amount = String(item.amount)
                                    }) {
                                        HStack {
                                            Text(item.icon)
                                                .font(.system(size: 24))
                                            VStack(alignment: .leading, spacing: Spacing.xxs) {
                                                Text(item.localizedTitle(localizationManager))
                                                    .font(.body)
                                                    .foregroundColor(.textPrimary)
                                                let subtitle = item.localizedSubtitle(localizationManager)
                                                if !subtitle.isEmpty {
                                                    Text(subtitle)
                                                        .font(.caption)
                                                        .foregroundColor(.textSecondary)
                                                }
                                            }
                                            Spacer()
                                            Text("-\(item.amount)")
                                                .font(.bodyBold)
                                                .foregroundColor(.dangerRed)
                                        }
                                        .padding(Spacing.m)
                                        .background(
                                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                                .fill(selectedReason?.id == item.id ? Color.dangerRed.opacity(0.2) : Color.backgroundMedium.opacity(0.5))
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
                            Text(localizationManager.localized("rewards_modal_custom_reason"))
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .padding(.horizontal, Spacing.screenPadding)
                            
                            TextField(localizationManager.localized("rewards_modal_punish_custom_reason_placeholder"), text: $reason)
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
                                        selectedReason = nil
                                    }
                                }
                        }
                        
                        // Сумма
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text(localizationManager.localized("rewards_modal_punish_amount"))
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
                            onConfirm(amountInt, buildHistoryTexts())
                            isPresented = false
                        }) {
                            Text(localizationManager.localized("rewards_modal_punish_confirm"))
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
                    Text(localizationManager.localized("rewards_modal_punish_title"))
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("rewards_modal_cancel")) {
                        isPresented = false
                    }
                }
            }
            .id("punish_input_modal_lang_\(localizationManager.currentLanguage.rawValue)")
        }
    }

    private func buildHistoryTexts() -> RewardHistoryTexts {
        let language = localizationManager.currentLanguage
        if let reasonModel = selectedReason {
            let titleText = reasonModel.title
            let subtitleText = reasonModel.subtitle
            let hasSubtitle = subtitleText.localizationKey != nil || subtitleText.translations.isEmpty == false
            let reasonText = hasSubtitle ? subtitleText : titleText
            return (title: titleText, reason: reasonText)
        }
        let trimmed = reason.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            return (
                title: RewardText(key: "child_rewards_history_punish_title"),
                reason: RewardText(key: "child_rewards_history_punish_reason_default")
            )
        }
        let customText = RewardText.custom(trimmed, language: language)
        return (title: customText, reason: customText)
    }
}

// MARK: - Reward Operation Model
// RewardOperation is defined in Shared/Models/RewardModels.swift

// MARK: - Shop Management Modal

struct ShopManagementModal: View {
    @Binding var rewards: [ShopReward]
    let onSave: () -> Void
    
    @Environment(\.presentationMode) var presentationMode
    @EnvironmentObject private var localizationManager: LocalizationManager
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
                                Text(localizationManager.localized("child_rewards_shop_edit_info_title"))
                                    .font(.body)
                                    .fontWeight(.semibold)
                            }
                            Text(localizationManager.localized("child_rewards_shop_edit_info_desc"))
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
                            Text(String(format: localizationManager.localized("child_rewards_shop_list_title"), rewards.count))
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
                                Text(localizationManager.localized("child_rewards_shop_add_new_button"))
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
            .navigationTitle(localizationManager.localized("rewards_modal_shop_management_nav_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("rewards_modal_cancel")) {
                        presentationMode.wrappedValue.dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("rewards_modal_confirm")) {
                        onSave()
                    }
                }
            }
            .id("shop_management_modal_lang_\(localizationManager.currentLanguage.rawValue)")
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
                .environmentObject(localizationManager)
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
                .environmentObject(localizationManager)
            }
        }
    }
    
    private func rewardEditRow(reward: Binding<ShopReward>) -> some View {
        let localizedTitle = reward.wrappedValue.localizedTitle(localizationManager)
        let localizedDesc = reward.wrappedValue.localizedDescription(localizationManager)
        
        return VStack(spacing: Spacing.m) {
            HStack(spacing: Spacing.m) {
                Text(reward.icon.wrappedValue)
                    .font(.system(size: 40))
                    .frame(width: 50)
                
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(localizedTitle)
                            .font(.body)
                            .fontWeight(.semibold)
                            .foregroundColor(.textPrimary)
                        
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
                    
                    if !localizedDesc.isEmpty {
                        Text(localizedDesc)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    HStack(spacing: Spacing.xs) {
                        Text(localizationManager.localized("child_rewards_shop_price_label"))
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
                    VStack(spacing: Spacing.xxs) {
                        Toggle("", isOn: reward.isEnabled)
                            .labelsHidden()
                            .scaleEffect(0.9)
                        Text(reward.isEnabled.wrappedValue ? localizationManager.localized("toggle_on") : localizationManager.localized("toggle_off"))
                            .font(.captionSmall)
                            .foregroundColor(reward.isEnabled.wrappedValue ? .successGreen : .textSecondary)
                    }
                    
                    Button(action: {
                        print("🔍 DEBUG: Редактирование награды: \(localizedTitle)")
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    let onAdd: (ShopReward) -> Void
    let onCancel: () -> Void

    @State private var icon: String = "🎁"
    @State private var title: String = ""
    @State private var desc: String = ""
    @State private var price: Int = 100

    private let availableIcons = ["🎮", "📱", "🌙", "🍕", "🎬", "🎁", "🎂", "🍦", "🎨", "📚", "⚽", "🎸"]

    private var language: LocalizationManager.Language {
        localizationManager.currentLanguage
    }

    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: Spacing.l) {
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text(localizationManager.localized("child_rewards_shop_field_icon"))
                                .font(.body)
                                .foregroundColor(.textPrimary)

                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 6), spacing: Spacing.m) {
                                ForEach(availableIcons, id: \.self) { iconEmoji in
                                    Button(action: { icon = iconEmoji }) {
                                        Text(iconEmoji)
                                            .font(.system(size: 32))
                                            .frame(width: 50, height: 50)
                                            .background(icon == iconEmoji ? Color.secondaryGold.opacity(0.3) : Color.backgroundMedium.opacity(0.5))
                                            .clipShape(RoundedRectangle(cornerRadius: 10))
                                    }
                                }
                            }
                        }

                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(localizationManager.localized("child_rewards_shop_field_name"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField(localizationManager.localized("child_rewards_shop_field_name_placeholder"), text: $title)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }

                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(localizationManager.localized("child_rewards_shop_field_description"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField(localizationManager.localized("child_rewards_shop_field_description_placeholder"), text: $desc)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }

                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(localizationManager.localized("child_rewards_shop_field_price"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField("", value: $price, format: .number)
                                .textFieldStyle(.plain)
                                .keyboardType(.numberPad)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }

                        Button(action: saveReward) {
                            Text(localizationManager.localized("child_rewards_shop_add_button"))
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
            .navigationTitle(localizationManager.localized("child_rewards_shop_add_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("rewards_modal_cancel")) {
                        onCancel()
                    }
                }
            }
        }
    }

    private func saveReward() {
        guard !title.isEmpty else { return }

        var descriptionText = RewardText(translations: [:])
        if !desc.isEmpty {
            descriptionText = RewardText(translations: [language.rawValue: desc])
        }

        let reward = ShopReward(
            icon: icon,
            title: RewardText(translations: [language.rawValue: title]),
            desc: descriptionText,
            price: price
        )

        onAdd(reward)
    }
}

// MARK: - Edit Reward Modal

struct EditRewardModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let reward: ShopReward
    let onSave: (ShopReward) -> Void
    let onCancel: () -> Void

    @State private var icon: String = ""
    @State private var title: String = ""
    @State private var desc: String = ""
    @State private var price: Int = 0
    @State private var initialTitle: String = ""
    @State private var initialDesc: String = ""
    @State private var didLoad = false

    private let availableIcons = ["🎮", "📱", "🌙", "🍕", "🎬", "🎁", "🎂", "🍦", "🎨", "📚", "⚽", "🎸"]

    private var language: LocalizationManager.Language {
        localizationManager.currentLanguage
    }

    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: Spacing.l) {
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            Text(localizationManager.localized("child_rewards_shop_field_icon"))
                                .font(.body)
                                .foregroundColor(.textPrimary)

                            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 6), spacing: Spacing.m) {
                                ForEach(availableIcons, id: \.self) { iconEmoji in
                                    Button(action: { icon = iconEmoji }) {
                                        Text(iconEmoji)
                                            .font(.system(size: 32))
                                            .frame(width: 50, height: 50)
                                            .background(icon == iconEmoji ? Color.secondaryGold.opacity(0.3) : Color.backgroundMedium.opacity(0.5))
                                            .clipShape(RoundedRectangle(cornerRadius: 10))
                                    }
                                }
                            }
                        }

                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(localizationManager.localized("child_rewards_shop_field_name"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField(localizationManager.localized("child_rewards_shop_field_name_placeholder"), text: $title)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }

                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(localizationManager.localized("child_rewards_shop_field_description"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField(localizationManager.localized("child_rewards_shop_field_description_placeholder"), text: $desc)
                                .textFieldStyle(.plain)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }

                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(localizationManager.localized("child_rewards_shop_field_price"))
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            TextField("", value: $price, format: .number)
                                .textFieldStyle(.plain)
                                .keyboardType(.numberPad)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
                        }

                        Button(action: saveChanges) {
                            Text(localizationManager.localized("child_rewards_shop_save_button"))
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
            .navigationTitle(localizationManager.localized("child_rewards_shop_edit_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("rewards_modal_cancel")) {
                        onCancel()
                    }
                }
            }
            .onAppear(perform: loadData)
            .onChange(of: localizationManager.currentLanguage) { _ in
                didLoad = false
                loadData()
            }
        }
    }

    private func loadData() {
        guard !didLoad else { return }

        icon = reward.icon
        price = reward.price

        let resolvedTitle = reward.titleValue(for: language)
        let resolvedDesc = reward.descriptionValue(for: language)

        let fallbackTitle = reward.localizedTitle(localizationManager)
        let fallbackDesc = reward.localizedDescription(localizationManager)

        title = resolvedTitle.isEmpty ? fallbackTitle : resolvedTitle
        desc = resolvedDesc.isEmpty ? fallbackDesc : resolvedDesc
        initialTitle = title
        initialDesc = desc
        didLoad = true
    }

    private func saveChanges() {
        var updated = reward
        updated.icon = icon
        updated.price = price
 
        if title != initialTitle {
            var titleText = updated.title
            titleText.setCustom(title, for: language)
            updated.title = titleText
        }
 
        if desc != initialDesc {
            var descText = updated.desc
            descText.setCustom(desc, for: language)
            updated.desc = descText
        }
 
        onSave(updated)
    }
}

// MARK: - Add/Edit Earning Way Modals

struct AddEarningWayModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool
    let onAdd: (EarningWay) -> Void

    @State private var icon: String = "📚"
    @State private var title: String = ""
    @State private var subtitle: String = ""
    @State private var amount: Int = 10

    private var language: LocalizationManager.Language { localizationManager.currentLanguage }

    var body: some View {
        NavigationView {
            Form {
                Section(localizationManager.localized("child_rewards_earning_field_icon")) {
                    TextField("📚", text: $icon)
                        .textInputAutocapitalization(.never)
                }
                Section(localizationManager.localized("child_rewards_earning_field_name")) {
                    TextField(localizationManager.localized("child_rewards_earning_field_name_placeholder"), text: $title)
                }
                Section(localizationManager.localized("child_rewards_earning_field_description")) {
                    TextField(localizationManager.localized("child_rewards_earning_field_description_placeholder"), text: $subtitle)
                }
                Section(localizationManager.localized("child_rewards_earning_field_amount")) {
                    Stepper("\(amount) 🦄", value: $amount, in: 1...1000)
                }
            }
            .navigationTitle(localizationManager.localized("child_rewards_earning_add_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("rewards_modal_cancel")) {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("child_rewards_earning_add_button")) {
                        addWay()
                    }
                    .disabled(title.isEmpty || subtitle.isEmpty)
                }
            }
        }
    }

    private func addWay() {
        let trimmedIcon = icon.trimmingCharacters(in: .whitespacesAndNewlines)
        let finalIcon = trimmedIcon.isEmpty ? "📚" : trimmedIcon

        let newWay = EarningWay(
            icon: finalIcon,
            title: RewardText(translations: [language.rawValue: title]),
            subtitle: RewardText(translations: [language.rawValue: subtitle]),
            amount: amount
        )

        onAdd(newWay)
        isPresented = false
    }
}

struct EditEarningWayModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool
    @Binding var earningWay: EarningWay
    let onSave: () -> Void
    let onDelete: () -> Void

    @State private var icon: String = ""
    @State private var title: String = ""
    @State private var subtitle: String = ""
    @State private var amount: Int = 0
    @State private var isEnabled: Bool = true
    @State private var initialTitle: String = ""
    @State private var initialSubtitle: String = ""
    @State private var didLoad = false

    private var language: LocalizationManager.Language { localizationManager.currentLanguage }

    var body: some View {
        NavigationView {
            Form {
                Section(localizationManager.localized("child_rewards_earning_field_icon")) {
                    TextField("📚", text: $icon)
                        .textInputAutocapitalization(.never)
                }
                Section(localizationManager.localized("child_rewards_earning_field_name")) {
                    TextField(localizationManager.localized("child_rewards_earning_field_name_placeholder"), text: $title)
                }
                Section(localizationManager.localized("child_rewards_earning_field_description")) {
                    TextField(localizationManager.localized("child_rewards_earning_field_description_placeholder"), text: $subtitle)
                }
                Section(localizationManager.localized("child_rewards_earning_field_amount")) {
                    Stepper("\(amount) 🦄", value: $amount, in: 1...1000)
                }
                Section(localizationManager.localized("rewards_modal_enabled")) {
                    Toggle(localizationManager.localized("rewards_modal_enabled"), isOn: $isEnabled)
                }
            }
            .navigationTitle(localizationManager.localized("child_rewards_earning_edit_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("child_rewards_earning_delete_button")) {
                        isPresented = false
                        onDelete()
                    }
                    .foregroundColor(.dangerRed)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("child_rewards_earning_save_button")) {
                        saveChanges()
                    }
                    .disabled(title.isEmpty || subtitle.isEmpty)
                }
            }
            .onAppear(perform: loadData)
            .onChange(of: localizationManager.currentLanguage) { _ in
                didLoad = false
                loadData()
            }
        }
    }

    private func loadData() {
        guard !didLoad else { return }

        icon = earningWay.icon
        amount = earningWay.amount
        isEnabled = earningWay.isEnabled

        let resolvedTitle = earningWay.titleValue(for: language)
        let resolvedSubtitle = earningWay.subtitleValue(for: language)

        let fallbackTitle = earningWay.localizedTitle(localizationManager)
        let fallbackSubtitle = earningWay.localizedSubtitle(localizationManager)

        title = resolvedTitle.isEmpty ? fallbackTitle : resolvedTitle
        subtitle = resolvedSubtitle.isEmpty ? fallbackSubtitle : resolvedSubtitle
        initialTitle = title
        initialSubtitle = subtitle
        didLoad = true
    }

    private func saveChanges() {
        let trimmedIcon = icon.trimmingCharacters(in: .whitespacesAndNewlines)
        earningWay.icon = trimmedIcon.isEmpty ? "📚" : trimmedIcon
        earningWay.amount = amount
        earningWay.isEnabled = isEnabled

        if title != initialTitle {
            earningWay.updateTitle(title, language: language)
        }

        if subtitle != initialSubtitle {
            earningWay.updateSubtitle(subtitle, language: language)
        }

        onSave()
        isPresented = false
    }
}

// MARK: - Add/Edit Punishment Reason Modals

struct AddPunishmentReasonModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool
    let onAdd: (PunishmentReason) -> Void

    @State private var icon: String = "⚠️"
    @State private var title: String = ""
    @State private var subtitle: String = ""
    @State private var amount: Int = 10

    private var language: LocalizationManager.Language { localizationManager.currentLanguage }

    var body: some View {
        NavigationView {
            Form {
                Section(localizationManager.localized("child_rewards_punish_field_icon")) {
                    TextField("⚠️", text: $icon)
                        .textInputAutocapitalization(.never)
                }
                Section(localizationManager.localized("child_rewards_punish_field_name")) {
                    TextField(localizationManager.localized("child_rewards_punish_field_name_placeholder"), text: $title)
                }
                Section(localizationManager.localized("child_rewards_punish_field_description")) {
                    TextField(localizationManager.localized("child_rewards_punish_field_description_placeholder"), text: $subtitle)
                }
                Section(localizationManager.localized("child_rewards_punish_field_amount")) {
                    Stepper("\(amount) 🦄", value: $amount, in: 1...200)
                }
            }
            .navigationTitle(localizationManager.localized("child_rewards_punish_add_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("rewards_modal_cancel")) {
                        isPresented = false
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("child_rewards_punish_add_button")) {
                        addReason()
                    }
                    .disabled(title.isEmpty || subtitle.isEmpty)
                }
            }
        }
    }

    private func addReason() {
        let trimmedIcon = icon.trimmingCharacters(in: .whitespacesAndNewlines)
        let finalIcon = trimmedIcon.isEmpty ? "⚠️" : trimmedIcon

        let reason = PunishmentReason(
            icon: finalIcon,
            title: RewardText(translations: [language.rawValue: title]),
            subtitle: RewardText(translations: [language.rawValue: subtitle]),
            amount: amount
        )

        onAdd(reason)
        isPresented = false
    }
}

struct EditPunishmentReasonModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Binding var isPresented: Bool
    @Binding var punishmentReason: PunishmentReason
    let onSave: () -> Void
    let onDelete: () -> Void

    @State private var icon: String = ""
    @State private var title: String = ""
    @State private var subtitle: String = ""
    @State private var amount: Int = 0
    @State private var isEnabled: Bool = true
    @State private var initialTitle: String = ""
    @State private var initialSubtitle: String = ""
    @State private var didLoad = false

    private var language: LocalizationManager.Language { localizationManager.currentLanguage }

    var body: some View {
        NavigationView {
            Form {
                Section(localizationManager.localized("child_rewards_punish_field_icon")) {
                    TextField("⚠️", text: $icon)
                        .textInputAutocapitalization(.never)
                }
                Section(localizationManager.localized("child_rewards_punish_field_name")) {
                    TextField(localizationManager.localized("child_rewards_punish_field_name_placeholder"), text: $title)
                }
                Section(localizationManager.localized("child_rewards_punish_field_description")) {
                    TextField(localizationManager.localized("child_rewards_punish_field_description_placeholder"), text: $subtitle)
                }
                Section(localizationManager.localized("child_rewards_punish_field_amount")) {
                    Stepper("\(amount) 🦄", value: $amount, in: 1...200)
                }
                Section(localizationManager.localized("rewards_modal_enabled")) {
                    Toggle(localizationManager.localized("rewards_modal_enabled"), isOn: $isEnabled)
                }
            }
            .navigationTitle(localizationManager.localized("child_rewards_punish_edit_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("child_rewards_punish_delete_button")) {
                        isPresented = false
                        onDelete()
                    }
                    .foregroundColor(.dangerRed)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("child_rewards_punish_save_button")) {
                        saveChanges()
                    }
                    .disabled(title.isEmpty || subtitle.isEmpty)
                }
            }
            .onAppear(perform: loadData)
            .onChange(of: localizationManager.currentLanguage) { _ in
                didLoad = false
                loadData()
            }
        }
    }

    private func loadData() {
        guard !didLoad else { return }

        icon = punishmentReason.icon
        amount = punishmentReason.amount
        isEnabled = punishmentReason.isEnabled

        let resolvedTitle = punishmentReason.titleValue(for: language)
        let resolvedSubtitle = punishmentReason.subtitleValue(for: language)

        let fallbackTitle = punishmentReason.localizedTitle(localizationManager)
        let fallbackSubtitle = punishmentReason.localizedSubtitle(localizationManager)

        title = resolvedTitle.isEmpty ? fallbackTitle : resolvedTitle
        subtitle = resolvedSubtitle.isEmpty ? fallbackSubtitle : resolvedSubtitle
        initialTitle = title
        initialSubtitle = subtitle
        didLoad = true
    }

    private func saveChanges() {
        let trimmedIcon = icon.trimmingCharacters(in: .whitespacesAndNewlines)
        punishmentReason.icon = trimmedIcon.isEmpty ? "⚠️" : trimmedIcon
        punishmentReason.amount = amount
        punishmentReason.isEnabled = isEnabled

        if title != initialTitle {
            punishmentReason.updateTitle(title, language: language)
        }

        if subtitle != initialSubtitle {
            punishmentReason.updateSubtitle(subtitle, language: language)
        }

        onSave()
        isPresented = false
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



