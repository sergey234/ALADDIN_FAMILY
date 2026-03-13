import Foundation

/**
 * 📊 Component Analytics
 * Отслеживание аналитики компонентов защиты
 */

@MainActor
class ComponentAnalytics {
    
    // MARK: - Singleton
    
    static let shared = ComponentAnalytics()
    
    private let analyticsManager = AnalyticsManager.shared
    
    private init() {
        // Инициализация
    }
    
    // MARK: - Component Toggle Tracking
    
    /// Отслеживать переключение компонента
    func trackComponentToggle(componentId: String, enabled: Bool) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            let eventName = enabled ? "component_enabled" : "component_disabled"
            let parameters: [String: Any] = [
                "component_id": componentId,
                "enabled": enabled
            ]
            
            self.analyticsManager.trackEvent(eventName, parameters: parameters)
        }
    }
    
    /// Отслеживать переключение настройки компонента
    func trackSettingToggle(componentId: String, settingKey: String, enabled: Bool) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            let eventName = "component_setting_toggled"
            let parameters: [String: Any] = [
                "component_id": componentId,
                "setting_key": settingKey,
                "enabled": enabled
            ]
            
            self.analyticsManager.trackEvent(eventName, parameters: parameters)
        }
    }
    
    /// Отслеживать просмотр экрана компонента
    func trackComponentScreenView(screenName: String, componentCount: Int) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            let eventName = "component_screen_view"
            let parameters: [String: Any] = [
                "screen_name": screenName,
                "component_count": componentCount
            ]
            
            self.analyticsManager.trackEvent(eventName, parameters: parameters)
        }
    }
    
    /// Отслеживать ошибку компонента
    func trackComponentError(componentId: String, error: Error) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            
            let eventName = "component_error"
            let parameters: [String: Any] = [
                "component_id": componentId,
                "error_description": error.localizedDescription
            ]
            
            self.analyticsManager.trackEvent(eventName, parameters: parameters)
        }
    }
}
