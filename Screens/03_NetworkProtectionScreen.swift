import SwiftUI
import Combine
import CoreMotion
import CoreLocation

// Master Logger for UI logging
private let logger = MasterLogger.shared

// ✅ Settings Modal - scope issue в Xcode
// Modal существует и работает, но имеет проблему с module resolution
// Временно отключен до настройки Xcode target/modules

/**
 * 🔒 Network Protection Screen
 * Полноценный экран защиты сети
 * Источник: 02_protection_screen.html (38KB)
 */

struct NetworkProtectionScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var networkProtectionManager = NetworkProtectionManager.shared
    @ObservedObject private var antivirusManager = AntivirusManager.shared
    @StateObject private var viewModel = NetworkProtectionViewModel()
    @State private var showingSettings = false
    @State private var showPasswordGenerator = false
    @State private var showIncidentResponseSettings = false
    @State private var showPhishingSettings = false
    @State private var showMalwareSettings = false
    @State private var showMobileSecuritySettings = false
    @State private var showNetworkSecuritySettings = false
    @State private var showCrashDetectionAlert = false
    @State private var showCrashDetectionSettings = false

    // Временный тестовый триггер для демонстрации модала
    @State private var testCrashDetection = false
    
    // ✅ BUILD 104: Защита от повторной загрузки статусов и отслеживания экрана
    @State private var hasLoadedStatuses = false
    @State private var hasTrackedScreenView = false
    
    // Состояния для аккордеонов
    @State private var emergencyHelpExpanded = false
    @State private var threatProtectionExpanded = false
    @State private var incidentResponseExpanded = false
    @State private var passwordSecurityExpanded = false
    // ✅ УДАЛЕНО: showingStatistics и showingHelp (использовались только в Quick Actions)
    
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
                        logger.buttonTap("Back", screen: "NetworkProtection")
                        // ✅ ИСПРАВЛЕНО: Правильный возврат на главный экран
                        if navigationManager.canGoBack {
                            navigationManager.goBack(reason: "NetworkProtection.onBack")
                        } else {
                            // Если стек пуст, возвращаемся на главный экран
                            navigationManager.navigateToRoot(.main)
                        }
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
                        
                        // ✅ НОВЫЕ РАЗДЕЛЫ: Компоненты безопасности (42 компонента)
                        componentsSections
                        
                        // ✅ УДАЛЕНО: Quick Actions карточка
                        // quickActionsCard
                        
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
        // 🚨 Наблюдение за обнаружением аварии
        // Временный тестовый триггер для демонстрации
        .onChange(of: testCrashDetection) { crashDetected in
            if crashDetected {
                showCrashDetectionAlert = true
            }
        }
        .sheet(isPresented: $showingSettings) {
            NetworkProtectionSettingsView()
        }
        .sheet(isPresented: $showPasswordGenerator) {
            PasswordGeneratorModal(
                componentId: "password_security_agent",
                isPresented: $showPasswordGenerator
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showIncidentResponseSettings) {
            IncidentResponseSettingsModal(
                componentId: "incident_response_agent",
                isPresented: $showIncidentResponseSettings
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showPhishingSettings) {
            PhishingProtectionSettingsModal(
                componentId: "phishing_protection_agent",
                isPresented: $showPhishingSettings
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showMalwareSettings) {
            MalwareDetectionSettingsModal(
                componentId: "malware_detection_agent",
                isPresented: $showMalwareSettings
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showMobileSecuritySettings) {
            MobileSecuritySettingsModal(
                componentId: "mobile_security_agent",
                isPresented: $showMobileSecuritySettings
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showNetworkSecuritySettings) {
            NetworkSecuritySettingsModal(
                componentId: "network_security_agent",
                isPresented: $showNetworkSecuritySettings
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showCrashDetectionAlert) {
            CrashDetectionAlertModal(
                isPresented: $showCrashDetectionAlert
            )
            .environmentObject(localizationManager)
        }
        // ⚠️ SETTINGS MODAL: Temporarily disabled due to Xcode scope issue
        // Modal exists at Shared/Components/Modals/CrashDetectionSettingsModal.swift
        // Requires Xcode module/target configuration to resolve
        // .sheet(isPresented: $showCrashDetectionSettings) {
        //     CrashDetectionSettingsModal(
        //         componentId: "crash_detection_agent",
        //         isPresented: $showCrashDetectionSettings
        //     )
        //     .environmentObject(localizationManager)
        // }
        // ✅ УДАЛЕНО: .sheet для showingStatistics и showingHelp (Quick Actions удалены)
    }
    
    // MARK: - Components Sections (42 компонента)
    
    private var componentsSections: some View {
        VStack(spacing: Spacing.l) {
            // Раздел 1: Экстренная помощь
            SettingsAccordion(
                icon: "🚨",
                title: localizationManager.localized("component.emergency_help.title"),
                subtitle: localizationManager.localized("component.emergency_help.subtitle"),
                isExpanded: $emergencyHelpExpanded
            ) {
                SecurityFeatureRow(
                    componentId: "crash_detection_agent",
                    title: localizationManager.localized("component.crash_detection_agent.title"),
                    description: localizationManager.localized("component.crash_detection_agent.desc"),
                    isEnabled: $viewModel.crashDetectionEnabled,
                    hasSettings: false, // ⚠️ Temporarily disabled due to scope issue
                    onToggle: { newValue in
                        logger.toggleChanged("Crash Detection", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleCrashDetectionSync(newValue)
                    }
                    // onSettingsTap: { showCrashDetectionSettings = true } // ⚠️ Temporarily disabled
                )

                // 🚨 Тестовая кнопка для демонстрации Crash Detection
                Button(action: {
                    logger.buttonTap("Test Crash Detection", screen: "NetworkProtection")
                    // Используем новый метод симуляции краха
                    Task {
                        await CrashDetectionManager.shared.simulateCrashForTesting(gForce: 5.0)
                    }
                }) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.red)
                        VStack(alignment: .leading) {
                            Text("🚨 ТЕСТ: Симулировать аварию")
                                .foregroundColor(.red)
                                .font(.subheadline)
                                .fontWeight(.bold)
                            Text("G-сила: 5.0 (критическая)")
                                .foregroundColor(.red.opacity(0.7))
                                .font(.caption)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundColor(.gray)
                    }
                    .padding()
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.red.opacity(0.3), lineWidth: 1)
                    )
                }
                .padding(.horizontal)
                
                SecurityFeatureRow(
                    componentId: "roadside_assistance_agent",
                    title: localizationManager.localized("component.roadside_assistance_agent.title"),
                    description: localizationManager.localized("component.roadside_assistance_agent.desc"),
                    isEnabled: $viewModel.roadsideAssistanceEnabled,
                    hasSettings: false,
                    onToggle: { newValue in
                        logger.toggleChanged("Roadside Assistance", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleRoadsideAssistanceSync(newValue)
                    }
                )
                
                SecurityFeatureRow(
                    componentId: "emergency_response_bot",
                    title: localizationManager.localized("component.emergency_response_bot.title"),
                    description: localizationManager.localized("component.emergency_response_bot.desc"),
                    isEnabled: $viewModel.emergencyResponseEnabled,
                    hasSettings: false,
                    onToggle: { newValue in viewModel.toggleEmergencyResponseSync(newValue) }
                )
                
                SecurityFeatureRow(
                    componentId: "emergency_event_manager",
                    title: localizationManager.localized("component.emergency_event_manager.title"),
                    description: localizationManager.localized("component.emergency_event_manager.desc"),
                    isEnabled: $viewModel.emergencyEventEnabled,
                    hasSettings: false,
                    onToggle: { newValue in viewModel.toggleEmergencyEventSync(newValue) }
                )
            }
            
            // Раздел 2: Защита от угроз
            SettingsAccordion(
                icon: "🛡️",
                title: localizationManager.localized("component.threat_protection.title"),
                subtitle: localizationManager.localized("component.threat_protection.subtitle"),
                isExpanded: $threatProtectionExpanded
            ) {
                SecurityFeatureRow(
                    componentId: "phishing_protection_agent",
                    title: localizationManager.localized("component.phishing_protection_agent.title"),
                    description: localizationManager.localized("component.phishing_protection_agent.desc"),
                    isEnabled: $viewModel.phishingProtectionEnabled,
                    hasSettings: true,
                    onToggle: { newValue in viewModel.togglePhishingProtectionSync(newValue) },
                    onSettingsTap: { showPhishingSettings = true }
                )
                
                SecurityFeatureRow(
                    componentId: "malware_detection_agent",
                    title: localizationManager.localized("component.malware_detection_agent.title"),
                    description: localizationManager.localized("component.malware_detection_agent.desc"),
                    isEnabled: $viewModel.malwareDetectionEnabled,
                    hasSettings: true,
                    onToggle: { newValue in viewModel.toggleMalwareDetectionSync(newValue) },
                    onSettingsTap: { showMalwareSettings = true }
                )
                
                SecurityFeatureRow(
                    componentId: "mobile_security_agent",
                    title: localizationManager.localized("component.mobile_security_agent.title"),
                    description: localizationManager.localized("component.mobile_security_agent.desc"),
                    isEnabled: $viewModel.mobileSecurityEnabled,
                    hasSettings: true,
                    onToggle: { newValue in viewModel.toggleMobileSecuritySync(newValue) },
                    onSettingsTap: { showMobileSecuritySettings = true }
                )
                
                SecurityFeatureRow(
                    componentId: "network_security_agent",
                    title: localizationManager.localized("component.network_security_agent.title"),
                    description: localizationManager.localized("component.network_security_agent.desc"),
                    isEnabled: $viewModel.networkSecurityEnabled,
                    hasSettings: true,
                    onToggle: { newValue in viewModel.toggleNetworkSecuritySync(newValue) },
                    onSettingsTap: { showNetworkSecuritySettings = true }
                )
            }
            
            // Раздел 3: Автоматическая система защиты
            SettingsAccordion(
                icon: "🚨",
                title: localizationManager.localized("component.incident_response.title"),
                subtitle: localizationManager.localized("component.incident_response.subtitle"),
                isExpanded: $incidentResponseExpanded
            ) {
                SecurityFeatureRow(
                    componentId: "incident_response_agent",
                    title: localizationManager.localized("component.incident_response_agent.title"),
                    description: localizationManager.localized("component.incident_response_agent.desc"),
                    isEnabled: $viewModel.incidentResponseEnabled,
                    hasSettings: true,
                    onToggle: { newValue in viewModel.toggleIncidentResponseSync(newValue) },
                    onSettingsTap: { showIncidentResponseSettings = true }
                )
            }
            
            // Раздел 4: Безопасность паролей
            SettingsAccordion(
                icon: "🔐",
                title: localizationManager.localized("component.password_security.title"),
                subtitle: localizationManager.localized("component.password_security.subtitle"),
                isExpanded: $passwordSecurityExpanded
            ) {
                SecurityFeatureRow(
                    componentId: "password_security_agent",
                    title: localizationManager.localized("component.password_security_agent.title"),
                    description: localizationManager.localized("component.password_security_agent.desc"),
                    isEnabled: $viewModel.passwordSecurityEnabled,
                    hasSettings: true,
                    onToggle: { newValue in viewModel.togglePasswordSecuritySync(newValue) },
                    onSettingsTap: { showPasswordGenerator = true }
                )
            }
        }
        .padding(.vertical, Spacing.m)
        .onAppear {
            // ✅ BUILD 104: Загружаем статусы только один раз
            if !hasLoadedStatuses {
                hasLoadedStatuses = true
                Task {
                    await viewModel.loadComponentStatuses()
                }
            }
            
            // ✅ BUILD 104: Отследить просмотр экрана с компонентами (с защитой от повторного вызова)
            if !hasTrackedScreenView {
                hasTrackedScreenView = true
                ComponentAnalytics.shared.trackComponentScreenView(
                    screenName: "NetworkProtectionScreen",
                    componentCount: 10
                )
            }
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
    
    
    // ✅ УДАЛЕНО: Quick Actions Card полностью
    
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


// ✅ УДАЛЕНО: QuickActionButton (использовался только в Quick Actions карточке)

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
    private let apiService = APIService.shared
    private let toastManager = ToastManager.shared
    
    // ✅ Guard: чтобы initial load с сервера не триггерил автосинк обратно на сервер
    @State private var isApplyingServerSettings: Bool = false
    
    @AppStorage("network_protection_auto_select_server") private var autoSelectServer = true
    @AppStorage("network_protection_auto_connect_wifi") private var autoConnectWiFi = true
    @AppStorage("network_protection_auto_connect_mobile") private var autoConnectMobile = false
    @AppStorage("network_protection_kill_switch") private var killSwitch = true
    @AppStorage("network_protection_dns_leak_protection") private var dnsLeakProtection = true
    @AppStorage("network_protection_battery_optimization") private var batteryOptimizationEnabled = true
    @AppStorage("antivirusEnabled") private var antivirusEnabled = true
    
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
                        Toggle("", isOn: $batteryOptimizationEnabled)
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
            .onAppear {
                loadNetworkProtectionSettingsFromServer()
            }
            .onChange(of: autoSelectServer) { _ in if !isApplyingServerSettings { syncNetworkProtectionSettingsToServer() } }
            .onChange(of: autoConnectWiFi) { _ in if !isApplyingServerSettings { syncNetworkProtectionSettingsToServer() } }
            .onChange(of: autoConnectMobile) { _ in if !isApplyingServerSettings { syncNetworkProtectionSettingsToServer() } }
            .onChange(of: killSwitch) { _ in if !isApplyingServerSettings { syncNetworkProtectionSettingsToServer() } }
            .onChange(of: dnsLeakProtection) { _ in if !isApplyingServerSettings { syncNetworkProtectionSettingsToServer() } }
            .onChange(of: batteryOptimizationEnabled) { _ in if !isApplyingServerSettings { syncNetworkProtectionSettingsToServer() } }
            .onChange(of: antivirusEnabled) { _ in if !isApplyingServerSettings { syncNetworkProtectionSettingsToServer() } }
        }
    }
    
    // MARK: - Server Synchronization
    
    /// Загружает настройки сетевой защиты с сервера
    private func loadNetworkProtectionSettingsFromServer() {
        Task {
            do {
                let settings = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<NetworkProtectionSettingsResponse, Error>) in
                    apiService.getNetworkProtectionSettings { result in
                        continuation.resume(with: result)
                    }
                }
                
                await MainActor.run {
                    isApplyingServerSettings = true
                    autoSelectServer = settings.autoSelectServer
                    autoConnectWiFi = settings.autoConnectWiFi
                    autoConnectMobile = settings.autoConnectMobile
                    killSwitch = settings.killSwitch
                    dnsLeakProtection = settings.dnsLeakProtection
                    batteryOptimizationEnabled = settings.batteryOptimizationEnabled
                    antivirusEnabled = settings.antivirusEnabled
                    isApplyingServerSettings = false
                }
            } catch {
                print("⚠️ NetworkProtectionSettingsView: Ошибка загрузки настроек с сервера: \(error)")
                // Используем локальные значения из @AppStorage
            }
        }
    }
    
    /// Синхронизирует настройки сетевой защиты с сервером
    private func syncNetworkProtectionSettingsToServer() {
        Task {
            do {
                _ = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<APIResponse<Bool>, Error>) in
                    apiService.updateNetworkProtectionSettings(
                        autoSelectServer: autoSelectServer,
                        autoConnectWiFi: autoConnectWiFi,
                        autoConnectMobile: autoConnectMobile,
                        killSwitch: killSwitch,
                        dnsLeakProtection: dnsLeakProtection,
                        batteryOptimizationEnabled: batteryOptimizationEnabled,
                        antivirusEnabled: antivirusEnabled
                    ) { result in
                        continuation.resume(with: result)
                    }
                }
                
                print("✅ NetworkProtectionSettingsView: Настройки синхронизированы с сервером")
            } catch {
                print("⚠️ NetworkProtectionSettingsView: Ошибка синхронизации настроек: \(error)")
                // Не показываем ошибку пользователю - локальное сохранение работает
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
