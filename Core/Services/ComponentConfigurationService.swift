import Foundation
import Combine

/**
 * ⚙️ Component Configuration Service
 * Сервис для управления конфигурациями компонентов
 * Сохранение, загрузка, валидация
 */

@MainActor
class ComponentConfigurationService: ObservableObject {
    static let shared = ComponentConfigurationService()
    
    // MARK: - Dependencies
    
    private let apiService: APIService
    private let cacheManager: ComponentCacheService
    
    // MARK: - Published Properties
    
    @Published var configurations: [String: ComponentConfiguration] = [:]
    
    // MARK: - Initialization
    
    init(
        apiService: APIService = APIService.shared,
        cacheManager: ComponentCacheService = ComponentCacheService.shared
    ) {
        self.apiService = apiService
        self.cacheManager = cacheManager
        
        // Загрузить кэшированные конфигурации
        loadCachedConfigurations()
    }
    
    // MARK: - Public Methods
    
    /// Получить конфигурацию компонента
    func getConfiguration(for componentId: String) async throws -> ComponentConfiguration {
        // Проверить кэш
        if let cached = configurations[componentId] {
            return cached
        }
        
        // Загрузить из API
        return try await loadConfigurationFromAPI(for: componentId)
    }
    
    /// Сохранить конфигурацию компонента
    func saveConfiguration(
        componentId: String,
        configuration: ComponentConfiguration
    ) async throws {
        // Валидация
        try validateConfiguration(configuration)
        
        // Сохранить локально
        configurations[componentId] = configuration
        
        // Отправить на сервер
        try await apiService.updateComponentConfiguration(
            componentId: componentId,
            configuration: configuration
        )
        
        // Сохранить в кэш
        await cacheManager.saveConfiguration(componentId: componentId, configuration: configuration)
    }
    
    /// Валидация конфигурации
    func validateConfiguration(_ configuration: ComponentConfiguration) throws {
        // Проверка базовых настроек
        if configuration.priority == .critical && !configuration.isEnabled {
            throw ComponentError.configurationError("Критичные компоненты должны быть включены")
        }
        
        // Проверка настроек мониторинга
        if let monitoring = configuration.monitoringSettings {
            if monitoring.alertThreshold < 0 {
                throw ComponentError.configurationError("Порог оповещений не может быть отрицательным")
            }
        }
        
        // Проверка настроек экстренной помощи
        if let emergency = configuration.emergencySettings {
            if emergency.responseTime < 0 || emergency.responseTime > 300 {
                throw ComponentError.configurationError("Время ответа должно быть от 0 до 300 секунд")
            }
        }
    }
    
    // MARK: - Private Methods
    
    private func loadConfigurationFromAPI(for componentId: String) async throws -> ComponentConfiguration {
        return try await apiService.getComponentConfiguration(componentId: componentId)
    }
    
    private func loadCachedConfigurations() {
        Task {
            let cached = await cacheManager.loadAllConfigurations()
            await MainActor.run {
                self.configurations = cached
            }
        }
    }
}

