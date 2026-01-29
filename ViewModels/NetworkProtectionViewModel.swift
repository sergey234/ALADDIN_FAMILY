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
    @Published var showPasswordGenerator: Bool = false
    @Published var showIncidentResponseSettings: Bool = false
    
    // ✅ ЗАЩИТА ОТ БЕСКОНЕЧНЫХ ЦИКЛОВ
    private var isUpdatingStatuses = false
    
    // MARK: - Private Properties
    
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(
        statusService: ComponentStatusService = .shared,
        configurationService: ComponentConfigurationService = .shared,
        retryManager: RetryManager = .balanced()
    ) {
        self.statusService = statusService
        self.configurationService = configurationService
        self.retryManager = retryManager
        
        // Загрузить критичные компоненты при инициализации
        Task {
            await loadCriticalComponents()
        }
    }
    
    // MARK: - Public Methods
    
    /// Загрузить статусы критичных компонентов
    func loadCriticalComponents() async {
        isLoading = true
        errorMessage = nil
        
        // Попытка загрузить компоненты (теперь с fallback в ComponentStatusService)
        do {
            try await self.statusService.loadCriticalComponentsStatus()
            await updateLocalStatuses()
            isLoading = false
        } catch {
            // Эта ветка теперь НЕ должна выполняться (fallback в ComponentStatusService)
            // Но на всякий случай обновляем локальные статусы из дефолтных
            await updateLocalStatuses()
            isLoading = false
            // НЕ показывать ошибку пользователю - fallback уже обработал ситуацию
            // toastManager.showError("Ошибка загрузки компонентов") // ❌ УБРАНО
        }
    }
    
    // MARK: - Toggle Methods
    
    func toggleCrashDetection(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "crash_detection_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.crashDetectionEnabled = value }
            )
        }
    }
    
    func toggleRoadsideAssistance(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "roadside_assistance_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.roadsideAssistanceEnabled = value }
            )
        }
    }

    func toggleEmergencyResponse(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "emergency_response_bot",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.emergencyResponseEnabled = value }
            )
        }
    }

    func toggleEmergencyEvent(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "emergency_event_manager",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.emergencyEventEnabled = value }
            )
        }
    }
    
    func togglePhishingProtection(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "phishing_protection_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.phishingProtectionEnabled = value }
            )
        }
    }

    func toggleMalwareDetection(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "malware_detection_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.malwareDetectionEnabled = value }
            )
        }
    }

    func toggleMobileSecurity(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "mobile_security_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.mobileSecurityEnabled = value }
            )
        }
    }
    
    func toggleNetworkSecurity(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "network_security_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.networkSecurityEnabled = value }
            )
        }
    }

    func toggleIncidentResponse(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "incident_response_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.incidentResponseEnabled = value }
            )
        }
    }

    func togglePasswordSecurity(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "password_security_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.passwordSecurityEnabled = value }
            )
        }
    }
    
    // MARK: - Private Methods
    
    private func toggleComponent(
        componentId: String,
        newValue: Bool,
        updateClosure: @escaping (Bool) -> Void
    ) async {
        // Оптимистичное обновление UI с переданным значением
        updateClosure(newValue)

        // Проверяем демо-режим (нет токена авторизации)
        let isDemoMode = AppConfig.authToken == nil

        if isDemoMode {
            // В демо-режиме сохраняем локально в UserDefaults
            UserDefaults.standard.set(newValue, forKey: "demo_\(componentId)")
            componentAnalytics.trackComponentToggle(componentId: componentId, enabled: newValue)
            toastManager.showSuccess("Компонент обновлен (демо-режим)")
            return
        }
        
        let result: Result<Void, NetworkError> = await retryManager.execute(
            operation: {
                do {
                    try await self.statusService.updateStatus(
                        componentId: componentId,
                        isEnabled: newValue
                    )
                } catch let error as ComponentError {
                    throw error.toNetworkError()
                }
            },
            retryCondition: { $0.isRetryable }
        )
        
        switch result {
        case .success:
            // Отследить успешное переключение
            componentAnalytics.trackComponentToggle(
                componentId: componentId,
                enabled: newValue
            )
            toastManager.showSuccess("Компонент обновлен")
        case .failure(let error):
            // Откат изменений
            updateClosure(!newValue)
            // Отследить ошибку
            componentAnalytics.trackComponentError(componentId: componentId, error: error)
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }

    private func updateLocalStatuses() async {
        // ✅ ЗАЩИТА ОТ БЕСКОНЕЧНЫХ ЦИКЛОВ: Если уже обновляется, пропустить
        guard !isUpdatingStatuses else {
            print("⚠️ NetworkProtectionViewModel: Обновление статусов уже выполняется, пропускаем")
            return
        }

        isUpdatingStatuses = true
        defer { isUpdatingStatuses = false }

        // ✅ ПРОВЕРКА ДЕМО-РЕЖИМА: В демо-режиме загружаем из UserDefaults
        let isDemoMode = AppConfig.authToken == nil
        if isDemoMode {
            await loadDemoSettings()
            return
        }

        // ✅ УЛУЧШЕНИЕ: Параллельная загрузка с лимитом и приоритизацией
        // Критичные компоненты загружаются первыми
        let componentIds: [(String, ComponentLoadPriority)] = [
            ("crash_detection_agent", .critical),
            ("emergency_response_bot", .critical),
            ("emergency_event_manager", .critical),
            ("phishing_protection_agent", .high),
            ("malware_detection_agent", .high),
            ("password_security_agent", .high),
            ("mobile_security_agent", .normal),
            ("network_security_agent", .normal),
            ("incident_response_agent", .normal),
            ("roadside_assistance_agent", .normal)
        ]
        
        let prioritizedItems: [PrioritizedLoadItem<ComponentStatus>] = componentIds.map { componentId, priority in
            PrioritizedLoadItem(
                id: componentId,
                priority: priority
            ) { [weak self] in
                guard let self = self else {
                    throw ComponentError.unknown(NSError(domain: "NetworkProtectionViewModel", code: -1))
                }
                do {
                    return try await self.statusService.getStatus(for: componentId)
                } catch {
                    // ✅ FALLBACK: Использовать дефолтное значение из componentStatuses
                    let defaultStatus = await self.statusService.componentStatuses[componentId]
                    if let status = defaultStatus {
                        return status
                    } else {
                        // Если даже дефолтного нет, создать новый со значением false
                        return ComponentStatus(
                            componentId: componentId,
                            isEnabled: false,
                            lastUpdate: nil,
                            configuration: nil
                        )
                    }
                }
            }
        }
        
        do {
            let results = try await ParallelLoader.executeWithLimit(
                items: prioritizedItems,
                maxConcurrent: 10
            ) { [weak self] componentId, status in
                self?.updateStatusForComponent(componentId: componentId, status: status)
            }
            
            print("✅ NetworkProtectionViewModel: Обновлено \(results.count) статусов")
        } catch {
            print("⚠️ NetworkProtectionViewModel: Ошибка загрузки статусов: \(error)")
        }
    }

    /// Загрузить настройки из демо-режима (UserDefaults)
    private func loadDemoSettings() async {
        print("🔄 NetworkProtectionViewModel: Загружаем демо-настройки из UserDefaults")

        await MainActor.run {
            let userDefaults = UserDefaults.standard

            // Загружаем сохраненные значения для каждого компонента
            crashDetectionEnabled = userDefaults.bool(forKey: "demo_crash_detection_agent")
                ? userDefaults.bool(forKey: "demo_crash_detection_agent") : crashDetectionEnabled

            roadsideAssistanceEnabled = userDefaults.bool(forKey: "demo_roadside_assistance_agent")
                ? userDefaults.bool(forKey: "demo_roadside_assistance_agent") : roadsideAssistanceEnabled

            emergencyResponseEnabled = userDefaults.bool(forKey: "demo_emergency_response_bot")
                ? userDefaults.bool(forKey: "demo_emergency_response_bot") : emergencyResponseEnabled

            emergencyEventEnabled = userDefaults.bool(forKey: "demo_emergency_event_manager")
                ? userDefaults.bool(forKey: "demo_emergency_event_manager") : emergencyEventEnabled

            phishingProtectionEnabled = userDefaults.bool(forKey: "demo_phishing_protection_agent")
                ? userDefaults.bool(forKey: "demo_phishing_protection_agent") : phishingProtectionEnabled

            malwareDetectionEnabled = userDefaults.bool(forKey: "demo_malware_detection_agent")
                ? userDefaults.bool(forKey: "demo_malware_detection_agent") : malwareDetectionEnabled

            mobileSecurityEnabled = userDefaults.bool(forKey: "demo_mobile_security_agent")
                ? userDefaults.bool(forKey: "demo_mobile_security_agent") : mobileSecurityEnabled

            networkSecurityEnabled = userDefaults.bool(forKey: "demo_network_security_agent")
                ? userDefaults.bool(forKey: "demo_network_security_agent") : networkSecurityEnabled

            incidentResponseEnabled = userDefaults.bool(forKey: "demo_incident_response_agent")
                ? userDefaults.bool(forKey: "demo_incident_response_agent") : incidentResponseEnabled

            passwordSecurityEnabled = userDefaults.bool(forKey: "demo_password_security_agent")
                ? userDefaults.bool(forKey: "demo_password_security_agent") : passwordSecurityEnabled

            print("✅ NetworkProtectionViewModel: Демо-настройки загружены из UserDefaults")
        }
    }

    private func updateStatusForComponent(componentId: String, status: ComponentStatus) {
        // ✅ ИСПРАВЛЕНИЕ МНОГОПОТОЧНОСТИ: Все обновления UI должны быть в main thread
        // ✅ ИСПРАВЛЕНИЕ БЕСКОНЕЧНЫХ ЛОГОВ: Обновляем только если значение изменилось
        Task { @MainActor in
        switch componentId {
        case "crash_detection_agent":
                if crashDetectionEnabled != status.isEnabled {
            crashDetectionEnabled = status.isEnabled
                }
        case "roadside_assistance_agent":
                if roadsideAssistanceEnabled != status.isEnabled {
            roadsideAssistanceEnabled = status.isEnabled
                }
        case "emergency_response_bot":
                if emergencyResponseEnabled != status.isEnabled {
            emergencyResponseEnabled = status.isEnabled
                }
        case "emergency_event_manager":
                if emergencyEventEnabled != status.isEnabled {
            emergencyEventEnabled = status.isEnabled
                }
        case "phishing_protection_agent":
                if phishingProtectionEnabled != status.isEnabled {
            phishingProtectionEnabled = status.isEnabled
                }
        case "malware_detection_agent":
                if malwareDetectionEnabled != status.isEnabled {
            malwareDetectionEnabled = status.isEnabled
                }
        case "mobile_security_agent":
                if mobileSecurityEnabled != status.isEnabled {
            mobileSecurityEnabled = status.isEnabled
                }
        case "network_security_agent":
                if networkSecurityEnabled != status.isEnabled {
            networkSecurityEnabled = status.isEnabled
                }
        case "incident_response_agent":
                if incidentResponseEnabled != status.isEnabled {
            incidentResponseEnabled = status.isEnabled
                }
        case "password_security_agent":
                if passwordSecurityEnabled != status.isEnabled {
            passwordSecurityEnabled = status.isEnabled
                }
        default:
            break
            }
        }
    }
}

