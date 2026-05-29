import SwiftUI

// Master Logger for navigation logging
private let logger = MasterLogger.shared

// MARK: - Navigation Manager для всех экранов ALADDIN - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
@MainActor
class NavigationManager: ObservableObject {
    // ✅ ИСПРАВЛЕНИЕ BUILD 90: Проверяем онбординг сразу при инициализации
    // Убираем страницу загрузки перед онбордингом для лучшего UX
    @Published var currentScreen: ALADDINScreen
    @Published var navigationStack: [ALADDINScreen] = []
    @Published var isPresentingModal: Bool = false
    @Published var currentModal: ALADDINModal? = nil
    @Published private(set) var isNavigatingBack: Bool = false
    @Published private(set) var isManuallyClosingPaymentQR: Bool = false
    @Published private(set) var debugLogs: [String] = []
    @Published private var lastScreenBeforePaymentQR: ALADDINScreen? = nil
    
    // ✅ ИСПРАВЛЕНИЕ: Добавляем для PaymentQRScreen через NavigationLink
    @Published var selectedTariffForPayment: Tariff? = nil

    /// Токен из `aladdin://bind?token=` или Universal Link — подставляется на экране присоединения.
    @Published var pendingDeviceBindToken: String? = nil

    /// Экран, на который возвращаемся из «Мир героев» (если стек навигации пуст/сброшен).
    @Published private(set) var companionReturnScreen: ALADDINScreen?
    
    // ✅ Стартовый экран: читаем только флаг онбординга (без записи), чтобы первый кадр SwiftUI
    // не строил OnboardingScreen до `WindowGroup.onAppear` → `initializeNavigation`.
    // BUILD 95: рекурсию вызывали сложные цепочки с @AppStorage; простой `bool(forKey:)` безопасен.
    init() {
        let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
        self.currentScreen = onboardingDone ? .main : .onboarding
        LaunchDiagnostics.appendStartupTrace("NavigationManager.init: currentScreen=\(self.currentScreen.rawValue) (UserDefaults hasCompletedOnboarding=\(onboardingDone))")
        print("🟢 NavigationManager.init: стартовый экран = \(self.currentScreen.rawValue) (онбординг завершён в UD: \(onboardingDone))")
    }
    
    // MARK: - Основные экраны (25)
    enum ALADDINScreen: String, CaseIterable {
        // Специальные экраны
        case loading = "LoadingScreen"

        // Основные экраны
        case main = "01_MainScreen"
        case family = "02_FamilyScreen"
        case networkProtection = "03_NetworkProtectionScreen"
        case analytics = "04_AnalyticsScreen"
        case settings = "05_SettingsScreen"
        case settingsTest = "SettingsTest"
        case settingsTestSuite = "SettingsTestSuite"
        case settingsFallback = "SettingsFallback"
        case aiAssistant = "06_AIAssistantScreen"
        case parentalControl = "07_ParentalControlScreen"
        case childInterface = "08_ChildInterfaceScreen"
        case childContent = "ChildContentScreen"
        case elderlyInterface = "09_ElderlyInterfaceScreen"
        case tariffs = "10_TariffsScreen"
        case profile = "11_ProfileScreen"
        case notifications = "12_NotificationsScreen"
        case support = "13_SupportScreen"
        case addMemberOptions = "AddMemberOptionsScreen"
        case onboarding = "14_OnboardingScreen"
        case privacyPolicy = "18_PrivacyPolicyScreen"
        case termsOfService = "19_TermsOfServiceScreen"
        case devices = "20_DevicesScreen"
        case joinDevice = "28_JoinDeviceScreen"
        case referral = "21_ReferralScreen"
        case deviceDetail = "22_DeviceDetailScreen"
        case familyChat = "23_FamilyChatScreen"
        case paymentQR = "25_PaymentQRScreen"
        case activationCode = "26_ActivationCodeScreen"
        
        // Игровые экраны
        case childRewards = "ChildRewardsScreen"
        case familyTournament = "FamilyTournamentView"
        case securityEducation = "SecurityEducationScreen"
        case gamesParentalControl = "GamesParentalControlView"
        case unicornPet = "UnicornPetView"
        case companionHome = "CompanionHomeScreen"
        case companionHub = "CompanionHubScreen"
        case companionConversation = "CompanionConversationScreen"
        
