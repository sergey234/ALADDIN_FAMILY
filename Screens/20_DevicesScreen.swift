import SwiftUI
import UIKit

/// 📱 Devices Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран управления устройствами семьи
/// Источник дизайна: /mobile/wireframes/12_devices_screen.html
struct DevicesScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @State private var devices: [Device] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var showAddDevice: Bool = false
    @State private var selectedFilter: DeviceFilter = .all
    @State private var expandedFilters: Set<DeviceFilter> = []
    @State private var scheduledLoadWorkItem: DispatchWorkItem?
    
    private let apiService = APIService.shared
    
    enum DeviceFilter: String, CaseIterable {
        case all
        case protected
        case warning
        case danger
        case inactive
        
        func title(localizationManager: LocalizationManager) -> String {
            switch self {
            case .all: return localizationManager.localized("devices_filter_all")
            case .protected: return localizationManager.localized("devices_filter_protected")
            case .warning: return localizationManager.localized("devices_filter_warning")
            case .danger: return localizationManager.localized("devices_filter_danger")
            case .inactive: return localizationManager.localized("devices_filter_inactive")
            }
        }
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
                // Навигационная панель (вне оверлея — кнопка «Добавить» всегда нажимается во время загрузки)
                navigationHeader
                
                ZStack {
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
                    .accessibilityLabel(localizationManager.localized("devices_list_accessibility"))
                    
                    if isLoading {
                        ProgressView()
                            .scaleEffect(1.5)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background(Color.black.opacity(0.25))
                    }
                }
            }
        }
        .navigationBarHidden(true)
        .sheet(isPresented: $showAddDevice) {
            AddDeviceView(onDeviceAdded: {
                loadDevices()
                UserDefaults.standard.set(true, forKey: AppConfig.UserDefaultsKeys.pendingMainDashboardDevicesRefresh)
                NotificationCenter.default.post(name: NSNotification.Name("FamilyDevicesDidChange"), object: nil)
            })
            .environmentObject(localizationManager)
        }
        .refreshable {
            await loadDevicesAsync()
        }
        .onAppear {
            scheduleLoadDevices()
        }
        .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("FamilyDevicesDidChange"))) { _ in
            scheduleLoadDevices()
        }
        .alert(localizationManager.localized("common_error"), isPresented: .constant(errorMessage != nil)) {
            Button(localizationManager.localized("common_ok")) {
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
            title: localizationManager.localized("devices_title"),
            subtitle: String(format: localizationManager.localized("devices_subtitle"), devices.count),
            showBackButton: true,
            showAddButton: true,
            showProfileButton: false,
            showListButton: false,
            onBack: {
                // ✅ ИСПРАВЛЕНИЕ: Используем NavigationManager для возврата
                navigationManager.goBack(reason: "DevicesScreen back button")
            },
            onAdd: { 
                showAddDevice = true 
            }
        )
        .padding(.bottom, Spacing.m)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(localizationManager.localized("devices_nav_accessibility"))
    }
    
    // MARK: - Device Stats
    
    private var deviceStats: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("devices_statistics"))
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
                    
                    Text(localizationManager.localized("devices_protected"))
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
                    
                    Text(localizationManager.localized("devices_warnings"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.7)
                }
                .frame(maxWidth: .infinity)
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Устройств с предупреждениями: \(devices.filter { $0.status == .warning }.count)")
                
                VStack {
                    Text("🔴 \(devices.filter { $0.status == .danger }.count)")
                        .font(.h1)
                        .foregroundColor(.dangerRed)
                    
                    Text(localizationManager.localized("devices_danger"))
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
    
    // MARK: - Device Filters (Раздвигающиеся секции как в SupportScreen)
    
    private var deviceFilters: some View {
        VStack(spacing: Spacing.m) {
            Text(localizationManager.localized("devices_filters"))
                .font(.h3)
                .foregroundColor(.textPrimary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .accessibilityAddTraits(.isHeader)
            
            VStack(spacing: Spacing.s) {
                ForEach(DeviceFilter.allCases, id: \.self) { filter in
                    filterSection(filter: filter)
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    private func filterSection(filter: DeviceFilter) -> some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            // Заголовок фильтра (раздвигается)
            Button(action: {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    if expandedFilters.contains(filter) {
                        expandedFilters.remove(filter)
                    } else {
                        // Закрываем остальные фильтры (аккордеон)
                        expandedFilters.removeAll()
                        expandedFilters.insert(filter)
                    }
                }
            }) {
                HStack(spacing: Spacing.m) {
                    // Иконка фильтра
                    Text(filterIcon(filter))
                        .font(.system(size: 20))
                    
                    // Название фильтра
                    Text(filter.title(localizationManager: localizationManager))
                        .font(.body.weight(.semibold))
                        .foregroundColor(.textPrimary)
                    
                    Spacer()
                    
                    // Количество устройств
                    Text("(\(getFilteredDeviceCount(filter)))")
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                    
                    // Стрелка
                    Image(systemName: expandedFilters.contains(filter) ? "chevron.up" : "chevron.down")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundColor(.primaryBlue)
                }
                .padding(Spacing.m)
            }
            .buttonStyle(PlainButtonStyle())
            .background(
                RoundedRectangle(cornerRadius: CornerRadius.medium)
                    .fill(selectedFilter == filter ? Color.primaryBlue.opacity(0.1) : Color.backgroundMedium)
            )
            
            // Контент фильтра (раскрывается)
            if expandedFilters.contains(filter) {
                VStack(alignment: .leading, spacing: Spacing.s) {
                    Text(filterDescription(filter))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .padding(.horizontal, Spacing.m)
                    
                    // Кнопка применения фильтра
                    Button(action: {
                        withAnimation {
                            selectedFilter = filter
                            expandedFilters.remove(filter)
                        }
                        // Haptic feedback
                        let generator = UIImpactFeedbackGenerator(style: .light)
                        generator.impactOccurred()
                    }) {
                        HStack {
                            Spacer()
                            Text(localizationManager.localized("devices_apply_filter"))
                                .font(.caption.weight(.semibold))
                                .foregroundColor(.white)
                            Spacer()
                        }
                        .padding(.vertical, Spacing.s)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.small)
                                .fill(Color.primaryBlue)
                        )
                    }
                    .padding(.horizontal, Spacing.m)
                    .padding(.bottom, Spacing.s)
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.5))
        )
    }
    
    private func filterIcon(_ filter: DeviceFilter) -> String {
        switch filter {
        case .all: return "📱"
        case .protected: return "🛡️"
        case .warning: return "⚠️"
        case .danger: return "🔴"
        case .inactive: return "⏸️"
        }
    }
    
    private func filterDescription(_ filter: DeviceFilter) -> String {
        switch filter {
        case .all: return localizationManager.localized("devices_filter_all_desc")
        case .protected: return localizationManager.localized("devices_filter_protected_desc")
        case .warning: return localizationManager.localized("devices_filter_warning_desc")
        case .danger: return localizationManager.localized("devices_filter_danger_desc")
        case .inactive: return localizationManager.localized("devices_filter_inactive_desc")
        }
    }
    
    private func getFilteredDeviceCount(_ filter: DeviceFilter) -> Int {
        switch filter {
        case .all: return devices.count
        case .protected: return devices.filter { $0.status == .protected }.count
        case .warning: return devices.filter { $0.status == .warning }.count
        case .danger: return devices.filter { $0.status == .danger }.count
        case .inactive: return devices.filter { $0.status == .inactive }.count
        }
    }
    
    // MARK: - Device List
    
    private var deviceList: some View {
        VStack(spacing: Spacing.m) {
            HStack {
                Text(localizationManager.localized("devices_title"))
                    .font(.h3)
                    .foregroundColor(.textPrimary)
                    .accessibilityAddTraits(.isHeader)
                
                Spacer()
                
                Text("\(filteredDevices.count) из \(devices.count)")
                    .font(.caption)
                    .foregroundColor(.textSecondary)
            }
            
            if devices.isEmpty && !isLoading {
                VStack(spacing: Spacing.m) {
                    Text(localizationManager.localized("devices_list_empty_title"))
                        .font(.bodyBold)
                        .foregroundColor(.textPrimary)
                        .multilineTextAlignment(.center)
                    Text(localizationManager.localized("devices_list_empty_subtitle"))
                        .font(.caption)
                        .foregroundColor(.textSecondary)
                        .multilineTextAlignment(.center)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, Spacing.xl)
            } else {
                LazyVStack(spacing: Spacing.s) {
                    ForEach(filteredDevices) { device in
                        NavigationLink(destination: DeviceDetailScreen(device: device)) {
                            DeviceCard(device: device)
                        }
                        .buttonStyle(PlainButtonStyle())
                        .simultaneousGesture(
                            TapGesture().onEnded {
                                let generator = UIImpactFeedbackGenerator(style: .light)
                                generator.impactOccurred()
                            }
                        )
                    }
                }
            }
        }
        .padding(Spacing.cardPadding)
        .background(cardBackground)
        .cardShadow()
    }
    
    // MARK: - Functions
    
    private func scheduleLoadDevices() {
        scheduledLoadWorkItem?.cancel()
        let item = DispatchWorkItem {
            loadDevicesImmediate()
        }
        scheduledLoadWorkItem = item
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.45, execute: item)
    }
    
    private func loadDevices() {
        scheduleLoadDevices()
    }
    
    private func loadDevicesImmediate() {
        isLoading = true
        errorMessage = nil
        
        apiService.getDevices { result in
            DispatchQueue.main.async {
                isLoading = false
                
                switch result {
                case .success(let deviceResponses):
                    let mapped = deviceResponses.map { convertToDevice($0) }
                    var seen = Set<String>()
                    devices = mapped.filter { seen.insert($0.id).inserted }
                    errorMessage = nil
                case .failure(let error):
                    devices = []
                    errorMessage = String(
                        format: "%@ %@",
                        localizationManager.localized("devices_load_failed"),
                        error.localizedDescription
                    )
                    print("❌ Ошибка загрузки устройств: \(error.localizedDescription)")
                }
            }
        }
    }
    
    /// Pull-to-refresh: только реальные данные с сервера (без моков).
    private func loadDevicesAsync() async {
        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            apiService.getDevices { result in
                DispatchQueue.main.async {
                    switch result {
                    case .success(let deviceResponses):
                        let mapped = deviceResponses.map { convertToDevice($0) }
                        var seen = Set<String>()
                        devices = mapped.filter { seen.insert($0.id).inserted }
                        errorMessage = nil
                    case .failure(let error):
                        devices = []
                        errorMessage = String(
                            format: "%@ %@",
                            localizationManager.localized("devices_load_failed"),
                            error.localizedDescription
                        )
                        print("❌ Ошибка обновления устройств: \(error.localizedDescription)")
                    }
                    continuation.resume()
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
            id: response.id,
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
    @EnvironmentObject private var localizationManager: LocalizationManager
    
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
                
                Text(device.status.localizedName(localizationManager))
                    .font(.caption)
                    .foregroundColor(device.status.color)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Статус: \(device.status.localizedName(localizationManager))")
        }
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.backgroundMedium.opacity(0.3))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Устройство \(device.name), владелец \(device.owner), статус \(device.status.localizedName(localizationManager))")
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
            .accessibilityLabel("Индикатор статуса: \(device.status.localizedName(localizationManager))")
    }
}

