import SwiftUI

// MARK: - Navigation Manager для всех экранов ALADDIN - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
@MainActor
class NavigationManager: ObservableObject {
    @Published var currentScreen: ALADDINScreen = .main
    @Published var navigationStack: [ALADDINScreen] = []
    @Published var isPresentingModal: Bool = false
    @Published var currentModal: ALADDINModal? = nil
    
    // ✅ ИСПРАВЛЕНИЕ: Добавляем для PaymentQRScreen через NavigationLink
    @Published var selectedTariffForPayment: Tariff? = nil
    
    // MARK: - Основные экраны (25)
    enum ALADDINScreen: String, CaseIterable {
        // Основные экраны
        case main = "01_MainScreen"
        case family = "02_FamilyScreen"
        case vpn = "03_VPNScreen"
        case analytics = "04_AnalyticsScreen"
        case settings = "05_SettingsScreen"
        case aiAssistant = "06_AIAssistantScreen"
        case parentalControl = "07_ParentalControlScreen"
        case childInterface = "08_ChildInterfaceScreen"
        case childContent = "ChildContentScreen"
        case elderlyInterface = "09_ElderlyInterfaceScreen"
        case tariffs = "10_TariffsScreen"
        case profile = "11_ProfileScreen"
        case notifications = "12_NotificationsScreen"
        case support = "13_SupportScreen"
        case onboarding = "14_OnboardingScreen"
        case privacyPolicy = "18_PrivacyPolicyScreen"
        case termsOfService = "19_TermsOfServiceScreen"
        case devices = "20_DevicesScreen"
        case referral = "21_ReferralScreen"
        case deviceDetail = "22_DeviceDetailScreen"
        case familyChat = "23_FamilyChatScreen"
        case vpnEnergyStats = "24_VPNEnergyStatsScreen"
        case paymentQR = "25_PaymentQRScreen"
        
        // Игровые экраны
        case childRewards = "ChildRewardsScreen"
        case familyTournament = "FamilyTournamentView"
        case securityEducation = "SecurityEducationScreen"
        case gamesParentalControl = "GamesParentalControlView"
        case unicornPet = "UnicornPetView"
        case unicornUniverse = "UnicornUniverseView"
        case wheelOfFortune = "WheelOfFortuneView"
        