        // НОВЫЕ ИГРОВЫЕ ЭКРАНЫ (геймификация)
        case youngDefender = "YoungDefenderView"           // 🛡️ Юный защитник
        case familyProtector = "FamilyProtectorView"       // 🕵️ Я защитник
        case childGoalEditor = "ChildGoalEditorView"       // 🎯 Моя цель
        
        // Экраны защиты
        case threatProtection = "ThreatProtectionScreen"
        case threatProtectionSettings = "ThreatProtectionSettingsScreen"
        case iotSecurity = "IoTSecurityScreen"
        case advancedProtection = "AdvancedProtectionSettingsScreen"
        
        // Дополнительные экраны
        case mainWithRegistration = "MainScreenWithRegistration"
        case languageSettings = "LanguageSettingsScreen"
        case notificationSettings = "NotificationSettingsScreen"
        case widgetConfiguration = "WidgetConfigurationScreen"
        case rewardsModal = "RewardsModalView"
        case rewardsQuickModal = "RewardsQuickModal"
        case qrCode = "QRCodeModal"
        case invitationCode = "InvitationCodeInputModal"
        
        var displayName: String {
            switch self {
            case .loading: return "Загрузка"
            case .main: return "Главная"
            case .family: return "Семья"
            case .networkProtection: return "Защита сети"
            case .analytics: return "Аналитика"
            case .settings: return "Настройки"
            case .settingsTest: return "Тест настроек"
            case .settingsTestSuite: return "Набор тестов"
            case .settingsFallback: return "Запасные настройки"
            case .aiAssistant: return "AI Помощник"
            case .parentalControl: return "Родительский контроль"
            case .childInterface: return "Детский интерфейс"
            case .childContent: return "Контент для детей"
            case .elderlyInterface: return "Пожилой интерфейс"
            case .tariffs: return "Тарифы"
            case .profile: return "Профиль"
            case .notifications: return "Уведомления"
            case .support: return "Поддержка"
            case .addMemberOptions: return "Добавить участника"
            case .onboarding: return "Обучение"
            case .privacyPolicy: return "Политика конфиденциальности"
            case .termsOfService: return "Условия использования"
            case .devices: return "Устройства"
            case .joinDevice: return "Присоединить устройство"
            case .referral: return "Реферальная программа"
            case .deviceDetail: return "Детали устройства"
            case .familyChat: return "Семейный чат"
            case .paymentQR: return "Оплата QR"
            case .childRewards: return "Детские награды"
            case .familyTournament: return "Семейный турнир"
            case .securityEducation: return "Безопасность"
            case .gamesParentalControl: return "Игры и контроль"
            case .unicornPet: return "Единорог-питомец"
            case .companionHome: return "Мир героев"
            case .companionHub: return "Герои"
            case .companionConversation: return "Разговор"
            case .mainWithRegistration: return "Главная с регистрацией"
            case .languageSettings: return "Настройки языка"
            case .notificationSettings: return "Настройки уведомлений"
            case .widgetConfiguration: return "Настройка виджетов"
            case .rewardsModal: return "Модальное окно наград"
            case .rewardsQuickModal: return "Быстрое окно наград"
            case .qrCode: return "QR код"
            case .invitationCode: return "Ввод кода приглашения"
            case .youngDefender: return "Юный защитник"
            case .familyProtector: return "Я защитник семьи"
            case .childGoalEditor: return "Моя цель"
            case .activationCode: return "Активация кода"
            case .threatProtection: return "Защита от угроз"
            case .threatProtectionSettings: return "Настройки защиты"
            case .iotSecurity: return "IoT безопасность"
            case .advancedProtection: return "Расширенная защита"
            }
        }
        
