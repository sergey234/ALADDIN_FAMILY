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
                    title: device.name,
                    subtitle: "\(device.owner) • \(device.type.name)",
                    showBackButton: true,
                    onBack: { dismiss() }
                )
                .padding(.bottom, Spacing.m)
                
                // Device Status Card
                VStack(spacing: Spacing.m) {
                    Text(device.type.icon)
                        .font(.system(size: Size.iconXLarge * 1.5))
                    
                    Text(device.name)
                        .font(.h1)
                        .foregroundColor(.textPrimary)
                    
                    HStack(spacing: Spacing.xs) {
                        Circle()
                            .fill(device.status.color)
                            .frame(width: Size.statusIndicatorLarge, height: Size.statusIndicatorLarge)
                        Text(statusText(device.status))
                            .font(.bodyBold)
                            .foregroundColor(device.status.color)
                    }
                    
                    Text("Последняя активность: \(device.lastActive)")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
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
                    SecondaryButton(title: "Заблокировать устройство", icon: "🔒") {
                        print("Block device")
                    }
                    
                    SecondaryButton(title: "Удалить устройство", icon: "🗑️") {
                        print("Remove device")
                    }
                    .foregroundColor(.dangerRed)
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        }
        .navigationBarHidden(true)
    }
    
    private func statusText(_ status: FunctionStatus) -> String {
        switch status {
        case .active: return "Защищено"
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
    }
}

// MARK: - Device Info View

struct DeviceInfoView: View {
    let device: Device
    
    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.m) {
            InfoRow(label: "Владелец", value: device.owner)
            InfoRow(label: "Тип", value: device.type.name)
            InfoRow(label: "Модель", value: device.name)
            InfoRow(label: "Система", value: "iOS 17.1")
            InfoRow(label: "IP адрес", value: "192.168.1.147")
            InfoRow(label: "MAC адрес", value: "AA:BB:CC:DD:EE:FF")
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

struct InfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(.body)
                .foregroundColor(.textSecondary)
            Spacer()
            Text(value)
                .font(.bodyBold)
                .foregroundColor(.textPrimary)
        }
        .padding(Spacing.m)
        .background(
            LinearGradient.cardGradient.appGlassmorphism()
        )
        .cornerRadius(CornerRadius.medium)
    }
}

// MARK: - Device Stats View

struct DeviceStatsView: View {
    var body: some View {
        VStack(spacing: Spacing.m) {
            StatCard(icon: "🛡️", title: "Угрозы заблокированы", value: "47", color: .dangerRed)
            StatCard(icon: "⬇️", title: "Трафик загружено", value: "2.4 GB", color: .infoBlue)
            StatCard(icon: "⬆️", title: "Трафик отправлено", value: "1.2 GB", color: .infoBlue)
            StatCard(icon: "⏱️", title: "Время использования", value: "4:37:21", color: .successGreen)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

struct StatCard: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        HStack {
            Text(icon)
                .font(.system(size: Size.iconMedium))
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(title)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                Text(value)
                    .font(.h3)
                    .foregroundColor(color)
            }
            Spacer()
        }
        .padding(Spacing.m)
        .background(LinearGradient.cardGradient.appGlassmorphism())
        .cornerRadius(CornerRadius.medium)
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
            VStack(alignment: .leading, spacing: Spacing.xxs) {
                Text(name)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                Text(time)
                    .font(.captionSmall)
                    .foregroundColor(.textTertiary)
            }
            Spacer()
        }
        .padding(Spacing.m)
        .background(LinearGradient.cardGradient.appGlassmorphism())
        .cornerRadius(CornerRadius.medium)
    }
}

// MARK: - Device Settings View

struct DeviceSettingsView: View {
    @Binding var isProtectionOn: Bool
    @Binding var isScanningEnabled: Bool
    
    var body: some View {
        VStack(spacing: Spacing.m) {
            ALADDINToggle(title: "Защита устройства", icon: "🛡️", isOn: $isProtectionOn)
            ALADDINToggle(title: "Автоматическое сканирование", icon: "🔍", isOn: $isScanningEnabled)
        }
        .padding(.horizontal, Spacing.screenPadding)
    }
}

// MARK: - Preview

struct DeviceDetailScreen_Previews: PreviewProvider {
    static var previews: some View {
        DeviceDetailScreen(device: Device(name: "iPhone 14 Pro", owner: "Сергей", type: .iphone, status: .active, lastActive: "Сейчас"))
    }
}