        // НОВЫЕ ИГРОВЫЕ ЭКРАНЫ (геймификация)
        case youngDefender = "YoungDefenderView"           // 🛡️ Юный защитник
        case familyProtector = "FamilyProtectorView"       // 🕵️ Я защитник
        case childGoalEditor = "ChildGoalEditorView"       // 🎯 Моя цель
        
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
            case .vpn: return "VPN"
            case .analytics: return "Аналитика"
            case .settings: return "Настройки"
            case .aiAssistant: return "AI Помощник"
            case .parentalControl: return "Родительский контроль"
            case .childInterface: return "Детский интерфейс"
            case .childContent: return "Контент для детей"
            case .elderlyInterface: return "Пожилой интерфейс"
            case .tariffs: return "Тарифы"
            case .profile: return "Профиль"
            case .notifications: return "Уведомления"
            case .support: return "Поддержка"
            case .onboarding: return "Обучение"
            case .privacyPolicy: return "Политика конфиденциальности"
            case .termsOfService: return "Условия использования"
            case .devices: return "Устройства"
            case .referral: return "Реферальная программа"
            case .deviceDetail: return "Детали устройства"
            case .familyChat: return "Семейный чат"
            case .vpnEnergyStats: return "Статистика VPN"
            case .paymentQR: return "Оплата QR"
            case .childRewards: return "Детские награды"
            case .familyTournament: return "Семейный турнир"
            case .securityEducation: return "Безопасность"
            case .gamesParentalControl: return "Игры и контроль"
            case .unicornPet: return "Единорог-питомец"
            case .unicornUniverse: return "Вселенная единорогов"
            case .wheelOfFortune: return "Колесо фортуны"
            case .mainWithRegistration: return "Главная с регистрацией"
            case .languageSettings: return "Настройки языка"
            case .notificationSettings: return "Настройки уведомлений"
            case .widgetConfiguration: return "Настройка виджетов"
            case .rewardsModal: return "Модальное окно наград"
            case .rewardsQuickModal: return "Быстрое окно наград"
            case .youngDefender: return "Юный защитник"
            case .familyProtector: return "Я защитник семьи"
            case .childGoalEditor: return "Моя цель"
            }
        }
        
        var icon: String {
            switch self {
            case .main: return "house.fill"
            case .family: return "person.3.fill"
            case .vpn: return "shield.fill"
            case .analytics: return "chart.bar.fill"
            case .settings: return "gearshape.fill"
            case .aiAssistant: return "brain.head.profile"
            case .parentalControl: return "person.crop.circle.badge.checkmark"
            case .childInterface: return "child"
            case .childContent: return "book.fill"
            case .elderlyInterface: return "person.crop.circle"
            case .tariffs: return "creditcard.fill"
            case .profile: return "person.fill"
            case .notifications: return "bell.fill"
            case .support: return "questionmark.circle.fill"
            case .onboarding: return "book.fill"
            case .privacyPolicy: return "doc.text.fill"
            case .termsOfService: return "doc.plaintext.fill"
            case .devices: return "iphone"
            case .referral: return "gift.fill"
            case .deviceDetail: return "info.circle.fill"
            case .familyChat: return "message.fill"
            case .vpnEnergyStats: return "battery.100percent"
            case .paymentQR: return "qrcode"
            case .childRewards: return "star.fill"
            case .familyTournament: return "trophy.fill"
            case .securityEducation: return "shield.lefthalf.filled"
            case .gamesParentalControl: return "gamecontroller.fill"
            case .unicornPet: return "pawprint.fill"
            case .unicornUniverse: return "sparkles"
            case .wheelOfFortune: return "circle.grid.3x3.fill"
            case .mainWithRegistration: return "house.fill"
            case .languageSettings: return "globe"
            case .notificationSettings: return "bell.badge.fill"
            case .widgetConfiguration: return "square.grid.3x3.fill"
            case .rewardsModal: return "gift.fill"
            case .rewardsQuickModal: return "gift.fill"
            case .youngDefender: return "shield.lefthalf.filled"
            case .familyProtector: return "sparkles"
            case .childGoalEditor: return "target"
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
            }
        }
    }
    
    // MARK: - Навигационные методы
    
    /// Переход к экрану
    func navigateTo(_ screen: ALADDINScreen) {
        // ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Проверка ДО асинхронного обновления
        if case .paymentQR = screen {
            guard selectedTariffForPayment != nil else {
                print("❌ КРИТИЧЕСКАЯ ОШИБКА: Попытка открыть PaymentQR без тарифа!")
                print("❌ selectedTariffForPayment = nil")
                return
            }
            print("✅ PaymentQR: тариф установлен - \(selectedTariffForPayment?.id ?? "nil")")
        }
        
        // ✅ ИСПРАВЛЕНИЕ: @MainActor гарантирует выполнение на main thread
        // Убираем проверку Thread.isMainThread и DispatchQueue.main.sync (может вызвать deadlock)
        print("🔍 DEBUG NavigationManager.navigateTo: Было \(self.currentScreen), Стало \(screen)")
        print("🔍 DEBUG NavigationManager.navigateTo: Текущий стек = \(self.navigationStack)")
        
        // Добавляем текущий экран в стек перед переходом
        self.navigationStack.append(self.currentScreen)
        self.currentScreen = screen
        
        print("🔍 DEBUG NavigationManager: currentScreen изменен на \(self.currentScreen)")
        print("🔍 DEBUG NavigationManager: Новый стек = \(self.navigationStack)")
    }
    
    /// Возврат к предыдущему экрану
    func goBack() {
        // Убедимся, что обновление происходит на главном потоке
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            print("🔍 DEBUG NavigationManager.goBack: Начало функции")
            print("🔍 DEBUG NavigationManager.goBack: Текущий экран = \(self.currentScreen)")
            print("🔍 DEBUG NavigationManager.goBack: Стек навигации = \(self.navigationStack)")
            
            guard !self.navigationStack.isEmpty else {
                print("❌ DEBUG NavigationManager.goBack: Стек пуст, возврат на .main")
                self.currentScreen = .main
                return
            }
            
            let previousScreen = self.navigationStack.removeLast()
            print("🔍 DEBUG NavigationManager.goBack: Было \(self.currentScreen), Возвращаемся к \(previousScreen)")
            
            self.currentScreen = previousScreen
            print("🔍 DEBUG NavigationManager.goBack: currentScreen изменен на \(self.currentScreen)")
            print("🔍 DEBUG NavigationManager.goBack: Оставшийся стек = \(self.navigationStack)")
        }
    }
    
    /// Возврат к корневому экрану
    func goToRoot() {
        navigationStack.removeAll()
        currentScreen = .main
    }
    
    /// Переход к экрану с очисткой стека
    func navigateToRoot(_ screen: ALADDINScreen) {
        navigationStack.removeAll()
        currentScreen = screen
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
    
    func switchToVPNScreen() {
        navigateToRoot(.vpn)
    }
    
    func switchToAnalyticsScreen() {
        navigateToRoot(.analytics)
    }
    
    func switchToSettingsScreen() {
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
}

// MARK: - Extensions

extension NavigationManager.ALADDINScreen {
    /// Проверка, является ли экран игровым
    var isGameScreen: Bool {
        switch self {
        case .childRewards, .familyTournament, .gamesParentalControl, 
             .unicornPet, .unicornUniverse, .wheelOfFortune:
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
