import SwiftUI

/**
 * 🔒 VPN Protection Screen
 * Полноценный экран VPN защиты
 * Источник: 02_protection_screen.html (38KB)
 */

struct VPNScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
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
                    title: localizationManager.localized("vpn_title"),
                    subtitle: localizationManager.localized("vpn_subtitle"),
                    showBackButton: true,
                    onBack: {
                        dismiss()
                    }
                )
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(localizationManager.localized("vpn_nav_panel"))
                
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
                .accessibilityLabel(localizationManager.localized("vpn_cards_list"))
            }
        }
        .navigationBarHidden(true)
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("vpn_screen_lang_\(localizationManager.currentLanguage.rawValue)")
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
            .accessibilityLabel(viewModel.isVPNEnabled ? localizationManager.localized("vpn_protection_active") : localizationManager.localized("vpn_protection_inactive"))
            .accessibilityHint(localizationManager.localized("vpn_status_hint"))
            
            // Status Text
            VStack(spacing: Spacing.s) {
                Text(viewModel.isVPNEnabled ? localizationManager.localized("vpn_protected") : localizationManager.localized("vpn_not_protected"))
                    .font(.h1)
                    .fontWeight(.bold)
                    .foregroundColor(viewModel.isVPNEnabled ? .successGreen : .dangerRed)
                    .accessibilityLabel(viewModel.isVPNEnabled ? localizationManager.localized("vpn_status_protected") : localizationManager.localized("vpn_status_not_protected"))
                
                Text(viewModel.isVPNEnabled ? localizationManager.localized("vpn_connection_protected") : localizationManager.localized("vpn_connect_for_protection"))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .multilineTextAlignment(.center)
                    .accessibilityLabel(viewModel.isVPNEnabled ? localizationManager.localized("vpn_connection_protected") : localizationManager.localized("vpn_connect_for_protection"))
            }
            
            // Connection Button
            Button(action: {
                viewModel.toggleVPN()
            }) {
                HStack(spacing: Spacing.s) {
                    Image(systemName: viewModel.isVPNEnabled ? "stop.fill" : "play.fill")
                        .font(.title2)
                    
                    Text(viewModel.isVPNEnabled ? localizationManager.localized("vpn_disconnect") : localizationManager.localized("vpn_connect"))
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
            .accessibilityLabel(viewModel.isVPNEnabled ? localizationManager.localized("vpn_disconnect_action") : localizationManager.localized("vpn_connect_action"))
            .accessibilityHint(localizationManager.localized("vpn_toggle_hint"))
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
                Text(localizationManager.localized("vpn_connection_info"))
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
                    Text(localizationManager.localized("vpn_server"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(viewModel.selectedServer.localizedName(localizationManager))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(localizationManager.localized("vpn_server")): \(viewModel.selectedServer.localizedName(localizationManager))")
                
                HStack {
                    Image(systemName: "speedometer")
                        .font(.system(size: 16))
                        .foregroundColor(.successGreen)
                    Text(localizationManager.localized("vpn_speed"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(localizationManager.localized("vpn_speed_value"))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(localizationManager.localized("vpn_speed")): \(localizationManager.localized("vpn_speed_value"))")
                
                HStack {
                    Image(systemName: "clock")
                        .font(.system(size: 16))
                        .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("vpn_connection_time"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(viewModel.connectionTime)
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(localizationManager.localized("vpn_connection_time")): \(viewModel.connectionTime)")
                
                HStack {
                    Image(systemName: "arrow.up.arrow.down")
                        .font(.system(size: 16))
                        .foregroundColor(.textSecondary)
                    Text(localizationManager.localized("vpn_data_transferred"))
                        .font(.body)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text("\(viewModel.downloadedToday) / \(viewModel.uploadedToday)")
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("\(localizationManager.localized("vpn_data_transferred")): \(viewModel.downloadedToday) / \(viewModel.uploadedToday)")
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
                .accessibilityLabel(localizationManager.localized("vpn_battery_icon"))
            
            VStack(alignment: .leading, spacing: 4) {
                Text(localizationManager.localized("vpn_battery_saving"))
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(.textPrimary)
                
                Text(localizationManager.localized("vpn_battery_saving_desc"))
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
        .accessibilityLabel(localizationManager.localized("vpn_battery_saving_desc"))
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
            Text(localizationManager.localized("vpn_server_selection"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .accessibilityAddTraits(.isHeader)
            
            Spacer()
            
            Button(action: {
                showingServerSelection = true
            }) {
                Text(localizationManager.localized("vpn_change"))
                    .font(.body)
                    .foregroundColor(.primaryBlue)
            }
                .accessibilityLabel(localizationManager.localized("vpn_change_server"))
                .accessibilityHint(localizationManager.localized("vpn_change_server_hint"))
            .accessibilityAddTraits(.isButton)
        }
    }
    
    private var serverSelectionContent: some View {
        HStack(spacing: Spacing.m) {
            // Flag
            Text(viewModel.selectedServer.flag)
                .font(.system(size: 32))
                .accessibilityLabel("\(localizationManager.localized("vpn_country_flag")) \(viewModel.selectedServer.localizedName(localizationManager))")
            
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
            Text(viewModel.selectedServer.localizedName(localizationManager))
                .font(.headline)
                .foregroundColor(.textPrimary)
                .accessibilityLabel("\(localizationManager.localized("vpn_server_name")): \(viewModel.selectedServer.localizedName(localizationManager))")
            
            Text(viewModel.selectedServer.location)
                .font(.body)
                .foregroundColor(.textSecondary)
                .accessibilityLabel("\(localizationManager.localized("vpn_location")): \(viewModel.selectedServer.location)")
            
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
        viewModel.selectedServer.status == .optimal ? localizationManager.localized("vpn_server_optimal") : localizationManager.localized("vpn_server_loaded")
    }
    
    private var serverStatusAccessibilityLabel: String {
        "\(localizationManager.localized("vpn_server_status")): \(serverStatusText)"
    }
    
    private var serverInfoBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.medium)
            .fill(Color.backgroundMedium.opacity(0.3))
    }
    
    // MARK: - Security Features Card
    
    private var securityFeaturesCard: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("vpn_security_features"))
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
                    title: localizationManager.localized("vpn_ad_blocking"),
                    isEnabled: true,
                    color: .successGreen
                )
                
                SecurityFeatureCard(
                    icon: "eye.slash.fill",
                    title: localizationManager.localized("vpn_anti_tracking"),
                    isEnabled: true,
                    color: .successGreen
                )
                
                SecurityFeatureCard(
                    icon: "lock.fill",
                    title: localizationManager.localized("vpn_encryption"),
                    isEnabled: true,
                    color: .successGreen
                )
                
                SecurityFeatureCard(
                    icon: "exclamationmark.triangle.fill",
                    title: localizationManager.localized("vpn_threat_protection"),
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
                Text(localizationManager.localized("vpn_statistics"))
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
                    Text(localizationManager.localized("vpn_threats_blocked"))
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
                    Text(localizationManager.localized("vpn_data_saved"))
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
                    Text(localizationManager.localized("vpn_protection_time"))
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
                Text(localizationManager.localized("vpn_quick_actions"))
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
                        Text(localizationManager.localized("vpn_settings"))
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
                        Text(localizationManager.localized("vpn_statistics_title"))
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
                        Text(localizationManager.localized("vpn_help"))
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
        // ✅ Пересоздаём View при изменении языка для обновления всех текстов
        .id("vpn_lang_\(localizationManager.currentLanguage.rawValue)")
    }
    
    // MARK: - Antivirus Card
    
    @AppStorage("antivirusEnabled") private var antivirusEnabled = true
    
    private var antivirusCard: some View {
        VStack(spacing: Spacing.m) {
            // Header
            HStack {
                Text(localizationManager.localized("vpn_antivirus"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                // Toggle для включения/выключения антивируса
                Toggle("", isOn: $antivirusEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .successGreen))
                
                Text(antivirusEnabled ? localizationManager.localized("vpn_active") : localizationManager.localized("vpn_inactive"))
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
                AntivirusStatItem(icon: "🔍", value: formatScanCount(), label: localizationManager.localized("vpn_files_scanned"))
                AntivirusStatItem(icon: "✅", value: "\(antivirusManager.threatsDetected.count)", label: localizationManager.localized("vpn_threats_found"))
                AntivirusStatItem(icon: "🔄", value: formatLastScan(), label: localizationManager.localized("vpn_ago"))
                AntivirusStatItem(icon: "⚡", value: antivirusEnabled ? "100%" : "0%", label: localizationManager.localized("vpn_protection"))
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
                    Text(antivirusManager.isScanning ? localizationManager.localized("vpn_scanning") : localizationManager.localized("vpn_start_scan"))
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
                return localizationManager.localized("vpn_just_now")
            } else if interval < 3600 {
                return "\(Int(interval / 60))\(localizationManager.localized("vpn_min"))"
            } else {
                return "\(Int(interval / 3600))\(localizationManager.localized("vpn_hour"))"
            }
        }
        return localizationManager.localized("vpn_never")
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
                Text(localizationManager.localized("vpn_third_party_detection"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                
                Spacer()
            }
            
            // Description
            VStack(alignment: .leading, spacing: Spacing.s) {
                Text(localizationManager.localized("vpn_third_party_desc"))
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Text(localizationManager.localized("vpn_third_party_examples"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            
            // Toggle
            HStack {
                Text(isThirdPartyVPNDetectionEnabled ? localizationManager.localized("vpn_enabled") : localizationManager.localized("vpn_disabled"))
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            VStack {
                Text(localizationManager.localized("vpn_server_selection_title"))
                    .font(.title)
                Text(localizationManager.localized("vpn_server_list_placeholder"))
                    .foregroundColor(.secondary)
                Spacer()
            }
            .navigationTitle(localizationManager.localized("vpn_servers"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("vpn_done")) {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct VPNSettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = VPNViewModel.shared
    @AppStorage("vpn_auto_select_server") private var autoSelectServer = true
    @AppStorage("vpn_auto_connect_wifi") private var autoConnectWiFi = true
    @AppStorage("vpn_auto_connect_mobile") private var autoConnectMobile = false
    @AppStorage("vpn_kill_switch") private var killSwitch = true
    @AppStorage("vpn_dns_leak_protection") private var dnsLeakProtection = true
    
    var body: some View {
        NavigationView {
            List {
                Section(localizationManager.localized("vpn_server_section")) {
                    HStack {
                        Text(localizationManager.localized("vpn_auto_server"))
                        Spacer()
                        Toggle("", isOn: $autoSelectServer)
                    }
                }
                
                Section(localizationManager.localized("vpn_connection_section")) {
                    HStack {
                        Text(localizationManager.localized("vpn_auto_wifi"))
                        Spacer()
                        Toggle("", isOn: $autoConnectWiFi)
                    }
                    HStack {
                        Text(localizationManager.localized("vpn_auto_mobile"))
                        Spacer()
                        Toggle("", isOn: $autoConnectMobile)
                    }
                }
                
                Section(localizationManager.localized("vpn_security_section")) {
                    HStack {
                        Text(localizationManager.localized("vpn_kill_switch"))
                        Spacer()
                        Toggle("", isOn: $killSwitch)
                    }
                    HStack {
                        Text(localizationManager.localized("vpn_dns_leak"))
                        Spacer()
                        Toggle("", isOn: $dnsLeakProtection)
                    }
                }
                
                Section(localizationManager.localized("vpn_battery_saving_section")) {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(localizationManager.localized("vpn_auto_disconnect"))
                                .font(.body)
                            Text(localizationManager.localized("vpn_auto_disconnect_desc"))
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        Toggle("", isOn: $viewModel.autoDisconnectEnabled)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("vpn_settings_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("vpn_done")) {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct VPNStatisticsView: View {
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
                            Text(localizationManager.localized("vpn_threats_blocked"))
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
                            Text(localizationManager.localized("vpn_protection_time"))
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
                            Text(localizationManager.localized("vpn_uploaded_today"))
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
                            Text(localizationManager.localized("vpn_downloaded_today"))
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
            .navigationTitle(localizationManager.localized("vpn_statistics_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("vpn_done")) {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct VPNHelpView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text(localizationManager.localized("vpn_faq"))
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .padding(.horizontal)
                    
                    VStack(spacing: 15) {
                        HelpCard(
                            question: localizationManager.localized("vpn_help_antivirus_question"),
                            answer: localizationManager.localized("vpn_help_antivirus_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_ad_blocking_question"),
                            answer: localizationManager.localized("vpn_help_ad_blocking_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_anti_tracking_question"),
                            answer: localizationManager.localized("vpn_help_anti_tracking_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_encryption_question"),
                            answer: localizationManager.localized("vpn_help_encryption_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_threat_protection_question"),
                            answer: localizationManager.localized("vpn_help_threat_protection_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_incognito_question"),
                            answer: localizationManager.localized("vpn_help_incognito_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_tor_question"),
                            answer: localizationManager.localized("vpn_help_tor_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_proxy_question"),
                            answer: localizationManager.localized("vpn_help_proxy_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_kill_switch_question"),
                            answer: localizationManager.localized("vpn_help_kill_switch_answer")
                        )
                        
                        HelpCard(
                            question: localizationManager.localized("vpn_help_dns_leak_question"),
                            answer: localizationManager.localized("vpn_help_dns_leak_answer")
                        )
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .navigationTitle(localizationManager.localized("vpn_help"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(localizationManager.localized("vpn_done")) {
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
