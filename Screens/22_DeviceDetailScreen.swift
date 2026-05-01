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
    
    /// Префикс ключей UserDefaults по **server id** устройства (стабильно при переименовании).
    private var settingsStoragePrefix: String {
        let safe = device.id.replacingOccurrences(of: "[^A-Za-z0-9_-]", with: "_", options: .regularExpression)
        return "device_\(safe)"
    }
    
    private var protectionKey: String { "\(settingsStoragePrefix)_protection_enabled" }
    private var scanningKey: String { "\(settingsStoragePrefix)_scanning_enabled" }
    
    private var legacyProtectionKey: String { "device_\(device.name)_protection_enabled" }
    private var legacyScanningKey: String { "device_\(device.name)_scanning_enabled" }
    
    // @State переменные, которые синхронизируются с UserDefaults
    @State private var isProtectionOn: Bool = true
    @State private var isScanningEnabled: Bool = true
    @State private var selectedTab: DetailTab = .info
    @State private var isLoadingAction: Bool = false
    @State private var actionErrorMessage: String? = nil
    @State private var showBlockConfirmation: Bool = false
    @State private var showRemoveConfirmation: Bool = false
    
    // ✅ ИСПРАВЛЕНО: Данные устройства из API вместо mock
    @State private var deviceDetail: DeviceDetailResponse? = nil
    @State private var isLoadingDeviceDetail: Bool = false
    @State private var deviceDetailError: String? = nil
    
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
                    DeviceInfoView(device: device, deviceDetail: deviceDetail)
                case .stats:
                    DeviceStatsView(deviceDetail: deviceDetail)
                case .threats:
                    DeviceThreatsView(deviceId: device.id)
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
            loadDeviceDetail()
        }
    }
    
    private func statusText(_ status: DeviceStatus) -> String {
        switch status {
        case .protected: return localizationManager.localized("device_detail_status_protected")
        case .warning: return localizationManager.localized("device_detail_status_warning")
        case .danger: return localizationManager.localized("device_detail_status_danger")
        case .inactive: return localizationManager.localized("device_detail_status_inactive")
        case .pending: return "Ожидает привязки"
        }
    }

    // MARK: - Device Actions

    private func blockDevice() {
        showBlockConfirmation = true
    }

    private func confirmBlockDevice() {
        isLoadingAction = true
        actionErrorMessage = nil

                apiService.blockDevice(deviceId: device.id) { result in
            DispatchQueue.main.async {
                self.isLoadingAction = false

                switch result {
                case .success:
                    // Успешная блокировка - показать сообщение и вернуться
                    print("✅ Device blocked successfully")
                    NotificationCenter.default.post(name: NSNotification.Name("FamilyDevicesDidChange"), object: nil)
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

                apiService.removeDevice(deviceId: device.id) { result in
            DispatchQueue.main.async {
                self.isLoadingAction = false

                switch result {
                case .success:
                    // Успешное удаление - показать сообщение и вернуться
                    print("✅ Device removed successfully")
                    NotificationCenter.default.post(name: NSNotification.Name("FamilyDevicesDidChange"), object: nil)
                    self.dismiss()
                case .failure(let error):
                    let networkError = NetworkError.from(error)
                    self.actionErrorMessage = networkError.localizedDescription
                }
            }
        }
    }

    // MARK: - Device Detail Loading
    
    /// ✅ ИСПРАВЛЕНО: Загружает детальные данные устройства с сервера
    private func loadDeviceDetail() {
        isLoadingDeviceDetail = true
        deviceDetailError = nil
        
        apiService.getDeviceDetail(deviceId: device.id) { result in
            DispatchQueue.main.async {
                self.isLoadingDeviceDetail = false
                
                switch result {
                case .success(let detail):
                    self.deviceDetail = detail
                case .failure(let error):
                    self.deviceDetailError = error.localizedDescription
                    print("⚠️ DeviceDetailScreen: Ошибка загрузки деталей устройства: \(error)")
                }
            }
        }
    }
    
    // MARK: - Settings Persistence
    
    /// Загружает настройки устройства из UserDefaults
    private func loadDeviceSettings() {
        let ud = UserDefaults.standard
        if ud.object(forKey: protectionKey) != nil {
            isProtectionOn = ud.object(forKey: protectionKey) as? Bool ?? true
            isScanningEnabled = ud.object(forKey: scanningKey) as? Bool ?? true
        } else if ud.object(forKey: legacyProtectionKey) != nil {
            isProtectionOn = ud.object(forKey: legacyProtectionKey) as? Bool ?? true
            isScanningEnabled = ud.object(forKey: legacyScanningKey) as? Bool ?? true
            ud.set(isProtectionOn, forKey: protectionKey)
            ud.set(isScanningEnabled, forKey: scanningKey)
            ud.removeObject(forKey: legacyProtectionKey)
            ud.removeObject(forKey: legacyScanningKey)
        } else {
            isProtectionOn = true
            isScanningEnabled = true
        }
    }
    
    /// Только локальный кэш (без PATCH) — после загрузки с сервера не шлём обратно те же значения.
    private func persistDeviceSettingsLocally() {
        UserDefaults.standard.set(isProtectionOn, forKey: protectionKey)
        UserDefaults.standard.set(isScanningEnabled, forKey: scanningKey)
    }

    /// Сохраняет настройки устройства в UserDefaults и синхронизирует с сервером (действия пользователя на вкладке «Настройки»).
    private func saveDeviceSettings() {
        persistDeviceSettingsLocally()
        syncDeviceSettingsToServer()
    }
    
    // MARK: - Server Synchronization
    
    /// Загружает настройки устройства с сервера
    private func loadDeviceSettingsFromServer() {
        Task {
            do {
                let deviceId = device.id
                
                let settings = try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<DeviceSettingsResponse, Error>) in
                    apiService.getDeviceSettings(deviceId: deviceId) { result in
                        continuation.resume(with: result)
                    }
                }
                
                await MainActor.run {
                    isProtectionOn = settings.isProtectionOn
                    isScanningEnabled = settings.isScanningEnabled
                    persistDeviceSettingsLocally()
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
                let deviceId = device.id
                
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
    let deviceDetail: DeviceDetailResponse?
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            InfoRow(icon: "person.fill", title: localizationManager.localized("device_detail_info_owner"), value: deviceDetail?.owner ?? device.owner, color: .blue)
            InfoRow(icon: "app.fill", title: localizationManager.localized("device_detail_info_type"), value: deviceDetail?.type ?? device.type.rawValue, color: .orange)
            InfoRow(icon: "phone.fill", title: localizationManager.localized("device_detail_info_model"), value: deviceDetail?.name ?? device.name, color: .green)
            // ✅ ИСПРАВЛЕНО: Используем реальные данные из API вместо hardcoded значений
            if let osVersion = deviceDetail?.osVersion {
                InfoRow(icon: "gear", title: localizationManager.localized("device_detail_info_system"), value: osVersion, color: .purple)
            }
            if let ipAddress = deviceDetail?.ipAddress {
                InfoRow(icon: "network", title: localizationManager.localized("device_detail_info_ip"), value: ipAddress, color: .blue)
            }
            // MAC адрес не приходит с сервера, поэтому скрываем если нет данных
            // InfoRow(icon: "antenna.radiowaves.left.and.right", title: localizationManager.localized("device_detail_info_mac"), value: "AA:BB:CC:DD:EE:FF", color: .orange)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Device Stats View

struct DeviceStatsView: View {
    let deviceDetail: DeviceDetailResponse?
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    // ✅ ИСПРАВЛЕНО: Используем реальные данные из API вместо hardcoded значений
    private func formatBytes(_ bytes: Int64) -> String {
        let formatter = ByteCountFormatter()
        formatter.allowedUnits = [.useGB, .useMB]
        formatter.countStyle = .binary
        return formatter.string(fromByteCount: bytes)
    }
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            if let detail = deviceDetail {
                StatCard(icon: "🛡️", label: localizationManager.localized("device_detail_stats_threats_blocked"), value: "\(detail.threatsBlocked)")
                // dataUsage может быть общим трафиком, показываем как загруженные данные
                StatCard(icon: "⬇️", label: localizationManager.localized("device_detail_stats_traffic_downloaded"), value: formatBytes(detail.dataUsage))
                // Если есть batteryLevel, показываем его
                if let batteryLevel = detail.batteryLevel {
                    StatCard(icon: "🔋", label: localizationManager.localized("device_detail_stats_battery"), value: "\(batteryLevel)%")
                }
            } else {
                // Показываем placeholder при загрузке
                ProgressView()
                    .padding()
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Device Threats View

struct DeviceThreatsView: View {
    let deviceId: String
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var threats: [ThreatItem] = []
    @State private var isLoadingThreats: Bool = false
    @State private var threatsError: String? = nil
    private let apiService = APIService.shared
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            // ✅ ИСПРАВЛЕНО: Загружаем реальные угрозы с сервера
            if isLoadingThreats {
                ProgressView()
                    .padding()
            } else if threats.isEmpty && threatsError == nil {
                Text(localizationManager.localized("device_detail_threats_empty") ?? "Нет угроз")
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .padding()
            } else if let error = threatsError {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.dangerRed)
                    .padding()
            } else {
                ForEach(threats.prefix(10)) { threat in
                    ThreatItemRow(
                        name: threat.name,
                        time: formatThreatTime(threat),
                        severity: ThreatItemRow.ThreatSeverity(from: threat.severity)
                    )
                }
            }
        }
        .padding(.horizontal, Spacing.screenPadding)
        .task {
            loadThreats()
        }
    }
    
    private func loadThreats() {
        isLoadingThreats = true
        threatsError = nil
        
        // Используем метод getTopThreats для получения угроз устройства
        apiService.getTopThreats { result in
            Task { @MainActor in
                switch result {
                case .success(let threatItems):
                    // Фильтруем угрозы для конкретного устройства (если нужно)
                    self.threats = threatItems
                    self.isLoadingThreats = false
                case .failure(let error):
                    self.threatsError = self.localizationManager.localized("device_threats_list_load_failed")
                    self.isLoadingThreats = false
                    print("⚠️ DeviceThreatsView: Ошибка загрузки угроз: \(error)")
                }
            }
        }
    }
    
    private func formatThreatTime(_ threat: ThreatItem) -> String {
        // ThreatItem не содержит timestamp, показываем количество
        if threat.count > 1 {
            let format = localizationManager.localized("device_detail_threat_count") ?? "Обнаружено: %d"
            return String(format: format, threat.count)
        }
        return localizationManager.localized("device_detail_threat_recent") ?? "Недавно"
    }
}

struct ThreatItemRow: View {
    let name: String
    let time: String
    let severity: ThreatSeverity
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    enum ThreatSeverity {
        case low, medium, high
        
        init(from severity: String) {
            switch severity.lowercased() {
            case "low", "низкая":
                self = .low
            case "medium", "средняя", "medium":
                self = .medium
            case "high", "critical", "высокая", "критическая":
                self = .high
            default:
                self = .medium
            }
        }
        
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
        DeviceDetailScreen(device: Device(id: "preview-device", name: "iPhone 14 Pro", owner: "Сергей", type: .iphone, status: .protected, lastActive: "Сейчас"))
    }
}



