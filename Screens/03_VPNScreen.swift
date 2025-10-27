import SwiftUI

/**
 * 🔒 VPN Protection Screen
 * Полноценный экран VPN защиты
 * Источник: 02_protection_screen.html (38KB)
 */

struct VPNScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @StateObject private var viewModel = VPNViewModel.shared
    @State private var showingServerSelection = false
    @State private var showingSettings = false
    @State private var showingStatistics = false
    @State private var showingHelp = false
    
    // MARK: - Helper Views
    
    private var backgroundShape: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Background
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Navigation Bar с кнопкой назад
                ALADDINNavigationBar(
                    title: "🔒 ALADDIN VPN",
                    subtitle: "Защита вашего интернета",
                    showBackButton: true,
                    onBack: {
                        dismiss()
                    }
                )
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("Навигационная панель VPN экрана")
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        
                        // VPN Status Card
                        vpnStatusCard
                        
                        // Connection Info
                        connectionInfoCard
                        
                        // Server Selection
                        serverSelectionCard
                        
                        // Security Features
                        securityFeaturesCard
                        
                        // Statistics
                        statisticsCard
                        
                        // Quick Actions
                        quickActionsCard
                        
                        // Antivirus Section
                        antivirusCard
                        
                        // Bypass Protection Section
                        bypassProtectionCard
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, Spacing.m)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Список карточек VPN информации")
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showingServerSelection) {
            ServerSelectionView(selectedServer: .constant(VPNServer(id: "1", country: "RU", city: "Москва", flag: "🇷🇺", ping: 12, load: 45, status: .optimal)))
        }
        .sheet(isPresented: $showingSettings) {
            VPNSettingsView()
        }
    }
    
    // MARK: - VPN Status Card
    
    private var vpnStatusCard: some View {
        VStack(spacing: Spacing.m) {
            // Status Icon
            ZStack {
                Circle()
                    .fill(viewModel.isVPNEnabled ? Color.successGreen : Color.dangerRed)
                    .frame(width: 120, height: 120)
                    .opacity(0.2)
                
                Image(systemName: viewModel.isVPNEnabled ? "shield.fill" : "shield.slash.fill")
                    .font(.system(size: 48))
                    .foregroundColor(viewModel.isVPNEnabled ? .successGreen : .dangerRed)
            }
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(viewModel.isVPNEnabled ? "VPN защита активна" : "VPN защита неактивна")
            .accessibilityHint("Статус VPN соединения")
            
            // Status Text
            VStack(spacing: Spacing.s) {
                Text(viewModel.isVPNEnabled ? "ЗАЩИЩЕНО" : "НЕ ЗАЩИЩЕНО")
                    .font(.h1)
                    .fontWeight(.bold)
                    .foregroundColor(viewModel.isVPNEnabled ? .successGreen : .dangerRed)
                    .accessibilityLabel(viewModel.isVPNEnabled ? "Статус: Защищено" : "Статус: Не защищено")
                
                Text(viewModel.isVPNEnabled ? "Ваше соединение защищено" : "Подключитесь к VPN для защиты")
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .accessibilityLabel(viewModel.isVPNEnabled ? "Ваше соединение защищено" : "Подключитесь к VPN для защиты")
            }
            
            // Connection Button
            Button(action: {
                viewModel.toggleVPN()
            }) {
                HStack(spacing: Spacing.s) {
                    Image(systemName: viewModel.isVPNEnabled ? "stop.fill" : "play.fill")
                        .font(.title2)
                    
                    Text(viewModel.isVPNEnabled ? "ОТКЛЮЧИТЬ" : "ПОДКЛЮЧИТЬ")
                        .font(.headline)
                        .fontWeight(.semibold)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: Size.buttonHeight)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(viewModel.isConnected ? Color.dangerRed : Color.successGreen)
                )
            }
            .accessibilityLabel(viewModel.isVPNEnabled ? "Отключить VPN" : "Подключить VPN")
            .accessibilityHint("Нажмите для переключения VPN соединения")
            .accessibilityAddTraits(.isButton)
            .buttonStyle(PlainButtonStyle())
        }
        .padding(Spacing.cardPadding)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.backgroundMedium.opacity(0.5))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color(red: 1.0, green: 1.0, blue: 1.0).opacity(0.1), lineWidth: 1)
                )
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Connection Info Card
    
    private var connectionInfoCard: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ИНФОРМАЦИЯ О СОЕДИНЕНИИ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
            }
            
            VStack(spacing: Spacing.s) {
                HStack {
                    Image(systemName: "globe")
                        .font(.system(size: 16))
                        .foregroundColor(.primaryBlue)
                    Text("Сервер")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(viewModel.selectedServer.name)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Сервер: \(viewModel.selectedServer.name)")
                
                HStack {
                    Image(systemName: "speedometer")
                        .font(.system(size: 16))
                        .foregroundColor(.successGreen)
                    Text("Скорость")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text("100 Мбит/с")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Скорость: 100 Мбит в секунду")
                
                HStack {
                    Image(systemName: "clock")
                        .font(.system(size: 16))
                        .foregroundColor(.textSecondary)
                    Text("Время подключения")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(viewModel.connectionTime)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Время подключения: \(viewModel.connectionTime)")
                
                HStack {
                    Image(systemName: "arrow.up.arrow.down")
                        .font(.system(size: 16))
                        .foregroundColor(.textSecondary)
                    Text("Передано данных")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text("\(viewModel.downloadedToday) / \(viewModel.uploadedToday)")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Передано данных: \(viewModel.downloadedToday) / \(viewModel.uploadedToday)")
            }
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Server Selection Card
    
    private var serverSelectionCard: some View {
        VStack(spacing: Spacing.m) {
            serverSelectionHeader
            serverSelectionContent
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    private var serverSelectionHeader: some View {
        HStack {
            Text("ВЫБОР СЕРВЕРА")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)
            
            Spacer()
            
            Button(action: {
                showingServerSelection = true
            }) {
                Text("Изменить")
                    .font(.body)
                    .foregroundColor(.primaryBlue)
            }
            .accessibilityLabel("Изменить сервер")
            .accessibilityHint("Нажмите для выбора другого VPN сервера")
            .accessibilityAddTraits(.isButton)
        }
    }
    
    private var serverSelectionContent: some View {
        HStack(spacing: Spacing.m) {
            // Flag
            Text(viewModel.selectedServer.flag)
                .font(.system(size: 32))
                .accessibilityLabel("Флаг страны \(viewModel.selectedServer.name)")
            
            serverInfoStack
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .font(.system(size: 14))
                .foregroundColor(.textSecondary)
        }
        .padding(Spacing.m)
        .background(serverInfoBackground)
    }
    
    private var serverInfoStack: some View {
        VStack(alignment: .leading, spacing: Spacing.xxs) {
            Text(viewModel.selectedServer.name)
                .font(.headline)
                .foregroundColor(.textPrimary)
                .accessibilityLabel("Название сервера: \(viewModel.selectedServer.name)")
            
            Text(viewModel.selectedServer.location)
                .font(.body)
                .foregroundColor(.textSecondary)
                .accessibilityLabel("Местоположение: \(viewModel.selectedServer.location)")
            
            serverStatusIndicator
        }
    }
    
    private var serverStatusIndicator: some View {
        HStack(spacing: Spacing.xs) {
            Circle()
                .fill(serverStatusColor)
                .frame(width: 8, height: 8)
                .accessibilityLabel(serverStatusAccessibilityLabel)
            
            Text(serverStatusText)
                .font(.caption)
                .foregroundColor(.textSecondary)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(serverStatusAccessibilityLabel)
    }
    
    private var serverStatusColor: Color {
        viewModel.selectedServer.status == .optimal ? Color.successGreen : Color.warningOrange
    }
    
    private var serverStatusText: String {
        viewModel.selectedServer.status == .optimal ? "Оптимальный" : "Загружен"
    }
    
    private var serverStatusAccessibilityLabel: String {
        "Статус сервера: \(serverStatusText)"
    }
    
    private var serverInfoBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.medium)
            .fill(Color.backgroundMedium.opacity(0.3))
    }
    
    // MARK: - Security Features Card
    
    private var securityFeaturesCard: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("ФУНКЦИИ БЕЗОПАСНОСТИ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: Spacing.m) {
                
                SecurityFeatureCard(
                    icon: "shield.fill",
                    title: "Блокировка рекламы",
                    isEnabled: true,
                    color: .successGreen
                )
                
                SecurityFeatureCard(
                    icon: "eye.slash.fill",
                    title: "Антитрекинг",
                    isEnabled: true,
                    color: .successGreen
                )
                
                SecurityFeatureCard(
                    icon: "lock.fill",
                    title: "Шифрование",
                    isEnabled: true,
                    color: .successGreen
                )
                
                SecurityFeatureCard(
                    icon: "exclamationmark.triangle.fill",
                    title: "Защита от угроз",
                    isEnabled: true,
                    color: .successGreen
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Statistics Card
    
    private var statisticsCard: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("СТАТИСТИКА")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            
            HStack(spacing: Spacing.l) {
                VStack(spacing: 5) {
                    Text("🛡️")
                        .font(.system(size: 24))
                    Text("\(viewModel.threatsBlocked)")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.white)
                    Text("Угроз\nблокировано")
                        .font(.system(size: 10))
                        .foregroundColor(.white.opacity(0.8))
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                        .minimumScaleFactor(0.8)
                }
                .frame(maxWidth: .infinity)
                
                Rectangle()
                    .fill(Color.white.opacity(0.2))
                    .frame(width: 1, height: 40)
                
                VStack(spacing: 5) {
                    Text("📊")
                        .font(.system(size: 24))
                    Text("2.4 GB")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.white)
                    Text("Данных\nсэкономлено")
                        .font(.system(size: 10))
                        .foregroundColor(.white.opacity(0.8))
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                        .minimumScaleFactor(0.8)
                }
                .frame(maxWidth: .infinity)
                
                Rectangle()
                    .fill(Color.white.opacity(0.2))
                    .frame(width: 1, height: 40)
                
                VStack(spacing: 5) {
                    Text("⏰")
                        .font(.system(size: 24))
                    Text("24:00")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.white)
                    Text("Время\nзащиты")
                        .font(.system(size: 10))
                        .foregroundColor(.white.opacity(0.8))
                        .multilineTextAlignment(.center)
                        .lineLimit(2)
                        .minimumScaleFactor(0.8)
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Quick Actions Card
    
    private var quickActionsCard: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("БЫСТРЫЕ ДЕЙСТВИЯ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            
            HStack(spacing: Spacing.s) {
                Button(action: { showingSettings = true }) {
                    VStack(spacing: 8) {
                        Image(systemName: "gearshape.fill")
                            .font(.title3)
                            .foregroundColor(.primaryBlue)
                        Text("Настройки")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.textPrimary)
                            .lineLimit(1)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 80)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                }
                .buttonStyle(PlainButtonStyle())
                
                Button(action: { showingStatistics = true }) {
                    VStack(spacing: 8) {
                        Image(systemName: "chart.bar.fill")
                            .font(.title3)
                            .foregroundColor(.primaryBlue)
                        Text("Статистика")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.textPrimary)
                            .lineLimit(1)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 80)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                }
                .buttonStyle(PlainButtonStyle())
                
                Button(action: { showingHelp = true }) {
                    VStack(spacing: 8) {
                        Image(systemName: "questionmark.circle.fill")
                            .font(.title3)
                            .foregroundColor(.primaryBlue)
                        Text("Помощь")
                            .font(.system(size: 11, weight: .semibold))
                            .foregroundColor(.textPrimary)
                            .lineLimit(1)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 80)
                    .background(
                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                            .fill(Color.backgroundMedium.opacity(0.3))
                    )
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
        .sheet(isPresented: $showingStatistics) {
            VPNStatisticsView()
        }
        .sheet(isPresented: $showingHelp) {
            VPNHelpView()
        }
    }
    
    // MARK: - Antivirus Card
    
    private var antivirusCard: some View {
        VStack(spacing: Spacing.m) {
            // Header
            HStack {
                Text("🛡️ Антивирус")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Text("Активен")
                    .font(.caption)
                    .foregroundColor(.successGreen)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(
                        Capsule()
                            .fill(Color.successGreen.opacity(0.2))
                    )
            }
            
            // Stats Grid
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: Spacing.s) {
                AntivirusStatItem(icon: "🔍", value: "1,247", label: "Файлов проверено")
                AntivirusStatItem(icon: "✅", value: "0", label: "Угроз найдено")
                AntivirusStatItem(icon: "🔄", value: "2ч назад", label: "Последняя проверка")
                AntivirusStatItem(icon: "⚡", value: "100%", label: "Защита")
            }
            
            // Scan Button
            Button(action: {
                // Запустить проверку
                print("Запуск антивирусной проверки")
            }) {
                HStack {
                    Image(systemName: "play.circle.fill")
                        .font(.title3)
                    Text("Запустить проверку")
                        .font(.headline)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 44)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(Color.primaryBlue)
                )
            }
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Bypass Protection Card
    
    private var bypassProtectionCard: some View {
        VStack(spacing: Spacing.m) {
            // Header
            HStack {
                Text("🚨 Защита от обхода")
                    .font(.h3)
                    .foregroundColor(.warningOrange)
                
                Spacer()
            }
            
            // Stats Grid 3 columns
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: Spacing.m) {
                VStack(spacing: 4) {
                    Text("0")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.successGreen)
                    Text("Попыток сегодня")
                        .font(.system(size: 10))
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                
                VStack(spacing: 4) {
                    Text("47")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.warningOrange)
                    Text("Всего за неделю")
                        .font(.system(size: 10))
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                
                VStack(spacing: 4) {
                    Text("100%")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.successGreen)
                    Text("Заблокировано")
                        .font(.system(size: 10))
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
            }
            
            // Detection Items (Accordion style from HTML)
            VStack(spacing: 8) {
                BypassDetectionItem(icon: "🌐", title: "Детекция VPN", enabled: true)
                BypassDetectionItem(icon: "🕶️", title: "Детекция Инкогнито", enabled: true)
                BypassDetectionItem(icon: "🧅", title: "Детекция Tor", enabled: true)
                BypassDetectionItem(icon: "🔀", title: "Детекция Proxy", enabled: true)
            }
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Bypass Detection Item

struct BypassDetectionItem: View {
    let icon: String
    let title: String
    @State private var enabled: Bool
    @State private var isExpanded: Bool = false
    
    init(icon: String, title: String, enabled: Bool = true) {
        self.icon = icon
        self.title = title
        self._enabled = State(initialValue: enabled)
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header (always visible)
            Button(action: {
                withAnimation {
                    isExpanded.toggle()
                }
            }) {
                HStack {
                    Text(icon)
                        .font(.system(size: 22))
                    Text(title)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.textPrimary)
                    Spacer()
                    Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                        .font(.system(size: 12))
                        .foregroundColor(.textSecondary)
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 12)
            }
            
            // Content (expandable)
            if isExpanded {
                VStack(spacing: 8) {
                    Rectangle()
                        .fill(Color.white.opacity(0.1))
                        .frame(height: 1)
                        .padding(.horizontal, 12)
                    
                    HStack {
                        Text(enabled ? "Статус защиты: Включено" : "Статус защиты: Выключено")
                            .font(.system(size: 12))
                            .foregroundColor(.textSecondary)
                        
                        Spacer()
                        
                        // Toggle Switch
                        Toggle("", isOn: $enabled)
                            .toggleStyle(SwitchToggleStyle(tint: enabled ? .successGreen : .gray))
                    }
                    .padding(.horizontal, 12)
                    .padding(.bottom, 12)
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white.opacity(0.05))
        )
    }
}

// MARK: - Supporting Views


struct SecurityFeatureCard: View {
    let icon: String
    let title: String
    let isEnabled: Bool
    let color: Color
    
    var body: some View {
        VStack(spacing: Spacing.s) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.textPrimary)
                .multilineTextAlignment(.center)
            
            Circle()
                .fill(isEnabled ? color : Color.textSecondary)
                .frame(width: 12, height: 12)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.s)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
    }
}


struct QuickActionButton: View {
    let icon: String
    let title: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: Spacing.s) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.primaryBlue)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.textPrimary)
            }
            .frame(maxWidth: .infinity)
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
                    .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Antivirus Stat Item

