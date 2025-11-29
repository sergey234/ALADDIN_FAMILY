import SwiftUI

struct FamilyScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @Environment(\.dismiss) private var dismiss
    
    @State private var showAddMemberModal = false
    @State private var showParentalSettingsModal = false
    @State private var showRewardsModal: Bool = false
    @State private var showInvitationGuideModal: Bool = false
    
    // UserDefaults ключи для участников семьи
    private let familyMembersKey = "family_members_list"
    private let currentUserRoleKey = "current_user_role"
    private let currentUserNameKey = "current_user_name"
    private let familyIdKey = "family_id"
    
    // Для RewardsModalView
    @AppStorage("child_unicorn_balance") private var unicornBalanceForRewards: Int = 245
    @AppStorage("child_weekly_earned") private var weeklyRewarded: Int = 0
    @AppStorage("child_weekly_punished") private var weeklyPunished: Int = 0
    
    // Динамический список участников семьи (до 10 человек)
    @State private var familyMembers: [FamilyMemberData] = []
    
    // Новые состояния для родительского контроля (7 карточек)
    @State private var showContentBlockModal: Bool = false
    @State private var showTimeControlModalNew: Bool = false
    @State private var showMonitoringModalNew: Bool = false
    @State private var showLocationModal: Bool = false
    @State private var showReportsModal: Bool = false
    @State private var showAdditionalModal: Bool = false
    @State private var showBypassProtectionModal: Bool = false
    
    // Состояния для карточек
    @State private var isContentBlockEnabled: Bool = true
    @State private var isTimeControlEnabled: Bool = true
    @State private var isMonitoringEnabled: Bool = true
    @State private var isLocationEnabled: Bool = true
    @State private var isReportsEnabled: Bool = true
    @State private var isAdditionalEnabled: Bool = true
    @State private var isBypassProtectionEnabled: Bool = true
    
    // Данные для карточек (из wireframe)
    @State private var contentBlockActive: Int = 3
    @State private var contentBlockTotal: Int = 4
    @State private var contentBlockedCount: Int = 1245
    
    @State private var timeRemaining: String = "1ч 24мин"
    @State private var timeSchedules: Int = 3
    
    @State private var monitoringWebsites: Int = 342
    @State private var monitoringApps: Int = 28
    
    @State private var locationStatus: String = ""
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
    
    @State private var unicornBalance: Int = 245
    
    // Computed property для получения актуального баланса из UserDefaults
    private var currentUnicornBalance: Int {
        UserDefaults.standard.integer(forKey: "child_unicorn_balance")
    }
    
    // MARK: - Navigation Helper
    
    private func navigateToMemberScreen(role: FamilyMemberCard.FamilyRole) {
        // ✅ КРИТИЧНО: Логируем в print для консоли Xcode
        print("🚨🚨🚨 navigateToMemberScreen ВЫЗВАН! role=\(role)")
        
        // Navigate based on role
        let targetScreen: NavigationManager.ALADDINScreen
        switch role {
        case .parent:
            targetScreen = .parentalControl
        case .child:
            targetScreen = .childInterface
        case .teenager:
            targetScreen = .childInterface
        case .elderly:
            targetScreen = .elderlyInterface
        }
        
        print("🚨 navigateToMemberScreen: Вызываю navigationManager.navigateTo(\(targetScreen))")
        print("🚨 navigateToMemberScreen: Текущий экран ДО = \(navigationManager.currentScreen)")
        
        navigationManager.navigateTo(targetScreen)
        
        // Проверяем результат через небольшую задержку
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            print("🚨 navigateToMemberScreen: Текущий экран ПОСЛЕ = \(self.navigationManager.currentScreen)")
            if self.navigationManager.currentScreen == targetScreen {
                print("✅ navigateToMemberScreen: УСПЕХ! Экран изменён!")
            } else {
                print("❌ navigateToMemberScreen: ОШИБКА! Ожидался \(targetScreen), получен \(self.navigationManager.currentScreen)")
            }
        }
    }
    
    // MARK: - Family Members Management
    
    // Загрузка участников семьи из UserDefaults при открытии экрана
    private func loadFamilyMembers() {
        // 1. Попытка загрузить из UserDefaults
        if let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData),
           !decoded.isEmpty {
            familyMembers = decoded
            print("✅ Загружено участников семьи из UserDefaults: \(familyMembers.count)")
            return
        }
        
        // 2. Если нет сохранённых данных - создать карточку текущего пользователя
        if let currentRoleString = UserDefaults.standard.string(forKey: currentUserRoleKey) {
            let role: FamilyMemberCard.FamilyRole
            switch currentRoleString {
            case "Parent", "parent", "Родитель": role = .parent
            case "Child", "child", "Ребёнок": role = .child
            case "Teenager", "teenager", "Подросток": role = .teenager
            case "Grandparent", "grandparent", "Elderly", "elderly", "Пожилой": role = .elderly
            default: role = .parent
            }
            let userName = UserDefaults.standard.string(forKey: currentUserNameKey) ?? localizationManager.localized("family_you")
            
            familyMembers = [
                FamilyMemberData(
                    name: userName,
                    role: role,
                    avatar: getAvatarForRole(role),
                    status: .protected,
                    threatsBlocked: 0,
                    lastActive: localizationManager.localized("family_now")
                )
            ]
            print("✅ Создан участник для текущего пользователя: \(userName)")
        } else {
            // 3. Если даже роли нет - создаём участника по умолчанию (родитель)
            familyMembers = [
                FamilyMemberData(
                    name: localizationManager.localized("family_you"),
                    role: .parent,
                    avatar: "👨‍💼",
                    status: .protected,
                    threatsBlocked: 0,
                    lastActive: localizationManager.localized("family_now")
                )
            ]
            print("⚠️ Нет данных, создан участник по умолчанию")
        }
        
        // Сохраняем созданный список
        saveFamilyMembers()
    }
    
    // Сохранение участников семьи в UserDefaults
    private func saveFamilyMembers() {
        guard let encoded = try? JSONEncoder().encode(familyMembers) else {
            print("❌ Ошибка кодирования участников семьи")
            return
        }
        
        UserDefaults.standard.set(encoded, forKey: familyMembersKey)
        print("✅ Сохранено участников семьи: \(familyMembers.count)")
        
        // Уведомляем другие экраны об изменении
        NotificationCenter.default.post(name: UserDefaults.didChangeNotification, object: nil)
    }
    
    // Вспомогательная функция для получения аватара по роли
    private func getAvatarForRole(_ role: FamilyMemberCard.FamilyRole) -> String {
        switch role {
        case .parent: return "👨"
        case .child: return "👧"
        case .teenager: return "🧒"
        case .elderly: return "👵"
        }
    }
    
    // Определяем, является ли пользователь создателем семьи
    private var isFamilyCreator: Bool {
        let familyId = UserDefaults.standard.string(forKey: familyIdKey)
        let memberCount = familyMembers.count
        
        // Если нет familyID - вероятно создатель
        if familyId == nil {
            return true
        }
        
        // Если участников <= 1 и это текущий пользователь - создатель
        if memberCount <= 1 {
            let currentUserName = UserDefaults.standard.string(forKey: currentUserNameKey) ?? localizationManager.localized("family_you")
            if let firstMember = familyMembers.first,
               firstMember.name == currentUserName || firstMember.name == localizationManager.localized("family_you") {
                return true
            }
        }
        
        return false
    }
    
    // Проверяем, новая ли это семья (1 участник или меньше)
    private var isNewFamily: Bool {
        return familyMembers.count <= 1
    }
    
    // Проверяем, является ли пользователь родителем
    private var isUserParent: Bool {
        if let roleString = UserDefaults.standard.string(forKey: currentUserRoleKey) {
            switch roleString {
            case "Parent", "parent", "Родитель": return true
            default: return false
            }
        }
        return false
    }
    
    // Получаем список детей из familyMembers (для использования в модальных окнах)
    private var childrenNames: [String] {
        familyMembers
            .filter { member in
                member.role == .child || member.role == .teenager
            }
            .map { $0.name }
    }
    
    // ✅ СИНХРОНИЗАЦИЯ: Количество детей для карточки "Семейная защита"
    private var childrenCount: Int {
        familyMembers.filter { member in
            member.role == .child || member.role == .teenager
        }.count
    }
    
    // Получаем имя первого ребенка (для дефолтного значения)
    private var firstChildName: String {
        childrenNames.first ?? ""
    }
    
    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                colors: [Color(red: 0.04, green: 0.07, blue: 0.16), Color(red: 0.12, green: 0.23, blue: 0.37), Color(red: 0.18, green: 0.31, blue: 0.56)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Button(action: {
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
                            .font(.system(size: 20, weight: .medium))
                            .foregroundColor(.white)
                            .frame(width: 44, height: 44)
                            .background(Color.white.opacity(0.1))
                            .clipShape(Circle())
                    }
                    .accessibilityLabel("Назад")
                    .accessibilityHint("Нажмите для возврата к предыдущему экрану")
                    
                    Spacer()
                    
                    Text(localizationManager.localized("family_title"))
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                        .accessibilityLabel("ALADDIN Family - Семейная защита")
                        .accessibilityAddTraits(.isHeader)
                    
                    Spacer()
                    
                    Button(action: { showAddMemberModal = true }) {
                        Image(systemName: "plus")
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(Color(red: 0.04, green: 0.07, blue: 0.16))
                            .frame(width: 40, height: 40)
                            .background(Color(red: 0.96, green: 0.62, blue: 0.04))
                            .clipShape(Circle())
                    }
                    .accessibilityLabel("Добавить участника")
                    .accessibilityHint("Нажмите для добавления нового участника семьи")
                }
                .padding(.horizontal, 20)
                .padding(.top, 20)
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Family Overview
                        VStack(spacing: 20) {
                            Text(localizationManager.localized("family_protection_title"))
                                .font(.h3)
                                .foregroundColor(Color.secondaryGold)
                                .accessibilityLabel("Семейная защита")
                                .accessibilityAddTraits(.isHeader)
                            
                            // Stats - ✅ СИНХРОНИЗИРУЕМ С familyMembers
                            HStack(spacing: 15) {
                                StatItem(
                                    icon: "👥",
                                    value: "\(familyMembers.count)",
                                    label: localizationManager.localized("family_members")
                                )
                                .accessibilityElement(children: .combine)
                                .accessibilityLabel("Участников: \(familyMembers.count)")
                                
                                StatItem(
                                    icon: "👶",
                                    value: "\(childrenCount)",
                                    label: "\(childrenCount == 1 ? localizationManager.localized("family_child") : childrenCount == 0 ? localizationManager.localized("family_no_children") : localizationManager.localized("family_children"))"
                                )
                                .accessibilityElement(children: .combine)
                                .accessibilityLabel("\(childrenCount == 1 ? localizationManager.localized("family_child") : localizationManager.localized("family_children")): \(childrenCount)")
                                
                                StatItem(icon: "🛡️", value: "100%", label: localizationManager.localized("family_protection"))
                                    .accessibilityElement(children: .combine)
                                    .accessibilityLabel("Защита: 100%")
                            }
                            .accessibilityElement(children: .contain)
                            .accessibilityLabel("Статистика семьи")
                            
                            Button(action: { showAddMemberModal = true }) {
                                Text(localizationManager.localized("family_add_member"))
                                    .font(.system(size: 16, weight: .bold))
                                    .foregroundColor(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                                    .background(
                                        LinearGradient(
                                            colors: [Color(red: 0.96, green: 0.62, blue: 0.04), Color(red: 0.85, green: 0.47, blue: 0.02)],
                                            startPoint: .leading,
                                            endPoint: .trailing
                                        )
                                    )
                                    .clipShape(Capsule())
                            }
                            .accessibilityLabel("Добавить участника")
                            .accessibilityHint("Нажмите для добавления нового участника в семью")
                        }
                        .padding(25)
                        .background(Color.secondaryGold.opacity(0.15))
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.secondaryGold.opacity(0.4), lineWidth: 2)
                        )
                        
                        // Family Members
                        VStack(alignment: .leading, spacing: 20) {
                            Text(localizationManager.localized("family_members_title"))
                                .font(.h3)
                                .foregroundColor(Color.secondaryGold)
                                .accessibilityLabel(localizationManager.localized("family_members_title"))
                                .accessibilityAddTraits(.isHeader)
                            
                            // ✅ ИСПРАВЛЕНИЕ: Всегда показываем карточки участников когда они есть
                            // WelcomeCardForCreator показывается только если список ПУСТ
                            if !familyMembers.isEmpty {
                                // ✅ ИСПРАВЛЕНИЕ: Заменяем LazyVGrid на VStack для исправления touch events
                                VStack(spacing: 8) {
                                    ForEach(familyMembers) { member in
                                        FamilyMemberCard(
                                            name: member.name,
                                            role: member.role,
                                            avatar: member.avatar,
                                            status: member.status,
                                            threatsBlocked: member.threatsBlocked,
                                            lastActive: member.lastActive,
                                            action: {
                                                self.navigateToMemberScreen(role: member.role)
                                            }
                                        )
                                    }
                                    
                                    // Кнопка "Добавить ещё" (если участников < 10 и пользователь родитель)
                                    if familyMembers.count < 10 && isUserParent {
                                        AddMoreMemberCard {
                                            showAddMemberModal = true
                                        }
                                    }
                                }
                            }
                            // Пустое состояние - показываем WelcomeCardForCreator только если список пуст
                            else {
                                VStack(spacing: Spacing.m) {
                                    Text("👨‍👩‍👧‍👦")
                                        .font(.system(size: 48))
                                        .opacity(0.5)
                                    
                                    Text(localizationManager.localized("family_no_members"))
                                        .font(.subheadline)
                                        .foregroundColor(.white.opacity(0.7))
                                    
                                    Button(action: {
                                        showAddMemberModal = true
                                    }) {
                                        Text(localizationManager.localized("family_add_first_member"))
                                            .font(.subheadline)
                                            .fontWeight(.semibold)
                                            .foregroundColor(.secondaryGold)
                                            .padding(.vertical, Spacing.s)
                                            .padding(.horizontal, Spacing.m)
                                            .background(Color.secondaryGold.opacity(0.1))
                                            .cornerRadius(CornerRadius.medium)
                                            .overlay(
                                                RoundedRectangle(cornerRadius: CornerRadius.medium)
                                                    .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                                            )
                                    }
                                }
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.l)
                            }
                        }
                        .padding(25)
                        .background(Color.secondaryGold.opacity(0.15))
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.secondaryGold.opacity(0.4), lineWidth: 2)
                        )
                        
                        // Parental Controls - НОВАЯ ВЕРСИЯ С КАРТОЧКАМИ 2x3
                        parentalControlsSection
                    }
                    .padding(.horizontal, 20)
                    .padding(.bottom, 100)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Семейный контент")
                
                Spacer()
            }
            // ✅ ИСПРАВЛЕНИЕ: Убираем последний Spacer, который может перекрывать карточки
            // Spacer()  // ЗАКОММЕНТИРОВАНО
        }
        .sheet(isPresented: $showAddMemberModal) {
            AddMemberOptionsModal(isPresented: $showAddMemberModal)
                .environmentObject(navigationManager)  // ✅ КРИТИЧНО: Передаем NavigationManager в модал
        }
        // Новые модалы для родительского контроля (7 карточек)
        .sheet(isPresented: $showContentBlockModal) {
            FamilyContentBlockModal(isPresented: $showContentBlockModal, isEnabled: $isContentBlockEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showTimeControlModalNew) {
            FamilyTimeControlModal(isPresented: $showTimeControlModalNew, isEnabled: $isTimeControlEnabled)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showMonitoringModalNew) {
            FamilyMonitoringModal(isPresented: $showMonitoringModalNew, isEnabled: $isMonitoringEnabled)
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
        }
        .sheet(isPresented: $showParentalSettingsModal) {
            FamilyParentalControlSettingsModal(isPresented: $showParentalSettingsModal)
        }
        .sheet(isPresented: $showRewardsModal) {
            RewardsModalView(
                unicornBalance: $unicornBalanceForRewards,
                weeklyRewarded: $weeklyRewarded,
                weeklyPunished: $weeklyPunished
            )
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("family_lang_\(localizationManager.currentLanguage.rawValue)")
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            // Обновляем список участников и баланс при изменении UserDefaults
            loadFamilyMembers()
            unicornBalance = UserDefaults.standard.integer(forKey: "child_unicorn_balance")
        }
        .onAppear {
            // Загружаем участников при появлении экрана
            loadFamilyMembers()
        }
    }
}

