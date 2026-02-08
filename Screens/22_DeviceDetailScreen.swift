import SwiftUI

/**
 * 📱 Device Detail Screen
 * Детали конкретного устройства
 * 15_device_detail_screen из HTML
 */

struct DeviceDetailScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    let device: Device
    
    private let apiService = APIService.shared
    
    // ✅ ИСПРАВЛЕНО: Заменено @State на сохранение через UserDefaults для каждого устройства
    // Используем имя устройства как часть ключа для уникальности настроек каждого устройства
    private var protectionKey: String { "device_\(device.name)_protection_enabled" }
    private var scanningKey: String { "device_\(device.name)_scanning_enabled" }
    
    // @State переменные, которые синхронизируются с UserDefaults
    @State private var isProtectionOn: Bool = true
    @State private var isScanningEnabled: Bool = true
    @State private var selectedTab: DetailTab = .info
    @State private var isLoadingAction: Bool = false
    @State private var actionErrorMessage: String? = nil
    @State private var showBlockConfirmation: Bool = false
    @State private var showRemoveConfirmation: Bool = false
    
    enum DetailTab: String, CaseIterable {
        case info = "info"
        case stats = "stats"
        case threats = "threats"
        case settings = "settings"
        
        func localizedTitle(_ localizationManager: LocalizationManager) -> String {
            switch self {
            case .info: return localizationManager.localized("device_detail_tab_info")
            case .stats: return localizationManager.localized("device_detail_tab_stats")
            case .threats: return localizationManager.localized("device_detail_tab_threats")
            case .settings: return localizationManager.localized("device_detail_tab_settings")
            }
        }
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: Spacing.l) {
                ALADDINNavigationBar(
                    title: "",
                    showBackButton: true,
                    showProfileButton: false,
                    showListButton: false,
                    onBack: {
                        // ✅ ИСПРАВЛЕНИЕ: Используем dismiss() для SwiftUI NavigationView
                        // NavigationLink работает на уровне SwiftUI, поэтому dismiss() вернет к DevicesScreen
                        dismiss()
                    }
                )
                .padding(.bottom, Spacing.m)
                .accessibilityElement(children: .combine)
                .accessibilityLabel(localizationManager.localized("device_detail_nav_accessibility"))
                
                // Device Status Card
                VStack(spacing: Spacing.m) {
                    Text(device.type.icon)
                        .font(.system(size: Size.iconXLarge * 1.5))
                        .accessibilityLabel(String(format: localizationManager.localized("device_detail_device_type"), device.type.rawValue))
                    
                    Text(device.name)
                        .font(.h1)
                        .foregroundColor(.textPrimary)
                        .accessibilityAddTraits(.isHeader)
                    
                    HStack(spacing: Spacing.xs) {
                        Circle()
                            .fill(device.status.color)
                            .frame(width: Size.statusIndicatorLarge, height: Size.statusIndicatorLarge)
                        Text(statusText(device.status))
                            .font(.bodyBold)
                            .foregroundColor(device.status.color)
                    }
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel(String(format: localizationManager.localized("device_detail_status"), statusText(device.status)))
                    
                    Text(String(format: localizationManager.localized("device_detail_last_activity"), device.lastActive))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel(String(format: localizationManager.localized("device_detail_last_activity"), device.lastActive))
                }
                .padding(Spacing.cardPadding)
                .background(
                    LinearGradient.cardGradient
                        .appGlassmorphism()
                )
                .cornerRadius(CornerRadius.large)
                .cardShadow()
                .padding(.horizontal, Spacing.screenPadding)
                
                // Tab Selector
                HStack(spacing: Spacing.s) {
                    ForEach(DetailTab.allCases, id: \.self) { tab in
                        TabButton(title: tab.localizedTitle(localizationManager), isSelected: selectedTab == tab) {
                            selectedTab = tab
                        }
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                .accessibilityElement(children: .contain)
                .accessibilityLabel(String(format: localizationManager.localized("device_detail_tab_selector"), selectedTab.localizedTitle(localizationManager)))
                
                // Tab Content
                switch selectedTab {
                case .info:
                    DeviceInfoView(device: device)
                case .stats:
                    DeviceStatsView()
                case .threats:
                    DeviceThreatsView()
                case .settings:
                    DeviceSettingsView(
                        isProtectionOn: Binding(
                            get: { isProtectionOn },
                            set: { newValue in
                                isProtectionOn = newValue
                                saveDeviceSettings()
                            }
                        ),
                        isScanningEnabled: Binding(
                            get: { isScanningEnabled },
                            set: { newValue in
                                isScanningEnabled = newValue
                                saveDeviceSettings()
                            }
                        )
                    )
                }
                
                // Action Buttons
                VStack(spacing: Spacing.m) {
                    SecondaryButton(localizationManager.localized("device_detail_block_device")) {
                        blockDevice()
                    }
                    .accessibilityLabel(localizationManager.localized("device_detail_block_device"))
                    .accessibilityHint(localizationManager.localized("device_detail_block_device_hint"))

                    SecondaryButton(localizationManager.localized("device_detail_remove_device")) {
                        removeDevice()
                    }
                    .foregroundColor(.dangerRed)
                    .accessibilityLabel(localizationManager.localized("device_detail_remove_device"))
                    .accessibilityHint(localizationManager.localized("device_detail_remove_device_hint"))
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel(String(format: localizationManager.localized("device_detail_accessibility"), device.name))
        .navigationBarHidden(true)
        .alert(localizationManager.localized("device_detail_block_confirmation_title"), isPresented: $showBlockConfirmation) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) { }
            Button(localizationManager.localized("device_detail_block_device"), role: .destructive) {
                confirmBlockDevice()
            }
        } message: {
            Text(String(format: localizationManager.localized("device_detail_block_confirmation_message"), device.name))
        }
        .alert(localizationManager.localized("device_detail_remove_confirmation_title"), isPresented: $showRemoveConfirmation) {
            Button(localizationManager.localized("common_cancel"), role: .cancel) { }
            Button(localizationManager.localized("device_detail_remove_device"), role: .destructive) {
                confirmRemoveDevice()
            }
        } message: {
            Text(String(format: localizationManager.localized("device_detail_remove_confirmation_message"), device.name))
        }
        .alert(localizationManager.localized("common_error"), isPresented: .constant(actionErrorMessage != nil)) {
            Button(localizationManager.localized("common_ok")) {
                actionErrorMessage = nil
            }
        } message: {
            if let error = actionErrorMessage {
                Text(error)
            }
        }
        .overlay {
            if isLoadingAction {
                ProgressView()
                    .scaleEffect(1.5)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.black.opacity(0.3))
            }
        }
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 DeviceDetailScreen загружен!")
            loadDeviceSettings()
            loadDeviceSettingsFromServer()
        }
    }
    
    private func statusText(_ status: DeviceStatus) -> String {
        switch status {
        case .protected: return localizationManager.localized("device_detail_status_protected")
        case .warning: return localizationManager.localized("device_detail_status_warning")
        case .danger: return localizationManager.localized("device_detail_status_danger")
        case .inactive: return localizationManager.localized("device_detail_status_inactive")
        }
    }

    // MARK: - Device Actions

    private func blockDevice() {
        showBlockConfirmation = true
    }

    private func confirmBlockDevice() {
        isLoadingAction = true
        actionErrorMessage = nil

                apiService.blockDevice(deviceId: device.id.uuidString) { result in
            DispatchQueue.main.async {
                self.isLoadingAction = false

                switch result {
                case .success:
                    // Успешная блокировка - показать сообщение и вернуться
                    print("✅ Device blocked successfully")
                    self.dismiss()
                case .failure(let error):
                    let networkError = NetworkError.from(error)
                    self.actionErrorMessage = networkError.localizedDescription
                }
            }
        }
    }

    private func removeDevice() {
        showRemoveConfirmation = true
    }

    private func confirmRemoveDevice() {
        isLoadingAction = true
        actionErrorMessage = nil

                apiService.removeDevice(deviceId: device.id.uuidString) { result in
            DispatchQueue.main.async {
                self.isLoadingAction = false

                switch result {
                case .success:
                    // Успешное удаление - показать сообщение и вернуться
                    print("✅ Device removed successfully")
                    self.dismiss()
                case .failure(let error):
                    let networkError = NetworkError.from(error)
                    self.actionErrorMessage = networkError.localizedDescription
                }
            }
        }
    }

    // MARK: - Settings Persistence
    
    /// Загружает настройки устройства из UserDefaults
    private func loadDeviceSettings() {
        isProtectionOn = UserDefaults.standard.object(forKey: protectionKey) as? Bool ?? true
        isScanningEnabled = UserDefaults.standard.object(forKey: scanningKey) as? Bool ?? true
    }
    
    /// Сохраняет настройки устройства в UserDefaults и синхронизирует с сервером
    private func saveDeviceSettings() {
        UserDefaults.standard.set(isProtectionOn, forKey: protectionKey)
        UserDefaults.standard.set(isScanningEnabled, forKey: scanningKey)
        syncDeviceSettingsToServer()
    }
    
    // MARK: - Server Synchronization
    
    /// Загружает настройки устройства с сервера
    private func loadDeviceSettingsFromServer() {
        Task {
            do {
                let deviceId = device.id.uuidString
                
                let settings = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<DeviceSettingsResponse, Error>) in
                    apiService.getDeviceSettings(deviceId: deviceId) { result in
                        continuation.resume(with: result)
                    }
                }
                
                await MainActor.run {
                    isProtectionOn = settings.isProtectionOn
                    isScanningEnabled = settings.isScanningEnabled
                    // Сохранить в UserDefaults для локального кэширования
                    saveDeviceSettings()
                }
            } catch {
                print("⚠️ DeviceDetailScreen: Ошибка загрузки настроек устройства: \(error)")
                // Используем локальные значения из UserDefaults
            }
        }
    }
    
    /// Синхронизирует настройки устройства с сервером
    private func syncDeviceSettingsToServer() {
        Task {
            do {
                let deviceId = device.id.uuidString
                
                _ = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<APIResponse<Bool>, Error>) in
                    apiService.updateDeviceSettings(
                        deviceId: deviceId,
                        isProtectionOn: isProtectionOn,
                        isScanningEnabled: isScanningEnabled
                    ) { result in
                        continuation.resume(with: result)
                    }
                }
                
                print("✅ DeviceDetailScreen: Настройки устройства \(device.name) синхронизированы с сервером")
            } catch {
                print("⚠️ DeviceDetailScreen: Ошибка синхронизации настроек устройства: \(error)")
                // Не показываем ошибку пользователю - локальное сохранение работает
            }
        }
    }
}

