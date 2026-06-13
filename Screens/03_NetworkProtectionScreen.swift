import SwiftUI
import Combine
import CoreMotion
import CoreLocation
import UniformTypeIdentifiers

// Master Logger for UI logging
private let logger = MasterLogger.shared

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
    @ObservedObject private var syncEngine = SyncEngine.shared
    private let configurationService = ComponentConfigurationService.shared
    @State private var showingSettings = false
    @State private var showPasswordGenerator = false
    @State private var showQuarantineDetails = false
    @State private var showScanHistory = false
    @State private var showAntivirusFileImporter = false
    
    // Данные для антивируса (локальное состояние)
    @State private var scanHistory: [ScanHistoryItem] = []
    @State private var quarantineActiveFiles: Int = 0
    @State private var quarantineSize: Int64 = 0
    @State private var isLoadingQuarantine = false
    
    // Настройки антивируса (локальное состояние)
    @AppStorage("antivirus_real_time_scanning") private var realTimeScanning = true
    @AppStorage("antivirus_scan_downloads") private var scanDownloads = true
    @AppStorage("antivirus_quarantine_threats") private var quarantineThreats = true
    @State private var isApplyingAntivirusQuickSettings = false
    
    // Структура для истории сканирований
    struct ScanHistoryItem: Identifiable {
        let id: String
        let startTime: Date
        let endTime: Date?
        let filesScanned: Int
        let threatsFound: Int
        let status: String
        let duration: TimeInterval?
    }
    @State private var showIncidentResponseSettings = false
    @State private var showPhishingSettings = false
    @State private var showMalwareSettings = false
    @State private var showMobileSecuritySettings = false
    @State private var showNetworkSecuritySettings = false
    @State private var showCrashDetectionAlert = false
    @State private var showCrashDetectionSettings = false
    @State private var showRoadsideAssistance = false

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
    @State private var antivirusExpanded = false
    // ✅ УДАЛЕНО: showingStatistics и showingHelp (использовались только в Quick Actions)
    
    // MARK: - Helper Views
    
    private var networkSyncState: SyncState {
        syncEngine.latestStateByDomain[.networkProtection] ?? .idle
    }

    private var networkSyncStatusTitle: String {
        networkSyncState.localizedTitle(using: localizationManager)
    }

    private var networkSyncStatusColor: Color {
        networkSyncState.statusColor
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон — Storm Mesh shield light (Batch 2, режим C)
            StormMeshBackground(variant: .shield)
            
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

                HStack {
                    Spacer()
                    Text(networkSyncStatusTitle)
                        .font(.caption2.weight(.semibold))
                        .foregroundColor(networkSyncStatusColor)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(networkSyncStatusColor.opacity(0.15))
                        .clipShape(Capsule())
                }
                .padding(.horizontal, Spacing.screenPadding)
                .padding(.top, Spacing.xs)
                
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        
                        // Battery Saving Tip
                        batterySavingTipCard
                        
                        // Security Features
                        securityFeaturesCard
                        
                        AntifakeQuickAccessCard()
                            .padding(.horizontal, Spacing.screenPadding)
                        
                        // ✅ НОВЫЕ РАЗДЕЛЫ: Компоненты безопасности (42 компонента)
                        componentsSections
                        
                        // Antivirus Section (в формате гармошки)
                        antivirusAccordion
                        
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
        .sheet(isPresented: $showScanHistory) {
            AntivirusScanHistoryModalView(
                isPresented: $showScanHistory,
                scanHistory: scanHistory.map { session in
                    AntivirusScanHistoryModalView.AntivirusScanHistoryItem(
                        id: session.id,
                        startTime: session.startTime,
                        endTime: session.endTime,
                        filesScanned: session.filesScanned,
                        threatsFound: session.threatsFound,
                        status: session.status,
                        duration: session.duration
                    )
                }
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showQuarantineDetails) {
            AntivirusQuarantineModalView(isPresented: $showQuarantineDetails)
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
        .sheet(isPresented: $showCrashDetectionSettings) {
            CrashDetectionSettingsModal(
                componentId: "crash_detection_agent",
                isPresented: $showCrashDetectionSettings
            )
            .environmentObject(localizationManager)
        }
        .sheet(isPresented: $showRoadsideAssistance) {
            RoadsideAssistanceView()
                .environmentObject(localizationManager)
        }
        // ✅ УДАЛЕНО: .sheet для showingStatistics и showingHelp (Quick Actions удалены)
        .withToast()
        .onAppear {
            if navigationManager.pendingNetworkProtectionExpandThreat {
                navigationManager.pendingNetworkProtectionExpandThreat = false
                withAnimation(.easeOut(duration: 0.2)) {
                    threatProtectionExpanded = true
                }
            }
        }
        .fileImporter(
            isPresented: $showAntivirusFileImporter,
            allowedContentTypes: [.item],
            allowsMultipleSelection: false
        ) { result in
            switch result {
            case .success(let urls):
                guard let url = urls.first else { return }
                Task {
                    await processAntivirusPickedFile(url)
                }
            case .failure(let error):
                if isLikelyDocumentPickerCancellation(error) {
                    VisualLogger.shared.log(
                        "ℹ️ Выбор файла для скана отменён пользователем",
                        level: .info,
                        category: "ANTIVIRUS.UI"
                    )
                } else {
                    VisualLogger.shared.log(
                        "⚠️ Ошибка выбора файла: \(error.localizedDescription)",
                        level: .warning,
                        category: "ANTIVIRUS.UI"
                    )
                    Task { @MainActor in
                        ToastManager.shared.showError(
                            localizationManager.localized("antivirus_scan_picker_error")
                        )
                    }
                }
            }
        }
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
                    hasSettings: true,
                    onToggle: { newValue in
                        logger.toggleChanged("Crash Detection", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleCrashDetectionSync(newValue)
                    },
                    onSettingsTap: { showCrashDetectionSettings = true }
                )
                
                if viewModel.crashDetectionUnavailableOnThisDevice {
                    HStack(alignment: .top, spacing: Spacing.xs) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.warningOrange)
                        Text(viewModel.crashDetectionUnavailableReason ?? "Crash Detection недоступен на этом устройстве.")
                            .font(.caption)
                            .foregroundColor(.warningOrange)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, Spacing.m)
                }

                #if DEBUG
                // Диагностика: не попадает в пользовательские Release-сборки
                Button(action: {
                    logger.buttonTap("Test Crash Detection", screen: "NetworkProtection")
                    Task {
                        await CrashDetectionManager.shared.simulateCrashForDiagnostics(gForce: 5.0)
                    }
                }) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.red)
                        VStack(alignment: .leading) {
                            Text(localizationManager.localized("network_protection_debug_simulate_crash"))
                                .foregroundColor(.red)
                                .font(.subheadline)
                                .fontWeight(.bold)
                            Text(localizationManager.localized("network_protection_debug_gforce_critical"))
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
                #endif
                
                SecurityFeatureRow(
                    componentId: "roadside_assistance_agent",
                    title: localizationManager.localized("component.roadside_assistance_agent.title"),
                    description: localizationManager.localized("component.roadside_assistance_agent.desc"),
                    isEnabled: $viewModel.roadsideAssistanceEnabled,
                    hasSettings: true,
                    onToggle: { newValue in
                        logger.toggleChanged("Roadside Assistance", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleRoadsideAssistanceSync(newValue)
                    },
                    onSettingsTap: { showRoadsideAssistance = true }
                )
                
                SecurityFeatureRow(
                    componentId: "emergency_response_bot",
                    title: localizationManager.localized("component.emergency_response_bot.title"),
                    description: localizationManager.localized("component.emergency_response_bot.desc"),
                    isEnabled: $viewModel.emergencyResponseEnabled,
                    hasSettings: false,
                    onToggle: { newValue in
                        logger.toggleChanged("Emergency Response", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleEmergencyResponseSync(newValue)
                    }
                )
                
                SecurityFeatureRow(
                    componentId: "emergency_event_manager",
                    title: localizationManager.localized("component.emergency_event_manager.title"),
                    description: localizationManager.localized("component.emergency_event_manager.desc"),
                    isEnabled: $viewModel.emergencyEventEnabled,
                    hasSettings: false,
                    onToggle: { newValue in
                        logger.toggleChanged("Emergency Event", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleEmergencyEventSync(newValue)
                    }
                )
            }
            
            // Раздел 2: Защита от угроз
            SettingsAccordion(
                icon: "🛡️",
                title: localizationManager.localized("component.threat_protection.title"),
                subtitle: localizationManager.localized("component.threat_protection.subtitle"),
                isExpanded: $threatProtectionExpanded
            ) {
                antifakeAccordionEntry

                // 1. Защита от фишинга
                SecurityFeatureRow(
                    componentId: "phishing_protection_agent",
                    title: localizationManager.localized("component.phishing_protection_agent.title"),
                    description: localizationManager.localized("component.phishing_protection_agent.desc"),
                    isEnabled: $viewModel.phishingProtectionEnabled,
                    hasSettings: true,
                    onToggle: { newValue in
                        logger.toggleChanged("Phishing Protection", newValue: newValue, screen: "NetworkProtection")
                        viewModel.togglePhishingProtectionSync(newValue)
                    },
                    onSettingsTap: { showPhishingSettings = true }
                )
                
                // 2. Обнаружение вредоносного ПО
                SecurityFeatureRow(
                    componentId: "malware_detection_agent",
                    title: localizationManager.localized("component.malware_detection_agent.title"),
                    description: localizationManager.localized("component.malware_detection_agent.desc"),
                    isEnabled: $viewModel.malwareDetectionEnabled,
                    hasSettings: true,
                    onToggle: { newValue in
                        logger.toggleChanged("Malware Detection", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleMalwareDetectionSync(newValue)
                    },
                    onSettingsTap: { showMalwareSettings = true }
                )
                
                // 3. Безопасность мобильных угроз
                SecurityFeatureRow(
                    componentId: "mobile_security_agent",
                    title: localizationManager.localized("component.mobile_security_agent.title"),
                    description: localizationManager.localized("component.mobile_security_agent.desc"),
                    isEnabled: $viewModel.mobileSecurityEnabled,
                    hasSettings: true,
                    onToggle: { newValue in
                        logger.toggleChanged("Mobile Security", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleMobileSecuritySync(newValue)
                    },
                    onSettingsTap: { showMobileSecuritySettings = true }
                )
                
                // 4. Безопасность сети
                SecurityFeatureRow(
                    componentId: "network_security_agent",
                    title: localizationManager.localized("component.network_security_agent.title"),
                    description: localizationManager.localized("component.network_security_agent.desc"),
                    isEnabled: $viewModel.networkSecurityEnabled,
                    hasSettings: true,
                    onToggle: { newValue in
                        logger.toggleChanged("Network Security", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleNetworkSecuritySync(newValue)
                    },
                    onSettingsTap: { showNetworkSecuritySettings = true }
                )

                // 5. IoT‑защита (умный дом)
                SecurityFeatureRow(
                    componentId: "iot_security_agent",
                    title: localizationManager.localized("component.iot_security_agent.title"),
                    description: localizationManager.localized("component.iot_security_agent.desc"),
                    isEnabled: $viewModel.iotSecurityEnabled,
                    hasSettings: true,
                    onToggle: { newValue in
                        logger.toggleChanged("IoT Security", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleIotSecuritySync(newValue)
                    },
                    onSettingsTap: {
                        navigationManager.navigateToDeviceHub(tab: .iot)
                    }
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
                    onToggle: { newValue in
                        logger.toggleChanged("Incident Response", newValue: newValue, screen: "NetworkProtection")
                        viewModel.toggleIncidentResponseSync(newValue)
                    },
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
                    onToggle: { newValue in
                        logger.toggleChanged("Password Security", newValue: newValue, screen: "NetworkProtection")
                        viewModel.togglePasswordSecuritySync(newValue)
                    },
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

            #if targetEnvironment(simulator)
            let bannerKey = "np_crash_simulator_banner_shown_v1"
            if !UserDefaults.standard.bool(forKey: bannerKey) {
                UserDefaults.standard.set(true, forKey: bannerKey)
                let text = localizationManager.localized("crash_detection_simulator_banner")
                Task { @MainActor in
                    try? await Task.sleep(nanoseconds: 600_000_000)
                    ToastManager.shared.showWarning(text)
                }
            }
            #endif
        }
    }

    /// ux-1-07 — второй вход в Antifake из аккордеона «Защита от угроз».
    private var antifakeAccordionEntry: some View {
        Button {
            HapticFeedback.selection()
            AntifakeAccessPolicy.openHubOrPaywall(using: navigationManager)
        } label: {
            HStack(spacing: Spacing.m) {
                Text("🎭")
                    .font(.title3)
                VStack(alignment: .leading, spacing: 2) {
                    Text(localizationManager.localized("protection_antifake_card_title"))
                        .font(.subheadline.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("protection_antifake_accordion_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                Spacer()
                Text(localizationManager.localized("protection_open_check_button"))
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primaryBlue)
                Image(systemName: "chevron.right")
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primaryBlue)
            }
            .padding(.vertical, Spacing.s)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("antifake_accordion_entry")
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
        .stormGlassCard(
            cornerRadius: 12,
            accentStripColor: networkProtectionManager.isConnected ? .statusProtected : .stormIndigo
        )
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
        .stormGlassCard(cornerRadius: CornerRadius.medium, accentStripColor: .warningOrange)
        .overlay(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .stroke(Color.warningOrange.opacity(0.3), lineWidth: 1)
        )
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
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .stormIndigo)
        .padding(.horizontal, Spacing.screenPadding)
    }
    
    
    // ✅ УДАЛЕНО: Quick Actions Card полностью
    
    // MARK: - Antivirus Accordion
    
    @AppStorage("antivirusEnabled") private var antivirusEnabled = true
    
    private var antivirusAccordion: some View {
        SettingsAccordion(
            icon: "🛡️",
            title: localizationManager.localized("antivirus_title"),
            subtitle: antivirusEnabled ? localizationManager.localized("network_protection_active") : localizationManager.localized("network_protection_inactive"),
            isExpanded: $antivirusExpanded
        ) {
            antivirusAccordionContent
        }
        .onAppear {
            loadQuarantineStats()
            loadAntivirusQuickSettingsFromServer()
        }
    }
    
    private var antivirusAccordionContent: some View {
        VStack(spacing: Spacing.m) {
            // Toggle для включения/выключения антивируса
            HStack {
                Text(localizationManager.localized("antivirus_settings_title"))
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Spacer()
                Toggle("", isOn: $antivirusEnabled)
                    .toggleStyle(SwitchToggleStyle(tint: .successGreen))
                    .onChange(of: antivirusEnabled) { newValue in
                        VisualLogger.shared.log(
                            "🔄 Antivirus enabled = \(newValue)",
                            level: .info,
                            category: "ANTIVIRUS.UI"
                        )
                    }
            }
            
            // Stats Grid - Статистика
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
            
            // Прогресс сканирования (если идет сканирование)
            if antivirusManager.isScanning {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(localizationManager.localized("antivirus_scan_progress"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(Int(antivirusManager.scanProgress * 100))%")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.primaryBlue)
                    }
                    ProgressView(value: antivirusManager.scanProgress)
                        .progressViewStyle(LinearProgressViewStyle(tint: .primaryBlue))
                }
                .padding(.top, Spacing.xs)
            }
            
            Divider()
                .padding(.vertical, Spacing.xs)
            
            // История сканирований
            antivirusHistorySection
            
            Divider()
                .padding(.vertical, Spacing.xs)
            
            // Статистика карантина
            antivirusQuarantineSection
            
            Divider()
                .padding(.vertical, Spacing.xs)
            
            // Быстрые настройки
            antivirusQuickSettingsSection
            
            // Scan Button - Кнопка сканирования
            Button(action: {
                VisualLogger.shared.log(
                    "▶️ Start antivirus scan tapped",
                    level: .info,
                    category: "ANTIVIRUS.UI"
                )
                showAntivirusFileImporter = true
            }) {
                HStack {
                    Image(systemName: antivirusManager.isScanning ? "stop.circle.fill" : "doc.badge.plus")
                        .font(.title3)
                    Text(
                        antivirusManager.isScanning
                            ? localizationManager.localized("network_protection_scanning")
                            : localizationManager.localized("antivirus_scan_choose_file_button")
                    )
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
            .accessibilityHint(localizationManager.localized("antivirus_scan_choose_file_accessibility_hint"))

            Text(
                localizationManager.localized(
                    "antivirus_scan_legal_disclaimer",
                    AntivirusManager.maxServerScanUploadMegabytes
                )
            )
            .font(.caption2)
            .foregroundColor(.textSecondary)
            .fixedSize(horizontal: false, vertical: true)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.top, Spacing.xs)
        }
        .padding(.top, Spacing.m)
    }
    
    // MARK: - Antivirus Card (старая версия - удалить после тестирования)
    
    private var antivirusCard: some View {
        VStack(spacing: Spacing.m) {
            // Header - Заголовок "🛡️ Антивирус"
            HStack {
                Text(localizationManager.localized("antivirus_title"))
                    .font(.h3)
                    .fontWeight(.bold)
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
            
            // Stats Grid - Статистика
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
            
            // Прогресс сканирования (если идет сканирование)
            if antivirusManager.isScanning {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(localizationManager.localized("antivirus_scan_progress"))
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Spacer()
                        Text("\(Int(antivirusManager.scanProgress * 100))%")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.primaryBlue)
                    }
                    ProgressView(value: antivirusManager.scanProgress)
                        .progressViewStyle(LinearProgressViewStyle(tint: .primaryBlue))
                }
                .padding(.top, Spacing.xs)
            }
            
            Divider()
                .padding(.vertical, Spacing.xs)
            
            // История сканирований
            antivirusHistorySection
            
            Divider()
                .padding(.vertical, Spacing.xs)
            
            // Статистика карантина
            antivirusQuarantineSection
            
            Divider()
                .padding(.vertical, Spacing.xs)
            
            // Быстрые настройки
            antivirusQuickSettingsSection
            
            // Scan Button - Кнопка сканирования
            Button(action: {
                showAntivirusFileImporter = true
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
        .stormGlassCard(cornerRadius: CornerRadius.large, accentStripColor: .stormIndigo)
        .padding(.horizontal, Spacing.screenPadding)
        .onAppear {
            loadQuarantineStats()
        }
    }
    
    // MARK: - Antivirus History Section
    
    private var antivirusHistorySection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text(localizationManager.localized("antivirus_scan_history_title"))
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Spacer()
                if !scanHistory.isEmpty {
                    Button(action: {
                        showScanHistory = true
                    }) {
                        Text(localizationManager.localized("antivirus_view_history"))
                            .font(.caption)
                            .foregroundColor(.primaryBlue)
                    }
                }
            }
            
            if scanHistory.isEmpty {
                Text(localizationManager.localized("antivirus_no_scans"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            } else {
                ForEach(Array(scanHistory.prefix(3)), id: \.id) { session in
                    HStack {
                        Image(systemName: "clock.fill")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text(formatScanDate(session.startTime))
                            .font(.caption)
                            .foregroundColor(.textPrimary)
                        Spacer()
                        Text("\(session.threatsFound) \(localizationManager.localized("antivirus_threats_found_in_scan"))")
                            .font(.caption)
                            .foregroundColor(session.threatsFound > 0 ? .red : .successGreen)
                    }
                }
            }
        }
    }
    
    // MARK: - Antivirus Quarantine Section
    
    private var antivirusQuarantineSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text(localizationManager.localized("antivirus_quarantine_title"))
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Spacer()
                if quarantineActiveFiles > 0 {
                    Button(action: {
                        showQuarantineDetails = true
                    }) {
                        Text(localizationManager.localized("antivirus_view_quarantine"))
                            .font(.caption)
                            .foregroundColor(.primaryBlue)
                    }
                }
            }
            
            if quarantineActiveFiles == 0 {
                Text(localizationManager.localized("antivirus_no_quarantine"))
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
            } else {
                HStack(spacing: Spacing.m) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(quarantineActiveFiles)")
                            .font(.headline)
                            .foregroundColor(.textPrimary)
                        Text(localizationManager.localized("antivirus_active_files"))
                            .font(.caption2)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 2) {
                        Text(formatBytes(quarantineSize))
                            .font(.headline)
                            .foregroundColor(.textPrimary)
                        Text(localizationManager.localized("antivirus_quarantine_size"))
                            .font(.caption2)
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
    }
    
    // MARK: - Antivirus Quick Settings Section
    
    private var antivirusQuickSettingsSection: some View {
        VStack(alignment: .leading, spacing: Spacing.s) {
            HStack {
                Text(localizationManager.localized("antivirus_quick_settings"))
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.textPrimary)
                Spacer()
                Button(action: {
                    showMalwareSettings = true
                }) {
                    Text(localizationManager.localized("antivirus_all_settings"))
                        .font(.caption)
                        .foregroundColor(.primaryBlue)
                }
            }
            
            VStack(spacing: Spacing.xs) {
                ToggleRow(
                    title: localizationManager.localized("malware_detection.real_time_scanning"),
                    isOn: $realTimeScanning
                )
                .onChange(of: realTimeScanning) { newValue in
                    VisualLogger.shared.log(
                        "🔄 realTimeScanning = \(newValue)",
                        level: .info,
                        category: "ANTIVIRUS.UI"
                    )
                    if !isApplyingAntivirusQuickSettings {
                        syncAntivirusQuickSettingsToServer()
                    }
                }
                
                ToggleRow(
                    title: localizationManager.localized("malware_detection.scan_downloads"),
                    isOn: $scanDownloads
                )
                .onChange(of: scanDownloads) { newValue in
                    VisualLogger.shared.log(
                        "🔄 scanDownloads = \(newValue)",
                        level: .info,
                        category: "ANTIVIRUS.UI"
                    )
                    if !isApplyingAntivirusQuickSettings {
                        syncAntivirusQuickSettingsToServer()
                    }
                }
                
                ToggleRow(
                    title: localizationManager.localized("malware_detection.quarantine_threats"),
                    isOn: $quarantineThreats
                )
                .onChange(of: quarantineThreats) { newValue in
                    VisualLogger.shared.log(
                        "🔄 quarantineThreats = \(newValue)",
                        level: .info,
                        category: "ANTIVIRUS.UI"
                    )
                    if !isApplyingAntivirusQuickSettings {
                        syncAntivirusQuickSettingsToServer()
                    }
                }
            }
        }
    }
    
    // MARK: - Helper Functions
    
    private func formatScanDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        formatter.locale = Locale(identifier: localizationManager.currentLanguage == .russian ? "ru_RU" : "en_US")
        return formatter.string(from: date)
    }
    
    private func formatBytes(_ bytes: Int64) -> String {
        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useKB, .useMB, .useGB]
        formatter.countStyle = .file
        return formatter.string(fromByteCount: bytes)
    }
    
    // MARK: - Antivirus Helper Functions
    
    private func formatScanCount() -> String {
        // Форматируем количество проверенных файлов
        if let lastResult = antivirusManager.lastScanResult {
            // В реальном приложении здесь будет реальное количество файлов
            // Пока используем данные из истории сканирований
            if let lastSession = scanHistory.first {
                return "\(lastSession.filesScanned)"
            }
            return "1"
        }
        // Если есть история, показываем общее количество из последнего сканирования
        if let lastSession = scanHistory.first {
            return "\(lastSession.filesScanned)"
        }
        return "0"
    }
    
    // MARK: - Quarantine Stats Loading
    
    private func loadQuarantineStats() {
        isLoadingQuarantine = true
        Task {
            let stats = QuarantineManager.shared.getQuarantineStats()
            await MainActor.run {
                quarantineActiveFiles = stats.activeFiles
                quarantineSize = stats.quarantineSize
                isLoadingQuarantine = false
            }
        }
    }

    /// Загружает quick-настройки антивируса из server component configuration.
    /// Используется guard-флаг, чтобы избежать лишней обратной синхронизации в onChange.
    private func loadAntivirusQuickSettingsFromServer() {
        Task {
            do {
                let config = try await configurationService.getConfiguration(for: "malware_detection_agent")
                let settings = config.additionalSettings ?? [:]

                let loadedRealTime = (settings["realTimeScanning"]?.value as? Bool) ?? realTimeScanning
                let loadedScanDownloads = (settings["scanDownloads"]?.value as? Bool) ?? scanDownloads
                let loadedQuarantine = (settings["quarantineThreats"]?.value as? Bool) ?? quarantineThreats

                await MainActor.run {
                    isApplyingAntivirusQuickSettings = true
                    realTimeScanning = loadedRealTime
                    scanDownloads = loadedScanDownloads
                    quarantineThreats = loadedQuarantine
                    isApplyingAntivirusQuickSettings = false
                }

                VisualLogger.shared.log(
                    "✅ Antivirus quick settings loaded from server",
                    level: .success,
                    category: "ANTIVIRUS.API"
                )
            } catch {
                VisualLogger.shared.log(
                    "⚠️ Antivirus quick settings load failed: \(error.localizedDescription)",
                    level: .warning,
                    category: "ANTIVIRUS.API"
                )
            }
        }
    }

    /// Сохраняет только quick-настройки, но с merge текущих server settings,
    /// чтобы не потерять остальные ключи конфигурации malware_detection_agent.
    private func syncAntivirusQuickSettingsToServer() {
        let currentRealTime = realTimeScanning
        let currentScanDownloads = scanDownloads
        let currentQuarantine = quarantineThreats

        syncEngine.publish(
            domain: .networkProtection,
            operation: "antivirus_quick_settings_sync_start",
            state: .syncing
        )

        Task {
            do {
                let existing = try await configurationService.getConfiguration(for: "malware_detection_agent")
                var mergedSettings = existing.additionalSettings ?? [:]
                mergedSettings["realTimeScanning"] = AnyCodable(currentRealTime)
                mergedSettings["scanDownloads"] = AnyCodable(currentScanDownloads)
                mergedSettings["quarantineThreats"] = AnyCodable(currentQuarantine)

                let mergedConfig = ComponentConfiguration(
                    isEnabled: existing.isEnabled,
                    priority: existing.priority,
                    additionalSettings: mergedSettings,
                    messengerSettings: existing.messengerSettings,
                    monitoringSettings: existing.monitoringSettings,
                    emergencySettings: existing.emergencySettings,
                    privacySettings: existing.privacySettings
                )

                try await configurationService.saveConfiguration(
                    componentId: "malware_detection_agent",
                    configuration: mergedConfig
                )

                VisualLogger.shared.log(
                    "✅ Antivirus quick settings synced to server",
                    level: .success,
                    category: "ANTIVIRUS.API"
                )
                syncEngine.publish(
                    domain: .networkProtection,
                    operation: "antivirus_quick_settings_sync_complete",
                    state: .synced
                )
            } catch {
                VisualLogger.shared.log(
                    "❌ Antivirus quick settings sync failed: \(error.localizedDescription)",
                    level: .error,
                    category: "ANTIVIRUS.API"
                )
                syncEngine.publish(
                    domain: .networkProtection,
                    operation: "antivirus_quick_settings_sync_error",
                    state: .error(error.localizedDescription)
                )
            }
        }
    }
    
    /// Отмена системного выбора файла — без ошибочного тоста.
    private func isLikelyDocumentPickerCancellation(_ error: Error) -> Bool {
        let ns = error as NSError
        if ns.domain == NSCocoaErrorDomain, ns.code == NSUserCancelledError {
            return true
        }
        if ns.domain == NSCocoaErrorDomain, ns.code == 3072 {
            return true
        }
        return false
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
    
    /// Скан выбранного пользователем файла: `AntivirusManager.performFullScan` + запись в локальную историю.
    private func processAntivirusPickedFile(_ url: URL) async {
        let visualLogger = VisualLogger.shared
        let startTime = Date()
        visualLogger.log("🛡️ Сканирование выбранного файла: \(url.lastPathComponent)", level: .info, category: "ANTIVIRUS")

        let accessed = url.startAccessingSecurityScopedResource()
        defer {
            if accessed {
                url.stopAccessingSecurityScopedResource()
            }
        }

        let declaredSize: Int64 = {
            guard let values = try? url.resourceValues(forKeys: [.fileSizeKey]),
                  let n = values.fileSize else { return 0 }
            return Int64(n)
        }()

        let scanResult = await antivirusManager.performFullScan(fileURL: url)
        let endTime = Date()
        let threatsFound = scanResult.detectedThreats.count
        let status: String
        if scanResult.threatLevel == .checkingServer {
            status = "warning"
        } else if scanResult.threatLevel == .dangerous || scanResult.threatLevel == .suspicious {
            status = threatsFound > 0 ? "completed" : "warning"
        } else {
            status = "completed"
        }

        let scanSession = ScanHistoryItem(
            id: UUID().uuidString,
            startTime: startTime,
            endTime: endTime,
            filesScanned: 1,
            threatsFound: threatsFound,
            status: status,
            duration: endTime.timeIntervalSince(startTime)
        )

        await MainActor.run {
            scanHistory.insert(scanSession, at: 0)
            if scanHistory.count > 50 {
                scanHistory.removeLast()
            }
        }

        visualLogger.log(
            "✅ Скан файла завершён: \(scanResult.threatLevel.rawValue), угроз: \(threatsFound)",
            level: .success,
            category: "ANTIVIRUS"
        )

        await MainActor.run {
            if scanResult.threatLevel == .checkingServer {
                ToastManager.shared.showWarning(
                    localizationManager.localized("antivirus_toast_server_check_unavailable")
                )
            } else if declaredSize > AntivirusManager.maxServerScanUploadBytes,
                      scanResult.threatLevel == .safe || scanResult.threatLevel == .clean {
                ToastManager.shared.showInfo(
                    localizationManager.localized(
                        "antivirus_toast_large_file_local_only",
                        AntivirusManager.maxServerScanUploadMegabytes
                    )
                )
            }
        }

        loadQuarantineStats()
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
        .stormGlassCard(cornerRadius: CornerRadius.medium)
    }
}


// ✅ УДАЛЕНО: QuickActionButton (использовался только в Quick Actions карточке)

// MARK: - Antivirus Modals

struct AntivirusScanHistoryModalView: View {
    @Binding var isPresented: Bool
    let scanHistory: [AntivirusScanHistoryItem]
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    struct AntivirusScanHistoryItem: Identifiable {
        let id: String
        let startTime: Date
        let endTime: Date?
        let filesScanned: Int
        let threatsFound: Int
        let status: String
        let duration: TimeInterval?
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .shield)
                
                if scanHistory.isEmpty {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "clock.badge.questionmark")
                            .font(.system(size: 64))
                            .foregroundColor(.textSecondary.opacity(0.5))
                        
                        Text(localizationManager.localized("antivirus_no_scans"))
                            .font(.headline)
                            .foregroundColor(.textSecondary)
                    }
                } else {
                    ScrollView {
                        LazyVStack(spacing: Spacing.m) {
                            ForEach(scanHistory, id: \.id) { session in
                                ScanHistoryRow(session: session)
                            }
                        }
                        .padding(Spacing.m)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("antivirus_scan_history_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        isPresented = false
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
    }
    
    private struct ScanHistoryRow: View {
        let session: AntivirusScanHistoryItem
        @EnvironmentObject private var localizationManager: LocalizationManager
        
        var body: some View {
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack {
                    Image(systemName: session.threatsFound > 0 ? "exclamationmark.triangle.fill" : "checkmark.circle.fill")
                        .foregroundColor(session.threatsFound > 0 ? .red : .successGreen)
                        .font(.title3)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(formatDate(session.startTime))
                            .font(.headline)
                            .foregroundColor(.textPrimary)
                        
                        if let endTime = session.endTime, let duration = session.duration {
                            Text("\(localizationManager.localized("antivirus_scan_duration")): \(formatDuration(duration))")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                    }
                    
                    Spacer()
                    
                    VStack(alignment: .trailing, spacing: 4) {
                        Text("\(session.threatsFound)")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(session.threatsFound > 0 ? .red : .successGreen)
                        
                        Text(localizationManager.localized("antivirus_threats_found_in_scan"))
                            .font(.caption2)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                HStack {
                    Label("\(session.filesScanned)", systemImage: "doc.text")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Spacer()
                    
                    Text(session.status.capitalized)
                        .font(.caption)
                        .foregroundColor(statusColor(session.status))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(
                            Capsule()
                                .fill(statusColor(session.status).opacity(0.2))
                        )
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        
        private func formatDate(_ date: Date) -> String {
            let formatter = DateFormatter()
            formatter.dateStyle = .medium
            formatter.timeStyle = .short
            formatter.locale = Locale(identifier: localizationManager.currentLanguage == .russian ? "ru_RU" : "en_US")
            return formatter.string(from: date)
        }
        
        private func formatDuration(_ duration: TimeInterval) -> String {
            let minutes = Int(duration) / 60
            let seconds = Int(duration) % 60
            return String(format: "%d:%02d", minutes, seconds)
        }
        
        private func statusColor(_ status: String) -> Color {
            switch status {
            case "completed":
                return .successGreen
            case "failed":
                return .red
            case "cancelled":
                return .textSecondary
            default:
                return .textSecondary
            }
        }
    }
}

struct AntivirusQuarantineModalView: View {
    @Binding var isPresented: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    @ObservedObject private var quarantineManager = QuarantineManager.shared
    
    var body: some View {
        NavigationView {
            ZStack {
                StormMeshBackground(variant: .shield)
                
                if quarantineManager.quarantinedFiles.isEmpty {
                    VStack(spacing: Spacing.m) {
                        Image(systemName: "shield.checkered")
                            .font(.system(size: 64))
                            .foregroundColor(.textSecondary.opacity(0.5))
                        
                        Text(localizationManager.localized("antivirus_no_quarantine"))
                            .font(.headline)
                            .foregroundColor(.textSecondary)
                    }
                } else {
                    ScrollView {
                        LazyVStack(spacing: Spacing.m) {
                            // Статистика карантина
                            QuarantineStatsCard()
                            
                            // Список файлов в карантине
                            ForEach(quarantineManager.quarantinedFiles.filter { $0.status == "quarantined" }, id: \.id) { file in
                                QuarantineFileRow(file: file)
                            }
                        }
                        .padding(Spacing.m)
                    }
                }
            }
            .navigationTitle(localizationManager.localized("antivirus_quarantine_title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        isPresented = false
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.textSecondary)
                    }
                }
            }
        }
    }
    
    private struct QuarantineStatsCard: View {
        @ObservedObject private var quarantineManager = QuarantineManager.shared
        @EnvironmentObject private var localizationManager: LocalizationManager
        
        var body: some View {
            let stats = quarantineManager.getQuarantineStats()
            
            VStack(spacing: Spacing.m) {
                HStack {
                    Text(localizationManager.localized("antivirus_quarantine_title"))
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    Spacer()
                }
                
                HStack(spacing: Spacing.l) {
                    StatItem(
                        value: "\(stats.activeFiles)",
                        label: localizationManager.localized("antivirus_active_files")
                    )
                    
                    StatItem(
                        value: "\(stats.restoredFiles)",
                        label: localizationManager.localized("antivirus_restored_files")
                    )
                    
                    StatItem(
                        value: "\(stats.removedFiles)",
                        label: localizationManager.localized("antivirus_removed_files")
                    )
                }
                
                HStack {
                    Text(localizationManager.localized("antivirus_quarantine_size"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    Spacer()
                    Text(formatBytes(stats.quarantineSize))
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        
        private struct StatItem: View {
            let value: String
            let label: String
            
            var body: some View {
                VStack(spacing: 4) {
                    Text(value)
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(.textPrimary)
                    Text(label)
                        .font(.caption2)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity)
            }
        }
        
        private func formatBytes(_ bytes: Int64) -> String {
            let formatter = ByteCountFormatter()
            formatter.allowedUnits = [.useKB, .useMB, .useGB]
            formatter.countStyle = .file
            return formatter.string(fromByteCount: bytes)
        }
    }
    
    private struct QuarantineFileRow: View {
        let file: QuarantineManager.QuarantinedFile
        @EnvironmentObject private var localizationManager: LocalizationManager
        
        var body: some View {
            VStack(alignment: .leading, spacing: Spacing.s) {
                HStack {
                    Image(systemName: threatIcon(file.severity))
                        .foregroundColor(threatColor(file.severity))
                        .font(.title3)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(file.originalName)
                            .font(.headline)
                            .foregroundColor(.textPrimary)
                            .lineLimit(1)
                        
                        Text(file.threatName)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    
                    Spacer()
                    
                    Menu {
                        Button(action: {
                            Task {
                                do {
                                    let restoreURL = URL(fileURLWithPath: file.originalPath)
                                    try await QuarantineManager.shared.restoreFile(from: file, to: restoreURL)
                                } catch {
                                    print("Ошибка восстановления: \(error)")
                                }
                            }
                        }) {
                            Label("Восстановить", systemImage: "arrow.uturn.backward")
                        }
                        
                        Button(role: .destructive, action: {
                            Task {
                                do {
                                    try await QuarantineManager.shared.permanentlyRemoveFile(file)
                                } catch {
                                    print("Ошибка удаления: \(error)")
                                }
                            }
                        }) {
                            Label("Удалить навсегда", systemImage: "trash")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                            .foregroundColor(.textSecondary)
                    }
                }
                
                HStack {
                    Label(file.threatType, systemImage: "tag")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    Spacer()
                    
                    Text(formatDate(file.quarantinedAt))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
            }
            .padding(Spacing.m)
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(Color.backgroundMedium.opacity(0.3))
            )
        }
        
        private func threatIcon(_ severity: String) -> String {
            switch severity.lowercased() {
            case "high", "critical":
                return "exclamationmark.triangle.fill"
            case "medium":
                return "exclamationmark.circle.fill"
            default:
                return "info.circle.fill"
            }
        }
        
        private func threatColor(_ severity: String) -> Color {
            switch severity.lowercased() {
            case "high", "critical":
                return .red
            case "medium":
                return .warningOrange
            default:
                return .textSecondary
            }
        }
        
        private func formatDate(_ date: Date) -> String {
            let formatter = DateFormatter()
            formatter.dateStyle = .short
            formatter.timeStyle = .short
            formatter.locale = Locale(identifier: localizationManager.currentLanguage == .russian ? "ru_RU" : "en_US")
            return formatter.string(from: date)
        }
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
                .lineLimit(1)
                .minimumScaleFactor(0.5)
                .allowsTightening(true)
            Text(label)
                .font(.system(size: 9))
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .lineLimit(2)
                .fixedSize(horizontal: false, vertical: true)
                .minimumScaleFactor(0.75)
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
    @ObservedObject private var syncEngine = SyncEngine.shared
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
        syncEngine.publish(domain: .networkProtection, operation: "settings_load_start", state: .syncing)
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
                syncEngine.publish(domain: .networkProtection, operation: "settings_load_complete", state: .synced)
            } catch {
                print("⚠️ NetworkProtectionSettingsView: Ошибка загрузки настроек с сервера: \(error)")
                syncEngine.publish(
                    domain: .networkProtection,
                    operation: "settings_load_error",
                    state: .error(error.localizedDescription)
                )
                // Используем локальные значения из @AppStorage
            }
        }
    }
    
    /// Синхронизирует настройки сетевой защиты с сервером
    private func syncNetworkProtectionSettingsToServer() {
        syncEngine.publish(domain: .networkProtection, operation: "settings_sync_start", state: .syncing)
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
                syncEngine.publish(domain: .networkProtection, operation: "settings_sync_complete", state: .synced)
            } catch {
                print("⚠️ NetworkProtectionSettingsView: Ошибка синхронизации настроек: \(error)")
                syncEngine.publish(
                    domain: .networkProtection,
                    operation: "settings_sync_error",
                    state: .error(error.localizedDescription)
                )
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
                            Text(localizationManager.localized("network_protection_stats_uploaded_value"))
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
                            Text(localizationManager.localized("network_protection_stats_downloaded_value"))
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
                            answer: localizationManager.localized(
                                "network_protection_help_antivirus_answer",
                                AntivirusManager.maxServerScanUploadMegabytes
                            )
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
