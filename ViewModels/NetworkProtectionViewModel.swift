import Foundation
import SwiftUI
import Combine
import CoreMotion
import CoreLocation

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
    private let toastManager = ToastManager.shared
    private let componentAnalytics = ComponentAnalytics.shared

    // MARK: - Published Properties - Component Statuses

    // Экстренная помощь (4 компонента)
    @Published var crashDetectionEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_crash_detection_agent_enabled")
    @Published var roadsideAssistanceEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_roadside_assistance_agent_enabled")
    @Published var emergencyResponseEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_emergency_response_bot_enabled")
    @Published var emergencyEventEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_emergency_event_manager_enabled")

    // Защита от угроз (4 компонента)
    @Published var phishingProtectionEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_phishing_protection_agent_enabled")
    @Published var malwareDetectionEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_malware_detection_agent_enabled")
    @Published var mobileSecurityEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_mobile_security_agent_enabled")
    @Published var networkSecurityEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_network_security_agent_enabled")

    // Автоматическая система защиты (1 компонент)
    @Published var incidentResponseEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_incident_response_agent_enabled")

    // Безопасность паролей (1 компонент)
    @Published var passwordSecurityEnabled: Bool = UserDefaults.standard.bool(forKey: "demo_component_password_security_agent_enabled")

    // MARK: - Published Properties - UI State

    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    // ✅ BUILD 104: Защита от повторной загрузки статусов
    private var hasLoadedStatuses = false

    // MARK: - Initialization

    init(
        statusService: ComponentStatusService = ComponentStatusService.shared,
        configurationService: ComponentConfigurationService = ComponentConfigurationService.shared,
        retryManager: RetryManager = RetryManager()
    ) {
        self.statusService = statusService
        self.configurationService = configurationService
        self.retryManager = retryManager

        // ✅ BUILD 104: УБРАЛИ Task {} из init() - загрузка статусов перенесена в .onAppear
        // Это предотвращает рекурсию при пересоздании View
    }

    // MARK: - Public Methods - Synchronous (BUILD 107)
    
    func toggleCrashDetectionSync(_ newValue: Bool) {
        self.crashDetectionEnabled = newValue
        Task { @MainActor in await toggleCrashDetection(newValue) }
    }
    
    func toggleRoadsideAssistanceSync(_ newValue: Bool) {
        self.roadsideAssistanceEnabled = newValue
        Task { @MainActor in await toggleRoadsideAssistance(newValue) }
    }
    
    func toggleEmergencyResponseSync(_ newValue: Bool) {
        self.emergencyResponseEnabled = newValue
        Task { @MainActor in await toggleEmergencyResponse(newValue) }
    }
    
    func toggleEmergencyEventSync(_ newValue: Bool) {
        self.emergencyEventEnabled = newValue
        Task { @MainActor in await toggleEmergencyEvent(newValue) }
    }
    
    func togglePhishingProtectionSync(_ newValue: Bool) {
        self.phishingProtectionEnabled = newValue
        Task { @MainActor in await togglePhishingProtection(newValue) }
    }
    
    func toggleMalwareDetectionSync(_ newValue: Bool) {
        self.malwareDetectionEnabled = newValue
        Task { @MainActor in await toggleMalwareDetection(newValue) }
    }
    
    func toggleMobileSecuritySync(_ newValue: Bool) {
        self.mobileSecurityEnabled = newValue
        Task { @MainActor in await toggleMobileSecurity(newValue) }
    }
    
    func toggleNetworkSecuritySync(_ newValue: Bool) {
        self.networkSecurityEnabled = newValue
        Task { @MainActor in await toggleNetworkSecurity(newValue) }
    }
    
    func toggleIncidentResponseSync(_ newValue: Bool) {
        self.incidentResponseEnabled = newValue
        Task { @MainActor in await toggleIncidentResponse(newValue) }
    }
    
    func togglePasswordSecuritySync(_ newValue: Bool) {
        self.passwordSecurityEnabled = newValue
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

        // Проверяем демо режим
        if AppConfig.authToken == nil {
            // Демо режим: загружаем из UserDefaults
            await loadDemoModeStatuses(prioritizedItems: prioritizedItems)
        } else {
            // Продакшен режим: загружаем из API
            await loadProductionModeStatuses(prioritizedItems: prioritizedItems)
        }

        print("✅ NetworkProtectionViewModel: Загрузка статусов завершена")
    }

    private func loadDemoModeStatuses(prioritizedItems: [(id: String, priority: ComponentLoadPriority)]) async {
        // Демо режим: загружаем статусы из UserDefaults
        // ✅ BUILD 104: УБРАЛИ await MainActor.run {} - метод уже на @MainActor
        for item in prioritizedItems {
            let userDefaultsKey = "demo_component_\(item.id)_enabled"
            let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)

            self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)

            print("📱 Демо режим: Загружен статус \(item.id) = \(isEnabled)")
        }
    }

    private func loadProductionModeStatuses(prioritizedItems: [(id: String, priority: ComponentLoadPriority)]) async {
        // Продакшен режим: загружаем из API
        // ✅ BUILD 104: УБРАЛИ await MainActor.run {} - метод уже на @MainActor
        for item in prioritizedItems {
            do {
                let status = try await APIService.shared.getComponentStatus(componentId: item.id)
                self.updateStatusForComponent(componentId: item.id, status: status)
            } catch {
                print("⚠️ Ошибка загрузки статуса для \(item.id): \(error.localizedDescription)")
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
        await toggleComponent(
            componentId: "crash_detection_agent",
            newValue: newValue,
            updateClosure: { [weak self] value in self?.crashDetectionEnabled = value }
        )

        // Интеграция с CrashDetectionManager
        do {
            if newValue {
                try await CrashDetectionManager.shared.startMonitoring()
            } else {
                try await CrashDetectionManager.shared.stopMonitoring()
            }
        } catch {
            print("❌ NetworkProtectionViewModel: Ошибка управления Crash Detection: \(error.localizedDescription)")
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
        // ✅ BUILD 101: Защита от повторного переключения
        togglingLock.lock()
        guard !isToggling else {
            togglingLock.unlock()
            print("⚠️ NetworkProtectionViewModel: toggleComponent уже выполняется, пропускаем повторный вызов")
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
        // Автоматически на main thread благодаря @MainActor
        updateClosure(newValue)

        // ✅ BUILD 102: Единая логика для всех режимов
        do {
            // Пытаемся обновить через API (если есть токен)
            if AppConfig.authToken != nil {
                try await statusService.updateStatus(
                    componentId: componentId,
                    isEnabled: newValue
                )
            } else {
                // Демо режим: сохраняем локально в UserDefaults
                // ✅ BUILD 104: УБРАЛИ await MainActor.run {} - метод уже на @MainActor
                let userDefaultsKey = "demo_component_\(componentId)_enabled"
                UserDefaults.standard.set(newValue, forKey: userDefaultsKey)
            }

            // Успешное обновление
            // ✅ BUILD 106: Используем await MainActor.run для гарантии main thread НЕМЕДЛЕННО после await
            await MainActor.run {
                componentAnalytics.trackComponentToggle(
                    componentId: componentId,
                    enabled: newValue
                )
                
                if AppConfig.authToken == nil {
                    toastManager.showSuccess("Компонент обновлен (демо режим)")
                } else {
                    toastManager.showSuccess("Компонент обновлен")
                }
            }

        } catch {
            // Откат изменений при ошибке
            // ✅ BUILD 102: Оптимистичное обновление UI
            updateClosure(!newValue)
            
            // Отследить ошибку
            // ✅ BUILD 106: Используем await MainActor.run для гарантии main thread НЕМЕДЛЕННО после await
            // Явно захватываем error в замыкании для избежания ошибок компиляции
            let errorToReport = error
            await MainActor.run {
                componentAnalytics.trackComponentError(componentId: componentId, error: errorToReport)
                toastManager.showError("Ошибка: \(errorToReport.localizedDescription)")
            }
        }
    }
}