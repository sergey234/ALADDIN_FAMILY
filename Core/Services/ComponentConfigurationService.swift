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
        if let cached = configurations[componentId],
           let fetchedAt = configurationFetchedAt[componentId],
           Date().timeIntervalSince(fetchedAt) < configurationFetchTTL {
            return cached
        }
        if let inflight = configurationInFlight[componentId] {
            return try await inflight.value
        }

        let task = Task<ComponentConfiguration, Error> { [weak self] in
            guard let self else {
                throw ComponentError.unknown(NSError(domain: "ComponentConfigurationService", code: -1))
            }
            return try await self.loadConfigurationFromAPI(for: componentId)
        }
        configurationInFlight[componentId] = task
        defer { configurationInFlight[componentId] = nil }

        let config = try await task.value
        configurations[componentId] = config
        configurationFetchedAt[componentId] = Date()
        return config
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
        configurationFetchedAt[componentId] = Date()

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
    private var lastParentalMonitoringSave: (messages: Bool, screenshots: Bool)?
    private var lastParentalMonitoringSaveAt: Date?
    private let parentalMonitoringSaveDedupeWindow: TimeInterval = 2
    private var configurationFetchedAt: [String: Date] = [:]
    private var configurationInFlight: [String: Task<ComponentConfiguration, Error>] = [:]
    private let configurationFetchTTL: TimeInterval = 45

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
        let payload = (messagesEnabled, screenshotsEnabled)
        if let last = lastParentalMonitoringSave,
           last == payload,
           let at = lastParentalMonitoringSaveAt,
           Date().timeIntervalSince(at) < parentalMonitoringSaveDedupeWindow {
            return
        }

        let existing = try? await getConfiguration(for: parentalMonitoringBotComponentId)
        var merged = existing?.additionalSettings ?? [:]
        merged["messagesMonitoringEnabled"] = AnyCodable(messagesEnabled)
        merged["screenshotsEnabled"] = AnyCodable(screenshotsEnabled)
        merged["parental_messages_monitoring"] = AnyCodable(messagesEnabled)
        merged["parental_screenshots_enabled"] = AnyCodable(screenshotsEnabled)

        let configuration = ComponentConfiguration(
            isEnabled: existing?.isEnabled ?? true,
            priority: existing?.priority ?? .normal,
            additionalSettings: merged
        )
        try await saveConfiguration(componentId: parentalMonitoringBotComponentId, configuration: configuration)
        configurationFetchedAt[parentalMonitoringBotComponentId] = Date()
        lastParentalMonitoringSave = payload
        lastParentalMonitoringSaveAt = Date()
    }

}