// MARK: - Parental Controls Section

extension FamilyScreen {
    
    private var parentalControlsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
                            HStack {
                Text(localizationManager.localized("family_parental_control"))
                    .font(.h3)
                    .foregroundColor(Color.secondaryGold)
                    .accessibilityAddTraits(.isHeader)
                                
                                Spacer()
                                
                Button(action: {
                    HapticFeedback.impact(.light)
                    showParentalSettingsModal = true
                }) {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "gearshape.fill")
                            .font(.system(size: 16))
                            .foregroundColor(Color.secondaryGold)
                        Text(localizationManager.localized("family_settings"))
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(Color.secondaryGold)
                    }
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, Spacing.xs)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.small)
                            .fill(Color.secondaryGold.opacity(0.15))
                            .overlay(
                                RoundedRectangle(cornerRadius: CornerRadius.small)
                                    .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                            )
                    )
                }
                .accessibilityLabel("Открыть настройки родительского контроля")
            }
            
            // Сетка 2x3 - НОВЫЕ КАРТОЧКИ
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: Spacing.s), count: 2), spacing: Spacing.s) {
                // 1. Блокировка контента
                FamilyParentalControlCard(
                    icon: "🔒",
                    title: localizationManager.localized("parental_content_block"),
                    statusBadge: "\(contentBlockActive)/\(contentBlockTotal)",
                    statusText: "✅ \(contentBlockActive) \(localizationManager.localized("parental_active"))",
                    metric: "\(contentBlockedCount) \(localizationManager.localized("parental_blocked"))",
                    cardColor: .red.opacity(0.2),
                    borderColor: .red.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: $isContentBlockEnabled,
                    action: { showContentBlockModal = true }
                )
                
                // 2. Управление временем
                FamilyParentalControlCard(
                    icon: "⏱️",
                    title: localizationManager.localized("parental_time_control"),
                    statusBadge: "⏳",
                    statusText: "⏳ \(timeRemaining)",
                    metric: "\(timeSchedules) \(localizationManager.localized("parental_schedules"))",
                    cardColor: .blue.opacity(0.2),
                    borderColor: .blue.opacity(0.4),
                    badgeColor: .warningOrange,
                    isEnabled: $isTimeControlEnabled,
                    action: { showTimeControlModalNew = true }
                )
                
                // 3. Мониторинг
                FamilyParentalControlCard(
                    icon: "👀",
                    title: localizationManager.localized("parental_monitoring"),
                    statusBadge: "4/5",
                    statusText: "📊 \(monitoringWebsites) \(localizationManager.localized("parental_sites"))",
                    metric: "\(monitoringApps) \(localizationManager.localized("parental_apps"))",
                    cardColor: .purple.opacity(0.2),
                    borderColor: .purple.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: $isMonitoringEnabled,
                    action: { showMonitoringModalNew = true }
                )
                
                // 4. Геолокация
                FamilyParentalControlCard(
                    icon: "📍",
                    title: localizationManager.localized("parental_geolocation"),
                    statusBadge: "🏠",
                    statusText: "🏠 \(locationStatus.isEmpty ? localizationManager.localized("parental_location_home") : locationStatus)",
                    metric: locationLastUpdate + (locationWarnings > 0 ? " • ⚠️ \(locationWarnings)" : ""),
                    cardColor: .green.opacity(0.2),
                    borderColor: .green.opacity(0.4),
                    badgeColor: .successGreen,
                    isEnabled: $isLocationEnabled,
                    action: { showLocationModal = true }
                )
                
                // 5. Отчёты
                FamilyParentalControlCard(
                    icon: "📊",
                    title: localizationManager.localized("parental_reports"),
                    statusBadge: "⚠️ \(reportsAlerts)",
                    statusText: reportsToday ? "📅 \(localizationManager.localized("parental_reports_today"))" : "📅 \(localizationManager.localized("parental_reports_week"))",
                    metric: "\(reportsAlerts) \(localizationManager.localized("parental_alerts"))",
                    cardColor: .orange.opacity(0.2),
                    borderColor: .orange.opacity(0.4),
                    badgeColor: .dangerRed,
                    isEnabled: $isReportsEnabled,
                    action: { showReportsModal = true }
                )
                
                // 6. Дополнительно
                FamilyParentalControlCard(
                    icon: "⚙️",
                    title: localizationManager.localized("parental_additional"),
                    statusBadge: "✋ \(additionalRequests)",
                    statusText: "✋ \(additionalRequests) \(localizationManager.localized("parental_requests"))",
                    metric: additionalProtection ? "🛡️ \(localizationManager.localized("parental_protection_on"))" : "🛡️ \(localizationManager.localized("parental_protection_off"))",
                    cardColor: .gray.opacity(0.2),
                    borderColor: .gray.opacity(0.4),
                    badgeColor: .warningOrange,
                    isEnabled: $isAdditionalEnabled,
                    action: { showAdditionalModal = true }
                )
                
                // 7. Защита от обхода (НОВАЯ)
                FamilyParentalControlCard(
                    icon: "🚨",
                    title: localizationManager.localized("parental_bypass_protection"),
                    statusBadge: bypassAttemptsToday > 0 ? "🚨 \(bypassAttemptsToday)" : "✅ 0",
                    statusText: "🚫 \(bypassAttemptsBlocked) \(localizationManager.localized("parental_blocked_count"))",
                    metric: "\(bypassDetectionActive)/3 \(localizationManager.localized("parental_detection_active"))",
                    cardColor: Color.warningOrange.opacity(0.2),  // Янтарный (новый цвет!)
                    borderColor: Color.warningOrange.opacity(0.4),
                    badgeColor: bypassAttemptsToday > 0 ? .dangerRed : .successGreen,
                    isEnabled: $isBypassProtectionEnabled,
                    action: { showBypassProtectionModal = true }
                )
            }
            
            // Разделитель и заголовок для геймификации
            VStack(spacing: Spacing.s) {
                Divider()
                    .background(Color.secondaryGold.opacity(0.3))
                    .padding(.vertical, Spacing.m)
                
                HStack {
                    Text(localizationManager.localized("family_gamification"))
                        .font(.h3)
                        .foregroundColor(Color.secondaryGold)
                        .accessibilityAddTraits(.isHeader)
                    
                    Spacer()
                }
            }
            .padding(.top, Spacing.s)
            
            // Карточка вознаграждения (полная ширина)
            // ✅ ИСПРАВЛЕНО: Карточка широкая, текст полностью виден на одной строке
            // ✅ ИСПРАВЛЕНО: Для родителей открывается RewardsModalView, для детей - ChildRewardsScreen
            Button(action: {
                HapticFeedback.impact(.medium)
                // Проверяем роль пользователя
                let role = UserDefaults.standard.string(forKey: "current_user_role") ?? ""
                if role == "Parent" {
                    // Для родителей - модальное окно RewardsModalView
                    showRewardsModal = true
                } else {
                    // Для детей - экран ChildRewardsScreen
                    navigationManager.navigateTo(.childRewards)
                }
            }) {
                HStack(spacing: Spacing.m) {
                    // Большой единорог слева
                    Text("🦄")
                        .font(.system(size: 40))
                        .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: true)
                    
                    // Название "Вознаграждение ребёнка" полностью видно - убран желтый овал, текст на всю ширину
                    Text(localizationManager.localized("family_child_reward"))
                        .font(.bodyBold)
                        .foregroundColor(Color(red: 0.75, green: 0.52, blue: 0.99))
                        .lineLimit(1)
                        .minimumScaleFactor(0.9) // Немного уменьшаем шрифт если не влезает
                        .frame(maxWidth: .infinity, alignment: .leading) // Текст занимает всю доступную ширину
                    
                    Image(systemName: "chevron.right")
                        .font(.system(size: 14))
                        .foregroundColor(.textTertiary)
                }
                .frame(maxWidth: .infinity, alignment: .leading) // Карточка на всю ширину
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
            .id("rewardsCard_\(currentUnicornBalance)") // Принудительное обновление при изменении баланса
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.large)
                .fill(Color.backgroundMedium.opacity(0.5))
                        .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .stroke(Color.secondaryGold.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
    }
}

// MARK: - Family Parental Control Card Component

struct FamilyParentalControlCard: View {
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
            VStack(spacing: 4) {
                // Badge в верхнем правом углу
                HStack {
                Spacer()
                    Text(statusBadge)
                        .font(.captionSmall)
                        .fontWeight(.bold)
                        .foregroundColor(badgeColor)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(badgeColor.opacity(0.2))
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(badgeColor.opacity(0.5), lineWidth: 1)
                        )
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                }
                .frame(height: 20)
                
                // Иконка (уменьшена)
                Text(icon)
                    .font(.system(size: 28))
                    .frame(height: 32)
                
                // Название (меньший шрифт, больше места)
                Text(title)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                    .multilineTextAlignment(.center)
                    .lineLimit(2)
                    .minimumScaleFactor(0.85)
                    .frame(height: 32)
                    .fixedSize(horizontal: false, vertical: true)
                
                // Статус
                Text(statusText)
                    .font(.captionSmall)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                    .frame(height: 14)
                
                // Метрика
                Text(metric)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
                    .multilineTextAlignment(.center)
                    .lineLimit(1)
                    .frame(height: 14)
                
                Spacer(minLength: 4)
                
                // Улучшенный toggle с визуальным индикатором
                HStack(spacing: 4) {
                    Circle()
                        .fill(isEnabled ? Color.successGreen : Color.textTertiary)
                        .frame(width: 8, height: 8)
                    
                    Text(isEnabled ? "ON" : "OFF")
                        .font(.captionSmall)
                        .fontWeight(.bold)
                        .foregroundColor(isEnabled ? .successGreen : .textTertiary)
                        .frame(width: 24)
                    
                    Button(action: {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            isEnabled.toggle()
                        }
                        HapticFeedback.impact(.medium)
                    }) {
                        ZStack {
                            RoundedRectangle(cornerRadius: 12)
                                .fill(
                                    LinearGradient(
                                        colors: isEnabled ?
                                            [Color(hex: "#8B5CF6"), Color(hex: "#A78BFA")] :
                                            [Color.backgroundMedium, Color.backgroundMedium.opacity(0.5)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: 40, height: 24)
                            
                            Circle()
                                .fill(Color.white)
                                .frame(width: 20, height: 20)
                                .shadow(color: Color.black.opacity(0.2), radius: 3, x: 0, y: 2)
                                .offset(x: isEnabled ? 8 : -8)
                        }
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                .frame(height: 24)
            }
            .frame(height: 190)
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 8)
            .padding(.vertical, 10)
            .background(cardColor)
            .clipShape(RoundedRectangle(cornerRadius: CornerRadius.medium))
            // Ободок только если включено (без захода на toggle)
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .stroke(
                        isEnabled ? Color.secondaryGold.opacity(0.5) : Color.clear,
                        lineWidth: isEnabled ? 2 : 0
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .cardShadow()
    }
}

// MARK: - Family Modal Views (заглушки)

struct FamilyContentBlockModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Manager для обработки блокировки контента
    @StateObject private var manager = ParentalControlManager.shared
    
    // Выбранный ребёнок (для применения блокировки)
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Состояния для 4 переключателей с сохранением в UserDefaults
    @AppStorage("parental_website_blocking") private var isWebsiteBlockingEnabled: Bool = true
    @AppStorage("parental_app_blocking") private var isAppBlockingEnabled: Bool = true
    @AppStorage("parental_search_blocking") private var isSearchBlockingEnabled: Bool = true
    @AppStorage("parental_safesearch") private var isSafeSearchEnabled: Bool = false // По умолчанию OFF
    
    // Статистика (загружается из UserDefaults)
    @State private var blockedWebsites: Int = 1245
    @State private var blockedApps: Int = 8
    @State private var dangerousQueries: Int = 34
    
    // Ключ для статистики
    private let statsKey = "parental_content_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: "🔒 Блокировка контента",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Блокировка сайтов
                FamilyContentBlockItem(
                    icon: "🚫",
                    title: localizationManager.localized("family_block_sites_title"),
                    description: localizationManager.localized("family_block_sites_desc"),
                    isEnabled: $isWebsiteBlockingEnabled
                )
                
                // 2. Блокировка приложений
                FamilyContentBlockItem(
                    icon: "📱",
                    title: localizationManager.localized("family_block_apps_title"),
                    description: localizationManager.localized("family_block_apps_desc"),
                    isEnabled: $isAppBlockingEnabled
                )
                
                // 3. Блокировка поисковых запросов
                FamilyContentBlockItem(
                    icon: "🔍",
                    title: localizationManager.localized("family_block_search_title"),
                    description: localizationManager.localized("family_block_search_desc"),
                    isEnabled: $isSearchBlockingEnabled
                )
                
