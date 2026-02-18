import SwiftUI

// MARK: - Navigation Manager для всех экранов ALADDIN - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
@MainActor
class NavigationManager: ObservableObject {
    // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Начинаем с онбординга для первого запуска
    @Published var currentScreen: ALADDINScreen = .onboarding
    @Published var navigationStack: [ALADDINScreen] = []
    @Published var isPresentingModal: Bool = false
    @Published var currentModal: ALADDINModal? = nil
    @Published private(set) var isNavigatingBack: Bool = false
    @Published private(set) var isManuallyClosingPaymentQR: Bool = false
    @Published private(set) var debugLogs: [String] = []
    @Published private var lastScreenBeforePaymentQR: ALADDINScreen? = nil

    // ✅ КРИТИЧЕСКОЕ: Защита от множественных навигаций
    private var isNavigating = false

    // ✅ ИСПРАВЛЕНИЕ: Добавляем для PaymentQRScreen через NavigationLink
    @Published var selectedTariffForPayment: Tariff? = nil
    
    // MARK: - Основные экраны (25)
    enum ALADDINScreen: String, CaseIterable {
        // Основные экраны
        case main = "01_MainScreen"
        case family = "02_FamilyScreen"
        case networkProtection = "03_NetworkProtectionScreen"
        case analytics = "04_AnalyticsScreen"
        case settings = "05_SettingsScreen"
        case settingsDiagnostic = "SettingsScreenDiagnostic"
        case settingsTest = "SettingsScreenTest"
        case settingsFallback = "SettingsScreenFallback"
        case settingsTestSuite = "SettingsTestSuite"
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
        
        var displayName: String {
            switch self {
            case .main: return "Главная"
            case .family: return "Семья"
            case .networkProtection: return "Защита сети"
            case .analytics: return "Аналитика"
            case .settings: return "Настройки"
            case .settingsDiagnostic: return "Диагностика настроек"
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
            case .referral: return "Реферальная программа"
            case .deviceDetail: return "Детали устройства"
            case .familyChat: return "Семейный чат"
            case .paymentQR: return "Оплата QR"
            case .childRewards: return "Детские награды"
            case .familyTournament: return "Семейный турнир"
            case .securityEducation: return "Безопасность"
            case .gamesParentalControl: return "Игры и контроль"
            case .unicornPet: return "Единорог-питомец"
            case .mainWithRegistration: return "Главная с регистрацией"
            case .languageSettings: return "Настройки языка"
            case .notificationSettings: return "Настройки уведомлений"
            case .widgetConfiguration: return "Настройка виджетов"
            case .rewardsModal: return "Модальное окно наград"
            case .rewardsQuickModal: return "Быстрое окно наград"
            case .youngDefender: return "Юный защитник"
            case .familyProtector: return "Я защитник семьи"
            case .childGoalEditor: return "Моя цель"
            case .activationCode: return "Активация кода"
            case .threatProtection: return "Защита от угроз"
            case .threatProtectionSettings: return "Настройки защиты"
            case .iotSecurity: return "IoT безопасность"
            case .advancedProtection: return "Расширенная защита"
            case .settingsTest: return "Тест настроек"
            case .settingsFallback: return "Резервные настройки"
            case .settingsTestSuite: return "Набор тестов настроек"
            }
        }
        
