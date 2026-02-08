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
    @Published var crashDetectionEnabled: Bool = false
    @Published var roadsideAssistanceEnabled: Bool = false
    @Published var emergencyResponseEnabled: Bool = false
    @Published var emergencyEventEnabled: Bool = false

    // Защита от угроз (4 компонента)
    @Published var phishingProtectionEnabled: Bool = false
    @Published var malwareDetectionEnabled: Bool = false
    @Published var mobileSecurityEnabled: Bool = false
    @Published var networkSecurityEnabled: Bool = false

    // Автоматическая система защиты (1 компонент)
    @Published var incidentResponseEnabled: Bool = false

    // Безопасность паролей (1 компонент)
    @Published var passwordSecurityEnabled: Bool = false

    // MARK: - Published Properties - UI State

    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    // MARK: - Initialization

    init(
        statusService: ComponentStatusService = ComponentStatusService.shared,
        configurationService: ComponentConfigurationService = ComponentConfigurationService.shared,
        retryManager: RetryManager = RetryManager()
    ) {
        self.statusService = statusService
        self.configurationService = configurationService
        self.retryManager = retryManager

        // Загружаем статусы компонентов при инициализации
        Task {
            await loadComponentStatuses()
        }
    }

    // MARK: - Public Methods

    /// Загрузить статусы всех компонентов
    func loadComponentStatuses() async {
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
        for item in prioritizedItems {
            let userDefaultsKey = "demo_component_\(item.id)_enabled"
            let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)

            await MainActor.run {
                self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)
            }

            print("📱 Демо режим: Загружен статус \(item.id) = \(isEnabled)")
        }
    }

    private func loadProductionModeStatuses(prioritizedItems: [(id: String, priority: ComponentLoadPriority)]) async {
        // Продакшен режим: загружаем из API
        for item in prioritizedItems {
            do {
                let status = try await APIService.shared.getComponentStatus(componentId: item.id)
                await MainActor.run {
                    self.updateStatusForComponent(componentId: item.id, status: status)
                }
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
        Task { @MainActor in
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
    }

    // MARK: - Private Toggle Method

    private func toggleComponent(
        componentId: String,
        newValue: Bool,
        updateClosure: @escaping (Bool) -> Void
    ) async {
        // Оптимистичное обновление UI с переданным значением
        updateClosure(newValue)

        // Проверяем демо режим (отсутствие токена)
        if AppConfig.authToken == nil {
            // Демо режим: сохраняем локально в UserDefaults
            await handleDemoModeToggle(componentId: componentId, newValue: newValue, updateClosure: updateClosure)
        } else {
            // Продакшен режим: используем API
            await handleProductionModeToggle(componentId: componentId, newValue: newValue, updateClosure: updateClosure)
        }
    }

    private func handleDemoModeToggle(
        componentId: String,
        newValue: Bool,
        updateClosure: @escaping (Bool) -> Void
    ) async {
        // Демо режим: сохраняем статус локально в UserDefaults
        let userDefaultsKey = "demo_component_\(componentId)_enabled"
        UserDefaults.standard.set(newValue, forKey: userDefaultsKey)

        // Отследить успешное переключение
        componentAnalytics.trackComponentToggle(
            componentId: componentId,
            enabled: newValue
        )

        // Показываем уведомление для демо режима
        toastManager.showSuccess("Компонент обновлен (демо режим)")
        print("✅ Демо режим: Компонент \(componentId) установлен в \(newValue)")
    }

    private func handleProductionModeToggle(
        componentId: String,
        newValue: Bool,
        updateClosure: @escaping (Bool) -> Void
    ) async {
        do {
            try await statusService.updateStatus(
                componentId: componentId,
                isEnabled: newValue
            )

            // Успешное обновление
            componentAnalytics.trackComponentToggle(
                componentId: componentId,
                enabled: newValue
            )
            toastManager.showSuccess("Компонент обновлен")

        } catch {
            // Откат изменений при ошибке
            updateClosure(!newValue)
            // Отследить ошибку
            componentAnalytics.trackComponentError(componentId: componentId, error: error)
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }
}