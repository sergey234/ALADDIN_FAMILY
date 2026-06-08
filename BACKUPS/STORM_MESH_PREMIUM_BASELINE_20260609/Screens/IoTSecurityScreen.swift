import SwiftUI

/// 🏡 IoT Security Screen
/// ТОЛЬКО UI, НИКАКОЙ бизнес-логики
struct IoTSecurityScreen: View {
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var iotModule = IoTSecurityModule()
    @State private var homeId: String = "home_default" // TODO: Получить из настроек
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView {
                    VStack(spacing: 20) {
                        // Карточка статуса безопасности
                        SecurityStatusCard(
                            devicesCount: iotModule.iotDevices.count,
                            threatsCount: iotModule.threatsDetected.count,
                            protectionLevel: iotModule.protectionLevel
                        )
                        
                        // Список устройств
                        DevicesListSection(
                            devices: iotModule.iotDevices,
                            onBlock: { deviceId in
                                Task {
                                    do {
                                        try await iotModule.blockDevice(deviceId)
                                    } catch {
                                        print("❌ Ошибка блокировки устройства: \(error)")
                                    }
                                }
                            }
                        )
                        
                        // Секция с угрозами
                        ThreatsSection(
                            threats: iotModule.threatsDetected,
                            onFix: { threatId in
                                Task {
                                    // TODO: Реализовать исправление угрозы
                                    print("Исправление угрозы: \(threatId)")
                                }
                            }
                        )
                        
                        // Секция с рекомендациями
                        RecommendationsSection(
                            recommendations: iotModule.recommendations
                        )
                    }
                    .padding()
                }
                .refreshable {
                    await refreshData()
                }
            }
        }
        .navigationBarHidden(true)
        .task {
            await loadData()
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        // Заголовок берём из displayName текущего экрана (уже локализованный)
        let title = navigationManager.currentScreen.displayName
        return ALADDINNavigationBar(
            title: title,
            subtitle: nil,
            showBackButton: true,
            showProfileButton: false,
            showListButton: false,
            rightButtons: [],
            onBack: {
                navigationManager.goBack()
            }
        )
    }
    
    // MARK: - Data Loading
    
    private func loadData() async {
        do {
            try await iotModule.loadStatus(homeId: homeId)
        } catch {
            print("❌ Ошибка загрузки данных IoT: \(error)")
        }
    }
    
    private func refreshData() async {
        do {
            try await iotModule.refreshStatus()
        } catch {
            print("❌ Ошибка обновления данных IoT: \(error)")
        }
    }
}

// MARK: - Security Status Card