                // 4. SafeSearch (Google/YouTube)
                FamilyContentBlockItem(
                    icon: "🛡️",
                    title: "SafeSearch",
                    description: "Google/YouTube + YouTube Kids",
                    isEnabled: $isSafeSearchEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_week"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    HStack(spacing: Spacing.m) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(localizationManager.localized("family_blocked_sites"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(blockedWebsites)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 4) {
                            Text(localizationManager.localized("family_blocked_apps"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(blockedApps)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                    
                    HStack {
                        Text(localizationManager.localized("family_dangerous_queries"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(dangerousQueries)")
                            .font(.bodyBold)
                            .foregroundColor(.dangerRed)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .onAppear {
            // Загружаем статистику при открытии модала
            loadStatistics()
        }
        .onChange(of: isWebsiteBlockingEnabled) { newValue in
            // Сохраняем и применяем блокировку через Manager
            print("✅ Блокировка сайтов: \(newValue ? "ВКЛ" : "ВЫКЛ")")
            manager.applyContentBlocking(
                childId: selectedChild,
                websiteBlocking: isWebsiteBlockingEnabled,
                appBlocking: isAppBlockingEnabled,
                searchBlocking: isSearchBlockingEnabled,
                safesearch: isSafeSearchEnabled
            )
        }
        .onChange(of: isAppBlockingEnabled) { newValue in
            print("✅ Блокировка приложений: \(newValue ? "ВКЛ" : "ВЫКЛ")")
            manager.applyContentBlocking(
                childId: selectedChild,
                websiteBlocking: isWebsiteBlockingEnabled,
                appBlocking: isAppBlockingEnabled,
                searchBlocking: isSearchBlockingEnabled,
                safesearch: isSafeSearchEnabled
            )
        }
        .onChange(of: isSearchBlockingEnabled) { newValue in
            print("✅ Блокировка поисковых запросов: \(newValue ? "ВКЛ" : "ВЫКЛ")")
            manager.applyContentBlocking(
                childId: selectedChild,
                websiteBlocking: isWebsiteBlockingEnabled,
                appBlocking: isAppBlockingEnabled,
                searchBlocking: isSearchBlockingEnabled,
                safesearch: isSafeSearchEnabled
            )
        }
        .onChange(of: isSafeSearchEnabled) { newValue in
            print("✅ SafeSearch: \(newValue ? "ВКЛ" : "ВЫКЛ")")
            manager.applyContentBlocking(
                childId: selectedChild,
                websiteBlocking: isWebsiteBlockingEnabled,
                appBlocking: isAppBlockingEnabled,
                searchBlocking: isSearchBlockingEnabled,
                safesearch: isSafeSearchEnabled
            )
        }
    }
    
    // Загрузка статистики из UserDefaults
    private func loadStatistics() {
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) as? [String: Int] {
            blockedWebsites = stats["blockedWebsites"] ?? 1245
            blockedApps = stats["blockedApps"] ?? 8
            dangerousQueries = stats["dangerousQueries"] ?? 34
        }
    }
    
    // Загрузка списка детей из family_members_list
    private func loadChildren() {
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            children = []
            return
        }
        
        children = decoded
            .filter { member in
                member.role == .child || member.role == .teenager
            }
            .map { $0.name }
    }
}

// MARK: - Content Block Item Component

struct FamilyContentBlockItem: View {
    let icon: String
    let title: String
    let description: String
    @Binding var isEnabled: Bool
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Toggle без ободков - используем кастомный без padding
            Button(action: {
                withAnimation(.easeInOut(duration: 0.3)) {
                    isEnabled.toggle()
                }
                HapticFeedback.impact(.medium)
            }) {
                ZStack {
                    RoundedRectangle(cornerRadius: 15)
                        .fill(
                            LinearGradient(
                                colors: isEnabled ?
                                    [Color(hex: "#8B5CF6"), Color(hex: "#A78BFA")] :
                                    [Color.backgroundMedium, Color.backgroundMedium.opacity(0.5)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 50, height: 30)
                    
                    Circle()
                        .fill(Color.white)
                        .frame(width: 26, height: 26)
                        .shadow(color: Color.black.opacity(0.2), radius: 4, x: 0, y: 2)
                        .offset(x: isEnabled ? 10 : -10)
                }
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
        // Убрали белый ободок - теперь только фон
    }
}

// MARK: - Config Button Item Component

struct FamilyConfigButtonItem: View {
    let icon: String
    let title: String
    let description: String
    let buttonTitle: String
    let action: () -> Void
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Золотая кнопка
            Button(action: {
                HapticFeedback.impact(.medium)
                action()
            }) {
                Text(buttonTitle)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondaryGold)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.xs)
                    .background(Color.secondaryGold.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.secondaryGold.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
    }
}

// MARK: - Badge Item Component

struct FamilyBadgeItem: View {
    let icon: String
    let title: String
    let description: String
    let badgeText: String
    let badgeColor: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            HapticFeedback.impact(.medium)
            action()
        }) {
            HStack(spacing: Spacing.m) {
                // Иконка
                Text(icon)
                    .font(.system(size: 28))
                    .frame(width: 40, height: 40)
                
                // Информация
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .lineLimit(2)
                        .fixedSize(horizontal: false, vertical: true)
                    
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(2)
                }
                
                Spacer(minLength: 8)
                
                // Badge
                Text(badgeText)
                    .font(.captionSmall)
                    .fontWeight(.bold)
                    .foregroundColor(badgeColor)
                    .padding(.horizontal, Spacing.s)
                    .padding(.vertical, 4)
                    .background(badgeColor.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(badgeColor.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
            .padding(Spacing.m)
            .background(Color.backgroundMedium.opacity(0.2))
            .cornerRadius(CornerRadius.medium)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Action Button Item Component

struct FamilyActionButtonItem: View {
    let icon: String
    let title: String
    let description: String
    let buttonTitle: String
    let action: () -> Void
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка
            Text(icon)
                .font(.system(size: 28))
                .frame(width: 40, height: 40)
            
            // Информация
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .lineLimit(2)
            }
            
            Spacer(minLength: 8)
            
            // Красная кнопка действия
            Button(action: {
                HapticFeedback.impact(.medium)
                action()
            }) {
                Text(buttonTitle)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.dangerRed)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                    .padding(.horizontal, Spacing.m)
                    .padding(.vertical, Spacing.xs)
                    .background(Color.dangerRed.opacity(0.2))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.dangerRed.opacity(0.5), lineWidth: 1)
                    )
                    .cornerRadius(8)
            }
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
    }
}

struct FamilyTimeControlModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для детальных модалов настроек
    @State private var showScreenTimeSettings = false
    @State private var showScheduleSettings = false
    @State private var showSleepTimeSettings = false
    @State private var showAppLimitsSettings = false
    
    // Настройки времени с сохранением в UserDefaults
    @AppStorage("parental_screen_time_limit") private var screenTimeLimit: String = "3 часа/день"
    @AppStorage("parental_screen_time_remaining") private var screenTimeRemaining: String = "1ч 24мин"
    @AppStorage("parental_schedule_weekdays") private var scheduleWeekdays: String = "15:00-18:00"
    @AppStorage("parental_schedule_weekends") private var scheduleWeekends: String = "10:00-20:00"
    @AppStorage("parental_bedtime_start") private var bedtimeStart: String = "22:00"
    @AppStorage("parental_bedtime_end") private var bedtimeEnd: String = "07:00"
    @AppStorage("parental_instagram_limit") private var instagramLimit: String = "30 мин"
    @AppStorage("parental_tiktok_limit") private var tiktokLimit: String = "20 мин"
    
    // Статистика
    @State private var totalTimeUsed: String = "1ч 36мин"
    @State private var totalTimeLimit: String = "3ч"
    @State private var instagramUsed: String = "18мин"
    @State private var instagramLimitStat: String = "30мин"
    @State private var tiktokUsed: String = "12мин"
    @State private var tiktokLimitStat: String = "20мин"
    
    var body: some View {
        FamilyModalBaseView(
            title: "⏱️ Управление временем",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Экранное время
                FamilyConfigButtonItem(
                    icon: "📱",
                    title: localizationManager.localized("family_screen_time"),
                    description: "\(localizationManager.localized("family_screen_time_now")) \(screenTimeLimit) (\(localizationManager.localized("family_screen_time_remaining")) \(screenTimeRemaining))",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showScreenTimeSettings = true }
                )
                
                // 2. Расписание доступа
                FamilyConfigButtonItem(
                    icon: "📅",
                    title: localizationManager.localized("family_schedule_access"),
                    description: "\(localizationManager.localized("family_weekdays_short")) \(scheduleWeekdays), \(localizationManager.localized("family_weekends_short")) \(scheduleWeekends)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showScheduleSettings = true }
                )
                
                // 3. Время сна
                FamilyConfigButtonItem(
                    icon: "🌙",
                    title: localizationManager.localized("family_bedtime"),
                    description: "\(localizationManager.localized("family_bedtime_block")) \(bedtimeStart) - \(bedtimeEnd)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showSleepTimeSettings = true }
                )
                
                // 4. Лимиты по приложениям
                FamilyConfigButtonItem(
                    icon: "⏰",
                    title: localizationManager.localized("family_app_limits"),
                    description: "\(localizationManager.localized("family_instagram")) \(instagramLimit), \(localizationManager.localized("family_tiktok")) \(tiktokLimit)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showAppLimitsSettings = true }
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_today"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(localizationManager.localized("family_total_time"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(totalTimeUsed) / \(totalTimeLimit)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_instagram"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(instagramUsed) / \(instagramLimitStat)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_tiktok"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(tiktokUsed) / \(tiktokLimitStat)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        // Детальные модалы настроек
        .sheet(isPresented: $showScreenTimeSettings) {
            ScreenTimeSettingsModal(isPresented: $showScreenTimeSettings)
        }
        .sheet(isPresented: $showScheduleSettings) {
            ScheduleSettingsModal(isPresented: $showScheduleSettings)
        }
        .sheet(isPresented: $showSleepTimeSettings) {
            SleepTimeSettingsModal(isPresented: $showSleepTimeSettings)
        }
        .sheet(isPresented: $showAppLimitsSettings) {
            AppLimitsSettingsModal(isPresented: $showAppLimitsSettings)
        }
        .onAppear {
            // Загружаем статистику при открытии модала
            loadTimeStatistics()
        }
    }
    
    // Загрузка статистики времени из UserDefaults
    private func loadTimeStatistics() {
        if let stats = UserDefaults.standard.dictionary(forKey: "parental_time_stats") as? [String: String] {
            totalTimeUsed = stats["totalTimeUsed"] ?? "1ч 36мин"
            totalTimeLimit = stats["totalTimeLimit"] ?? "3ч"
            instagramUsed = stats["instagramUsed"] ?? "18мин"
            instagramLimitStat = stats["instagramLimitStat"] ?? "30мин"
            tiktokUsed = stats["tiktokUsed"] ?? "12мин"
            tiktokLimitStat = stats["tiktokLimitStat"] ?? "20мин"
        }
    }
}

struct FamilyMonitoringModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_messages_monitoring") private var isMessagesMonitoringEnabled: Bool = false
    @AppStorage("parental_screenshots_enabled") private var isScreenshotsEnabled: Bool = false
    
    // Состояния для детальных модалов просмотра
    @State private var showBrowserHistory = false
    @State private var showAppHistory = false
    @State private var showContacts = false
    
    // Mock-данные (загружаются из UserDefaults)
    @State private var browserSitesCount: Int = 342
    @State private var appsUsedCount: Int = 28
    @State private var contactsCount: Int = 47
    
    // Статистика (загружается из UserDefaults)
    @State private var topSite: String = "YouTube.com"
    @State private var topSiteVisits: Int = 142
    @State private var topApp: String = "Instagram"
    @State private var topAppTime: String = "8ч 24мин"
    @State private var activeContacts: Int = 47
    
