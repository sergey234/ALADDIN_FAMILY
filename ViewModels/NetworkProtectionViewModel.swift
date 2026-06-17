import Foundation
import SwiftUI
import Combine

/**
 * 🔒 Network Protection ViewModel
 * ViewModel для управления 10 компонентами на экране NetworkProtectionScreen
 * Использует ComponentStatusService для загрузки и обновления статусов
 */

@MainActor
class NetworkProtectionViewModel: ObservableObject {

    // MARK: - Dependencies

    private let statusService: ComponentStatusService
    private let configurationService: ComponentConfigurationService
    private let retryManager: RetryManager
    private let crashDetection: CrashDetectionControlling
    private let toastManager = ToastManager.shared
    private let componentAnalytics = ComponentAnalytics.shared

    // MARK: - Published Properties - Component Statuses

    // Экстренная помощь (4 компонента)
    @Published var crashDetectionEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "crash_detection_agent")
    @Published var roadsideAssistanceEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "roadside_assistance_agent")
    @Published var emergencyResponseEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "emergency_response_bot")
    @Published var emergencyEventEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "emergency_event_manager")

    // Защита от угроз (4 компонента)
    @Published var phishingProtectionEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "phishing_protection_agent")
    @Published var malwareDetectionEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "malware_detection_agent")
    @Published var mobileSecurityEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "mobile_security_agent")
    @Published var networkSecurityEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "network_security_agent")
    @Published var iotSecurityEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "iot_security_agent")

    // Автоматическая система защиты (1 компонент)
    @Published var incidentResponseEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "incident_response_agent")

    // Безопасность паролей (1 компонент)
    @Published var passwordSecurityEnabled: Bool = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: "password_security_agent")

    // MARK: - Published Properties - UI State

    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var crashDetectionUnavailableOnThisDevice: Bool = false
    @Published var crashDetectionUnavailableReason: String?

    // ✅ BUILD 104: Защита от повторной загрузки статусов
    private var hasLoadedStatuses = false

    // MARK: - Initialization

    @MainActor init(
        statusService: ComponentStatusService = .shared,
        configurationService: ComponentConfigurationService = .shared,
        retryManager: RetryManager = RetryManager(),
        crashDetection: CrashDetectionControlling? = nil
    ) {
        self.statusService = statusService
        self.configurationService = configurationService
        self.retryManager = retryManager
        self.crashDetection = crashDetection ?? CrashDetectionManager.shared
        self.crashDetectionUnavailableOnThisDevice = !self.crashDetection.isCrashDetectionSupportedOnCurrentDevice
        self.crashDetectionUnavailableReason = self.crashDetection.crashDetectionUnsupportedReason

        // ✅ BUILD 104: УБРАЛИ Task {} из init() - загрузка статусов перенесена в .onAppear
        // Это предотвращает рекурсию при пересоздании View
    }

    // MARK: - Public Methods - Synchronous (BUILD 107)
    
    func toggleCrashDetectionSync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.crashDetectionEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения и аналитики
        Task { @MainActor in 
            await toggleCrashDetection(newValue) 
        }
    }
    
    func toggleRoadsideAssistanceSync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.roadsideAssistanceEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения и аналитики
        Task { @MainActor in 
            await toggleRoadsideAssistance(newValue) 
        }
    }
    
    func toggleEmergencyResponseSync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.emergencyResponseEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения
        Task { @MainActor in await toggleEmergencyResponse(newValue) }
    }
    
    func toggleEmergencyEventSync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.emergencyEventEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения
        Task { @MainActor in await toggleEmergencyEvent(newValue) }
    }
    
    func togglePhishingProtectionSync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.phishingProtectionEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения
        Task { @MainActor in await togglePhishingProtection(newValue) }
    }
    
    func toggleMalwareDetectionSync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.malwareDetectionEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения
        Task { @MainActor in await toggleMalwareDetection(newValue) }
    }
    
    func toggleMobileSecuritySync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.mobileSecurityEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения
        Task { @MainActor in await toggleMobileSecurity(newValue) }
    }
    
    func toggleNetworkSecuritySync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.networkSecurityEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения
        Task { @MainActor in await toggleNetworkSecurity(newValue) }
    }
    
    func toggleIotSecuritySync(_ newValue: Bool) {
        self.iotSecurityEnabled = newValue
        Task { @MainActor in await toggleIotSecurity(newValue) }
    }
    
    func toggleIncidentResponseSync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.incidentResponseEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения
        Task { @MainActor in await toggleIncidentResponse(newValue) }
    }
    
    func togglePasswordSecuritySync(_ newValue: Bool) {
        // ✅ BUILD 114: Сначала мгновенно обновляем UI
        self.passwordSecurityEnabled = newValue
        
        // Затем асинхронно запускаем логику сохранения
        Task { @MainActor in await togglePasswordSecurity(newValue) }
    }

    // MARK: - Public Methods - Asynchronous (Core Logic)
    func loadComponentStatuses() async {
        // ✅ BUILD 104: Защита от повторной загрузки
        guard !hasLoadedStatuses else {
            print("⚠️ NetworkProtectionViewModel: Статусы уже загружены, пропускаем")
            return
        }
        
        hasLoadedStatuses = true
        isLoading = true
        defer { isLoading = false }

        // Загружаем статусы по приоритетам
        let prioritizedItems = createPrioritizedLoadItems()

        // Режим без сессии (локальный кэш тумблеров)
        if !TokenValidator.hasUsableAPISession {
            await loadLocalCacheStatuses(prioritizedItems: prioritizedItems)
        } else {
            // Продакшен режим: загружаем из API
            await loadProductionModeStatuses(prioritizedItems: prioritizedItems)
        }

        print("✅ NetworkProtectionViewModel: Загрузка статусов завершена")
    }

    private func loadLocalCacheStatuses(prioritizedItems: [(id: String, priority: ComponentLoadPriority)]) async {
        // Локальный режим: статусы из UserDefaults (кэш тумблеров)
        // ✅ BUILD 104: УБРАЛИ await MainActor.run {} - метод уже на @MainActor
        for item in prioritizedItems {
            let isEnabled = AppConfig.NetworkProtectionComponentToggleStorage.readBool(componentId: item.id)

            self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)

            print("📱 Локальный кэш: статус \(item.id) = \(isEnabled)")
        }
    }

    private func loadProductionModeStatuses(prioritizedItems: [(id: String, priority: ComponentLoadPriority)]) async {
        // Продакшен режим: загружаем из API
        // ✅ BUILD 104: УБРАЛИ await MainActor.run {} - метод уже на @MainActor
        // ✅ ЭТАП 2: Проверка токена перед загрузкой
        guard TokenValidator.hasUsableAPISession else {
            print("⚠️ NetworkProtectionViewModel: Нет API-сессии, загружаем локальный кэш тумблеров")
            await loadLocalCacheStatuses(prioritizedItems: prioritizedItems)
            return
        }
        
        for item in prioritizedItems {
            do {
                let status = try await statusService.getStatus(for: item.id, priority: .normal)
                self.updateStatusForComponent(componentId: item.id, status: status)
            } catch {
                // ✅ ЭТАП 3: Обработка unauthorized
                let networkError = NetworkError.from(error)
                if case .unauthorized = networkError {
                    print("⚠️ NetworkProtectionViewModel: Ошибка авторизации при загрузке статуса для \(item.id)")
                    // Отправляем уведомление о необходимости логина
                    NotificationCenter.default.post(
                        name: NSNotification.Name("SessionExpired"),
                        object: nil,
                        userInfo: ["message": "Сессия истекла. Пожалуйста, войдите снова."]
                    )
                    // Прерываем загрузку остальных статусов
                    break
                } else {
                    print("⚠️ Ошибка загрузки статуса для \(item.id): \(error.localizedDescription)")
                }
            }
        }
    }

    /// Обновить статус компонента
    func toggleComponent(_ componentId: String, newValue: Bool) async {
        await toggleComponent(
            componentId: componentId,
            newValue: newValue,
            updateClosure: { [weak self] value in
                self?.updateStatusForComponent(componentId: componentId, isEnabled: value)
            }
        )
    }

    func toggleCrashDetection(_ newValue: Bool) async {
        if newValue {
            await enableCrashDetectionHardwareFirstThenServer()
            return
        }

        await toggleComponent(
            componentId: "crash_detection_agent",
            newValue: false,
            updateClosure: { [weak self] value in self?.crashDetectionEnabled = value }
        )

        do {
            try await crashDetection.stopMonitoring()
        } catch {
            print("❌ NetworkProtectionViewModel: Ошибка остановки Crash Detection: \(error.localizedDescription)")
        }
    }

    /// Вариант B: сначала локальный мониторинг; при успехе — включение компонента на сервере.
    private func enableCrashDetectionHardwareFirstThenServer() async {
        let componentId = "crash_detection_agent"
        let recursionKey = "NetworkProtectionViewModel.isToggling.\(componentId)"
        if Thread.current.threadDictionary[recursionKey] != nil {
            print("⚠️ [NetworkProtectionViewModel] Рекурсия заблокирована для \(componentId)")
            return
        }
        Thread.current.threadDictionary[recursionKey] = true
        defer { Thread.current.threadDictionary.removeObject(forKey: recursionKey) }

        togglingLock.lock()
        guard !isToggling else {
            togglingLock.unlock()
            print("⚠️ NetworkProtectionViewModel: toggleComponent уже выполняется, пропускаем")
            return
        }
        isToggling = true
        togglingLock.unlock()
        defer {
            togglingLock.lock()
            isToggling = false
            togglingLock.unlock()
        }

        let isProduction = AppConfig.authToken != nil

        errorMessage = nil

        do {
            try await crashDetection.startMonitoring()
            crashDetectionUnavailableOnThisDevice = false
            crashDetectionUnavailableReason = nil
        } catch {
            crashDetectionEnabled = false
            errorMessage = error.localizedDescription
            if case CrashDetectionError.accelerometerUnavailable = error {
                crashDetectionUnavailableOnThisDevice = true
                crashDetectionUnavailableReason = crashDetection.crashDetectionUnsupportedReason ?? error.localizedDescription
            }
            componentAnalytics.trackComponentError(componentId: componentId, error: error)
            toastManager.showError(error.localizedDescription)
            print("❌ NetworkProtectionViewModel: Не удалось запустить Crash Detection на устройстве: \(error.localizedDescription)")
            return
        }

        if isProduction {
            do {
                try await statusService.updateStatus(componentId: componentId, isEnabled: true)
            } catch {
                try? await crashDetection.stopMonitoring()
                crashDetectionEnabled = false
                errorMessage = error.localizedDescription
                let networkError = NetworkError.from(error)
                if case .unauthorized(let message) = networkError {
                    let errorText = message ?? "Сессия истекла. Пожалуйста, войдите снова."
                    toastManager.showError(errorText)
                    NotificationCenter.default.post(
                        name: NSNotification.Name("SessionExpired"),
                        object: nil,
                        userInfo: ["message": errorText]
                    )
                } else {
                    componentAnalytics.trackComponentError(componentId: componentId, error: error)
                    toastManager.showError("Ошибка: \(error.localizedDescription)")
                }
                return
            }
            componentAnalytics.trackComponentToggle(componentId: componentId, enabled: true)
            toastManager.showSuccess("Компонент обновлен")
        } else {
            AppConfig.NetworkProtectionComponentToggleStorage.writeBool(true, componentId: componentId)
            componentAnalytics.trackComponentToggle(componentId: componentId, enabled: true)
            toastManager.showSuccess("Компонент обновлён локально")
        }
    }

    func toggleRoadsideAssistance(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "roadside_assistance_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.roadsideAssistanceEnabled = value }
        )
    }

    func toggleEmergencyResponse(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "emergency_response_bot",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.emergencyResponseEnabled = value }
        )
    }

    func toggleEmergencyEvent(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "emergency_event_manager",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.emergencyEventEnabled = value }
        )
    }

    func togglePhishingProtection(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "phishing_protection_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.phishingProtectionEnabled = value }
        )
    }

    func toggleMalwareDetection(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "malware_detection_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.malwareDetectionEnabled = value }
        )
    }

    func toggleMobileSecurity(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "mobile_security_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.mobileSecurityEnabled = value }
        )
    }

    func toggleNetworkSecurity(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "network_security_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.networkSecurityEnabled = value }
        )
    }

    func toggleIotSecurity(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "iot_security_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.iotSecurityEnabled = value }
        )
    }

    func toggleIncidentResponse(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "incident_response_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.incidentResponseEnabled = value }
        )
    }

    func togglePasswordSecurity(_ newValue: Bool) async {
        await toggleComponent(
            componentId: "password_security_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.passwordSecurityEnabled = value }
        )
    }

    // MARK: - Private Methods

    private func createPrioritizedLoadItems() -> [(id: String, priority: ComponentLoadPriority)] {
        let components: [(String, ComponentLoadPriority)] = [
            ("crash_detection_agent", .critical),
            ("roadside_assistance_agent", .critical),
            ("emergency_response_bot", .high),
            ("emergency_event_manager", .high),
            ("phishing_protection_agent", .normal),
            ("malware_detection_agent", .normal),
            ("mobile_security_agent", .normal),
            ("network_security_agent", .normal),
            ("iot_security_agent", .normal),
            ("incident_response_agent", .low),
            ("password_security_agent", .low)
        ]

        return components
    }

    private func updateStatusForComponent(componentId: String, status: ComponentStatus) {
        updateStatusForComponent(componentId: componentId, isEnabled: status.isEnabled)
    }

    private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
        // ✅ BUILD 104: УБРАЛИ Task { @MainActor in } - метод уже на @MainActor
        switch componentId {
        case "crash_detection_agent":
            crashDetectionEnabled = isEnabled
        case "roadside_assistance_agent":
            roadsideAssistanceEnabled = isEnabled
        case "emergency_response_bot":
            emergencyResponseEnabled = isEnabled
        case "emergency_event_manager":
            emergencyEventEnabled = isEnabled
        case "phishing_protection_agent":
            phishingProtectionEnabled = isEnabled
        case "malware_detection_agent":
            malwareDetectionEnabled = isEnabled
        case "mobile_security_agent":
            mobileSecurityEnabled = isEnabled
        case "network_security_agent":
            networkSecurityEnabled = isEnabled
        case "iot_security_agent":
            iotSecurityEnabled = isEnabled
        case "incident_response_agent":
            incidentResponseEnabled = isEnabled
        case "password_security_agent":
            passwordSecurityEnabled = isEnabled
        default:
            break
        }
    }

    // MARK: - Private Toggle Method
    
    /// ✅ BUILD 101: Защита от повторного переключения для предотвращения рекурсии
    /// На реальном устройстве синхронный UserDefaults.standard.set() вызывает обновление View,
    /// которое может вызвать повторное переключение тумблера → рекурсия
    private var isToggling = false
    private let togglingLock = NSLock()

    private func toggleComponent(
        componentId: String,
        newValue: Bool,
        updateClosure: @escaping (Bool) -> Void
    ) async {
        // 🛡️ BUILD 114: Защита от рекурсии через thread dictionary
        let recursionKey = "NetworkProtectionViewModel.isToggling.\(componentId)"
        if Thread.current.threadDictionary[recursionKey] != nil {
            print("⚠️ [NetworkProtectionViewModel] Рекурсия заблокирована для \(componentId)")
            return
        }
        Thread.current.threadDictionary[recursionKey] = true
        defer { Thread.current.threadDictionary.removeObject(forKey: recursionKey) }

        // ✅ BUILD 101: Защита от повторного переключения (второй уровень)
        togglingLock.lock()
        guard !isToggling else {
            togglingLock.unlock()
            print("⚠️ NetworkProtectionViewModel: toggleComponent уже выполняется, пропускаем")
            return
        }
        isToggling = true
        togglingLock.unlock()
        
        defer {
            togglingLock.lock()
            isToggling = false
            togglingLock.unlock()
        }
        
        // ✅ BUILD 102: Оптимистичное обновление UI
        updateClosure(newValue)

        let isProduction = AppConfig.authToken != nil

        if isProduction {
            // ✅ ЭТАП 2: Проверка токена перед запросом
            guard AppConfig.authToken != nil else {
                DispatchQueue.main.async { [weak self] in
                    updateClosure(!newValue)
                    self?.toastManager.showError("Требуется авторизация. Войдите в аккаунт.")
                    // Отправляем уведомление о необходимости логина
                    NotificationCenter.default.post(
                        name: NSNotification.Name("SessionExpired"),
                        object: nil,
                        userInfo: ["message": "Требуется авторизация. Войдите в аккаунт."]
                    )
                }
                return
            }
            
            do {
                try await statusService.updateStatus(componentId: componentId, isEnabled: newValue)
                
                // Успешная аналитика (асинхронно)
                DispatchQueue.main.async { [weak self] in
                    self?.componentAnalytics.trackComponentToggle(componentId: componentId, enabled: newValue)
                    self?.toastManager.showSuccess("Компонент обновлен")
                }
            } catch {
                // ✅ ЭТАП 3: Обработка unauthorized
                let networkError = NetworkError.from(error)
                if case .unauthorized(let message) = networkError {
                    // Откат изменений (асинхронно)
                    DispatchQueue.main.async { [weak self] in
                        updateClosure(!newValue)
                        let errorMessage = message ?? "Сессия истекла. Пожалуйста, войдите снова."
                        self?.toastManager.showError(errorMessage)
                        // Отправляем уведомление о необходимости логина
                        NotificationCenter.default.post(
                            name: NSNotification.Name("SessionExpired"),
                            object: nil,
                            userInfo: ["message": errorMessage]
                        )
                    }
                } else {
                    // Откат изменений (асинхронно)
                    DispatchQueue.main.async { [weak self] in
                        updateClosure(!newValue)
                        self?.componentAnalytics.trackComponentError(componentId: componentId, error: error)
                        self?.toastManager.showError("Ошибка: \(error.localizedDescription)")
                    }
                }
            }
        } else {
            // Локально (без сессии): сохраняем только на устройстве
            DispatchQueue.main.async { [weak self] in
                AppConfig.NetworkProtectionComponentToggleStorage.writeBool(newValue, componentId: componentId)
                self?.componentAnalytics.trackComponentToggle(componentId: componentId, enabled: newValue)
                self?.toastManager.showSuccess("Компонент обновлён локально")
            }
        }
    }
}