        var icon: String {
            switch self {
            case .main: return "house.fill"
            case .family: return "person.3.fill"
            case .networkProtection: return "shield.fill"
            case .analytics: return "chart.bar.fill"
            case .settings: return "gearshape.fill"
            case .settingsDiagnostic: return "wrench.and.screwdriver.fill"
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
            case .referral: return "gift.fill"
            case .deviceDetail: return "info.circle.fill"
            case .familyChat: return "message.fill"
            case .paymentQR: return "qrcode"
            case .childRewards: return "star.fill"
            case .familyTournament: return "trophy.fill"
            case .securityEducation: return "shield.lefthalf.filled"
            case .gamesParentalControl: return "gamecontroller.fill"
            case .unicornPet: return "pawprint.fill"
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
            case .settingsTest: return "testtube.2"
            case .settingsFallback: return "arrow.triangle.2.circlepath"
            case .settingsTestSuite: return "checklist"
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
        // ✅ [PHASE 7] НАВИГАЦИОННАЯ ВАЛИДАЦИЯ
        print("🔍 [NAV_VALIDATION] navigateTo(\(screen)) requested")
        print("🔍 [NAV_VALIDATION] Current screen: \(currentScreen)")
        print("🔍 [NAV_VALIDATION] Navigation stack: \(navigationStack)")
        print("🔍 [NAV_VALIDATION] Is navigating: \(isNavigating)")

        // Предотвращаем циклическую навигацию
        if navigationStack.contains(screen) && navigationStack.last == screen {
            print("⚠️ [NAV_VALIDATION] Prevented circular navigation to same screen: \(screen)")
            return
        }

        // Предотвращаем быструю последовательную навигацию
        if let lastScreen = navigationStack.last, lastScreen == screen {
            print("⚠️ [NAV_VALIDATION] Prevented duplicate navigation to same screen: \(screen)")
            return
        }

        // ✅ КРИТИЧЕСКОЕ: Защита от множественных навигаций
        // Предотвращает race conditions и множественные одновременные навигации
        guard !isNavigating else {
            appendLog("⚠️ navigateTo(\(screen)) отклонён: навигация уже выполняется")
            return
        }

        isNavigating = true
        defer {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                self.isNavigating = false
            }
        }

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
    
    /// Возврат к предыдущему экрану
    func goBack(reason: String? = nil) {
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
        #if DEBUG
        if screen == .settings {
            print("🔴 NAVIGATION: navigateToRoot(.settings) вызван")
        }
        #endif
        appendLog("⬆️ navigateToRoot(\(screen)) | до очистки стека = \(navigationStack)")
        navigationStack.removeAll()
        currentScreen = screen
        #if DEBUG
        if screen == .settings {
            print("🔴 NAVIGATION: currentScreen установлен в .settings")
        }
        #endif
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
        navigateToRoot(.main)
    }
    
    func switchToFamilyScreen() {
        navigateToRoot(.family)
    }
    
    func switchToNetworkProtectionScreen() {
        navigateToRoot(.networkProtection)
    }
    
    
    func switchToAnalyticsScreen() {
        navigateToRoot(.analytics)
    }
    
    func switchToSettingsScreen() {
        // ✅ КРИТИЧЕСКОЕ: Заменены crashLog на print чтобы избежать рекурсии
        print("🔴 NAVIGATION: switchToSettingsScreen() вызван - ПЕРЕХОД К НАСТРОЙКАМ")
        print("🔴 NAVIGATION: Текущий экран: \(currentScreen)")
        print("🔴 NAVIGATION: Thread.isMainThread: \(Thread.isMainThread)")
        print("🔴 NAVIGATION: Stack trace: \(Thread.callStackSymbols.prefix(3).joined(separator: " <- "))")

        navigateToRoot(.settings)
    }
    
    // MARK: - Специальные переходы
    
    /// Переход к экрану устройства
    func navigateToDevice(_ deviceId: String) {
        navigateTo(.deviceDetail)
        // Здесь можно передать deviceId в ViewModel
    }
    
    /// Переход к профилю пользователя
    func navigateToProfile(_ userId: String) {
        navigateTo(.profile)
        // Здесь можно передать userId в ViewModel
    }
    
    /// Переход к настройкам уведомлений
    func navigateToNotificationSettings() {
        navigateTo(.notificationSettings)
    }
    
    /// Переход к языковым настройкам
    func navigateToLanguageSettings() {
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
             .unicornPet:
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
        case .profile, .devices, .referral, .familyChat, .paymentQR:
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
