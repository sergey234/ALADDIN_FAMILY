import Foundation

/**
 * 💾 Component Cache Service
 * Сервис для кэширования статусов и конфигураций компонентов
 * Использует UserDefaults для персистентного хранения
 */

actor ComponentCacheService {
    static let shared = ComponentCacheService()
    
    // MARK: - Constants
    
    private let statusesKey = "ComponentStatuses"
    private let configurationsKey = "ComponentConfigurations"
    private let cacheExpirationKey = "ComponentCacheExpiration"
    
    // MARK: - Private Properties
    
    private let userDefaults: UserDefaults
    private let cacheTTL: TimeInterval = 300 // 5 минут
    
    // MARK: - Initialization
    
    init(userDefaults: UserDefaults = .standard) {
        self.userDefaults = userDefaults
    }
    
    // MARK: - Status Methods
    
    /// Сохранить статус компонента
    func saveStatus(componentId: String, status: ComponentStatus) async {
        var statuses = await loadAllStatuses()
        statuses[componentId] = status
        await saveAllStatuses(statuses)
    }
    
    /// Сохранить несколько статусов
    func saveStatuses(_ statuses: [String: ComponentStatus]) async {
        var allStatuses = await loadAllStatuses()
        for (componentId, status) in statuses {
            allStatuses[componentId] = status
        }
        await saveAllStatuses(allStatuses)
    }
    
    /// Загрузить статус компонента
    func loadStatus(componentId: String) async -> ComponentStatus? {
        let allStatuses = await loadAllStatuses()
        return allStatuses[componentId]
    }
    
    /// Загрузить все статусы
    func loadAllStatuses() async -> [String: ComponentStatus] {
        guard let data = userDefaults.data(forKey: statusesKey),
              let decoded = try? JSONDecoder().decode([String: ComponentStatus].self, from: data) else {
            return [:]
        }
        return decoded
    }
    
    /// Сохранить все статусы
    private func saveAllStatuses(_ statuses: [String: ComponentStatus]) async {
        if let encoded = try? JSONEncoder().encode(statuses) {
            userDefaults.set(encoded, forKey: statusesKey)
            userDefaults.set(Date(), forKey: cacheExpirationKey)
        }
    }
    
    /// Очистить кэш статусов
    func clearStatuses() async {
        userDefaults.removeObject(forKey: statusesKey)
    }
    
    // MARK: - Configuration Methods
    
    /// Сохранить конфигурацию компонента
    func saveConfiguration(componentId: String, configuration: ComponentConfiguration) async {
        var configurations = await loadAllConfigurations()
        configurations[componentId] = configuration
        await saveAllConfigurations(configurations)
    }
    
    /// Загрузить конфигурацию компонента
    func loadConfiguration(componentId: String) async -> ComponentConfiguration? {
        let allConfigurations = await loadAllConfigurations()
        return allConfigurations[componentId]
    }
    
    /// Загрузить все конфигурации
    func loadAllConfigurations() async -> [String: ComponentConfiguration] {
        guard let data = userDefaults.data(forKey: configurationsKey),
              let decoded = try? JSONDecoder().decode([String: ComponentConfiguration].self, from: data) else {
            return [:]
        }
        return decoded
    }
    
    /// Сохранить все конфигурации
    private func saveAllConfigurations(_ configurations: [String: ComponentConfiguration]) async {
        if let encoded = try? JSONEncoder().encode(configurations) {
            userDefaults.set(encoded, forKey: configurationsKey)
        }
    }
    
    /// Очистить кэш конфигураций
    func clearConfigurations() async {
        userDefaults.removeObject(forKey: configurationsKey)
    }
    
    // MARK: - Cache Management
    
    /// Проверить, устарел ли кэш
    func isCacheExpired() async -> Bool {
        guard let expirationDate = userDefaults.object(forKey: cacheExpirationKey) as? Date else {
            return true
        }
        return Date().timeIntervalSince(expirationDate) > cacheTTL
    }
    
    /// Очистить весь кэш
    func clearAllCache() async {
        await clearStatuses()
        await clearConfigurations()
        userDefaults.removeObject(forKey: cacheExpirationKey)
    }
}