        var icon: String {
            switch self {
            case .loading: return "hourglass"
            case .main: return "house.fill"
            case .family: return "person.3.fill"
            case .networkProtection: return "shield.fill"
            case .analytics: return "chart.bar.fill"
            case .settings: return "gearshape.fill"
            case .settingsTest: return "testtube.2"
            case .settingsTestSuite: return "checklist"
            case .settingsFallback: return "arrow.triangle.2.circlepath"
            case .aiAssistant: return "brain.head.profile"
            case .parentalControl: return "person.crop.circle.badge.checkmark"
            case .childInterface: return "figure.child"
            case .childContent: return "book.fill"
            case .elderlyInterface: return "person.crop.circle"
            case .tariffs: return "creditcard.fill"
            case .profile: return "person.fill"
            case .notifications: return "bell.fill"
            case .support: return "questionmark.circle.fill"
            case .addMemberOptions: return "person.badge.plus"
            case .onboarding: return "book.fill"
            case .privacyPolicy: return "doc.text.fill"
            case .termsOfService: return "doc.plaintext.fill"
            case .devices: return "iphone"
            case .joinDevice: return "iphone.and.arrow.forward.inward"
            case .referral: return "gift.fill"
            case .deviceDetail: return "info.circle.fill"
            case .familyChat: return "message.fill"
            case .paymentQR: return "qrcode"
            case .childRewards: return "star.fill"
            case .familyTournament: return "trophy.fill"
            case .securityEducation: return "shield.lefthalf.filled"
            case .gamesParentalControl: return "gamecontroller.fill"
            case .unicornPet: return "pawprint.fill"
            case .companionHome: return "person.2.wave.2.fill"
            case .companionHub: return "sparkles"
            case .companionConversation: return "bubble.left.and.bubble.right.fill"
            case .mainWithRegistration: return "house.fill"
            case .languageSettings: return "globe"
            case .notificationSettings: return "bell.badge.fill"
            case .widgetConfiguration: return "square.grid.3x3.fill"
            case .rewardsModal: return "gift.fill"
            case .rewardsQuickModal: return "gift.fill"
            case .youngDefender: return "shield.lefthalf.filled"
            case .familyProtector: return "sparkles"
            case .childGoalEditor: return "target"
            case .activationCode: return "key.fill"
            case .threatProtection: return "shield.lefthalf.filled"
            case .threatProtectionSettings: return "gearshape.2.fill"
            case .iotSecurity: return "wifi"
            case .advancedProtection: return "lock.shield.fill"
            case .qrCode: return "qrcode"
            case .invitationCode: return "keyboard"
            }
        }

        /// Выпадающий список экранов в шапке (`ALADDINNavigationBar`). В **Release** скрываем отладочные и модальные маршруты без полноценного стека.
        var isListedInProductionQuickNavigationMenu: Bool {
            switch self {
            case .notificationSettings, .rewardsModal, .rewardsQuickModal:
                return false
            // Служебные экраны настроек — никогда в быстром меню (и в Debug тоже).
            case .settingsTest, .settingsTestSuite, .settingsFallback:
                return false
            case .loading, .mainWithRegistration, .qrCode, .invitationCode:
                #if DEBUG
                return true
                #else
                return false
                #endif
            default:
                return true
            }
        }
    }
    
    // MARK: - Модальные окна
    enum ALADDINModal: String, CaseIterable {
        case addDevice = "AddDeviceModal"
        case editProfile = "EditProfileModal"
        case shareReferral = "ShareReferralModal"
        case qrCode = "QRCodeModal"
        case rewards = "RewardsModal"
        case settings = "SettingsModal"
        case help = "HelpModal"
        case about = "AboutModal"
        case crashDetectionAlert = "CrashDetectionAlertModal"
        
        var displayName: String {
            switch self {
            case .addDevice: return "Добавить устройство"
            case .editProfile: return "Редактировать профиль"
            case .shareReferral: return "Поделиться реферальным кодом"
            case .qrCode: return "QR код"
            case .rewards: return "Награды"
            case .settings: return "Настройки"
            case .help: return "Помощь"
            case .about: return "О приложении"
            case .crashDetectionAlert: return "Предупреждение об аварии"
            }
        }
    }
    
    // MARK: - Навигационные методы
    
