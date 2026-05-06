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
        apiService: APIService? = nil,
        cacheManager: ComponentCacheService = ComponentCacheService.shared
    ) {
        self.apiService = apiService ?? APIService.shared
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

    // MARK: - Parental monitoring bot (`parental_control_bot`)

    private var parentalMonitoringBotComponentId: String { "parental_control_bot" }

    /// Загрузка флагов `parental_messages_monitoring` / `parental_screenshots_enabled` с сервера (компонентная конфигурация).
    func loadParentalMonitoringTogglesFromServer() async -> (messages: Bool?, screenshots: Bool?) {
        do {
            let config = try await getConfiguration(for: parentalMonitoringBotComponentId)
            let settings = config.additionalSettings ?? [:]
            let messages =
                (settings["messagesMonitoringEnabled"]?.value as? Bool)
                ?? (settings["parental_messages_monitoring"]?.value as? Bool)
            let screenshots =
                (settings["screenshotsEnabled"]?.value as? Bool)
                ?? (settings["parental_screenshots_enabled"]?.value as? Bool)
            return (messages, screenshots)
        } catch {
            return (nil, nil)
        }
    }

    func saveParentalMonitoringTogglesToServer(messagesEnabled: Bool, screenshotsEnabled: Bool) async throws {
        let configuration = ComponentConfiguration(
            isEnabled: true,
            priority: .normal,
            additionalSettings: [
                "messagesMonitoringEnabled": AnyCodable(messagesEnabled),
                "screenshotsEnabled": AnyCodable(screenshotsEnabled),
                "parental_messages_monitoring": AnyCodable(messagesEnabled),
                "parental_screenshots_enabled": AnyCodable(screenshotsEnabled)
            ]
        )
        try await saveConfiguration(componentId: parentalMonitoringBotComponentId, configuration: configuration)
    }

}

