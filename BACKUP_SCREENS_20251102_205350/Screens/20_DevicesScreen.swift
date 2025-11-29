import SwiftUI

/// 📱 Devices Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран управления устройствами семьи
/// Источник дизайна: /mobile/wireframes/12_devices_screen.html
struct DevicesScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) var dismiss
    @State private var devices: [Device] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var showAddDevice: Bool = false
    @State private var selectedFilter: DeviceFilter = .all
    
    private let apiService = APIService(networkManager: NetworkManager())
    
    enum DeviceFilter: String, CaseIterable {
        case all = "Все"
        case protected = "Защищённые"
        case warning = "Предупреждения"
        case danger = "Опасность"
        case inactive = "Неактивные"
    }
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            // Фон
            LinearGradient.backgroundGradient
                .ignoresSafeArea()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Фон экрана устройств")
            
            VStack(spacing: 0) {
                // Навигационная панель
                navigationHeader
                
                // Основной контент
                ScrollView(.vertical, showsIndicators: false) {
                    VStack(spacing: Spacing.l) {
                        // Статистика устройств
                        deviceStats
                        
                        // Фильтры
                        deviceFilters
                        
                        // Список устройств
                        deviceList
                    }
                    .padding(.horizontal, Spacing.screenPadding)
                    .padding(.bottom, Spacing.xxl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Список устройств семьи")
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showAddDevice) {
            AddDeviceView()
        }
        .onAppear {
            loadDevices()
        }
        .overlay {
            if isLoading {
                ProgressView()
                    .scaleEffect(1.5)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.black.opacity(0.3))
            }
        }
        .alert("Ошибка", isPresented: .constant(errorMessage != nil)) {
            Button("ОК") {
                errorMessage = nil
            }
        } message: {
            if let error = errorMessage {
                Text(error)
            }
        }
    }
    
    // MARK: - Navigation Header
    
    private var navigationHeader: some View {
        ALADDINNavigationBar(
            title: "УСТРОЙСТВА",
            subtitle: "\(devices.count) устройств под защитой",
            showBackButton: true,
            showAddButton: true,
            showProfileButton: false,
            showListButton: false,
            onBack: { 
                dismiss() 
            },
            onAdd: { 
                showAddDevice = true 
            }
        )
        .padding(.bottom, Spacing.m)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Навигационная панель устройств")
    }
    
    // MARK: - Device Stats
    
    private var deviceStats: some View {
        VStack(spacing: Spacing.m) {
            Text("📊 СТАТИСТИКА")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            HStack {
                Spacer()
                
                VStack {
                    Text("🛡️ \(devices.filter { $0.status == .protected }.count)")
                        .font(.h1)
                        .foregroundColor(.successGreen)
                    
                    Text("Защищённые")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity)
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Защищённых устройств: \(devices.filter { $0.status == .protected }.count)")
                
                VStack {
                    Text("⚠️ \(devices.filter { $0.status == .warning }.count)")
                        .font(.h1)
                        .foregroundColor(.warningOrange)
                    
                    Text("Предупреждения")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity)
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Устройств с предупреждениями: \(devices.filter { $0.status == .warning }.count)")
                
                VStack {
                    Text("🔴 \(devices.filter { $0.status == .danger }.count)")
                        .font(.h1)
                        .foregroundColor(.dangerRed)
                    
                    Text("Опасность")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                }
                .frame(maxWidth: .infinity)
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Устройств в опасности: \(devices.filter { $0.status == .danger }.count)")
                
                Spacer()
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Device Filters
    
    private var deviceFilters: some View {
        VStack(spacing: Spacing.m) {
            Text("ФИЛЬТРЫ")
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: Spacing.s) {
                    ForEach(DeviceFilter.allCases, id: \.self) { filter in
                        Button(action: {
                            selectedFilter = filter
                        }) {
                            Text(filter.rawValue)
                                .font(.body)
                                .foregroundColor(selectedFilter == filter ? .white : .textPrimary)
                                .padding(.horizontal, Spacing.m)
                                .padding(.vertical, Spacing.s)
                                .background(
                                    RoundedRectangle(cornerRadius: CornerRadius.medium)
                                        .fill(selectedFilter == filter ? Color.primaryBlue : Color.backgroundMedium)
                                )
                        }
                        .accessibilityLabel("Фильтр: \(filter.rawValue)")
                        .accessibilityAddTraits(selectedFilter == filter ? .isSelected : [])
                    }
                }
                .padding(.horizontal, Spacing.screenPadding)
            }
            .padding(.horizontal, -Spacing.screenPadding)
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Device List
    
    private var deviceList: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text("УСТРОЙСТВА")
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                Text("\(filteredDevices.count) из \(devices.count)")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            LazyVStack(spacing: Spacing.s) {
                ForEach(filteredDevices) { device in
                    DeviceCard(device: device)
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Functions
    
    private func loadDevices() {
        isLoading = true
        errorMessage = nil
        
        apiService.getDevices { result in
            DispatchQueue.main.async {
                isLoading = false
                
                switch result {
                case .success(let deviceResponses):
                    devices = deviceResponses.map { response in
                        convertToDevice(response)
                    }
                    errorMessage = nil
                    
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    print("❌ Ошибка загрузки устройств: \(error.localizedDescription)")
                }
            }
        }
    }
    
    private func convertToDevice(_ response: DeviceResponse) -> Device {
        // Конвертируем тип устройства
        let deviceType: DeviceType
        switch response.type.lowercased() {
        case "iphone": deviceType = .iphone
        case "ipad": deviceType = .ipad
        case "mac": deviceType = .mac
        case "android": deviceType = .android
        default: deviceType = .iphone
        }
        
        // Конвертируем статус
        let deviceStatus: DeviceStatus
        switch response.status.lowercased() {
        case "protected": deviceStatus = .protected
        case "warning": deviceStatus = .warning
        case "danger": deviceStatus = .danger
        case "inactive": deviceStatus = .inactive
        default: deviceStatus = .inactive
        }
        
        return Device(
            id: UUID(uuidString: response.id) ?? UUID(),
            name: response.name,
            owner: response.owner,
            type: deviceType,
            status: deviceStatus,
            lastActive: response.lastActive
        )
    }
    
    // MARK: - Computed Properties
    
    private var filteredDevices: [Device] {
        switch selectedFilter {
        case .all:
            return devices
        case .protected:
            return devices.filter { $0.status == .protected }
        case .warning:
            return devices.filter { $0.status == .warning }
        case .danger:
            return devices.filter { $0.status == .danger }
        case .inactive:
            return devices.filter { $0.status == .inactive }
        }
    }
    
    private var cardBackground: some View {
        RoundedRectangle(cornerRadius: CornerRadius.large)
            .fill(Color.backgroundMedium.opacity(0.5))
            .overlay(
                RoundedRectangle(cornerRadius: CornerRadius.large)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
}

// MARK: - Device Card

struct DeviceCard: View {
    let device: Device
    
    var body: some View {
        HStack(spacing: Spacing.m) {
            // Иконка устройства
            deviceIcon
            
            // Информация об устройстве
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(device.name)
                    .font(.bodyBold)
                    .foregroundColor(.textPrimary)
                    .accessibilityLabel("Название устройства: \(device.name)")
                
                Text(device.owner)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .accessibilityLabel("Владелец: \(device.owner)")
                
                Text(device.lastActive)
                    .font(.caption)
                    .foregroundColor(.textSecondary)
                    .accessibilityLabel("Последняя активность: \(device.lastActive)")
            }
            
            Spacer()
            
            // Статус
            VStack(alignment: .trailing, spacing: Spacing.xs) {
                statusIndicator
                
                Text(device.status.rawValue)
                    .font(.caption)
                    .foregroundColor(device.status.color)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Статус: \(device.status.rawValue)")
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Устройство \(device.name), владелец \(device.owner), статус \(device.status.rawValue)")
    }
    
    private var deviceIcon: some View {
        Image(systemName: device.type.icon)
            .font(.system(size: 24))
            .foregroundColor(device.type.color)
            .frame(width: 40, height: 40)
            .background(
                Circle()
                    .fill(device.type.color.opacity(0.1))
            )
            .accessibilityLabel("Тип устройства: \(device.type.rawValue)")
    }
    
    private var statusIndicator: some View {
        Circle()
            .fill(device.status.color)
            .frame(width: 12, height: 12)
            .accessibilityLabel("Индикатор статуса: \(device.status.rawValue)")
    }
}

// MARK: - Device Model

struct Device: Identifiable {
    let id: UUID
    let name: String
    let owner: String
    let type: DeviceType
    let status: DeviceStatus
    let lastActive: String
    
    init(id: UUID = UUID(), name: String, owner: String, type: DeviceType, status: DeviceStatus, lastActive: String) {
        self.id = id
        self.name = name
        self.owner = owner
        self.type = type
        self.status = status
        self.lastActive = lastActive
    }
}

enum DeviceType: String, CaseIterable {
    case iphone = "iPhone"
    case ipad = "iPad"
    case mac = "Mac"
    case android = "Android"
    
    var icon: String {
        switch self {
        case .iphone: return "iphone"
        case .ipad: return "ipad"
        case .mac: return "laptopcomputer"
        case .android: return "phone"
        }
    }
    
    var color: Color {
        switch self {
        case .iphone: return .primaryBlue
        case .ipad: return .secondaryBlue
        case .mac: return .textPrimary
        case .android: return .successGreen
        }
    }
}

enum DeviceStatus: String, CaseIterable {
    case protected = "Защищён"
    case warning = "Предупреждение"
    case danger = "Опасность"
    case inactive = "Неактивен"
    
    var color: Color {
        switch self {
        case .protected: return .successGreen
        case .warning: return .warningOrange
        case .danger: return .dangerRed
        case .inactive: return .textSecondary
        }
    }
}

// MARK: - Placeholder Views

struct AddDeviceView: View {
    var body: some View {
        Text("Добавление устройства")
    }
}

// MARK: - Preview

struct DevicesScreen_Previews: PreviewProvider {
    static var previews: some View {
        DevicesScreen()
    }
}