    /// Переход к экрану
    func navigateTo(_ screen: ALADDINScreen) {
        logger.navigation(from: currentScreen.displayName, to: screen.displayName, function: #function)
        
        // ✅ ИСПРАВЛЕНИЕ: Весь NavigationManager работает под @MainActor,
        // поэтому выполняем изменения синхронно, без DispatchQueue.main.async.
        if case .paymentQR = screen {
            if currentScreen == .paymentQR {
                appendLog("⚠️ navigateTo(.paymentQR) отклонён: уже на PaymentQR")
                return
            }

            if let last = navigationStack.last, last == .paymentQR {
                appendLog("⚠️ navigateTo(.paymentQR) отклонён: PaymentQR уже находится в стеке")
                return
            }

            guard selectedTariffForPayment != nil else {
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: Попытка открыть PaymentQR без тарифа!")
                print("❌ selectedTariffForPayment = nil")
                appendLog("❌ navigateTo(.paymentQR) без выбранного тарифа")
                return
            }

            lastScreenBeforePaymentQR = currentScreen
            print("✅ PaymentQR: тариф установлен - \(selectedTariffForPayment?.id ?? "nil")")
            appendLog("✅ navigateTo(.paymentQR) из \(currentScreen)")
        }

        navigationStack.append(currentScreen)
        currentScreen = screen
        objectWillChange.send()
        appendLog("➡️ navigateTo(\(screen)) | стек = \(navigationStack)")
    }

    /// «Мир героев» — запоминаем экран-источник для корректного «Назад».
    func navigateToCompanionHome(returnTo: ALADDINScreen? = nil) {
        companionReturnScreen = returnTo ?? currentScreen
        navigateTo(.companionHome)
    }

    /// Возврат с CompanionHome: не уходим на `.main`, если вход был с наград/детского UI.
    func goBackFromCompanionHome() {
        if let target = companionReturnScreen {
            companionReturnScreen = nil
            appendLog("⬅️ goBackFromCompanionHome → \(target) (explicit return)")
            if navigationStack.last == target {
                _ = navigationStack.popLast()
            } else if let idx = navigationStack.lastIndex(of: target) {
                navigationStack.removeSubrange((idx + 1)...)
            }
            currentScreen = target
            objectWillChange.send()
            return
        }
        goBack()
    }
    
    /// Возврат к предыдущему экрану
    func goBack(reason: String? = nil) {
        let fromScreen = currentScreen.displayName
        let toScreen = navigationStack.last?.displayName ?? "Main"
        logger.navigation(from: fromScreen, to: "<-- \(toScreen)", function: #function) // Добавляем лог для возврата
        if let reason = reason {
            appendLog("⬅️ goBack(reason: \(reason))")
        } else {
            appendLog("⬅️ goBack()")
        }

        if currentScreen == .paymentQR,
           selectedTariffForPayment == nil,
           navigationStack.isEmpty,
           lastScreenBeforePaymentQR == nil {
            appendLog("❗️ goBack: PaymentQR без тарифа и пустой стек — возвращаемся к Tariffs")
            currentScreen = .tariffs
            navigationStack = [.main]
            endManualPaymentQRClose()
            return
        }

        if Thread.isMainThread {
            performGoBack()
        } else {
            DispatchQueue.main.async { [weak self] in
                self?.performGoBack()
            }
        }
    }
    
    func beginManualPaymentQRClose() {
        isManuallyClosingPaymentQR = true
        appendLog("🔒 beginManualPaymentQRClose()")
    }
    
    private func endManualPaymentQRClose() {
        guard isManuallyClosingPaymentQR else { return }
        isManuallyClosingPaymentQR = false
        appendLog("🔓 endManualPaymentQRClose()")
    }
    
    private func performGoBack() {
        if isNavigatingBack {
            print("⚠️ DEBUG NavigationManager.goBack: Переход уже выполняется, пропускаем повторный вызов")
            appendLog("⚠️ goBack: переход уже выполняется")
            return
        }
        
        isNavigatingBack = true
        let unlockDelay: TimeInterval = 0.35
        let unlockBackNavigation = {
            DispatchQueue.main.asyncAfter(deadline: .now() + unlockDelay) { [weak self] in
                guard let self = self else { return }
                self.isNavigatingBack = false
                print("🔓 DEBUG NavigationManager.goBack: Разблокировали повторный переход назад")
            }
        }
        
        defer { unlockBackNavigation() }
        
        print("🔍 DEBUG NavigationManager.goBack: Начало функции")
        print("🔍 DEBUG NavigationManager.goBack: Текущий экран = \(currentScreen)")
        print("🔍 DEBUG NavigationManager.goBack: Стек навигации = \(navigationStack)")
        appendLog("🔍 goBack start | current = \(currentScreen) | стек = \(navigationStack)")
        
        if currentScreen == .paymentQR {
            let fallbackScreen: ALADDINScreen
            if let previousFromStack = navigationStack.popLast() {
                fallbackScreen = previousFromStack
            } else if let stored = lastScreenBeforePaymentQR {
                fallbackScreen = stored
            } else {
                fallbackScreen = .tariffs
                appendLog("⚠️ goBack: lastScreenBeforePaymentQR отсутствует — используем Tariffs")
            }
            
            print("🔁 DEBUG NavigationManager.goBack: Возврат с PaymentQR к \(fallbackScreen)")
            currentScreen = fallbackScreen
            selectedTariffForPayment = nil
            lastScreenBeforePaymentQR = nil
            appendLog("🔁 Возврат с PaymentQR к \(fallbackScreen)")
            endManualPaymentQRClose()
            
            if fallbackScreen == .tariffs && navigationStack.isEmpty {
                print("ℹ️ DEBUG NavigationManager.goBack: Восстанавливаем стек [.main] после возврата на Tariffs")
                navigationStack = [.main]
                appendLog("ℹ️ Стек восстановлен до [.main]")
            }
            
            print("🔍 DEBUG NavigationManager.goBack: Текущий экран после PaymentQR = \(currentScreen)")
            print("🔍 DEBUG NavigationManager.goBack: Стек после PaymentQR = \(navigationStack)")
            appendLog("✅ goBack завершён | current = \(currentScreen) | стек = \(navigationStack)")
            return
        }
        
        if navigationStack.isEmpty {
            print("❌ DEBUG NavigationManager.goBack: Стек пуст. Текущий экран = \(currentScreen)")
            
            if currentScreen == .paymentQR {
                print("🔁 DEBUG NavigationManager.goBack: Возвращаемся на TariffsScreen вместо .main")
                currentScreen = .tariffs
                selectedTariffForPayment = nil
                endManualPaymentQRClose()
                appendLog("⚠️ Стек пуст при PaymentQR — fallback на Tariffs")
            } else {
                print("⬅️ DEBUG NavigationManager.goBack: Возврат на .main")
                currentScreen = .main
                appendLog("⬅️ Стек пуст — возврат на .main")
            }
            return
        }
        
        let previousScreen = navigationStack.removeLast()
        print("🔍 DEBUG NavigationManager.goBack: Было \(currentScreen), Возвращаемся к \(previousScreen)")
        
        currentScreen = previousScreen
        print("🔍 DEBUG NavigationManager.goBack: currentScreen изменен на \(currentScreen)")
        print("🔍 DEBUG NavigationManager.goBack: Оставшийся стек = \(navigationStack)")
        
        if previousScreen == .tariffs {
            print("ℹ️ DEBUG NavigationManager.goBack: Сброс selectedTariffForPayment после возврата на TariffsScreen")
            selectedTariffForPayment = nil
        }
        
        appendLog("✅ goBack завершён | current = \(currentScreen) | стек = \(navigationStack)")
        endManualPaymentQRClose()
    }
    
    /// Возврат к корневому экрану
    func goToRoot() {
        navigationStack.removeAll()
        currentScreen = .main
    }
    
    /// Переход к экрану с очисткой стека
    func navigateToRoot(_ screen: ALADDINScreen) {
        logger.navigation(from: currentScreen.displayName, to: "<-- Root (\(screen.displayName))", function: #function) // Логируем переход к корню
        appendLog("⬆️ navigateToRoot(\(screen)) | до очистки стека = \(navigationStack)")
        navigationStack.removeAll()
        currentScreen = screen
        appendLog("⬆️ navigateToRoot завершён | current = \(currentScreen)")
        objectWillChange.send()
    }
    
    /// Показать модальное окно
    func presentModal(_ modal: ALADDINModal) {
        currentModal = modal
        isPresentingModal = true
    }
    
    /// Скрыть модальное окно
    func dismissModal() {
        currentModal = nil
        isPresentingModal = false
    }
    
    /// Переключение между основными экранами
    func switchToMainScreen() {
        logger.ui("Switching to Main Screen", function: #function)
        navigateToRoot(.main)
    }
    
    func switchToFamilyScreen() {
        logger.ui("Switching to Family Screen", function: #function)
        navigateToRoot(.family)
    }
    
    func switchToNetworkProtectionScreen() {
        logger.ui("Switching to Network Protection Screen", function: #function)
        navigateToRoot(.networkProtection)
    }
    
    
    func switchToAnalyticsScreen() {
        logger.ui("Switching to Analytics Screen", function: #function)
        navigateToRoot(.analytics)
    }
    
    func switchToSettingsScreen() {
        logger.ui("Switching to Settings Screen", function: #function)
        guard currentScreen != .settings else { return }
        navigateTo(.settings)
    }
    
    // MARK: - Специальные переходы
    
    /// Переход к экрану устройства
    func navigateToDevice(_ deviceId: String) {
        logger.ui("Navigating to Device Detail for ID: \(deviceId)", function: #function)
        navigateTo(.deviceDetail)
        // Здесь можно передать deviceId в ViewModel
    }
    
    /// Переход к профилю пользователя
    func navigateToProfile(_ userId: String) {
        logger.ui("Navigating to Profile for ID: \(userId)", function: #function)
        navigateTo(.profile)
        // Здесь можно передать userId в ViewModel
    }
    
    /// Переход к настройкам уведомлений
    func navigateToNotificationSettings() {
        logger.ui("Navigating to Notification Settings", function: #function)
        navigateTo(.notificationSettings)
    }
    
    /// Переход к языковым настройкам
    func navigateToLanguageSettings() {
        logger.ui("Navigating to Language Settings", function: #function)
        navigateTo(.languageSettings)
    }
    
    // MARK: - Проверки состояния
    
    /// Проверка, можно ли вернуться назад
    var canGoBack: Bool {
        !navigationStack.isEmpty
    }
    
    /// Проверка, является ли экран корневым
    var isAtRoot: Bool {
        navigationStack.isEmpty
    }
    
    /// Получение предыдущего экрана
    var previousScreen: ALADDINScreen? {
        navigationStack.last
    }
    
    /// Получение глубины навигации
    var navigationDepth: Int {
        navigationStack.count
    }
    
    // MARK: - Сброс состояния
    
    /// Полный сброс навигации
    func reset() {
        currentScreen = .main
        navigationStack.removeAll()
        isPresentingModal = false
        currentModal = nil
        appendLog("♻️ reset(): current = .main, стек очищен")
    }
    
    /// Сброс только модальных окон
    func resetModals() {
        isPresentingModal = false
        currentModal = nil
    }
    
    // MARK: - Отладочные методы
    
    /// Печать текущего состояния навигации
    func printNavigationState() {
        print("=== Navigation State ===")
        print("Current Screen: \(currentScreen.displayName)")
        print("Navigation Stack: \(navigationStack.map { $0.displayName })")
        print("Is Presenting Modal: \(isPresentingModal)")
        print("Current Modal: \(currentModal?.displayName ?? "None")")
        print("========================")
    }
    
    /// Получение истории навигации
    var navigationHistory: [String] {
        var history = navigationStack.map { $0.displayName }
        history.append(currentScreen.displayName)
        return history
    }
    
    #if DEBUG
    func recordDebugLog(_ message: String) {
        appendLog(message)
    }
    #endif
}

// MARK: - Extensions

extension NavigationManager.ALADDINScreen {
    /// Проверка, является ли экран игровым
    var isGameScreen: Bool {
        switch self {
        case .childRewards, .familyTournament, .gamesParentalControl,
             .unicornPet, .companionHome, .companionHub, .companionConversation:
            return true
        default:
            return false
        }
    }
    
    /// Проверка, является ли экран настройками
    var isSettingsScreen: Bool {
        switch self {
        case .settings, .languageSettings, .notificationSettings, .widgetConfiguration:
            return true
        default:
            return false
        }
    }
    
    /// Проверка, требует ли экран авторизации
    var requiresAuthentication: Bool {
        switch self {
        case .profile, .devices, .joinDevice, .referral, .familyChat, .paymentQR:
            return true
        default:
            return false
        }
    }
}

extension NavigationManager {
    private static let logDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss.SSS"
        return formatter
    }()

    private static let maxLogEntries = 200

    func appendLog(_ message: String) {
        let entry = "[\(Self.logDateFormatter.string(from: Date()))] \(message)"
        debugLogs.append(entry)
        if debugLogs.count > Self.maxLogEntries {
            debugLogs.removeFirst(debugLogs.count - Self.maxLogEntries)
        }
    }
}

extension NavigationManager.ALADDINModal {
    /// Проверка, является ли модальное окно критическим
    var isCritical: Bool {
        switch self {
        case .addDevice, .editProfile, .qrCode:
            return true
        default:
            return false
        }
    }
    
    /// Проверка, можно ли закрыть модальное окно свайпом
    var isDismissible: Bool {
        switch self {
        case .help, .about, .rewards:
            return true
        default:
            return false
        }
    }
}