    // Ключ для статистики мониторинга
    private let statsKey = "parental_monitoring_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: "👀 Мониторинг",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. История браузера - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "🌐",
                    title: localizationManager.localized("family_browser_history"),
                    description: "\(browserSitesCount) \(localizationManager.localized("family_sites")) за неделю",
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showBrowserHistory = true }
                )
                
                // 2. История приложений - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "📲",
                    title: localizationManager.localized("family_app_history"),
                    description: "\(appsUsedCount) \(localizationManager.localized("family_apps")) использовано",
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showAppHistory = true }
                )
                
                // 3. Мониторинг сообщений - Toggle Item
                FamilyContentBlockItem(
                    icon: "💬",
                    title: localizationManager.localized("family_message_monitoring"),
                    description: localizationManager.localized("family_message_monitoring_desc"),
                    isEnabled: $isMessagesMonitoringEnabled
                )
                
                // 4. Просмотр контактов - Badge Item (кликабельный)
                FamilyBadgeItem(
                    icon: "👥",
                    title: localizationManager.localized("family_contacts_view"),
                    description: localizationManager.localized("family_contacts_desc"),
                    badgeText: localizationManager.localized("family_active_badge"),
                    badgeColor: .successGreen,
                    action: { showContacts = true }
                )
                
                // 5. Скриншоты экрана - Toggle Item
                FamilyContentBlockItem(
                    icon: "📸",
                    title: localizationManager.localized("family_screenshots"),
                    description: localizationManager.localized("family_screenshots_desc"),
                    isEnabled: $isScreenshotsEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_week_detailed"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Text(localizationManager.localized("family_top_site"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(topSite) (\(topSiteVisits) \(localizationManager.localized("family_visits")))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_top_app"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(topApp) (\(topAppTime))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text(localizationManager.localized("family_contacts"))
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(activeContacts) \(localizationManager.localized("family_active"))")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        // Детальные модалы просмотра (создадим полноценные ниже)
        .sheet(isPresented: $showBrowserHistory) {
            BrowserHistoryDetailModal(isPresented: $showBrowserHistory)
        }
        .sheet(isPresented: $showAppHistory) {
            AppHistoryDetailModal(isPresented: $showAppHistory)
        }
        .sheet(isPresented: $showContacts) {
            ContactsDetailModal(isPresented: $showContacts)
        }
        .onAppear {
            // Загружаем статистику при открытии модала
            loadMonitoringStatistics()
        }
        .onChange(of: isMessagesMonitoringEnabled) { newValue in
            print("✅ Мониторинг сообщений: \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
        .onChange(of: isScreenshotsEnabled) { newValue in
            print("✅ Скриншоты экрана: \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
    }
    
    // Загрузка статистики мониторинга из UserDefaults
    private func loadMonitoringStatistics() {
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            browserSitesCount = stats["browserSitesCount"] as? Int ?? 342
            appsUsedCount = stats["appsUsedCount"] as? Int ?? 28
            contactsCount = stats["contactsCount"] as? Int ?? 47
            topSite = stats["topSite"] as? String ?? "YouTube.com"
            topSiteVisits = stats["topSiteVisits"] as? Int ?? 142
            topApp = stats["topApp"] as? String ?? "Instagram"
            topAppTime = stats["topAppTime"] as? String ?? "8ч 24мин"
            activeContacts = stats["activeContacts"] as? Int ?? 47
        }
    }
}

struct FamilyLocationModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_location_enabled") private var isLocationEnabledState: Bool = true
    @AppStorage("parental_sos_enabled") private var isSOSEnabled: Bool = true
    
    // Состояния для детальных модалов
    @State private var showGeofencesSettings = false
    @State private var showLocationHistory = false
    
    // Mock-данные (загружаются из UserDefaults)
    @State private var locationStatus: String = "🏠 Дома (ул. Ленина, 42)"
    @State private var locationLastUpdate: String = "2 мин назад"
    @State private var geofencesCount: Int = 2
    @State private var geofencesList: String = ""
    
    // Статистика событий сегодня (загружается из UserDefaults)
    @State private var todayEvents: [LocationEvent] = []
    
    // Ключ для статистики геолокации
    private let statsKey = "parental_location_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: "📍 Геолокация",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Местоположение - Toggle Item
                FamilyContentBlockItem(
                    icon: "📍",
                    title: localizationManager.localized("family_location"),
                    description: "\(locationStatus) • \(locationLastUpdate)",
                    isEnabled: $isLocationEnabledState
                )
                
                // 2. Геозоны - Config Button Item
                FamilyConfigButtonItem(
                    icon: "🗺️",
                    title: localizationManager.localized("family_geofences"),
                    description: "\(geofencesCount) активны: \(geofencesList)",
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showGeofencesSettings = true }
                )
                
                // 3. История перемещений - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📜",
                    title: localizationManager.localized("family_movement_history"),
                    description: localizationManager.localized("family_movement_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showLocationHistory = true }
                )
                
                // 4. Кнопка SOS - Toggle Item
                FamilyContentBlockItem(
                    icon: "🆘",
                    title: localizationManager.localized("family_sos_button"),
                    description: localizationManager.localized("family_sos_desc"),
                    isEnabled: $isSOSEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_statistics_today_detailed"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(todayEvents) { event in
                        HStack {
                            Text("• \(event.time) - \(event.action)")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text(event.status.icon)
                                .font(.caption)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showGeofencesSettings) {
            GeofencesSettingsModal(isPresented: $showGeofencesSettings)
        }
        .sheet(isPresented: $showLocationHistory) {
            LocationHistoryDetailModal(isPresented: $showLocationHistory)
        }
        .onAppear {
            // Загружаем статистику при открытии модала
            loadLocationStatistics()
        }
        .onChange(of: isLocationEnabledState) { newValue in
            print("✅ Геолокация: \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
        .onChange(of: isSOSEnabled) { newValue in
            print("✅ Кнопка SOS: \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
    }
    
    // Загрузка статистики геолокации из UserDefaults
    private func loadLocationStatistics() {
        // Загружаем статус и данные
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            locationStatus = stats["locationStatus"] as? String ?? "🏠 Дома (ул. Ленина, 42)"
            locationLastUpdate = stats["locationLastUpdate"] as? String ?? "2 мин назад"
            geofencesCount = stats["geofencesCount"] as? Int ?? 2
            geofencesList = stats["geofencesList"] as? String ?? localizationManager.localized("family_location_default")
        }
        
        // Загружаем события сегодня (по умолчанию примерные)
        if todayEvents.isEmpty {
            todayEvents = [
                LocationEvent(time: "08:30", action: localizationManager.localized("family_left_home"), status: .departure),
                LocationEvent(time: "09:15", action: localizationManager.localized("family_arrived_school"), status: .arrival),
                LocationEvent(time: "15:45", action: localizationManager.localized("family_returned_home"), status: .arrival)
            ]
        }
    }
}

// MARK: - Location Event Model

struct LocationEvent: Identifiable {
    let id = UUID()
    let time: String
    let action: String
    let status: LocationStatus
    
    enum LocationStatus {
        case arrival
        case departure
        
        var icon: String {
            switch self {
            case .arrival: return "✅"
            case .departure: return "🚶"
            }
        }
    }
}

struct FamilyReportsModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Выбранный ребёнок для загрузки статистики
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Состояния для детальных модалов просмотра
    @State private var showWeeklyReport = false
    @State private var showSuspiciousActivity = false
    @State private var showTopSites = false
    @State private var showTopApps = false
    @State private var showUsageHours = false
    @State private var showBypassAttempts = false
    
    // Mock-данные (загружаются из UserDefaults)
    @State private var suspiciousActivityCount: Int = 2
    @State private var bypassAttemptsCount: Int = 0
    
    // Статистика предупреждений (загружается из UserDefaults)
    @State private var warnings: [ReportWarning] = []
    
    // Ключ для статистики отчётов
    private let statsKey = "parental_reports_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: "📊 Отчёты",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Еженедельный отчёт - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📅",
                    title: localizationManager.localized("family_weekly_report"),
                    description: localizationManager.localized("family_weekly_report_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showWeeklyReport = true }
                )
                
                // 2. Подозрительная активность - Badge Item
                FamilyBadgeItem(
                    icon: "⚠️",
                    title: localizationManager.localized("family_suspicious_activity_title"),
                    description: "\(suspiciousActivityCount) \(localizationManager.localized("family_new")) предупреждения",
                    badgeText: "\(suspiciousActivityCount)",
                    badgeColor: .dangerRed,
                    action: { showSuspiciousActivity = true }
                )
                
                // 3. Top-5 сайтов - Config Button Item
                FamilyConfigButtonItem(
                    icon: "🌐",
                    title: localizationManager.localized("family_top_5_sites"),
                    description: localizationManager.localized("family_top_sites_desc"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showTopSites = true }
                )
                
                // 4. Top-5 приложений - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📱",
                    title: localizationManager.localized("family_top_5_apps"),
                    description: localizationManager.localized("family_usage_by_time"),
                    buttonTitle: localizationManager.localized("family_view"),
                    action: { showTopApps = true }
                )
                
                // 5. Пиковые часы активности - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📊",
                    title: "Пиковые часы активности",
                    description: "Детальная аналитика по часам",
                    buttonTitle: "Смотреть",
                    action: { showUsageHours = true }
                )
                
                // 6. Попытки обхода блокировок - Badge Item
                FamilyBadgeItem(
                    icon: "🛡️",
                    title: "Попытки обхода блокировок",
                    description: "VPN/Tor/Скрытый режим попытки",
                    badgeText: "\(bypassAttemptsCount)",
                    badgeColor: .successGreen,
                    action: { showBypassAttempts = true }
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика предупреждений
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_suspicious_activity"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(warnings) { warning in
                        HStack {
                            Text("• \(warning.text)")
                                .font(.caption)
                                .foregroundColor(warning.color)
                            Spacer()
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showWeeklyReport) {
            WeeklyReportDetailModal(isPresented: $showWeeklyReport)
                .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showSuspiciousActivity) {
            SuspiciousActivityDetailModal(isPresented: $showSuspiciousActivity)
        }
        .sheet(isPresented: $showTopSites) {
            TopSitesDetailModal(isPresented: $showTopSites)
        }
        .sheet(isPresented: $showTopApps) {
            TopAppsDetailModal(isPresented: $showTopApps)
        }
        .sheet(isPresented: $showUsageHours) {
            UsageHoursDetailModal(isPresented: $showUsageHours)
        }
        .sheet(isPresented: $showBypassAttempts) {
            BypassAttemptsDetailModal(isPresented: $showBypassAttempts)
        }
        .onAppear {
            loadChildren()
            if selectedChild.isEmpty && !children.isEmpty {
                selectedChild = children.first ?? ""
            }
            // Загружаем статистику при открытии модала
            loadReportsStatistics()
        }
    }
    
    // Загрузка списка детей из family_members_list
    private func loadChildren() {
        guard let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
              let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) else {
            children = []
            return
        }
        
        children = decoded
            .filter { member in
                member.role == .child || member.role == .teenager
            }
            .map { $0.name }
    }
    
    // Загрузка статистики отчётов из UserDefaults и API
    private func loadReportsStatistics() {
        // Загружаем из UserDefaults (локальный кэш)
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            suspiciousActivityCount = stats["suspiciousActivityCount"] as? Int ?? 2
            bypassAttemptsCount = stats["bypassAttemptsCount"] as? Int ?? 0
        }
        
        // Загружаем статистику обхода через API
        let manager = ParentalControlManager.shared
        manager.getBypassStats(childId: selectedChild) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    self.bypassAttemptsCount = stats.week
                    // Сохраняем в UserDefaults для кэширования
                    var cachedStats = UserDefaults.standard.dictionary(forKey: self.statsKey) ?? [:]
                    cachedStats["bypassAttemptsCount"] = stats.week
                    UserDefaults.standard.set(cachedStats, forKey: self.statsKey)
                case .failure(let error):
                    print("⚠️ Ошибка загрузки статистики обхода: \(error.localizedDescription)")
                    // Оставляем значения по умолчанию
                }
            }
        }
        
        // Загружаем предупреждения (по умолчанию примерные)
        if warnings.isEmpty {
            warnings = [
                ReportWarning(text: "Попытка доступа к заблокированному сайту", color: .dangerRed),
                ReportWarning(text: "Превышено экранное время на 15 минут", color: .warningOrange)
            ]
        }
    }
}

// MARK: - Report Warning Model

struct ReportWarning: Identifiable {
    let id = UUID()
    let text: String
    let color: Color
}

struct FamilyAdditionalModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // Состояния для toggle-элементов с сохранением в UserDefaults
    @AppStorage("parental_homework_mode") private var isHomeworkModeEnabled: Bool = false
    
    // Состояния для детальных модалов
    @State private var showRemoteLockConfirmation = false
    @State private var showRemoteWipeConfirmation = false
    @State private var showAccessRequests = false
    @State private var showYouTubeSettings = false
    
    // Mock-данные (загружаются из UserDefaults)
    @State private var accessRequestsCount: Int = 2
    @State private var deviceName: String = "iPhone 12 (Алексей)"
    @State private var deviceStatus: String = "Онлайн"
    @State private var deviceBattery: String = "67%"
    
    // Статистика запросов (загружается из UserDefaults)
    @State private var requests: [AccessRequest] = []
    
    // Ключ для статистики дополнительных настроек
    private let statsKey = "parental_additional_stats"
    
    var body: some View {
        FamilyModalBaseView(
            title: "⚙️ Дополнительно",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Удалённая блокировка - Action Button Item
                FamilyActionButtonItem(
                    icon: "🔒",
                    title: "Удалённая блокировка",
                    description: "Заблокировать телефон ребёнка",
                    buttonTitle: "Блокировать",
                    action: { showRemoteLockConfirmation = true }
                )
                
                // 2. Удаление данных - Action Button Item
                FamilyActionButtonItem(
                    icon: "🗑️",
                    title: "Удаление данных",
                    description: "Стереть все данные (НОВОЕ!)",
                    buttonTitle: "Удалить",
                    action: { showRemoteWipeConfirmation = true }
                )
                
                // 3. Запросы доступа - Badge Item
                FamilyBadgeItem(
                    icon: "✋",
                    title: localizationManager.localized("family_access_requests"),
                    description: "\(accessRequestsCount) \(localizationManager.localized("family_access_requests_count"))",
                    badgeText: "\(accessRequestsCount)",
                    badgeColor: .warningOrange,
                    action: { showAccessRequests = true }
                )
                
                // 4. YouTube фильтрация - Config Button Item
                FamilyConfigButtonItem(
                    icon: "📺",
                    title: localizationManager.localized("family_youtube_filtering"),
                    description: localizationManager.localized("family_age_restriction"),
                    buttonTitle: localizationManager.localized("family_configure"),
                    action: { showYouTubeSettings = true }
                )
                
                // 5. Режим "Домашнее задание" - Toggle Item
                FamilyContentBlockItem(
                    icon: "📚",
                    title: localizationManager.localized("family_homework_mode"),
                    description: localizationManager.localized("family_homework_desc"),
                    isEnabled: $isHomeworkModeEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика запросов
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(localizationManager.localized("family_access_requests"))
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(requests) { request in
                        HStack {
                            Text("• \(localizationManager.localized("family_unlock")) \(request.app) (\(request.time))")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .sheet(isPresented: $showRemoteLockConfirmation) {
            RemoteLockConfirmationModal(isPresented: $showRemoteLockConfirmation, deviceName: deviceName, deviceStatus: deviceStatus, deviceBattery: deviceBattery)
        }
        .sheet(isPresented: $showRemoteWipeConfirmation) {
            RemoteWipeConfirmationModal(isPresented: $showRemoteWipeConfirmation)
        }
        .sheet(isPresented: $showAccessRequests) {
            AccessRequestsModal(isPresented: $showAccessRequests, requests: $requests)
        }
        .sheet(isPresented: $showYouTubeSettings) {
            YouTubeSettingsModal(isPresented: $showYouTubeSettings)
        }
        .onAppear {
            // Загружаем статистику при открытии модала
            loadAdditionalStatistics()
        }
        .onChange(of: isHomeworkModeEnabled) { newValue in
            print("✅ Режим \"Домашнее задание\": \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
    }
    
    // Загрузка статистики дополнительных настроек из UserDefaults
    private func loadAdditionalStatistics() {
        if let stats = UserDefaults.standard.dictionary(forKey: statsKey) {
            accessRequestsCount = stats["accessRequestsCount"] as? Int ?? 2
            deviceName = stats["deviceName"] as? String ?? "iPhone 12 (Алексей)"
            deviceStatus = stats["deviceStatus"] as? String ?? "Онлайн"
            deviceBattery = stats["deviceBattery"] as? String ?? "67%"
        }
        
        // Загружаем запросы доступа (по умолчанию примерные)
        if requests.isEmpty {
            requests = [
                AccessRequest(app: "Instagram", time: "10 мин назад", reason: "Хочу посмотреть сообщения", limit: "30 мин/день (использовано)"),
                AccessRequest(app: "YouTube", time: "5 мин назад", reason: "Нужно посмотреть урок", limit: "45 мин/день (осталось 12 мин)")
            ]
        }
    }
}

// MARK: - Access Request Model

struct AccessRequest: Identifiable {
    let id = UUID()
    let app: String
    let time: String
    let reason: String
    let limit: String
}

// MARK: - Family Modal Base View

struct FamilyModalBaseView<Content: View>: View {
    let title: String
    @Binding var isPresented: Bool
    let content: Content
    
    init(title: String, isPresented: Binding<Bool>, @ViewBuilder content: () -> Content) {
        self.title = title
        self._isPresented = isPresented
        self.content = content()
    }
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                HStack {
                    Text(title)
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    Button(action: {
                        HapticFeedback.impact(.light)
                        isPresented = false
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 28))
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(
                    RoundedRectangle(cornerRadius: 0)
                        .fill(Color.backgroundMedium.opacity(0.5))
                )
                
                // Content
                ScrollView {
                    VStack(spacing: Spacing.m) {
                        content
                    }
                    .padding(Spacing.m)
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct ControlCard: View {
    let icon: String
    let title: String
    let info: String
    let status: ControlStatus
    let action: () -> Void
    
    enum ControlStatus {
        case green, red
    }
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                HStack(spacing: 4) {
                    Text(icon)
                        .font(.system(size: 16))
                    
                    Text(title)
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(Color(red: 0.96, green: 0.62, blue: 0.04))
                }
                
                Text(info)
                    .font(.system(size: 11))
                    .foregroundColor(.white.opacity(0.9))
                
                Spacer()
                
                Text(status == .green ? "🟢" : "🔴")
                    .font(.system(size: 28))
                    .animation(.easeInOut(duration: 2).repeatForever(autoreverses: true), value: status)
            }
            .frame(height: 90)
            .frame(maxWidth: .infinity)
            .padding(8)
            .background(Color(red: 0.96, green: 0.62, blue: 0.04).opacity(0.1))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color(red: 0.96, green: 0.62, blue: 0.04), lineWidth: 2)
            )
            .clipShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Modals

struct AddMemberModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: 20) {
            Text(localizationManager.localized("family_add_member_title"))
                .font(.title2)
                .foregroundColor(.white)
            
            Text(localizationManager.localized("family_scan_qr_code"))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
            
            Button(localizationManager.localized("family_close")) {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

struct RewardsModal: View {
    @Binding var isPresented: Bool
    
    var body: some View {
        VStack(spacing: 20) {
            Text("🦄 Вознаграждение ребёнка")
                .font(.title2)
                .foregroundColor(Color(red: 0.75, green: 0.52, blue: 0.99))
            
            Text("245 единорогов на счету")
                .foregroundColor(.gray)
            
            Button("Закрыть") {
                isPresented = false
            }
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .clipShape(Capsule())
        }
        .padding()
        .background(Color.black)
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}

// MARK: - Detailed Modals

// MARK: 1. Подтверждения (приоритетные)

struct RemoteLockConfirmationModal: View {
    @Binding var isPresented: Bool
    let deviceName: String
    let deviceStatus: String
    let deviceBattery: String
    
    @State private var showSuccess = false
    
    var body: some View {
        FamilyModalBaseView(
            title: "🔒 Удалённая блокировка",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Предупреждение
                VStack(spacing: Spacing.m) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 64))
                        .foregroundColor(.warningOrange)
                    
                    Text("Внимание!")
                        .font(.h2)
                        .foregroundColor(.textPrimary)
                    
                    Text("Вы собираетесь заблокировать устройство ребёнка удалённо.")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(Spacing.l)
                .background(Color.warningOrange.opacity(0.1))
                .cornerRadius(CornerRadius.large)
                
                // Информация об устройстве
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("📱 Информация об устройстве:")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    HStack {
                        Text("Устройство:")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceName)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                    }
                    
                    HStack {
                        Text("Статус:")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceStatus)
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    
                    HStack {
                        Text("Батарея:")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text(deviceBattery)
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Действия
                if showSuccess {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.successGreen)
                        
                        Text("Устройство успешно заблокировано!")
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    .padding(Spacing.l)
                } else {
                    VStack(spacing: Spacing.m) {
                        Button(action: {
                            HapticFeedback.impact(.heavy)
                            withAnimation {
                                showSuccess = true
                            }
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                                isPresented = false
                            }
                        }) {
                            Text("Подтвердить блокировку")
                                .font(.bodyBold)
                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.dangerRed)
                                .cornerRadius(CornerRadius.medium)
                        }
                        
                        Button(action: {
                            HapticFeedback.impact(.light)
                            isPresented = false
                        }) {
                            Text("Отмена")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                    }
                }
            }
        }
    }
}

struct RemoteWipeConfirmationModal: View {
    @Binding var isPresented: Bool
    
    @State private var showSuccess = false
    @State private var confirmationText = ""
    @State private var isConfirmationValid = false
    
    var body: some View {
        FamilyModalBaseView(
            title: "🗑️ Удаление данных",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Критическое предупреждение
                VStack(spacing: Spacing.m) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.dangerRed)
                    
                    Text("ОПАСНО!")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(.dangerRed)
                    
                    Text("Это действие удалит ВСЕ данные с устройства ребёнка без возможности восстановления!")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .padding(Spacing.l)
                .background(Color.dangerRed.opacity(0.15))
                .cornerRadius(CornerRadius.large)
                
                // Подтверждение
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("Для подтверждения введите \"УДАЛИТЬ\" ниже:")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    
                    TextField("УДАЛИТЬ", text: $confirmationText)
                        .font(.body)
                        .foregroundColor(.textPrimary)
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.5))
                        .cornerRadius(CornerRadius.medium)
                        .autocapitalization(.allCharacters)
                        .onChange(of: confirmationText) { newValue in
                            isConfirmationValid = newValue.uppercased() == "УДАЛИТЬ"
                        }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Действия
                if showSuccess {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "trash.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.dangerRed)
                        
                        Text("Данные удаляются...")
                            .font(.bodyBold)
                            .foregroundColor(.dangerRed)
                    }
                    .padding(Spacing.l)
                } else {
                    VStack(spacing: Spacing.m) {
                        Button(action: {
                            HapticFeedback.impact(.heavy)
                            withAnimation {
                                showSuccess = true
                            }
                            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                isPresented = false
            }
                        }) {
                            Text("Удалить все данные")
                                .font(.bodyBold)
            .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(isConfirmationValid ? Color.dangerRed : Color.dangerRed.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                        .disabled(!isConfirmationValid)
                        
                        Button(action: {
                            HapticFeedback.impact(.light)
                            isPresented = false
                        }) {
                            Text("Отмена")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .frame(maxWidth: .infinity)
                                .padding(Spacing.m)
                                .background(Color.backgroundMedium.opacity(0.5))
                                .cornerRadius(CornerRadius.medium)
                        }
                    }
                }
            }
        }
    }
}

