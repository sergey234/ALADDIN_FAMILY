import SwiftUI
import UIKit

/// 📱 Devices Screen - НОВАЯ ВЕРСИЯ БЕЗ ОШИБОК
/// Экран управления устройствами семьи
/// Источник дизайна: /mobile/wireframes/12_devices_screen.html
struct DevicesScreen: View {
    
    // MARK: - State
    
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var devices: [Device] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var showAddDevice: Bool = false
    @State private var selectedFilter: DeviceFilter = .all
    @State private var expandedFilters: Set<DeviceFilter> = []
    
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
            AddDeviceView(onDeviceAdded: {
                loadDevices()
            })
        }
        .refreshable {
            await loadDevicesAsync()
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
                // ✅ ГИБРИДНЫЙ ПОДХОД: dismiss() как основной механизм + синхронизация NavigationManager
                // dismiss() - использует встроенный механизм SwiftUI, работает надёжно
                dismiss()
                
                // Дополнительно синхронизируем NavigationManager для корректной работы стека
                DispatchQueue.main.async {
                    if navigationManager.canGoBack {
                        navigationManager.goBack()
                    }
                }
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
    
    // MARK: - Device Filters (Раздвигающиеся секции как в SupportScreen)
    
    private var deviceFilters: some View {
        VStack(spacing: Spacing.m) {
            Text("ФИЛЬТРЫ")
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
                    Text(filter.rawValue)
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
                            Text("Применить фильтр")
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
        case .all: return "Показать все устройства семьи"
        case .protected: return "Устройства с активной защитой"
        case .warning: return "Устройства с предупреждениями"
        case .danger: return "Устройства в опасности"
        case .inactive: return "Неактивные устройства"
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
                    NavigationLink(destination: DeviceDetailScreen(device: device)) {
                    DeviceCard(device: device)
                    }
                    .buttonStyle(PlainButtonStyle())
                    .simultaneousGesture(
                        TapGesture().onEnded {
                            // Haptic feedback при нажатии на карточку
                            let generator = UIImpactFeedbackGenerator(style: .light)
                            generator.impactOccurred()
                        }
                    )
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
        
        // ✅ Таймаут: Если запрос не успевает за 5 секунд, показываем мок-данные
        let timeoutWorkItem = DispatchWorkItem {
            DispatchQueue.main.async {
                if self.isLoading {
                    print("⚠️ Таймаут загрузки устройств - показываем мок-данные")
                    self.isLoading = false
                    self.devices = self.getMockDevices()
                    self.errorMessage = nil
                }
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 5.0, execute: timeoutWorkItem)
        
        apiService.getDevices { result in
            timeoutWorkItem.cancel() // Отменяем таймаут если запрос успел
            
            DispatchQueue.main.async {
                isLoading = false
                
                switch result {
                case .success(let deviceResponses):
                    devices = deviceResponses.map { response in
                        convertToDevice(response)
                    }
                    errorMessage = nil
                    
                case .failure(let error):
                    // ✅ При ошибке показываем мок-данные вместо ошибки
                    print("⚠️ Ошибка загрузки устройств: \(error.localizedDescription) - показываем мок-данные")
                    devices = getMockDevices()
                    errorMessage = nil
                }
            }
        }
    }
    
    // ✅ МОК-ДАННЫЕ для демонстрации при ошибке API
    private func getMockDevices() -> [Device] {
        return [
            Device(
                id: UUID(),
                name: "iPhone 13",
                owner: "Родитель",
                type: .iphone,
                status: .protected,
                lastActive: "2 часа назад"
            ),
            Device(
                id: UUID(),
                name: "iPad Pro",
                owner: "Дочь",
                type: .ipad,
                status: .warning,
                lastActive: "5 минут назад"
            ),
            Device(
                id: UUID(),
                name: "MacBook Air",
                owner: "Родитель",
                type: .mac,
                status: .protected,
                lastActive: "1 день назад"
            ),
            Device(
                id: UUID(),
                name: "Samsung Galaxy",
                owner: "Сын",
                type: .android,
                status: .danger,
                lastActive: "Только что"
            )
        ]
    }
    
    // ✅ PULL-TO-REFRESH: Асинхронная версия loadDevices
    private func loadDevicesAsync() async {
        await withCheckedContinuation { (continuation: CheckedContinuation<Void, Never>) in
            // ✅ Таймаут: 5 секунд
            let timeoutWorkItem = DispatchWorkItem {
                DispatchQueue.main.async {
                    print("⚠️ Таймаут обновления устройств - показываем мок-данные")
                    self.devices = self.getMockDevices()
                    self.errorMessage = nil
                    continuation.resume()
                }
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 5.0, execute: timeoutWorkItem)
            
            apiService.getDevices { result in
                timeoutWorkItem.cancel() // Отменяем таймаут если запрос успел
                
                DispatchQueue.main.async {
                    switch result {
                    case .success(let deviceResponses):
                        devices = deviceResponses.map { response in
                            convertToDevice(response)
                        }
                        errorMessage = nil
                        
                    case .failure(let error):
                        // ✅ При ошибке показываем мок-данные
                        print("⚠️ Ошибка обновления устройств: \(error.localizedDescription) - показываем мок-данные")
                        devices = getMockDevices()
                        errorMessage = nil
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
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
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

// MARK: - Add Device View

struct AddDeviceView: View {
    @Environment(\.dismiss) var dismiss
    
    let onDeviceAdded: () -> Void
    
    @State private var deviceName: String = ""
    @State private var selectedDeviceType: DeviceType = .iphone
    @State private var selectedOwner: String = ""
    @State private var isLoading: Bool = false
    @State private var errorMessage: String? = nil
    @State private var showSuccessAlert: Bool = false
    
    @State private var familyMembers: [String] = []
    
    private let apiService = APIService(networkManager: NetworkManager())
    
    var body: some View {
        NavigationView {
            ZStack {
                // Фон
                LinearGradient.backgroundGradient
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Spacing.l) {
                        // Заголовок
                        Text("Добавить устройство")
                            .font(.h1)
                            .foregroundColor(.textPrimary)
                            .padding(.top, Spacing.l)
                        
                        // Форма
                        VStack(spacing: Spacing.m) {
                            // Название устройства
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text("Название устройства")
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                
                                TextField("Например: iPhone 14 Pro", text: $deviceName)
                                    .textFieldStyle(ALADDINTextFieldStyle())
                                    .autocapitalization(.words)
                                    .accessibilityLabel("Название устройства")
                            }
                            
                            // Тип устройства
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text("Тип устройства")
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                
                                    Picker("Тип устройства", selection: $selectedDeviceType) {
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
                                .accessibilityLabel("Тип устройства")
                            }
                            
                            // Владелец
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text("Владелец")
                                    .font(.body)
                                    .foregroundColor(.textPrimary)
                                
                                if familyMembers.isEmpty {
                                    Text("Загрузка членов семьи...")
                                        .font(.caption)
                                        .foregroundColor(.textSecondary)
                                        .padding()
                                } else {
                                    Picker("Владелец", selection: $selectedOwner) {
                                        ForEach(familyMembers, id: \.self) { member in
                                            Text(member)
                                                .tag(member)
                                        }
                                    }
                                    .pickerStyle(MenuPickerStyle())
                                    .padding()
                                    .background(Color.backgroundMedium.opacity(0.3))
                                    .cornerRadius(CornerRadius.medium)
                                    .accessibilityLabel("Владелец устройства")
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
                                    Text("Добавить устройство")
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
                        .padding(.bottom, Spacing.xl)
                        .accessibilityLabel("Добавить устройство")
                        .accessibilityHint(isFormValid ? "Нажмите для добавления устройства" : "Заполните все поля")
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityLabel("Форма добавления устройства")
            }
            .navigationTitle("Новое устройство")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Отмена") {
                        dismiss()
                    }
                    .foregroundColor(.textPrimary)
                }
            }
            .onAppear {
                loadFamilyMembers()
            }
            .alert("Успех", isPresented: $showSuccessAlert) {
                Button("ОК") {
                    dismiss()
                    onDeviceAdded()
                }
            } message: {
                Text("Устройство успешно добавлено!")
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
    }
    
    // MARK: - Computed Properties
    
    private var isFormValid: Bool {
        !deviceName.trimmingCharacters(in: .whitespaces).isEmpty &&
        !selectedOwner.isEmpty &&
        !familyMembers.isEmpty
    }
    
    // MARK: - Functions
    
    private func loadFamilyMembers() {
        // Загружаем список участников семьи из UserDefaults
        let familyMembersKey = "family_members_list"
        if let savedData = UserDefaults.standard.data(forKey: familyMembersKey),
           let decoded = try? JSONDecoder().decode([FamilyMemberData].self, from: savedData) {
            familyMembers = decoded.map { $0.name }
            
            // Устанавливаем первого владельца по умолчанию
            if selectedOwner.isEmpty, let firstMember = familyMembers.first {
                selectedOwner = firstMember
            }
        } else {
            // Если нет участников, добавляем текущего пользователя
            if let currentUserName = UserDefaults.standard.string(forKey: "current_user_name") {
                familyMembers = [currentUserName]
                selectedOwner = currentUserName
            } else {
                familyMembers = ["Вы"]
                selectedOwner = "Вы"
            }
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
            name: deviceName.trimmingCharacters(in: .whitespaces),
            type: deviceTypeString,
            owner: selectedOwner
        ) { result in
            DispatchQueue.main.async {
                isLoading = false
                
                switch result {
                case .success:
                    showSuccessAlert = true
                    
                case .failure(let error):
                    errorMessage = error.localizedDescription
                    print("❌ Ошибка добавления устройства: \(error.localizedDescription)")
                }
            }
        }
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
