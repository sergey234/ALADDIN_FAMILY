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
    @StateObject private var antivirusManager = AntivirusManager.shared
    @State private var showingServerSelection = false
    @State private var showingSettings = false
    @State private var showingStatistics = false
    @State private var showingHelp = false
    @State private var isThirdPartyVPNDetectionEnabled: Bool = true
    
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
                        
                        // Battery Saving Tip
                        batterySavingTipCard
                        
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
                        
                        // Third-Party VPN Detection Section
                        thirdPartyVPNDetectionCard
                        
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
    
    // MARK: - Battery Saving Tip Card
    
    private var batterySavingTipCard: some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: "battery.100.bolt")
                .font(.system(size: 24))
                .foregroundColor(.warningOrange)
                .accessibilityLabel("Иконка экономии батареи")
            
            VStack(alignment: .leading, spacing: 4) {
                Text("💡 Экономия батареи")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.textPrimary)
                
                Text("VPN автоматически отключается через 5 минут бездействия для экономии заряда")
                    .font(.system(size: 11))
                    .foregroundColor(.textSecondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            
            Spacer()
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.warningOrange.opacity(0.1))
                .overlay(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .stroke(Color.warningOrange.opacity(0.3), lineWidth: 1)
                )
        )
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Рекомендация: VPN автоматически отключается через 5 минут бездействия для экономии батареи")
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
    
    @AppStorage("antivirusEnabled") private var antivirusEnabled = true
    
    private var antivirusCard: some View {
        VStack(spacing: Spacing.m) {
            // Header
            HStack {
                Text("🛡️ Антивирус")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                // Toggle для включения/выключения антивируса
                Toggle("", isOn: $antivirusEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .successGreen))
                
                Text(antivirusEnabled ? "Активен" : "Отключен")
                    .font(.caption)
                    .foregroundColor(antivirusEnabled ? .successGreen : .textSecondary)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(
                        Capsule()
                            .fill((antivirusEnabled ? Color.successGreen : Color.textSecondary).opacity(0.2))
                    )
            }
            
            // Stats Grid
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: Spacing.s) {
                AntivirusStatItem(icon: "🔍", value: formatScanCount(), label: "Файлов проверено")
                AntivirusStatItem(icon: "✅", value: "\(antivirusManager.threatsDetected.count)", label: "Угроз найдено")
                AntivirusStatItem(icon: "🔄", value: formatLastScan(), label: "Назад")
                AntivirusStatItem(icon: "⚡", value: antivirusEnabled ? "100%" : "0%", label: "Защита")
            }
            
            // Scan Button
            Button(action: {
                // Запустить проверку
                Task {
                    await performQuickScan()
                }
            }) {
                HStack {
                    Image(systemName: antivirusManager.isScanning ? "stop.circle.fill" : "play.circle.fill")
                        .font(.title3)
                    Text(antivirusManager.isScanning ? "Сканирование..." : "Запустить проверку")
                        .font(.headline)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: 44)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(antivirusEnabled ? Color.primaryBlue : Color.textSecondary)
                )
            }
            .disabled(!antivirusEnabled || antivirusManager.isScanning)
            .opacity(antivirusEnabled ? 1.0 : 0.5)
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    // MARK: - Antivirus Helper Functions
    
    private func formatScanCount() -> String {
        // Форматируем количество проверок
        if antivirusManager.lastScanResult != nil {
            return "1" // Пока просто показываем что была проверка
        }
        return "0"
    }
    
    private func formatLastScan() -> String {
        // Форматируем время последней проверки
        if let lastResult = antivirusManager.lastScanResult {
            let now = Date()
            let interval = now.timeIntervalSince(lastResult.scanTime)
            
            if interval < 60 {
                return "только что"
            } else if interval < 3600 {
                return "\(Int(interval / 60))мин"
            } else {
                return "\(Int(interval / 3600))ч"
            }
        }
        return "Никогда"
    }
    
    private func performQuickScan() async {
        // Быстрое сканирование демонстрационных файлов
        print("🛡️ Начато антивирусное сканирование...")
        
        // В реальном приложении здесь будет выбор файлов
        // Пока имитируем сканирование
        await MainActor.run {
            antivirusManager.isScanning = true
        }
        
        // Небольшая задержка для демонстрации
        try? await Task.sleep(nanoseconds: 2_000_000_000) // 2 секунды
        
        await MainActor.run {
            antivirusManager.isScanning = false
        }
        
        print("✅ Сканирование завершено")
    }
    
    // MARK: - Third-Party VPN Detection Card
    
    private var thirdPartyVPNDetectionCard: some View {
        VStack(spacing: Spacing.m) {
            // Header
            HStack {
                Text("🌐 Обнаружение сторонних VPN")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            
            // Description
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text("Обнаружение других VPN для защиты ALADDIN VPN")
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Text("NordVPN, ExpressVPN, Surfshark и др.")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            
            // Toggle
            HStack {
                Text(isThirdPartyVPNDetectionEnabled ? "Включено" : "Выключено")
                    .font(.body)
                    .foregroundColor(isThirdPartyVPNDetectionEnabled ? .successGreen : .textSecondary)
                
                Spacer()
                
                Toggle("", isOn: $isThirdPartyVPNDetectionEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .successGreen))
            }
            .padding(Spacing.m)
            .background(Color.backgroundMedium.opacity(0.3))
            .cornerRadius(CornerRadius.medium)
        }
        .padding(Spacing.cardPadding)
        .background(backgroundShape)
        .cardShadow()
        .padding(.horizontal, Spacing.screenPadding)
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
    @StateObject private var viewModel = VPNViewModel.shared
    @AppStorage("vpn_auto_select_server") private var autoSelectServer = true
    @AppStorage("vpn_auto_connect_wifi") private var autoConnectWiFi = true
    @AppStorage("vpn_auto_connect_mobile") private var autoConnectMobile = false
    @AppStorage("vpn_kill_switch") private var killSwitch = true
    @AppStorage("vpn_dns_leak_protection") private var dnsLeakProtection = true
    
    var body: some View {
        NavigationView {
            List {
                Section("Сервер") {
                    HStack {
                        Text("Автовыбор сервера")
                        Spacer()
                        Toggle("", isOn: $autoSelectServer)
                    }
                }
                
                Section("Подключение") {
                    HStack {
                        Text("Автоподключение при Wi‑Fi")
                        Spacer()
                        Toggle("", isOn: $autoConnectWiFi)
                    }
                    HStack {
                        Text("Автоподключение при мобильной сети")
                        Spacer()
                        Toggle("", isOn: $autoConnectMobile)
                    }
                }
                
                Section("Безопасность") {
                    HStack {
                        Text("Kill Switch")
                        Spacer()
                        Toggle("", isOn: $killSwitch)
                    }
                    HStack {
                        Text("DNS Leak Protection")
                        Spacer()
                        Toggle("", isOn: $dnsLeakProtection)
                    }
                }
                
                Section("Экономия батареи") {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Автоотключение")
                                .font(.body)
                            Text("Через 5 мин неактивности")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        Toggle("", isOn: $viewModel.autoDisconnectEnabled)
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
                        .foregroundColor(.white)
                        .padding(.horizontal)
                    
                    VStack(spacing: 15) {
                        HelpCard(
                            question: "Что такое Антивирус?",
                            answer: "Автоматическая проверка файлов на вирусы. Защищает телефон от вредоносного ПО. Можно выключить в настройках."
                        )
                        
                        HelpCard(
                            question: "Что такое Блокировка рекламы?",
                            answer: "Убирает рекламу в приложениях и браузерах. Ускоряет загрузку страниц и экономит трафик."
                        )
                        
                        HelpCard(
                            question: "Что такое Антитрекинг?",
                            answer: "Скрывает вашу активность от рекламных компаний. Они не смогут отслеживать ваши действия."
                        )
                        
                        HelpCard(
                            question: "Что такое Шифрование?",
                            answer: "Защищает данные от перехвата. Вся информация превращается в код, который никто не прочитает."
                        )
                        
                        HelpCard(
                            question: "Что такое Защита от угроз?",
                            answer: "Блокирует опасные сайты и вредоносное ПО до того, как они навредят вашему устройству."
                        )
                        
                        HelpCard(
                            question: "Что такое Детекция Скрытого режима?",
                            answer: "Обнаруживает попытки войти в приватный режим браузера для ограничения доступа к контенту."
                        )
                        
                        HelpCard(
                            question: "Что такое Детекция Tor?",
                            answer: "Блокирует использование анонимной сети Tor для предотвращения доступа к запрещенному контенту."
                        )
                        
                        HelpCard(
                            question: "Что такое Детекция Proxy?",
                            answer: "Обнаруживает использование прокси-серверов для скрытия реального IP-адреса."
                        )
                        
                        HelpCard(
                            question: "Что такое Kill Switch?",
                            answer: "Если VPN соединение разрывается, эта функция блокирует весь интернет-трафик для защиты данных."
                        )
                        
                                                HelpCard(
                            question: "Что такое DNS Leak Protection?",
                            answer: "Защищает от утечки DNS запросов. Все запросы идут через VPN сервер."
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
                .foregroundColor(.black)
            
            Text(answer)
                .font(.system(size: 14))
                .foregroundColor(.black.opacity(0.8))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.white)
        )
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
}

#if DEBUG
struct VPNScreen_Previews: PreviewProvider {
    static var previews: some View {
        VPNScreen()
    }
}
#endif
