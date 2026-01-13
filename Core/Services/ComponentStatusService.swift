import Foundation
import Combine

/**
 * 📊 Component Status Service
 * Сервис для управления статусами всех 42 компонентов
 * Ленивая загрузка, кэширование, background refresh
 */

@MainActor
class ComponentStatusService: ObservableObject {
    static let shared = ComponentStatusService()
    
    // MARK: - Dependencies
    
    private let apiService: APIService
    private let cacheManager: ComponentCacheService
    
    // MARK: - Published Properties
    
    @Published var componentStatuses: [String: ComponentStatus] = [:]
    @Published var isLoading: Bool = false
    @Published var lastUpdate: Date?
    
    // MARK: - Private Properties
    
    private var cancellables = Set<AnyCancellable>()
    private let cacheTTL: TimeInterval = 300 // 5 минут
    
    // MARK: - Initialization
    
    init(
        apiService: APIService = APIService.shared,
        cacheManager: ComponentCacheService = ComponentCacheService.shared
    ) {
        self.apiService = apiService
        self.cacheManager = cacheManager
        
        // Загрузить кэшированные данные при инициализации
        loadCachedStatuses()
    }
    
    // MARK: - Public Methods
    
    /// Получить статус компонента (с ленивой загрузкой)
    func getStatus(
        for componentId: String,
        priority: ComponentPriority = .normal
    ) async throws -> ComponentStatus {
        // Проверить кэш
        if let cachedStatus = componentStatuses[componentId],
           !cachedStatus.isStale(maxAge: cacheTTL) {
            return cachedStatus
        }
        
        // Загрузить из API
        return try await loadStatusFromAPI(for: componentId, priority: priority)
    }
    
    /// Загрузить статусы критичных компонентов (batch)
    func loadCriticalComponentsStatus() async throws {
        isLoading = true
        defer { isLoading = false }
        
        // Список критичных компонентов (первые 10 для NetworkProtectionScreen)
        let criticalComponents = [
            "crash_detection_agent",
            "roadside_assistance_agent",
            "incident_response_agent",
            "password_security_agent",
            "phishing_protection_agent",
            "malware_detection_agent",
            "mobile_security_agent",
            "network_security_agent",
            "emergency_response_bot",
            "emergency_event_manager"
        ]
        
        do {
            // Попытка загрузить все критичные компоненты параллельно
            var statuses: [String: ComponentStatus] = [:]
            
            try await withThrowingTaskGroup(of: (String, ComponentStatus).self) { group in
                for componentId in criticalComponents {
                    group.addTask { [weak self] in
                        guard let self = self else {
                            throw ComponentError.unknown(NSError(domain: "ComponentStatusService", code: -1))
                        }
                        let status = try await self.loadStatusFromAPI(for: componentId, priority: .critical)
                        return (componentId, status)
                    }
                }
                
                for try await (componentId, status) in group {
                    statuses[componentId] = status
                }
            }
            
            // Обновить статусы
            for (componentId, status) in statuses {
                componentStatuses[componentId] = status
            }
            
            // Сохранить в кэш
            await cacheManager.saveStatuses(statuses)
            
            lastUpdate = Date()
            
        } catch {
            // ✅ FALLBACK: Если ошибка, использовать дефолтные значения
            print("⚠️ ComponentStatusService: Ошибка загрузки компонентов, используем дефолтные значения: \(error.localizedDescription)")
            
            // Создать дефолтные статусы (все выключены)
            var defaultStatuses: [String: ComponentStatus] = [:]
            for componentId in criticalComponents {
                // Использовать существующий статус из кэша, если есть, иначе создать новый
                if let existingStatus = componentStatuses[componentId] {
                    defaultStatuses[componentId] = existingStatus
                } else {
                    let defaultStatus = ComponentStatus(
                        componentId: componentId,
                        isEnabled: false,
                        lastUpdate: nil,
                        configuration: nil
                    )
                    defaultStatuses[componentId] = defaultStatus
                    componentStatuses[componentId] = defaultStatus
                }
            }
            
            // Сохранить дефолтные статусы в кэш
            await cacheManager.saveStatuses(defaultStatuses)
            
            // НЕ пробрасывать ошибку дальше - использовать дефолтные значения
            // Приложение продолжит работать с дефолтными значениями
        }
    }
    
    /// Обновить статус компонента
    func updateStatus(
        componentId: String,
        isEnabled: Bool,
        configuration: ComponentConfiguration? = nil
    ) async throws {
        // Оптимистичное обновление UI
        if var currentStatus = componentStatuses[componentId] {
            currentStatus.update(isEnabled: isEnabled, configuration: configuration)
            componentStatuses[componentId] = currentStatus
        } else {
            let newStatus = ComponentStatus(
                componentId: componentId,
                isEnabled: isEnabled,
                lastUpdate: Date(),
                configuration: configuration
            )
            componentStatuses[componentId] = newStatus
        }
        
        // Отправить на сервер
        try await apiService.updateComponentStatus(
            componentId: componentId,
            isEnabled: isEnabled,
            configuration: configuration
        )
        
        // Обновить кэш
        if let status = componentStatuses[componentId] {
            await cacheManager.saveStatus(componentId: componentId, status: status)
        }
    }
    
    /// Background refresh (для критичных компонентов)
    func refreshCriticalComponents() async {
        do {
            try await loadCriticalComponentsStatus()
        } catch {
            print("⚠️ ComponentStatusService: Ошибка background refresh: \(error)")
        }
    }
    
    // MARK: - Private Methods
    
    private func loadStatusFromAPI(
        for componentId: String,
        priority: ComponentPriority
    ) async throws -> ComponentStatus {
        // Использовать APIService для загрузки
        do {
            return try await apiService.getComponentStatus(componentId: componentId)
        } catch {
            // Если компонент не найден, вернуть дефолтный статус
            throw ComponentError.componentNotFound(componentId)
        }
    }
    
    private func loadCachedStatuses() {
        Task {
            let cached = await cacheManager.loadAllStatuses()
            await MainActor.run {
                self.componentStatuses = cached
            }
        }
    }
}

