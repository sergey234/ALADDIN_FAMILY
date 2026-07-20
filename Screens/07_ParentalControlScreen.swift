import SwiftUI

/// 👶 Parental Control Screen - НОВЫЙ ДИЗАЙН С КАРТОЧКАМИ 2x3
/// Экран родительского контроля с системой вознаграждений единорогами 🦄
/// Источник дизайна: /mobile/wireframes/14_parental_control_screen.html
/// Стиль оформления: единообразие с Privacy/Terms (золотые акценты)
struct ParentalControlScreen: View {
    
    // MARK: - Dependencies
    
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    private let apiService = APIService.shared
    @ObservedObject private var manager = ParentalControlManager.shared
    @ObservedObject private var contentBlockerManager = ContentBlockerManager.shared
    @StateObject private var viewModel = ParentalControlViewModel()
    
    // Состояние для аккордеона "Защита детей"
    @State private var childProtectionExpanded = false
    
    // MARK: - Child Selection
    
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    @AppStorage("parental_selected_child_id") private var selectedChildId: String = ""
    @State private var children: [FamilyMemberResponse] = []
    @State private var isChildrenLoading: Bool = false
    @State private var childrenErrorMessage: String?
    @ObservedObject private var profileManager = ProfileManager.shared

    private var familyMembersForPolicy: [FamilyMemberData] {
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            return []
        }
        return decoded
    }

    private var canManageParentalControls: Bool {
        FamilyAccessPolicy.hasPermission(.manageParentalControls, members: familyMembersForPolicy)
    }

    private var canManageFamilyLimits: Bool {
        FamilyAccessPolicy.hasPermission(.manageFamilyLimits, members: familyMembersForPolicy)
    }

    private var canManageCriticalFamilySettings: Bool {
        FamilyAccessPolicy.hasPermission(.manageCriticalFamilySettings, members: familyMembersForPolicy)
    }

    private var profileBackedChildren: [FamilyMemberResponse] {
        profileManager.profiles.compactMap { profile in
            let sid = (profile.serverUserId ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
            guard !sid.isEmpty else { return nil }
            let role: String = {
                switch profile.ageGroup {
                case .teen14plus, .tween11to13: return "teenager"
                default: return "child"
                }
            }()
            return FamilyMemberResponse(
                id: sid,
                name: profile.displayName,
                role: role,
                avatar: profile.avatarKey,
                status: "protected",
                threatsBlocked: nil,
                lastActive: nil,
                devices: nil
            )
        }
    }

    private var childMembers: [FamilyMemberResponse] {
        let apiChildren = children.filter { member in
            let role = member.role.lowercased()
            return role == "child" || role == "teenager" || role == "teen"
        }
        if apiChildren.isEmpty {
            return profileBackedChildren
        }

        var merged = apiChildren
        let existing = Set(apiChildren.map(\.id))
        for profileChild in profileBackedChildren where !existing.contains(profileChild.id) {
            merged.append(profileChild)
        }
        return merged
    }
    
    private var currentChildDisplayName: String {
        if let child = childMembers.first(where: { $0.id == selectedChild }) {
            return child.name
        }
        return localizationManager.localized("parental_child_placeholder")
    }
    
    // MARK: - Loading State
    
    @State private var isStatsLoading: Bool = false
    @State private var statsErrorMessage: String?
    
    // MARK: - Control States
    // ✅ ИСПРАВЛЕНО: Заменено @State на @AppStorage для синхронизации с FamilyScreen
    
    @AppStorage("family_content_block_enabled") private var isContentBlockEnabled: Bool = true
    @AppStorage("family_time_control_enabled") private var isTimeControlEnabled: Bool = true
    @AppStorage("family_monitoring_enabled") private var isMonitoringEnabled: Bool = true
    @AppStorage("family_location_enabled") private var isLocationEnabled: Bool = true
    @AppStorage("family_reports_enabled") private var isReportsEnabled: Bool = true
    @AppStorage("family_additional_enabled") private var isAdditionalEnabled: Bool = true
    @AppStorage("family_bypass_protection_enabled") private var isBypassProtectionEnabled: Bool = true
    
    // MARK: - Modal Visibility
    
    @State private var showContentBlockModal: Bool = false
    @State private var showUnifiedTimeLimits: Bool = false
    @State private var showMonitoringModal: Bool = false
    @State private var showLocationModal: Bool = false
    @State private var showReportsModal: Bool = false
    @State private var showAdditionalModal: Bool = false
    @State private var showBypassProtectionModal: Bool = false
    @State private var showRewardsModal: Bool = false
    @State private var showParentDashboardModal: Bool = false
    @State private var elderlySyncReportBanner: String?
    
    // MARK: - Rewards Storage
    
    @AppStorage("child_unicorn_balance") private var unicornBalance: Int = 245
    @AppStorage("child_weekly_earned") private var weeklyRewarded: Int = 0
    @AppStorage("child_weekly_punished") private var weeklyPunished: Int = 0
    @State private var actualBalance: Int = 0

    private var rewardsScopeChildId: String? {
        let trimmed = selectedChildId.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty { return trimmed }
        return UnicornRewardsStore.resolveActiveChildId()
    }
    
    // MARK: - Card Metrics
    
    @State private var contentBlockActive: Int = 0
    @State private var contentBlockTotal: Int = 0
    @State private var contentBlockedCount: Int = 0
    
    @State private var timeRemaining: String = ""
    @State private var timeSchedules: Int = 0
    
    @State private var monitoringWebsites: Int = 0
    @State private var monitoringApps: Int = 0
    
    @State private var locationStatus: String = ""
    @State private var locationLastUpdate: String = ""
    @State private var locationWarnings: Int = 0
    
    @State private var reportsToday: Bool = true
    @State private var reportsAlerts: Int = 0
    
    @State private var additionalRequests: Int = 0
    @State private var additionalProtection: Bool = true
    
    // MARK: - Bypass Protection State
    
    @State private var bypassAttemptsToday: Int = 0
    @State private var bypassAttemptsWeek: Int = 0
    @State private var bypassAttemptsBlocked: Int = 0
    @State private var bypassDetectionActive: Int = 0
    
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон — Storm Mesh grow light (Batch 2, режим C)
            StormMeshBackground(variant: .grow)
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(localizationManager.localized("parental_accessibility_background"))
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Выбор ребёнка
                        childSelector

                        elderlySyncAuditBanner
                        
                        // Сетка карточек родительского контроля
                        parentalControlCards
                        
                        // ✅ НОВЫЙ РАЗДЕЛ: Защита детей (5 компонентов)
                        childProtectionSection
                        
                        // ✅ План 2026: Карта достижений (Недельный отчет)
                        achievementCard
                        
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
                .accessibilityLabel(localizationManager.localized("parental_accessibility_cards"))
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showContentBlockModal) {
            FamilyContentBlockModal(isPresented: $showContentBlockModal, isEnabled: $isContentBlockEnabled)
                .environmentObject(localizationManager)
        }
        .onAppear {
            // Загрузить статус Content Blocker при появлении экрана
            Task {
                await contentBlockerManager.checkBlockingStatus()
                contentBlockerManager.loadActiveCategories()
            }
        }
        .sheet(isPresented: $showUnifiedTimeLimits) {
            UnifiedTimeLimitsScreen()
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showMonitoringModal) {
            FamilyMonitoringModal(isPresented: $showMonitoringModal, isEnabled: $isMonitoringEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showLocationModal) {
            FamilyLocationModal(isPresented: $showLocationModal, isEnabled: $isLocationEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showReportsModal) {
            FamilyReportsModal(isPresented: $showReportsModal, isEnabled: $isReportsEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showAdditionalModal) {
            FamilyAdditionalModal(isPresented: $showAdditionalModal, isEnabled: $isAdditionalEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showBypassProtectionModal) {
            FamilyBypassProtectionModal(
                isPresented: $showBypassProtectionModal,
                isEnabled: $isBypassProtectionEnabled
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showRewardsModal) {
            RewardsModalView(
                unicornBalance: $unicornBalance,
                weeklyRewarded: $weeklyRewarded,
                weeklyPunished: $weeklyPunished
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showParentDashboardModal) {
            ParentDashboardView(isPresented: $showParentDashboardModal)
                .environmentObject(localizationManager)
        }
        .onAppear {
            // ✅ КРИТИЧНО: Устанавливаем роль родителя при входе в экран
            // ДОЛЖНО БЫТЬ В САМОМ НАЧАЛЕ .onAppear!
            UserDefaults.standard.set("parent", forKey: "current_user_role")
            UserDefaults.standard.synchronize() // Принудительная синхронизация
            
            print("✅ ParentalControlScreen: Роль установлена как 'parent'")
            print("   Проверка: UserDefaults['current_user_role'] = '\(UserDefaults.standard.string(forKey: "current_user_role") ?? "НЕ УСТАНОВЛЕНА")'")
            
            if locationStatus.isEmpty {
                locationStatus = localizationManager.localized("parental_location_home")
            }
            
            if timeRemaining.isEmpty {
                timeRemaining = localizationManager.localized("parental_time_remaining_default")
            }
            
            if locationLastUpdate.isEmpty {
                locationLastUpdate = localizationManager.localized("parental_location_last_update_default")
            }
            
            // Инициализация и синхронизация баланса
            actualBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
            if actualBalance == 0 && unicornBalance > 0 {
                actualBalance = unicornBalance
            }
            
            loadChildMembers()
            
            // ✅ РОДИТЕЛЬСКИЙ КОНТРОЛЬ: Синхронизация с сервером
            Task {
                await syncParentalControlData()
                manager.refreshFamilyControlsReadinessForCurrentDevice()
                refreshElderlySyncReport()
            }
        }
        .onChange(of: selectedChildId) { newId in
            let trimmed = newId.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !trimmed.isEmpty else { return }
            if selectedChild != trimmed {
                selectedChild = trimmed
            }
            UserDefaults.standard.set(trimmed, forKey: "active_child_profile_server_id")
            loadParentalControlData(for: trimmed)
        }
        .refreshable {
            await syncParentalControlData()
            manager.refreshFamilyControlsReadinessForCurrentDevice()
            refreshElderlySyncReport()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            let newBalance = UnicornRewardsStore.readBalance(for: rewardsScopeChildId)
            if newBalance != actualBalance {
                actualBalance = newBalance
                print("🔍 DEBUG: actualBalance обновлён до \(actualBalance)")
            }
        }
        .withVisualLogger()
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("parental_lang_\(localizationManager.currentLanguage.rawValue)")
    }

    @MainActor
    private func requireSensitiveParentSession(
        permission: FamilyAccessPolicy.Permission = .manageCriticalFamilySettings,
        deniedMessageRu: String = "Недостаточно прав для выполнения действия.",
        deniedMessageEn: String = "You don't have enough permissions to perform this action.",
        verifyFailedRu: String = "Подтверждение не выполнено. Действие отменено.",
        verifyFailedEn: String = "Verification was not completed. Action was cancelled.",
        action: @escaping () -> Void
    ) {
        guard FamilyAccessPolicy.hasPermission(permission, members: familyMembersForPolicy) else {
            statsErrorMessage = localizationManager.currentLanguage == .russian ? deniedMessageRu : deniedMessageEn
            HapticFeedback.notification(.warning)
            return
        }

        action()
    }

    @MainActor
    private func requestSensitiveToggleUpdate(
        _ newValue: Bool,
        permission: FamilyAccessPolicy.Permission = .manageCriticalFamilySettings,
        apply: @escaping (Bool) -> Void
    ) {
        requireSensitiveParentSession(
            permission: permission,
            deniedMessageRu: "Недостаточно прав для изменения настройки.",
            deniedMessageEn: "You don't have enough permissions to change this setting.",
            verifyFailedRu: "Изменение отклонено: нужно подтверждение родителя.",
            verifyFailedEn: "Change was blocked: parent verification is required."
        ) {
            apply(newValue)
        }
    }
    
    // MARK: - Achievement Card
    
    private var achievementCard: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("parental_achievements_weekly_map"))
                    .font(.h3)
                    .foregroundColor(.secondaryGold)
                
                Spacer()
                
                Button("Dashboard") {
                    requireSensitiveParentSession(permission: .viewParentalDashboard) {
                        showParentDashboardModal = true
                    }
                }
                .font(.captionBold)
                .foregroundColor(.textTertiary)
            }
            
            VStack(alignment: .leading, spacing: Spacing.s) {
                if let report = viewModel.weeklyReports.first {
                    if let list = report.content["achievements"]?.value as? [[String: Any]] {
                        ForEach(0..<min(list.count, 3), id: \.self) { index in
                            let item = list[index]
                            HStack(spacing: Spacing.m) {
                                Text(item["icon"] as? String ?? "✅")
                                    .font(.title3)
                                
                                Text(item["text"] as? String ?? "")
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                
                                Spacer()
                            }
                            .padding(.vertical, 4)
                        }
                    }
                } else {
                    // Placeholder если данных нет
                    HStack(spacing: Spacing.m) {
                        Text("⏳")
                            .font(.title3)
                        Text(localizationManager.localized("parental_achievements_weekly_loading"))
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                }
            }
            .padding(Spacing.m)
            .background(Color.white.opacity(0.05))
            .cornerRadius(CornerRadius.medium)
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.secondaryGold.opacity(0.2), lineWidth: 1)
        )
    }

    private var elderlySyncAuditBanner: some View {
        Group {
            if let elderlySyncReportBanner, !elderlySyncReportBanner.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text(localizationManager.currentLanguage == .russian ? "Elderly sync audit" : "Elderly sync audit")
                        .font(.caption.weight(.semibold))
                        .foregroundColor(.white.opacity(0.9))
                    Text(elderlySyncReportBanner)
                        .font(.caption2)
                        .foregroundColor(.white)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(Spacing.s)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.orange.opacity(0.22))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(Color.orange.opacity(0.45), lineWidth: 1)
                )
                .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            }
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: localizationManager.localized("parental_control_title"),
            subtitle: "\(localizationManager.localized("parental_control_subtitle")) \(currentChildDisplayName)",
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
            onBack: {
                navigationManager.goBackToPreviousScreen(reason: "ParentalControl.onBack")
            }
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("parental_accessibility_navigation"))
    }
    
    // MARK: - Child Selector
    
    private var childSelector: some View {
        VStack(spacing: Spacing.s) {
            HStack {
                Text(localizationManager.localized("parental_select_child"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            if isChildrenLoading {
                HStack(spacing: Spacing.s) {
                    ProgressView()
                        .progressViewStyle(.circular)
                    Text(localizationManager.localized("parental_children_loading"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            } else if let errorMessage = childrenErrorMessage {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundColor(.dangerRed)
                        .fixedSize(horizontal: false, vertical: true)
                    Button(action: {
                        HapticFeedback.selection()
                        loadChildMembers()
                    }) {
                        Text(localizationManager.localized("parental_retry"))
                            .font(.captionBold)
                            .foregroundColor(Color.secondaryGold)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            } else if childMembers.isEmpty {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(localizationManager.localized("parental_children_empty"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                    Button(action: {
                        HapticFeedback.selection()
                        loadChildMembers()
                    }) {
                        Text(localizationManager.localized("parental_retry"))
                            .font(.captionBold)
                            .foregroundColor(Color.secondaryGold)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            } else {
                HStack(spacing: Spacing.s) {
                    ForEach(childMembers) { child in
                        Button(action: {
                            withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                                selectedChild = child.id
                                selectedChildId = child.id
                            }
                            UserDefaults.standard.set(child.id, forKey: "active_child_profile_server_id")
                            HapticFeedback.selection()
                            loadParentalControlData(for: child.id)
                        }) {
                            VStack(spacing: Spacing.xs) {
                                Text(((child.avatar ?? "").isEmpty ? "👤" : (child.avatar ?? "")))
                                    .font(.system(size: 28))
                                
                                Text(child.name)
                                    .font(.bodyBold)
                                    .foregroundColor(selectedChild == child.id ? .white : .textPrimary)
                                    .lineLimit(1)
                            }
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.s)
                            .background(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .fill(selectedChild == child.id ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                    .stroke(
                                        selectedChild == child.id ? Color.secondaryGold.opacity(0.5) : Color.white.opacity(0.1),
                                        lineWidth: selectedChild == child.id ? 2 : 1
                                    )
                            )
                        }
                        .accessibilityLabel(String(format: localizationManager.localized("parental_select_child_accessibility"), child.name))
                        .accessibilityAddTraits(selectedChild == child.id ? .isSelected : [])
                    }
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.secondaryGold.opacity(0.2), lineWidth: 1)
        )
    }
    
    // MARK: - Parental Control Cards Grid
    
    private var parentalControlCards: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("parental_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            if isStatsLoading {
                HStack(spacing: Spacing.s) {
                    ProgressView()
                        .progressViewStyle(.circular)
                    Text(localizationManager.localized("parental_stats_loading"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            } else if let statsErrorMessage = statsErrorMessage {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(statsErrorMessage)
                        .font(.caption)
                        .foregroundColor(.dangerRed)
                        .fixedSize(horizontal: false, vertical: true)
                    if !childMembers.isEmpty {
                        Button(action: {
                            HapticFeedback.selection()
                            loadParentalControlData(for: selectedChild)
                        }) {
                            Text(localizationManager.localized("parental_retry"))
                                .font(.captionBold)
                                .foregroundColor(Color.secondaryGold)
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            } else {
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: Spacing.s), count: 2), spacing: Spacing.s) {
                    if FamilyFocusSessionFeature.isEnabled {
                        ParentalControlCard(
                            icon: "🎯",
                            title: localizationManager.localized("focus_session_title"),
                            statusBadge: localizationManager.localized("focus_session_badge"),
                            statusText: localizationManager.localized("focus_session_card_status"),
                            metric: localizationManager.localized("focus_session_card_metric"),
                            cardColor: Color(hex: "8B5CF6").opacity(0.2),
                            borderColor: Color(hex: "8B5CF6").opacity(0.45),
                            badgeColor: .secondaryGold,
                            isEnabled: .constant(true),
                            action: {
                                navigationManager.navigateTo(.focusSession)
                            }
                        )
                        .accessibilityIdentifier("parental_focus_session_card")
                    }
                    ParentalControlCard(
                        icon: "🔒",
                        title: localizationManager.localized("parental_content_block"),
                        statusBadge: contentBlockerManager.isEnabled ? localizationManager.localized("content_blocker_badge_enabled") : localizationManager.localized("content_blocker_badge_disabled"),
                        statusText: contentBlockerManager.isEnabled ?
                            String(format: localizationManager.localized("parental_content_blocked_metric"), contentBlockerManager.blockedSitesCount) :
                            localizationManager.localized("parental_content_blocker_disabled"),
                        metric: String(format: localizationManager.localized("parental_content_categories_active"), contentBlockerManager.activeCategories.count),
                        cardColor: .red.opacity(0.2),
                        borderColor: .red.opacity(0.4),
                        badgeColor: contentBlockerManager.isEnabled ? .successGreen : .warningOrange,
                        isEnabled: Binding(
                            get: { isContentBlockEnabled },
                            set: { newValue in
                                requestSensitiveToggleUpdate(newValue, permission: .manageFamilyLimits) { accepted in
                                    isContentBlockEnabled = accepted
                                    VisualLogger.shared.log("🔄 family_content_block_enabled = \(accepted)", level: .info, category: "PARENTAL.UI")
                                }
                            }
                        ),
                        action: {
                            guard canManageFamilyLimits else {
                                statsErrorMessage = localizationManager.currentLanguage == .russian
                                    ? "Недостаточно прав для управления лимитами."
                                    : "You don't have enough permissions to manage limits."
                                HapticFeedback.notification(.warning)
                                return
                            }
                            showContentBlockModal = true
                        }
                    )
                    
                    ParentalControlCard(
                        icon: "⏱️",
                        title: localizationManager.localized("parental_time_control"),
                        statusBadge: timeRemaining.isEmpty ? "⏳" : timeRemaining,
                        statusText: String(format: localizationManager.localized("parental_time_remaining_status"), timeRemaining.isEmpty ? localizationManager.localized("parental_time_remaining_default") : timeRemaining),
                        metric: String(format: localizationManager.localized("parental_time_schedules_metric"), timeSchedules),
                        cardColor: .blue.opacity(0.2),
                        borderColor: .blue.opacity(0.4),
                        badgeColor: .warningOrange,
                        isEnabled: Binding(
                            get: { isTimeControlEnabled },
                            set: { newValue in
                                requestSensitiveToggleUpdate(newValue, permission: .manageFamilyLimits) { accepted in
                                    isTimeControlEnabled = accepted
                                    VisualLogger.shared.log("🔄 family_time_control_enabled = \(accepted)", level: .info, category: "PARENTAL.UI")
                                }
                            }
                        ),
                        action: {
                            guard canManageFamilyLimits else {
                                statsErrorMessage = localizationManager.currentLanguage == .russian
                                    ? "Недостаточно прав для управления лимитами."
                                    : "You don't have enough permissions to manage limits."
                                HapticFeedback.notification(.warning)
                                return
                            }
                            showUnifiedTimeLimits = true
                        }
                    )
                    
                    ParentalControlCard(
                        icon: "👀",
                        title: localizationManager.localized("parental_monitoring"),
                        statusBadge: String(format: localizationManager.localized("parental_monitoring_badge"), monitoringWebsites),
                        statusText: String(format: localizationManager.localized("parental_monitoring_sites"), monitoringWebsites),
                        metric: String(format: localizationManager.localized("parental_monitoring_apps"), monitoringApps),
                        cardColor: .purple.opacity(0.2),
                        borderColor: .purple.opacity(0.4),
                        badgeColor: .successGreen,
                        isEnabled: Binding(
                            get: { isMonitoringEnabled },
                            set: { newValue in
                                requestSensitiveToggleUpdate(newValue, permission: .manageFamilyLimits) { accepted in
                                    isMonitoringEnabled = accepted
                                    VisualLogger.shared.log("🔄 family_monitoring_enabled = \(accepted)", level: .info, category: "PARENTAL.UI")
                                }
                            }
                        ),
                        action: {
                            guard canManageFamilyLimits else {
                                statsErrorMessage = localizationManager.currentLanguage == .russian
                                    ? "Недостаточно прав для управления лимитами."
                                    : "You don't have enough permissions to manage limits."
                                HapticFeedback.notification(.warning)
                                return
                            }
                            showMonitoringModal = true
                        }
                    )
                    
                    ParentalControlCard(
                        icon: "📍",
                        title: localizationManager.localized("parental_geofence"),
                        statusBadge: locationStatus.isEmpty ? "🏠" : locationStatus,
                        statusText: locationStatus.isEmpty ? localizationManager.localized("parental_location_home") : locationStatus,
                        metric: "Точность: 50м • " + locationLastUpdate,
                        cardColor: .green.opacity(0.2),
                        borderColor: .green.opacity(0.4),
                        badgeColor: .successGreen,
                        isEnabled: Binding(
                            get: { isLocationEnabled },
                            set: { newValue in
                                requestSensitiveToggleUpdate(newValue, permission: .manageFamilyLimits) { accepted in
                                    isLocationEnabled = accepted
                                    VisualLogger.shared.log("🔄 family_location_enabled = \(accepted)", level: .info, category: "PARENTAL.UI")
                                }
                            }
                        ),
                        action: {
                            guard canManageFamilyLimits else {
                                statsErrorMessage = localizationManager.currentLanguage == .russian
                                    ? "Недостаточно прав для управления лимитами."
                                    : "You don't have enough permissions to manage limits."
                                HapticFeedback.notification(.warning)
                                return
                            }
                            showLocationModal = true
                        }
                    )
                    
                    ParentalControlCard(
                        icon: "📊",
                        title: localizationManager.localized("parental_reports"),
                        statusBadge: String(format: localizationManager.localized("parental_alert_badge"), reportsAlerts),
                        statusText: reportsToday ? localizationManager.localized("parental_reports_today_status") : localizationManager.localized("parental_reports_week_status"),
                        metric: String(format: localizationManager.localized("parental_alerts_metric"), reportsAlerts),
                        cardColor: .orange.opacity(0.2),
                        borderColor: .orange.opacity(0.4),
                        badgeColor: .dangerRed,
                        isEnabled: Binding(
                            get: { isReportsEnabled },
                            set: { newValue in
                                requestSensitiveToggleUpdate(newValue, permission: .manageCriticalFamilySettings) { accepted in
                                    isReportsEnabled = accepted
                                    VisualLogger.shared.log("🔄 family_reports_enabled = \(accepted)", level: .info, category: "PARENTAL.UI")
                                }
                            }
                        ),
                        action: {
                            requireSensitiveParentSession(permission: .manageCriticalFamilySettings) {
                                showReportsModal = true
                            }
                        }
                    )
                    
                    ParentalControlCard(
                        icon: "⚙️",
                        title: localizationManager.localized("parental_additional"),
                        statusBadge: String(format: localizationManager.localized("parental_requests_badge"), additionalRequests),
                        statusText: String(format: localizationManager.localized("parental_requests_status"), additionalRequests),
                        metric: additionalProtection ? localizationManager.localized("parental_protection_on") : localizationManager.localized("parental_protection_off"),
                        cardColor: .gray.opacity(0.2),
                        borderColor: .gray.opacity(0.4),
                        badgeColor: .warningOrange,
                        isEnabled: Binding(
                            get: { isAdditionalEnabled },
                            set: { newValue in
                                requestSensitiveToggleUpdate(newValue, permission: .manageCriticalFamilySettings) { accepted in
                                    isAdditionalEnabled = accepted
                                    VisualLogger.shared.log("🔄 family_additional_enabled = \(accepted)", level: .info, category: "PARENTAL.UI")
                                }
                            }
                        ),
                        action: {
                            requireSensitiveParentSession(permission: .manageCriticalFamilySettings) {
                                showAdditionalModal = true
                            }
                        }
                    )
                    
                    ParentalControlCard(
                        icon: "🚨",
                        title: localizationManager.localized("parental_bypass_protection"),
                        statusBadge: bypassAttemptsToday > 0 ? String(format: localizationManager.localized("parental_bypass_badge"), bypassAttemptsToday) : localizationManager.localized("parental_bypass_no_attempts"),
                        statusText: String(format: localizationManager.localized("parental_bypass_blocked_metric"), bypassAttemptsBlocked),
                        metric: String(format: localizationManager.localized("parental_detection_active_metric"), bypassDetectionActive),
                        cardColor: Color.blue.opacity(0.2),
                        borderColor: Color.blue.opacity(0.4),
                        badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen,
                        isEnabled: Binding(
                            get: { isBypassProtectionEnabled },
                            set: { newValue in
                                requestSensitiveToggleUpdate(newValue, permission: .manageCriticalFamilySettings) { accepted in
                                    isBypassProtectionEnabled = accepted
                                    VisualLogger.shared.log("🔄 family_bypass_protection_enabled = \(accepted)", level: .info, category: "PARENTAL.UI")
                                }
                            }
                        ),
                        action: {
                            requireSensitiveParentSession(permission: .manageCriticalFamilySettings) {
                                showBypassProtectionModal = true
                            }
                        }
                    )
                }
            }
        }
        .padding(Spacing.m)
        .stormGlassCard(cornerRadius: CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .stroke(Color.secondaryGold.opacity(0.2), lineWidth: 1)
        )
    }
    
    // MARK: - Rewards Card
    
    private var rewardsCard: some View {
        Button(action: {
            requireSensitiveParentSession(permission: .manageCriticalFamilySettings) {
                HapticFeedback.impact(.medium)
                showRewardsModal = true
            }
        }) {
            HStack(spacing: Spacing.m) {
                // Название "Вознаграждение ребенка" на всю ширину карточки (без переносов)
                Text(localizationManager.localized("parental_reward"))
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
    
    // MARK: - Data Loading
    
    private func loadChildMembers() {
        isChildrenLoading = true
        childrenErrorMessage = nil
        
        // ✅ ИСПРАВЛЕНИЕ: Сначала пробуем загрузить из UserDefaults (локальный кэш)
        var hasLocalChildren = false
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            // Фильтруем только детей (child и teenager)
            let localChildren = decoded.filter { member in
                member.role == .child || member.role == .teenager
            }
            
            if !localChildren.isEmpty {
                // Преобразуем FamilyMemberData в FamilyMemberResponse
                let convertedChildren = localChildren.map { member in
                    FamilyMemberResponse(
                        id: member.serverMemberId ?? member.id,
                        name: member.name,
                        role: member.role.rawValue, // Преобразуем enum в строку
                        avatar: member.avatar,
                        status: member.status.rawValue,
                        threatsBlocked: member.threatsBlocked,
                        lastActive: member.lastActive,
                        devices: 1 // Дефолтное значение
                    )
                }
                self.children = convertedChildren
                hasLocalChildren = true
                print("✅ Загружено \(convertedChildren.count) детей из локального кэша")
            }
        }
        
        // ✅ ИСПРАВЛЕНИЕ: Проверяем токен перед загрузкой из API
        guard AppConfig.authToken != nil else {
            DispatchQueue.main.async {
                self.isChildrenLoading = false
                // Если есть локальные дети - не показываем ошибку
                if hasLocalChildren && !self.childMembers.isEmpty {
                    self.childrenErrorMessage = nil
                    // Загружаем данные для выбранного ребенка
                    if let resolvedId = self.resolveSelectedChildID() {
                        self.loadParentalControlData(for: resolvedId)
                    }
                } else {
                    // Если нет локальных детей и нет токена - список пустой
                    self.children = []
                    self.childrenErrorMessage = nil
                }
            }
            return
        }
        
        // Загружаем из API для синхронизации
        apiService.getFamilyMembers { result in
            DispatchQueue.main.async {
                self.isChildrenLoading = false
                switch result {
                case .success(let members):
                    self.statsErrorMessage = nil
                    // Обновляем список детей из API
                    self.children = members
                    let rosterFamilyId = UserDefaults.standard.string(forKey: FamilyLocalStore.familyIdKey)?
                        .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
                    ProfileManager.shared.syncChildRosterFromServer(
                        members: members,
                        familyId: rosterFamilyId.isEmpty ? nil : rosterFamilyId,
                        removeMissingServerLinkedChildren: true
                    )
                    
                    // ✅ ИСПРАВЛЕНИЕ: Если после фильтрации нет детей из API, но есть локальные - используем локальные
                    if self.childMembers.isEmpty && hasLocalChildren {
                        // Пробуем снова загрузить из UserDefaults
                        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
                           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
                            let localChildren = decoded.filter { member in
                                member.role == .child || member.role == .teenager
                            }
                            if !localChildren.isEmpty {
                                // Используем локальные данные
                                let convertedChildren = localChildren.map { member in
                                    FamilyMemberResponse(
                                        id: member.serverMemberId ?? member.id,
                                        name: member.name,
                                        role: member.role.rawValue,
                                        avatar: member.avatar,
                                        status: member.status.rawValue,
                                        threatsBlocked: member.threatsBlocked,
                                        lastActive: member.lastActive,
                                        devices: 1 // Дефолтное значение
                                    )
                                }
                                self.children = convertedChildren
                                print("✅ Используем локальные данные: \(convertedChildren.count) детей")
                            }
                        }
                    }
                    
                    // Проверяем, есть ли дети после фильтрации
                    if self.childMembers.isEmpty {
                        // Если нет детей, не показываем ошибку - это нормальная ситуация
                        self.childrenErrorMessage = nil
                        self.statsErrorMessage = self.localizationManager.localized("parental_children_empty")
                        return
                    }
                    
                    guard let resolvedId = self.resolveSelectedChildID() else {
                        self.statsErrorMessage = self.localizationManager.localized("parental_children_empty")
                        return
                    }
                    self.loadParentalControlData(for: resolvedId)
                case .failure(let error):
                    // ✅ ИСПРАВЛЕНИЕ: Если ошибка API, но есть локальные данные - используем их
                    if hasLocalChildren && !self.childMembers.isEmpty {
                        print("⚠️ Ошибка загрузки из API, используем локальные данные")
                        self.childrenErrorMessage = nil
                        // Загружаем данные для выбранного ребенка
                        if let resolvedId = self.resolveSelectedChildID() {
                            self.loadParentalControlData(for: resolvedId)
                        }
                    } else {
                        // Если нет локальных данных - показываем ошибку
                        let networkError = NetworkError.from(error)
                        if case .unauthorized = networkError {
                            // Для ошибки авторизации не показываем ошибку загрузки детей
                            self.children = []
                            self.childrenErrorMessage = nil
                        } else {
                            // Только для других ошибок показываем сообщение
                            let message = self.localizationManager.localized("parental_children_error_generic")
                    self.childrenErrorMessage = message
                    self.statsErrorMessage = message
                    print("❌ Ошибка загрузки списка детей: \(error.localizedDescription)")
                        }
                    }
                }
            }
        }
    }
    
    private func resolveSelectedChildID() -> String? {
        // Приоритет нового ключа ID
        if let byStoredId = childMembers.first(where: { $0.id == selectedChildId }) {
            selectedChild = byStoredId.id
            UserDefaults.standard.set(byStoredId.id, forKey: "active_child_profile_server_id")
            return byStoredId.id
        }
        // Обратная совместимость: если selectedChild содержит имя, конвертируем в ID
        if let byName = childMembers.first(where: { $0.name == selectedChild }) {
            selectedChild = byName.id
            selectedChildId = byName.id
            UserDefaults.standard.set(byName.id, forKey: "active_child_profile_server_id")
            return byName.id
        }
        if let existing = childMembers.first(where: { $0.id == selectedChild }) {
            selectedChildId = existing.id
            UserDefaults.standard.set(existing.id, forKey: "active_child_profile_server_id")
            return existing.id
        }
        if let firstChild = childMembers.first {
            selectedChild = firstChild.id
            selectedChildId = firstChild.id
            UserDefaults.standard.set(firstChild.id, forKey: "active_child_profile_server_id")
            return firstChild.id
        }
        selectedChild = ""
        selectedChildId = ""
        UserDefaults.standard.removeObject(forKey: "active_child_profile_server_id")
        return nil
    }
    
    private func loadParentalControlData(for childId: String) {
        statsErrorMessage = nil
        guard !childId.isEmpty else {
            statsErrorMessage = localizationManager.localized("parental_children_empty")
            return
        }
        loadParentalControlStats(for: childId)
        loadBypassStats(for: childId)
    }
    
    private func loadParentalControlStats(for childId: String?) {
        isStatsLoading = true
        statsErrorMessage = nil
        manager.getStats(childId: childId) { result in
            DispatchQueue.main.async {
                // Не снимаем флаг здесь, так как мы еще ждем ответа от getBypassStats
                switch result {
                case .success(let stats):
                    self.applyStats(stats)
                case .failure(let error):
                    self.isStatsLoading = false
                    let message = String(format: localizationManager.localized("parental_stats_error_generic"), error.localizedDescription)
                    self.statsErrorMessage = message
                    print("❌ Ошибка загрузки статистики: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func loadBypassStats(for childId: String?) {
        manager.getBypassStats(childId: childId) { result in
            DispatchQueue.main.async {
                self.isStatsLoading = false
                switch result {
                case .success(let stats):
                    self.bypassAttemptsToday = stats.today
                    self.bypassAttemptsWeek = stats.week
                    self.bypassAttemptsBlocked = stats.blocked
                    let active = [stats.incognito, stats.tor, stats.proxy].reduce(0) { $0 + ($1 > 0 ? 1 : 0) }
                    self.bypassDetectionActive = active
                    // ✅ ИСПРАВЛЕНО: Не перезаписываем isBypassProtectionEnabled из статистики - это пользовательская настройка через @AppStorage
                case .failure(let error):
                    print("❌ Ошибка загрузки статистики обхода: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func applyStats(_ stats: ParentalControlStatsResponse) {
        let totalFilters = max(stats.contentBlocked.activeFilters, 4)
        contentBlockActive = stats.contentBlocked.activeFilters
        contentBlockTotal = totalFilters
        contentBlockedCount = stats.contentBlocked.websitesBlocked + stats.contentBlocked.appsBlocked + stats.contentBlocked.searchQueriesBlocked
        // ✅ ИСПРАВЛЕНО: Не перезаписываем isContentBlockEnabled из статистики - это пользовательская настройка через @AppStorage
        
        let remaining = stats.screenTime.remaining
        timeRemaining = remaining.isEmpty ? localizationManager.localized("parental_time_remaining_default") : remaining
        timeSchedules = stats.screenTime.schedulesCount
        // ✅ ИСПРАВЛЕНО: Не перезаписываем isTimeControlEnabled из статистики - это пользовательская настройка через @AppStorage
        
        monitoringWebsites = stats.monitoring.sitesTracked
        monitoringApps = stats.monitoring.appsTracked
        // ✅ ИСПРАВЛЕНО: Не перезаписываем isMonitoringEnabled из статистики - это пользовательская настройка через @AppStorage
        
        locationStatus = stats.location.currentLocation ?? localizationManager.localized("parental_location_unknown")
        locationLastUpdate = stats.location.lastUpdate ?? localizationManager.localized("parental_location_not_updated")
        locationWarnings = stats.location.eventsToday
        // ✅ ИСПРАВЛЕНО: Не перезаписываем isLocationEnabled из статистики - это пользовательская настройка через @AppStorage
        
        if let rep = stats.reports {
            reportsAlerts = rep.alertsCount
            reportsToday = rep.hasDailyToday
        } else {
            reportsAlerts = 0
            reportsToday = false
        }
        // ✅ ИСПРАВЛЕНО: Не перезаписываем isReportsEnabled из статистики - это пользовательская настройка через @AppStorage
        
        additionalRequests = stats.location.geofencesCount
        additionalProtection = stats.monitoring.screenshotsEnabled ?? false  // ✅ ИСПРАВЛЕНО: Опциональное поле
        // ✅ ИСПРАВЛЕНО: Не перезаписываем isAdditionalEnabled из статистики - это пользовательская настройка через @AppStorage
    }
    
    // MARK: - Child Protection Section (5 компонентов)
    
    private var childProtectionSection: some View {
        VStack(spacing: Spacing.l) {
            SettingsAccordion(
                icon: "🛡️",
                title: localizationManager.localized("component.child_protection.title"),
                subtitle: localizationManager.localized("component.child_protection.subtitle"),
                isExpanded: $childProtectionExpanded
            ) {
                Text(localizationManager.localized("parental_family_controls_child_device_hint"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(.bottom, Spacing.xs)

                // 4 компонента защиты детей
                SecurityFeatureRow(
                    componentId: "self_harm_detection_agent",
                    title: localizationManager.localized("component.self_harm_detection_agent.title"),
                    description: localizationManager.localized("component.self_harm_detection_agent.desc"),
                    isEnabled: $viewModel.selfHarmDetectionEnabled,
                    hasSettings: false,
                    onToggle: { newValue in viewModel.toggleSelfHarmDetection(newValue) }
                )
                
                SecurityFeatureRow(
                    componentId: "grooming_detection_agent",
                    title: localizationManager.localized("component.grooming_detection_agent.title"),
                    description: localizationManager.localized("component.grooming_detection_agent.desc"),
                    isEnabled: $viewModel.groomingDetectionEnabled,
                    hasSettings: false,
                    onToggle: { newValue in viewModel.toggleGroomingDetection(newValue) }
                )
                
                SecurityFeatureRow(
                    componentId: "online_predators_agent",
                    title: localizationManager.localized("component.online_predators_agent.title"),
                    description: localizationManager.localized("component.online_predators_agent.desc"),
                    isEnabled: $viewModel.onlinePredatorsEnabled,
                    hasSettings: false,
                    onToggle: { newValue in viewModel.toggleOnlinePredators(newValue) }
                )
                
                SecurityFeatureRow(
                    componentId: "psychological_support_agent",
                    title: localizationManager.localized("component.psychological_support_agent.title"),
                    description: localizationManager.localized("component.psychological_support_agent.desc"),
                    isEnabled: $viewModel.psychologicalSupportEnabled,
                    hasSettings: false,
                    onToggle: { newValue in viewModel.togglePsychologicalSupport(newValue) }
                )
                
                // Улучшенный родительский контроль бот
                SecurityFeatureRow(
                    componentId: "parental_control_bot",
                    title: localizationManager.localized("component.parental_control_bot.title"),
                    description: localizationManager.localized("component.parental_control_bot.desc"),
                    isEnabled: $viewModel.parentalControlBotEnabled,
                    hasSettings: true,
                    onToggle: { newValue in viewModel.toggleParentalControlBot(newValue) },
                    onSettingsTap: { /* TODO: Открыть расширенные настройки родительского контроля */ }
                )
            }
        }
        .padding(.vertical, Spacing.m)
    }
    
    // MARK: - ✅ РОДИТЕЛЬСКИЙ КОНТРОЛЬ: Методы синхронизации с сервером
    
    /// Синхронизировать все данные родительского контроля с сервером
    @MainActor
    private func syncParentalControlData() async {
        guard let resolvedChildId = resolveSelectedChildID(), !resolvedChildId.isEmpty else { return }
        
        let familyId = UserDefaults.standard.string(forKey: "family_id") ?? "family_001"
        
        // Синхронизация настроек
        manager.loadSettingsFromServer(familyId: familyId, childId: resolvedChildId) { result in
            switch result {
            case .success(let response):
                // Обновляем локальные настройки из ответа сервера
                isContentBlockEnabled = response.isContentFilterEnabled
                isTimeControlEnabled = true // Включаем, если есть лимиты
                // Сохраняем другие настройки
                UserDefaults.standard.set(response.screenTimeLimitHours, forKey: "parental_screen_time_limit_hours")
                UserDefaults.standard.set(response.allowedApps, forKey: "parental_allowed_apps")
                UserDefaults.standard.set(response.blockedWebsites, forKey: "parental_blocked_websites")
                if let bedtime = response.bedtime {
                    UserDefaults.standard.set(bedtime, forKey: "parental_bedtime")
                }
            case .failure(let error):
                print("⚠️ Ошибка загрузки настроек: \(error.localizedDescription)")
            }
        }
        
        // Синхронизация лимитов времени
        manager.loadTimeLimitsFromServer(childId: resolvedChildId) { result in
            switch result {
            case .success(let response):
                // Обновляем локальные лимиты
                let dailyHours = response.dailyLimitMinutes / 60
                UserDefaults.standard.set(dailyHours, forKey: "parental_screen_time_limit")
                if let bedtimeStart = response.bedtimeStart {
                    UserDefaults.standard.set(bedtimeStart, forKey: "parental_bedtime_start")
                }
                if let bedtimeEnd = response.bedtimeEnd {
                    UserDefaults.standard.set(bedtimeEnd, forKey: "parental_bedtime_end")
                }
            case .failure(let error):
                print("⚠️ Ошибка загрузки лимитов времени: \(error.localizedDescription)")
            }
        }
        
        // Синхронизация расписаний
        manager.loadSchedulesFromServer(childId: resolvedChildId) { result in
            switch result {
            case .success(let schedules):
                // Обновляем количество расписаний
                timeSchedules = schedules.count
                // Сохраняем расписания
                if let encoded = try? JSONEncoder().encode(schedules) {
                    UserDefaults.standard.set(encoded, forKey: "parental_schedules_\(resolvedChildId)")
                }
            case .failure(let error):
                print("⚠️ Ошибка загрузки расписаний: \(error.localizedDescription)")
            }
        }
        
        // Синхронизация геозон
        manager.loadGeofencesFromServer(childId: resolvedChildId) { result in
            switch result {
            case .success(let geofences):
                // Обновляем количество геозон
                // Сохраняем геозоны
                if let encoded = try? JSONEncoder().encode(geofences) {
                    UserDefaults.standard.set(encoded, forKey: "parental_geofences_\(resolvedChildId)")
                }
            case .failure(let error):
                print("⚠️ Ошибка загрузки геозон: \(error.localizedDescription)")
            }
        }
        
        // Синхронизация блокировок приложений
        manager.loadAppBlocksFromServer(childId: resolvedChildId) { result in
            switch result {
            case .success(let response):
                // Обновляем локальные блокировки
                UserDefaults.standard.set(response.blockedApps, forKey: "parental_blocked_apps_\(resolvedChildId)")
                if let encoded = try? JSONEncoder().encode(response.appLimits) {
                    UserDefaults.standard.set(encoded, forKey: "parental_app_limits_\(resolvedChildId)")
                }
            case .failure(let error):
                print("⚠️ Ошибка загрузки блокировок приложений: \(error.localizedDescription)")
            }
        }
    }

    private func refreshElderlySyncReport() {
        guard let report = ElderlyHealthSyncAudit.latestReport() else {
            elderlySyncReportBanner = nil
            return
        }
        guard report.hasDesync else {
            elderlySyncReportBanner = nil
            return
        }
        elderlySyncReportBanner = report.summary
    }
}

// MARK: - Parental Control Card Component

struct ParentalControlCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
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
        VStack(spacing: Spacing.xs) {
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
                }
            }
            .buttonStyle(PlainButtonStyle())
                
            // Быстрый toggle (отдельная зона взаимодействия без открытия модалки)
            HStack {
                Text(isEnabled ? localizationManager.localized("parental_toggle_on") : localizationManager.localized("parental_toggle_off"))
                    .font(.caption2)
                    .fontWeight(.semibold)
                    .foregroundColor(isEnabled ? .successGreen : .textTertiary)
                
                ALADDINToggle(isOn: Binding(
                    get: { isEnabled },
                    set: { newValue in
                        isEnabled = newValue
                        VisualLogger.shared.log(
                            "🔄 card_toggle [\(title)] = \(newValue)",
                            level: .info,
                            category: "PARENTAL.UI"
                        )
                    }
                ))
                    .scaleEffect(0.7)
                    .onChange(of: isEnabled) { newValue in
                        VisualLogger.shared.log(
                            "🔄 \(title) = \(newValue)",
                            level: .info,
                            category: "PARENTAL.UI"
                        )
                    }
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
            .environmentObject(LocalizationManager())
    }
}
