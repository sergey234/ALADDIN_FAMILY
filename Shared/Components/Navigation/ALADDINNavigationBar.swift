import SwiftUI

struct ALADDINNavigationBar: View {
    @EnvironmentObject var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var showingScreenList = false
    
    // MARK: - Properties
    let title: String
    let subtitle: String?
    let showBackButton: Bool
    let showAddButton: Bool
    let showProfileButton: Bool
    let showListButton: Bool
    let rightButtons: [NavigationActionButton]
    let onBack: (() -> Void)?
    let onAdd: (() -> Void)?
    
    // MARK: - Initializers
    
    // Старый инициализатор для совместимости
    init() {
        self.title = "ALADDIN"
        self.subtitle = "AI Защита семьи"
        self.showBackButton = false
        self.showAddButton = false
        self.showProfileButton = true
        self.showListButton = true
        self.rightButtons = []
        self.onBack = nil
        self.onAdd = nil
    }
    
    // Новый инициализатор с параметрами
    init(
        title: String,
        subtitle: String? = nil,
        showBackButton: Bool = false,
        showAddButton: Bool = false,
        showProfileButton: Bool = true,
        showListButton: Bool = true,
        rightButtons: [NavigationActionButton] = [],
        onBack: (() -> Void)? = nil,
        onAdd: (() -> Void)? = nil
    ) {
        self.title = title
        self.subtitle = subtitle
        self.showBackButton = showBackButton
        self.showAddButton = showAddButton
        self.showProfileButton = showProfileButton
        self.showListButton = showListButton
        self.rightButtons = rightButtons
        self.onBack = onBack
        self.onAdd = onAdd
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Верхняя панель с заголовком и кнопками (оптимизированная)
            HStack {
                // Левая сторона - кнопка назад или логотип
                if showBackButton {
                    Button(action: {
                        onBack?()
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 18, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(width: 44, height: 44)
                            .background(
                                Circle()
                                    .fill(Color.orange.opacity(0.2))
                            )
                    }
                    .accessibilityLabel("Назад")
                } else {
                    // Логотип ALADDIN
                    HStack(spacing: 8) {
                        Circle()
                            .fill(Color.orange)
                            .frame(width: 32, height: 32)
                            .overlay(
                                Text("👁️")
                                    .font(.system(size: 18))
                            )
                            .shadow(color: Color.orange.opacity(0.4), radius: 10)
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(title)
                                .font(.system(size: 18, weight: .bold))
                                .foregroundColor(.orange)
                                .dynamicTypeSize(.medium ... .large)
                            
                            if let subtitle = subtitle {
                                Text(subtitle)
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(.white.opacity(0.7))
                                    .dynamicTypeSize(.small ... .medium)
                            }
                        }
                    }
                    .onTapGesture {
                        if navigationManager.isManuallyClosingPaymentQR {
                            navigationManager.appendLog("⚠️ ALADDINNavigationBar: tap по логотипу заблокирован (manual close)")
                            return
                        }
                        navigationManager.appendLog("🧭 ALADDINNavigationBar: navigateToRoot(.main)")
                        navigationManager.navigateToRoot(.main)
                    }
                }
                
                Spacer()
                
                // Правая сторона - кнопки
                HStack(spacing: 8) {
                    // Кнопка добавления
                    if showAddButton {
                        Button(action: {
                            onAdd?()
                        }) {
                            HStack(spacing: 4) {
                                Image(systemName: "plus")
                                    .font(.system(size: 14, weight: .bold))
                                Text("Добавить")
                                    .font(.system(size: 14, weight: .bold))
                            }
                            .foregroundColor(Color(red: 1.0, green: 0.84, blue: 0.0)) // Золотой цвет
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(
                                Capsule()
                                    .fill(Color(red: 1.0, green: 0.84, blue: 0.0).opacity(0.15))
                            )
                        }
                        .accessibilityLabel("Добавить")
                    }
                    
                    // Дополнительные кнопки
                    ForEach(rightButtons.indices, id: \.self) { index in
                        Button(action: {
                            rightButtons[index].action()
                        }) {
                            Image(systemName: rightButtons[index].icon)
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .frame(width: 32, height: 32)
                                .background(
                                    Circle()
                                        .fill(Color.orange.opacity(0.2))
                                )
                        }
                        .accessibilityLabel(rightButtons[index].accessibilityLabel)
                    }
                    
                    // Кнопка списка экранов
                    if showListButton {
                        Button(action: {
                            showingScreenList.toggle()
                        }) {
                            Image(systemName: "list.bullet")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.white)
                                .frame(width: 32, height: 32)
                                .background(
                                    Circle()
                                        .fill(Color.orange.opacity(0.2))
                                )
                        }
                        .accessibilityLabel("Список экранов")
                    }
                    
                    // Кнопка профиля
                    if showProfileButton {
                        Button(action: {
                            // Переходим в профиль через NavigationManager
                            navigationManager.navigateTo(.profile)
                        }) {
                            Circle()
                                .fill(Color.orange)
                                .frame(width: 32, height: 32)
                                .overlay(
                                    Text("👤")
                                        .font(.system(size: 16, weight: .bold))
                                        .foregroundColor(.black)
                                )
                        }
                        .accessibilityLabel("Профиль")
                    }
                }
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background(
                LinearGradient(
                    colors: [
                        Color(red: 0.04, green: 0.07, blue: 0.16),
                        Color(red: 0.12, green: 0.23, blue: 0.37)
                    ],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            
            // Список экранов (если показан)
            if showingScreenList {
                ScrollView {
                    LazyVStack(spacing: 8) {
                        ForEach(NavigationManager.ALADDINScreen.allCases.filter { screen in
                            // Скрываем модальные окна и служебные экраны из навигации
                            switch screen {
                            case .notificationSettings, .rewardsModal, .rewardsQuickModal:
                                return false
                            default:
                                return true
                            }
                        }, id: \.self) { screen in
                            let localizedTitle = screen.localizedTitle(using: localizationManager)
                            NavigationScreenButton(
                                screen: screen,
                                title: localizedTitle,
                                isActive: navigationManager.currentScreen == screen
                            ) {
                                navigationManager.navigateTo(screen)
                                showingScreenList = false
                            }
                        }
                    }
                    .padding(.horizontal, 20)
                    .padding(.vertical, 12)
                }
                .frame(maxHeight: 300)
                .background(
                    Color.black.opacity(0.9)
                        .cornerRadius(12)
                )
                .padding(.horizontal, 20)
                .transition(.opacity.combined(with: .scale))
            }
        }
        .animation(.easeInOut(duration: 0.3), value: showingScreenList)
    }
}

// MARK: - Navigation Button Models

struct NavigationActionButton {
    let icon: String
    let accessibilityLabel: String
    let action: () -> Void
    
