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
     * ✅ BUILD 102: Dictionary создается на main thread автоматически благодаря @MainActor
     */
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // 🛡️ BUILD 108: Прямое создание словаря. 
        // Потокобезопасность обеспечивается NSLock внутри AnalyticsManager.
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
    
    // MARK: - Component Settings Tracking
    
    /**
     * Отследить открытие настроек компонента
     */
    func trackComponentSettingsOpened(componentId: String) {
        let parameters: [String: Any] = [
            "component_id": componentId,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_settings_opened", parameters: parameters)
    }
    
    /**
     * Отследить сохранение настроек компонента
     */
    func trackComponentSettingsSaved(componentId: String, settings: [String: Any]) {
        let parameters: [String: Any] = [
            "component_id": componentId,
            "settings": settings,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_settings_saved", parameters: parameters)
    }

    /**
     * Отследить переключение настройки компонента
     */
    func trackSettingToggle(componentId: String, settingKey: String, enabled: Bool) {
        let parameters: [String: Any] = [
            "component_id": componentId,
            "setting_key": settingKey,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_setting_toggle", parameters: parameters)
    }
    
    // MARK: - Component Error Tracking
    
    /**
     * Отследить ошибку компонента
     */
    func trackComponentError(componentId: String, error: Error) {
        let parameters: [String: Any] = [
            "component_id": componentId,
            "error_type": String(describing: type(of: error)),
            "error_message": error.localizedDescription,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_error", parameters: parameters)
    }
    
    // MARK: - Component Status Tracking
    
    /**
     * Отследить загрузку статуса компонента
     */
    func trackComponentStatusLoaded(componentId: String, isEnabled: Bool, loadTime: TimeInterval) {
        let parameters: [String: Any] = [
            "component_id": componentId,
            "is_enabled": isEnabled,
            "load_time": loadTime,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_status_loaded", parameters: parameters)
    }
    
    // MARK: - Component Usage Statistics
    
    /**
     * Отследить использование компонента (включен/выключен)
     */
    func trackComponentUsage(componentId: String, duration: TimeInterval, enabled: Bool) {
        let parameters: [String: Any] = [
            "component_id": componentId,
            "duration": duration,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_usage", parameters: parameters)
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
        
        let parameters: [String: Any] = [
            "screen_name": screenName,
            "component_count": componentCount,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_screen_view", parameters: parameters)
    }
}

