import SwiftUI

/**
 * 📱 Device Detail Screen
 * Детали конкретного устройства
 * 15_device_detail_screen из HTML
 */

struct DeviceDetailScreen: View {
    
    @Environment(\.dismiss) var dismiss
    let device: Device
    
    @State private var isProtectionOn: Bool = true
    @State private var isScanningEnabled: Bool = true
    @State private var selectedTab: DetailTab = .info
    
    enum DetailTab: String, CaseIterable {
        case info = "Инфо"
        case stats = "Статистика"
        case threats = "Угрозы"
        case settings = "Настройки"
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: Spacing.l) {
                ALADDINNavigationBar(
                    title: "",
                    showBackButton: true,
                    showProfileButton: false,
                    showListButton: false
                )
                .padding(.bottom, Spacing.m)
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Навигационная панель деталей устройства")
                
                // Device Status Card
                VStack(spacing: Spacing.m) {
                    Text(device.type.icon)
                        .font(.system(size: Size.iconXLarge * 1.5))
                        .accessibilityLabel("\(device.type.rawValue) устройство")
                    
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
                    .accessibilityLabel("Статус: \(statusText(device.status))")
                    
                    Text("Последняя активность: \(device.lastActive)")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .accessibilityLabel("Последняя активность: \(device.lastActive)")
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
                        TabButton(title: tab.rawValue, isSelected: selectedTab == tab) {
                            selectedTab = tab
                        }
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Выбор вкладки: \(selectedTab.rawValue)")
                
                // Tab Content
                switch selectedTab {
                case .info:
                    DeviceInfoView(device: device)
                case .stats:
                    DeviceStatsView()
                case .threats:
                    DeviceThreatsView()
                case .settings:
                    DeviceSettingsView(isProtectionOn: $isProtectionOn, isScanningEnabled: $isScanningEnabled)
                }
                
                // Action Buttons
                VStack(spacing: Spacing.m) {
                    SecondaryButton(title: "Заблокировать устройство") {
                        print("Block device")
                    }
                    .accessibilityLabel("Заблокировать устройство")
                    .accessibilityHint("Нажмите для блокировки устройства")
                    
                    SecondaryButton(title: "Удалить устройство") {
                        print("Remove device")
                    }
                    .foregroundColor(.dangerRed)
                    .accessibilityLabel("Удалить устройство")
                    .accessibilityHint("Нажмите для удаления устройства из системы")
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Детали устройства \(device.name)")
        .navigationBarHidden(true)
        .safeAreaInset(edge: .top) {
            Color.clear.frame(height: Spacing.m)
        }
        .task {
            print("🚨 DeviceDetailScreen загружен!")
        }
    }
    
    private func statusText(_ status: DeviceStatus) -> String {
        switch status {
        case .protected: return "Защищено"
        case .warning: return "Требует внимания"
        case .danger: return "Опасность"
        case .inactive: return "Неактивно"
        }
    }
}

// MARK: - Tab Button

struct TabButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
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
        .accessibilityLabel("\(title) вкладка")
        .accessibilityHint(isSelected ? "Выбранная вкладка \(title)" : "Нажмите для переключения на вкладку \(title)")
    }
}

// MARK: - Device Info View

struct DeviceInfoView: View {
    let device: Device
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            InfoRow(icon: "person.fill", title: "Владелец", value: device.owner, color: .blue)
            InfoRow(icon: "app.fill", title: "Тип", value: device.type.rawValue, color: .orange)
            InfoRow(icon: "phone.fill", title: "Модель", value: device.name, color: .green)
            InfoRow(icon: "gear", title: "Система", value: "iOS 17.1", color: .purple)
            InfoRow(icon: "network", title: "IP адрес", value: "192.168.1.147", color: .blue)
            InfoRow(icon: "antenna.radiowaves.left.and.right", title: "MAC адрес", value: "AA:BB:CC:DD:EE:FF", color: .orange)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Device Stats View

struct DeviceStatsView: View {
    var body: some View {
        VStack(spacing: Spacing.m) {
            StatCard(icon: "🛡️", label: "Угрозы заблокированы", value: "47")
            StatCard(icon: "⬇️", label: "Трафик загружено", value: "2.4 GB")
            StatCard(icon: "⬆️", label: "Трафик отправлено", value: "1.2 GB")
            StatCard(icon: "⏱️", label: "Время использования", value: "4:37:21")
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Device Threats View

struct DeviceThreatsView: View {
    var body: some View {
        VStack(spacing: Spacing.m) {
            ThreatItemRow(name: "Вредоносный сайт", time: "5 мин назад", severity: .high)
            ThreatItemRow(name: "Трекер заблокирован", time: "15 мин назад", severity: .medium)
            ThreatItemRow(name: "Фишинг попытка", time: "1 час назад", severity: .high)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

struct ThreatItemRow: View {
    let name: String
    let time: String
    let severity: ThreatSeverity
    
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
                .accessibilityLabel("Уровень угрозы: \(severityText)")
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(name)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(time)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(name), время: \(time)")
            Spacer()
        }
        .padding(Spacing.m)
        .background(LinearGradient.cardGradient.appGlassmorphism())
        .cornerRadius(CornerRadius.medium)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Угроза: \(name), уровень \(severityText), время \(time)")
    }
    
    private var severityText: String {
        switch severity {
        case .low: return "низкий"
        case .medium: return "средний"
        case .high: return "высокий"
        }
    }
}

// MARK: - Device Settings View

struct DeviceSettingsView: View {
    @Binding var isProtectionOn: Bool
    @Binding var isScanningEnabled: Bool
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            ALADDINToggle("Защита устройства", isOn: $isProtectionOn)
            ALADDINToggle("Автоматическое сканирование", isOn: $isScanningEnabled)
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



