import SwiftUI

/**
 * 📱 Devices Screen
 * Экран управления устройствами семьи
 * 12_devices_screen из HTML
 */

struct DevicesScreen: View {
    
    @Environment(\.dismiss) var dismiss
    @State private var devices: [Device] = [
        Device(name: "iPhone 14 Pro", owner: "Сергей", type: .iphone, status: .protected, lastActive: "Сейчас"),
        Device(name: "MacBook Pro", owner: "Сергей", type: .mac, status: .protected, lastActive: "5 мин назад"),
        Device(name: "iPad Air", owner: "Маша", type: .ipad, status: .warning, lastActive: "10 мин назад"),
        Device(name: "iPhone 12", owner: "Мария", type: .iphone, status: .protected, lastActive: "1 час назад"),
        Device(name: "Samsung Galaxy", owner: "Бабушка", type: .android, status: .inactive, lastActive: "2 часа назад"),
        Device(name: "MacBook Air", owner: "Маша", type: .mac, status: .protected, lastActive: "3 часа назад"),
        Device(name: "iPad Mini", owner: "Петя", type: .ipad, status: .danger, lastActive: "5 часов назад"),
        Device(name: "iPhone SE", owner: "Петя", type: .iphone, status: .warning, lastActive: "1 день назад")
    ]
    @State private var showAddDevice: Bool = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: Spacing.l) {
                ALADDINNavigationBar(
                    title: "УСТРОЙСТВА",
                    subtitle: "\(devices.count) устройств под защитой",
                    showBackButton: true,
                    showAddButton: true,
                    onBack: { dismiss() },
                    onAdd: { showAddDevice = true }
                )
                .padding(.bottom, Spacing.m)
                
                // Device Stats
                VStack(spacing: Spacing.m) {
                    Text("📊 СТАТИСТИКА")
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    
                    HStack {
                        Spacer()
                        VStack {
                            Text("🛡️ \(devices.filter { $0.status == .protected }.count)")
                                .font(.h2)
                                .foregroundColor(.successGreen)
                            Text("Защищено")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        Spacer()
                        VStack {
                            Text("⚠️ \(devices.filter { $0.status == .warning || $0.status == .danger }.count)")
                                .font(.h2)
                                .foregroundColor(.warningOrange)
                            Text("Требует внимания")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        Spacer()
                        VStack {
                            Text("📱 \(devices.count)")
                                .font(.h2)
                                .foregroundColor(.infoBlue)
                            Text("Всего")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        Spacer()
                    }
                    .padding(Spacing.cardPadding)
                    .background(
                        LinearGradient.cardGradient
                            .appGlassmorphism()
                    )
                    .cornerRadius(CornerRadius.large)
                    .cardShadow()
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Devices List
                Text("СПИСОК УСТРОЙСТВ")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, Spacing.screenPadding)
                
                VStack(spacing: Spacing.m) {
                    ForEach(devices) { device in
                        DeviceRow(device: device) {
                            print("Device details: \(device.name)")
                        }
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                // Add Device Button
                Button(action: {
                    showAddDevice = true
                    HapticFeedback.lightImpact()
                }) {
                    HStack(spacing: Spacing.m) {
                        Image(systemName: "plus.circle.fill")
                            .font(.system(size: Size.iconMedium))
                            .foregroundColor(.secondaryGold)
                        VStack(alignment: .leading) {
                            Text("Добавить устройство")
                                .font(.h3)
                                .foregroundColor(.textPrimary)
                            Text("Подключите новое устройство к защите")
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundColor(.textSecondary)
                    }
                    .padding(Spacing.cardPadding)
                    .frame(maxWidth: .infinity)
                    .background(
                        LinearGradient.cardGradient
                            .appGlassmorphism()
                    )
                    .cornerRadius(CornerRadius.large)
                    .cardShadow()
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            .background(LinearGradient.backgroundGradient.ignoresSafeArea())
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showAddDevice) {
            AddDeviceView()
        }
    }
}

// MARK: - Device Model

struct Device: Identifiable {
    let id = UUID()
    let name: String
    let owner: String
    let type: DeviceType
    var status: FunctionStatus
    let lastActive: String
}

enum DeviceType {
    case iphone, ipad, mac, android, windows
    
    var icon: String {
        switch self {
        case .iphone: return "📱"
        case .ipad: return "📱"
        case .mac: return "💻"
        case .android: return "📱"
        case .windows: return "💻"
        }
    }
    
    var name: String {
        switch self {
        case .iphone: return "iPhone"
        case .ipad: return "iPad"
        case .mac: return "Mac"
        case .android: return "Android"
        case .windows: return "Windows"
        }
    }
}

// MARK: - Device Row

struct DeviceRow: View {
    let device: Device
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            action()
            HapticFeedback.lightImpact()
        }) {
            HStack(spacing: Spacing.m) {
                // Device Icon
                ZStack {
                    Circle()
                        .fill(Color.surfaceDark)
                        .frame(width: Size.avatarSize, height: Size.avatarSize)
                    Text(device.type.icon)
                        .font(.system(size: Size.iconMedium))
                    Circle()
                        .stroke(device.status.color, lineWidth: 2)
                        .frame(width: Size.avatarSize + 4, height: Size.avatarSize + 4)
                }
                
                // Device Info
                VStack(alignment: .leading, spacing: Spacing.xxs) {
                    Text(device.name)
                        .font(.h3)
                        .foregroundColor(.textPrimary)
                    HStack(spacing: Spacing.xs) {
                        Text("👤 \(device.owner)")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                        Text("•")
                            .font(.caption)
                            .foregroundColor(.textTertiary)
                        Text(device.type.name)
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                    Text("⏰ \(device.lastActive)")
                        .font(.captionSmall)
                        .foregroundColor(.textTertiary)
                }
                
                Spacer()
                
                // Status
                VStack(alignment: .trailing, spacing: Spacing.xxs) {
                    Text(device.status.icon)
                        .font(.system(size: Size.statusIndicatorLarge))
                        .shadow(color: device.status.color.opacity(0.5), radius: 5)
                    Text(statusText(device.status))
                        .font(.captionSmall)
                        .foregroundColor(device.status.color)
                }
            }
            .padding(Spacing.cardPadding)
            .frame(maxWidth: .infinity)
            .background(
                LinearGradient.cardGradient
                    .appGlassmorphism()
            )
            .cornerRadius(CornerRadius.large)
            .cardShadow()
        }
    }
    
    private func statusText(_ status: FunctionStatus) -> String {
        switch status {
        case .active: return "Защищено"
        case .warning: return "Внимание"
        case .danger: return "Опасность"
        case .inactive: return "Неактивно"
        }
    }
}

// MARK: - Add Device View

struct AddDeviceView: View {
    @Environment(\.dismiss) var dismiss
    @State private var deviceName: String = ""
    @State private var selectedOwner: String = "Выберите владельца"
    
    var body: some View {
        ZStack {
            LinearGradient.backgroundGradient.ignoresSafeArea()
            
            VStack(spacing: Spacing.l) {
                HStack {
                    Button(action: { dismiss() }) {
                        Image(systemName: "xmark")
                            .font(.bodyBold)
                            .foregroundColor(.textPrimary)
                            .frame(width: Size.navButtonSize, height: Size.navButtonSize)
                            .background(Color.surfaceDark.opacity(0.6))
                            .cornerRadius(CornerRadius.medium)
                    }
                    Spacer()
                    Text("Добавить устройство")
                        .font(.h2)
                        .foregroundColor(.secondaryGold)
                    Spacer()
                    Color.clear.frame(width: Size.navButtonSize, height: Size.navButtonSize)
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                Spacer()
                
                VStack(spacing: Spacing.xl) {
                    Text("📱")
                        .font(.system(size: Size.iconXLarge * 1.5))
                    
                    Text("Отсканируйте QR код")
                        .font(.h1)
                        .foregroundColor(.textPrimary)
                    
                    Text("На новом устройстве откройте ALADDIN и отсканируйте QR код")
                        .font(.body)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                    
                    // QR Code Placeholder
                    RoundedRectangle(cornerRadius: CornerRadius.large)
                        .fill(Color.white)
                        .frame(width: 200, height: 200)
                        .overlay(
                            Text("QR CODE")
                                .font(.h3)
                                .foregroundColor(.backgroundDark)
                        )
                    
                    PrimaryButton(title: "Добавить вручную") {
                        print("Manual add")
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
                
                Spacer()
            }
        }
    }
}

// MARK: - Preview

struct DevicesScreen_Previews: PreviewProvider {
    static var previews: some View {
        DevicesScreen()
    }
}




