import Foundation

/**
 * 📊 Component Status Model
 * Модель для хранения статуса компонента
 * Используется для отслеживания состояния всех 42 компонентов
 */

struct ComponentStatus: Codable, Identifiable, Equatable {
    let id: String
    let componentId: String
    var isEnabled: Bool
    var lastUpdate: Date?
    var configuration: ComponentConfiguration?
    
    init(
        componentId: String,
        isEnabled: Bool = false,
        lastUpdate: Date? = nil,
        configuration: ComponentConfiguration? = nil
    ) {
        self.id = UUID().uuidString
        self.componentId = componentId
        self.isEnabled = isEnabled
        self.lastUpdate = lastUpdate
        self.configuration = configuration
    }
    
    /// Обновить статус компонента
    mutating func update(isEnabled: Bool, configuration: ComponentConfiguration? = nil) {
        self.isEnabled = isEnabled
        self.lastUpdate = Date()
        if let configuration = configuration {
            self.configuration = configuration
        }
    }
    
    /// Проверить, устарел ли статус (старше 5 минут)
    func isStale(maxAge: TimeInterval = 300) -> Bool {
        guard let lastUpdate = lastUpdate else { return true }
        return Date().timeIntervalSince(lastUpdate) > maxAge
    }
}