/// Карточка статуса безопасности
struct SecurityStatusCard: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let devicesCount: Int
    let threatsCount: Int
    let protectionLevel: Int
    
    private var protectionLevelColor: Color {
        switch protectionLevel {
        case 80...100:
            return .green
        case 50..<80:
            return .orange
        default:
            return .red
        }
    }
    
    var body: some View {
        VStack(spacing: 12) {
            Text(localizationManager.localized("iot_security_status_title"))
                .font(.headline)
                .foregroundColor(.textPrimary)
            
            HStack {
                VStack {
                    Text("\(devicesCount)")
                        .font(.title)
                        .foregroundColor(.textPrimary)
                    Text(localizationManager.localized("iot_security_devices_label"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                VStack {
                    Text("\(threatsCount)")
                        .font(.title)
                        .foregroundColor(threatsCount > 0 ? .red : .green)
                    Text(localizationManager.localized("iot_security_threats_label"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                VStack {
                    Text("\(protectionLevel)%")
                        .font(.title)
                        .foregroundColor(protectionLevelColor)
                    Text(localizationManager.localized("iot_security_protection_label"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
            }
        }
        .padding()
        .background(cardBackground)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
    
    private var cardBackground: Color {
        Color(white: 1.0, opacity: 0.9)
    }
}

// MARK: - Devices List Section

/// Список IoT устройств
struct DevicesListSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let devices: [IoTDevice]
    let onBlock: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("iot_security_devices_section"))
                .font(.headline)
                .foregroundColor(.textPrimary)
            
            if devices.isEmpty {
                Text(localizationManager.localized("iot_security_devices_empty"))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .padding()
            } else {
                ForEach(devices) { device in
                    DeviceRow(
                        device: device,
                        onBlock: { onBlock(device.id) }
                    )
                }
            }
        }
        .padding()
        .background(cardBackground)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
    
    private var cardBackground: Color {
        Color(white: 1.0, opacity: 0.9)
    }
}

// MARK: - Device Row

struct DeviceRow: View {
    let device: IoTDevice
    let onBlock: () -> Void
    
    private var statusColor: Color {
        switch device.status {
        case .online, .safe:
            return .green
        case .compromised:
            return .red
        case .offline:
            return .gray
        }
    }
    
    private var statusIcon: String {
        switch device.status {
        case .online, .safe:
            return "checkmark.circle.fill"
        case .compromised:
            return "exclamationmark.triangle.fill"
        case .offline:
            return "xmark.circle.fill"
        }
    }
    
    var body: some View {
        HStack {
            // Иконка типа устройства
            Image(systemName: deviceIcon(for: device.type))
                .font(.title2)
                .foregroundColor(.blue)
                .frame(width: 40)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(device.name)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                HStack {
                    Text(device.type.rawValue.capitalized)
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    if let vendor = device.vendor {
                        Text("• \(vendor)")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
            }
            
            Spacer()
            
            // Статус
            HStack(spacing: 4) {
                Image(systemName: statusIcon)
                    .font(.caption)
                    .foregroundColor(statusColor)
                Text(device.status.rawValue.capitalized)
                    .font(.caption)
                    .foregroundColor(statusColor)
            }
            
            // Кнопка блокировки (только для скомпрометированных)
            if device.status == .compromised {
                Button(action: onBlock) {
                    Image(systemName: "hand.raised.fill")
                        .foregroundColor(.red)
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
    }
    
    private func deviceIcon(for type: IoTDeviceType) -> String {
        switch type {
        case .camera:
            return "camera.fill"
        case .speaker:
            return "speaker.wave.2.fill"
        case .sensor:
            return "sensor.tag.radiowaves.forward.fill"
        case .thermostat:
            return "thermometer"
        case .light:
            return "lightbulb.fill"
        case .door:
            return "lock.fill"
        default:
            return "appletv.fill"
        }
    }
}

// MARK: - Threats Section

/// Секция с обнаруженными угрозами
struct ThreatsSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let threats: [IoTThreat]
    let onFix: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("iot_security_threats_section"))
                .font(.headline)
                .foregroundColor(threats.isEmpty ? .green : .red)
            
            if threats.isEmpty {
                HStack {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                    Text(localizationManager.localized("iot_security_threats_empty"))
                        .foregroundColor(.green)
                }
                .padding()
            } else {
                ForEach(threats) { threat in
                    ThreatRow(
                        threat: threat,
                        onFix: { onFix(threat.id) }
                    )
                }
            }
        }
        .padding()
        .background(cardBackground)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
    
    private var cardBackground: Color {
        Color(white: 1.0, opacity: 0.9)
    }
}

// MARK: - Threat Row

struct ThreatRow: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let threat: IoTThreat
    let onFix: () -> Void
    
    private var severityColor: Color {
        switch threat.severity {
        case .low:
            return .green
        case .medium:
            return .orange
        case .high, .critical:
            return .red
        }
    }
    
    private var severityIcon: String {
        switch threat.severity {
        case .low:
            return "info.circle.fill"
        case .medium:
            return "exclamationmark.triangle.fill"
        case .high, .critical:
            return "exclamationmark.octagon.fill"
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: severityIcon)
                    .foregroundColor(severityColor)
                
                Text(threat.threatType.rawValue.replacingOccurrences(of: "_", with: " ").capitalized)
                    .font(.body)
                    .foregroundColor(.textPrimary)
                
                Spacer()
                
                Text(threat.severity.rawValue.capitalized)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(severityColor.opacity(0.2))
                    .foregroundColor(severityColor)
                    .cornerRadius(4)
            }
            
            Text(threat.description)
                .font(.caption)
                .foregroundColor(.textSecondary)
            
            if let recommendations = threat.recommendations, !recommendations.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text(localizationManager.localized("iot_security_recommendations_title"))
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.textPrimary)
                    
                    ForEach(recommendations, id: \.self) { recommendation in
                        Text("• \(recommendation)")
                            .font(.caption)
                            .foregroundColor(.textSecondary)
                    }
                }
                .padding(.top, 4)
            }
            
            Button(action: onFix) {
                HStack {
                    Image(systemName: "wrench.fill")
                    Text(localizationManager.localized("iot_security_fix_action"))
                }
                .font(.caption)
                .foregroundColor(.white)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(Color.blue)
                .cornerRadius(6)
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(8)
    }
}

// MARK: - Recommendations Section

/// Секция с рекомендациями
struct RecommendationsSection: View {
    @EnvironmentObject private var localizationManager: LocalizationManager
    let recommendations: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(localizationManager.localized("iot_security_recommendations_section"))
                .font(.headline)
                .foregroundColor(.textPrimary)
            
            if recommendations.isEmpty {
                Text(localizationManager.localized("iot_security_recommendations_empty"))
                    .font(.body)
                    .foregroundColor(.textSecondary)
                    .padding()
            } else {
                ForEach(recommendations, id: \.self) { recommendation in
                    HStack(alignment: .top, spacing: 8) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.blue)
                            .font(.caption)
                        Text(recommendation)
                            .font(.body)
                            .foregroundColor(.textPrimary)
                    }
                    .padding(.vertical, 4)
                }
            }
        }
        .padding()
        .background(cardBackground)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
    }
    
    private var cardBackground: Color {
        Color(white: 1.0, opacity: 0.9)
    }
}