// MARK: - Device Model

struct Device: Identifiable, Hashable {
    /// Идентификатор устройства на сервере (как в `GET /api/devices`); для API и UserDefaults.
    let id: String
    let name: String
    let owner: String
    let type: DeviceType
    let status: DeviceStatus
    let lastActive: String
    
    init(id: String, name: String, owner: String, type: DeviceType, status: DeviceStatus, lastActive: String) {
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
    case protected = "protected"
    case warning = "warning"
    case danger = "danger"
    case inactive = "inactive"
    case pending = "pending"
    
    var color: Color {
        switch self {
        case .protected: return .successGreen
        case .warning: return .warningOrange
        case .danger: return .dangerRed
        case .inactive: return .textSecondary
        case .pending: return .gray
        }
    }
    
    func localizedName(_ localizationManager: LocalizationManager) -> String {
        switch self {
        case .protected: return localizationManager.localized("devices_status_protected")
        case .warning: return localizationManager.localized("devices_status_warning")
        case .danger: return localizationManager.localized("devices_status_danger")
        case .inactive: return localizationManager.localized("devices_status_inactive")
        case .pending: return "Ожидает привязки"
        }
    }
}

// MARK: - Add Device View

struct AddDeviceView: View {
    
    /// Участник для привязки устройства: стабильный `id` (`MEM_*`) и имя для UI.
    private struct OwnerPick: Identifiable, Equatable, Hashable {
        let id: String
        let displayName: String
    }
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var localizationManager: LocalizationManager
    
