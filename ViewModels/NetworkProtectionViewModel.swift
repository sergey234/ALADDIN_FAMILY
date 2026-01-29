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
    
    func toggleCrashDetection() {
        Task {
            await toggleComponent(
                componentId: "crash_detection_agent",
                updateClosure: { [weak self] value in self?.crashDetectionEnabled = value },
                getCurrentValue: { [weak self] in self?.crashDetectionEnabled ?? false }
            )
        }
    }
    
    func toggleRoadsideAssistance() {
        Task {
            await toggleComponent(
                componentId: "roadside_assistance_agent",
                updateClosure: { [weak self] value in self?.roadsideAssistanceEnabled = value },
                getCurrentValue: { [weak self] in self?.roadsideAssistanceEnabled ?? false }
            )
        }
    }
    
    func toggleEmergencyResponse() {
        Task {
            await toggleComponent(
                componentId: "emergency_response_bot",
                updateClosure: { [weak self] value in self?.emergencyResponseEnabled = value },
                getCurrentValue: { [weak self] in self?.emergencyResponseEnabled ?? false }
            )
        }
    }
    
    func toggleEmergencyEvent() {
        Task {
            await toggleComponent(
                componentId: "emergency_event_manager",
                updateClosure: { [weak self] value in self?.emergencyEventEnabled = value },
                getCurrentValue: { [weak self] in self?.emergencyEventEnabled ?? false }
            )
        }
    }
    
    func togglePhishingProtection() {
        Task {
            await toggleComponent(
                componentId: "phishing_protection_agent",
                updateClosure: { [weak self] value in self?.phishingProtectionEnabled = value },
                getCurrentValue: { [weak self] in self?.phishingProtectionEnabled ?? false }
            )
        }
    }
    
    func toggleMalwareDetection() {
        Task {
            await toggleComponent(
                componentId: "malware_detection_agent",
                updateClosure: { [weak self] value in self?.malwareDetectionEnabled = value },
                getCurrentValue: { [weak self] in self?.malwareDetectionEnabled ?? false }
            )
        }
    }
    
    func toggleMobileSecurity() {
        Task {
            await toggleComponent(
                componentId: "mobile_security_agent",
                updateClosure: { [weak self] value in self?.mobileSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.mobileSecurityEnabled ?? false }
            )
        }
    }
    
    func toggleNetworkSecurity() {
        Task {
            await toggleComponent(
                componentId: "network_security_agent",
                updateClosure: { [weak self] value in self?.networkSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.networkSecurityEnabled ?? false }
            )
        }
    }
    
    func toggleIncidentResponse() {
        Task {
            await toggleComponent(
                componentId: "incident_response_agent",
                updateClosure: { [weak self] value in self?.incidentResponseEnabled = value },
                getCurrentValue: { [weak self] in self?.incidentResponseEnabled ?? false }
            )
        }
    }
    
    func togglePasswordSecurity() {
        Task {
            await toggleComponent(
                componentId: "password_security_agent",
                updateClosure: { [weak self] value in self?.passwordSecurityEnabled = value },
                getCurrentValue: { [weak self] in self?.passwordSecurityEnabled ?? false }
            )
        }
    }
    
    // MARK: - Private Methods
    
    private func toggleComponent(
        componentId: String,
        updateClosure: @escaping (Bool) -> Void,
        getCurrentValue: @escaping () -> Bool
    ) async {
        let oldValue = getCurrentValue()
        let newValue = !oldValue
        
        // Оптимистичное обновление UI
        updateClosure(newValue)
        
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
            updateClosure(oldValue)
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