struct AntivirusStatItem: View {
    let icon: String
    let value: String
    let label: String
    
    var body: some View {
        VStack(spacing: 4) {
            Text(icon)
                .font(.system(size: 24))
            Text(value)
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(.white)
            Text(label)
                .font(.system(size: 9))
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.s)
    }
}

// MARK: - Placeholder Views

struct ServerSelectionView: View {
    @Binding var selectedServer: VPNServer
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack {
                Text("Выбор сервера")
                    .font(.title)
                Text("Здесь будет список серверов")
                    .foregroundColor(.secondary)
                Spacer()
            }
            .navigationTitle("Серверы")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct VPNSettingsView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            List {
                Section("Сервер") {
                    HStack {
                        Text("Автовыбор сервера")
                        Spacer()
                        Toggle("", isOn: .constant(true))
                    }
                    HStack {
                        Text("Страна по умолчанию")
                        Spacer()
                        Text("Россия")
                            .foregroundColor(.secondary)
                    }
                }
                
                Section("Подключение") {
                    HStack {
                        Text("Автоподключение при Wi‑Fi")
                        Spacer()
                        Toggle("", isOn: .constant(true))
                    }
                    HStack {
                        Text("Автоподключение при мобильной сети")
                        Spacer()
                        Toggle("", isOn: .constant(false))
                    }
                }
                
                Section("Безопасность") {
                    HStack {
                        Text("Kill Switch")
                        Spacer()
                        Toggle("", isOn: .constant(true))
                    }
                    HStack {
                        Text("DNS Леak Protection")
                        Spacer()
                        Toggle("", isOn: .constant(true))
                    }
                }
            }
            .navigationTitle("Настройки VPN")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct VPNStatisticsView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Stats Cards
                    HStack(spacing: 15) {
                        VStack(spacing: 8) {
                            Text("🛡️")
                                .font(.system(size: 40))
                            Text("47")
                                .font(.system(size: 32, weight: .bold))
                                .foregroundColor(.white)
                            Text("Угроз\nблокировано")
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.8))
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(20)
                        .background(
                            RoundedRectangle(cornerRadius: 15)
                                .fill(Color.blue.opacity(0.3))
                        )
                        