// MARK: - Tab Button

struct TabButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        Button(action: {
            action()
            HapticFeedback.selection()
        }) {
            Text(title)
                .font(.captionBold)
                .foregroundColor(isSelected ? .backgroundDark : .textPrimary)
                .padding(.vertical, Spacing.s)
                .frame(maxWidth: .infinity)
                .background(isSelected ? Color.secondaryGold : Color.surfaceDark.opacity(0.6))
                .cornerRadius(CornerRadius.medium)
        }
        .accessibilityLabel(String(format: localizationManager.localized("device_detail_tab_accessibility"), title))
        .accessibilityHint(isSelected ? String(format: localizationManager.localized("device_detail_tab_selected_hint"), title) : String(format: localizationManager.localized("device_detail_tab_switch_hint"), title))
    }
}

// MARK: - Device Info View

struct DeviceInfoView: View {
    let device: Device
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            InfoRow(icon: "person.fill", title: localizationManager.localized("device_detail_info_owner"), value: device.owner, color: .blue)
            InfoRow(icon: "app.fill", title: localizationManager.localized("device_detail_info_type"), value: device.type.rawValue, color: .orange)
            InfoRow(icon: "phone.fill", title: localizationManager.localized("device_detail_info_model"), value: device.name, color: .green)
            InfoRow(icon: "gear", title: localizationManager.localized("device_detail_info_system"), value: "iOS 17.1", color: .purple)
            InfoRow(icon: "network", title: localizationManager.localized("device_detail_info_ip"), value: "192.168.1.147", color: .blue)
            InfoRow(icon: "antenna.radiowaves.left.and.right", title: localizationManager.localized("device_detail_info_mac"), value: "AA:BB:CC:DD:EE:FF", color: .orange)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Device Stats View

struct DeviceStatsView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            StatCard(icon: "🛡️", label: localizationManager.localized("device_detail_stats_threats_blocked"), value: "47")
            StatCard(icon: "⬇️", label: localizationManager.localized("device_detail_stats_traffic_downloaded"), value: "2.4 GB")
            StatCard(icon: "⬆️", label: localizationManager.localized("device_detail_stats_traffic_uploaded"), value: "1.2 GB")
            StatCard(icon: "⏱️", label: localizationManager.localized("device_detail_stats_usage_time"), value: "4:37:21")
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Device Threats View

struct DeviceThreatsView: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            // Mock данные - в реальном приложении будут приходить из API
            ThreatItemRow(name: localizationManager.localized("device_detail_threat_malicious_site"), time: localizationManager.localized("device_detail_threat_time_5_min"), severity: .high)
            ThreatItemRow(name: localizationManager.localized("device_detail_threat_tracker_blocked"), time: localizationManager.localized("device_detail_threat_time_15_min"), severity: .medium)
            ThreatItemRow(name: localizationManager.localized("device_detail_threat_phishing_attempt"), time: localizationManager.localized("device_detail_threat_time_1_hour"), severity: .high)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

struct ThreatItemRow: View {
    let name: String
    let time: String
    let severity: ThreatSeverity
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    enum ThreatSeverity {
        case low, medium, high
        var color: Color {
            switch self {
            case .low: return .successGreen
            case .medium: return .warningOrange
            case .high: return .dangerRed
            }
        }
        var icon: String {
            switch self {
            case .low: return "🟢"
            case .medium: return "⚠️"
            case .high: return "🔴"
            }
        }
    }
    