    init(icon: String, accessibilityLabel: String, action: @escaping () -> Void) {
        self.icon = icon
        self.accessibilityLabel = accessibilityLabel
        self.action = action
    }
}

struct NavigationScreenButton: View {
    let screen: NavigationManager.ALADDINScreen
    let title: String
    let isActive: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: screen.icon)
                    .font(.system(size: 16))
                    .foregroundColor(isActive ? .orange : .white)
                    .frame(width: 24)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(isActive ? .orange : .white)
                    
                    // ✅ УБРАНО: Английское название (rawValue) - оставлены только русские названия
                    // Text(screen.rawValue)
                    //     .font(.system(size: 10))
                    //     .foregroundColor(.white.opacity(0.6))
                }
                
                Spacer()
                
                if isActive {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 16))
                        .foregroundColor(.orange)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(isActive ? Color.orange.opacity(0.2) : Color.clear)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(isActive ? Color.orange : Color.white.opacity(0.2), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Navigation Localization

private extension NavigationManager.ALADDINScreen {
    func navigationLocalizationKey() -> String {
        switch self {
        case .main: return "nav_screen_main"
        case .family: return "nav_screen_family"
        case .networkProtection: return "nav_screen_network_protection"
        case .analytics: return "nav_screen_analytics"
        case .settings: return "nav_screen_settings"
        case .aiAssistant: return "nav_screen_ai_assistant"
        case .parentalControl: return "nav_screen_parental_control"
        case .childInterface: return "nav_screen_child_interface"
        case .childContent: return "nav_screen_child_content"
        case .elderlyInterface: return "nav_screen_elderly_interface"
        case .tariffs: return "nav_screen_tariffs"
        case .profile: return "nav_screen_profile"
        case .notifications: return "nav_screen_notifications"
        case .support: return "nav_screen_support"
        case .addMemberOptions: return "nav_screen_add_member_options"
        case .onboarding: return "nav_screen_onboarding"
        case .privacyPolicy: return "nav_screen_privacy_policy"
        case .termsOfService: return "nav_screen_terms_of_service"
        case .settingsTest: return "nav_screen_settings_test"
        case .settingsFallback: return "nav_screen_settings_fallback"
        case .settingsTestSuite: return "nav_screen_settings_test_suite"
        case .devices: return "nav_screen_devices"
        case .referral: return "nav_screen_referral"
        case .deviceDetail: return "nav_screen_device_detail"
        case .familyChat: return "nav_screen_family_chat"
        case .paymentQR: return "nav_screen_payment_qr"
        case .activationCode: return "nav_screen_activation_code"
        case .childRewards: return "nav_screen_child_rewards"
        case .familyTournament: return "nav_screen_family_tournament"
        case .securityEducation: return "nav_screen_security_education"
        case .gamesParentalControl: return "nav_screen_games_parental_control"
        case .unicornPet: return "nav_screen_unicorn_pet"
        case .mainWithRegistration: return "nav_screen_main_registration"
        case .languageSettings: return "nav_screen_language_settings"
        case .notificationSettings: return "nav_screen_notification_settings"
        case .widgetConfiguration: return "nav_screen_widget_configuration"
        case .rewardsModal: return "nav_screen_rewards_modal"
        case .rewardsQuickModal: return "nav_screen_rewards_quick_modal"
        case .youngDefender: return "nav_screen_young_defender"
        case .familyProtector: return "nav_screen_family_protector"
        case .childGoalEditor: return "nav_screen_child_goal_editor"
        case .threatProtection: return "nav_screen_threat_protection"
        case .threatProtectionSettings: return "nav_screen_threat_settings"
        case .iotSecurity: return "nav_screen_iot_security"
        case .advancedProtection: return "nav_screen_advanced_protection"
        default: return "nav_screen_unknown"
        }
    }
    
    func localizedTitle(using localizationManager: LocalizationManager) -> String {
        let key = navigationLocalizationKey()
        let localized = localizationManager.localized(key)
        return localized == key ? displayName : localized
    }
}

struct ALADDINNavigationBar_Previews: PreviewProvider {
    static var previews: some View {
        ALADDINNavigationBar()
            .environmentObject(NavigationManager())
            .environmentObject(LocalizationManager())
            .background(Color.black)
    }
}