    let onDeviceAdded: () -> Void
    
    @State private var deviceName: String = ""
    @State private var selectedDeviceType: DeviceType = .iphone
    /// Выбранный участник по идентификатору из API (`MEM_*`) или fallback-префикс `fallback_*`.
    @State private var selectedOwnerPickId: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var ownerPicks: [OwnerPick] = []
    /// Только фоновое обновление списка с сервера; форма не блокируется (сначала кэш/`Вы`).
    @State private var isLoadingFamilyMembers: Bool = false
    @State private var showPairingModal: Bool = false
    @State private var pairingQrToken: String = ""
    @State private var pairingShortPin: String = ""
    
    private let apiService = APIService.shared
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Заголовок
                        Text(localizationManager.localized("devices_add_device"))
                            .font(.h1)
                            .foregroundColor(.textPrimary)
                            .padding(.top, Spacing.l)
                        
                        // Форма
                        VStack(spacing: Spacing.m) {
                            // Название устройства (по умолчанию подставляем «Тип · Владелец» — кнопка активна без ручного ввода)
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text(localizationManager.localized("devices_device_name"))
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                
                                TextField(localizationManager.localized("devices_device_name_placeholder"), text: $deviceName)
                                    .textFieldStyle(ALADDINTextFieldStyle())
                                    .autocapitalization(.words)
                                    .frame(minHeight: 48)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: CornerRadius.medium)
                                            .stroke(Color.white.opacity(0.22), lineWidth: 1)
                                    )
                                    .accessibilityLabel(localizationManager.localized("devices_device_name"))
                                
