import Foundation
import SwiftUI
import Combine

// Master Logger for parental control logging
private let logger = MasterLogger.shared

/**
 * 👶 Parental Control ViewModel
 * ViewModel для управления родительским контролем и 5 компонентами защиты детей
 * Использует ComponentStatusService для загрузки и обновления статусов
 */

@MainActor
class ParentalControlViewModel: ObservableObject {
    
    // MARK: - Published Properties - Child Data
    
    @Published var selectedChild: Child?
    @Published var children: [Child] = []
    @Published var isContentFilterEnabled: Bool = true
    @Published var isAppBlockingEnabled: Bool = true
    @Published var screenTimeLimit: Double = 3
    @Published var allowedApps: [String] = []
    @Published var blockedSitesToday: Int = 12
    @Published var screenTimeToday: String = "2:45"
    
    // MARK: - Published Properties - Component Statuses (5 компонентов)
    
    // Защита детей (4 компонента)
    @Published var selfHarmDetectionEnabled: Bool = false
    @Published var groomingDetectionEnabled: Bool = false
    @Published var onlinePredatorsEnabled: Bool = false
    @Published var psychologicalSupportEnabled: Bool = false
    
    // Родительский контроль (1 компонент - улучшить)
    @Published var parentalControlBotEnabled: Bool = true
    
    // MARK: - Dependencies
    
    private let statusService: ComponentStatusService
    private let retryManager: RetryManager
    private let toastManager = ToastManager.shared
    
    // MARK: - Initialization
    
    init(
        statusService: ComponentStatusService = .shared,
        retryManager: RetryManager = .balanced()
    ) {
        logger.business("Initializing ParentalControlViewModel")
        self.statusService = statusService
        self.retryManager = retryManager
        
        loadChildren()
        
        // Загрузить статусы компонентов
        Task {
            await loadComponentStatuses()
        }
    }
    
    // MARK: - Component Methods
    
    /// Загрузить статусы всех компонентов
    func loadComponentStatuses() async {
        logger.business("Loading parental control component statuses")

        // ✅ УЛУЧШЕНИЕ: Параллельная загрузка с лимитом и приоритизацией
        // Критичные компоненты загружаются первыми
        let componentIds: [(String, ComponentLoadPriority)] = [
            ("self_harm_detection_agent", .critical),
            ("grooming_detection_agent", .critical),
            ("online_predators_agent", .critical),
            ("parental_control_bot", .high),
            ("psychological_support_agent", .normal)
        ]
        
        let prioritizedItems: [PrioritizedLoadItem<ComponentStatus>] = componentIds.map { componentId, priority in
            PrioritizedLoadItem(
                id: componentId,
                priority: priority
            ) { [weak self] in
                guard let self = self else {
                    throw ComponentError.unknown(NSError(domain: "ParentalControlViewModel", code: -1))
                }
                return try await self.statusService.getStatus(for: componentId)
            }
        }
        
        do {
            let results = try await ParallelLoader.executeWithLimit(
                items: prioritizedItems,
                maxConcurrent: 10
            ) { [weak self] componentId, status in
                self?.updateStatusForComponent(componentId: componentId, status: status)
            }
            
            print("✅ ParentalControlViewModel: Загружено \(results.count) статусов")
        } catch {
            print("⚠️ ParentalControlViewModel: Ошибка загрузки статусов: \(error)")
        }
    }


    // MARK: - Toggle Methods
    
    func toggleSelfHarmDetection(_ newValue: Bool) {
        logger.business("Toggling self-harm detection: \(newValue)")
        Task {
            await toggleComponent(
                componentId: "self_harm_detection_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.selfHarmDetectionEnabled = value }
            )
        }
    }
    
    func toggleGroomingDetection(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "grooming_detection_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.groomingDetectionEnabled = value }
            )
        }
    }
    
    func toggleOnlinePredators(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "online_predators_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.onlinePredatorsEnabled = value }
            )
        }
    }
    
    func togglePsychologicalSupport(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "psychological_support_agent",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.psychologicalSupportEnabled = value }
            )
        }
    }
    
    func toggleParentalControlBot(_ newValue: Bool) {
        Task {
            await toggleComponent(
                componentId: "parental_control_bot",
                newValue: newValue,
                updateClosure: { [weak self] value in self?.parentalControlBotEnabled = value }
            )
        }
    }
    
    // MARK: - Private Methods
    
    /// Переключить компонент
    private func toggleComponent(
        componentId: String,
        newValue: Bool,
        updateClosure: @escaping (Bool) -> Void
    ) async {
        // Оптимистичное обновление UI с переданным значением
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
            toastManager.showSuccess("Компонент обновлен")
        case .failure(let error):
            // Откат при ошибке - используем противоположное значение
            updateClosure(!newValue)
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }
    
    /// Обновить статус компонента локально
    private func updateStatusForComponent(componentId: String, status: ComponentStatus) {
        switch componentId {
        case "self_harm_detection_agent":
            selfHarmDetectionEnabled = status.isEnabled
        case "grooming_detection_agent":
            groomingDetectionEnabled = status.isEnabled
        case "online_predators_agent":
            onlinePredatorsEnabled = status.isEnabled
        case "psychological_support_agent":
            psychologicalSupportEnabled = status.isEnabled
        case "parental_control_bot":
            parentalControlBotEnabled = status.isEnabled
        default:
            break
        }
    }
    
    // MARK: - Child Management
    
    func loadChildren() {
        logger.business("Loading children data for parental control")
        children = [
            Child(name: "Маша", age: 10, avatar: "👧", screenTimeToday: "2:45", threatsBlocked: 23),
            Child(name: "Петя", age: 7, avatar: "👦", screenTimeToday: "1:30", threatsBlocked: 8)
        ]
        selectedChild = children.first
    }
    
    func toggleContentFilter() {
        isContentFilterEnabled.toggle()
    }
    
    func toggleAppBlocking() {
        isAppBlockingEnabled.toggle()
    }
    
    func updateScreenTimeLimit(_ value: Double) {
        screenTimeLimit = value
    }
    
    func addTime(minutes: Int) {
        print("Add \(minutes) minutes to screen time")
    }
    
    func blockDevice() {
        print("Block child device immediately")
    }
    
    func showLocation() {
        print("Show child location on map")
    }
    
    // MARK: - Child Model
    
    struct Child: Identifiable {
        let id = UUID()
        let name: String
        let age: Int
        let avatar: String
        let screenTimeToday: String
        let threatsBlocked: Int
    }
}
