import SwiftUI

/**
 * 🔒 Network Protection Screen
 * Полноценный экран защиты сети
 * Источник: 02_protection_screen.html (38KB)
 */

struct NetworkProtectionScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var networkProtectionManager = NetworkProtectionManager.shared
    @StateObject private var antivirusManager = AntivirusManager.shared
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
                    title: localizationManager.localized("secure_connection_title"),
                    subtitle: localizationManager.localized("secure_connection_subtitle"),
                    showBackButton: true,
                    onBack: {
                        dismiss()
                    }
                )
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(localizationManager.localized("network_protection_nav_panel"))
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        
                        // Antivirus Section (1-я позиция - СВЕРХУ)
                        antivirusCard
                        
                        // Battery Saving Tip
                        batterySavingTipCard
                        
                        // Security Features
                        securityFeaturesCard
                        
                        // Quick Actions
                        quickActionsCard
                        
                        // ✅ УДАЛЕНО: Безопасное соединение Status Card (5-я позиция - СНИЗУ)
                        // secureConnectionStatusCard
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.top, Spacing.m)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("network_protection_cards_list"))
            }
        }
        .navigationBarHidden(true)
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("network_protection_screen_lang_\(localizationManager.currentLanguage.rawValue)")
        .sheet(isPresented: $showingSettings) {
            NetworkProtectionSettingsView()
        }
    }
    
    // MARK: - Безопасное соединение Status Card (компактная версия)
    
    private var secureConnectionStatusCard: some View {
        VStack(spacing: Spacing.m) {
            // Заголовок и индикатор
            HStack {
                Text(localizationManager.localized("secure_connection_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                // Индикатор (красный/зеленый) небольшого размера
                Circle()
                    .fill(networkProtectionManager.isConnected ? Color.successGreen : Color.dangerRed)
                    .frame(width: 20, height: 20)
                    .accessibilityLabel(networkProtectionManager.isConnected ? localizationManager.localized("secure_connection_active") : localizationManager.localized("secure_connection_inactive"))
            }
            
            // Connection Button
            Button(action: {
                if networkProtectionManager.isConnected {
                    networkProtectionManager.disconnect()
                } else {
                    networkProtectionManager.connect()
                }
            }) {
                HStack(spacing: Spacing.s) {
                    Image(systemName: networkProtectionManager.isConnected ? "stop.fill" : "play.fill")
                        .font(.title2)
                    
                    Text(networkProtectionManager.isConnected ? localizationManager.localized("network_protection.disconnect") : localizationManager.localized("network_protection.connect"))
                        .font(.headline)
                        .fontWeight(.semibold)
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .frame(height: Size.buttonHeight)
                .background(
                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                        .fill(networkProtectionManager.isConnected ? Color.dangerRed : Color.successGreen)
                )
            }
            .accessibilityLabel(networkProtectionManager.isConnected ? localizationManager.localized("network_protection_disconnect_action") : localizationManager.localized("network_protection_connect_action"))
            .accessibilityHint(localizationManager.localized("network_protection_toggle_hint"))
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
    
    
    // MARK: - Battery Saving Tip Card
    
    private var batterySavingTipCard: some View {
        HStack(spacing: Spacing.m) {
            Image(systemName: "battery.100.bolt")
                .font(.system(size: 24))
                .foregroundColor(.warningOrange)
                .accessibilityLabel(localizationManager.localized("network_protection_battery_icon"))
            
            VStack(alignment: .leading, spacing: 4) {
                Text(localizationManager.localized("network_protection_battery_saving"))
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.textPrimary)
                
                Text(localizationManager.localized("secure_connection_battery_saving_desc"))
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
        .accessibilityLabel(localizationManager.localized("secure_connection_battery_saving_desc"))
    }
    
    
    // MARK: - Security Features Card
    
    private var securityFeaturesCard: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("network_protection_security_features"))
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
                    title: localizationManager.localized("network_protection_ad_blocking"),
                    isEnabled: true,
                    color: .successGreen
                )
                
                SecurityFeatureCard(
                    icon: "eye.slash.fill",
                    title: localizationManager.localized("network_protection_anti_tracking"),
                    isEnabled: true,
                    color: .successGreen
                )
                
                SecurityFeatureCard(
                    icon: "exclamationmark.triangle.fill",
                    title: localizationManager.localized("network_protection_threat_protection"),
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
    
    
    // MARK: - Quick Actions Card
    
    private var quickActionsCard: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("network_protection_quick_actions"))
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
                        Text(localizationManager.localized("network_protection_settings"))
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
                        Text(localizationManager.localized("network_protection.statistics"))
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
                        Text(localizationManager.localized("network_protection_help"))
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
            NetworkProtectionStatisticsView()
        }
        .sheet(isPresented: $showingHelp) {
            NetworkProtectionHelpView()
        }
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("network_protection_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    // MARK: - Antivirus Card
    
    @AppStorage("antivirusEnabled") private var antivirusEnabled = true
    
    private var antivirusCard: some View {
        VStack(spacing: Spacing.m) {
            // Header
            HStack {
                Text(localizationManager.localized("network_protection_antivirus"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                // Toggle для включения/выключения антивируса
                Toggle("", isOn: $antivirusEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .successGreen))
                
                Text(antivirusEnabled ? localizationManager.localized("network_protection_active") : localizationManager.localized("network_protection_inactive"))
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
                AntivirusStatItem(icon: "🔍", value: formatScanCount(), label: localizationManager.localized("network_protection_files_scanned"))
                AntivirusStatItem(icon: "✅", value: "\(antivirusManager.threatsDetected.count)", label: localizationManager.localized("network_protection_threats_found"))
                AntivirusStatItem(icon: "🔄", value: formatLastScan(), label: localizationManager.localized("network_protection_ago"))
                AntivirusStatItem(icon: "⚡", value: antivirusEnabled ? "100%" : "0%", label: localizationManager.localized("network_protection_protection"))
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
                    Text(antivirusManager.isScanning ? localizationManager.localized("network_protection_scanning") : localizationManager.localized("network_protection_start_scan"))
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
                return localizationManager.localized("network_protection_just_now")
            } else if interval < 3600 {
                return "\(Int(interval / 60))\(localizationManager.localized("network_protection_min"))"
            } else {
                return "\(Int(interval / 3600))\(localizationManager.localized("network_protection_hour"))"
            }
        }
        return localizationManager.localized("network_protection_never")
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
    @Binding var selectedServer: NetworkProtectionServer
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    private let apiService = APIService.shared
    @State private var availableServers: [NetworkProtectionServer] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let error = errorMessage {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 48))
                            .foregroundColor(.warningOrange)
                        Text(error)
                            .foregroundColor(.textSecondary)
                            .multilineTextAlignment(.center)
                        Button(localizationManager.localized("network_protection_retry")) {
                            loadServers()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding(Spacing.screenPadding)
                } else {
                    List(availableServers) { server in
                        ServerRowView(
                            server: server,
                            isSelected: server.id == selectedServer.id,
                            onSelect: {
                                selectedServer = server
                                dismiss()
                            }
                        )
                    }
                    .listStyle(.insetGrouped)
                }
            }
            .navigationTitle(localizationManager.localized("network_protection.server"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("network_protection_done")) {
                        dismiss()
                    }
                }
            }
            .onAppear {
                loadServers()
            }
        }
    }
    
    private func loadServers() {
        isLoading = true
        errorMessage = nil
        
        apiService.getNetworkProtectionServers { result in
            DispatchQueue.main.async {
                isLoading = false
                switch result {
                case .success(let servers):
                    self.availableServers = servers.sorted { $0.ping < $1.ping }
                case .failure(let error):
                    // Fallback на локальные серверы
                    let networkProtectionManager = NetworkProtectionManager.shared
                    let networkProtectionManagerServers = networkProtectionManager.getAvailableServers()
                    // Используем NetworkProtectionServer из APIModels
                    self.availableServers = networkProtectionManagerServers.map { networkProtectionServer in
                        NetworkProtectionServer(
                            id: networkProtectionServer.id,
                            country: networkProtectionServer.country,
                            city: networkProtectionServer.name,
                            flag: networkProtectionServer.flag,
                            ping: networkProtectionServer.ping,
                            load: networkProtectionServer.load,
                            status: networkProtectionServer.load > 80 ? .loaded : .optimal
                        )
                    }.sorted { $0.ping < $1.ping }
                    self.errorMessage = error.localizedDescription
                }
            }
        }
    }
}