// MARK: 2. Запросы доступа

struct AccessRequestsModal: View {
    @Binding var isPresented: Bool
    @Binding var requests: [AccessRequest]
    
    // Manager для обработки запросов
    @StateObject private var manager = ParentalControlManager.shared
    @State private var processingRequestId: String?
    
    var body: some View {
        FamilyModalBaseView(
            title: "✋ Запросы доступа",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                if requests.isEmpty {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 64))
                            .foregroundColor(.successGreen)
                        
                        Text("Нет новых запросов")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Text("Все запросы обработаны")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.xl)
                } else {
                    ForEach(requests) { request in
                        VStack(alignment: .leading, spacing: Spacing.m) {
                            HStack {
                                Text(request.app)
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Spacer()
                                
                                Text(request.time)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Text(request.reason)
                                .font(.body)
                                .foregroundColor(.textSecondary)
                                .lineLimit(2)
                            
                            Text(request.limit)
                                .font(.caption)
                                .foregroundColor(.warningOrange)
                            
                            Divider()
                            
                            HStack(spacing: Spacing.m) {
                                Button(action: {
                                    handleAccessRequest(requestId: request.id.uuidString, action: "accept")
                                }) {
                                    Text("Одобрить")
                                        .font(.bodyBold)
                .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .padding(Spacing.s)
                                        .background(processingRequestId == request.id.uuidString ? Color.gray : Color.successGreen)
                                        .cornerRadius(CornerRadius.small)
                                }
                                .disabled(processingRequestId == request.id.uuidString || manager.isLoading)
                                
                                Button(action: {
                                    handleAccessRequest(requestId: request.id.uuidString, action: "reject")
                                }) {
                                    Text("Отклонить")
                                        .font(.bodyBold)
                                        .foregroundColor(.white)
                                        .frame(maxWidth: .infinity)
                                        .padding(Spacing.s)
                                        .background(processingRequestId == request.id.uuidString ? Color.gray : Color.dangerRed)
                                        .cornerRadius(CornerRadius.small)
                                }
                                .disabled(processingRequestId == request.id.uuidString || manager.isLoading)
                            }
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
        .onAppear {
            // Загружаем запросы из API при открытии
            loadAccessRequests()
        }
    }
    
    // Загрузка запросов доступа из API
    private func loadAccessRequests() {
        manager.getAccessRequests { result in
            switch result {
            case .success(let apiRequests):
                // Конвертируем API ответы в локальные модели
                requests = apiRequests.map { apiRequest in
                    AccessRequest(
                        app: apiRequest.app,
                        time: apiRequest.time,
                        reason: apiRequest.reason,
                        limit: apiRequest.limit
                    )
                }
                print("✅ Загружено \(requests.count) запросов доступа")
            case .failure(let error):
                print("❌ Ошибка загрузки запросов: \(error.localizedDescription)")
                // Оставляем существующие mock-данные при ошибке
            }
        }
    }
    
    // Обработка запроса доступа
    private func handleAccessRequest(requestId: String, action: String) {
        HapticFeedback.impact(.medium)
        processingRequestId = requestId
        
        manager.handleAccessRequest(requestId: requestId, action: action) { (success: Bool, error: String?) in
            DispatchQueue.main.async {
                processingRequestId = nil
                
                if success {
                    // Удаляем запрос из списка после успешной обработки
                    withAnimation {
                        requests.removeAll { $0.id.uuidString == requestId }
                    }
                    print("✅ Запрос \(requestId) \(action == "accept" ? "принят" : "отклонён")")
                } else {
                    print("❌ Ошибка обработки запроса: \(error ?? "Неизвестная ошибка")")
                }
            }
        }
    }
}

// MARK: 3. История браузера

struct BrowserHistoryDetailModal: View {
    @Binding var isPresented: Bool
    
    @State private var browserHistory: [BrowserHistoryItem] = [
        BrowserHistoryItem(site: "youtube.com", visits: 142, time: "8ч 24мин", category: "Видео", color: .red),
        BrowserHistoryItem(site: "instagram.com", visits: 89, time: "4ч 12мин", category: "Соц. сети", color: .purple),
        BrowserHistoryItem(site: "vk.com", visits: 67, time: "2ч 45мин", category: "Соц. сети", color: .blue),
        BrowserHistoryItem(site: "google.com", visits: 45, time: "1ч 15мин", category: "Поиск", color: .blue),
        BrowserHistoryItem(site: "tiktok.com", visits: 34, time: "3ч 20мин", category: "Видео", color: .black)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: "🌐 История браузера",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text("Всего сайтов")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(browserHistory.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text("Всего времени")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("20ч 16мин")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 сайтов
                Text("Топ-5 сайтов за неделю")
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                ForEach(Array(browserHistory.enumerated()), id: \.element.id) { index, item in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.site)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text("\(item.visits) визитов")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text(item.time)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Text(item.category)
                                .font(.captionSmall)
                                .foregroundColor(item.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(item.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
    }
}

struct BrowserHistoryItem: Identifiable {
    let id = UUID()
    let site: String
    let visits: Int
    let time: String
    let category: String
    let color: Color
}

// MARK: 4. История приложений

struct AppHistoryDetailModal: View {
    @Binding var isPresented: Bool
    
    @State private var appHistory: [AppHistoryItem] = [
        AppHistoryItem(app: "Instagram", time: "8ч 24мин", limit: "30мин/день", exceeded: true, exceededBy: "7ч 54мин", color: .purple),
        AppHistoryItem(app: "TikTok", time: "4ч 12мин", limit: "20мин/день", exceeded: true, exceededBy: "3ч 52мин", color: .black),
        AppHistoryItem(app: "YouTube", time: "3ч 45мин", limit: "45мин/день", exceeded: true, exceededBy: "3ч 0мин", color: .red),
        AppHistoryItem(app: "WhatsApp", time: "1ч 30мин", limit: "60мин/день", exceeded: false, exceededBy: nil, color: .green),
        AppHistoryItem(app: "VK", time: "45мин", limit: "30мин/день", exceeded: true, exceededBy: "15мин", color: .blue)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: "📲 История приложений",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text("Всего приложений")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(appHistory.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text("Превышений лимита")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(appHistory.filter { $0.exceeded }.count)")
                            .font(.h3)
                            .foregroundColor(.dangerRed)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 приложений
                Text("Топ-5 приложений за неделю")
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                ForEach(Array(appHistory.enumerated()), id: \.element.id) { index, item in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text(item.time)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("Лимит: \(item.limit)")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            if item.exceeded, let exceededBy = item.exceededBy {
                                HStack {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                    
                                    Text("Превышено на \(exceededBy)")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.dangerRed.opacity(0.2))
                                .cornerRadius(8)
                            } else {
                                HStack {
                                    Image(systemName: "checkmark.circle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.successGreen)
                                    
                                    Text("В пределах лимита")
                                        .font(.captionSmall)
                                        .foregroundColor(.successGreen)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.successGreen.opacity(0.2))
                                .cornerRadius(8)
                            }
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(item.exceeded ? Color.dangerRed.opacity(0.1) : Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(item.exceeded ? Color.dangerRed.opacity(0.5) : Color.clear, lineWidth: 2)
                    )
                }
            }
        }
    }
}

struct AppHistoryItem: Identifiable {
    let id = UUID()
    let app: String
    let time: String
    let limit: String
    let exceeded: Bool
    let exceededBy: String?
    let color: Color
}

// MARK: 5. Контакты

struct ContactsDetailModal: View {
    @Binding var isPresented: Bool
    
    @State private var contacts: [ContactItem] = []
    
    var body: some View {
        FamilyModalBaseView(
            title: "👥 Просмотр контактов",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading) {
                        Text("Всего контактов")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(contacts.count)")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing) {
                        Text("Сообщений")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("\(contacts.reduce(0) { $0 + $1.messages })")
                            .font(.h3)
                            .foregroundColor(.secondaryGold)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Топ-5 контактов
                if contacts.isEmpty {
                    EmptyStateView(
                        icon: "👥",
                        title: "Контакты не найдены",
                        description: "Данные о контактах будут загружены после начала мониторинга активности ребёнка",
                        actionTitle: nil,
                        action: nil
                    )
                    .padding()
                } else {
                    Text("Топ-5 контактов за неделю")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    ForEach(Array(contacts.enumerated()), id: \.element.id) { index, contact in
                    HStack(spacing: Spacing.m) {
                        // Номер
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(contact.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text("\(contact.messages) сообщений")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("\(contact.calls) звонков")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Text("Последний контакт: \(contact.lastContact)")
                                .font(.captionSmall)
                                .foregroundColor(contact.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(contact.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
        .onAppear {
            loadContacts()
        }
        .onReceive(NotificationCenter.default.publisher(for: UserDefaults.didChangeNotification)) { _ in
            loadContacts() // Синхронизируем при изменении данных
        }
    }
    
    // Загрузка контактов из UserDefaults (child_family_contacts_list) или создание из family_members_list
    private func loadContacts() {
        // Попытка загрузить из child_family_contacts_list (если есть сохранённые контакты)
        if let savedData = UserDefaults.standard.data(forKey: "child_family_contacts_list"),
           let decoded = try? JSONDecoder().decode([ChildFamilyContact].self, from: savedData),
           !decoded.isEmpty {
            // Преобразуем ChildFamilyContact в ContactItem
            contacts = decoded.prefix(5).map { contact in
                ContactItem(
                    name: contact.name,
                    messages: 0, // TODO: Загрузить из API мониторинга
                    calls: 0, // TODO: Загрузить из API мониторинга
                    lastContact: "Недавно", // TODO: Загрузить из API мониторинга
                    color: .successGreen
                )
            }
            return
        }
        
        // Если нет сохранённых контактов, пробуем создать из family_members_list
        if let savedData = UserDefaults.standard.data(forKey: "family_members_list"),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData),
           !decoded.isEmpty {
            contacts = decoded.prefix(5).map { member in
                ContactItem(
                    name: member.name,
                    messages: 0, // TODO: Загрузить из API мониторинга
                    calls: 0, // TODO: Загрузить из API мониторинга
                    lastContact: "Недавно", // TODO: Загрузить из API мониторинга
                    color: .successGreen
                )
            }
            return
        }
        
        // Если ничего не найдено - пустой список
        contacts = []
        
        print("✅ Загружено контактов: \(contacts.count)")
    }
}

struct ContactItem: Identifiable {
    let id = UUID()
    let name: String
    let messages: Int
    let calls: Int
    let lastContact: String
    let color: Color
}

// MARK: 6. Остальные настройки и просмотры

// MARK: Настройки времени

struct ScreenTimeSettingsModal: View {
    @Binding var isPresented: Bool
    
    // Сохранение настроек в UserDefaults
    @AppStorage("screen_time_weekday_limit") private var weekdayLimit: Double = 120 // минуты
    @AppStorage("screen_time_weekend_limit") private var weekendLimit: Double = 180 // минуты
    @AppStorage("screen_time_is_weekday_selected") private var isWeekdaySelected = true
    
    var body: some View {
        FamilyModalBaseView(
            title: "⏱️ Настройка экранного времени",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Выбор режима
                HStack(spacing: Spacing.m) {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = true
                    }) {
                        Text("Будни")
                            .font(.bodyBold)
                            .foregroundColor(isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                    
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = false
                    }) {
                        Text("Выходные")
                            .font(.bodyBold)
                            .foregroundColor(!isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(!isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                }
                
                // Ползунок лимита
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text("Лимит времени")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("\(Int(isWeekdaySelected ? weekdayLimit : weekendLimit)) мин")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Slider(value: isWeekdaySelected ? $weekdayLimit : $weekendLimit, in: 30...480, step: 15) {
                        Text("Лимит")
                    }
                    .tint(.secondaryGold)
                    
                    HStack {
                        Text("30 мин")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        Spacer()
                        
                        Text("8 часов")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Рекомендации
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("💡 Рекомендации:")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    VStack(alignment: .leading, spacing: 6) {
                        Text("• Дети 6-10 лет: 1-2 часа в день")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        
                        Text("• Подростки: 2-3 часа в день")
                            .font(.body)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(Spacing.m)
                .background(Color.secondaryGold.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    print("✅ Экранное время сохранено: будни \(Int(weekdayLimit)) мин, выходные \(Int(weekendLimit)) мин")
                isPresented = false
                }) {
                    Text("Сохранить")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onChange(of: weekdayLimit) { newValue in
            print("✅ Лимит будних дней: \(Int(newValue)) мин")
        }
        .onChange(of: weekendLimit) { newValue in
            print("✅ Лимит выходных: \(Int(newValue)) мин")
        }
    }
}

struct ScheduleSettingsModal: View {
    @Binding var isPresented: Bool
    
    // Сохранение дат через TimeInterval в UserDefaults
    @AppStorage("schedule_weekday_start") private var weekdayStartInterval: Double = 0
    @AppStorage("schedule_weekday_end") private var weekdayEndInterval: Double = 0
    @AppStorage("schedule_weekend_start") private var weekendStartInterval: Double = 0
    @AppStorage("schedule_weekend_end") private var weekendEndInterval: Double = 0
    @AppStorage("schedule_is_weekday_selected") private var isWeekdaySelected = true
    
    // Вычисляемые свойства для работы с Date
    private var weekdayStart: Binding<Date> {
        Binding(
            get: {
                weekdayStartInterval == 0 ? Date() : Date(timeIntervalSince1970: weekdayStartInterval)
            },
            set: { weekdayStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekdayEnd: Binding<Date> {
        Binding(
            get: {
                weekdayEndInterval == 0 ? Date() : Date(timeIntervalSince1970: weekdayEndInterval)
            },
            set: { weekdayEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekendStart: Binding<Date> {
        Binding(
            get: {
                weekendStartInterval == 0 ? Date() : Date(timeIntervalSince1970: weekendStartInterval)
            },
            set: { weekendStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var weekendEnd: Binding<Date> {
        Binding(
            get: {
                weekendEndInterval == 0 ? Date() : Date(timeIntervalSince1970: weekendEndInterval)
            },
            set: { weekendEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: "📅 Настройка расписания",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Выбор режима
                HStack(spacing: Spacing.m) {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = true
                    }) {
                        Text("Будни")
                            .font(.bodyBold)
                            .foregroundColor(isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                    
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        isWeekdaySelected = false
                    }) {
                        Text("Выходные")
                            .font(.bodyBold)
                            .foregroundColor(!isWeekdaySelected ? .white : .textSecondary)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(!isWeekdaySelected ? Color.secondaryGold : Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                    }
                }
                
                // Время начала и окончания
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Доступ с:")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: isWeekdaySelected ? weekdayStart : weekendStart, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Доступ до:")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: isWeekdaySelected ? weekdayEnd : weekendEnd, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    let formatter = DateFormatter()
                    formatter.timeStyle = .short
                    print("✅ Расписание сохранено: будни \(formatter.string(from: weekdayStart.wrappedValue)) - \(formatter.string(from: weekdayEnd.wrappedValue)), выходные \(formatter.string(from: weekendStart.wrappedValue)) - \(formatter.string(from: weekendEnd.wrappedValue))")
                    isPresented = false
                }) {
                    Text("Сохранить")
                        .font(.bodyBold)
            .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onAppear {
            // Инициализация дат по умолчанию если они не сохранены
            if weekdayStartInterval == 0 {
                weekdayStartInterval = Date().timeIntervalSince1970
            }
            if weekdayEndInterval == 0 {
                weekdayEndInterval = Date().timeIntervalSince1970
            }
            if weekendStartInterval == 0 {
                weekendStartInterval = Date().timeIntervalSince1970
            }
            if weekendEndInterval == 0 {
                weekendEndInterval = Date().timeIntervalSince1970
            }
        }
    }
}

struct SleepTimeSettingsModal: View {
    @Binding var isPresented: Bool
    
    // Сохранение дат через TimeInterval в UserDefaults
    @AppStorage("sleep_bedtime_start") private var bedtimeStartInterval: Double = 0
    @AppStorage("sleep_bedtime_end") private var bedtimeEndInterval: Double = 0
    @AppStorage("sleep_emergency_calls_enabled") private var isEmergencyCallsEnabled = true
    
    // Вычисляемые свойства для работы с Date
    private var bedtimeStart: Binding<Date> {
        Binding(
            get: {
                bedtimeStartInterval == 0 ? Date() : Date(timeIntervalSince1970: bedtimeStartInterval)
            },
            set: { bedtimeStartInterval = $0.timeIntervalSince1970 }
        )
    }
    
    private var bedtimeEnd: Binding<Date> {
        Binding(
            get: {
                bedtimeEndInterval == 0 ? Date() : Date(timeIntervalSince1970: bedtimeEndInterval)
            },
            set: { bedtimeEndInterval = $0.timeIntervalSince1970 }
        )
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: "🌙 Настройка времени сна",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Время сна
                VStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Блокировка с:")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: bedtimeStart, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                    
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("Блокировка до:")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        DatePicker("", selection: bedtimeEnd, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .labelsHidden()
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Экстренные вызовы
                FamilyContentBlockItem(
                    icon: "🆘",
                    title: "Экстренные вызовы",
                    description: "Разрешить звонки родителям во время блокировки",
                    isEnabled: $isEmergencyCallsEnabled
                )
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    let formatter = DateFormatter()
                    formatter.timeStyle = .short
                    print("✅ Время сна сохранено: \(formatter.string(from: bedtimeStart.wrappedValue)) - \(formatter.string(from: bedtimeEnd.wrappedValue)), экстренные звонки \(isEmergencyCallsEnabled ? "ВКЛ" : "ВЫКЛ")")
                    isPresented = false
                }) {
                    Text("Сохранить")
                        .font(.bodyBold)
                .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onAppear {
            // Инициализация дат по умолчанию если они не сохранены
            if bedtimeStartInterval == 0 {
                bedtimeStartInterval = Date().timeIntervalSince1970
            }
            if bedtimeEndInterval == 0 {
                bedtimeEndInterval = Date().timeIntervalSince1970
            }
        }
        .onChange(of: isEmergencyCallsEnabled) { newValue in
            print("✅ Экстренные звонки: \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
    }
}

struct AppLimitsSettingsModal: View {
    @Binding var isPresented: Bool
    
    // Сохранение лимитов приложений в UserDefaults
    private let limitsKey = "app_limits_settings"
    
    @State private var appLimits: [AppLimitItem] = []
    
    // Загрузка лимитов из UserDefaults
    private func loadAppLimits() {
        if let data = UserDefaults.standard.data(forKey: limitsKey),
           let decoded = try? JSONDecoder().decode([AppLimitItemCodable].self, from: data) {
            appLimits = decoded.map { AppLimitItem(app: $0.app, limit: $0.limit, color: Color(hex: $0.colorHex)) }
        } else {
            // Значения по умолчанию
            appLimits = [
                AppLimitItem(app: "Instagram", limit: 30.0, color: .purple),
                AppLimitItem(app: "TikTok", limit: 20.0, color: .black),
                AppLimitItem(app: "WhatsApp", limit: 60.0, color: .green),
                AppLimitItem(app: "Telegram", limit: 60.0, color: .blue),
                AppLimitItem(app: "YouTube", limit: 45.0, color: .red),
                AppLimitItem(app: "VK", limit: 30.0, color: .blue),
                AppLimitItem(app: "Одноклассники", limit: 20.0, color: .orange),
                AppLimitItem(app: "Discord", limit: 30.0, color: .indigo),
                AppLimitItem(app: "Игры", limit: 60.0, color: .pink)
            ]
        }
    }
    
    // Сохранение лимитов в UserDefaults
    private func saveAppLimits() {
        let codable = appLimits.map { AppLimitItemCodable(app: $0.app, limit: $0.limit, colorHex: "") }
        if let encoded = try? JSONEncoder().encode(codable) {
            UserDefaults.standard.set(encoded, forKey: limitsKey)
        }
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: "⏰ Лимиты по приложениям",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach($appLimits) { $limit in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(limit.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(Int(limit.limit)) мин/день")
                                .font(.bodyBold)
                                .foregroundColor(.secondaryGold)
                        }
                        
                        Slider(value: $limit.limit, in: 5...120, step: 5) {
                            Text(limit.app)
                        }
                        .tint(limit.color)
                        
                        HStack {
                            Text("5 мин")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            Spacer()
                            
                            Text("2 часа")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                    saveAppLimits()
                    print("✅ Лимиты приложений сохранены: \(appLimits.count) приложений")
                isPresented = false
                }) {
                    Text("Сохранить все")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onAppear {
            loadAppLimits()
        }
    }
}

// Вспомогательная структура для Codable
struct AppLimitItemCodable: Codable {
    let app: String
    var limit: Double
    let colorHex: String
}

struct AppLimitItem: Identifiable {
    let id = UUID()
    var app: String
    var limit: Double
    let color: Color
}

// MARK: Геолокация

struct GeofencesSettingsModal: View {
    @Binding var isPresented: Bool
    
    // Сохранение геозон в UserDefaults
    private let geofencesKey = "geofences_settings"
    
    @State private var geofences: [GeofenceItem] = []
    
    @State private var showAddForm = false
    @State private var newGeofenceName = ""
    @State private var newGeofenceAddress = ""
    @State private var newGeofenceRadius: Double = 100
    
    // Загрузка геозон из UserDefaults
    private func loadGeofences() {
        if let data = UserDefaults.standard.data(forKey: geofencesKey),
           let decoded = try? JSONDecoder().decode([GeofenceItemCodable].self, from: data) {
            geofences = decoded.map { GeofenceItem(name: $0.name, address: $0.address, radius: $0.radius) }
        } else {
            // Значения по умолчанию
            geofences = [
                GeofenceItem(name: "Дом", address: "ул. Ленина, 42", radius: 100),
                GeofenceItem(name: "Школа", address: "ул. Пушкина, 15", radius: 200)
            ]
        }
    }
    
    // Сохранение геозон в UserDefaults
    private func saveGeofences() {
        let codable = geofences.map { GeofenceItemCodable(name: $0.name, address: $0.address, radius: $0.radius) }
        if let encoded = try? JSONEncoder().encode(codable) {
            UserDefaults.standard.set(encoded, forKey: geofencesKey)
        }
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: "🗺️ Настройка геозон",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Существующие геозоны
                ForEach($geofences) { $geofence in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(geofence.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                geofences.removeAll { $0.id == geofence.id }
                                saveGeofences()
                            }) {
                                Image(systemName: "trash")
                                    .font(.body)
                                    .foregroundColor(.dangerRed)
                            }
                        }
                        
                        Text(geofence.address)
                            .font(.body)
                            .foregroundColor(.textSecondary)
                        
                        HStack {
                            Text("Радиус:")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            
                            Text("\(Int(geofence.radius)) м")
                                .font(.caption)
                                .foregroundColor(.secondaryGold)
                                .fontWeight(.semibold)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
                
                // Форма добавления
                if showAddForm {
                    VStack(spacing: Spacing.m) {
                        TextField("Название (например: Дом)", text: $newGeofenceName)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                            .padding(Spacing.m)
                            .background(Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                        
                        TextField("Адрес", text: $newGeofenceAddress)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                            .padding(Spacing.m)
                            .background(Color.backgroundMedium.opacity(0.5))
                            .cornerRadius(CornerRadius.medium)
                        
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            HStack {
                                Text("Радиус")
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Spacer()
                                
                                Text("\(Int(newGeofenceRadius)) м")
                                    .font(.bodyBold)
                                    .foregroundColor(.secondaryGold)
                            }
                            
                            Slider(value: $newGeofenceRadius, in: 50...500, step: 10) {
                                Text("Радиус")
                            }
                            .tint(.secondaryGold)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                        
                        HStack(spacing: Spacing.m) {
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                showAddForm = false
                            }) {
                                Text("Отмена")
                                    .font(.body)
                                    .foregroundColor(.textSecondary)
                                    .frame(maxWidth: .infinity)
                                    .padding(Spacing.m)
                                    .background(Color.backgroundMedium.opacity(0.5))
                                    .cornerRadius(CornerRadius.medium)
                            }
                            
                            Button(action: {
                                HapticFeedback.impact(.medium)
                                geofences.append(GeofenceItem(name: newGeofenceName, address: newGeofenceAddress, radius: newGeofenceRadius))
                                newGeofenceName = ""
                                newGeofenceAddress = ""
                                newGeofenceRadius = 100
                                showAddForm = false
                                saveGeofences()
                            }) {
                                Text("Добавить")
                                    .font(.bodyBold)
            .foregroundColor(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding(Spacing.m)
                                    .background(Color.secondaryGold)
                                    .cornerRadius(CornerRadius.medium)
                            }
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.secondaryGold.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                } else {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        showAddForm = true
                    }) {
                        HStack {
                            Image(systemName: "plus.circle.fill")
                                .font(.body)
                                .foregroundColor(.secondaryGold)
                            
                            Text("Добавить геозону")
                                .font(.bodyBold)
                                .foregroundColor(.secondaryGold)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold.opacity(0.2))
                        .cornerRadius(CornerRadius.medium)
                        .overlay(
                            RoundedRectangle(cornerRadius: CornerRadius.medium)
                                .stroke(Color.secondaryGold.opacity(0.5), lineWidth: 1)
                        )
                    }
                }
            }
        }
        .onAppear {
            loadGeofences()
        }
    }
}

// Вспомогательная структура для Codable
struct GeofenceItemCodable: Codable {
    let name: String
    let address: String
    let radius: Double
}

struct GeofenceItem: Identifiable {
    let id = UUID()
    let name: String
    let address: String
    let radius: Double
}

struct LocationHistoryDetailModal: View {
    @Binding var isPresented: Bool
    
    @State private var locationHistory: [LocationHistoryItem] = [
        LocationHistoryItem(time: "08:30", location: "ул. Ленина, 42", action: "Выход из дома", icon: "🚶"),
        LocationHistoryItem(time: "09:15", location: "ул. Пушкина, 15", action: "Прибытие в школу", icon: "✅"),
        LocationHistoryItem(time: "15:45", location: "ул. Ленина, 42", action: "Возвращение домой", icon: "🏠"),
        LocationHistoryItem(time: "17:30", location: "ТЦ Мега", action: "Посещение торгового центра", icon: "🛒")
    ]
    
    @State private var frequentPlaces: [FrequentPlace] = [
        FrequentPlace(name: "Дом", visits: 45, color: .successGreen),
        FrequentPlace(name: "Школа", visits: 32, color: .blue),
        FrequentPlace(name: "ТЦ Мега", visits: 8, color: .warningOrange)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: "📍 История перемещений",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Частые места
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("Частые места за 30 дней")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(frequentPlaces) { place in
                        HStack {
                            Text(place.name)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(place.visits) визитов")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
                
                Divider()
                
                // История событий
                VStack(alignment: .leading, spacing: Spacing.m) {
                    Text("История событий сегодня")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    ForEach(locationHistory) { item in
                        HStack(spacing: Spacing.m) {
                            Text(item.icon)
                                .font(.system(size: 32))
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.action)
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                                
                                Text(item.location)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Spacer()
                            
                            Text(item.time)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        .padding(Spacing.m)
                        .background(Color.backgroundMedium.opacity(0.3))
                        .cornerRadius(CornerRadius.medium)
                    }
                }
            }
        }
    }
}

struct LocationHistoryItem: Identifiable {
    let id = UUID()
    let time: String
    let location: String
    let action: String
    let icon: String
}

struct FrequentPlace: Identifiable {
    let id = UUID()
    let name: String
    let visits: Int
    let color: Color
}

// MARK: Отчёты

struct WeeklyReportDetailModal: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        FamilyModalBaseView(
            title: "📅 \(localizationManager.localized("family_weekly_report"))",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Статистика по категориям
                ReportStatCard(icon: "🌐", title: localizationManager.localized("family_web_activity"), value: "342 \(localizationManager.localized("family_sites"))", color: .blue)
                ReportStatCard(icon: "📱", title: localizationManager.localized("family_applications"), value: "28 \(localizationManager.localized("family_apps"))", color: .purple)
                ReportStatCard(icon: "⏰", title: localizationManager.localized("family_screen_time"), value: "45ч 23мин", color: .orange)
                ReportStatCard(icon: "🚫", title: localizationManager.localized("family_blocked_attempts"), value: "1245 \(localizationManager.localized("family_attempts"))", color: .red)
                ReportStatCard(icon: "📍", title: localizationManager.localized("family_movements"), value: "32 \(localizationManager.localized("family_events"))", color: .green)
                ReportStatCard(icon: "⚠️", title: localizationManager.localized("family_warnings_new"), value: "2 \(localizationManager.localized("family_new"))", color: .warningOrange)
            }
        }
    }
}

struct ReportStatCard: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 32))
                .frame(width: 50, height: 50)
                .background(color.opacity(0.2))
                .cornerRadius(25)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.body)
                    .foregroundColor(.textSecondary)
                
                Text(value)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.3))
        .cornerRadius(CornerRadius.medium)
    }
}

struct SuspiciousActivityDetailModal: View {
    @Binding var isPresented: Bool
    
    @State private var warnings: [SuspiciousWarning] = [
        SuspiciousWarning(text: "Попытка доступа к заблокированному сайту", level: .high, time: "2 часа назад"),
        SuspiciousWarning(text: "Превышено экранное время на 15 минут", level: .medium, time: "5 часов назад"),
        SuspiciousWarning(text: "Неизвестный контакт в сообщениях", level: .high, time: "1 день назад"),
        SuspiciousWarning(text: "Попытка установки запрещённого приложения", level: .high, time: "2 дня назад")
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: "⚠️ Подозрительная активность",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(warnings) { warning in
                    HStack(spacing: Spacing.m) {
                        Image(systemName: warning.level == .high ? "exclamationmark.triangle.fill" : "exclamationmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(warning.level == .high ? .dangerRed : .warningOrange)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(warning.text)
                                .font(.body)
                                .foregroundColor(.textPrimary)
                            
                            Text(warning.time)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(warning.level == .high ? Color.dangerRed.opacity(0.1) : Color.warningOrange.opacity(0.1))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(warning.level == .high ? Color.dangerRed.opacity(0.5) : Color.warningOrange.opacity(0.5), lineWidth: 2)
                    )
                }
            }
        }
    }
}

struct SuspiciousWarning: Identifiable {
    let id = UUID()
    let text: String
    let level: WarningLevel
    let time: String
    
    enum WarningLevel {
        case high, medium
    }
}

struct TopSitesDetailModal: View {
    @Binding var isPresented: Bool
    
    @State private var topSites: [TopSiteItem] = [
        TopSiteItem(site: "youtube.com", visits: 142, time: "8ч 24мин", category: "Видео", color: .red),
        TopSiteItem(site: "instagram.com", visits: 89, time: "4ч 12мин", category: "Соц. сети", color: .purple),
        TopSiteItem(site: "vk.com", visits: 67, time: "2ч 45мин", category: "Соц. сети", color: .blue),
        TopSiteItem(site: "google.com", visits: 45, time: "1ч 15мин", category: "Поиск", color: .blue),
        TopSiteItem(site: "tiktok.com", visits: 34, time: "3ч 20мин", category: "Видео", color: .black)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: "🌐 Top-5 сайтов",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(Array(topSites.enumerated()), id: \.element.id) { index, site in
                    HStack(spacing: Spacing.m) {
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(site.site)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text("\(site.visits) визитов")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text(site.time)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            Text(site.category)
                                .font(.captionSmall)
                                .foregroundColor(site.color)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(site.color.opacity(0.2))
                                .cornerRadius(8)
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
    }
}

struct TopSiteItem: Identifiable {
    let id = UUID()
    let site: String
    let visits: Int
    let time: String
    let category: String
    let color: Color
}

struct TopAppsDetailModal: View {
    @Binding var isPresented: Bool
    
    @State private var topApps: [TopAppItem] = [
        TopAppItem(app: "Instagram", time: "8ч 24мин", limit: "30мин/день", exceeded: true, color: .purple),
        TopAppItem(app: "TikTok", time: "4ч 12мин", limit: "20мин/день", exceeded: true, color: .black),
        TopAppItem(app: "YouTube", time: "3ч 45мин", limit: "45мин/день", exceeded: true, color: .red),
        TopAppItem(app: "WhatsApp", time: "1ч 30мин", limit: "60мин/день", exceeded: false, color: .green),
        TopAppItem(app: "VK", time: "45мин", limit: "30мин/день", exceeded: true, color: .blue)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: "📱 Top-5 приложений",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(Array(topApps.enumerated()), id: \.element.id) { index, app in
                    HStack(spacing: Spacing.m) {
                        Text("\(index + 1)")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                            .frame(width: 32, height: 32)
                            .background(Color.secondaryGold.opacity(0.2))
                            .cornerRadius(16)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(app.app)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            HStack(spacing: Spacing.s) {
                                Text(app.time)
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("•")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                
                                Text("Лимит: \(app.limit)")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                            }
                            
                            if app.exceeded {
                                HStack {
                                    Image(systemName: "exclamationmark.triangle.fill")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                    
                                    Text("Превышен лимит")
                                        .font(.captionSmall)
                                        .foregroundColor(.dangerRed)
                                        .fontWeight(.semibold)
                                }
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(Color.dangerRed.opacity(0.2))
                                .cornerRadius(8)
                            }
                        }
                        
                        Spacer()
                    }
                    .padding(Spacing.m)
                    .background(app.exceeded ? Color.dangerRed.opacity(0.1) : Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .stroke(app.exceeded ? Color.dangerRed.opacity(0.5) : Color.clear, lineWidth: 2)
                    )
                }
            }
        }
    }
}

struct TopAppItem: Identifiable {
    let id = UUID()
    let app: String
    let time: String
    let limit: String
    let exceeded: Bool
    let color: Color
}

struct UsageHoursDetailModal: View {
    @Binding var isPresented: Bool
    
    @State private var usageHours: [UsageHourItem] = [
        UsageHourItem(hour: "06:00-08:00", usage: 15, level: .low, color: .blue),
        UsageHourItem(hour: "08:00-12:00", usage: 35, level: .medium, color: .green),
        UsageHourItem(hour: "12:00-16:00", usage: 45, level: .high, color: .orange),
        UsageHourItem(hour: "16:00-20:00", usage: 80, level: .veryHigh, color: .red),
        UsageHourItem(hour: "20:00-22:00", usage: 60, level: .high, color: .orange),
        UsageHourItem(hour: "22:00-00:00", usage: 25, level: .medium, color: .green),
        UsageHourItem(hour: "00:00-06:00", usage: 5, level: .low, color: .blue)
    ]
    
    var body: some View {
        FamilyModalBaseView(
            title: "📊 Пиковые часы активности",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                ForEach(usageHours) { item in
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text(item.hour)
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Text("\(item.usage)%")
                                .font(.bodyBold)
                                .foregroundColor(item.color)
                        }
                        
                        GeometryReader { geometry in
                            ZStack(alignment: .leading) {
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(Color.backgroundMedium.opacity(0.3))
                                    .frame(height: 20)
                                
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(item.color)
                                    .frame(width: geometry.size.width * CGFloat(item.usage) / 100, height: 20)
                            }
                        }
                        .frame(height: 20)
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
    }
}

struct UsageHourItem: Identifiable {
    let id = UUID()
    let hour: String
    let usage: Int
    let level: UsageLevel
    let color: Color
    
    enum UsageLevel {
        case low, medium, high, veryHigh
    }
}

struct BypassAttemptsDetailModal: View {
    @Binding var isPresented: Bool
    
    @StateObject private var manager = ParentalControlManager.shared
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Статистика (загружается через API)
    @State private var today: Int = 0
    @State private var week: Int = 0
    @State private var blocked: Int = 0
    @State private var incognitoCount: Int = 0
    @State private var torCount: Int = 0
    @State private var proxyCount: Int = 0
    @State private var isLoading: Bool = true
    
    var body: some View {
        FamilyModalBaseView(
            title: "🚨 Попытки обхода блокировок",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                if isLoading {
                    ProgressView()
                        .padding(Spacing.l)
                } else {
                    // Общая статистика
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("📊 Статистика:")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                        
                        HStack(spacing: Spacing.m) {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Попыток сегодня")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                Text("\(today)")
                                    .font(.bodyBold)
                                    .foregroundColor(.textPrimary)
                            }
                            
                            Spacer()
                            
                            VStack(alignment: .trailing, spacing: 4) {
                                Text("Всего за неделю")
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                Text("\(week)")
                                    .font(.bodyBold)
                                    .foregroundColor(.warningOrange)
                            }
                        }
                        
                        HStack {
                            Text("Заблокировано")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(blocked)")
                                .font(.bodyBold)
                                .foregroundColor(.successGreen)
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                    
                    // Детализация по типам
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        Text("📋 Детализация по типам:")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                        
                        // Скрытый режим
                        BypassTypeCard(
                            icon: "🕶️",
                            title: "Скрытый режим",
                            count: incognitoCount,
                            color: .warningOrange
                        )
                        
                        // Tor
                        BypassTypeCard(
                            icon: "🧅",
                            title: "Tor",
                            count: torCount,
                            color: .dangerRed
                        )
                        
                        // Proxy
                        BypassTypeCard(
                            icon: "🔀",
                            title: "Скрытие IP (адрес)",
                            count: proxyCount,
                            color: .infoBlue
                        )
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onAppear {
            loadBypassStatistics()
        }
    }
    
    private func loadBypassStatistics() {
        isLoading = true
        manager.getBypassStats(childId: selectedChild) { result in
            DispatchQueue.main.async {
                self.isLoading = false
                switch result {
                case .success(let stats):
                    self.today = stats.today
                    self.week = stats.week
                    self.blocked = stats.blocked
                    self.incognitoCount = stats.incognito
                    self.torCount = stats.tor
                    self.proxyCount = stats.proxy
                case .failure(let error):
                    print("⚠️ Ошибка загрузки статистики обхода: \(error.localizedDescription)")
                    // Оставляем значения по умолчанию
                }
            }
        }
    }
}

// MARK: - Bypass Type Card Component

struct BypassTypeCard: View {
    let icon: String
    let title: String
    let count: Int
    let color: Color
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            Text(icon)
                .font(.system(size: 32))
                .frame(width: 50, height: 50)
                .background(color.opacity(0.2))
                .cornerRadius(25)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                
                Text("\(count) попыток")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            Spacer()
            
            Text("\(count)")
                .font(.title3)
                .foregroundColor(color)
                .bold()
        }
        .padding(Spacing.m)
        .background(Color.backgroundMedium.opacity(0.2))
        .cornerRadius(CornerRadius.medium)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .stroke(color.opacity(0.5), lineWidth: 2)
        )
    }
}

// BypassAttempt (старая версия для модалов) - переименована для избежания конфликта с ParentalControlManager.BypassAttempt
struct BypassAttemptOld: Identifiable {
    let id = UUID()
    let method: String
    let count: Int
    let lastTime: String
    let color: Color
}

// MARK: YouTube настройки

struct YouTubeSettingsModal: View {
    @Binding var isPresented: Bool
    
    // Сохранение настроек YouTube в UserDefaults
    @AppStorage("youtube_safe_mode") private var isSafeModeEnabled = true
    @AppStorage("youtube_age_restriction_enabled") private var isAgeRestrictionEnabled = true
    @AppStorage("youtube_age_restriction") private var ageRestriction = 12
    @AppStorage("youtube_time_limit") private var timeLimit: Double = 45
    
    var body: some View {
        FamilyModalBaseView(
            title: "📺 Настройка YouTube",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.l) {
                // Безопасный режим
                FamilyContentBlockItem(
                    icon: "🛡️",
                    title: "Безопасный режим",
                    description: "Фильтрация нежелательного контента",
                    isEnabled: $isSafeModeEnabled
                )
                
                // Возрастные ограничения
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text("Возрастные ограничения")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Toggle("", isOn: $isAgeRestrictionEnabled)
                            .labelsHidden()
                            .tint(.secondaryGold)
                    }
                    
                    if isAgeRestrictionEnabled {
                        VStack(alignment: .leading, spacing: Spacing.s) {
                            Text("Ограничение: 12+")
                                .font(.body)
                                .foregroundColor(.textSecondary)
                            
                            Text("Доступен контент для возраста 12 лет и старше")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // Лимит времени
                VStack(alignment: .leading, spacing: Spacing.m) {
                    HStack {
                        Text("Лимит времени")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                        
                        Spacer()
                        
                        Text("\(Int(timeLimit)) мин/день")
                            .font(.bodyBold)
                            .foregroundColor(.secondaryGold)
                    }
                    
                    Slider(value: $timeLimit, in: 15...120, step: 15) {
                        Text("Лимит")
                    }
                    .tint(.secondaryGold)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                Button(action: {
                    HapticFeedback.impact(.medium)
                isPresented = false
                }) {
                    Text("Сохранить")
                        .font(.bodyBold)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(Spacing.m)
                        .background(Color.secondaryGold)
                        .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onChange(of: isSafeModeEnabled) { newValue in
            print("✅ YouTube Safe Mode: \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
        .onChange(of: isAgeRestrictionEnabled) { newValue in
            print("✅ YouTube Age Restriction: \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
        .onChange(of: ageRestriction) { newValue in
            print("✅ YouTube Age Restriction: \(newValue)+")
        }
        .onChange(of: timeLimit) { newValue in
            print("✅ YouTube Time Limit: \(Int(newValue)) мин/день")
        }
    }
}

// MARK: - Parental Control Settings Modal

struct FamilyParentalControlSettingsModal: View {
    @Binding var isPresented: Bool
    
    // Manager для применения правил
    @StateObject private var manager = ParentalControlManager.shared
    
    // Выбор ребёнка (динамический список) с сохранением в UserDefaults
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Уровень защиты по возрасту
    enum AgeGroup: String, CaseIterable {
        case toddler = "1-6 лет"
        case school = "7-13 лет"
        case teen = "14-17 лет"
        case adult = "18+ лет"
        
        var description: String {
            switch self {
            case .toddler: return "Максимальная защита (YouTube Kids, мультики 0+)"
            case .school: return "Средняя защита (YouTube Kids + SafeSearch, мультики до 12+)"
            case .teen: return "Умеренная защита (YouTube с фильтрами, мультики до 17+)"
            case .adult: return "Базовая защита (без ограничений)"
            }
        }
    }
    
    // Сохранение возраста в UserDefaults
    @AppStorage("parental_age_group") private var selectedAgeGroupRaw: String = AgeGroup.school.rawValue
    
    // Вычисляемое свойство для работы с enum
    private var selectedAgeGroup: AgeGroup {
        get {
            AgeGroup(rawValue: selectedAgeGroupRaw) ?? .school
        }
        set {
            selectedAgeGroupRaw = newValue.rawValue
        }
    }
    
    // Автоматические правила с сохранением в UserDefaults
    @AppStorage("parental_automated_rules_enabled") private var isAutomatedRulesEnabled: Bool = true // По умолчанию ВКЛЮЧЕНЫ
    @State private var showAutomatedRulesModal = false
    
    // Применение правил при изменении возраста
    private func applyAgeBasedRules() {
        guard isAutomatedRulesEnabled else { return }
        
        // Сохраняем настройки в UserDefaults
        let rules: [String: Any] = [
            "selectedChild": selectedChild,
            "ageGroup": selectedAgeGroup.rawValue,
            "isEnabled": isAutomatedRulesEnabled,
            "appliedDate": Date().timeIntervalSince1970
        ]
        
        // Сохраняем через UserDefaults
        UserDefaults.standard.set(rules, forKey: "parental_control_rules_\(selectedChild)")
        
        // Логируем применение правил
        print("✅ Правила применены для \(selectedChild), возраст: \(selectedAgeGroup.rawValue)")
        
        // Вызываем API через Manager для применения правил на бэкенде
        let parentalRules = ParentalControlRules(
            websiteBlocking: UserDefaults.standard.bool(forKey: "parental_website_blocking"),
            appBlocking: UserDefaults.standard.bool(forKey: "parental_app_blocking"),
            searchBlocking: UserDefaults.standard.bool(forKey: "parental_search_blocking"),
            safesearch: UserDefaults.standard.bool(forKey: "parental_safesearch"),
            screenTimeLimit: nil,
            bedtimeStart: nil,
            bedtimeEnd: nil,
            appLimits: nil,
            geofences: nil
        )
        
        // Преобразуем возрастную группу в формат API
        let ageGroupString: String = {
            switch selectedAgeGroup {
            case .toddler: return "1-6"
            case .school: return "7-13"
            case .teen: return "14-17"
            case .adult: return "18+"
            }
        }()
        
        manager.applyRules(
            childId: selectedChild,
            ageGroup: ageGroupString,
            rules: parentalRules
        ) { success, error in
            if success {
                print("✅ Правила применены через API для \(selectedChild)")
            } else {
                print("⚠️ Ошибка применения правил: \(error ?? "Неизвестная ошибка")")
            }
        }
    }
    
    var body: some View {
        FamilyModalBaseView(
            title: "⚙️ Настройки родительского контроля",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Выбор ребёнка
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Выберите ребёнка:")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Picker("Ребёнок", selection: $selectedChild) {
                        ForEach(children, id: \.self) { child in
                            Text(child).tag(child)
                        }
                    }
                    .pickerStyle(.segmented)
                    .tint(Color.secondaryGold)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // 2. Уровень защиты по возрасту
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("Уровень защиты:")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                    
                    Picker("Возраст", selection: Binding(
                        get: { selectedAgeGroup },
                        set: { newValue in
                            selectedAgeGroupRaw = newValue.rawValue
                        }
                    )) {
                        ForEach(AgeGroup.allCases, id: \.self) { age in
                            Text(age.rawValue).tag(age)
                        }
                    }
                    .pickerStyle(.menu)
                    .tint(Color.secondaryGold)
                    .onChange(of: selectedAgeGroupRaw) { _ in
                        // Автоматически применяем правила при изменении возраста
                        applyAgeBasedRules()
                    }
                    
                    Text(selectedAgeGroup.description)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .padding(.top, Spacing.xs)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
                
                // 3. Автоматические правила
                FamilyConfigButtonItem(
                    icon: "🤖",
                    title: "Автоматические правила",
                    description: isAutomatedRulesEnabled ? "Включены (фильтрация по возрасту активна)" : "Выключены",
                    buttonTitle: "Настроить",
                    action: { showAutomatedRulesModal = true }
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Информация
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("ℹ️ Как это работает:")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    Text("При изменении возраста ребёнка правила автоматически обновляются. Контент фильтруется по типу (YouTube, игры, соц. сети, мессенджеры).")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .padding(Spacing.m)
                .background(Color.secondaryGold.opacity(0.1))
                .cornerRadius(CornerRadius.medium)
                
                // Кнопка применения правил
                if isAutomatedRulesEnabled {
                    Button(action: {
                        HapticFeedback.impact(.medium)
                        applyAgeBasedRules()
                    }) {
                        Text("Применить правила")
                            .font(.bodyBold)
            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(Spacing.m)
                            .background(Color.secondaryGold)
                            .cornerRadius(CornerRadius.medium)
                    }
                    .padding(.top, Spacing.s)
                }
            }
        }
        .onAppear {
            // Применяем правила при открытии модала (если уже включены)
            if isAutomatedRulesEnabled {
                applyAgeBasedRules()
            }
        }
        .onChange(of: selectedChild) { _ in
            // Применяем правила при смене ребёнка
            if isAutomatedRulesEnabled {
                applyAgeBasedRules()
            }
        }
        .onChange(of: isAutomatedRulesEnabled) { newValue in
            if newValue {
                // Применяем правила при включении
                applyAgeBasedRules()
            }
            print("✅ Автоматические правила: \(newValue ? "ВКЛ" : "ВЫКЛ")")
        }
        .sheet(isPresented: $showAutomatedRulesModal) {
            AutomatedRulesModal(isPresented: $showAutomatedRulesModal, isEnabled: $isAutomatedRulesEnabled, ageGroup: selectedAgeGroup) {
                // Обновляем правила при изменении в модале автоматических правил
                applyAgeBasedRules()
            }
        }
    }
}

// MARK: - Automated Rules Modal

struct AutomatedRulesModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    let ageGroup: FamilyParentalControlSettingsModal.AgeGroup
    var onRulesChanged: (() -> Void)? = nil
    
    // Состояния для правил
    @State private var showAgeBasedFilteringExplanation = false
    
    var body: some View {
        FamilyModalBaseView(
            title: "🤖 Автоматические правила",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // Toggle включения правил
                FamilyContentBlockItem(
                    icon: "🤖",
                    title: "Включить автоматические правила",
                    description: isEnabled ? "Правила активны и работают автоматически" : "Правила отключены",
                    isEnabled: $isEnabled
                )
                .onChange(of: isEnabled) { newValue in
                    // Применяем правила при изменении toggle
                    print("✅ AutomatedRulesModal: правила \(newValue ? "ВКЛЮЧЕНЫ" : "ВЫКЛЮЧЕНЫ")")
                    if newValue {
                        onRulesChanged?()
                    }
                }
                
                if isEnabled {
                    Divider()
                        .background(Color.white.opacity(0.2))
                        .padding(.vertical, Spacing.s)
                    
                    // Правило 1: Фильтрация контента по возрасту (с объяснением)
                    VStack(alignment: .leading, spacing: Spacing.s) {
                        HStack {
                            Text("🎯 Фильтрация контента по возрасту")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                            
                            Spacer()
                            
                            Button(action: {
                                HapticFeedback.impact(.light)
                                showAgeBasedFilteringExplanation.toggle()
                            }) {
                                Image(systemName: showAgeBasedFilteringExplanation ? "chevron.up" : "chevron.down")
                                    .font(.system(size: 14))
                                    .foregroundColor(.secondaryGold)
                            }
                        }
                        
                        if showAgeBasedFilteringExplanation {
                            ageBasedFilteringExplanation
                        }
                    }
                    .padding(Spacing.m)
                    .background(Color.backgroundMedium.opacity(0.3))
                    .cornerRadius(CornerRadius.medium)
                }
            }
        }
        .onAppear {
            // Логируем текущее состояние при открытии
            print("✅ AutomatedRulesModal открыт: возраст \(ageGroup.rawValue), правила \(isEnabled ? "ВКЛ" : "ВЫКЛ")")
        }
    }
    
    private var ageBasedFilteringExplanation: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            Divider()
                .background(Color.white.opacity(0.2))
                .padding(.vertical, Spacing.xs)
            
            switch ageGroup {
            case .toddler:
                Text("📋 ДЛЯ 1-6 ЛЕТ:")
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("✅ YouTube: только YouTube Kids")
                    Text("✅ Мультики: только 0+ и 6+")
                    Text("✅ Игры: только образовательные")
                    Text("❌ Соц. сети: блокируются (Instagram, TikTok, VK)")
                    Text("❌ Мессенджеры: блокируются (WhatsApp, Telegram)")
                }
                .font(.caption)
                .foregroundColor(.textSecondary)
                
            case .school:
                Text("📋 ДЛЯ 7-13 ЛЕТ:")
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("✅ YouTube: YouTube Kids + обычный с SafeSearch")
                    Text("✅ Мультики: до 12+ (0+, 6+, 12+)")
                    Text("✅ Игры: до рейтинга 12+ (без 17+, 18+)")
                    Text("❌ Соц. сети: блокируются, кроме мессенджеров")
                    Text("✅ Мессенджеры: доступны с мониторингом")
                }
                .font(.caption)
                .foregroundColor(.textSecondary)
                
            case .teen:
                Text("📋 ДЛЯ 14-17 ЛЕТ:")
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("✅ YouTube: обычный с SafeSearch")
                    Text("✅ Мультики: до 17+ (все кроме 18+)")
                    Text("✅ Игры: до рейтинга 17+ (без 18+)")
                    Text("✅ Соц. сети: доступны с фильтрацией")
                    Text("✅ Мессенджеры: доступны с фильтрацией")
                }
                .font(.caption)
                .foregroundColor(.textSecondary)
                
            case .adult:
                Text("📋 ДЛЯ 18+ ЛЕТ:")
                    .font(.bodyBold)
                    .foregroundColor(.secondaryGold)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("✅ YouTube: весь доступен")
                    Text("✅ Мультики: все доступны")
                    Text("✅ Игры: все доступны")
                    Text("✅ Соц. сети: без ограничений")
                    Text("✅ Мессенджеры: без ограничений")
                }
                .font(.caption)
                .foregroundColor(.textSecondary)
            }
        }
        .padding(.top, Spacing.xs)
    }
}

// MARK: - Family Member Data Model

struct FamilyMemberData: Identifiable, Codable {
    let id: UUID
    let name: String
    let role: FamilyMemberCard.FamilyRole
    let avatar: String
    let status: FamilyMemberCard.ProtectionStatus
    let threatsBlocked: Int
    let lastActive: String
    
    init(id: UUID = UUID(), name: String, role: FamilyMemberCard.FamilyRole, avatar: String, status: FamilyMemberCard.ProtectionStatus, threatsBlocked: Int, lastActive: String) {
        self.id = id
        self.name = name
        self.role = role
        self.avatar = avatar
        self.status = status
        self.threatsBlocked = threatsBlocked
        self.lastActive = lastActive
    }
}

// MARK: - Codable Extensions для FamilyMemberCard типов

extension FamilyMemberCard.FamilyRole: Codable {
    enum CodableError: Error {
        case invalidValue(String)
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        
        switch rawValue {
        case "Родитель", "parent", "Parent": self = .parent
        case "Ребёнок", "child", "Child": self = .child
        case "Подросток", "teenager", "Teenager": self = .teenager
        case "Пожилой", "elderly", "Elderly", "Grandparent", "grandparent": self = .elderly
        default: throw CodableError.invalidValue(rawValue)
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(label)
    }
}

extension FamilyMemberCard.ProtectionStatus: Codable {
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        
        switch rawValue {
        case "Защищён", "protected", "Protected": self = .protected
        case "Внимание", "warning", "Warning": self = .warning
        case "Угроза", "danger", "Danger": self = .danger
        case "Оффлайн", "offline", "Offline": self = .offline
        default: self = .protected
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(label)
    }
}

// MARK: - Family Bypass Protection Modal

struct FamilyBypassProtectionModal: View {
    @Binding var isPresented: Bool
    @Binding var isEnabled: Bool
    
    // Manager для обработки защиты от обхода
    @StateObject private var manager = ParentalControlManager.shared
    
    // Выбранный ребёнок
    @AppStorage("parental_selected_child") private var selectedChild: String = ""
    
    // Список детей (динамический)
    @State private var children: [String] = []
    
    // Состояния для 3 переключателей с сохранением в UserDefaults
    @AppStorage("bypass_incognito_enabled") private var isIncognitoDetectionEnabled: Bool = true
    @AppStorage("bypass_tor_enabled") private var isTorDetectionEnabled: Bool = true
    @AppStorage("bypass_proxy_enabled") private var isProxyDetectionEnabled: Bool = true
    
    // Статистика
    @State private var attemptsToday: Int = 0
    @State private var attemptsWeek: Int = 47
    @State private var attemptsBlocked: Int = 47
    
    // Детализация по типам
    @State private var incognitoAttempts: Int = 15
    @State private var torAttempts: Int = 8
    @State private var proxyAttempts: Int = 6
    
    var body: some View {
        FamilyModalBaseView(
            title: "🚨 Защита от обхода",
            isPresented: $isPresented
        ) {
            VStack(spacing: Spacing.m) {
                // 1. Детекция Скрытого режима (было "Инкогнито")
                FamilyContentBlockItem(
                    icon: "🕶️",
                    title: "Детекция Скрытого режима",
                    description: "Приватный режим браузера",
                    isEnabled: $isIncognitoDetectionEnabled
                )
                
                // 2. Детекция Tor
                FamilyContentBlockItem(
                    icon: "🧅",
                    title: "Детекция Tor",
                    description: "Анонимный браузер",
                    isEnabled: $isTorDetectionEnabled
                )
                
                // 3. Детекция Proxy
                FamilyContentBlockItem(
                    icon: "🔀",
                    title: "Детекция Proxy",
                    description: "Скрытие IP (адрес)",
                    isEnabled: $isProxyDetectionEnabled
                )
                
                Divider()
                    .background(Color.white.opacity(0.2))
                    .padding(.vertical, Spacing.s)
                
                // Статистика
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text("📊 Статистика за неделю:")
                        .font(.bodyBold)
                        .foregroundColor(.secondaryGold)
                    
                    HStack(spacing: Spacing.m) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Попыток сегодня")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(attemptsToday)")
                                .font(.bodyBold)
                                .foregroundColor(.textPrimary)
                        }
                        
                        Spacer()
                        
                        VStack(alignment: .trailing, spacing: 4) {
                            Text("Всего за неделю")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Text("\(attemptsWeek)")
                                .font(.bodyBold)
                                .foregroundColor(.warningOrange)
                        }
                    }
                    
                    HStack {
                        Text("Заблокировано")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(attemptsBlocked)")
                            .font(.bodyBold)
                            .foregroundColor(.successGreen)
                    }
                    
                    // Детализация по типам (с заменой названий)
                    VStack(spacing: Spacing.xs) {
                        HStack {
                            Text("🕶️ Скрытый режим")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(incognitoAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text("🧅 Tor")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(torAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                        
                        HStack {
                            Text("🔀 Скрытие IP (адрес)")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                            Spacer()
                            Text("\(proxyAttempts)")
                                .font(.caption)
                                .foregroundColor(.textPrimary)
                        }
                    }
                    .padding(.top, Spacing.s)
                }
                .padding(Spacing.m)
                .background(Color.backgroundMedium.opacity(0.3))
                .cornerRadius(CornerRadius.medium)
            }
        }
        .onAppear {
            loadBypassStatistics()
        }
        .onChange(of: isIncognitoDetectionEnabled) { newValue in
            applyBypassProtection()
        }
        .onChange(of: isTorDetectionEnabled) { newValue in
            applyBypassProtection()
        }
        .onChange(of: isProxyDetectionEnabled) { newValue in
            applyBypassProtection()
        }
    }
    
    private func loadBypassStatistics() {
        // Загружаем статистику из API через manager
        manager.getBypassStats(childId: selectedChild) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let stats):
                    self.attemptsToday = stats.today
                    self.attemptsWeek = stats.week
                    self.attemptsBlocked = stats.blocked
                    self.incognitoAttempts = stats.incognito
                    self.torAttempts = stats.tor
                    self.proxyAttempts = stats.proxy
                case .failure(let error):
                    print("⚠️ Ошибка загрузки статистики обхода: \(error.localizedDescription)")
                    // Оставляем значения по умолчанию
                }
            }
        }
    }
    
    private func applyBypassProtection() {
        // Применяем настройки защиты от обхода через API
        manager.applyBypassProtection(
            childId: selectedChild,
            incognito: isIncognitoDetectionEnabled,
            tor: isTorDetectionEnabled,
            proxy: isProxyDetectionEnabled
        ) { success, errorMessage in
            DispatchQueue.main.async {
                if success {
                    print("✅ Защита от обхода применена: Скрытый режим=\(self.isIncognitoDetectionEnabled), Tor=\(self.isTorDetectionEnabled), Proxy=\(self.isProxyDetectionEnabled)")
                    // Обновляем статистику после применения
                    self.loadBypassStatistics()
                } else {
                    print("❌ Ошибка применения защиты от обхода: \(errorMessage ?? "Неизвестная ошибка")")
                }
            }
        }
    }
}

struct FamilyScreen_Previews: PreviewProvider {
    static var previews: some View {
        FamilyScreen()
    }
}