    var body: some View {
        HStack {
            Text(severity.icon)
                .accessibilityLabel(String(format: localizationManager.localized("device_detail_threat_severity"), severityText))
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(name)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(time)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(name), \(String(format: localizationManager.localized("device_detail_threat_time"), time))")
            Spacer()
        }
        .padding(Spacing.m)
        .background(LinearGradient.cardGradient.appGlassmorphism())
        .cornerRadius(CornerRadius.medium)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(String(format: localizationManager.localized("device_detail_threat_accessibility"), name, severityText, time))
    }
    
    private var severityText: String {
        switch severity {
        case .low: return localizationManager.localized("device_detail_threat_severity_low")
        case .medium: return localizationManager.localized("device_detail_threat_severity_medium")
        case .high: return localizationManager.localized("device_detail_threat_severity_high")
        }
    }
}

// MARK: - Device Settings View

struct DeviceSettingsView: View {
    @Binding var isProtectionOn: Bool
    @Binding var isScanningEnabled: Bool
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            ToggleRow(
                title: localizationManager.localized("device_detail_protection_enabled"),
                isOn: $isProtectionOn
            )
            ToggleRow(
                title: localizationManager.localized("device_detail_scanning_enabled"),
                isOn: $isScanningEnabled
            )
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}


// MARK: - Preview

struct DeviceDetailScreen_Previews: PreviewProvider {
    static var previews: some View {
        DeviceDetailScreen(device: Device(name: "iPhone 14 Pro", owner: "Сергей", type: .iphone, status: .protected, lastActive: "Сейчас"))
    }
}



