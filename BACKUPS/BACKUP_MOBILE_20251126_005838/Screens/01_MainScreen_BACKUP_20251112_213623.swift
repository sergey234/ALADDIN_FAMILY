import SwiftUI
import UIKit

struct MainScreen: View {
    // Сохраняем состояние семейной защиты в AppStorage
    @AppStorage("family_protection_enabled") private var isFamilyProtectionEnabled: Bool = true
    @State private var aiQuestion: String = ""
    @State private var showAddMemberModal: Bool = false
    @StateObject private var vpnViewModel = VPNViewModel.shared
    @StateObject private var mainViewModel = MainViewModel()
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var profileImage: UIImage? = nil
    
    private var vpnConnected: Bool {
        vpnViewModel.isVPNEnabled
    }
    
    var body: some View {
        ZStack {
            // Фон - красивый градиент как на заставке
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
                    
                    // 🛡️ Защита (Каталог 100 угроз)
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
                            // VPN карточка
                            NavigationLink(destination: VPNScreen()) {
                                VStack(spacing: 8) {
                                    HStack(spacing: 8) {
                                        Text("🛡️")
                                            .font(.system(size: 20))
                                            .accessibilityLabel("Иконка защиты")
                                        Text(vpnConnected ? "🟢" : "🔴")
                                            .font(.system(size: 24))
                                            .accessibilityLabel(vpnConnected ? "Статус: Подключено" : "Статус: Отключено")
                                    }
                                    
                                    Text(localizationManager.localized("main_vpn_title"))
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                        .accessibilityLabel("Название: ALADDIN VPN")
                                    
                                    Text(localizationManager.localized("main_vpn_subtitle"))
                                        .font(.system(size: 10))
                                        .foregroundColor(.white.opacity(0.8))
                                        .accessibilityLabel("Описание: VPN защита")
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
                            .accessibilityLabel("ALADDIN VPN - \(vpnConnected ? "Подключено" : "Отключено")")
                            .accessibilityHint("Нажмите для открытия VPN экрана")
                            
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
                            // Заголовок с переключателем
                            HStack {
                                Text("👨‍👩‍👧‍👦")
                                    .font(.system(size: 18))
                                
                                Text(localizationManager.localized("main_family_title"))
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundColor(.black)
                                
                                Spacer()
                                
                                // Переключатель
                                Button(action: {
                                    isFamilyProtectionEnabled.toggle()
                                }) {
                                    ZStack {
                                        RoundedRectangle(cornerRadius: 18)
                                            .fill(isFamilyProtectionEnabled ? Color.black : Color.black.opacity(0.3))
                                            .frame(width: 35, height: 18)
                                        
                                        Circle()
                                            .fill(isFamilyProtectionEnabled ? Color.secondaryGold : Color.black)
                                            .frame(width: 14, height: 14)
                                            .offset(x: isFamilyProtectionEnabled ? 8.5 : -8.5)
                                    }
                                }
                            }
                            
                            // Информация о семье - ДИНАМИЧЕСКАЯ из MainViewModel
                            VStack(alignment: .leading, spacing: 3) {
                                Text(localizationManager.localized("main_family_info", mainViewModel.familyMembers, mainViewModel.devicesProtected))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text(localizationManager.localized("main_family_protection_info"))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text(localizationManager.localized("main_family_vpn_info", mainViewModel.threatsBlocked))
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
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
                        
                        #if DEBUG
                        VStack(spacing: 12) {
                            // ✅ Синяя кнопка: Перейти на онбординг
                            Button(action: {
                                navigationManager.navigateTo(.onboarding)
                            }) {
                                Text("🔵 DEV: Показать онбординг")
                                    .font(.caption)
                                    .foregroundColor(.white)
                                    .padding()
                                    .frame(maxWidth: .infinity)
                                    .background(Color.blue.opacity(0.7))
                                    .cornerRadius(14)
                                    .shadow(radius: 4)
                            }
                            
                            // ✅ Красная кнопка: Сбросить онбординг
                            Button(action: {
                                UserDefaults.standard.set(false, forKey: "hasCompletedOnboarding")
                            }) {
                                Text("⚙️ DEV: Сбросить онбординг")
                                    .font(.caption)
                                    .foregroundColor(.white)
                                    .padding()
                                    .frame(maxWidth: .infinity)
                                    .background(Color.red.opacity(0.7))
                                    .cornerRadius(14)
                                    .shadow(radius: 4)
                            }
                        }
                        .padding(.horizontal)
                        .padding(.bottom, 24)
                        #endif
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Основной контент приложения")
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
