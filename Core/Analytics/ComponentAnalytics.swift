import Foundation

/**
 * 📊 Component Analytics
 * Аналитика для отслеживания использования 42 компонентов
 * Интеграция с AnalyticsManager
 */

class ComponentAnalytics {
    
    // MARK: - Singleton
    
    static let shared = ComponentAnalytics()
    
    private let analyticsManager = AnalyticsManager.shared
    
    private init() {}
    
    // MARK: - Component Toggle Tracking
    
    /**
     * Отследить переключение компонента
     */
    func trackComponentToggle(componentId: String, enabled: Bool) {
        analyticsManager.trackEvent(
            "component_toggle",
            parameters: [
                "component_id": componentId,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
    
    // MARK: - Component Settings Tracking
    
    /**
     * Отследить открытие настроек компонента
     */
    func trackComponentSettingsOpened(componentId: String) {
        analyticsManager.trackEvent(
            "component_settings_opened",
            parameters: [
                "component_id": componentId,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
    
    /**
     * Отследить сохранение настроек компонента
     */
    func trackComponentSettingsSaved(componentId: String, settings: [String: Any]) {
        analyticsManager.trackEvent(
            "component_settings_saved",
            parameters: [
                "component_id": componentId,
                "settings": settings,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
    
    // MARK: - Component Error Tracking
    
    /**
     * Отследить ошибку компонента
     */
    func trackComponentError(componentId: String, error: Error) {
        analyticsManager.trackEvent(
            "component_error",
            parameters: [
                "component_id": componentId,
                "error_type": String(describing: type(of: error)),
                "error_message": error.localizedDescription,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
    
    // MARK: - Component Status Tracking
    
    /**
     * Отследить загрузку статуса компонента
     */
    func trackComponentStatusLoaded(componentId: String, isEnabled: Bool, loadTime: TimeInterval) {
        analyticsManager.trackEvent(
            "component_status_loaded",
            parameters: [
                "component_id": componentId,
                "is_enabled": isEnabled,
                "load_time": loadTime,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
    
    // MARK: - Component Usage Statistics
    
    /**
     * Отследить использование компонента (включен/выключен)
     */
    func trackComponentUsage(componentId: String, duration: TimeInterval, enabled: Bool) {
        analyticsManager.trackEvent(
            "component_usage",
            parameters: [
                "component_id": componentId,
                "duration": duration,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
    
    // MARK: - Screen Tracking
    
    /**
     * Отследить просмотр экрана с компонентами
     */
    func trackComponentScreenView(screenName: String, componentCount: Int) {
        analyticsManager.trackScreen(
            screenName,
            screenClass: "ComponentScreen"
        )
        
        analyticsManager.trackEvent(
            "component_screen_view",
            parameters: [
                "screen_name": screenName,
                "component_count": componentCount,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
}

