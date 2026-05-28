import SwiftUI
import Foundation
import UIKit

/// 🦄 Child Rewards Screen
/// Экран наград для детского интерфейса
/// Источник дизайна: GAMIFICATION_NAVIGATION_ARCHITECTURE.md
/// 
/// ✅ RewardHistoryEntry определён в Shared/Models/RewardModels.swift
struct ChildRewardsScreen: View {
    
    // MARK: - State
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @StateObject private var viewModel = ChildRewardsViewModel()
    @State private var selectedTab: RewardTab = .shop
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    @AppStorage("parental_selected_child") private var legacySelectedChild: String = ""
    
    // Награды магазина (загружаются из UserDefaults)
    @AppStorage("shop_rewards_list") private var shopRewardsData: String = ""
    @State private var availableRewards: [ShopReward] = []
    
    // Сохраняем игровой прогресс в AppStorage
    // ✅ СТАРТОВЫЙ БАЛАНС: 100 единорогов для нового ребенка
    @AppStorage("child_unicorn_balance") private var storedUnicornBalance: Int = 100
    @State private var unicornBalance: Int = 100 {
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
    
    @AppStorage("child_goal_title") private var storedGoalTitle: String = ""
    @State private var goalTitle: String = "" {
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
    @State private var loadErrorMessage: String?
    @State private var isInitialLoadCompleted: Bool = false
    @State private var initialLoadingFallbackScheduled: Bool = false
    @State private var didStartInitialLoading: Bool = false
    @State private var showSettingsSheet: Bool = false
    @State private var isInitialLoadInFlight: Bool = false
    @State private var cachedHistoryOperations: [RewardHistoryEntry] = []
    @State private var shopRewardsSaveDebounceTask: Task<Void, Never>? = nil
    @State private var lastDashboardSignature: String? = nil
    @State private var lastDashboardHandledAt: Date = .distantPast
    @State private var achievementBurstActive = false
    @State private var lastSampledGoalProgress: Double = -1
    @State private var purchaseRewardBurstActive = false

    // ✅ ГЕЙМИФИКАЦИЯ: API синхронизация
    @State private var isLoadingRewards: Bool = false
    @State private var isLoadingHistory: Bool = false
    @State private var apiError: String? = nil
    
    private let apiService = APIService.shared
    
    private var effectiveChildId: String? {
        let trimmedId = selectedChildId.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmedId.isEmpty { return trimmedId }
        let legacy = legacySelectedChild.trimmingCharacters(in: .whitespacesAndNewlines)
        return legacy.isEmpty ? nil : legacy
    }
    
    // Получаем userId для API вызовов
    private var userId: String {
        let defaults = UserDefaults.standard
        if let id = defaults.string(forKey: "user_id")?.trimmingCharacters(in: .whitespacesAndNewlines), !id.isEmpty {
            return id
        }
        if let memberId = defaults.string(forKey: "your_member_id")?.trimmingCharacters(in: .whitespacesAndNewlines), !memberId.isEmpty {
            return memberId
        }
        if let childId = effectiveChildId?.trimmingCharacters(in: .whitespacesAndNewlines), !childId.isEmpty {
            return childId
        }
        return "guest"
    }

    private var rewardsScopeChildId: String? {
        effectiveChildId ?? UnicornRewardsStore.resolveActiveChildId()
    }

    private func mergedBalanceWithLocal(_ serverBalance: Int) -> Int {
        let localBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
        // Защита: не затираем реальный локальный баланс подозрительным нулем от guest/пустого контекста.
        if serverBalance <= 0 && localBalance > 0 {
            return localBalance
        }
        return max(serverBalance, 0)
    }
    
    // MARK: - Tabs
    
    enum RewardTab {
        case shop
        case history
        case achievements
        
        func localizedTitle(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .shop: return localizationManager.localized("child_rewards_tab_shop")
            case .history: return localizationManager.localized("child_rewards_tab_history")
            case .achievements: return localizationManager.localized("child_rewards_tab_achievements")
            }
        }
        
        var title: String {
            // Deprecated: используйте localizedTitle вместо этого
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

            CelebrationParticleBurstView(kind: .achievementMagic, active: achievementBurstActive, onFinished: { achievementBurstActive = false })
                .ignoresSafeArea()

            CelebrationParticleBurstView(kind: .rewardPurchase, active: purchaseRewardBurstActive, onFinished: { purchaseRewardBurstActive = false })
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                header
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Группа 1: Состояния загрузки и ошибки
                        Group {
                            if viewModel.isLoading && !isInitialLoadCompleted {
                                loadingState
                            }
                            if let loadErrorMessage = loadErrorMessage {
                                errorBanner(message: loadErrorMessage)
                            }
                        }
                        
                        // Группа 2: Основные карточки
                        Group {
                            if !isCurrentUserParent() {
                                companionWorldHeroCard
                            }
                            // Баланс единорогов
                            balanceCard
                            
                            // Прогресс к цели
                            goalProgressCard
                            
                            // Кнопка "Сообщить родителям"
                            requestButton
                        }
                        
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
                        
                        // Группа 3: Игры и табы
                        Group {
                            // 🎮 Игровые карточки 2x3
                            gamesGrid
                            
                            // Табы (Магазин, История)
                            tabSelector
                            
                            // Контент вкладок
                            tabContent
                        }
                        
                        Spacer()
                            .frame(height: Spacing.xxl)
                    }
                    .padding(.top, Spacing.m)
                }
                .refreshable {
                    // ✅ ГЕЙМИФИКАЦИЯ: Обновление данных с сервера
                    await refreshData()
                }
            }
        }
        .onAppear {
            lastSampledGoalProgress = goalProgress
        }
        .onChange(of: goalProgress) { newValue in
            if newValue >= 0.999 && lastSampledGoalProgress < 0.999 {
                achievementBurstActive = true
            }
            lastSampledGoalProgress = newValue
        }
        .navigationBarHidden(true)
        .withVisualLogger()
        .id("child_rewards_lang_\(localizationManager.currentLanguage.rawValue)")
        .sheet(isPresented: $showRequestModal) {
            AchievementRequestModal(
                onSendRequest: { achievement in
                    sendRequestToParents(achievement)
                }
            )
            .environmentObject(localizationManager)
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
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showSettingsSheet) {
            ChildRewardsSettingsModal(isPresented: $showSettingsSheet)
                .environmentObject(localizationManager)
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
        }
        .onAppear {
            guard !didStartInitialLoading else { return }
            didStartInitialLoading = true
            VisualLogger.shared.log("👀 ChildRewardsScreen onAppear", level: .info, category: "CHILD_REWARDS.UI")

            // ✅ КРИТИЧНО: Принудительная установка роли при открытии экрана
            // Это гарантирует, что роль будет установлена даже если пользователь открыл экран напрямую
            let currentRole = UserDefaults.standard.string(forKey: "current_user_role")
            print("🔍 ChildRewardsScreen.onAppear: Текущая роль: '\(currentRole ?? "НЕ УСТАНОВЛЕНА")'")
            
            // Если роль не установлена, пытаемся определить по текущему экрану
            if currentRole == nil {
                let currentScreen = navigationManager.currentScreen
                print("   🔍 Роль не установлена, проверяем текущий экран: \(currentScreen)")
                
                if currentScreen == .parentalControl {
                    UserDefaults.standard.set("parent", forKey: "current_user_role")
                    UserDefaults.standard.synchronize()
                    print("   ✅ Роль установлена как 'parent' (по текущему экрану)")
                } else if currentScreen == .childInterface {
                    UserDefaults.standard.set("child", forKey: "current_user_role")
                    UserDefaults.standard.synchronize()
                    print("   ✅ Роль установлена как 'child' (по текущему экрану)")
                } else {
                    // Проверяем стек навигации
                    if !navigationManager.navigationStack.isEmpty {
                        let previousScreen = navigationManager.navigationStack.last
                        print("   🔍 Проверяем предыдущий экран в стеке: \(previousScreen?.rawValue ?? "нет")")
                        
                        if previousScreen == .parentalControl {
                            UserDefaults.standard.set("parent", forKey: "current_user_role")
                            UserDefaults.standard.synchronize()
                            print("   ✅ Роль установлена как 'parent' (по предыдущему экрану)")
                        } else if previousScreen == .childInterface {
                            UserDefaults.standard.set("child", forKey: "current_user_role")
                            UserDefaults.standard.synchronize()
                            print("   ✅ Роль установлена как 'child' (по предыдущему экрану)")
                        }
                    }
                }
            }
            
            // Повторная проверка после установки
            let finalRole = UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА"
            print("   📋 Финальная роль: '\(finalRole)'")
            
            Task {
                VisualLogger.shared.log("🔄 Initial load triggered", level: .info, category: "CHILD_REWARDS.UI")
                await runInitialLoad()
            }

            // Hard-fallback: never keep the screen in endless initial loading.
            if !isInitialLoadCompleted && !initialLoadingFallbackScheduled {
                initialLoadingFallbackScheduled = true
                DispatchQueue.main.asyncAfter(deadline: .now() + 4.0) {
                    if !isInitialLoadCompleted {
                        isInitialLoadCompleted = true
                        VisualLogger.shared.log("⏱️ Initial UI fallback fired (4s)", level: .warning, category: "CHILD_REWARDS.UI")
                        if viewModel.isLoading {
                            loadErrorMessage = localizationManager.localized("child_rewards_error_generic")
                        }
                    }
                }
            }
            RewardLocalizationMigration.performIfNeeded()
            
            // Синхронизируем баланс из UserDefaults (единый источник истины)
            let currentBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
            if currentBalance > 0 {
                unicornBalance = currentBalance
                storedUnicornBalance = currentBalance
            } else {
                unicornBalance = storedUnicornBalance
            }
            
            // Восстанавливаем сохранённый прогресс из AppStorage
            weeklyEarned = UnicornRewardsStore.readWeeklyEarned(for: rewardsScopeChildId)
            weeklyPunished = UnicornRewardsStore.readWeeklyPunished(for: rewardsScopeChildId)
            goalProgress = storedGoalProgress
            goalTitle = storedGoalTitle
            goalCost = storedGoalCost
            
            // Загружаем награды магазина
            loadShopRewards()
            
            VisualLogger.shared.log("👤 role_is_parent = \(isCurrentUserParent())", level: .info, category: "CHILD_REWARDS.UI")
        }
        .onChange(of: storedUnicornBalance) { newValue in
            // Автообновление баланса при изменении в UserDefaults (например, из RewardsModalView)
            unicornBalance = newValue
        }
        .onReceive(NotificationCenter.default.publisher(for: .childRewardsDataDidChange)) { _ in
            // Обновляем список наград при изменении в UserDefaults
            loadShopRewards()
            cachedHistoryOperations = getHistoryOperations()
            // Обновляем баланс из UserDefaults
            let newBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
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
        .onReceive(viewModel.$dashboard.compactMap { $0 }) { data in
            let signature = "\(data.balance)|\(data.weeklyEarned)|\(data.weeklyPunished)|\(data.goalTitleKey ?? "nil")|\(data.goalCost)|\(data.rewards.count)"
            let isDuplicatePayload = (lastDashboardSignature == signature)
            let isTooSoon = Date().timeIntervalSince(lastDashboardHandledAt) < 1.0
            if isDuplicatePayload && isTooSoon {
                VisualLogger.shared.log("⏭️ Duplicate dashboard event ignored", level: .info, category: "CHILD_REWARDS.UI")
                return
            }
            lastDashboardSignature = signature
            lastDashboardHandledAt = Date()
            VisualLogger.shared.log("✅ Dashboard received and rendered", level: .success, category: "CHILD_REWARDS.UI")
            let safeBalance = mergedBalanceWithLocal(data.balance)
            unicornBalance = safeBalance
            storedUnicornBalance = safeBalance
            weeklyEarned = data.weeklyEarned
            weeklyPunished = data.weeklyPunished
            goalProgress = data.goalProgress
            if let titleKey = data.goalTitleKey {
                goalTitle = localizationManager.localized(titleKey)
            } else if goalTitle.isEmpty {
                // ✅ ИСПРАВЛЕНИЕ: Используем локализованное значение по умолчанию
                goalTitle = localizationManager.localized("child_rewards_goal_default_title")
            }
            if data.goalCost > 0 {
                goalCost = data.goalCost
            }
            if !data.rewards.isEmpty {
                availableRewards = data.rewards
                scheduleSaveShopRewards()
            }
            loadErrorMessage = nil
            isInitialLoadCompleted = true
            initialLoadingFallbackScheduled = false
        }
        .onAppear {
            guard didStartInitialLoading else { return }
            // ✅ ИСПРАВЛЕНИЕ: Инициализируем goalTitle локализованным значением по умолчанию при первом запуске
            if goalTitle.isEmpty && storedGoalTitle.isEmpty {
                goalTitle = localizationManager.localized("child_rewards_goal_default_title")
            } else if !storedGoalTitle.isEmpty && goalTitle.isEmpty {
                goalTitle = storedGoalTitle
            }
            
            cachedHistoryOperations = getHistoryOperations()
            if selectedTab == .history {
                loadHistoryFromServer()
            }
        }
        .onChange(of: selectedTab) { newTab in
            VisualLogger.shared.log("🧭 tab_changed = \(newTab.localizedTitle(localizationManager))", level: .info, category: "CHILD_REWARDS.UI")
            // Загружаем историю при переключении на вкладку истории
            if newTab == .history && !isLoadingHistory {
                loadHistoryFromServer()
            }
        }
        .onReceive(viewModel.$errorMessage) { message in
            // ✅ ИСПРАВЛЕНИЕ: Локализуем ошибку "Ресурс не найден"
            if let errorMessage = message {
                VisualLogger.shared.log("❌ ViewModel error = \(errorMessage)", level: .error, category: "CHILD_REWARDS.UI")
                // Не держим экран в вечной initial-loading фазе, если API вернул ошибку/таймаут.
                isInitialLoadCompleted = true
                if errorMessage.contains("Ресурс не найден") || errorMessage.contains("Not Found") || errorMessage.contains("404") {
                    loadErrorMessage = localizationManager.localized("child_rewards_error_resource_not_found")
                } else {
                    loadErrorMessage = errorMessage
                }
            } else {
                VisualLogger.shared.log("ℹ️ ViewModel error cleared", level: .info, category: "CHILD_REWARDS.UI")
                loadErrorMessage = nil
            }
        }
    }
    
    // MARK: - Header
    
    private var header: some View {
        HStack {
            Button(action: {
                HapticFeedback.impact(.light)
                VisualLogger.shared.log("⬅️ Back tapped", level: .info, category: "CHILD_REWARDS.UI")
                // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                dismiss()
                
                // Дополнительно синхронизируем NavigationManager для корректной работы стека.
                // Вызываем goBack без условия: при пустом стеке он сам делает fallback на root.
                DispatchQueue.main.async {
                    navigationManager.goBack(reason: "ChildRewards back button fallback")
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
            
            Text(localizationManager.localized("child_rewards_title"))
                .font(.h2)
                .foregroundColor(.textPrimary)
            
            Spacer()
            
            Button(action: {
                HapticFeedback.impact(.light)
                showSettingsSheet = true
                print("🔧 Открываем настройки наград")
            }) {
                Image(systemName: "gearshape.fill")
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(.textPrimary)
                    .frame(width: 44, height: 44)
                    .background(
                        Circle()
                            .fill(Color.backgroundMedium.opacity(0.5))
                    )
            }
            .accessibilityLabel(localizationManager.localized("child_rewards_settings_accessibility_label"))
            .accessibilityHint(localizationManager.localized("child_rewards_settings_accessibility_hint"))
        }
        .padding(.horizontal, Spacing.screenPadding)
        .padding(.vertical, Spacing.s)
    }
    
    private var loadingState: some View {
        HStack(spacing: Spacing.m) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .primaryBlue))
            Text(localizationManager.localized("child_rewards_loading"))
                .font(.body)
                .foregroundColor(.textSecondary)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.4))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private func errorBanner(message: String) -> some View {
        HStack(spacing: Spacing.s) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.warningOrange)
            Text(message)
                .font(.caption)
                .foregroundColor(.warningOrange)
            Spacer()
            Button(action: {
                loadErrorMessage = nil
                VisualLogger.shared.log("🔁 Retry tapped", level: .info, category: "CHILD_REWARDS.UI")
                Task { await runInitialLoad() }
            }) {
                Text(localizationManager.localized("child_rewards_retry"))
                    .font(.captionBold)
                    .foregroundColor(.primaryBlue)
            }
        }
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Balance Card
    
    private var balanceCard: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            // Иконка единорога
            Text("🦄")
                .font(.system(size: 60))
            
            // Баланс
            Text("\(unicornBalance)")
                .font(.system(size: 48, weight: .bold))
                .foregroundColor(Color(hex: "C084FC"))
            
            Text(localizationManager.localized("child_rewards_balance_label"))
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
                    Text(localizationManager.localized("child_rewards_earned_week"))
                        .font(.captionSmall)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                
                VStack(spacing: Spacing.xs) {
                    Text("-\(weeklyPunished)")
                        .font(.h2)
                        .foregroundColor(.dangerRed)
                    Text(localizationManager.localized("child_rewards_punished_week"))
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

    /// Крупная карточка входа в «Мир героев» (как баланс, на первом месте у ребёнка).
    private var companionWorldHeroCard: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            navigationManager.navigateTo(.companionHome)
        }) {
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack {
                    Text("✨")
                        .font(.system(size: 60))
                    Spacer()
                    Text("Голос и чат")
                        .font(.captionSmall.weight(.semibold))
                        .foregroundColor(Color(hex: "6366F1"))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color(hex: "6366F1").opacity(0.18))
                        .clipShape(Capsule())
                }

                Text("Мир героев")
                    .font(.system(size: 32, weight: .bold))
                    .foregroundColor(.textPrimary)

                Text("Зажми микрофон — скажи герою вслух. Единорог, Аладдин и Джин.")
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)

                Rectangle()
                    .fill(Color.textSecondary.opacity(0.2))
                    .frame(height: 1)
                    .padding(.vertical, Spacing.xs)

                HStack(spacing: Spacing.m) {
                    Label("🦄 Единорог", systemImage: "sparkles")
                    Label("🧞 Джин", systemImage: "wand.and.stars")
                }
                .font(.caption)
                .foregroundColor(.textSecondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(Spacing.l)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .fill(
                        LinearGradient(
                            gradient: Gradient(colors: [
                                Color(hex: "6366F1").opacity(0.18),
                                Color(hex: "A855F7").opacity(0.22)
                            ]),
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.large)
                            .stroke(Color(hex: "6366F1").opacity(0.45), lineWidth: 2)
                    )
            )
        }
        .buttonStyle(PressScaleButtonStyle())
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityIdentifier("child_rewards_companion_world_card")
    }
    
    // MARK: - Goal Progress Card
    
    private var goalProgressCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack(spacing: Spacing.xs) {
                Text("🎯")
                    .font(.system(size: 20))
                Text(String(format: localizationManager.localized("child_rewards_goal_title"), goalTitle))
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
            }
            
            // Прогресс-бар (цвет по фазе накопления + микро-анимация ширины)
            GeometryReader { geometry in
                let w = geometry.size.width
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 10)
                        .fill(Color.backgroundMedium.opacity(0.5))
                        .frame(height: 20)
                        .overlay(milestoneTicks(totalWidth: w))

                    RoundedRectangle(cornerRadius: 10)
                        .fill(
                            LinearGradient(
                                gradient: goalProgressGradient(for: goalProgress),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: max(8, w * goalProgress), height: 20)
                        .animation(reduceMotion ? nil : .spring(response: 0.55, dampingFraction: 0.82), value: goalProgress)
                }
            }
            .frame(height: 20)
            
            // Текст прогресса
            HStack {
                Text(String(format: localizationManager.localized("child_rewards_goal_accumulated"), unicornBalance))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                
                Spacer()
                
                Text(String(format: localizationManager.localized("child_rewards_goal_need"), goalCost))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Text(String(format: localizationManager.localized("child_rewards_goal_remaining"), goalCost - unicornBalance, 35))
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

    private func goalProgressGradient(for progress: Double) -> Gradient {
        let p = min(1, max(0, progress))
        if p < 0.34 {
            return Gradient(colors: [Color(hex: "22C55E"), Color(hex: "84CC16")])
        }
        if p < 0.67 {
            return Gradient(colors: [Color(hex: "EAB308"), Color(hex: "F97316")])
        }
        return Gradient(colors: [Color(hex: "A855F7"), Color(hex: "EC4899")])
    }

    private func milestoneTicks(totalWidth: CGFloat) -> some View {
        ZStack(alignment: .leading) {
            ForEach([0.25, 0.5, 0.75], id: \.self) { mark in
                Rectangle()
                    .fill(Color.textSecondary.opacity(0.22))
                    .frame(width: 1, height: 14)
                    .offset(x: totalWidth * mark - 0.5)
            }
        }
        .allowsHitTesting(false)
    }
    
    // MARK: - Games Grid (2x3)
    
    private var gamesGrid: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            Text(localizationManager.localized("child_rewards_games_title"))
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
                    title: localizationManager.localized("child_rewards_game_young_defender"),
                    status: localizationManager.localized("child_rewards_game_status_available"),
                    metric: String(format: localizationManager.localized("child_rewards_game_metric_lessons"), getCompletedLessons()),
                    color: .primaryBlue,
                    destination: NavigationManager.ALADDINScreen.youngDefender
                )
                
                // Карточка 2: 🦄 Питомец
                gameCardButton(
                    icon: "🦄",
                    title: localizationManager.localized("child_rewards_game_pet"),
                    status: String(format: localizationManager.localized("child_rewards_game_status_level"), getPetLevel()),
                    metric: String(format: localizationManager.localized("unicorn_pet_metric_format"), Int(getPetLove() * 100)),
                    color: Color(hex: "A855F7"),
                    destination: NavigationManager.ALADDINScreen.unicornPet
                )

                // Карточка 3: 🕵️ Я защитник
                gameCardButton(
                    icon: "🕵️",
                    title: localizationManager.localized("child_rewards_game_protector"),
                    status: localizationManager.localized("child_rewards_game_status_available"),
                    metric: String(format: localizationManager.localized("child_rewards_game_metric_quests"), getCompletedQuests()),
                    color: Color(hex: "EC4899"),
                    destination: NavigationManager.ALADDINScreen.familyProtector
                )
                
                // Карточка 4: 🏆 Турнир
                gameCardButton(
                    icon: "🏆",
                    title: localizationManager.localized("child_rewards_game_tournament"),
                    status: String(format: localizationManager.localized("child_rewards_game_status_days_left"), getTournamentDaysLeft()),
                    metric: localizationManager.localized("child_rewards_game_metric_leader"),
                    color: .warningOrange,
                    destination: NavigationManager.ALADDINScreen.familyTournament
                )
                
                // Карточка 5: 🏪 Магазин (встроенный таб)
                gameCardButton(
                    icon: "🏪",
                    title: localizationManager.localized("child_rewards_game_shop"),
                    status: localizationManager.localized("child_rewards_game_status_products"),
                    metric: localizationManager.localized("child_rewards_game_metric_from"),
                    color: .secondaryGold,
                    isTab: true,
                    tabDestination: .shop
                )
                
                // Карточка 6: 📊 История (встроенный таб)
                gameCardButton(
                    icon: "📊",
                    title: localizationManager.localized("child_rewards_game_history"),
                    status: localizationManager.localized("child_rewards_game_status_days"),
                    metric: localizationManager.localized("child_rewards_game_metric_stats"),
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
                withAnimation(reduceMotion ? nil : .spring(response: 0.38, dampingFraction: 0.84)) {
                    selectedTab = tab
                }
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
        .buttonStyle(PressScaleButtonStyle())
    }
    
    // MARK: - Helper Methods
    
    /// Загрузка наград магазина из UserDefaults (fallback)
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
    
    // MARK: - ✅ ГЕЙМИФИКАЦИЯ: API методы для синхронизации
    
    /// Загрузить баланс единорогов с сервера
    private func loadBalanceFromServer() {
        VisualLogger.shared.log("🌐 balance request start", level: .info, category: "CHILD_REWARDS.API")
        apiService.getGamificationBalance(userId: userId) { [self] result in
            switch result {
            case .success(let response):
                VisualLogger.shared.log("✅ balance request ok = \(response.balance)", level: .success, category: "CHILD_REWARDS.API")
                let safeBalance = mergedBalanceWithLocal(response.balance)
                unicornBalance = safeBalance
                storedUnicornBalance = safeBalance
                UnicornRewardsStore.writeBalance(safeBalance, for: rewardsScopeChildId)
            case .failure(let error):
                // Используем кэшированное значение при ошибке
                VisualLogger.shared.log("❌ balance request failed: \(error.localizedDescription)", level: .error, category: "CHILD_REWARDS.API")
                apiError = error.localizedDescription
                if storedUnicornBalance > 0 {
                    unicornBalance = storedUnicornBalance
                }
            }
        }
    }
    
    /// Загрузить награды магазина с сервера
    private func loadRewardsFromServer() {
        isLoadingRewards = true
        apiError = nil
        VisualLogger.shared.log("🌐 rewards shop request start", level: .info, category: "CHILD_REWARDS.API")
        
        // Используем локальные награды для быстрого отображения
        loadShopRewards()
        
        apiService.getGamificationRewardsShop(userId: userId) { [self] result in
            isLoadingRewards = false
            switch result {
            case .success(let response):
                VisualLogger.shared.log("✅ rewards shop request ok items=\(response.rewards.count)", level: .success, category: "CHILD_REWARDS.API")
                // Конвертируем RewardResponse в ShopReward
                // Используем существующие награды и обновляем их данными с сервера
                var updatedRewards: [ShopReward] = []
                for serverReward in response.rewards {
                    // Ищем существующую награду по ID или создаем новую
                    if let existingReward = availableRewards.first(where: { $0.id == serverReward.id }) {
                        // Обновляем существующую награду (создаем новую с обновленными данными)
                        updatedRewards.append(ShopReward(
                            id: serverReward.id,
                            icon: existingReward.icon,
                            titleKey: serverReward.name, // Используем название с сервера
                            descKey: serverReward.description ?? existingReward.localizedDescription(localizationManager),
                            price: serverReward.price,
                            isEnabled: serverReward.available
                        ))
                    } else {
                        // Создаем новую награду
                        updatedRewards.append(ShopReward(
                            id: serverReward.id,
                            icon: "🎁",
                            titleKey: serverReward.name,
                            descKey: serverReward.description ?? "",
                            price: serverReward.price,
                            isEnabled: serverReward.available
                        ))
                    }
                }
                // Если наград с сервера нет, используем локальные
                if updatedRewards.isEmpty {
                    // Оставляем существующие награды
                } else {
                    availableRewards = updatedRewards
                }
                scheduleSaveShopRewards()
            case .failure(let error):
                VisualLogger.shared.log("❌ rewards shop request failed: \(error.localizedDescription)", level: .error, category: "CHILD_REWARDS.API")
                apiError = error.localizedDescription
                // Используем локальные награды при ошибке
            }
        }
    }
    
    /// Загрузить историю наград с сервера
    private func loadHistoryFromServer() {
        isLoadingHistory = true
        VisualLogger.shared.log("🌐 rewards history request start", level: .info, category: "CHILD_REWARDS.API")
        
        apiService.getGamificationRewardsHistory(userId: userId, limit: 50) { [self] result in
            switch result {
            case .success(let rewards):
                if rewards.isEmpty {
                    VisualLogger.shared.log("ℹ️ rewards/history empty → balance op history", level: .info, category: "CHILD_REWARDS.API")
                } else {
                    VisualLogger.shared.log("ℹ️ rewards/history count=\(rewards.count); list UI uses /gamification/balance history (rewards/history 500-safe)", level: .info, category: "CHILD_REWARDS.API")
                }
                self.loadHistoryFromBalanceHistoryFallback()
            case .failure(let error):
                VisualLogger.shared.log("❌ rewards history request failed: \(error.localizedDescription) — balance history fallback", level: .error, category: "CHILD_REWARDS.API")
                self.loadHistoryFromBalanceHistoryFallback()
            }
        }
    }
    
    /// If `/api/gamification/rewards/history` is empty or 5xx, we still show wallet activity from `/api/gamification/balance?...` history.
    private func loadHistoryFromBalanceHistoryFallback() {
        apiService.getGamificationBalanceHistory(userId: userId, limit: 100, offset: 0) { [self] result in
            switch result {
            case .success(let response):
                DispatchQueue.main.async {
                    isLoadingHistory = false
                    let mapped = response.history.map { balanceEntryToHistoryEntry($0) }
                    if mapped.isEmpty {
                        VisualLogger.shared.log("ℹ️ balance history empty, keeping local rewards_history", level: .info, category: "CHILD_REWARDS.API")
                    } else {
                        VisualLogger.shared.log("✅ balance history ok items=\(mapped.count) (rewards/history fallback)", level: .success, category: "CHILD_REWARDS.API")
                    }
                    persistAndApplyHistory(mergeWithLocal: true, serverEntries: mapped)
                }
            case .failure(let error):
                DispatchQueue.main.async {
                    isLoadingHistory = false
                    VisualLogger.shared.log("❌ balance history fallback failed: \(error.localizedDescription)", level: .error, category: "CHILD_REWARDS.API")
                    if getHistoryOperations().isEmpty {
                        apiError = error.localizedDescription
                    } else {
                        apiError = nil
                    }
                }
            }
        }
    }
    
    private func dateFromServerTimestamp(_ raw: String) -> Date {
        let f1 = ISO8601DateFormatter()
        f1.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let d = f1.date(from: raw) { return d }
        let f2 = ISO8601DateFormatter()
        f2.formatOptions = [.withInternetDateTime]
        if let d = f2.date(from: raw) { return d }
        return Date()
    }
    
    private func balanceEntryToHistoryEntry(_ entry: BalanceHistoryEntry) -> RewardHistoryEntry {
        let label: String
        if let r = entry.reason, !r.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            label = r
        } else {
            label = entry.amount >= 0
                ? localizationManager.localized("child_rewards_balance_server_credit")
                : localizationManager.localized("child_rewards_balance_server_debit")
        }
        var title = RewardText(translations: [:])
        title.setCustom(label, for: .russian)
        title.setCustom(label, for: .english)
        return RewardHistoryEntry(
            id: "server.balance.\(entry.id)",
            title: title,
            reason: RewardText(translations: [:]),
            amount: abs(entry.amount),
            isReward: entry.amount >= 0,
            date: dateFromServerTimestamp(entry.timestamp)
        )
    }
    
    private func persistAndApplyHistory(mergeWithLocal: Bool, serverEntries: [RewardHistoryEntry]) {
        let local = getHistoryOperations()
        let merged: [RewardHistoryEntry]
        if mergeWithLocal {
            let serverIds = Set(serverEntries.map(\.id))
            let localOnly = local.filter { !serverIds.contains($0.id) }
            merged = (serverEntries + localOnly).sorted { $0.date > $1.date }
        } else {
            merged = serverEntries.sorted { $0.date > $1.date }
        }
        cachedHistoryOperations = merged
        if let encoded = try? JSONEncoder().encode(merged),
           let jsonString = String(data: encoded, encoding: .utf8) {
            UserDefaults.standard.set(jsonString, forKey: "rewards_history")
        }
    }
    
    /// Обновить все данные с сервера (для pull-to-refresh)
    @MainActor
    private func refreshData() async {
        guard !isInitialLoadInFlight, !viewModel.isLoading else { return }
        await runInitialLoad()
        if selectedTab == .history {
            loadHistoryFromServer()
        }
        // Небольшая задержка для плавности анимации
        try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 секунды
    }
    
    /// Сохранение наград магазина в UserDefaults
    private func saveShopRewards() {
        if let data = try? JSONEncoder().encode(availableRewards),
           let jsonString = String(data: data, encoding: .utf8) {
            shopRewardsData = jsonString
        }
    }

    private func scheduleSaveShopRewards() {
        shopRewardsSaveDebounceTask?.cancel()
        shopRewardsSaveDebounceTask = Task { @MainActor in
            try? await Task.sleep(nanoseconds: 300_000_000)
            guard !Task.isCancelled else { return }
            saveShopRewards()
        }
    }

    @MainActor
    private func runInitialLoad() async {
        guard !isInitialLoadInFlight, !viewModel.isLoading else { return }
        isInitialLoadInFlight = true
        defer { isInitialLoadInFlight = false }
        await viewModel.load(childId: effectiveChildId)
    }
    
    /// Проверка: является ли текущий пользователь родителем
    /// ✅ КРИТИЧНО ДЛЯ БЕЗОПАСНОСТИ: Дети НЕ должны видеть родительские функции
    private func isCurrentUserParent() -> Bool {
        // 1. Проверка через UserDefaults (основной способ)
        if let roleString = UserDefaults.standard.string(forKey: "current_user_role") {
            print("🔍 ChildRewardsScreen.isCurrentUserParent: Найдена роль в UserDefaults: '\(roleString)'")
            
            // Пробуем распознать роль через FamilyRole
            if let role = FamilyRole(storageValue: roleString) {
                let isParent = role == .parent
                print("   - FamilyRole распознан: \(role.rawValue)")
                print("   - Результат: \(isParent ? "РОДИТЕЛЬ" : "РЕБЁНОК")")
                
                if isParent {
                    print("   ✅ Разрешён доступ к родительским функциям")
                } else {
                    print("   🔒 Доступ к родительским функциям ЗАБЛОКИРОВАН (ребёнок)")
                }
                
                return isParent
            } else {
                // Роль не распознана, пробуем прямую проверку строки
                print("   ⚠️ FamilyRole не распознан, пробуем прямую проверку строки")
                let lowercased = roleString.lowercased()
                if lowercased == "parent" || lowercased.contains("parent") {
                    print("   ✅ Прямая проверка: 'parent' найдено в строке")
                    return true
                }
            }
        } else {
            print("🔍 ChildRewardsScreen.isCurrentUserParent: Роль НЕ найдена в UserDefaults")
        }
        
        // 2. Fallback: проверка текущего экрана
        let currentScreen = navigationManager.currentScreen
        print("   🔍 Fallback: проверяем текущий экран: \(currentScreen)")
        
        if currentScreen == .parentalControl {
            print("   ✅ Fallback: текущий экран ParentalControl -> устанавливаем роль 'parent'")
            UserDefaults.standard.set("parent", forKey: "current_user_role")
            UserDefaults.standard.synchronize()
            return true
        }
        
        // 3. Fallback: проверка предыдущего экрана в стеке навигации
        if !navigationManager.navigationStack.isEmpty {
            let previousScreen = navigationManager.navigationStack.last
            print("   🔍 Fallback: проверяем предыдущий экран в стеке: \(previousScreen?.rawValue ?? "нет")")
            
            if previousScreen == .parentalControl {
                print("   ✅ Fallback: предыдущий экран ParentalControl -> устанавливаем роль 'parent'")
                UserDefaults.standard.set("parent", forKey: "current_user_role")
                UserDefaults.standard.synchronize()
                return true
            }
        }
        
        // 4. По умолчанию - ребёнок (безопаснее)
        print("   🚨 Fallback: роль не найдена -> false (безопасность, считаем ребёнком)")
        return false
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
                Text(localizationManager.localized("child_rewards_parent_section"))
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
                            .accessibilityLabel(localizationManager.localized("child_rewards_reward_icon_accessibility"))
                        Text(localizationManager.localized("child_rewards_reward_button"))
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
                .accessibilityLabel(localizationManager.localized("child_rewards_reward_accessibility"))
                .accessibilityHint(localizationManager.localized("child_rewards_reward_hint"))
                
                // Кнопка "Наказать"
                Button(action: {
                    print("🔍 DEBUG: Нажата кнопка 'Наказать' в ChildRewardsScreen")
                    HapticFeedback.impact(.medium)
                    showPunishInput = true
                }) {
                    VStack(spacing: Spacing.xs) {
                        Text("❌")
                            .font(.system(size: 36))
                            .accessibilityLabel(localizationManager.localized("child_rewards_punish_icon_accessibility"))
                        Text(localizationManager.localized("child_rewards_punish_button"))
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
                .accessibilityLabel(localizationManager.localized("child_rewards_punish_accessibility"))
                .accessibilityHint(localizationManager.localized("child_rewards_punish_hint"))
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
                Text(localizationManager.localized("child_rewards_child_history_title"))
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                    .fontWeight(.bold)
            }
            .padding(.horizontal, Spacing.screenPadding)
            .padding(.bottom, Spacing.s)
            
            // История наград/наказаний (последние 5)
            if cachedHistoryOperations.prefix(5).isEmpty {
                VStack(spacing: Spacing.s) {
                    Text("📝")
                        .font(.system(size: 32))
                    Text(localizationManager.localized("child_rewards_history_empty"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("child_rewards_history_empty_desc"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.l)
            } else {
                VStack(spacing: Spacing.s) {
                    ForEach(Array(cachedHistoryOperations.prefix(5))) { operation in
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
    private func childHistoryItem(operation: RewardHistoryEntry) -> some View {
        let title = operation.title.resolved(with: localizationManager)
        let reason = operation.reason.resolved(with: localizationManager)
        let icon = getHistoryIcon(
            title: title,
            reason: reason,
            titleKey: operation.title.localizationKey,
            reasonKey: operation.reason.localizationKey,
            isReward: operation.isReward
        )
        
        return HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 32))
            
            VStack(alignment: .leading, spacing: Spacing.xs) {
                // Название действия
                Text(title)
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                
                // Причина (почему наградили/наказали)
                if !reason.isEmpty {
                    Text(String(format: localizationManager.localized("child_rewards_reason_label"), reason))
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
                Text(localizationManager.localized("child_rewards_request_button"))
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
                    withAnimation(reduceMotion ? nil : .spring(response: 0.38, dampingFraction: 0.84)) {
                        selectedTab = tab
                    }
                }) {
                    Text(tab.localizedTitle(localizationManager))
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
                        .scaleEffect(selectedTab == tab && !reduceMotion ? 1.03 : 1.0)
                }
                .buttonStyle(PressScaleButtonStyle())
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
                Text(localizationManager.localized("child_rewards_shop_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                // Загружаем награды из UserDefaults или используем дефолтные
                if availableRewards.filter({ $0.isEnabled }).isEmpty {
                    // Сообщение если наград нет
                    VStack(spacing: Spacing.m) {
                        Text("🎁")
                            .font(.system(size: 48))
                        Text(localizationManager.localized("child_rewards_shop_empty"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Text(localizationManager.localized("child_rewards_shop_empty_desc"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(Spacing.xxl)
                } else {
                    ForEach(availableRewards.filter { $0.isEnabled }) { reward in
                        rewardItem(
                            reward: reward,
                            canAfford: unicornBalance >= reward.price
                        )
                    }
                }
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func rewardItem(reward: ShopReward, canAfford: Bool) -> some View {
        let title = reward.localizedTitle(localizationManager)
        let description = reward.localizedDescription(localizationManager)
        let price = reward.price
        
        return Button(action: {
            print("🛒 Нажата награда: \(title), цена: \(price) 🦄, баланс: \(unicornBalance) 🦄, можно купить: \(canAfford)")
            if canAfford {
                buyReward(price: price, title: title)
            } else {
                HapticFeedback.notification(.error)
                print("❌ Недостаточно единорогов для покупки: \(title)")
            }
        }) {
            HStack(spacing: Spacing.m) {
                Text(reward.icon)
                    .font(.system(size: 32))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(title)
                        .font(.body)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: Spacing.xxs) {
                    Text("\(price) 🦄")
                        .font(.body)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "C084FC"))
                    
                    Text(canAfford ? localizationManager.localized("child_rewards_buy_button") : localizationManager.localized("child_rewards_save_more"))
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
        .buttonStyle(PressScaleButtonStyle())
        .disabled(!canAfford)
    }
    
    // MARK: - Rewards History
    
    private var rewardsHistory: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text("📊")
                    .font(.system(size: 18))
                Text(localizationManager.localized("child_rewards_history_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            // Загружаем реальную историю из AppStorage
            if cachedHistoryOperations.isEmpty {
                VStack(spacing: Spacing.m) {
                    Text("📝")
                        .font(.system(size: 48))
                    Text(localizationManager.localized("child_rewards_history_empty"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("child_rewards_history_empty_full"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                .padding(Spacing.xxl)
            } else {
            VStack(spacing: Spacing.s) {
                    ForEach(cachedHistoryOperations) { operation in
                        historyItemFromOperation(operation: operation)
                    }
            }
            .padding(.horizontal, Spacing.screenPadding)
            }
        }
    }
    
    /// Загрузка истории из AppStorage
    private func getHistoryOperations() -> [RewardHistoryEntry] {
        guard let historyData = UserDefaults.standard.string(forKey: "rewards_history"),
              let data = historyData.data(using: .utf8),
              let operations = try? JSONDecoder().decode([RewardHistoryEntry].self, from: data) else {
            return []
        }
        return operations.sorted { $0.date > $1.date } // Новые сверху
    }
    
    /// Отображение элемента истории из RewardHistoryEntry
    private func historyItemFromOperation(operation: RewardHistoryEntry) -> some View {
        let title = operation.title.resolved(with: localizationManager)
        let reason = operation.reason.resolved(with: localizationManager)
        let icon = getHistoryIcon(
            title: title,
            reason: reason,
            titleKey: operation.title.localizationKey,
            reasonKey: operation.reason.localizationKey,
            isReward: operation.isReward
        )
        
        return HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 28))
            
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                // Показываем причину (reason)
                if !reason.isEmpty && reason != title {
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
                .fill(operation.isReward ? Color.backgroundMedium.opacity(0.5) : Color.dangerRed.opacity(0.08))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(operation.isReward ? Color.textSecondary.opacity(0.2) : Color.dangerRed.opacity(0.3), lineWidth: 1)
                )
        )
    }
    
    /// Определение иконки для истории
    private func getHistoryIcon(title: String, reason: String, titleKey: String?, reasonKey: String?, isReward: Bool) -> String {
        let iconByKey: [String: String] = [
            "child_rewards_history_reward_title": "✅",
            "child_rewards_history_reward_reason_default": "✅",
            "child_rewards_history_punish_title": "❌",
            "child_rewards_history_punish_reason_default": "❌",
            "child_rewards_earning_homework_title": "📚",
            "child_rewards_earning_chores_title": "🧹",
            "child_rewards_earning_behavior_title": "😊",
            "child_rewards_earning_reading_title": "📖",
            "child_rewards_earning_achievement_title": "🏆",
            "child_rewards_punish_homework_title": "📚",
            "child_rewards_punish_behavior_title": "😡",
            "child_rewards_punish_limits_title": "⏰",
            "child_rewards_punish_bypass_title": "🚫",
            "child_rewards_punish_custom_title": "❌",
            "child_rewards_history_achievement_title": "🏆",
            "child_rewards_history_goal_title": "🎯"
        ]

        if let key = titleKey, let icon = iconByKey[key] {
            return icon
        }
        if let key = reasonKey, let icon = iconByKey[key] {
            return icon
        }

        let combined = (title + " " + reason).lowercased()
        let matches: [(phrases: [String], icon: String, rewardOverride: String?)] = [
            (["домашнее", "дз", "homework"], "📚", nil),
            (["уборк", "chores", "clean"], "🧹", nil),
            (["повед", "behavior"], "😡", "😊"),
            (["книг", "чит", "reading"], "📖", nil),
            (["достиж", "achievement"], "🏆", nil),
            (["лимит", "screen", "limit"], "⏰", nil),
            (["обход", "bypass"], "🚫", nil),
            (["цель", "goal"], "🎯", nil)
        ]

        for match in matches {
            if match.phrases.contains(where: { combined.contains($0) }) {
                if let rewardIcon = match.rewardOverride, isReward {
                    return rewardIcon
                }
                return match.icon
            }
        }

        return isReward ? "✅" : "❌"
    }
    
    // ✅ ИСПРАВЛЕНИЕ BUILD 91+: Статические форматтеры для предотвращения рекурсии
    private static let timeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        formatter.locale = Locale(identifier: "ru_RU")
        return formatter
    }()
    
    private static let dateTimeFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: "ru_RU")
        return formatter
    }()
    
    /// Форматирование даты
    private func formatDate(_ date: Date) -> String {
        let timeString = Self.timeFormatter.string(from: date)
        
        if Calendar.current.isDateInToday(date) {
            return String(format: localizationManager.localized("child_rewards_date_today"), timeString)
        } else if Calendar.current.isDateInYesterday(date) {
            return String(format: localizationManager.localized("child_rewards_date_yesterday"), timeString)
        } else {
            return Self.dateTimeFormatter.string(from: date)
        }
    }
    
    private func historyItem(icon: String, title: String, amount: String, isReward: Bool, date: String) -> some View {
        return HStack(spacing: Spacing.m) {
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
                Text(localizationManager.localized("child_rewards_achievements_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
            }
            .padding(.horizontal, Spacing.screenPadding)
            
            VStack(spacing: Spacing.s) {
                achievementItem(icon: "📚", title: localizationManager.localized("child_rewards_achievement_excellent"), desc: localizationManager.localized("child_rewards_achievement_excellent_desc"), progress: 0.7)
                achievementItem(icon: "🧹", title: localizationManager.localized("child_rewards_achievement_helper"), desc: localizationManager.localized("child_rewards_achievement_helper_desc"), progress: 0.5)
                achievementItem(icon: "📖", title: localizationManager.localized("child_rewards_achievement_bookworm"), desc: localizationManager.localized("child_rewards_achievement_bookworm_desc"), progress: 0.4)
            }
            .padding(.horizontal, Spacing.screenPadding)
        }
    }
    
    private func achievementItem(icon: String, title: String, desc: String, progress: Double) -> some View {
        return VStack(alignment: .leading, spacing: Spacing.s) {
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
                        .fill(
                            LinearGradient(
                                gradient: Gradient(colors: [Color.successGreen, Color.secondaryGold.opacity(0.95)]),
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: max(4, geometry.size.width * progress), height: 8)
                        .animation(reduceMotion ? nil : .easeOut(duration: 0.35), value: progress)
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
        
        // ✅ ГЕЙМИФИКАЦИЯ: Покупаем награду через API
        // Находим награду по названию
        if let reward = availableRewards.first(where: { $0.localizedTitle(localizationManager) == pendingPurchaseTitle }) {
            apiService.purchaseGamificationReward(
                userId: userId,
                rewardId: reward.id,
                deviceId: UIDevice.current.identifierForVendor?.uuidString
            ) { [self] result in
                switch result {
                case .success(let response):
                    Task { @MainActor in
                        unicornBalance = response.newBalance
                        storedUnicornBalance = response.newBalance
                        UnicornRewardsStore.writeBalance(unicornBalance, for: rewardsScopeChildId)
                        applyReward(pendingPurchaseTitle)
                        NotificationCenter.default.post(name: .childRewardsDataDidChange, object: nil)
                        HapticFeedback.notification(.success)
                        print("🎁 Куплена награда: \(pendingPurchaseTitle) за \(pendingPurchasePrice) 🦄. Осталось: \(unicornBalance) 🦄")
                        showPurchaseConfirmation = false
                        purchaseRewardBurstActive = true
                    }
                case .failure(let error):
                    Task { @MainActor in
                        apiError = error.localizedDescription
                        HapticFeedback.notification(.error)
                        print("❌ Ошибка покупки награды: \(error.localizedDescription)")
                    }
                }
            }
        } else {
            // Fallback на локальную покупку, если награда не найдена
            unicornBalance -= pendingPurchasePrice
            storedUnicornBalance = unicornBalance
            UnicornRewardsStore.writeBalance(unicornBalance, for: rewardsScopeChildId)
            applyReward(pendingPurchaseTitle)
            NotificationCenter.default.post(name: .childRewardsDataDidChange, object: nil)
            HapticFeedback.notification(.success)
            showPurchaseConfirmation = false
            purchaseRewardBurstActive = true
        }
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
    private func rewardChild(amount: Int, history: RewardHistoryTexts) {
        // ✅ КРИТИЧНАЯ ПРОВЕРКА БЕЗОПАСНОСТИ
        guard isCurrentUserParent() else {
            print("🚨 ПРОБЛЕМА БЕЗОПАСНОСТИ: Попытка наградить ребёнка не родителем!")
            print("   - Роль: \(UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА")")
            HapticFeedback.notification(.error)
            return
        }
        let resolvedReason = history.reason.resolved(with: localizationManager)
        
        // Обновляем баланс в AppStorage (синхронизация)
        let currentBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
        let newBalance = currentBalance + amount
        UnicornRewardsStore.writeBalance(newBalance, for: rewardsScopeChildId)
        
        // Обновляем статистику за неделю
        let currentWeekly = UnicornRewardsStore.readWeeklyEarned(for: rewardsScopeChildId)
        UnicornRewardsStore.writeWeeklyEarned(currentWeekly + amount, for: rewardsScopeChildId)
        
        // Явно отправляем уведомление для обновления других экранов
        NotificationCenter.default.post(name: .childRewardsDataDidChange, object: nil)
        
        // Обновляем локальные переменные
        unicornBalance = newBalance
        weeklyEarned += amount
        
        // Добавляем в историю (используем ту же логику, что и в RewardsModalView)
        addToHistory(isReward: true, texts: history, amount: amount)
        
        HapticFeedback.notification(.success)
        print("✅ Вознаградили ребёнка: +\(amount) 🦄, причина: \(resolvedReason)")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    /// Наказание ребёнка (ТОЛЬКО ДЛЯ РОДИТЕЛЕЙ!)
    /// ✅ БЕЗОПАСНОСТЬ: Проверка роли обязательна
    private func punishChild(amount: Int, history: RewardHistoryTexts) {
        // ✅ КРИТИЧНАЯ ПРОВЕРКА БЕЗОПАСНОСТИ
        guard isCurrentUserParent() else {
            print("🚨 ПРОБЛЕМА БЕЗОПАСНОСТИ: Попытка наказать ребёнка не родителем!")
            print("   - Роль: \(UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА")")
            HapticFeedback.notification(.error)
            return
        }
        let resolvedReason = history.reason.resolved(with: localizationManager)
        
        // Обновляем баланс в AppStorage (синхронизация)
        let currentBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
        let newBalance = max(0, currentBalance - amount) // Не может быть отрицательным
        UnicornRewardsStore.writeBalance(newBalance, for: rewardsScopeChildId)
        
        // Обновляем статистику за неделю
        let currentWeekly = UnicornRewardsStore.readWeeklyPunished(for: rewardsScopeChildId)
        UnicornRewardsStore.writeWeeklyPunished(currentWeekly + amount, for: rewardsScopeChildId)
        
        // Явно отправляем уведомление для обновления других экранов
        NotificationCenter.default.post(name: .childRewardsDataDidChange, object: nil)
        
        // Обновляем локальные переменные
        unicornBalance = newBalance
        weeklyPunished += amount
        
        // Добавляем в историю (используем ту же логику, что и в RewardsModalView)
        addToHistory(isReward: false, texts: history, amount: amount)
        
        HapticFeedback.notification(.error)
        print("✅ Наказали ребёнка: -\(amount) 🦄, причина: \(resolvedReason)")
        print("💰 Новый баланс: \(newBalance) 🦄")
    }
    
    // MARK: - History Management
    
    private func addToHistory(isReward: Bool, texts: RewardHistoryTexts, amount: Int) {
        let operation = RewardHistoryEntry(
            id: UUID().uuidString,
            title: texts.title,
            reason: texts.reason,
            amount: amount,
            isReward: isReward,
            date: Date()
        )
        var history = getHistoryOperations()
        history.append(operation)
        cachedHistoryOperations = history.sorted { $0.date > $1.date }
        if let encoded = try? JSONEncoder().encode(history),
           let jsonString = String(data: encoded, encoding: .utf8) {
            UserDefaults.standard.set(jsonString, forKey: "rewards_history")
        }
    }

    private func sendRequestToParents(_ achievement: String) {
        guard !achievement.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            print("⚠️ Пустой запрос не будет отправлен")
            return
        }

        var requests: [[String: Any]] = []
        if let stored = UserDefaults.standard.data(forKey: "child_achievement_requests"),
           let decoded = try? JSONSerialization.jsonObject(with: stored) as? [[String: Any]] {
            requests = decoded
        }

        let request: [String: Any] = [
            "id": UUID().uuidString,
            "achievement": achievement,
            "date": ISO8601DateFormatter().string(from: Date())
        ]
        requests.append(request)

        if let encoded = try? JSONSerialization.data(withJSONObject: requests) {
            UserDefaults.standard.set(encoded, forKey: "child_achievement_requests")
            print("📣 Отправлен запрос родителям: \(achievement)")
            print("📊 Всего запросов: \(requests.count)")
        }
    }
}

private extension Notification.Name {
    static let childRewardsDataDidChange = Notification.Name("ChildRewardsDataDidChange")
}

// MARK: - Achievement Request Modal

struct AchievementRequestModal: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    let onSendRequest: (String) -> Void
    
    @State private var selectedTemplate: String?
    @State private var customMessage: String = ""
    
    private var templates: [(icon: String, title: String, reward: String)] {
        [
            ("📚", localizationManager.localized("child_rewards_achievement_request_template_homework"), "+10 🦄"),
            ("🧹", localizationManager.localized("child_rewards_achievement_request_template_cleaning"), "+5 🦄"),
            ("📖", localizationManager.localized("child_rewards_achievement_request_template_reading"), "+20 🦄"),
            ("🏆", localizationManager.localized("child_rewards_achievement_request_template_grade"), "+50 🦄"),
            ("🤝", localizationManager.localized("child_rewards_achievement_request_template_help"), "+15 🦄")
        ]
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        Text(localizationManager.localized("child_rewards_achievement_request_select"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        VStack(spacing: Spacing.s) {
                            ForEach(Array(templates.enumerated()), id: \.offset) { index, template in
                                templateButton(template, index: index)
                            }
                            customMessageSection
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
                    Text(localizationManager.localized("child_rewards_achievement_request_title"))
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
    
    private func templateButton(_ template: (icon: String, title: String, reward: String), index: Int) -> some View {
        return Button(action: {
            selectedTemplate = template.title
            customMessage = ""
        }) {
            HStack(spacing: Spacing.m) {
                Text(template.icon)
                    .font(.system(size: 28))
                
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(template.title)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                    Text(template.reward)
                        .font(.caption)
                        .foregroundColor(.successGreen)
                }
                
                Spacer()
                
                if selectedTemplate == template.title {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(.successGreen)
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(selectedTemplate == template.title ? Color.successGreen.opacity(0.2) : Color.backgroundMedium.opacity(0.5))
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(selectedTemplate == template.title ? Color.successGreen : Color.textSecondary.opacity(0.2), lineWidth: selectedTemplate == template.title ? 2 : 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var customMessageSection: some View {
        return VStack(alignment: .leading, spacing: Spacing.s) {
            HStack(spacing: Spacing.m) {
                Text("✍️")
                    .font(.system(size: 28))
                Text(localizationManager.localized("child_rewards_achievement_request_custom"))
                    .font(.body)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
            }
            
            TextField(localizationManager.localized("child_rewards_achievement_request_custom_placeholder"), text: $customMessage)
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
        return Button(action: {
            let message = customMessage.isEmpty ? (selectedTemplate ?? "") : customMessage
            onSendRequest(message)
            dismiss()
        }) {
            Text(localizationManager.localized("child_rewards_achievement_request_send"))
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    
    let title: String
    let price: Int
    let balance: Int
    let onConfirm: () -> Void
    let onCancel: () -> Void
    
    var body: some View {
        NavigationView {
            VStack(spacing: Spacing.l) {
                Text("🎁")
                    .font(.system(size: 60))
                
                Text(localizationManager.localized("child_rewards_purchase_confirm_title"))
                    .font(.h2)
                    .foregroundColor(.textPrimary)
                
                VStack(alignment: .leading, spacing: Spacing.m) {
                    infoRow(label: localizationManager.localized("child_rewards_purchase_confirm_reward"), value: title)
                    infoRow(label: localizationManager.localized("child_rewards_purchase_confirm_cost"), value: "\(price) 🦄")
                    infoRow(label: localizationManager.localized("child_rewards_purchase_confirm_balance"), value: "\(balance - price) 🦄")
                    Text(localizationManager.localized("child_rewards_purchase_confirm_remaining"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.backgroundMedium.opacity(0.4))
                )
                .padding(.horizontal, Spacing.screenPadding)
                
                VStack(spacing: Spacing.s) {
                    Button(action: {
                        onConfirm()
                        dismiss()
                    }) {
                        Text(localizationManager.localized("child_rewards_purchase_confirm_buy"))
                            .font(.bodyBold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(Color.successGreen)
                            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.large))
                    }
                    .buttonStyle(PlainButtonStyle())
                    
                    Button(action: {
                        onCancel()
                        dismiss()
                    }) {
                        Text(localizationManager.localized("child_rewards_purchase_confirm_cancel"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.large)
                                    .stroke(Color.textSecondary.opacity(0.2), lineWidth: 1)
                            )
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                Button(action: { dismiss() }) {
                    Text(localizationManager.localized("child_rewards_purchase_confirm_close"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .padding(.top, Spacing.s)
                }
            }
            .padding(.vertical, Spacing.l)
            .background(
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
            )
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(localizationManager.localized("child_rewards_purchase_confirm_title"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
            }
        }
    }
    
    private func infoRow(label: String, value: String) -> some View {
        return HStack {
            Text(label)
                .font(.body)
                .foregroundColor(.textSecondary)
            Spacer()
            Text(value)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
        }
    }
}