                                Text(localizationManager.localized("devices_name_auto_hint"))
                                    .font(.caption)
                                    .foregroundColor(.textSecondary)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                            
                            // Тип устройства
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text(localizationManager.localized("devices_device_type"))
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                
                                    Picker(localizationManager.localized("devices_device_type"), selection: $selectedDeviceType) {
                                    ForEach([DeviceType.iphone, .ipad, .mac, .android], id: \.self) { type in
                                        HStack {
                                            Image(systemName: type.icon)
                                            Text(type.rawValue)
                                        }
                                        .tag(type)
                                    }
                                }
                                .pickerStyle(MenuPickerStyle())
                                .padding()
                                .background(Color.backgroundMedium.opacity(0.3))
                                .cornerRadius(CornerRadius.medium)
                                .accessibilityLabel(localizationManager.localized("devices_device_type"))
                                .onChange(of: selectedDeviceType) { _ in
                                    deviceName = makeSuggestedDeviceName()
                                }
                            }
                            
                            // Владелец
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text(localizationManager.localized("devices_owner"))
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                
                                if isLoadingFamilyMembers && ownerPicks.isEmpty {
                                    Text(localizationManager.localized("devices_loading_members"))
                                        .font(.caption)
                                        .foregroundColor(.textSecondary)
                                        .padding()
                                } else if !ownerPicks.isEmpty {
                                    Picker(localizationManager.localized("devices_owner"), selection: $selectedOwnerPickId) {
                                        ForEach(ownerPicks) { pick in
                                            Text(pick.displayName)
                                                .tag(pick.id)
                                        }
                                    }
                                    .pickerStyle(MenuPickerStyle())
                                    .padding()
                                    .background(Color.backgroundMedium.opacity(0.3))
                                    .cornerRadius(CornerRadius.medium)
                                    .accessibilityLabel(localizationManager.localized("devices_owner"))
                                    .onChange(of: selectedOwnerPickId) { _ in
                                        deviceName = makeSuggestedDeviceName()
                                    }
                                } else {
                                    Text(localizationManager.localized("devices_loading_members"))
                                        .font(.caption)
                                        .foregroundColor(.textSecondary)
                                        .padding()
                                }
                            }
                        }
                        .padding(Spacing.cardPadding)
                        .background(
                            RoundedRectangle(cornerRadius: CornerRadius.large)
                                .fill(Color.backgroundMedium.opacity(0.5))
                                .overlay(
                                    RoundedRectangle(cornerRadius: CornerRadius.large)
                                        .stroke(Color.white.opacity(0.1), lineWidth: 1)
                                )
                        )
                        .padding(.horizontal, Spacing.screenPadding)
                        
                        // Кнопка добавления
                        Button(action: {
                            // Haptic feedback
                            let generator = UIImpactFeedbackGenerator(style: .medium)
                            generator.impactOccurred()
                            addDevice()
                        }) {
                            HStack {
                                if isLoading {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                } else {
                                    Text(localizationManager.localized("devices_add_device_button"))
                                        .font(.bodyBold)
                                }
                            }
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, Spacing.m)
                            .background(
                                LinearGradient(
                                    colors: isFormValid ? [Color.primaryBlue, Color.secondaryBlue] : [Color.gray, Color.gray.opacity(0.5)],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .cornerRadius(CornerRadius.medium)
                        }
                        .disabled(!isFormValid || isLoading)
                        .padding(.horizontal, Spacing.screenPadding)
                        .accessibilityLabel(localizationManager.localized("devices_add_device_button"))
                        .accessibilityHint(isFormValid ? localizationManager.localized("devices_add_device_hint_enabled") : localizationManager.localized("devices_add_device_hint_disabled"))
                        
                        if !isFormValid, !isLoading {
                            Text(addDeviceFormValidationHint)
                                .font(.caption)
                                .foregroundColor(.textSecondary)
                                .multilineTextAlignment(.center)
                                .padding(.horizontal, Spacing.screenPadding)
                        }
                    }
                    .padding(.bottom, Spacing.xl)
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel(localizationManager.localized("devices_add_form_label"))
            }
            .navigationTitle(localizationManager.localized("devices_add_new_device"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(localizationManager.localized("common_cancel")) {
                        dismiss()
                    }
                    .foregroundColor(.textPrimary)
                }
            }
            .onAppear {
                setupAddDeviceForm()
            }
            .sheet(isPresented: $showPairingModal) {
                DevicePairingModal(
                    deviceName: effectiveDeviceName,
                    ownerName: selectedOwnerDisplayName,
                    qrToken: pairingQrToken,
                    shortPin: pairingShortPin
                )
                .environmentObject(localizationManager)
                .onDisappear {
                    onDeviceAdded()
                    dismiss()
                }
            }
            .alert(localizationManager.localized("common_error"), isPresented: .constant(errorMessage != nil)) {
                Button(localizationManager.localized("common_ok")) {
                    errorMessage = nil
                }
            } message: {
                if let error = errorMessage {
                    Text(error)
                }
            }
        }
    }
    
    // MARK: - Computed Properties
    
    /// Имя для API и проверки кнопки: введённое пользователем или автоматическое «Тип · Владелец».
    private var effectiveDeviceName: String {
        let typed = deviceName.trimmingCharacters(in: .whitespacesAndNewlines)
        if !typed.isEmpty { return typed }
        return makeSuggestedDeviceName().trimmingCharacters(in: .whitespacesAndNewlines)
    }
    
    private var selectedOwnerDisplayName: String {
        ownerPicks.first(where: { $0.id == selectedOwnerPickId })?.displayName ?? ""
    }
    
    private var isFormValid: Bool {
        !effectiveDeviceName.isEmpty &&
        !selectedOwnerPickId.isEmpty &&
        !ownerPicks.isEmpty
    }
    
    /// Почему кнопка серая (`.disabled`) — подсказка без тапа по кнопке.
    private var addDeviceFormValidationHint: String {
        if isLoadingFamilyMembers && ownerPicks.isEmpty {
            return localizationManager.localized("devices_form_hint_syncing_owners")
        }
        if ownerPicks.isEmpty {
            return localizationManager.localized("devices_form_hint_no_owners")
        }
        if effectiveDeviceName.isEmpty {
            return localizationManager.localized("devices_form_hint_enter_name")
        }
        if selectedOwnerPickId.isEmpty {
            return localizationManager.localized("devices_form_hint_select_owner")
        }
        return localizationManager.localized("devices_add_device_hint_disabled")
    }
    
    // MARK: - Functions
    
    /// Сразу заполняем владельцев из кэша (кнопка не ждёт сеть), затем подтягиваем актуальный список с API.
    private func setupAddDeviceForm() {
        applyOwnerListFromLocalFallback()
        syncSelectedOwnerWithMembersList()
        deviceName = makeSuggestedDeviceName()
        #if DEBUG
        print("AddDeviceView.setup: members=\(ownerPicks.count) owner='\(selectedOwnerDisplayName)' effectiveName='\(effectiveDeviceName)' isFormValid=\(isFormValid)")
        #endif
        fetchFamilyMembersFromServer()
    }
    
    /// Удобное имя по умолчанию: тип устройства и владелец (пользователь может отредактировать поле).
    private func makeSuggestedDeviceName() -> String {
        let owner = selectedOwnerDisplayName.trimmingCharacters(in: .whitespacesAndNewlines)
        let type = selectedDeviceType.rawValue
        if owner.isEmpty { return type }
        return "\(type) · \(owner)"
    }
    
    private func syncSelectedOwnerWithMembersList() {
        guard !ownerPicks.isEmpty else { return }
        if selectedOwnerPickId.isEmpty || !ownerPicks.contains(where: { $0.id == selectedOwnerPickId }) {
            selectedOwnerPickId = ownerPicks[0].id
        }
    }
    
    private func fetchFamilyMembersFromServer() {
        isLoadingFamilyMembers = true
        apiService.getFamilyMembers { result in
            Task { @MainActor in
                defer { isLoadingFamilyMembers = false }
                switch result {
                case .success(let members):
                    let picks: [OwnerPick] = members.compactMap { m in
                        let name = m.name.trimmingCharacters(in: .whitespacesAndNewlines)
                        let sid = m.id.trimmingCharacters(in: .whitespacesAndNewlines)
                        guard !name.isEmpty, !sid.isEmpty else { return nil }
                        return OwnerPick(id: sid, displayName: name)
                    }
                    guard !picks.isEmpty else { return }
                    ownerPicks = picks
                    syncSelectedOwnerWithMembersList()
                    deviceName = makeSuggestedDeviceName()
                case .failure:
                    break
                }
            }
        }
    }
    
    /// Если `GET /api/family/members` недоступен или пуст — тот же fallback, что раньше (кэш + текущий пользователь).
    private func applyOwnerListFromLocalFallback() {
        let familyMembersKey = "family_members_list"
        if let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            let picks = decoded.compactMap { m -> OwnerPick? in
                let name = m.name.trimmingCharacters(in: .whitespacesAndNewlines)
                guard !name.isEmpty else { return nil }
                let sid = m.canonicalId.trimmingCharacters(in: .whitespacesAndNewlines)
                let rid = sid.isEmpty ? "fallback_\(name)" : sid
                return OwnerPick(id: rid, displayName: name)
            }
            if !picks.isEmpty {
                ownerPicks = picks
                if selectedOwnerPickId.isEmpty, let first = picks.first {
                    selectedOwnerPickId = first.id
                }
                return
            }
        }
        if let currentUserName = UserDefaults.standard.string(forKey: "current_user_name"),
           !currentUserName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            let nm = currentUserName.trimmingCharacters(in: .whitespacesAndNewlines)
            ownerPicks = [OwnerPick(id: "fallback_local_user", displayName: nm)]
            selectedOwnerPickId = "fallback_local_user"
        } else {
            let you = localizationManager.localized("devices_owner_you").trimmingCharacters(in: .whitespacesAndNewlines)
            let youResolved = you.isEmpty
                ? (localizationManager.currentLanguage == .english ? "You" : "Вы")
                : you
            ownerPicks = [OwnerPick(id: "fallback_you", displayName: youResolved)]
            selectedOwnerPickId = "fallback_you"
        }
    }
    
    private func addDevice() {
        guard isFormValid else { return }
        
        isLoading = true
        errorMessage = nil
        
        // Конвертируем DeviceType в строку для API
        let deviceTypeString: String
        switch selectedDeviceType {
        case .iphone: deviceTypeString = "iphone"
        case .ipad: deviceTypeString = "ipad"
        case .mac: deviceTypeString = "mac"
        case .android: deviceTypeString = "android"
        }
        
        apiService.addDevice(
            name: effectiveDeviceName,
            type: deviceTypeString,
            owner: selectedOwnerDisplayName,
            ownerMemberId: ownerMemberIdForAPI()
        ) { result in
            DispatchQueue.main.async {
                isLoading = false
                
                switch result {
                case .success(let response):
                    if let token = response.pairingToken?.trimmingCharacters(in: .whitespacesAndNewlines), !token.isEmpty {
                        pairingQrToken = token
                        pairingShortPin = (response.shortPin ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
                        showPairingModal = true
                    } else {
                        onDeviceAdded()
                        dismiss()
                    }
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    print("❌ Ошибка добавления устройства: \(error.localizedDescription)")
                }
            }
        }
    }
    
    /// В API передаём `owner_member_id` только для реальных идентификаторов с сервера (не локальные fallback).
    private func ownerMemberIdForAPI() -> String? {
        guard let pick = ownerPicks.first(where: { $0.id == selectedOwnerPickId }) else { return nil }
        let id = pick.id
        if id.hasPrefix("fallback_") { return nil }
        return id.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : id
    }
}

// MARK: - Text Field Style

struct ALADDINTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding(Spacing.m)
            .background(Color.backgroundMedium.opacity(0.3))
            .cornerRadius(CornerRadius.medium)
            .foregroundColor(.textPrimary)
    }
}

// MARK: - Preview

struct DevicesScreen_Previews: PreviewProvider {
    static var previews: some View {
        DevicesScreen()
    }
}
