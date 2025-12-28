import SwiftUI
import UIKit

struct MainScreen: View {
    @State private var aiQuestion: String = ""
    @State private var showAddMemberModal: Bool = false
    @StateObject private var mainViewModel = MainViewModel()
    @StateObject private var tariffManager = TariffManager.shared
    @StateObject private var antivirusManager = AntivirusManager.shared
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var profileImage: UIImage? = nil
    @AppStorage("subscription_expires_at_iso") private var subscriptionExpiresAtIso: String = ""
    @AppStorage("antivirusEnabled") private var antivirusEnabled = true
    
    var body: some View {
        ZStack {
            // Фон - красивый градиент как в SupportScreen
            LinearGradient(
                colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // ✅ УДАЛЕНО: Декораторы времени и заряда/сети - они больше не нужны
                // Заголовок - логотип слева, профиль справа
                HStack {
                    // Логотип и контент - ЛЕВЫЙ УГОЛ
                    HStack(spacing: 10) {
                        // ✅ Логотип с ободком из онбординга (как на странице 7)
                        Group {
                            if let profileImage = profileImage {
                                // Используем изображение профиля если есть
                                Image(uiImage: profileImage)
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 44, height: 44)
                                    .clipShape(Circle())
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 3) // ✅ Золотой ободок (пропорционально 14px для 140x140)
                                    )
                            } else if UIImage(named: "app_icon") != nil || UIImage(named: "AppIcon") != nil {
                                // Используем логотип из Assets
                                Image("app_icon")
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 44, height: 44)
                                    .clipShape(Circle())
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 3) // ✅ Золотой ободок
                                    )
                            } else {
                                // Fallback - единорог с золотым ободком
                                Circle()
                                    .fill(Color.secondaryGold.opacity(0.2))
                                    .frame(width: 44, height: 44)
                                    .overlay(
                                        Text("🦄")
                                            .font(.system(size: 22))
                                    )
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 3) // ✅ Золотой ободок
                                    )
                            }
                        }
                        .shadow(color: Color.secondaryGold.opacity(0.5), radius: 10)
                        .accessibilityLabel("Логотип ALADDIN")
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text(localizationManager.localized("main_aladdin_title"))
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.secondaryGold)
                                .shadow(color: Color.secondaryGold.opacity(0.5), radius: 10)
                                .dynamicTypeSize(.medium ... .large)
                                .accessibilityLabel("Название приложения ALADDIN")
                            
                            Text(localizationManager.localized("main_ai_protection"))
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(.white.opacity(0.7))
                                .dynamicTypeSize(.small ... .medium)
                                .accessibilityLabel("Описание: AI Защита семьи")
                        }
                        .accessibilityElement(children: .combine)
                        .accessibilityLabel("ALADDIN - AI Защита семьи")
                    }
                    
                    Spacer()
                    
                    // Кнопка профиля - ПРАВЫЙ УГОЛ (через NavigationManager)
                    Button(action: {
                        navigationManager.navigateTo(.profile)
                    }) {
                        ZStack {
                            Circle()
                                .fill(Color.secondaryGold)
                                .frame(width: 44, height: 44)
                            
                            if let profileImage = profileImage {
                                Image(uiImage: profileImage)
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 44, height: 44)
                                    .clipShape(Circle())
                                    .overlay(
                                        Circle()
                                            .stroke(Color.secondaryGold, lineWidth: 3) // ✅ Золотой ободок (как у логотипа слева)
                                    )
                            } else {
                                Text("👤")
                                    .font(.system(size: 18, weight: .bold))
                                    .foregroundColor(.white)
                            }
                        }
                    }
                    .accessibilityLabel("Открыть профиль")
                    .accessibilityHint("Нажмите для перехода в профиль пользователя")
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
                
                // Основной контент - главная страница
                homeContent
                
                // Нижняя навигация - красивое меню с эмодзи
                HStack(spacing: 0) {
                    // 🏠 Главная
                    Button(action: {
                        // Остаемся на главной странице
                        print("Главная страница уже активна")
                    }) {
                        VStack(spacing: 4) {
                            Text("🏠")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_home"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 🛡️ Защита (Каталог угроз)
                    NavigationLink(destination: ThreatProtectionScreen()) {
                        VStack(spacing: 4) {
                            Text("🛡️")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_protection"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 🔔 Уведомления
                    NavigationLink(destination: NotificationsScreen()) {
                        VStack(spacing: 4) {
                            Text("🔔")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_notifications"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 👤 Профиль
                    Button(action: {
                        navigationManager.navigateTo(.profile)
                    }) {
                        VStack(spacing: 4) {
                            Text("👤")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_profile"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 📱 Устройства
                    NavigationLink(destination: DevicesScreen()) {
                        VStack(spacing: 4) {
                            Text("📱")
                                .font(.system(size: 20))
                            Text(localizationManager.localized("main_tab_devices"))
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                }
                .padding(.vertical, 6)
                .padding(.horizontal, 2)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(Color.black.opacity(0.4))
                )
                .padding(.horizontal, 20)
                .padding(.bottom, 20)
            }
        }
        .task {
            print("🚨 MainScreen загружен! Точная копия HTML!")
            loadProfileImage()
            // Загружаем статистику из API
            mainViewModel.loadDashboardData()
        }
        .onAppear {
            loadProfileImage()
        }
        .sheet(isPresented: $showAddMemberModal) {
            AddMemberOptionsModal(isPresented: $showAddMemberModal)
                .environmentObject(navigationManager)
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("main_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    // MARK: - Profile Image Management
    
    private func loadProfileImage() {
        profileImage = ProfileImageManager.shared.loadProfileImage()
    }
    
    // MARK: - Home Content
    
    private var homeContent: some View {
        ScrollView {
            VStack(spacing: 20) {
                        // Карточки функций - сетка 2x2
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 15) {
                            // Антивирус карточка (вместо VPN)
                            NavigationLink(destination: NetworkProtectionScreen()) {
                                VStack(spacing: 8) {
                                    HStack(spacing: 8) {
                                        Text("🛡️")
                                            .font(.system(size: 20))
                                            .accessibilityLabel("Иконка антивируса")
                                        Text(antivirusEnabled ? "🟢" : "🔴")
                                            .font(.system(size: 24))
                                            .accessibilityLabel(antivirusEnabled ? "Статус: Активен" : "Статус: Отключен")
                                    }
                                    
                                    Text(localizationManager.localized("main_antivirus_title"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                        .accessibilityLabel("Название: Антивирус Аладин")
                                    
                                    Text(localizationManager.localized("main_antivirus_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                        .accessibilityLabel("Описание: Защита устройств")
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            .accessibilityLabel("Антивирус Аладин - \(antivirusEnabled ? "Активен" : "Отключен")")
                            .accessibilityHint("Нажмите для открытия экрана защиты")
                            
                            // Тарифы карточка
                            Button(action: {
                                navigationManager.navigateTo(.tariffs)
                            }) {
                                VStack(spacing: 8) {
                                    Text("💎")
                                        .font(.system(size: 20))
                                        .accessibilityLabel("Иконка тарифов")
                                    
                                    Text(localizationManager.localized("main_tariffs"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                        .accessibilityLabel("Название: Тарифы")
                                    
                                    Text(localizationManager.localized("main_tariffs_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                        .accessibilityLabel("Описание: Выбор плана")
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            .buttonStyle(PlainButtonStyle())
                            .accessibilityLabel("Тарифы - Выбор плана")
                            .accessibilityHint("Нажмите для открытия экрана тарифов")
                            
                            // Аналитика карточка (через NavigationManager)
                            Button(action: {
                                navigationManager.navigateTo(.analytics)
                            }) {
                                VStack(spacing: 8) {
                                    Text("📊")
                                        .font(.system(size: 20))
                                    
                                    Text(localizationManager.localized("main_analytics"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text(localizationManager.localized("main_analytics_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                            
                            // Настройки карточка
                            NavigationLink(destination: SettingsScreen()) {
                                VStack(spacing: 8) {
                                    Text("⚙️")
                                        .font(.system(size: 20))
                                    
                                    Text(localizationManager.localized("main_settings"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text(localizationManager.localized("main_settings_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                }
                                .frame(maxWidth: .infinity)
                                .frame(height: 80)
                                .background(
                                    RoundedRectangle(cornerRadius: 10)
                                        .fill(Color.white.opacity(0.1))
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 10)
                                                .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                        )
                                )
                            }
                        }
                        .padding(.horizontal, 20)
                        
                        // FAMILY статус - большая карточка
                        VStack(spacing: 12) {
                            // Заголовок с капсулой статуса
                            HStack {
                                Text("👨‍👩‍👧‍👦")
                                    .font(.system(size: 18))
                                
                                Text(localizationManager.localized("main_family_title"))
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundColor(.black)
                                
                                Spacer()
                                
                                // Капсула статуса (вместо тумблера)
                                FamilyStatusBadge(
                                    status: mainViewModel.familyProtectionStatus,
                                    localizationManager: localizationManager,
                                    action: {
                                        navigationManager.navigateTo(.family)
                                    }
                                )
                            }
                            
                            // Информация о семье - ДИНАМИЧЕСКАЯ из MainViewModel
                            VStack(alignment: .leading, spacing: 3) {
                                Text(localizationManager.localized("main_family_info", mainViewModel.familyMembers, mainViewModel.devicesProtected))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                // Сообщение статуса (из API или fallback)
                                Text(mainViewModel.familyProtectionStatusMessage ?? localizationManager.localized(mainViewModel.familyProtectionStatus.messageLocalizationKey))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text(localizationManager.localized("main_family_network_protection_info", mainViewModel.threatsBlocked))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)

                                Text("\(localizationManager.localized("main_family_tariff_label")) \(currentTariffDisplayName)")
                                    .font(.system(size: 9, weight: .semibold))
                                    .foregroundColor(.black)

                                if let expirationText = subscriptionExpirationText {
                                    Text("\(localizationManager.localized("main_family_subscription_valid_until")) \(expirationText)")
                                        .font(.system(size: 9))
                                        .foregroundColor(.black)
                                }
                            }
                            
                            // Кнопки действий
                            HStack(spacing: 8) {
                                Button(action: {
                                    navigationManager.navigateTo(.family)
                                }) {
                                    Text(localizationManager.localized("main_family_manage"))
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.secondaryGold)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 32)
                                        .background(
                                            RoundedRectangle(cornerRadius: 8)
                                                .fill(Color.black)
                                        )
                                }
                                
                                Button(action: {
                                    // Используем модал для добавления участника
                                    showAddMemberModal = true
                                }) {
                                    Text(localizationManager.localized("main_family_add_member"))
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.black)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 32)
                                        .background(
                                            RoundedRectangle(cornerRadius: 8)
                                                .fill(Color.black.opacity(0.2))
                                                .overlay(
                                                    RoundedRectangle(cornerRadius: 8)
                                                        .stroke(Color.black, lineWidth: 2)
                                                )
                                        )
                                }
                            }
                        }
                        .padding(12)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(
                                    LinearGradient(
                                        colors: [Color.secondaryGold, Color.secondaryGold.opacity(0.8)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10)
                                        .stroke(Color.secondaryGold, lineWidth: 2)
                                )
                        )
                        .shadow(color: Color.secondaryGold.opacity(0.3), radius: 8)
                        .padding(.horizontal, 20)
                        
                        // AI помощник
                        Button(action: {
                            navigationManager.navigateTo(.aiAssistant)
                        }) {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(localizationManager.localized("main_ai_assistant_title"))
                                    .font(.system(size: 12, weight: .bold))
                                    .foregroundColor(.secondaryGold)
                                
                                Text(localizationManager.localized("main_ai_assistant_greeting"))
                                    .font(.system(size: 10))
                                    .foregroundColor(.white.opacity(0.9))
                                
                                TextField(localizationManager.localized("main_ai_assistant_placeholder"), text: $aiQuestion)
                                    .font(.system(size: 11))
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 8)
                                    .background(
                                        RoundedRectangle(cornerRadius: 16)
                                            .fill(Color.white.opacity(0.1))
                                            .overlay(
                                                RoundedRectangle(cornerRadius: 16)
                                                    .stroke(Color.white.opacity(0.3), lineWidth: 1)
                                            )
                                    )
                            }
                            .padding(10)
                            .background(
                                RoundedRectangle(cornerRadius: 10)
                                    .fill(Color.secondaryGold.opacity(0.1))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 10)
                                            .stroke(Color.secondaryGold, lineWidth: 2)
                                    )
                            )
                        }
                        .padding(.horizontal, 20)
                        
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Основной контент приложения")
    }

    private var currentTariffDisplayName: String {
        switch tariffManager.currentTariff {
        case .free:
            return localizationManager.localized("tariffs_free")
        case .personal:
            return localizationManager.localized("tariffs_personal")
        case .family:
            return localizationManager.localized("tariffs_family")
        case .premium:
            return localizationManager.localized("tariffs_premium")
        }
    }

    private var subscriptionExpirationText: String? {
        guard !subscriptionExpiresAtIso.isEmpty else { return nil }
        
        let isoFormatter = ISO8601DateFormatter()
        isoFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        
        var parsedDate = isoFormatter.date(from: subscriptionExpiresAtIso)
        if parsedDate == nil {
            isoFormatter.formatOptions = [.withInternetDateTime]
            parsedDate = isoFormatter.date(from: subscriptionExpiresAtIso)
        }
        guard let date = parsedDate else { return nil }
        
        let displayFormatter = DateFormatter()
        displayFormatter.dateStyle = .medium
        displayFormatter.timeStyle = .none
        displayFormatter.locale = Locale(identifier: Locale.preferredLanguages.first ?? "ru_RU")
        return displayFormatter.string(from: date)
    }
    
    // MARK: - Navigation Button Content
    
    private func navButtonContent(icon: String, label: String, isActive: Bool = false) -> some View {
        VStack(spacing: 2) {
            Image(systemName: icon)
                .font(.system(size: 14))
                .foregroundColor(isActive ? .white : .white.opacity(0.7))
            
            Text(label)
                .font(.system(size: 8, weight: .bold))
                .foregroundColor(isActive ? .white : .white.opacity(0.7))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 4)
    }
}

// MARK: - Family Status Badge

struct FamilyStatusBadge: View {
    let status: FamilyProtectionStatus
    let localizationManager: LocalizationManager
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                // Иконка
                Image(systemName: status.iconName)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(status.iconColor)
                
                // Текст статуса
                Text(localizationManager.localized(status.titleLocalizationKey))
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundColor(status.iconColor)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(status.color.opacity(0.2))
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - FamilyProtectionStatus Extension

extension FamilyProtectionStatus {
    var iconColor: Color {
        switch self {
        case .active: return Color(red: 0.04, green: 0.55, blue: 0.28) // #0A8C47
        case .paused: return Color(red: 0.43, green: 0.45, blue: 0.52) // #6E7484
        case .attention: return Color(red: 0.88, green: 0.55, blue: 0.16) // #E08F29
        case .critical: return Color(red: 0.88, green: 0.26, blue: 0.27) // #E04345
        }
    }
}

struct MainScreen_Previews: PreviewProvider {
    static var previews: some View {
        MainScreen()
    }
}

struct Previews_01_MainScreen_LibraryContent: LibraryContentProvider {
    var views: [LibraryItem] {
        LibraryItem(/*@START_MENU_TOKEN@*/Text("Hello, World!")/*@END_MENU_TOKEN@*/)
    }
}
