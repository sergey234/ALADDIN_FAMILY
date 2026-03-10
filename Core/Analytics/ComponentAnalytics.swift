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
     * ✅ BUILD 102: Dictionary создается на main thread для предотвращения рекурсии
     * На реальном устройстве создание Dictionary в background thread при рекурсии
     * вызывает проблемы с Dictionary.resize → краш
     */
    func trackComponentToggle(componentId: String, enabled: Bool) {
        Task {
            await MainActor.run {
                // ✅ BUILD 102: Dictionary создается на main thread
                // await MainActor.run гарантирует выполнение на main thread
                let parameters: [String: Any] = [
                    "component_id": componentId,
                    "enabled": enabled,
                    "timestamp": Date().timeIntervalSince1970
                ]
                analyticsManager.trackEvent("component_toggle", parameters: parameters)
            }
        }
    }
    
    // MARK: - Component Settings Tracking
    
    /**
     * Отследить открытие настроек компонента
     * ✅ BUILD 102: Dictionary создается на main thread для предотвращения рекурсии
     */
    func trackComponentSettingsOpened(componentId: String) {
        Task {
            await MainActor.run {
                let parameters: [String: Any] = [
                    "component_id": componentId,
                    "timestamp": Date().timeIntervalSince1970
                ]
                analyticsManager.trackEvent("component_settings_opened", parameters: parameters)
            }
        }
    }
    
    /**
     * Отследить сохранение настроек компонента
     * ✅ BUILD 102: Dictionary создается на main thread для предотвращения рекурсии
     */
    func trackComponentSettingsSaved(componentId: String, settings: [String: Any]) {
        Task {
            await MainActor.run {
                let parameters: [String: Any] = [
                    "component_id": componentId,
                    "settings": settings,
                    "timestamp": Date().timeIntervalSince1970
                ]
                analyticsManager.trackEvent("component_settings_saved", parameters: parameters)
            }
        }
    }

    /**
     * Отследить переключение настройки компонента
     * ✅ BUILD 102: Dictionary создается на main thread для предотвращения рекурсии
     */
    func trackSettingToggle(componentId: String, settingKey: String, enabled: Bool) {
        Task {
            await MainActor.run {
                // ✅ BUILD 102: Dictionary создается на main thread
                // await MainActor.run гарантирует выполнение на main thread
                let parameters: [String: Any] = [
                    "component_id": componentId,
                    "setting_key": settingKey,
                    "enabled": enabled,
                    "timestamp": Date().timeIntervalSince1970
                ]
                analyticsManager.trackEvent("component_setting_toggle", parameters: parameters)
            }
        }
    }
    
    // MARK: - Component Error Tracking
    
    /**
     * Отследить ошибку компонента
     * ✅ BUILD 102: Dictionary создается на main thread для предотвращения рекурсии
     */
    func trackComponentError(componentId: String, error: Error) {
        Task {
            await MainActor.run {
                let parameters: [String: Any] = [
                    "component_id": componentId,
                    "error_type": String(describing: type(of: error)),
                    "error_message": error.localizedDescription,
                    "timestamp": Date().timeIntervalSince1970
                ]
                analyticsManager.trackEvent("component_error", parameters: parameters)
            }
        }
    }
    
    // MARK: - Component Status Tracking
    
    /**
     * Отследить загрузку статуса компонента
     * ✅ BUILD 102: Dictionary создается на main thread для предотвращения рекурсии
     */
    func trackComponentStatusLoaded(componentId: String, isEnabled: Bool, loadTime: TimeInterval) {
        Task {
            await MainActor.run {
                let parameters: [String: Any] = [
                    "component_id": componentId,
                    "is_enabled": isEnabled,
                    "load_time": loadTime,
                    "timestamp": Date().timeIntervalSince1970
                ]
                analyticsManager.trackEvent("component_status_loaded", parameters: parameters)
            }
        }
    }
    
    // MARK: - Component Usage Statistics
    
    /**
     * Отследить использование компонента (включен/выключен)
     * ✅ BUILD 102: Dictionary создается на main thread для предотвращения рекурсии
     */
    func trackComponentUsage(componentId: String, duration: TimeInterval, enabled: Bool) {
        Task {
            await MainActor.run {
                let parameters: [String: Any] = [
                    "component_id": componentId,
                    "duration": duration,
                    "enabled": enabled,
                    "timestamp": Date().timeIntervalSince1970
                ]
                analyticsManager.trackEvent("component_usage", parameters: parameters)
            }
        }
    }
    
    // MARK: - Screen Tracking
    
    /**
     * Отследить просмотр экрана с компонентами
     * ✅ BUILD 102: Dictionary создается на main thread для предотвращения рекурсии
     */
    func trackComponentScreenView(screenName: String, componentCount: Int) {
        Task {
            await MainActor.run {
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
    }
}

