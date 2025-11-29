import SwiftUI
import SwiftUI

// MARK: - Navigation Manager для всех 36 экранов ALADDIN
class NavigationManager: ObservableObject {
    @Published var currentScreen: ALADDINScreen = .main
    @Published var navigationStack: [ALADDINScreen] = []
    @Published var isPresentingModal: Bool = false
    @Published var currentModal: ALADDINModal? = nil
    
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
        case gamesParentalControl = "GamesParentalControlView"
        case unicornPet = "UnicornPetView"
        case unicornUniverse = "UnicornUniverseView"
        case wheelOfFortune = "WheelOfFortuneView"
        
        // Дубликаты (используем основные версии)
        case mainExact = "01_MainScreen_Exact"
        case mainFixed = "01_MainScreen_Fixed"
        case vpnTemp = "03_VPNScreen_temp"
        case familyDuplicate = "FamilyScreen"
        case mainWithRegistration = "MainScreenWithRegistration"
        
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
            case .elderlyInterface: return "Интерфейс для пожилых"
            case .tariffs: return "Тарифы"
            case .profile: return "Профиль"
            case .notifications: return "Уведомления"
            case .support: return "Поддержка"
            case .onboarding: return "Онбординг"
            case .privacyPolicy: return "Политика конфиденциальности"
            case .termsOfService: return "Условия использования"
            case .devices: return "Устройства"
            case .referral: return "Рефералы"
            case .deviceDetail: return "Детали устройства"
            case .familyChat: return "Семейный чат"
            case .vpnEnergyStats: return "Статистика VPN"
            case .paymentQR: return "QR Оплата"
            case .childRewards: return "Детские награды"
            case .familyTournament: return "Семейный турнир"
            case .gamesParentalControl: return "Игровой контроль"
            case .unicornPet: return "Единорог питомец"
            case .unicornUniverse: return "Вселенная единорогов"
            case .wheelOfFortune: return "Колесо фортуны"
            case .mainExact: return "Главная (точная)"
            case .mainFixed: return "Главная (исправленная)"
            case .vpnTemp: return "VPN (временная)"
            case .familyDuplicate: return "Семья (дубликат)"
            case .mainWithRegistration: return "Главная с регистрацией"
            }
        }
        
        var icon: String {
            switch self {
            case .main: return "house.fill"
            case .family: return "person.3.fill"
            case .vpn: return "shield.fill"
            case .analytics: return "chart.bar.fill"
            case .settings: return "gear"
            case .aiAssistant: return "brain.head.profile"
            case .parentalControl: return "lock.shield.fill"
            case .childInterface: return "child"
            case .elderlyInterface: return "person.crop.circle"
            case .tariffs: return "creditcard.fill"
            case .profile: return "person.fill"
            case .notifications: return "bell.fill"
            case .support: return "questionmark.circle.fill"
            case .onboarding: return "arrow.right.circle.fill"
            case .privacyPolicy: return "doc.text.fill"
            case .termsOfService: return "doc.text.fill"
            case .devices: return "iphone"
            case .referral: return "person.2.fill"
            case .deviceDetail: return "iphone.gen3"
            case .familyChat: return "message.fill"
            case .vpnEnergyStats: return "battery.100"
            case .paymentQR: return "qrcode"
            case .childRewards: return "gift.fill"
            case .familyTournament: return "trophy.fill"
            case .gamesParentalControl: return "gamecontroller.fill"
            case .unicornPet: return "pawprint.fill"
            case .unicornUniverse: return "sparkles"
            case .wheelOfFortune: return "circle.grid.3x3.fill"
            case .mainExact: return "house.fill"
            case .mainFixed: return "house.fill"
            case .vpnTemp: return "shield.fill"
            case .familyDuplicate: return "person.3.fill"
            case .mainWithRegistration: return "house.fill"
            }
        }
        
        var category: ScreenCategory {
            switch self {
            case .main, .family, .vpn, .analytics, .settings, .aiAssistant, .parentalControl, .childInterface, .elderlyInterface, .tariffs, .profile, .notifications, .support, .onboarding, .privacyPolicy, .termsOfService, .devices, .referral, .deviceDetail, .familyChat, .vpnEnergyStats, .paymentQR:
                return .main
            case .childRewards, .familyTournament, .gamesParentalControl, .unicornPet, .unicornUniverse, .wheelOfFortune:
                return .games
            case .mainExact, .mainFixed, .vpnTemp, .familyDuplicate, .mainWithRegistration:
                return .duplicates
            }
        }
    }
    
    // MARK: - Модальные окна (8)
    enum ALADDINModal: String, CaseIterable {
        case ageGroupSelection = "AgeGroupSelectionModal"
        case consent = "ConsentModal"
        case familyCreated = "FamilyCreatedModal"
        case letterSelection = "LetterSelectionModal"
        case qrScanner = "QRScannerModal"
        case recoveryOptions = "RecoveryOptionsModal"
        case registrationSuccess = "RegistrationSuccessModal"
        case roleSelection = "RoleSelectionModal"
        
        var displayName: String {
            switch self {
            case .ageGroupSelection: return "Выбор возрастной группы"
            case .consent: return "Согласие"
            case .familyCreated: return "Семья создана"
            case .letterSelection: return "Выбор буквы"
            case .qrScanner: return "QR Сканер"
            case .recoveryOptions: return "Опции восстановления"
            case .registrationSuccess: return "Успешная регистрация"
            case .roleSelection: return "Выбор роли"
            }
        }
    }
    
    // MARK: - Категории экранов
    enum ScreenCategory {
        case main
        case games
        case duplicates
    }
    
    // MARK: - Навигационные методы
    
    func navigateTo(_ screen: ALADDINScreen) {
        navigationStack.append(currentScreen)
        currentScreen = screen
    }
    
    func navigateBack() {
        if !navigationStack.isEmpty {
            currentScreen = navigationStack.removeLast()
        }
    }
    
    func navigateToRoot() {
        navigationStack.removeAll()
        currentScreen = .main
    }
    
    func presentModal(_ modal: ALADDINModal) {
        currentModal = modal
        isPresentingModal = true
    }
    
    func dismissModal() {
        currentModal = nil
        isPresentingModal = false
    }
    
    // MARK: - Получение View для экрана
    
    @ViewBuilder
    func getView(for screen: ALADDINScreen) -> some View {
        switch screen {
        case .main:
            MainScreen()
        case .family:
            FamilyScreen()
        case .vpn:
            VPNScreen()
        case .analytics:
            AnalyticsScreen()
        case .settings:
            SettingsScreen()
        case .aiAssistant:
            AIAssistantScreen()
        case .parentalControl:
            ParentalControlScreen()
        case .childInterface:
            ChildInterfaceScreen()
        case .elderlyInterface:
            ElderlyInterfaceScreen()
        case .tariffs:
            TariffsScreen()
        case .profile:
            ProfileScreen()
        case .notifications:
            NotificationsScreen()
        case .support:
            SupportScreen()
        case .onboarding:
            OnboardingScreen()
        case .privacyPolicy:
            PrivacyPolicyScreen()
        case .termsOfService:
            TermsOfServiceScreen()
        case .devices:
            DevicesScreen()
        case .referral:
            ReferralScreen()
        case .deviceDetail:
            DeviceDetailScreen()
        case .familyChat:
            FamilyChatScreen()
        case .vpnEnergyStats:
            VPNEnergyStatsScreen()
        case .paymentQR:
            PaymentQRScreen()
        case .childRewards:
            ChildRewardsScreen()
        case .familyTournament:
            FamilyTournamentView()
        case .gamesParentalControl:
            GamesParentalControlView()
        case .unicornPet:
            UnicornPetView()
        case .unicornUniverse:
            UnicornUniverseView()
        case .wheelOfFortune:
            WheelOfFortuneView()
        case .mainExact:
            MainScreenExact()
        case .mainFixed:
            MainScreenFixed()
        case .vpnTemp:
            VPNScreen_temp()
        case .familyDuplicate:
            FamilyScreen()
        case .mainWithRegistration:
            MainScreenWithRegistration()
        }
    }
    
    // MARK: - Получение View для модального окна
    
    @ViewBuilder
    func getModalView(for modal: ALADDINModal) -> some View {
        switch modal {
        case .ageGroupSelection:
            AgeGroupSelectionModal(isPresented: .constant(true))
        case .consent:
            ConsentModal(isPresented: .constant(true))
        case .familyCreated:
            FamilyCreatedModal(isPresented: .constant(true))
        case .letterSelection:
            LetterSelectionModal(isPresented: .constant(true))
        case .qrScanner:
            QRScannerModal(isPresented: .constant(true))
        case .recoveryOptions:
            RecoveryOptionsModal(isPresented: .constant(true))
        case .registrationSuccess:
            RegistrationSuccessModal(isPresented: .constant(true))
        case .roleSelection:
            RoleSelectionModal(isPresented: .constant(true))
        }
    }
    
    // MARK: - Статистика
    
    var totalScreens: Int {
        ALADDINScreen.allCases.count
    }
    
    var mainScreensCount: Int {
        ALADDINScreen.allCases.filter { $0.category == .main }.count
    }
    
    var gameScreensCount: Int {
        ALADDINScreen.allCases.filter { $0.category == .games }.count
    }
    
    var duplicateScreensCount: Int {
        ALADDINScreen.allCases.filter { $0.category == .duplicates }.count
    }
    
    var modalsCount: Int {
        ALADDINModal.allCases.count
    }
}

// MARK: - Singleton для глобального доступа
extension NavigationManager {
    static let shared = NavigationManager()
}