import SwiftUI

struct MainScreen: View {
    @State private var isFamilyProtectionEnabled: Bool = true
    @State private var aiQuestion: String = ""
    @StateObject private var vpnViewModel = VPNViewModel.shared
    @EnvironmentObject private var localizationManager: LocalizationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    
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
                // Статус бар
                HStack {
                    Text("9:41")
                        .font(.system(size: 12, weight: .medium, design: .default))
                        .foregroundColor(.white)
                        .dynamicTypeSize(.small ... .medium)
                        .accessibilityLabel("Время: 9:41")
                    
                    Spacer()
                    
                    HStack(spacing: 5) {
                        Text("📶")
                            .font(.system(size: 12))
                            .accessibilityLabel("Сигнал сети")
                        Text("🔋")
                            .font(.system(size: 12))
                            .accessibilityLabel("Заряд батареи")
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Статус устройства")
                }
                .padding(.horizontal, 20)
                .padding(.top, 10)
                .padding(.bottom, 20)
                
                // Заголовок - логотип слева, профиль справа
                HStack {
                    // Логотип и контент - ЛЕВЫЙ УГОЛ
                    HStack(spacing: 10) {
                        // Логотип единорога - синий
                        Circle()
                            .fill(Color.blue.opacity(0.2))
                            .frame(width: 36, height: 36)
                            .overlay(
                                Text("🦄")
                                    .font(.system(size: 22))
                            )
                            .shadow(color: Color.blue.opacity(0.5), radius: 10)
                            .overlay(
                                Circle()
                                    .stroke(Color.blue.opacity(0.3), lineWidth: 2)
                            )
                            .accessibilityLabel("Логотип ALADDIN - Единорог")
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text("ALADDIN")
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.blue)
                                .shadow(color: Color.blue.opacity(0.3), radius: 10)
                                .dynamicTypeSize(.medium ... .large)
                                .accessibilityLabel("Название приложения ALADDIN")
                            
                            Text("AI Защита семьи")
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(.white.opacity(0.7))
                                .dynamicTypeSize(.small ... .medium)
                                .accessibilityLabel("Описание: AI Защита семьи")
                        }
                        .accessibilityElement(children: .combine)
                        .accessibilityLabel("ALADDIN - AI Защита семьи")
                    }
                    
                    Spacer()
                    
                    // Кнопка профиля - ПРАВЫЙ УГОЛ
                    NavigationLink(destination: ProfileScreen()) {
                        Circle()
                            .fill(Color.orange)
                            .frame(width: 44, height: 44)
                            .overlay(
                                Text("👤")
                                    .font(.system(size: 18, weight: .bold))
                                    .foregroundColor(.black)
                            )
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
                            Text("Главная")
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 🛡️ Защита (VPN)
                    NavigationLink(destination: VPNScreen()) {
                        VStack(spacing: 4) {
                            Text("🛡️")
                                .font(.system(size: 20))
                            Text("Защита")
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
                            Text("Уведомления")
                                .font(.system(size: 9, weight: .bold))
                                .foregroundColor(.white.opacity(0.7))
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 6)
                    }
                    
                    // 👤 Профиль
                    NavigationLink(destination: ProfileScreen()) {
                        VStack(spacing: 4) {
                            Text("👤")
                                .font(.system(size: 20))
                            Text("Профиль")
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
                            Text("Устройства")
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
        }
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
                                    
                                    Text("ALADDIN VPN")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                        .accessibilityLabel("Название: ALADDIN VPN")
                                    
                                    Text("VPN • Защита")
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
                            NavigationLink(destination: TariffsScreen()) {
                                VStack(spacing: 8) {
                                    Text("💎")
                                        .font(.system(size: 20))
                                        .accessibilityLabel("Иконка тарифов")
                                    
                                    Text("Тарифы")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                        .accessibilityLabel("Название: Тарифы")
                                    
                                    Text("Выбор плана")
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
                            .accessibilityLabel("Тарифы - Выбор плана")
                            .accessibilityHint("Нажмите для открытия экрана тарифов")
                            
                            // Аналитика карточка
                            NavigationLink(destination: AnalyticsScreen()) {
                                VStack(spacing: 8) {
                                    Text("📊")
                                        .font(.system(size: 20))
                                    
                                    Text("Аналитика")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text("Статистика")
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
                                    
                                    Text("Настройки")
                                        .font(.system(size: 12, weight: .semibold))
                                        .foregroundColor(.white)
                                    
                                    Text("Параметры")
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
                                
                                Text("ALADDIN FAMILY")
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
                                            .fill(isFamilyProtectionEnabled ? Color.orange : Color.black)
                                            .frame(width: 14, height: 14)
                                            .offset(x: isFamilyProtectionEnabled ? 8.5 : -8.5)
                                    }
                                }
                            }
                            
                            // Информация о семье
                            VStack(alignment: .leading, spacing: 3) {
                                Text("👤 6 членов семьи • 4 устройства")
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text("🛡️ Защита 98% • Все возрасты")
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                                
                                Text("🟢 VPN 100 Мбит/с • Защищено от 2,847 угроз")
                                    .font(.system(size: 9))
                                    .foregroundColor(.black)
                            }
                            
                            // Кнопки действий
                            HStack(spacing: 8) {
                                Button(action: {
                                    navigationManager.navigateTo(.family)
                                }) {
                                    Text("Управление семьей")
                                        .font(.system(size: 11, weight: .bold))
                                        .foregroundColor(.orange)
                                        .frame(maxWidth: .infinity)
                                        .frame(height: 32)
                                        .background(
                                            RoundedRectangle(cornerRadius: 8)
                                                .fill(Color.black)
                                        )
                                }
                                
                                Button(action: {
                                    navigationManager.navigateTo(.family)
                                }) {
                                    Text("Добавить члена семьи")
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
                                        colors: [Color.orange, Color.orange.opacity(0.8)],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10)
                                        .stroke(Color.orange, lineWidth: 2)
                                )
                        )
                        .shadow(color: Color.orange.opacity(0.3), radius: 8)
                        .padding(.horizontal, 20)
                        
                        // AI помощник
                        Button(action: {
                            navigationManager.navigateTo(.aiAssistant)
                        }) {
                            VStack(alignment: .leading, spacing: 8) {
                                Text("🤖 AI Помощник ALADDIN")
                                    .font(.system(size: 12, weight: .bold))
                                    .foregroundColor(.orange)
                                
                                Text("\"Привет! Я помогу настроить защиту для вашей семьи. Чем могу помочь?\"")
                                    .font(.system(size: 10))
                                    .foregroundColor(.white.opacity(0.9))
                                
                                TextField("Задайте вопрос...", text: $aiQuestion)
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
                                    .fill(Color.orange.opacity(0.1))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 10)
                                            .stroke(Color.orange, lineWidth: 2)
                                    )
                            )
                        }
                        .padding(.horizontal, 20)
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Основной контент приложения")
        }
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

struct MainScreen_Previews: PreviewProvider {
    static var previews: some View {
        MainScreen()
    }
}