                        VStack(spacing: 8) {
                            Text("⏰")
                                .font(.system(size: 40))
                            Text("24:00:00")
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.white)
                            Text("Время\nзащиты")
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.8))
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(20)
                        .background(
                            RoundedRectangle(cornerRadius: 15)
                                .fill(Color.green.opacity(0.3))
                        )
                    }
                    
                    HStack(spacing: 15) {
                        VStack(spacing: 8) {
                            Text("⬇️")
                                .font(.system(size: 40))
                            Text("2.4 GB")
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.white)
                            Text("Загружено\nсегодня")
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.8))
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(20)
                        .background(
                            RoundedRectangle(cornerRadius: 15)
                                .fill(Color.purple.opacity(0.3))
                        )
                        
                        VStack(spacing: 8) {
                            Text("⬆️")
                                .font(.system(size: 40))
                            Text("1.2 GB")
                                .font(.system(size: 20, weight: .bold))
                                .foregroundColor(.white)
                            Text("Отправлено\nсегодня")
                                .font(.system(size: 12))
                                .foregroundColor(.white.opacity(0.8))
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(20)
                        .background(
                            RoundedRectangle(cornerRadius: 15)
                                .fill(Color.orange.opacity(0.3))
                        )
                    }
                }
                .padding()
            }
            .navigationTitle("Статистика")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct VPNHelpView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("Часто задаваемые вопросы")
                        .font(.title2)
                        .fontWeight(.bold)
                        .padding(.horizontal)
                    
                    VStack(spacing: 15) {
                        HelpCard(
                            question: "Как подключить VPN?",
                            answer: "Нажмите большую кнопку 'ПОДКЛЮЧИТЬ' в центре экрана. Соединение установится автоматически."
                        )
                        
                        HelpCard(
                            question: "Как выбрать сервер?",
                            answer: "Нажмите на карточку 'Выбор сервера' и выберите страну из списка."
                        )
                        
                        HelpCard(
                            question: "Что такое Kill Switch?",
                            answer: "Функция автоматически отключает интернет, если VPN соединение прерывается."
                        )
                        
                        HelpCard(
                            question: "Влияет ли VPN на скорость?",
                            answer: "Минимальное влияние. Мы используем быстрые серверы для оптимальной скорости."
                        )
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .navigationTitle("Помощь")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Готово") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct HelpCard: View {
    let question: String
    let answer: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(question)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(.white)
            
            Text(answer)
                .font(.system(size: 14))
                .foregroundColor(.white.opacity(0.8))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white.opacity(0.1))
        )
    }
}

#if DEBUG
struct VPNScreen_Previews: PreviewProvider {
    static var previews: some View {
        VPNScreen()
    }
}
#endif
