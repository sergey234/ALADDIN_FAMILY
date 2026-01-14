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
    @State private var children: [FamilyMemberResponse] = []
    @State private var isChildrenLoading: Bool = false
    @State private var childrenErrorMessage: String?
    
    private var childMembers: [FamilyMemberResponse] {
        children.filter { member in
            let role = member.role.lowercased()
            return role == "child" || role == "teenager"
        }
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
    @State private var showTimeControlModal: Bool = false
    @State private var showMonitoringModal: Bool = false
    @State private var showLocationModal: Bool = false
    @State private var showReportsModal: Bool = false
    @State private var showAdditionalModal: Bool = false
    @State private var showBypassProtectionModal: Bool = false
    @State private var showRewardsModal: Bool = false
    
    // MARK: - Rewards Storage
    
    @AppStorage("child_unicorn_balance") private var unicornBalance: Int = 245
    @AppStorage("child_weekly_earned") private var weeklyRewarded: Int = 0
    @AppStorage("child_weekly_punished") private var weeklyPunished: Int = 0
    @State private var actualBalance: Int = 0
    
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
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
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
                        
                        // Сетка карточек родительского контроля
                        parentalControlCards
                        
                        // ✅ НОВЫЙ РАЗДЕЛ: Защита детей (5 компонентов)
                        childProtectionSection
                        
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
        .sheet(isPresented: $showTimeControlModal) {
            FamilyTimeControlModal(isPresented: $showTimeControlModal, isEnabled: $isTimeControlEnabled)
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
            actualBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
            if actualBalance == 0 && unicornBalance > 0 {
                actualBalance = unicornBalance
            }
            
            loadChildMembers()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            let newBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
            if newBalance != actualBalance {
                actualBalance = newBalance
                print("🔍 DEBUG: actualBalance обновлён до \(actualBalance)")
            }
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("parental_lang_\(localizationManager.currentLanguage.rawValue)")
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
                // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                dismiss()
                
                // Дополнительно синхронизируем NavigationManager для корректной работы стека
                DispatchQueue.main.async {
                    if navigationManager.canGoBack {
                        navigationManager.goBack()
                    }
                }
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
                            }
                            HapticFeedback.selection()
                            loadParentalControlData(for: child.id)
                        }) {
                            VStack(spacing: Spacing.xs) {
                                Text(child.avatar.isEmpty ? "👤" : child.avatar)
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
        .background(cardBackground)
        .cardShadow()
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
                        isEnabled: $isContentBlockEnabled,
                        action: { showContentBlockModal = true }
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
                        isEnabled: $isTimeControlEnabled,
                        action: { showTimeControlModal = true }
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
                        isEnabled: $isMonitoringEnabled,
                        action: { showMonitoringModal = true }
                    )
                    
                    ParentalControlCard(
                        icon: "📍",
                        title: localizationManager.localized("parental_geofence"),
                        statusBadge: locationStatus.isEmpty ? "🏠" : locationStatus,
                        statusText: locationStatus.isEmpty ? localizationManager.localized("parental_location_home") : locationStatus,
                        metric: locationWarnings > 0 ?
                            String(format: localizationManager.localized("parental_location_metric_with_warning"), locationLastUpdate, locationWarnings) :
                            String(format: localizationManager.localized("parental_location_metric"), locationLastUpdate),
                        cardColor: .green.opacity(0.2),
                        borderColor: .green.opacity(0.4),
                        badgeColor: .successGreen,
                        isEnabled: $isLocationEnabled,
                        action: { showLocationModal = true }
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
                        isEnabled: $isReportsEnabled,
                        action: { showReportsModal = true }
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
                        isEnabled: $isAdditionalEnabled,
                        action: { showAdditionalModal = true }
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
                        isEnabled: $isBypassProtectionEnabled,
                        action: { showBypassProtectionModal = true }
                    )
                }
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
    
    private func loadChildMembers() {
        isChildrenLoading = true
        childrenErrorMessage = nil
        apiService.getFamilyMembers { result in
            DispatchQueue.main.async {
                self.isChildrenLoading = false
                switch result {
                case .success(let members):
                    self.statsErrorMessage = nil
                    self.children = members
                    guard let resolvedId = resolveSelectedChildID() else {
                        self.statsErrorMessage = localizationManager.localized("parental_children_empty")
                        return
                    }
                    loadParentalControlData(for: resolvedId)
                case .failure(let error):
                    let message = localizationManager.localized("parental_children_error_generic")
                    self.childrenErrorMessage = message
                    self.statsErrorMessage = message
                    print("❌ Ошибка загрузки списка детей: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func resolveSelectedChildID() -> String? {
        if let existing = childMembers.first(where: { $0.id == selectedChild }) {
            return existing.id
        }
        if let firstChild = childMembers.first {
            selectedChild = firstChild.id
            return firstChild.id
        }
        selectedChild = ""
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
                self.isStatsLoading = false
                switch result {
                case .success(let stats):
                    self.applyStats(stats)
                case .failure(let error):
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
        
        reportsAlerts = stats.monitoring.contactsTracked
        reportsToday = stats.monitoring.messagesMonitored
        // ✅ ИСПРАВЛЕНО: Не перезаписываем isReportsEnabled из статистики - это пользовательская настройка через @AppStorage
        
        additionalRequests = stats.location.geofencesCount
        additionalProtection = stats.monitoring.screenshotsEnabled
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
                // 4 компонента защиты детей
                SecurityFeatureRow(
                    componentId: "self_harm_detection_agent",
                    title: localizationManager.localized("component.self_harm_detection_agent.title"),
                    description: localizationManager.localized("component.self_harm_detection_agent.desc"),
                    isEnabled: $viewModel.selfHarmDetectionEnabled,
                    hasSettings: false,
                    onToggle: { viewModel.toggleSelfHarmDetection() }
                )
                
                SecurityFeatureRow(
                    componentId: "grooming_detection_agent",
                    title: localizationManager.localized("component.grooming_detection_agent.title"),
                    description: localizationManager.localized("component.grooming_detection_agent.desc"),
                    isEnabled: $viewModel.groomingDetectionEnabled,
                    hasSettings: false,
                    onToggle: { viewModel.toggleGroomingDetection() }
                )
                
                SecurityFeatureRow(
                    componentId: "online_predators_agent",
                    title: localizationManager.localized("component.online_predators_agent.title"),
                    description: localizationManager.localized("component.online_predators_agent.desc"),
                    isEnabled: $viewModel.onlinePredatorsEnabled,
                    hasSettings: false,
                    onToggle: { viewModel.toggleOnlinePredators() }
                )
                
                SecurityFeatureRow(
                    componentId: "psychological_support_agent",
                    title: localizationManager.localized("component.psychological_support_agent.title"),
                    description: localizationManager.localized("component.psychological_support_agent.desc"),
                    isEnabled: $viewModel.psychologicalSupportEnabled,
                    hasSettings: false,
                    onToggle: { viewModel.togglePsychologicalSupport() }
                )
                
                // Улучшенный родительский контроль бот
                SecurityFeatureRow(
                    componentId: "parental_control_bot",
                    title: localizationManager.localized("component.parental_control_bot.title"),
                    description: localizationManager.localized("component.parental_control_bot.desc"),
                    isEnabled: $viewModel.parentalControlBotEnabled,
                    hasSettings: true,
                    onToggle: { viewModel.toggleParentalControlBot() },
                    onSettingsTap: { /* TODO: Открыть расширенные настройки родительского контроля */ }
                )
            }
        }
        .padding(.vertical, Spacing.m)
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
                    Text(isEnabled ? localizationManager.localized("parental_toggle_on") : localizationManager.localized("parental_toggle_off"))
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
            .environmentObject(LocalizationManager())
    }
}