struct ServerRowView: View {
    let server: NetworkProtectionServer
    let isSelected: Bool
    let onSelect: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        Button(action: onSelect) {
            HStack(spacing: Spacing.m) {
                // Флаг
                Text(server.flag)
                    .font(.system(size: 32))
                
                // Информация о сервере
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(server.localizedName(localizationManager))
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    
                    Text(server.location)
                        .font(.subheadline)
                        .foregroundColor(.textSecondary)
                    
                    HStack(spacing: Spacing.xs) {
                        // Ping
                        Label("\(server.ping) ms", systemImage: "speedometer")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        
                        // Load
                        Label("\(server.load)%", systemImage: "chart.bar.fill")
                            .font(.caption)
                            .foregroundColor(server.load < 50 ? .successGreen : .warningOrange)
                    }
                }
                
                Spacer()
                
                // Статус
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.primaryBlue)
                        .font(.system(size: 24))
                } else {
                    Circle()
                        .fill(server.status == .optimal ? Color.successGreen : Color.warningOrange)
                        .frame(width: 12, height: 12)
                }
            }
            .padding(.vertical, Spacing.xs)
        }
        .buttonStyle(.plain)
    }
}

struct NetworkProtectionSettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var networkProtectionManager = NetworkProtectionManager.shared
    @AppStorage("network_protection_auto_select_server") private var autoSelectServer = true
    @AppStorage("network_protection_auto_connect_wifi") private var autoConnectWiFi = true
    @AppStorage("network_protection_auto_connect_mobile") private var autoConnectMobile = false
    @AppStorage("network_protection_kill_switch") private var killSwitch = true
    @AppStorage("network_protection_dns_leak_protection") private var dnsLeakProtection = true
    
    var body: some View {
        NavigationView {
            List {
                Section(localizationManager.localized("network_protection_server_section")) {
                    HStack {
                        Text(localizationManager.localized("network_protection_auto_server"))
                        Spacer()
                        Toggle("", isOn: $autoSelectServer)
                    }
                }
                
                Section(localizationManager.localized("network_protection_connection_section")) {
                    HStack {
                        Text(localizationManager.localized("network_protection_auto_wifi"))
                        Spacer()
                        Toggle("", isOn: $autoConnectWiFi)
                    }
                    HStack {
                        Text(localizationManager.localized("network_protection_auto_mobile"))
                        Spacer()
                        Toggle("", isOn: $autoConnectMobile)
                    }
                }
                
                Section(localizationManager.localized("network_protection_security_section")) {
                    HStack {
                        Text(localizationManager.localized("network_protection_kill_switch"))
                        Spacer()
                        Toggle("", isOn: $killSwitch)
                    }
                    HStack {
                        Text(localizationManager.localized("network_protection_dns_leak"))
                        Spacer()
                        Toggle("", isOn: $dnsLeakProtection)
                    }
                }
                
                Section(localizationManager.localized("network_protection_battery_saving_section")) {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(localizationManager.localized("network_protection_auto_disconnect"))
                                .font(.body)
                            Text(localizationManager.localized("network_protection_auto_disconnect_desc"))
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        Toggle("", isOn: $networkProtectionManager.batteryOptimizationEnabled)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("network_protection_settings_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("network_protection_done")) {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct NetworkProtectionStatisticsView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
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
                            Text(localizationManager.localized("network_protection.threats.blocked"))
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
                            Text(localizationManager.localized("network_protection_protection_time"))
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
                            Text(localizationManager.localized("network_protection.uploaded"))
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
                            Text(localizationManager.localized("network_protection.downloaded"))
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
            .navigationTitle(localizationManager.localized("network_protection.statistics"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("network_protection_done")) {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct NetworkProtectionHelpView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text(localizationManager.localized("network_protection_faq"))
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .padding(.horizontal)
                    
                    VStack(spacing: 15) {
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_antivirus_question"),
                            answer: localizationManager.localized("network_protection_help_antivirus_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_ad_blocking_question"),
                            answer: localizationManager.localized("network_protection_help_ad_blocking_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_anti_tracking_question"),
                            answer: localizationManager.localized("network_protection_help_anti_tracking_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_encryption_question"),
                            answer: localizationManager.localized("network_protection_help_encryption_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_threat_protection_question"),
                            answer: localizationManager.localized("network_protection_help_threat_protection_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_incognito_question"),
                            answer: localizationManager.localized("network_protection_help_incognito_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_tor_question"),
                            answer: localizationManager.localized("network_protection_help_tor_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_proxy_question"),
                            answer: localizationManager.localized("network_protection_help_proxy_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_kill_switch_question"),
                            answer: localizationManager.localized("network_protection_help_kill_switch_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("network_protection_help_dns_leak_question"),
                            answer: localizationManager.localized("network_protection_help_dns_leak_answer")
                        )
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .navigationTitle(localizationManager.localized("network_protection_help"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("network_protection_done")) {
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
struct NetworkProtectionScreen_Previews: PreviewProvider {
    static var previews: some View {
        NetworkProtectionScreen()
    }
}
#endif
